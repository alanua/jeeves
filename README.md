# Jeeves

A local-first multi-agent orchestration system. Accepts tasks via a REST API, routes them to local or cloud LLM providers, executes them through a typed agent interface, and returns structured answers with trace metadata.

**Current scope: Stage 1 — vertical slice.** The system answers real requests end-to-end. No UI, no voice, no RAG.

---

## Architecture

```
POST /ask
  │
  ▼
Orchestrator
  ├── PolicyEngine      (pre-flight: self-modification check)
  ├── TaskClassifier    (keyword heuristics → TaskType)
  ├── SessionMemory     (in-process, bounded history)
  ├── ExecutorAgent
  │     └── LLMRouter
  │           ├── OllamaProvider   (local, tried first by default)
  │           └── OpenRouterProvider (cloud fallback)
  └── DB persistence   (sessions / messages / traces)
```

**Key design decisions:**
- Providers are behind a common `BaseProvider` interface — swap or add without touching orchestration.
- Policy gates run before every provider call and tool invocation. Deny by default.
- Session memory is in-process for Stage 1 (replace with Redis/DB-backed in Stage 2).
- All LLM traffic goes through `LLMRouter`. Fallback is opt-in via `ENABLE_CLOUD_FALLBACK`.
- Every request generates a trace record in PostgreSQL for observability from day one.
- Structured JSON logging throughout. No `print()` statements.

---

## Requirements

- Python 3.12+
- Docker + Docker Compose
- (Optional) [Ollama](https://ollama.com) running locally for local inference

---

## Quick Start

### 1. Clone and configure

```bash
git clone <repo>
cd jeeves
cp .env.example .env
# Edit .env — set OPENROUTER_API_KEY if you want cloud fallback
```

### 2. Start with Docker Compose

```bash
docker compose up --build -d
```

This starts:
- `postgres` — PostgreSQL 16 on `127.0.0.1:5432`
- `api` — FastAPI app on `http://localhost:8000`

Tables are managed explicitly by Alembic migrations. After spinning up the database, you must run migrations:
`docker compose exec api alembic upgrade head` (if running inside docker) or `alembic upgrade head` locally.

### 3. Run locally (without Docker)

```bash
# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux/macOS

# Install dependencies
pip install -e ".[dev]"

# Start PostgreSQL separately (Docker or native), then:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Ollama Setup

Ollama is the local inference backend. It is **not containerized** — run it natively:

```bash
# Install: https://ollama.com/download
ollama serve              # starts on http://localhost:11434
ollama pull llama3        # or whichever model you set in OLLAMA_MODEL_DEFAULT
```

The app boots fine without Ollama. If Ollama is unavailable and `ENABLE_CLOUD_FALLBACK=true`, requests fall back to OpenRouter automatically.

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `APP_ENV` | `development` | Environment tag |
| `APP_PORT` | `8000` | API listen port |
| `DATABASE_URL` | `postgresql+asyncpg://...` | PostgreSQL connection string |
| `DEFAULT_MODE` | `local_first` | Provider strategy (`local_first`, `cloud_first`, `cheapest`, `strongest`) |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL_DEFAULT` | `llama3` | Default Ollama model |
| `OLLAMA_TIMEOUT_SECONDS` | `30` | Request timeout for Ollama |
| `OPENROUTER_API_KEY` | _(empty)_ | OpenRouter API key |
| `OPENROUTER_MODEL_DEFAULT` | `openai/gpt-4o-mini` | Default OpenRouter model |
| `ENABLE_CLOUD_FALLBACK` | `true` | Allow fallback to OpenRouter if local fails |
| `TOOL_SHELL_ENABLED` | `false` | Enable shell execution tool |
| `TOOL_FILESYSTEM_ENABLED` | `false` | Enable filesystem tool |
| `TOOL_HTTP_ENABLED` | `false` | Enable HTTP fetch tool |
| `SELF_MODIFICATION_ENABLED` | `false` | Allow self-modification requests (keep false) |

---

## Database Migrations

Tables are managed purely by Alembic. The application does not auto-create tables on startup. To apply the schema:

```bash
# Apply migrations
alembic upgrade head

# Create a new migration after model changes
alembic revision --autogenerate -m "describe change"
```

The initial migration is at `migrations/versions/0001_initial_schema.py`.

---

## API Reference

### `GET /health`

Liveness check. Always returns 200 if the process is alive.

```bash
curl http://localhost:8000/health
# {"status": "ok"}
```

### `GET /ready`

Readiness check. Verifies DB connectivity and reports provider availability.

```bash
curl http://localhost:8000/ready
```

```json
{
  "status": "ready",
  "database": "ok",
  "providers": {
    "ollama": "ok",
    "openrouter": "unavailable"
  }
}
```

### `GET /metrics`

Structured configuration stats.

```bash
curl http://localhost:8000/metrics
```

### `POST /ask`

Submit a task.

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the capital of Germany?",
    "session_id": "my-session-01",
    "preferred_mode": "local_first",
    "allow_tools": false
  }'
```

**Response:**

```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "answer": "The capital of Germany is Berlin.",
  "selected_agent": "executor",
  "selected_provider": "ollama",
  "selected_model": "llama3",
  "fallback_used": false,
  "tool_calls": [],
  "latency_ms": 812.4,
  "warnings": []
}
```

**With cloud fallback triggered:**

```json
{
  "request_id": "...",
  "answer": "Berlin is the capital of Germany.",
  "selected_provider": "openrouter",
  "fallback_used": true,
  ...
}
```

**Request schema:**

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | `string` | ✓ | Task or question |
| `session_id` | `string` | — | Session continuity ID (auto-generated if omitted) |
| `user_id` | `string` | — | User identifier for tracing |
| `preferred_mode` | `enum` | — | `local_first` \| `cloud_first` \| `cheapest` \| `strongest` |
| `allow_tools` | `bool` | — | Enable tool use (default: `false`) |
| `metadata` | `object` | — | Arbitrary caller metadata |

---

## Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest -v

# Run a specific test file
pytest tests/test_policy.py -v
pytest tests/test_router.py -v
pytest tests/test_ask_smoke.py -v
pytest tests/test_health.py -v
```

Tests use an in-memory SQLite database — no running Postgres or Ollama required.

---

## Linting and Formatting

```bash
ruff check app/ tests/
ruff format app/ tests/
black app/ tests/
```

---

## OpenAPI Docs

Available at `http://localhost:8000/docs` when the server is running.

---

## Known Limitations (Stage 1)

- **Session memory is in-process.** Stored in a Python dict. Cleared on restart. Production deployments need Redis or DB-backed session memory.
- **Task classification is keyword-based.** No ML. Accurate enough for routing, not suitable for nuanced classification.
- **No streaming.** Responses are returned as complete payloads. Streaming is a Stage 2 concern.
- **One agent active.** The `ExecutorAgent` handles all task types. Specialized agents (coding, research, planner) are future work.
- **No tool implementations.** Tools are gated by policy and config. Shell/filesystem/HTTP tools are not implemented — only the policy layer is in place.
- **No long-term memory.** Per-session bounded history only.
- **No authentication.** The API is open. Add OAuth2/API-key middleware before any external exposure.

---

## Next Stages

| Stage | Scope |
|---|---|
| **Stage 2** | Redis-backed session memory, streaming responses, tool implementations (shell allowlist, HTTP fetch) |
| **Stage 3** | Specialized agents (coding, research, planner), agent registry, task routing to agents |
| **Stage 4** | Long-term memory with vector store, retrieval-augmented context |
| **Stage 5** | Voice/text input gateway, multi-modal inputs |
| **Stage 6** | Controlled self-improvement subsystem with human-in-the-loop approval |

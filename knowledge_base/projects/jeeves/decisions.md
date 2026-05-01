# Jeeves — Decisions

Status: CONFIRMED_CANON
Last consolidated: 2026-05-01

## Confirmed decisions

### Memory architecture

- GitHub KB is the public-safe durable canon after review.
- Google Drive private memory is temporary private working memory.
- ChatGPT memory is compact working memory only.
- Raw chats, branches, exports, screenshots, and logs are historical evidence, not automatic canon.
- Wiki-first memory is preferred: Markdown canon + JSON/YAML structured facts + logs/evals.
- RAG/LightRAG/MemPalace are retrieval support layers, not canonical truth.

### Recovery workflow

- `JEEVES_BRANCH_RECOVERY_MODE` / `ВІДН ДЖ` means process all supplied messages as historical source.
- Do not blindly canonize.
- Classify every durable item before saving.
- Keep public KB clean and private/sensitive data out of public GitHub.

### Agent architecture

- Start simple and expand progressively.
- Agent teams are future controlled capability, not default mode.
- Contract-first spawning is required for complex coordinated development.
- Agent outputs should be artifact-driven via files, not hidden chat-only state.

### Runner-mediated executor workflow

- The user does not manually pass tasks to Codex.
- ChatGPT/architect writes structured task files or task instructions in the KB/workspace.
- Runner reads those tasks and passes them to Codex or the selected executor.
- Runner returns execution results/logs/handoff for ChatGPT review.
- ChatGPT then audits the result, updates KB/handoff, and prepares the next task if needed.
- Therefore, task files must be written for machine/runner consumption: clear goal, context, allowed changes, forbidden changes, commands/checks, expected output, and handoff requirements.

### Safety and self-improvement

- No autonomous self-rewrites.
- Controlled self-improvement chain: observe -> detect -> propose -> validate -> approve -> apply -> monitor -> rollback.
- Least-privilege tools and explicit approval for dangerous actions.
- Browser/computer-use only in sandbox early on.

### LLM/provider strategy

- Jeeves must not rely on ChatGPT subscription as runtime backend.
- Runtime should use provider APIs and/or local models through a router.
- ChatGPT Plus/Pro remains useful for human interactive architecture/review work.

## Superseded / rejected

- Do not copy OpenClaw wholesale as architecture.
- Do not copy Claude-specific tmux/iTerm settings as core design.
- Do not accept marketing claims about autonomous corporations as canon.
- Do not store secrets in Markdown, prompts, or public GitHub.
- Do not tell the user to manually give Codex tasks when the runner workflow is available; runner is the executor handoff mechanism.

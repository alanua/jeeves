# Jeeves — Open Questions

Status: LIVING_DOCUMENT
Last consolidated: 2026-05-01

## Architecture

- Which orchestration library, if any, should be used long-term: own lightweight orchestrator, LangGraph-style flow, or mixed approach?
- When exactly should MCP/tool layer be introduced after Stage 1?
- What is the first safe tool set: filesystem read-only, GitHub read/write, Drive, shell allowlist, HTTP fetch?
- What should be the minimal schema for tasks, traces, approvals, and handoff?

## Memory

- What should be imported first from ChatGPT export?
- What belongs in public GitHub vs private Drive vs local encrypted storage?
- How should structured facts be represented: YAML files, JSON files, SQLite/Postgres tables, or spreadsheet during temporary phase?
- When to test MemPalace or LightRAG as retrieval support?

## Agents

- What is the first specialist agent to add: reviewer, memory/doc agent, coder, tester, or monitor?
- What criteria should trigger subagents vs full agent team?
- How to prevent multiple agents editing the same file?

## Runtime

- When to move from local/dev machine to Hetzner/VDS runtime?
- What sandbox profile is required before browser/computer-use tests?
- How should Telegram control be introduced safely?

## Governance

- What approval UI/flow is minimal but safe?
- What should count as destructive action?
- What logs/evals are mandatory before self-improvement loop is enabled?

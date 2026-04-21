# Jeeves Knowledge Base

Last updated: 2026-04-21

This directory is the durable project knowledge base for **Jeeves**. It is intended to make project continuation possible for a new engineer, agent, or reviewer without relying on chat history.

## Read order for a new contributor

1. [01_PROJECT_OVERVIEW.md](./01_PROJECT_OVERVIEW.md)
2. [02_ARCHITECTURE_AND_PRINCIPLES.md](./02_ARCHITECTURE_AND_PRINCIPLES.md)
3. [03_IMPLEMENTATION_STATE.md](./03_IMPLEMENTATION_STATE.md)
4. [04_COORDINATION_AND_AGENTS.md](./04_COORDINATION_AND_AGENTS.md)
5. [05_ACTION_LAYER.md](./05_ACTION_LAYER.md)
6. [06_MEMORY_AND_HANDOFF.md](./06_MEMORY_AND_HANDOFF.md)
7. [07_KNOWLEDGE_BASE_SUBSYSTEM.md](./07_KNOWLEDGE_BASE_SUBSYSTEM.md)
8. [08_MODEL_PROVIDER_AND_SKILLS_STRATEGY.md](./08_MODEL_PROVIDER_AND_SKILLS_STRATEGY.md)
9. [09_ECOSYSTEM_WATCHLIST.md](./09_ECOSYSTEM_WATCHLIST.md)
10. [10_SECURITY_AND_RELEASE_HYGIENE.md](./10_SECURITY_AND_RELEASE_HYGIENE.md)
11. [11_CONTINUATION_GUIDE_AND_NEXT_STEPS.md](./11_CONTINUATION_GUIDE_AND_NEXT_STEPS.md)

## Purpose of this knowledge base

This knowledge base captures accepted project information about:
- product intent
- architecture
- implementation status
- accepted engineering decisions
- current and future subsystems
- ecosystem watchlists and external signal interpretation
- safe next steps

## What this directory is not

This directory is not a replacement for:
- canonical code-level contracts in the repo
- tests as the source of behavioral truth
- future memory / handoff runtime objects
- future research wiki / external knowledge-base subsystem

## Current project snapshot

- Stage 1 foundation is closed and HTTP-locked.
- Stage 2 hybrid coordination is live and stable.
- Execution-aware hybrid with dry-run executor is live and stable.
- Canonical action-layer contracts and policy scaffolding exist.
- Live proposal generation and real action execution are not yet wired.

## Related entrypoints

- [PROJECT_KNOWLEDGE_BASE.md](./PROJECT_KNOWLEDGE_BASE.md) — legacy one-file snapshot, now kept as an index/summary pointer.

## Maintenance rule

Update this knowledge base when any of the following changes materially:
- accepted architecture
- stage status
- subsystem direction
- watchlist priorities
- policy / action / memory strategy
- provider evaluation strategy
- safe next-step posture

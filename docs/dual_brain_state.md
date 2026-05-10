# Skeleton Dual-Brain Externalizer v0.1 — Architectural Anchor

Status: **v0.1 foundation merged into `main`**

This document anchors the current practical state of the Skeleton Dual-Brain Externalizer. It is intended to prevent context drift across long sessions and to give ChatGPT, Gemini, Runner, and Oleksii the same map of the implemented system.

## 1. Purpose

Skeleton Dual-Brain Externalizer is the practical bridge between:

- **ChatGPT / Skeleton** as architect, control plane, synthesis node, and canon gate.
- **Gemini Auditor Node** as stateless external auditor and evidence source.
- **Hetzner Runner** as deterministic execution and routing environment.
- **GitHub Issues** as task queue, state machine, and public-safe audit trail.

The current system does not make Jeeves fully autonomous yet. It provides the first verified foundation for a safe dual-brain workflow:

```text
GitHub Issue
-> typed task packet
-> Gemini auditor input
-> Gemini adapter
-> audit result
-> GitHub comment
-> label transition

# Assistant diary

Status: CONFIRMED_CANON
Scope: public-safe global ChatGPT/Jeeves collaboration diary
Created: 2026-05-03

This file is the public-safe external diary for durable ChatGPT collaboration changes. It is not a raw chat log and must not contain private material, secrets, bank data, personal documents, email bodies, or production credentials.

Use this file for short entries when a durable global behavior rule, startup/resume rule, recovery/audit operation, or cross-chat continuity decision changes.

Private or sensitive diary material belongs in Google Drive private memory, especially:

```text
Jeeves Private Memory - Handoff
Jeeves Private Memory - Recovery Audit Log
Jeeves Private Memory - Structured Facts
```

## 2026-05-03 — Boot continuity cleanup

Classification: CONFIRMED_CANON
Sensitivity: public-safe

What changed:
- The main ChatGPT startup entrypoint was optimized so it explicitly points to the full boot sequence.
- `knowledge_base/CHATGPT_BRANCH_CONTINUITY_BOOT.md` is now part of the required startup file set.
- The boot route is clarified as: settings prompt -> GitHub public canon -> private Google Drive memory when needed -> project-specific handoff/diary/structured facts -> current task.
- The assistant diary is externalized: public-safe entries go here; private entries stay in Drive handoff/audit/structured facts.

Reason:
- The user requested a self-audit for gaps and then asked to close the gaps and optimize boot.
- The main risk was not missing memory, but unsynchronized entrypoints causing the next ChatGPT branch to skip part of the boot chain.

Operating rule:
- At the start of serious project work, do not trust ChatGPT internal memory as canon.
- Load `START_HERE_FOR_CHATGPT.md`, `MEMORY_POLICY.md`, `WORKING_PROTOCOL.md`, `CHATGPT_BRANCH_CONTINUITY_BOOT.md`, and project-specific startup files as needed.
- Check private Drive memory only when private/non-public context is relevant.

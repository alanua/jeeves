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

## 2026-05-03 — Second full audit pass

Classification: CONFIRMED_CANON
Sensitivity: public-safe

What changed:
- A second pass found that `MEMORY_POLICY.md` and `assistant_startup_prompt.md` still contained older compact startup wording.
- Both files were synchronized with the optimized boot chain.
- The current global required startup set is now consistent across the main boot files:
  - `START_HERE_FOR_CHATGPT.md`
  - `MEMORY_POLICY.md`
  - `WORKING_PROTOCOL.md`
  - `CHATGPT_BRANCH_CONTINUITY_BOOT.md`
  - `assistant_diary.md`
  - for Jeeves/OpenClaw work: `assistant_startup_prompt.md`

Reason:
- The user requested another full audit pass and logic check after the initial cleanup.

Operating rule:
- Future compact memory text must include `CHATGPT_BRANCH_CONTINUITY_BOOT.md`, `WORKING_PROTOCOL.md`, and the Drive private memory hub.
- No startup file should imply that `assistant_startup_prompt.md` alone is enough for Jeeves work; global boot files must be loaded first.

## 2026-05-03 — Third/Fourth full audit pass

Classification: CONFIRMED_CANON
Sensitivity: public-safe

What changed:
- Another audit pass searched for remaining old boot formulas instead of only checking file existence.
- `CHATGPT_BRANCH_CONTINUITY_BOOT.md` still had an older required sequence that omitted `assistant_diary.md` and did not list itself in the global startup set. It was corrected.
- `knowledge_base/recovery_audit/2026-05-01_memory_overflow_branch.md` still had a historical compact-memory replacement saying to start from `assistant_startup_prompt.md`. It was corrected and marked as historical audit evidence where current boot files win if conflict exists.
- Drive `Jeeves Private Memory - START HERE` was checked again; its top startup section now has the full optimized boot order.

Current required boot set:
- `knowledge_base/START_HERE_FOR_CHATGPT.md`
- `knowledge_base/MEMORY_POLICY.md`
- `knowledge_base/WORKING_PROTOCOL.md`
- `knowledge_base/CHATGPT_BRANCH_CONTINUITY_BOOT.md`
- `knowledge_base/assistant_diary.md`
- for Jeeves/OpenClaw work: `knowledge_base/assistant_startup_prompt.md`
- when private context is relevant: Drive private memory hub

Operating rule:
- Historical recovery/audit notes are not primary startup instructions. If any historical text conflicts with current boot files, current boot files win.

## 2026-05-03 — Debt closure pass: private infrastructure split

Classification: CONFIRMED_CANON
Sensitivity: public-safe summary only

What changed:
- The remaining hygiene debt was closed: raw private Jeeves runner / Hetzner / Termux infrastructure details were removed from the global Drive handoff.
- A dedicated private Drive document now holds those operational details: `Jeeves Private Memory - Runner Hetzner Handoff`.
- The global Drive handoff now keeps only a redacted pointer to that private project-specific handoff.
- `Jeeves Private Memory - START HERE` now lists the runner/Hetzner handoff as a project-specific private memory file.
- `Jeeves Private Memory - Structured Facts` now contains an index row for `jeeves_runner` / private handoff.

Reason:
- The user requested another full audit pass and explicitly asked to close the remaining debt.

Operating rule:
- Global handoff should stay compact and should not carry raw infrastructure details.
- Runner/Hetzner/Termux operational details must stay in the dedicated private Drive handoff.
- Do not copy raw IPs, SSH details, access notes, keys, or credentials into public GitHub.

## 2026-05-03 — ChatGPT exoskeleton operating model

Classification: CONFIRMED_CANON
Sensitivity: public-safe

What changed:
- Added `knowledge_base/CHATGPT_EXOSKELETON.md` as the canonical working model for the external operating layer around ChatGPT.
- Added the exoskeleton to the required startup set in `START_HERE_FOR_CHATGPT.md`.
- Defined the development-team workflow as part of the exoskeleton.
- Defined memory tools as parts of the exoskeleton.
- Clarified that future Jeeves may inherit selected tested exoskeleton tools later, but must not inherit raw ChatGPT memory chaos.

Operating rule:
- ChatGPT wears the exoskeleton now.
- The development team workflow is part of the exoskeleton.
- The memory tools are parts of the exoskeleton.
- Jeeves may inherit selected tested tools later only after review, cleanup, adaptation, testing, approval, and implementation.

## 2026-05-03 — Recovery mode integrated into exoskeleton

Classification: CONFIRMED_CANON
Sensitivity: public-safe

What changed:
- Older `JEEVES_BRANCH_RECOVERY_MODE` instructions were reviewed as historical source.
- The useful parts were integrated into `CHATGPT_EXOSKELETON.md` as `Recovery / Historical Source Layer`.
- The old recovery process is now a module of the ChatGPT exoskeleton, not the whole operating model.
- The exoskeleton now explicitly records the strategic goal: first strengthen ChatGPT through the exoskeleton, then use that stronger collaboration loop to design and build Jeeves as a separate independent private assistant.

Operating rule:
- Treat old branches/files/exports/screenshots/docs as historical sources.
- Extract durable knowledge only.
- Classify before saving.
- Write only minimal history source index, behavior rule, recovery audit note, or approved canonical doc.
- Never overwrite canon from old chat without approval.

## 2026-05-03 — Skeleton startup synchronization

Classification: CONFIRMED_CANON
Sensitivity: public-safe

What changed:
- Synchronized supporting boot files after `АУД ВСЕ` found gaps.
- `MEMORY_POLICY.md` now includes `CHATGPT_EXOSKELETON.md` in the compact startup pointer and defines the exoskeleton memory rule.
- `WORKING_PROTOCOL.md` now includes `СК` / `SK` as the Skeleton alias and documents boot levels.
- `CHATGPT_BRANCH_CONTINUITY_BOOT.md` now includes `CHATGPT_EXOSKELETON.md` in the required boot sequence.
- Drive START HERE, Drive Handoff, and Drive Recovery Audit Log were updated to include the exoskeleton in startup/hand-off/audit context.
- Structured Facts received an `operating_model` index row for `chatgpt_exoskeleton`.

Operating rule:
- Serious ChatGPT project work should boot through starter, policy, working protocol, continuity boot, diary, and exoskeleton.
- `СК` / `SK` means use or audit the ChatGPT exoskeleton operating model.
- Recovery mode remains a module inside the exoskeleton.

## 2026-05-03 — Skeleton Stage 1 runbook

Classification: CONFIRMED_CANON
Sensitivity: public-safe

What changed:
- Added `knowledge_base/CHATGPT_EXOSKELETON_RUNBOOK.md` as the operational checklist for using Skeleton v1 in real ChatGPT work.
- Added the runbook to `START_HERE_FOR_CHATGPT.md` required startup files.
- The runbook defines boot levels, command handling, read-before-write, post-write verification, recovery handling, private routing, runner task behavior, and failure defenses.

Operating rule:
- `CHATGPT_EXOSKELETON.md` defines the model.
- `CHATGPT_EXOSKELETON_RUNBOOK.md` defines the behavior/checklist.
- For serious Skeleton/protocol/memory work, use both.
- Stage 1 is behavioral/procedural: boot level selection, read-before-write, post-write verification, classification before storage, private/public routing, runner-readable tasks, short handoffs, and periodic audits.

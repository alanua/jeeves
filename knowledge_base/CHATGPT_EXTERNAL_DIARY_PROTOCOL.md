# ChatGPT External Diary Protocol

Status: CONFIRMED_CANON
Scope: ChatGPT collaboration continuity, structured action diary, handoff, and anti-amnesia workflow
Recorded: 2026-05-03

## Purpose

This protocol defines how ChatGPT should keep an external structured diary for work with Oleksii.

The diary is not raw chat history. It is not a memory dump. It is a structured continuity layer that lets each new chat resume from the correct state instead of repeating setup, guessing from unreliable internal memory, or mixing unrelated project branches.

## Core rule

Every serious project chat should start by reading the startup instructions file. That file tells the assistant what to read next and in what order.

The boot sequence is:

```text
settings starter / custom instructions
-> knowledge_base/START_HERE_FOR_CHATGPT.md
-> knowledge_base/MEMORY_POLICY.md
-> knowledge_base/WORKING_PROTOCOL.md
-> project-specific startup/handoff/structured facts
-> external diary/current state
-> current user request
```

For Jeeves/OpenClaw-style work also read:

```text
knowledge_base/assistant_startup_prompt.md
knowledge_base/CHATGPT_BRANCH_CONTINUITY_BOOT.md
knowledge_base/CHATGPT_SETTINGS_STARTER.md
knowledge_base/CHATGPT_EXTERNAL_DIARY_PROTOCOL.md
```

## Diary is structured, not raw

The diary must not store everything. It must store only useful operational continuity.

Allowed diary content:

- what task was being worked on
- what was changed
- what decision was made
- what files/docs were updated
- what commit/result happened
- what remains open
- what is blocked
- what the next step is
- which project branch this belongs to
- classification of saved information
- links/paths to relevant KB files or private Drive docs

Forbidden diary content in public GitHub:

- raw private messages
- raw finance/banking/health/email contents
- secrets, keys, credentials, tokens
- noisy logs unless redacted and needed for audit
- large chat dumps
- temporary thoughts without durable value

## Required diary entry shape

Use this structure for each meaningful work session or important state change:

```yaml
entry_id: YYYY-MM-DD-short-slug
project: Jeeves | BauClock | Gewerbe | Lavalamp | Homelab | AndroidTV | Van | Global
status: active | blocked | done | superseded
classification: CONFIRMED_CANON | NEEDS_REVIEW | BACKLOG | REJECTED | PRIVATE | TEMPORARY
summary: short human-readable summary
what_was_done:
  - item
current_state:
  - item
next_steps:
  - item
open_questions:
  - item
artifacts:
  - path_or_link
commits:
  - sha
privacy_notes: public-safe | private-context-in-drive | contains-no-secrets
```

Markdown form is also acceptable:

```text
Date:
Project:
Status:
Classification:
What was done:
Current state:
Next steps:
Open questions:
Artifacts/links:
Commits:
Privacy notes:
```

## Relationship to handoff

Diary and handoff are related but not identical.

Diary:

```text
chronological structured record of important actions and state changes
```

Handoff:

```text
latest resume point for the next session
```

A new chat should prefer the latest handoff for speed, and use the diary/audit log when the handoff is insufficient or when cross-chat consistency is in question.

## Anti-chaos rule

Do not create a new diary file for every random message.

Prefer:

```text
one global diary index
project-specific diary/handoff files
small dated audit notes only for important recovery or policy events
```

Use public GitHub for public-safe durable diary entries. Use private Google Drive memory for private context.

## Anti-amnesia rule

The assistant must not rely on internal memory to remember what it did.

After important work, write or update an external diary/handoff entry if tools are available. If tools are unavailable, give the user a compact handoff block that can be saved later.

## Classification

CONFIRMED_CANON.

Reason: user explicitly required that ChatGPT begin new chats by reading startup instructions, then follow ordered memory pointers, and maintain a structured external diary of actions, current state, results, and next steps rather than storing chaotic raw history.

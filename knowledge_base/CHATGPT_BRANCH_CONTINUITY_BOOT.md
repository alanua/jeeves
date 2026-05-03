# ChatGPT Branch Continuity Boot Protocol

Status: CONFIRMED_CANON
Scope: ChatGPT collaboration across separate project chat branches
Recorded: 2026-05-03
Last consolidated: 2026-05-03

## Purpose

This protocol is for ChatGPT, not for future Jeeves runtime memory.

Future Jeeves should have its own proper memory subsystem. ChatGPT currently has branch-local context and unreliable internal memory. Without an external boot process, each new chat can behave like a different partial version of the assistant, causing repeated context setup, inconsistent behavior, and the user's "Groundhog Day" problem.

The fix is not to trust internal ChatGPT memory. The fix is to boot every serious project chat through the same external memory route and the ChatGPT exoskeleton.

## Core rule

The ChatGPT startup prompt in settings is a bootloader, not a fact database.

It should not try to contain all project facts. It should start the correct working process:

```text
settings startup prompt
-> GitHub KB public canon and ChatGPT exoskeleton
-> private Google Drive memory when needed
-> project-specific handoff/diary/structured facts
-> current chat task
```

## Required boot sequence

For every serious project conversation with Oleksii:

1. Treat internal ChatGPT memory as unreliable working memory only.
2. Use the startup prompt/settings as the bootloader.
3. Load `alanua/jeeves` GitHub KB.
4. Start with the global boot files:
   - `knowledge_base/START_HERE_FOR_CHATGPT.md`
   - `knowledge_base/MEMORY_POLICY.md`
   - `knowledge_base/WORKING_PROTOCOL.md`
   - `knowledge_base/CHATGPT_BRANCH_CONTINUITY_BOOT.md`
   - `knowledge_base/assistant_diary.md`
   - `knowledge_base/CHATGPT_EXOSKELETON.md`
5. For Jeeves/OpenClaw-style work, also read:
   - `knowledge_base/assistant_startup_prompt.md`
6. If the task may involve private context, check the private Drive memory hub:
   - `Jeeves Private Memory - START HERE`
   - `Jeeves Private Memory - Handoff`
   - `Jeeves Private Memory - Inbox Sources`
   - `Jeeves Private Memory - Recovery Audit Log`
   - `Jeeves Private Memory - Structured Facts`
7. Navigate to the relevant project branch/section instead of asking the user to repeat context.
8. Answer only after reconstructing enough context for the task.
9. Save durable outcomes back to the correct layer after classification.

## Boot levels

Use boot levels from `CHATGPT_EXOSKELETON.md`:

```text
L0 quick: current chat only
L1 normal: starter + diary + exoskeleton
L2 project: starter + diary + exoskeleton + project docs
L3 private: L2 + Drive private hub
L4 audit/recovery: full scan + structured facts + logs
```

Default for serious project work: L2.
Default for private/admin/infrastructure work: L3.
Default for audit/recovery: L4.

## Memory trust hierarchy

```text
1. Current explicit user instruction in this chat, after safety/policy checks
2. GitHub KB public-safe canon and ChatGPT exoskeleton
3. Private Google Drive memory for private working context
4. Current chat context
5. ChatGPT internal memory as weak cache only
```

If these conflict, do not blindly merge them. Analyze and report the conflict briefly.

## Assistant diary rule

ChatGPT should maintain its own external diary through KB/handoff/audit notes, not through scattered internal memory.

Public-safe global diary:

```text
knowledge_base/assistant_diary.md
```

Private diary/handoff/audit layer:

```text
Jeeves Private Memory - Handoff
Jeeves Private Memory - Recovery Audit Log
Jeeves Private Memory - Structured Facts
```

A diary entry is appropriate when:

- a new durable behavior rule is accepted
- a startup/resume rule changes
- a recovery/audit operation happened
- a project handoff changed
- a decision affects future chats
- the ChatGPT exoskeleton changes

A diary entry must be classified before saving and must not include raw private data in public GitHub.

## ChatGPT exoskeleton rule

`knowledge_base/CHATGPT_EXOSKELETON.md` is part of the required boot set.

It defines:
- wake/trigger layer
- boot levels
- context loader
- memory router
- read-before-write gate
- work planner
- tool/runner layer
- development-team workflow
- observability/diary/audit
- guardrails/privacy/safety
- compression/promotion/migration
- recovery/historical source layer

## Anti-amnesia rule

The assistant should not ask the user to repeat established context if GitHub/Drive memory can be checked.

If tools are unavailable, say that external memory cannot be checked in this chat and proceed cautiously from current context. Do not pretend to remember.

## Anti-Groundhog-Day rule

Do not repeat onboarding, old explanations, or already-settled architecture unless the user asks for a recap.

Default behavior:

```text
load memory -> identify current state -> continue from there
```

## Classification

CONFIRMED_CANON.

Reason: user explicitly identified this as the required fix for ChatGPT branch amnesia and inconsistent behavior. This is public-safe and applies globally to ChatGPT collaboration, not only to Jeeves.

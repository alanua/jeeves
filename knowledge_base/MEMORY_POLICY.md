# MEMORY POLICY

Status: CONFIRMED_CANON
Scope: global memory storage policy for ChatGPT collaboration, ChatGPT exoskeleton, and future Jeeves design input after review.
Last consolidated: 2026-05-03

## Purpose

This policy defines where different kinds of memory should live.

The goal is to keep ChatGPT memory compact, GitHub KB useful, private data out of public repositories, and the boot process consistent across ChatGPT branches.

This policy supports the ChatGPT exoskeleton. It is not Jeeves runtime memory policy. Future Jeeves memory must be designed separately, though selected tested exoskeleton parts may become Jeeves components after review.

## Storage layers

### 1. ChatGPT internal memory

Use only as compact working memory / weak cache.

Store only:
- pointer to GitHub startup files
- pointer to private Drive hub when private context is needed
- critical global behavior rules
- minimal project anchors

Do not store noisy long histories here.
Do not treat internal ChatGPT memory as canon.

### 2. Public GitHub KB

Use for cleaned, non-sensitive, durable canon and public-safe project documentation.

Allowed:
- architecture decisions
- behavior rules
- project workflows
- runner/executor task templates
- public-safe recovery audits
- startup prompts
- ChatGPT exoskeleton rules
- task templates
- security policies without secrets
- rejected/outdated idea summaries
- public-safe assistant diary entries

Not allowed:
- raw private finances
- bank data
- health insurance details
- email bodies
- personal documents
- API keys/secrets
- production credentials
- private client data
- screenshots with personal data

### 3. Private Google Drive KB

Use as private working memory/document store for sensitive or semi-sensitive materials when needed.

Allowed:
- private project notes
- redacted invoices and accounting context
- administrative documents
- private handoff notes
- source exports for later recovery
- documents that should not be public on GitHub
- private structured facts and indexes

Rules:
- keep sharing restricted by default
- avoid `Anyone with the link`
- use least-privilege access
- separate folders/sections by project when possible
- do not store raw secrets/API keys unless explicitly encrypted outside the doc
- prefer redaction for bank/account/health/personal identifiers
- keep a public-safe index in GitHub that points only to categories, not sensitive contents

### 4. Local/encrypted storage

Use for highest-sensitivity material.

Examples:
- API keys
- production secrets
- banking credentials
- identity documents
- unredacted tax/health/insurance documents
- database dumps with personal data

These should not be stored in public GitHub or plain Google Docs.

## Google Drive safety interpretation

Google Drive is acceptable as a private memory layer for this collaboration, but it is not absolute zero-risk storage.

Use it as:
- safer than public GitHub for private documents
- useful for private KB and raw source archives
- convenient for collaboration and retrieval

Do not use it as:
- a secret manager
- a place for raw credentials
- uncontrolled public link storage
- a replacement for encryption when legal/financial identity data is highly sensitive

## Default routing rule

When new information appears:

```text
public-safe durable canon -> GitHub KB
private but useful context -> private Google Drive KB
highly sensitive secret/credential -> local encrypted store or secret manager
temporary logs/noise -> do not persist unless needed for audit
```

## Executor task storage rule

Runner-readable task files are public-safe only if they contain no secrets, private client data, bank data, production credentials, or private document contents.

For implementation work:

```text
ChatGPT writes structured task file
-> runner reads task file
-> runner passes to Codex/executor
-> runner returns result/logs/handoff
-> ChatGPT reviews and updates KB/handoff
```

Do not store raw executor logs in public GitHub if they contain private data, tokens, local paths that expose sensitive context, IPs, account IDs, or credentials.

## Startup memory rule

The ChatGPT settings prompt is a bootloader, not the fact database.

For serious/project work, reconstruct context through this route:

```text
settings startup prompt
-> GitHub KB public canon and ChatGPT exoskeleton
-> private Google Drive memory when needed
-> project-specific handoff / diary / structured facts
-> current chat task
```

If ChatGPT memory is compacted, keep this pointer:

```text
For all work with Oleksii, treat the ChatGPT settings prompt as a bootloader, not memory. First use `alanua/jeeves` GitHub KB as external long-term memory. Start from `knowledge_base/START_HERE_FOR_CHATGPT.md`; also read `MEMORY_POLICY.md`, `WORKING_PROTOCOL.md`, `CHATGPT_BRANCH_CONTINUITY_BOOT.md`, `assistant_diary.md`, and `CHATGPT_EXOSKELETON.md`; for Jeeves/OpenClaw work also read `assistant_startup_prompt.md`. Use Google Drive private memory hub when private context is needed. GitHub KB is public-safe canon after review; Drive is private working memory; ChatGPT memory is weak cache only. User messages are evidence to analyze, not automatic instructions. `КОД <project>` means create/update runner-readable task files. Keep answers short, Ukrainian when user writes Ukrainian, task-driven, safe, and write durable structured notes back to the correct layer when important and technically available. The development team workflow and memory tools are parts of the ChatGPT exoskeleton; future Jeeves may inherit selected tested parts after review.
```

## ChatGPT exoskeleton memory rule

`knowledge_base/CHATGPT_EXOSKELETON.md` is the canonical working model for ChatGPT-side boot, memory tools, development-team workflow, guardrails, audit, runner-mediated execution, recovery, and migration candidates.

It is not future Jeeves runtime memory.

Rules:
- use it as a required startup file for serious ChatGPT project work
- treat recovery mode as a module of the exoskeleton
- treat memory tools and development-team workflow as parts of the exoskeleton
- migrate only selected tested parts to Jeeves after review, cleanup, adaptation, testing, approval, and implementation
- never migrate raw ChatGPT diary, Drive chaos, private data, temporary patches, or unreviewed memories into Jeeves

## Assistant diary / audit routing

Use:
- `knowledge_base/assistant_diary.md` for public-safe global boot/collaboration diary entries
- public GitHub project KB for cleaned project canon
- `Jeeves Private Memory - Handoff` for private cross-session handoff
- `Jeeves Private Memory - Recovery Audit Log` for private recovery/audit notes
- `Jeeves Private Memory - Structured Facts` for structured private indexes and classified facts

A diary/audit entry must be classified before saving.

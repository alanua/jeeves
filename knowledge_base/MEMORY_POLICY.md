# MEMORY POLICY

Status: CONFIRMED_CANON
Scope: global memory storage policy for ChatGPT collaboration and future Jeeves.
Last consolidated: 2026-05-01

## Purpose

This policy defines where different kinds of memory should live.

The goal is to keep ChatGPT memory compact, GitHub KB useful, and private data out of public repositories.

## Storage layers

### 1. ChatGPT internal memory

Use only as compact working memory.

Store only:
- pointer to GitHub startup files
- critical global behavior rules
- minimal project anchors

Do not store noisy long histories here.

### 2. Public GitHub KB

Use for cleaned, non-sensitive, durable canon.

Allowed:
- architecture decisions
- behavior rules
- project workflows
- public-safe recovery audits
- startup prompts
- task templates
- security policies without secrets
- rejected/outdated idea summaries

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

Rules:
- keep sharing restricted by default
- avoid `Anyone with the link`
- use least-privilege access
- separate folders by project
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

## Startup memory rule

If ChatGPT memory is compacted, keep this pointer:

```text
For all work with this user, first use `alanua/jeeves` GitHub KB as external long-term memory. Start from `knowledge_base/START_HERE_FOR_CHATGPT.md`; for Jeeves-specific work also read `knowledge_base/assistant_startup_prompt.md`; use `knowledge_base/MEMORY_POLICY.md` to decide what belongs in GitHub, Google Drive, local encrypted storage, or nowhere. GitHub KB is canon after review; Google Drive may hold private working memory; ChatGPT memory is only compact working memory.
```

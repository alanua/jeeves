# Fuel Strategy Notes

Status: IDEA_BACKLOG
Scope: public-safe strategy notes for Skeleton/Jeeves fuel routing and external workbench use
Source: user-approved working strategy after OpenHands pilot was blocked by OpenAI API quota/billing

## Core observation

Not every external component needs LLM fuel.

No-fuel armor should be built first:

```text
GitHub issues/PR/checks
git worktrees
gh CLI checkpoints
scripts and validators
artifact gates
secrets-preflight
status collectors
server hygiene inventory
logs and trace summaries
```

LLM-fueled components must be treated as engines, not armor:

```text
OpenHands
Aider
Codex
Antigravity / Gemini workbench
Gemini auditor
Graphiti/Zep extraction or summarization
any agent that writes, reasons, summarizes, or plans
```

## Subscription workbenches

Subscription workbenches may be useful now, but they are not unified backend fuel.

Working distinction:

```text
ChatGPT/Codex subscription surface = external OpenAI workbench.
Gemini/Antigravity subscription surface = external Google workbench.
OpenAI API / Gemini API / OpenRouter = backend fuel for tools and runners.
Local LLM = local low-cost fuel for lower-risk work.
```

Near-term economy rule:

```text
Use what is already available first.
Do not buy another fuel source until no-fuel armor and subscription-workbench workflows are exhausted.
Do not make OpenHands, Aider, Codex, Antigravity, or Gemini the core control plane.
```

Current near-term strategy:

```text
1. Build no-fuel armor first: contracts, gates, validation, checkpoints, cleanup, and trace.
2. Use ChatGPT/Codex and Antigravity/Gemini as external workbenches on existing subscriptions when useful.
3. Skeleton produces bounded task packets for those workbenches.
4. Workbench output must return as diff/PR/patch/report.
5. Skeleton audits the artifact before acceptance.
6. Do not continue API-fueled OpenHands until separate fuel policy and budget are approved.
```

## Free/provider-list handling

Free API provider lists are leads, not fuel policy.

Candidate providers from external videos or comments should be tested only through a provider-evaluation harness:

```text
official docs check
separate disposable key
no secrets in prompts
one tiny request
rate-limit/quota result
OpenAI-compatible endpoint check
cost/budget check
logging/checkpoint to GitHub
cleanup/revoke if rejected
```

Provider-specific free tiers are unstable and may depend on region, phone verification, anti-abuse systems, model availability, changing quotas, or billing setup.

Therefore, free providers may be useful for experiments, but must not become required infrastructure for Skeleton or Jeeves.

## Gemini migration note

A user-provided Gemini API email says the preview model used by project `gen-lang-client-0238167084` must be migrated before 2026-05-25.

Working action:

```text
Search private runner/config only where Gemini model IDs are stored.
If a preview ID is found, replace only the model identifier with gemini-3.1-flash-lite.
Do not change prompts or application logic unless testing proves it is needed.
Do not expose API keys or private config in GitHub/public notes.
```

This is operational maintenance, not a new architecture decision.

## Future Jeeves fuel direction

```text
local-first for cheap/low-risk tasks
OpenRouter or similar gateway as the first paid unified fuel candidate
optional direct OpenAI/Gemini/Anthropic API only when justified
cost, model, provider, task_id, and result must be traced
```

Fuel-router goal:

```text
task -> required capability -> privacy level -> cost cap -> provider/model choice -> trace
```

Core principle:

```text
Skeleton should not depend on one expensive model or one vendor-specific agent surface.
Jeeves should eventually choose fuel automatically under explicit budget, privacy, and authority constraints.
```

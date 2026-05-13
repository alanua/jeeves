# King Armor / Clean Skeleton Core Roadmap

Status: IDEA_BACKLOG -> LIKELY_NEEDS_REVIEW
Scope: future public/sanitized Skeleton product direction derived from user discussion.
Created: 2026-05-12

This document records a future direction only. It does not change current Skeleton permissions, does not create a public product, and does not promote any private memory into a public artifact.

## Correction of terms

This roadmap is about extracting a clean, reusable Skeleton core.

It is not about cleaning or publishing Jeeves.

The early project history created naming confusion because the Skeleton work grew inside the `alanua/jeeves` repository. For future planning, keep these concepts separate:

```text
Skeleton = exoskeleton / harness / protocol / memory and safety layer
Jeeves   = future assistant/product that may later use the Skeleton
King Armor / Обладунки Короля = possible clean deployable Skeleton core for other users
```

Therefore, the future clean extraction target is:

```text
clean Skeleton core
```

not:

```text
clean Jeeves
```

## Core idea

The current Skeleton is a private workshop for building a model-independent exoskeleton around LLMs.

A possible later extraction is a clean, sanitized, user-deployable Skeleton-core project tentatively described as:

```text
King Armor / Обладунки Короля
```

Working meaning:

```text
LLM = an amnesic wise person
Skeleton / Armor = memory, rules, tools, gates, roles, skills, logs, and safety protocol
User = final authority and owner of the kingdom
Jeeves = a possible future assistant/product that may wear or use the armor
```

The product idea is not another chatbot.

It is a self-hosted, model-independent personal AI exoskeleton that can be deployed by a user and gradually adapted to that user's context, tools, memory, workflows, and safety rules.

## Bootstrapping Jeeves through Skeleton

The long-term direction is that a growing Skeleton can become capable enough to help build Jeeves itself.

Initial constraint:

```text
At the beginning, the user did not yet have the tool needed to build something as complex and powerful as Jeeves directly.
```

Practical strategy:

```text
First strengthen the assistant through Skeleton.
Then use the strengthened Skeleton to build more of Jeeves safely.
```

This makes Skeleton a bootstrapping harness:

- first it stabilizes LLM work;
- then it stores memory outside one chat window;
- then it adds audit and review gates;
- then it adds planning and evaluation;
- then it adds skills;
- later it can help design, test, and assemble Jeeves components.

Important boundary:

```text
Skeleton does not automatically become Jeeves.
Skeleton is the toolchain and armor that may help create Jeeves.
Jeeves remains the future assistant/product.
```

## Why context-window users matter

Most users interact with AI through ordinary context windows, not through agentic systems.

This matters because a clean Skeleton core should not require users to start as agent-framework experts.

A practical user path could be:

```text
ordinary LLM chat window
-> Skeleton entry prompt / boot protocol
-> external memory/context pack
-> GitHub or local task protocol
-> optional runner / audit / PR workflow
```

The value is to give ordinary LLM chat windows external continuity, memory, rules, and safe action pathways.

In short:

```text
The context window remains the familiar interface.
Skeleton provides the external memory, rules, and tools behind it.
```

This could make the idea more accessible than a pure agent-platform-first product.

## Why this exists

Modern LLMs are powerful but unstable as long-term assistants because they:

- forget context between chats;
- depend on one vendor or one context window;
- confuse temporary evidence with durable canon;
- lack a stable user-owned memory layer;
- lack a consistent permission model;
- lack reliable audit / review / rollback gates;
- often cannot distinguish advice from authority to act.

King Armor would treat the LLM as a replaceable reasoning node, not as the system itself.

## Relationship to current projects

Current distinction:

```text
Skeleton = current exoskeleton / harness / workshop
Jeeves = future personal assistant/product
King Armor = possible cleaned, generic, deployable Skeleton core for other users
```

The current `alanua/jeeves` repository is not yet the clean public Skeleton-core product. It contains project history, local assumptions, private-workflow traces, and user-specific direction.

A future clean project should be extracted from the lessons, not published by simply exposing the private workshop.

## Clean-room extraction principle

Do not publish the private Skeleton workspace directly.

A future public / reusable project should be extracted through a clean process:

1. audit the current repository for private data, user-specific details, secrets, and local assumptions;
2. separate generic Skeleton architecture from user-specific memory;
3. extract only public-safe core components;
4. replace private examples with synthetic examples;
5. provide setup templates instead of real credentials or personal configuration;
6. document that each user owns their own memory, providers, GitHub, and deployment;
7. keep current private Skeleton/Jeeves context separate from public clean core.

## Intended user experience

A user should be able to deploy a clean instance, for example on a VPS/cloud/local machine, and configure:

- GitHub repository and token;
- LLM providers and model choices;
- memory storage location;
- public canon repository;
- private memory boundaries;
- skills folder;
- allowed tools;
- approval policy;
- runner permissions;
- audit / review / PR workflow.

The system should then grow with the user by accumulating:

- canon rules;
- personal/project memory;
- skills;
- workflows;
- trusted tools;
- review patterns;
- task history;
- role definitions;
- provider health knowledge.

## Game-like growth without being a game

The product may have a progression feeling similar to equipment/character development, but it is not a game.

Possible maturity levels:

```text
Level 1: reads canon and memory
Level 2: drafts tasks and issues
Level 3: runs audits
Level 4: creates PRs for review
Level 5: manages allowlisted skills
Level 6: maintains a private memory hub
Level 7: plans tasks with risk analysis
Level 8: evaluates with immutable judge rules
Level 9: isolates work through branches/worktrees
Level 10: supports a richer assistant experience on top of the armor
```

This progression should always remain bound by safety and human approval.

## Model-independent architecture

The system should not depend on one LLM.

Different LLMs can occupy different roles:

```text
ChatGPT -> operator / planner / analyst
Gemini  -> auditor / extractor / long-context reviewer
Claude  -> code reviewer / implementation critic
local model -> cheap classifier / summarizer
```

Roles are not authority.

The same safety protocol must apply to all models:

- no secrets by default;
- no direct merge;
- no direct deploy;
- no autonomous canon promotion;
- no arbitrary shell;
- no permission escalation through skill files;
- all critical changes go through reviewable artifacts.

## External memory and context bootstrap

The product should reduce dependence on any one chat window.

Target concept:

```text
new LLM chat opens
-> reads entry protocol
-> requests context pack
-> loads current state from user-owned memory hub
-> acts only within its assigned role
```

The memory should live outside the LLM chat:

```text
GitHub = public canon and reviewable project history
VPS / local server = private runtime memory and state
LLM chat = temporary reasoning window
```

Possible layers:

```text
L0 GitHub Canon
L1 Current State
L2 Operational Diary
L3 Project Memory
L4 Retrieval Index / Context Packs
L5 Private Sensitive Store
```

Sensitive memory and secrets must remain protected and must not be exposed to LLMs by default.

## Possible clean Skeleton core components

A reusable clean core may include:

- entry protocol;
- memory policy template;
- canon folder template;
- issue/task protocol;
- label/state machine template;
- provider health / routing layer;
- read-only audit routes;
- bounded PR creation route;
- skills folder structure;
- context pack generator;
- setup wizard;
- Docker Compose deployment template;
- sample GitHub Actions validation;
- example configs without real secrets;
- human approval gates.

## Boundaries and non-goals

This idea does not mean:

- publishing the current private repository as-is;
- exposing private user memory;
- exposing secrets;
- giving LLMs root/SSH access;
- creating an autonomous self-modifying agent;
- bypassing GitHub PR review;
- merging or deploying without human approval;
- treating Jeeves and Skeleton as the same project.

King Armor is a possible clean deployable Skeleton foundation.

Jeeves remains a separate future assistant/product that may use this foundation or share components with it.

## Proposed future roadmap placement

Suggested placement after current Skeleton trust-layer work:

```text
Sprint 12 — LLM Provider Health / Routing Layer
Sprint 13 — External Memory / Context Bootstrap
Sprint 14 — AI Planning Layer
Sprint 15 — Evaluation / Judge Layer
Sprint 16 — Skills Layer
Sprint 17 — LLM Node Registry
Sprint 18 — Remote Operator Layer
Sprint 19 — Worktree Isolation Layer
Later — Clean Skeleton Core Extraction / King Armor prototype
Later — Jeeves construction using mature Skeleton capabilities
```

The clean extraction should happen only after enough of the private Skeleton has matured to identify stable abstractions.

Jeeves construction should happen only when the Skeleton is strong enough to support planning, memory, evaluation, audit, and controlled implementation.

## Classification

- King Armor / clean Skeleton core product idea: IDEA_BACKLOG
- model-independent Skeleton direction: LIKELY_NEEDS_REVIEW -> CONFIRMED_CANON-compatible
- context-window-first entry path: LIKELY_NEEDS_REVIEW
- external memory / context bootstrap: LIKELY_NEEDS_REVIEW
- public clean-room extraction: IDEA_BACKLOG
- game-like progression model: IDEA_BACKLOG as UX framing
- Skeleton as bootstrapping harness for Jeeves: LIKELY_NEEDS_REVIEW -> CONFIRMED_CANON-compatible
- no direct publication of private workspace: CONFIRMED_CANON-compatible
- distinction between Skeleton and Jeeves: CONFIRMED_CANON-compatible

## Working principle

```text
Do not build a magical autonomous agent.
Build user-owned memory, roles, permissions, audits, skills, and reviewable growth around replaceable LLMs.

Do not clean and publish Jeeves.
Extract a clean, reusable Skeleton core when the private Skeleton is mature enough.

Use the growing Skeleton as the tool that can eventually help build Jeeves safely.
```

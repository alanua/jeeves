# Recovery audit: ChatGPT memory overflow branch

Date: 2026-05-01
Mode: JEEVES_BRANCH_RECOVERY_MODE
Status: CONFIRMED_CANON audit note
Source type: current chat branch + pasted ChatGPT/project memory snapshot
Last consolidated: 2026-05-03

## Purpose

This audit records what was extracted from a noisy memory-overflow branch. It does not copy the whole branch. It separates durable Jeeves canon from project-specific facts, private/sensitive details, backlog ideas, and items that should stay out of compact assistant memory.

This file is historical audit evidence. If any startup-memory text here conflicts with current boot files, current boot files win:

```text
knowledge_base/START_HERE_FOR_CHATGPT.md
knowledge_base/MEMORY_POLICY.md
knowledge_base/WORKING_PROTOCOL.md
knowledge_base/CHATGPT_BRANCH_CONTINUITY_BOOT.md
knowledge_base/assistant_diary.md
knowledge_base/assistant_startup_prompt.md
```

## Important correction from the user

The user clarified that not every message in a recovery branch is an instruction.

User messages may be:
- explicit decisions
- brainstorming
- advice-seeking
- raw memory dumps
- old context
- project-specific facts
- private administrative details
- temporary troubleshooting

Therefore, recovery processing must analyze all supplied messages, but only durable, reviewed, non-sensitive conclusions should be promoted into the knowledge base.

Classification: CONFIRMED_CANON

## CONFIRMED_CANON: Jeeves identity and behavior

1. Jeeves is intended as a universal personal/workspace assistant that can be deployed for different people and then adapt to its companion over time.
2. The user’s current collaboration with ChatGPT is a behavioral prototype for Jeeves.
3. ChatGPT should act as architect/reviewer; Codex/other agents act as executors; the user remains operator/final controller.
4. The assistant should give short, practical, human-readable reports.
5. The assistant should minimize user actions and ask only for critical decisions, missing inputs, credentials, or permissions.
6. The assistant should not use repeated onboarding phrases or award/expert intros.
7. The assistant should answer in the user’s language.
8. The assistant must distinguish brainstorming from confirmed decisions.
9. The user wants continuity across conversations without repeated reconfiguration.

## CONFIRMED_CANON: Memory model

1. ChatGPT/project memory is working memory, not the official source of truth.
2. GitHub knowledge base is the durable canonical layer after review/approval.
3. Long-term Jeeves memory should be wiki-first: Markdown wiki + structured JSON/YAML facts + logs/evals.
4. Raw chat exports, old chat branches, screenshots, transcripts, and pasted memory dumps are historical evidence only.
5. MemPalace may be tested as optional raw/verbatim retrieval and wake-up/session diary memory, not canonical truth.
6. LightRAG/RAG may be added later as retrieval support, not as the canonical source.
7. Memory must be compacted: many scattered assistant memories should be replaced by a short startup reference plus structured KB documents.
8. Temporary logs, one-off troubleshooting, old implementation fragments, and private finance details should not pollute compact assistant memory.

## CONFIRMED_CANON: Branch recovery workflow

1. `JEEVES_BRANCH_RECOVERY_MODE` means process the supplied branch as a historical source.
2. All messages in the branch should be considered, but not blindly canonized.
3. Extract only durable items: identity, architecture, memory, security/policy, controlled self-improvement, agent pipeline/department, behavior/UX rules, concrete decisions, rejected/outdated ideas, backlog ideas.
4. Classify each extracted item as `CONFIRMED_CANON`, `LIKELY_NEEDS_REVIEW`, `IDEA_BACKLOG`, or `OUTDATED_REJECTED`.
5. Prefer small docs-only KB updates.
6. Report briefly in the user’s requested format.

## CONFIRMED_CANON: Architecture direction

1. Jeeves should be a local/server-first controlled workspace orchestrator.
2. The current runnable baseline is the small Stage-1 vertical slice: API, orchestrator, policy gate, task classification, bounded session memory, provider routing, DB traces.
3. The earlier target v1 map is strategic architecture, not the current runnable bootstrap.
4. Long-term strategic components may include LangGraph-style orchestration, MCP/tool plane, OpenHands/coding sidecar, Langfuse-like observability, browser worker, and custom policy/approval layer.
5. The target workspace structure is:
   - `workspace.md`
   - `project.md`
   - `wiki/`
   - `structured_facts/`
   - `tasks/tasks.yaml`
   - `agent_profiles/`
   - `skills/`
   - `workflows/`
   - `tools/`
   - `agent_runtime/`
   - `logs/`
   - `handoff.md`

## CONFIRMED_CANON: Agent/team workflow

1. Start with simple single-agent operation.
2. Add complexity progressively: reflection/reviewer, router, tool layer, scheduler, observability, specialist agents, read-only subagents, then controlled agent teams.
3. Agent teams are useful only for tasks with real benefit from parallel research, coordinated coding, review/fix loops, synthesis, or artifact generation.
4. Multi-agent work should be artifact-driven through `agent_runtime/`, not hidden chat-only coordination.
5. For complex development use contract-first spawning: research -> implementation plan -> schema/API/shared contract -> safe parallel work -> review/validation -> handoff.
6. Avoid launching many agents without workspace, tasks, tests, logging, cost boundaries, approvals, and graceful shutdown.

## CONFIRMED_CANON: Security and governance

1. Default posture: zero trust.
2. No real banks, production email control, production GitHub secrets, production DBs, or destructive tools for early Jeeves.
3. Browser/computer-use only in sandbox/isolated profiles.
4. No unreviewed GitHub skills/scripts.
5. Skills/plugins/tools require allowlists and permissions.
6. Human approval is required for write/delete/network/secrets/destructive actions.
7. Controlled self-improvement must follow: observe -> detect -> propose -> validate -> approve -> apply -> monitor -> rollback.
8. No autonomous self-rewrites or silent policy changes.

## CONFIRMED_CANON: Observability/evals

1. Observability is a core requirement, not a late add-on.
2. Track agent/model/tool/retriever calls, latency, cost, tokens, errors, input/output summaries, retrieved docs, approvals, and quality/eval notes.
3. Langfuse/self-hosted observability is preferred for privacy-sensitive use.
4. LangSmith/LangChain can be reference/prototype material, not mandatory core.
5. Good/bad runs should become datasets/evals.

## CONFIRMED_CANON: LLM/provider strategy

1. Jeeves should not depend on one corporate chat UI.
2. Use provider interfaces and smart routing.
3. Local/cheap models can handle private/simple/routine tasks.
4. Cloud frontier models handle hard reasoning, planning, architecture, review, and complex coding.
5. Fallback must be explicit and logged.
6. ChatGPT Plus/Pro is useful for the human operator’s interactive work, but external Jeeves runtime should use API billing or provider APIs, not assume subscription access as a backend.

## LIKELY_NEEDS_REVIEW: Project-specific memories not promoted into this Jeeves startup file

The pasted memory snapshot contains many valid but separate project memories:
- BauClock product architecture and legal-hardening details.
- BauClock UI/style decisions.
- Gewerbe accounting/administrative workflow.
- Lavalamp/ESP32/WLED architecture.
- Homelab/Proxmox/Home Assistant context.
- Android TV/device troubleshooting.

These may be useful, but they should live in their own project KB sections, not in the compact Jeeves startup prompt.

## SENSITIVE / DO NOT STORE IN PUBLIC JEEVES KB RAW

The pasted memory included private/administrative items such as finance, bank flows, invoices, insurance, Gmail/support correspondence, and personal business details.

Do not copy those raw details into a public Jeeves repository.

If needed, store them only in a private accounting/admin KB with redaction and explicit purpose.

## IDEA_BACKLOG

1. Use ChatGPT export as the first practical test of the wiki-first memory recovery pipeline.
2. Build a startup/wake-up procedure where Jeeves reads its latest startup prompt/handoff before work.
3. Add structured facts for behavior rules, project canon, workflows, and agent policies.
4. Add a memory-pruning workflow that proposes which ChatGPT memories can be removed after KB consolidation.
5. Add a future bridge where Jeeves can prepare context packs for ChatGPT conversations.

## OUTDATED_REJECTED / Do not canonize

1. Do not treat OpenClaw as the full architecture base.
2. Do not treat marketing claims about autonomous corporations, game-changing agent teams, or no-code agent companies as architecture truth.
3. Do not copy Claude-specific tmux/iTerm/settings as core Jeeves architecture.
4. Do not use third-party key sellers or block-circumvention tricks as canonical access strategy.
5. Do not store secrets in Markdown or prompts.
6. Do not treat every user message as a direct instruction.

## Resulting startup memory replacement

The compact assistant memory should be reduced to something like:

```text
For all work with Oleksii, treat the ChatGPT settings prompt as a bootloader, not memory. First use `alanua/jeeves` GitHub KB as external long-term memory. Start from `knowledge_base/START_HERE_FOR_CHATGPT.md`; also read `MEMORY_POLICY.md`, `WORKING_PROTOCOL.md`, and `CHATGPT_BRANCH_CONTINUITY_BOOT.md`; for Jeeves/OpenClaw work also read `assistant_startup_prompt.md`; public-safe diary is `assistant_diary.md`. Use Google Drive private memory hub when private context is needed. GitHub KB is public-safe canon after review; Drive is private working memory; ChatGPT memory is weak cache only. User messages are evidence to analyze, not automatic instructions. `КОД <project>` means create/update runner-readable task files. Keep answers short, Ukrainian when user writes Ukrainian, task-driven, safe.
```

## User action

No immediate user action is required unless the user wants to manually prune ChatGPT saved memories now.

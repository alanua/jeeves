# 08 — Model Provider and Skills Strategy

Last updated: 2026-04-24

## Evaluation stance

The project treats model and ecosystem claims conservatively.

Principles:
- evaluate practical architectural fit, not hype
- require verification before major platform decisions
- do not rewrite the core around a new model provider
- benchmark models against actual Jeeves tasks

## Current model/provider shortlist

Future cloud-provider benchmark candidates for coding and agent tasks:
- GPT-5.4
- GLM-5.1
- MiniMax M2.7

These are candidates for future evaluation, not automatic replacements.

## Local model stance

Large open-weight models are interesting but may not fit the current local hardware constraints.

Local models should be evaluated only when:
- a realistic quantized build exists
- memory/latency requirements fit available hardware
- the task is appropriate for local inference

## Provider routing direction

Provider strategy should remain part of explicit runtime configuration and routing.

Accepted goals:
- local-first where practical
- cloud fallback when needed
- provider choice threaded through canonical request/runtime path
- no decorative provider fields that do not affect execution

## Skills strategy

Public skill repositories are useful as pattern sources, not direct dependencies.

Potential sources to curate from:
- Anthropic skills
- Vercel agent skills
- UI/UX skill repositories

Accepted approach:
- curate small repo-local skills
- keep skills auditable
- prefer project-specific skills over large generic imports
- do not mass-import third-party skill packs blindly

## Future repo-local skill candidates

Useful future skills may include:
- Stage closeout review
- coordination audit
- action-contract audit
- memory handoff builder
- release hygiene check
- provider benchmark runner
- UI/UX review for generated interfaces
- security and permission-model review

## Important boundaries

Skills are not allowed to bypass:
- policy checks
- approval gates
- canonical runtime contracts
- tests

Skills should improve repeatability, not become hidden architecture.

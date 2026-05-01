# Lavalamp / WLED / ESP32 — Decisions

Status: CONFIRMED_CANON
Last consolidated: 2026-05-01

## Confirmed decisions

- Use BauClock-style task-driven collaboration model: user = operator, ChatGPT = architect/reviewer, Codex = executor.
- Architecture must separate geometry, physics, render, and WLED integration.
- Coordinate transform should be decoupled from effect kernel.
- Cylindrical shell mapping is a core concept.
- Performance must be considered early because ESP32 render loop can be starved.
- Do not mix physical simulation, coordinate mapping, and optical/render tuning in one uncontrolled change.

## Rejected / cautions

- Do not keep increasing sampling/complexity without performance validation.
- Do not treat a visually static image as success.
- Do not merge unrelated refactors into effect tuning tasks.

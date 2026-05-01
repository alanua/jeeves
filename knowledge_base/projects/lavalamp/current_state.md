# Lavalamp / WLED / ESP32 — Current State

Status: PUBLIC_SAFE_SUMMARY
Last consolidated: 2026-05-01

## Current state

Project goal: visually convincing lava-lamp / anemone-like animation inside a transparent cylindrical tube using WLED/ESP32.

Current architectural rule:

```text
geometry -> physics -> render -> WLED integration
```

Current known constraints:
- ESP32 performance is limited.
- Deep sampling/noise can starve render loop.
- Effects must remain visible and optically convincing on a cylinder.
- Coordinate transform should be separated from effect kernel.

## Current workflow

Use `КОД ЛАВ` for precise Codex tasks and `СТАН ЛАВ` for handoff after meaningful work.

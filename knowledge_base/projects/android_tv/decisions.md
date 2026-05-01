# Android TV / Device Experiments — Decisions

Status: PUBLIC_SAFE_CANON
Last consolidated: 2026-05-01

## Confirmed decisions

- Treat Android TV/device work as an experimental side project with high risk of boot/device breakage.
- Work step-by-step with verification after each change.
- Prefer reversible boot configuration changes where possible.
- Use ADB/logs/device state as evidence before making further changes.
- Personal media-app experiments must remain for personal use and should avoid distribution/rights issues.

## Cautions

- Do not issue destructive partition/format commands without explicit intent.
- Do not assume one Android/x86 image fits all hardware.
- Do not mix BIOS/bootloader recovery with app-level troubleshooting in one uncontrolled step.

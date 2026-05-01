# BauClock — Current State

Status: CONFIRMED_CANON
Last consolidated: 2026-05-01

## Current state

BauClock is treated as a standalone product, not as SEK-branded internal tooling.

The active development model:
- User = operator / product owner
- ChatGPT = architect / reviewer / task framer
- Codex = implementation executor
- Lovable = dashboard/UI executor when appropriate

## Current product focus

Core focus:
- construction time tracking
- QR/GPS-based site check-in
- company/site/worker model
- owner/objektmanager/accountant/worker roles
- subcontractor/Gewerbe support
- overtime/payment support
- auditability and dispute resistance
- dashboard and Telegram/Mini App UX

## Current architecture focus

Do not overbuild full payroll or full accounting engine in v1.

Prioritize:
- dashboard token security
- role isolation
- audit logging
- manual correction traceability
- retention/privacy rules
- export boundaries
- clear module separation

## Current UI focus

- BauClock name instead of SEK system identity
- Material-style icons instead of letter badges
- collapsible cards/blocks
- reduced border radius compared with earlier UI
- cleaner, flatter mobile-first dashboard

## Current memory rule

Public-safe decisions live in GitHub KB.
Private business/accounting/client details should go to Google Drive private memory, not public GitHub.

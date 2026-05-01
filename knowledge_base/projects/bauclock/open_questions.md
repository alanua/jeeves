# BauClock — Open Questions

Status: LIVING_DOCUMENT
Last consolidated: 2026-05-01

## Product/business

- What is the minimal v1 package for first real clients?
- Which features belong to core subscription vs add-ons?
- How much invoice/payment support is enough for Gewerbe v1 without becoming a full accounting/payroll tool?
- What should be the first paid onboarding flow?

## Legal/Germany

- What exact ArbZG checks should v1 implement?
- What retention periods should be default vs configurable?
- What DATEV/export scope is enough for early version?
- What DPA/AVV/TOMs/privacy notice templates are needed first?

## Roles/access

- What precise permissions should accountant, objektmanager, owner, and worker have in v1?
- Which sensitive screens should auto-clear after inactivity?
- What role changes require audit entries?

## Multi-company sites

- What is the minimal master-site/master-QR implementation?
- How should late merging of separately created site contours work?
- How should partner/subcontractor visibility be represented in dashboard?

## UI/UX

- What is the final icon pack?
- What blocks should be collapsible first?
- What is the minimal unauthorized screen for shared bot?
- How much dashboard functionality should live in Telegram Mini App vs web dashboard?

## Implementation

- What is the current codebase state and next safe Codex task?
- Which existing overloaded flags/permissions need refactoring first?
- What tests are required before changing role/access logic?

# BauClock — Decisions

Status: CONFIRMED_CANON
Last consolidated: 2026-05-01

## Product identity

- BauClock is the standalone product name.
- SEK Zeiterfassung should not remain the system/product name.
- SEK may exist only as a first client/tenant/legacy example.

## Canonical model

- Core model: company -> site -> person/worker -> time events -> summaries/payments/export.
- Target identity model: `person + company_membership`.
- Implementation may transition gradually through the current `worker` layer.
- Contract workers should be active in only one company at a time.
- Gewerbe can be modeled as its own company profile and can join sites as subcontractor/partner.

## Site / QR direction

- Target multi-company model: one physical site moves toward one master QR/master site.
- General contractor/company owner can invite subcontractor companies to join an existing site.
- Subcontractor can track own people in own context while connected to the shared site.
- If separate site/QR contours must later merge, master/general contractor site becomes primary.

## Roles

- Objektmanager is optional.
- Owner can assign/remove objektmanager per site.
- Accountant can be internal or external.
- External accountant may support multiple companies with scoped access.
- Accountant can record payment date, paid amount, and payment comment, but should not normally change rates/terms unless explicitly delegated.

## Privacy/access

- Privacy-by-business-logic is canonical.
- Each bot/role sees only the legitimate minimum data.
- Sensitive UI blocks should auto-hide/clear after inactivity where appropriate.
- Public/unauthorized screens should not expose company/system data.

## Legal-hardening for Germany

- Do not rebuild the whole model; harden it.
- Required: access control, audit logs, manual correction traceability, ArbZG checks, retention/privacy layer, export boundaries.
- Do not overbuild full payroll engine in early v1.

## UI/design

- Use BauClock branding.
- Replace letter badges with Material-style icons.
- Use warm sand/white card/black text/orange-red accent style direction.
- Main cards should be collapsible.
- Reduce border radius compared with earlier overly rounded UI.

## Bot strategy

- `@gewerbebot` is platform/personal contour for platform superadmin and user’s own Gewerbe.
- `@SEKbaubot` is SEK client contour only.
- `@bauuhrbot` is the shared client bot for new companies by default.
- Dedicated company bots are optional for branded clients.

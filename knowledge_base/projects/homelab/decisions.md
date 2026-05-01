# Homelab / Proxmox / Home Assistant — Decisions

Status: PUBLIC_SAFE_CANON
Last consolidated: 2026-05-01

## Confirmed decisions

- Use Proxmox as primary homelab virtualization platform.
- Prefer Home Assistant OS in VM when add-ons and full HA flexibility are desired.
- Keep service deployment modular: VM/LXC/container depending on service needs.
- Treat Tailscale/remote access as useful but security-sensitive.
- Do not put secrets, keys, private IPs, or exposed service URLs in public GitHub.

## Cautions

- Do not make infrastructure changes without backups/rollback plan.
- Do not expose services publicly without explicit security review.

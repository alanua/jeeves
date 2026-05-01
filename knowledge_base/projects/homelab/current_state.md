# Homelab / Proxmox / Home Assistant — Current State

Status: PUBLIC_SAFE_SUMMARY
Last consolidated: 2026-05-01

## Current state

Homelab work covers local server infrastructure, Proxmox, Home Assistant, LXC/VM services, storage, networking, and remote access.

Public-safe baseline:
- Proxmox is the host direction.
- Home Assistant OS should run as VM where full add-on flexibility is needed.
- LMS and other services may run as LXC/VMs where appropriate.
- Remote access and domain/subdomain work must be handled safely.

## Security note

Do not store secrets, keys, passwords, private IPs, or live exposed URLs in public KB.

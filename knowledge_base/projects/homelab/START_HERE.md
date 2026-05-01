# Homelab / Proxmox / Home Assistant — START HERE

Status: CONFIRMED_CANON
Project alias: `ХЛ` / `HL`
Scope: public-safe startup file for homelab/server infrastructure.
Last consolidated: 2026-05-01

## Purpose

Read this file when work is about the homelab server, Proxmox, Home Assistant, LXC/VMs, LMS, local services, networking, domain/subdomain setup, Tailscale, storage, or hardware expansion.

Global startup files:
- `knowledge_base/START_HERE_FOR_CHATGPT.md`
- `knowledge_base/MEMORY_POLICY.md`
- `knowledge_base/WORKING_PROTOCOL.md`

## Privacy/security rule

Do not store secrets, passwords, private IPs, tokens, Cloudflare/API credentials, SSH keys, exposed service URLs, or full private network topology in public GitHub.

Use Google Drive private memory for private infrastructure notes if needed. Use secret manager/local encrypted storage for credentials.

Use `ПРИВ ХЛ` for private infrastructure context.

## Working model

- User = operator / final controller
- ChatGPT = architect / reviewer / task framer / troubleshooting guide
- Runner = execution bridge when a structured task file is needed
- Runtime = local homelab / Proxmox / services

Work step-by-step. Prefer one diagnostic/action at a time when troubleshooting live systems.

## Executor workflow

For `КОД ХЛ`, only create runner-readable task files when they are public-safe or properly redacted.

Do not put secrets, tokens, internal IPs, SSH details, Cloudflare credentials, or sensitive topology into public GitHub task files.

Correct flow when a task file is appropriate:

```text
ChatGPT creates or updates redacted runner-readable task file
-> runner reads task file
-> runner gives task to executor
-> runner returns redacted result/logs/handoff
-> ChatGPT reviews and updates KB/handoff
```

## Known baseline

Primary homelab direction includes:
- Proxmox as host platform
- Home Assistant OS in VM
- LXC/VM services where appropriate
- local-first automation and media/server experiments
- Tailscale/remote access only with safety checks

## Startup command

```text
СТ ХЛ
```

## Standard files

- `current_state.md`
- `decisions.md`
- `open_questions.md`
- `tasks.md`
- `handoff.md`
- optional `executor_tasks/` only for public-safe/redacted runner-readable task files

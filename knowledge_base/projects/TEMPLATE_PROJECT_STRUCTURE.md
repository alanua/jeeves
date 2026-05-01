# Template Project Structure

Status: CONFIRMED_CANON
Last consolidated: 2026-05-01

## Purpose

Every active project should use the same public-safe KB structure so ChatGPT and future Jeeves can load context predictably.

## Files

### START_HERE.md
Project-specific entry point. Contains identity, scope, aliases, startup command, and links to related files.

### current_state.md
Current public-safe status. No raw private data.

### decisions.md
Confirmed decisions and rejected/superseded ideas.

### open_questions.md
Unresolved questions to answer gradually.

### tasks.md
Active and next tasks.

### handoff.md
Short active handoff for the next session.

### executor_tasks/ or codex_tasks/
Optional folder for runner-readable task files. Use it when `КОД <project>` is invoked.

These files are for the runner, not for the user to manually copy into Codex.

## Rules

- Keep project memory separated.
- Public-safe durable canon goes to GitHub.
- Private context goes to Google Drive.
- Secrets and credentials go to neither plain GitHub nor plain Drive.
- End important sessions with `СТАН <project>`.
- Start serious project sessions with `СТ <project>`.
- `КОД <project>` means create/update a runner-readable task file.
- Runner passes tasks to Codex/executor and returns result/logs/handoff.
- Do not tell the user to manually pass tasks to Codex when runner workflow is available.

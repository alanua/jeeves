# Agent Worktree Protocol

Status: LIKELY_NEEDS_REVIEW
Scope: Skeleton / ChatGPT Exoskeleton protocol for parallel AI-agent development
Created: 2026-05-12
Source issue: #165

## Purpose

This protocol defines how Skeleton should use Git worktrees for parallel AI-agent development.

The goal is to keep the main control checkout clean while allowing bounded executor tasks to work in isolated Git working directories.

This is a Skeleton protocol. It is not Jeeves runtime behavior and does not grant merge, deploy, production, server, database, or secret access.

## Core rule

```text
One issue = one branch = one worktree = one reviewable PR/diff.
```

The main checkout remains the control plane. Executors work inside task-specific worktrees.

## Control checkout vs task worktree

```text
Control checkout
-> runner/orchestrator state
-> queue inspection
-> PR review
-> coordination
-> must stay clean

Task worktree
-> one bounded issue task
-> one branch
-> one reviewable diff or PR
-> removable after completion
```

Do not run code-modifying executor tasks directly in the main control checkout.

## Isolation limits

Git worktrees isolate Git working directories and branch state. They reduce checkout-level conflicts, but do **not** isolate runtime resources, secrets, databases, ports, processes, caches, or virtual environments.

Worktree isolation is not sandboxing. Any task that starts services, tests with shared databases, uses Docker, touches Redis, uses shared caches, or depends on `.venv`/environment state needs separate runtime isolation rules.

## Read-only audits

Read-only audits do not require a worktree when they only read GitHub/files and post a report.

Use a temporary read-only checkout or worktree only if local tests, static analysis, grep, or tool execution needs a filesystem tree.

Pure audits do not create branches or PRs.

## Test-only and code tasks

Worktree use is mandatory for test-only and code-changing tasks.

Test-only tasks must remain test-only. If a production bug is discovered during a test-only task, the executor must stop and report the bug instead of fixing production code in the same task.

## Cleanup safety

After a PR is opened and the worktree is no longer needed:

```bash
git worktree remove <task-worktree-path>
git worktree prune
git branch -d <local-task-branch>
```

Use `git branch -d`, not `git branch -D`, unless it has been explicitly verified that all local-only commits were pushed or intentionally discarded.

Delete the local branch only after the PR branch is pushed and no local-only commits remain.

## Forbidden actions

```text
No nested worktrees.
No `.env` copying, symlinking, committing, or printing.
No secrets in repository files, prompts, logs, or public reports.
No direct merge from a worktree.
No deploy from a worktree.
No production/server/database access because a worktree exists.
No out-of-scope fixes inside a worktree task.
No treating worktree isolation as runtime/container isolation.
```

## Recommended naming

```text
Branch: docs/issue-<number>-<short-topic>
Branch: test/issue-<number>-<short-topic>
Branch: fix/issue-<number>-<short-topic>

Worktree path: ../agent-worktrees/<repo>-issue-<number>-<short-topic>
```

Use the issue number in the branch and worktree path so stale worktrees can be audited and cleaned.

## Pre-PR checklist

Before opening a PR from a worktree:

```text
[ ] Scope matches the issue.
[ ] Main/control checkout was not mutated.
[ ] No runtime/production/server action was performed unless explicitly authorized.
[ ] No secrets, `.env`, tokens, private infrastructure data, or credentials appear in the diff or report.
[ ] Validation ran, or skipped validation is explained.
[ ] PR body lists changed files, validation, and safety confirmation.
```

## Relationship to runner implementation

This document is a protocol only. Runner code must not be changed merely because this file exists.

A separate reviewed implementation task is required before `yellow_runnerd` or any runner wrapper starts creating worktrees automatically.

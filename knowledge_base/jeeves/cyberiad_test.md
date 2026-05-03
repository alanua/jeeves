# Cyberiad Test for Jeeves

Status: CONFIRMED_CANON
Scope: Jeeves behavior, safety, controlled autonomy, and controlled self-improvement
Recorded: 2026-05-03

## Summary

The Cyberiad Test is a compact engineering metaphor for Jeeves safety.

When a Jeeves capability looks like a brilliant Trurl-style invention, the system must immediately activate a Klapaucius-style critic: skeptical review, literal-execution analysis, failure simulation, authority limitation, policy checks, tests, logs, and rollback planning.

This is not a literary feature. It is a safety and design heuristic for agent behavior.

## Canonical rule

Before granting more autonomy, tool access, self-improvement ability, or executor authority, Jeeves must pass the Cyberiad Test:

```text
If this agent executes the instruction literally, optimizes the wrong thing, overgeneralizes, or becomes too confident, what can break?
```

The answer must be turned into constraints before execution:

```text
risk -> boundary -> test -> approval gate -> logging -> rollback path
```

## Applies to

- autonomous planning
- tool use
- browser/computer-use
- code generation
- executor delegation
- memory writes
- knowledge-base canonization
- controlled self-improvement
- policy changes
- multi-agent orchestration

## Required checks

For any powerful or persistent action, the lead/orchestrator must ask:

1. What is the literal but wrong interpretation?
2. What is the cheapest safe sandbox version?
3. What authority does the agent not need?
4. What data must not be touched?
5. What must be logged for later audit?
6. What test proves this did not degrade behavior?
7. What is the rollback path?

## Relationship to controlled self-improvement

The Cyberiad Test reinforces the existing self-improvement chain:

```text
observe -> detect -> propose -> validate -> approve -> apply -> monitor -> rollback if needed
```

It does not replace the chain. It is a pre-flight skepticism layer before autonomy or self-modification expands.

## Classification

CONFIRMED_CANON.

Reason: user explicitly confirmed the principle after discussion; it is public-safe, durable, and consistent with the existing Jeeves security and controlled self-improvement canon.

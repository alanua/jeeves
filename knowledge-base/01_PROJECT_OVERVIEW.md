# 01 — Project Overview

## Project identity

**Name:** Jeeves

**Working concept:** a personal local-first multi-agent assistant system with an OpenClaw-style direction, but without blind copying of OpenClaw.

## Product thesis

The project is built on the belief that durable value does not come only from the model itself. The real product layer is the runtime shell around the model:
- context
- memory
- tools
- permissions
- integrations
- deterministic orchestration
- handoff continuity

## Intended role of Jeeves

Jeeves is intended to be the top-level assistant that:
- receives user requests
- routes work into specialized agents or future subsystems
- preserves continuity across sessions
- accumulates reusable skills and structured knowledge
- eventually operates real workflows under policy and approval gates

## Design posture

The project prefers:
- local-first execution where practical
- cloud fallback where necessary
- typed canonical contracts
- deterministic runtime orchestration instead of prompt-only control
- explicit boundaries between internal runtime objects and external API / trace shapes
- conservative rollout of real-world side effects

## What Jeeves is not

At its current stage, Jeeves is not:
- a general autonomous self-modifying system
- a production action engine with real side effects
- a pure prompt wrapper around a single model
- a memory-only system
- a knowledge-base-only system

## Project layers at a glance

The long-term architecture is understood as a set of cooperating layers:
- API / ingress
- routing
- orchestration
- specialized agents
- policy / permissions
- memory / handoff continuity
- knowledge-base / research wiki
- action-contract / approval-gated execution
- repo-local skills
- future browser-use / computer-use capabilities

## Current maturity snapshot

As of the latest accepted project state:
- Stage 1 foundation is closed.
- Stage 2 hybrid coordination is live.
- Execution-aware hybrid with dry-run executor is live.
- Action-layer canonical contracts exist, but are not yet live in the runtime.

## Continuation rule

Anyone continuing the project should assume:
1. the repo already contains meaningful architecture and tests;
2. behavior must be changed through small explicit passes;
3. current stable layers must not be destabilized by speculative feature work;
4. any future action capability must stay approval-gated and runtime-owned.

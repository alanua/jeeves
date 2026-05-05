# External LLM Harness Patterns

Status: IDEA_BACKLOG
Scope: public research note for ChatGPT Exoskeleton / Skeleton design, not Jeeves runtime canon
Created: 2026-05-05

## Purpose

This note captures nearby public ideas and patterns for the ChatGPT Exoskeleton.

The object of comparison is not Jeeves runtime. The object is the external support/control layer around ChatGPT:

```text
ChatGPT
-> external skeleton / harness
-> stable boot, memory, protocols, tools, audit, runner workflow
-> stronger collaboration loop for later Jeeves design/build work
```

This note is evidence and design input only. It is not a new policy document.

## Core framing

The strongest matching public framing is:

```text
externalization in LLM agents
external LLM harness
agent scaffold
context repository
memory filesystem
agent-computer interface
skills/protocols/harness engineering
```

The relevant pattern is to improve agent reliability not only by using a stronger model, but by moving state, procedures, protocols, tool control, audit, and recovery outside the model into a managed surrounding system.

## High-value references and usable Skeleton patterns

### 1. Externalization / harness engineering

Source:

```text
Externalization in LLM Agents: A Unified Review of Memory, Skills, Protocols and Harness Engineering
https://arxiv.org/abs/2604.08224
https://huggingface.co/papers/2604.08224
```

Useful idea:

```text
LLM agent capability increasingly comes from external memory stores, reusable skills, interaction protocols, and the harness that coordinates them into governed execution.
```

Skeleton fit:

```text
BOOT + memory router + runbook + runner workflow + audit = practical external harness around ChatGPT.
```

### 2. Git-backed context repositories / memory filesystem

Source:

```text
Letta Context Repositories / MemFS
https://www.letta.com/blog/context-repositories
https://docs.letta.com/letta-code/memory/
```

Useful idea:

```text
Agent memory can live as git-backed markdown files with versioning, progressive disclosure, and separate memory files for different topics.
```

Skeleton fit:

```text
GitHub KB already acts as public-safe canon memory.
The Skeleton should keep canon as reviewed docs, not uncontrolled auto-memory.
```

Difference from Skeleton:

```text
Letta allows agents to maintain memory more directly.
Skeleton should keep read-before-write, classification, verification, and user approval for durable canon changes.
```

### 3. Project memory / boot files

Source:

```text
Claude Code memory / CLAUDE.md / auto memory
https://code.claude.com/docs/en/memory
```

Useful idea:

```text
Each agent session starts with a fresh context window, so persistent startup files and auto memory are needed to carry project knowledge across sessions.
```

Skeleton fit:

```text
прокинься + BOOTLOADER.md + START_HERE_FOR_CHATGPT.md + CURRENT_STATE.md solves the same branch/session amnesia problem for ChatGPT collaboration.
```

### 4. Agent Skills as filesystem procedures

Source:

```text
Anthropic Agent Skills
https://docs.claude.com/en/docs/agents-and-tools/agent-skills
```

Useful idea:

```text
Skills are reusable filesystem-based packages with SKILL.md metadata, instructions, and optional resources that load when relevant.
```

Skeleton fit:

```text
Future Skeleton skills should be small procedural modules, not loose prompts:
when to use, allowed inputs, forbidden actions, sources to read, verification, expected output.
```

### 5. Agent-Computer Interface

Source:

```text
SWE-agent Agent-Computer Interface
https://swe-agent.com/0.7/background/aci/
```

Useful idea:

```text
Agents work better with LM-centric commands and feedback formats: bounded file viewing, concise search results, edit checks, explicit success output.
```

Skeleton fit:

```text
Runner should expose agent-facing operations, not raw uncontrolled shell/computer access.
Good runner interface = short outputs, scoped reads, diffs, checks, verification, rollback-friendly behavior.
```

### 6. Durable execution / checkpointing

Source:

```text
LangGraph durable execution
https://docs.langchain.com/oss/python/langgraph/durable-execution
```

Useful idea:

```text
Long-running workflows need saved progress, resumability, human-in-the-loop checkpoints, and protection against repeating side effects after interruption.
```

Skeleton fit:

```text
CURRENT_STATE.md + GitHub issue checkpoints + handoff notes are the current docs-first version of durable execution for ChatGPT collaboration.
```

### 7. MCP as tool port, not trust boundary

Source:

```text
Model Context Protocol introduction
https://modelcontextprotocol.io/docs/getting-started/intro
```

Useful idea:

```text
MCP standardizes how AI applications connect to external tools and data sources.
```

Skeleton fit:

```text
MCP can be useful later as a tool connector layer.
It must sit below Skeleton policy: allowlist, privacy routing, permissions, audit, approval.
```

### 8. Guardrails and tracing

Source:

```text
OpenAI Agents SDK guardrails and tracing
https://openai.github.io/openai-agents-js/guides/guardrails/
https://openai.github.io/openai-agents-python/tracing/
```

Useful idea:

```text
Guardrails check inputs, outputs, and tool calls. Tracing records agent runs, LLM generations, tool calls, handoffs, guardrails, and custom events.
```

Skeleton fit:

```text
Skeleton guardrails are currently procedural:
read-before-answer, read-before-write, privacy routing, post-write verification.
Future runner/runtime layers should make these machine-enforced where possible.
```

## Pattern summary for Skeleton Stage 1

Keep the active Stage 1 loop small:

```text
BOOT
-> LOAD CANON
-> CLASSIFY
-> SMALL ACTION
-> VERIFY
-> CHECKPOINT
-> HANDOFF
```

Avoid expanding too early into full runtime implementation.

## Candidate later work

```text
1. Convert this research note into a compact Skeleton pattern table.
2. Create one small Skeleton skill spec for read-before-write or research-note creation.
3. Define a runner-facing Agent-Computer Interface shape for docs tasks.
4. Keep all of this separate from Jeeves runtime until explicitly switched.
```

## Current classification

```text
IDEA_BACKLOG
```

Reason:

```text
The public references support the current Skeleton direction, but they should not become canon architecture until reviewed and converted into specific Skeleton tasks or rules.
```

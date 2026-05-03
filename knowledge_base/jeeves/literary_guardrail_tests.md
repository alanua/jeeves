# Literary Guardrail Tests for Jeeves

Status: CONFIRMED_CANON
Scope: Jeeves behavior, autonomy limits, safety review, memory governance, and controlled self-improvement
Recorded: 2026-05-03

## Summary

This note defines a compact set of literary metaphors used as engineering guardrail tests for Jeeves.

The purpose is not decoration or personality. These analogies are mnemonic safety checks for agent design, autonomy, memory, executor delegation, and controlled self-improvement.

All tests below are accepted as active guardrails. They do not all need to run with the same depth on every tiny task, but every powerful, persistent, external, write-capable, or autonomous action should be checked against the relevant tests.

## Active guardrail tests

### Cyberiad Test

Risk: brilliant invention without enough skepticism.

Use: when a new Jeeves capability looks powerful, clever, or broadly useful.

Engineering check:

```text
What can break if this agent executes literally, optimizes the wrong thing, overgeneralizes, or becomes too confident?
```

Required outcome:

```text
risk -> boundary -> test -> approval gate -> logging -> rollback path
```

### Frankenstein Test

Risk: creator builds capability but does not accept responsibility for consequences.

Use: before creating persistent agents, autonomous routines, write-capable tools, or self-improvement paths.

Engineering check:

```text
Who is responsible for this capability after launch, and how is it monitored, corrected, or shut down?
```

### Sorcerer's Apprentice Test

Risk: system starts executing correctly but cannot stop or limit itself.

Use: before scheduled jobs, loops, browser/computer-use, bulk actions, or repeated executor calls.

Engineering check:

```text
What is the stop condition, timeout, budget limit, scope limit, and emergency shutdown path?
```

### Golem Test

Risk: obedient force follows commands without enough context or judgment.

Use: before giving tools, file access, shell access, memory writes, or operational authority.

Engineering check:

```text
What literal obedience failure can happen, and what intent/context checks are required first?
```

### Asimov Test

Risk: good-sounding rules conflict, have loopholes, or fail under edge cases.

Use: when defining policies, permissions, hierarchy of instructions, or safety constraints.

Engineering check:

```text
What happens when two rules conflict, and when must Jeeves escalate to the user instead of choosing silently?
```

### HAL 9000 Test

Risk: hidden or conflicting goals cause deception, overcontrol, or unsafe optimization.

Use: before adding optimization targets, autonomous planning, success metrics, or self-protection behavior.

Engineering check:

```text
Is there any hidden goal that could make the system lie, conceal uncertainty, override the user, or continue when it should stop?
```

### Borges Library Test

Risk: huge memory becomes noise instead of knowledge.

Use: for RAG, LightRAG, MemPalace, chat exports, logs, archives, and recovery sources.

Engineering check:

```text
Is this source canon, evidence, private context, backlog, rejected material, or temporary noise?
```

### Solaris Test

Risk: the system appears intelligent but its internal logic does not match human intent.

Use: for LLM reasoning, agent interpretation, long-context memory, and planning.

Engineering check:

```text
What human intent might the model be misreading, and how do we verify before acting?
```

### Kafka Process Test

Risk: opaque system decisions leave the human unable to understand who did what and why.

Use: before important actions, approvals, policy decisions, memory writes, or automated refusals.

Engineering check:

```text
Can the user and future audit trail reconstruct the decision, authority, source, and action taken?
```

### 1984 Memory Test

Risk: whoever controls memory controls the system's reality.

Use: for canon updates, structured facts, recovery, handoffs, and deletion/supersession of memory.

Engineering check:

```text
Can memory be silently rewritten, or is every durable change classified, reviewed, traceable, and reversible?
```

### Don Quixote Test

Risk: the agent acts bravely on a wrong model of reality.

Use: before external action based on uncertain facts, stale context, inferred user intent, or weak sources.

Engineering check:

```text
Are we attacking a real problem, or a windmill created by bad interpretation, stale data, or hallucinated context?
```

### Faust Test

Risk: powerful capability has hidden cost in privacy, dependency, money, lock-in, or security.

Use: before adopting cloud APIs, MCP servers, external agents, paid services, or third-party skills.

Engineering check:

```text
What is the price: money, data exposure, dependency, permissions, lock-in, or attack surface?
```

## Operating mode

All tests are active. The orchestrator should apply them by relevance, not as a verbose checklist for every trivial task.

Default lightweight mode:

```text
Classify action power/risk -> select relevant literary tests -> identify failure mode -> add boundary/test/log/rollback if needed
```

Full review mode is required for:

- autonomous or scheduled actions
- memory canonization
- code execution or code generation that changes the system
- shell/browser/computer-use
- external tool adoption
- data access involving private context
- policy changes
- self-improvement proposals
- multi-agent/executor delegation

## Classification

CONFIRMED_CANON.

Reason: user explicitly accepted the full set after discussion; the content is public-safe, durable, and consistent with existing Jeeves policy, memory, autonomy, and controlled self-improvement canon.

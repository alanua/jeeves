# 07 — Knowledge-Base Subsystem

Last updated: 2026-04-24

## Position of this subsystem

The future knowledge-base subsystem is a separate research and documentation layer.

It is not:
- runtime memory
- GitHub continuity insurance
- canonical code contracts
- a replacement for tests

## Accepted model

The accepted model is:

```text
raw evidence / docs / repos / images
-> LLM-compiled markdown wiki
-> agent Q&A and linting
-> derived outputs such as reports, slides, and visuals
```

Optional viewing tools:
- Obsidian
- Marp

## Why this matters

Jeeves development depends on ongoing research into:
- agent runtimes
- OpenClaw-style systems
- coding agents
- model/provider benchmarks
- memory architectures
- permission models
- action contracts
- browser-use / computer-use
- MCP and tool integration

A durable research wiki allows accumulated external evidence to be reused instead of rediscovered.

## Proposed future structure

A future knowledge-base subsystem may use:

```text
knowledge-system/
  raw/
    articles/
    papers/
    repos/
    images/
  wiki/
    index.md
    concepts/
    systems/
    providers/
    architecture-patterns/
  outputs/
    reports/
    slides/
    diagrams/
  lint/
    health-checks.md
    inconsistencies.md
```

## Accepted workflow

1. Ingest source material into `raw/`.
2. Let an LLM compile or update markdown wiki pages.
3. Maintain index files and backlinks.
4. Ask Q&A against the wiki.
5. Run health checks to detect contradictions and missing information.
6. Produce derived artifacts.
7. File useful outputs back into the wiki.

## Important separation from GitHub KB

The `knowledge-base/` directory in this repository is currently the project-continuation documentation layer.

The future research wiki is a broader research corpus and should not overwrite canonical project decisions unless the user explicitly accepts a decision.

## Safe implementation order

Do not build a large RAG system first.

Recommended order:
1. markdown structure
2. simple indexes
3. agent-readable summaries
4. lint / health-check prompts
5. small search CLI
6. only later vector retrieval if needed

# ChatGPT Bootloader

Main wake command:

```text
прокинься
```

This file is a tiny current ChatGPT-facing shim into the Skeleton prototype.

Active read order:
1. Read `knowledge_base/START_HERE_FOR_CHATGPT.md`.
2. Follow its global startup order.
3. Route into the active project only after the user names it.

Ontology rule:

```text
ChatGPT Exoskeleton = historical/current ChatGPT-facing prototype of Skeleton.
Unified Skeleton Core = target model-neutral external exoskeleton/control layer for LLM-assisted work.
ChatGPT = current host/interface for using the prototype.
Jeeves = separate future independent assistant/product.
```

Jeeves is not a Skeleton adapter. Jeeves is not runtime under Skeleton.

Old aliases remain valid, but `прокинься` is the preferred entrypoint.

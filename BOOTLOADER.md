# ChatGPT Bootloader

Main wake command:

```text
прокинься
```

This file is a tiny shim only.

Active read order:
1. Read `knowledge_base/START_HERE_FOR_CHATGPT.md`.
2. Follow its global startup order.
3. Route into the active project only after the user names it.

Namespace rule:

```text
Skeleton / ChatGPT Exoskeleton = ChatGPT-side external control/support layer.
Jeeves runtime = separate future runtime/code layer.
```

Do not treat Skeleton work as Jeeves runtime work just because both live in `alanua/jeeves`.

Old aliases remain valid, but `прокинься` is the preferred entrypoint.

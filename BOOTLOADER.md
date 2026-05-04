# ChatGPT Bootloader

Main wake command:

```text
прокинься
```

Meaning:
- wake up through the ChatGPT exoskeleton;
- read the global startup files first;
- load the general context across projects;
- do not assume the active project yet;
- wait for Oleksii to name the current project or continue with a global task.

Important namespace rule:

```text
The repo name `alanua/jeeves` is historical and can cause confusion.
Skeleton / ChatGPT Exoskeleton = external control/support layer around ChatGPT.
Jeeves runtime = separate future assistant runtime/code layer.
Do not treat Skeleton work as Jeeves runtime work just because both currently live in the same repository.
```

Required global startup files:

```text
knowledge_base/START_HERE_FOR_CHATGPT.md
knowledge_base/MEMORY_POLICY.md
knowledge_base/WORKING_PROTOCOL.md
knowledge_base/CHATGPT_BRANCH_CONTINUITY_BOOT.md
knowledge_base/assistant_diary.md
knowledge_base/chatgpt_exoskeleton/START_HERE.md
knowledge_base/CHATGPT_EXOSKELETON.md
knowledge_base/CHATGPT_EXOSKELETON_RUNBOOK.md
```

Project switch after wake:

```text
Skeleton -> use chatgpt_exoskeleton/START_HERE.md + CHATGPT_EXOSKELETON.md + CHATGPT_EXOSKELETON_RUNBOOK.md
Jeeves runtime -> use jeeves_runtime/START_HERE.md + assistant_startup_prompt.md + Jeeves project docs
BauClock / Gewerbe / Lavalamp / Homelab / Android TV / Van -> load the matching project context
```

Do not treat `прокинься` as a normal word. It is the main ChatGPT-side boot command.

Old aliases such as `СТ СК`, `СТ ДЖ`, `АУД СК`, and `БЗ СК` remain valid, but the preferred entrypoint is now `прокинься`.

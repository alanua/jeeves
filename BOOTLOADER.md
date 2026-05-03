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

Required global startup files:

```text
knowledge_base/START_HERE_FOR_CHATGPT.md
knowledge_base/MEMORY_POLICY.md
knowledge_base/WORKING_PROTOCOL.md
knowledge_base/CHATGPT_BRANCH_CONTINUITY_BOOT.md
knowledge_base/assistant_diary.md
knowledge_base/CHATGPT_EXOSKELETON.md
knowledge_base/CHATGPT_EXOSKELETON_RUNBOOK.md
```

Project switch after wake:

```text
Jeeves -> read assistant_startup_prompt.md and Jeeves project docs
Skeleton -> use CHATGPT_EXOSKELETON.md + CHATGPT_EXOSKELETON_RUNBOOK.md
BauClock / Gewerbe / Lavalamp / Homelab / Android TV / Van -> load the matching project context
```

Do not treat `прокинься` as a normal word. It is the main ChatGPT-side boot command.

Old aliases such as `СТ СК`, `СТ ДЖ`, `АУД СК`, and `БЗ СК` remain valid, but the preferred entrypoint is now `прокинься`.

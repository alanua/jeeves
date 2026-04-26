from __future__ import annotations

from enum import Enum


class TaskType(str, Enum):
    simple = "simple"
    general = "general"
    complex = "complex"
    coding = "coding"
    research = "research"


# Keywords that signal task type — simple heuristics, no ML needed at this stage.
_CODING_KEYWORDS = {
    "code",
    "function",
    "class",
    "bug",
    "debug",
    "implement",
    "python",
    "javascript",
    "typescript",
    "sql",
    "script",
    "program",
    "refactor",
}
_RESEARCH_KEYWORDS = {
    "research",
    "summarise",
    "summarize",
    "explain",
    "compare",
    "analyse",
    "analyze",
    "find out",
    "what is",
    "how does",
    "why does",
    "latest",
}
_COMPLEX_KEYWORDS = {
    "architecture",
    "design",
    "plan",
    "strategy",
    "system",
    "multi-step",
    "detailed",
    "comprehensive",
    "elaborate",
}


def classify_task(message: str) -> TaskType:
    """
    Classify a user message into a TaskType using keyword heuristics.

    This is intentionally simple and deterministic. Replace with a small
    classifier model in a future iteration if needed.
    """
    lower = message.lower()
    words = set(lower.split())

    if words & _CODING_KEYWORDS or any(kw in lower for kw in _CODING_KEYWORDS):
        return TaskType.coding
    if any(kw in lower for kw in _RESEARCH_KEYWORDS):
        return TaskType.research
    if any(kw in lower for kw in _COMPLEX_KEYWORDS):
        return TaskType.complex
    if len(message.split()) <= 15:
        return TaskType.simple
    return TaskType.general

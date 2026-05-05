"""Risk classification for Skeleton task packets."""

from tools.skeleton_core.models import RiskLevel, TaskPacket

RED_TERMS = (
    "secret",
    "token",
    "password",
    ".env",
    "ssh",
    "oauth",
    "production",
    "deploy",
    "payment",
    "bank",
    "health",
    "private document",
)

ORANGE_TERMS = (
    "code",
    "implement",
    "test",
    "cli",
    "package",
    "refactor",
)

YELLOW_TERMS = (
    "docs",
    "markdown",
    "note",
    "policy",
    "readme",
)


def _task_text(packet: TaskPacket) -> str:
    return f"{packet.title}\n{packet.body}".casefold()


def _contains_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(term.casefold() in text for term in terms)


def classify_task(packet: TaskPacket) -> RiskLevel:
    """Classify a task using conservative priority ordering."""
    text = _task_text(packet)

    if _contains_any(text, RED_TERMS):
        return RiskLevel.RED
    if _contains_any(text, ORANGE_TERMS):
        return RiskLevel.ORANGE
    if _contains_any(text, YELLOW_TERMS):
        return RiskLevel.YELLOW
    return RiskLevel.GREEN

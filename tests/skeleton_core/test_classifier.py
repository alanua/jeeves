from tools.skeleton_core.classifier import classify_task
from tools.skeleton_core.models import RiskLevel, TaskPacket


def test_docs_task_is_yellow() -> None:
    packet = TaskPacket(title="Docs note", body="Write a markdown note")

    assert classify_task(packet) == RiskLevel.YELLOW


def test_code_task_is_orange() -> None:
    packet = TaskPacket(title="Implement CLI", body="Add code and tests")

    assert classify_task(packet) == RiskLevel.ORANGE


def test_secret_task_is_red() -> None:
    packet = TaskPacket(title="Use token", body="Read .env and SSH secret")

    assert classify_task(packet) == RiskLevel.RED


def test_red_beats_orange_and_yellow() -> None:
    packet = TaskPacket(title="Deploy CLI docs", body="Use production token")

    assert classify_task(packet) == RiskLevel.RED


def test_green_task_has_no_trigger_terms() -> None:
    packet = TaskPacket(title="Sort queue", body="Classify items by current status")

    assert classify_task(packet) == RiskLevel.GREEN

import json

from tools.skeleton_core.cli import main


def test_cli_classify_queue_outputs_items_and_summary(capsys) -> None:
    exit_code = main(["classify-queue", "--input", "tests/fixtures/github_queue_sample.json"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert "items" in payload
    assert "summary" in payload
    assert len(payload["items"]) == 4
    assert payload["items"][0]["classification"] == "ACTIVE_SKELETON"
    assert payload["items"][0]["kind"] == "issue"
    assert "reason" in payload["items"][0]
    assert payload["summary"]["ACTIVE_SKELETON"] == 1
    assert payload["summary"]["JEEVES_RUNTIME_NOISE_FOR_NOW"] == 1
    assert payload["summary"]["EVIDENCE_ONLY"] == 1
    assert payload["summary"]["BLOCKED_WAITING_FOR_OLEKSII"] == 1

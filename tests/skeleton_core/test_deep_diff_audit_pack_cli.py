import json

from tools.skeleton_core import cli


def test_deep_diff_audit_pack_cli_prints_packet_json(tmp_path, capsys) -> None:
    input_path = tmp_path / "packet_input.json"
    input_path.write_text(
        json.dumps(
            {
                "subject": {
                    "repo": "alanua/jeeves",
                    "issue_number": 178,
                    "title": "CLI wiring for deep-diff audit packet builder",
                },
                "sources": [
                    {
                        "source_type": "issue_body",
                        "source_ref": "alanua/jeeves#178",
                        "content": "Already-prepared public-safe issue body excerpt.",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    exit_code = cli.main(["deep-diff-audit-pack", "--input", str(input_path)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert captured.err == ""
    assert payload["schema_version"] == "deep-diff-evidence-packet/v1"
    assert payload["subject"]["repo"] == "alanua/jeeves"
    assert payload["subject"]["issue_number"] == 178
    assert payload["sources"][0]["source_ref"] == "alanua/jeeves#178"
    assert payload["sources"][0]["excerpt"] == "Already-prepared public-safe issue body excerpt."


def test_deep_diff_audit_pack_cli_returns_nonzero_for_validation_errors(tmp_path, capsys) -> None:
    input_path = tmp_path / "packet_input.json"
    input_path.write_text(
        json.dumps(
            {
                "sources": [
                    {
                        "source_type": "issue_body",
                        "source_ref": "alanua/jeeves#178",
                        "content": "Missing subject should fail validation.",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    exit_code = cli.main(["deep-diff-audit-pack", "--input", str(input_path)])

    captured = capsys.readouterr()
    payload = json.loads(captured.err)

    assert exit_code == 2
    assert captured.out == ""
    assert payload["ok"] is False
    assert payload["error"] == "input_validation_failed"
    assert payload["input"].endswith("packet_input.json")
    assert payload["detail"][0]["loc"] == ["subject"]

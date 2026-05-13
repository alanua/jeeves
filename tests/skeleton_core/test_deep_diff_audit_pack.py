import json

from tools.skeleton_core.deep_diff_audit_pack import (
    DEFAULT_SCHEMA_VERSION,
    DeepDiffEvidenceInput,
    DeepDiffSourceInput,
    DeepDiffSubject,
    build_deep_diff_audit_pack,
    build_deep_diff_audit_pack_from_json,
    contains_secret_like_text,
    packet_to_json_dict,
)


def test_deep_diff_audit_pack_builds_required_structure() -> None:
    packet = build_deep_diff_audit_pack(
        DeepDiffEvidenceInput(
            subject=DeepDiffSubject(
                repo="alanua/jeeves",
                issue_number=175,
                title="Add Skeleton branch continuity state guardrail",
            ),
            sources=[
                DeepDiffSourceInput(
                    source_type="issue_body",
                    source_ref="alanua/jeeves#175",
                    content="Proposed continuity guardrail.",
                ),
                DeepDiffSourceInput(
                    source_type="repo_file_excerpt",
                    source_ref="knowledge_base/chatgpt_exoskeleton/CURRENT_STATE.md",
                    content="Existing current state excerpt.",
                ),
            ],
        )
    )

    payload = packet_to_json_dict(packet)

    assert payload["schema_version"] == DEFAULT_SCHEMA_VERSION
    assert payload["subject"]["repo"] == "alanua/jeeves"
    assert payload["subject"]["issue_number"] == 175
    assert len(payload["sources"]) == 2
    assert payload["sources"][0]["source_type"] == "issue_body"
    assert payload["sources"][1]["source_type"] == "repo_file_excerpt"
    assert "questions" in payload
    assert "expected_matrix_schema" in payload
    assert payload["expected_matrix_schema"]["required_fields"] == [
        "proposed_item",
        "existing_source",
        "status",
        "recommendation",
        "confidence",
    ]


def test_deep_diff_audit_pack_truncates_long_excerpt() -> None:
    packet = build_deep_diff_audit_pack(
        DeepDiffEvidenceInput(
            subject=DeepDiffSubject(repo="alanua/jeeves"),
            sources=[
                DeepDiffSourceInput(
                    source_type="manual_excerpt",
                    source_ref="manual:test",
                    content="x" * 250,
                    max_excerpt_chars=100,
                )
            ],
        )
    )

    source = packet.sources[0]

    assert source.truncated is True
    assert source.chars_original == 250
    assert source.excerpt.endswith("<truncated>")
    assert "excerpt_truncated_to_100_chars" in source.limits_applied


def test_deep_diff_audit_pack_redacts_secret_like_content() -> None:
    assert contains_secret_like_text("token=abc123") is True

    packet = build_deep_diff_audit_pack(
        DeepDiffEvidenceInput(
            subject=DeepDiffSubject(repo="alanua/jeeves"),
            sources=[
                DeepDiffSourceInput(
                    source_type="manual_excerpt",
                    source_ref="manual:bad",
                    content="token=abc123\nnormal line",
                )
            ],
        )
    )

    source = packet.sources[0]

    assert source.secret_like_redaction_applied is True
    assert source.excerpt == "<redacted-secret-like-content>"
    assert "abc123" not in source.excerpt
    assert "secret_like_content_redacted" in source.limits_applied


def test_deep_diff_audit_pack_from_json() -> None:
    raw = json.dumps(
        {
            "subject": {
                "repo": "alanua/jeeves",
                "issue_number": 178,
                "title": "Add Skeleton deep-diff audit evidence packet builder",
            },
            "sources": [
                {
                    "source_type": "issue_body",
                    "source_ref": "alanua/jeeves#178",
                    "content": "Deep audit without evidence packet is shallow audit.",
                }
            ],
            "questions": ["Is this duplicate, overlap, gap, conflict, or new?"],
        }
    )

    packet = build_deep_diff_audit_pack_from_json(raw)

    assert packet.subject.issue_number == 178
    assert packet.questions == ["Is this duplicate, overlap, gap, conflict, or new?"]
    assert packet.sources[0].source_ref == "alanua/jeeves#178"


def test_deep_diff_audit_pack_marks_builder_limits() -> None:
    packet = build_deep_diff_audit_pack(
        DeepDiffEvidenceInput(
            subject=DeepDiffSubject(repo="alanua/jeeves"),
            sources=[
                DeepDiffSourceInput(
                    source_type="pr_changed_files",
                    source_ref="alanua/Knowledge-base#178",
                    content="scripts/agent-host-wrapper-reference/README.md",
                    limits_applied=["changed_filenames_only"],
                )
            ],
        )
    )

    assert "changed_filenames_only" in packet.sources[0].limits_applied
    assert any("does not fetch GitHub" in note for note in packet.safety_notes)

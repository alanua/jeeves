from tools.skeleton_core.cli import main


def test_cli_handoff_pack_current_repo(capsys) -> None:
    exit_code = main(["handoff-pack"])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.out.startswith("skeleton_handoff_pack\nstate_validation")
    assert "ok: true" in captured.out
    assert "current_state_excerpt" in captured.out
    assert "available_commands\n- validate-state" in captured.out
    assert "next_recommended_step" in captured.out

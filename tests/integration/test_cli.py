import json
from pathlib import Path

import pytest

from presentation_studio import cli
from presentation_studio.models import CLIResult


@pytest.fixture(autouse=True)
def clean_registries() -> None:
    cli._BACKENDS.clear()
    cli._RENDERERS.clear()
    yield
    cli._BACKENDS.clear()
    cli._RENDERERS.clear()


def _run_json(capsys: pytest.CaptureFixture[str], argv: list[str]) -> tuple[int, dict]:
    exit_code = cli.run([*argv, "--json"])
    captured = capsys.readouterr()
    assert len([line for line in captured.out.splitlines() if line.strip()]) == 1
    assert captured.err == ""
    return exit_code, json.loads(captured.out)


@pytest.mark.parametrize("returned", [None, {"status": "passed"}])
def test_handler_returning_non_result_is_contract_failure(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    returned: object,
) -> None:
    cli.register_backend("broken", lambda paths: returned)
    exit_code, payload = _run_json(
        capsys,
        ["build", "--workspace", str(tmp_path), "--backend", "broken"],
    )
    assert exit_code == 5
    assert payload["errors"][0]["code"] == "HANDLER_CONTRACT_ERROR"


def test_handler_command_mismatch_is_contract_failure(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    cli.register_backend(
        "broken",
        lambda paths: CLIResult(command="render", status="passed", exit_code=0),
    )
    exit_code, payload = _run_json(
        capsys,
        ["build", "--workspace", str(tmp_path), "--backend", "broken"],
    )
    assert exit_code == 5
    assert payload["errors"][0]["code"] == "HANDLER_CONTRACT_ERROR"


def test_backend_exception_is_sanitized_and_not_misclassified_as_invalid_input(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    def broken(paths: object) -> None:
        raise ValueError(r"token=synthetic-secret path=C:\private\deck.yaml")

    cli.register_backend("broken", broken)
    exit_code = cli.run(
        [
            "build",
            "--workspace",
            str(tmp_path),
            "--backend",
            "broken",
            "--json",
        ]
    )
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 5
    assert payload["errors"][0]["code"] == "BACKEND_FAILURE"
    combined = captured.out + captured.err
    diagnostic_ref = payload["errors"][0]["evidence_ref"]
    assert diagnostic_ref.startswith("diagnostic:")
    diagnostic_id = diagnostic_ref.removeprefix("diagnostic:")
    assert (
        f"technical-error diagnostic_id={diagnostic_id} "
        "command=build category=backend exception_type=ValueError"
    ) in captured.err
    assert "synthetic-secret" not in combined
    assert "private" not in combined
    assert "deck.yaml" not in combined
    assert "Traceback" not in combined


def test_internal_exception_emits_sanitized_technical_diagnostic(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def broken(args: object) -> None:
        raise RuntimeError(r"token=synthetic-secret path=C:\private\deck.yaml")

    monkeypatch.setattr(cli, "_run_command", broken)
    exit_code = cli.run(
        ["doctor", "--workspace", str(tmp_path), "--json"]
    )
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 5
    assert payload["errors"][0]["code"] == "INTERNAL_ERROR"
    combined = captured.out + captured.err
    diagnostic_ref = payload["errors"][0]["evidence_ref"]
    assert diagnostic_ref.startswith("diagnostic:")
    diagnostic_id = diagnostic_ref.removeprefix("diagnostic:")
    assert (
        f"technical-error diagnostic_id={diagnostic_id} "
        "command=doctor category=internal exception_type=RuntimeError"
    ) in captured.err
    assert "synthetic-secret" not in combined
    assert "private" not in combined
    assert "deck.yaml" not in combined
    assert "Traceback" not in combined


def test_invalid_syntax_does_not_echo_unknown_positional_input(
    capsys: pytest.CaptureFixture[str],
) -> None:
    synthetic_secret = "synthetic-secret-positional"

    exit_code = cli.run([synthetic_secret, "--json"])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 2
    assert payload["command"] == "unknown"
    assert payload["errors"][0]["code"] == "INVALID_INPUT"
    assert synthetic_secret not in captured.out + captured.err


def test_permission_error_is_structured_json(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def denied(*args: object, **kwargs: object) -> None:
        raise PermissionError("sensitive filesystem detail")

    monkeypatch.setattr(cli, "init_project", denied)
    exit_code, payload = _run_json(
        capsys,
        ["init", "--workspace", str(tmp_path), "--title", "Deck"],
    )
    assert exit_code == 3
    assert payload["errors"][0]["code"] == "PERMISSION_DENIED"
    assert "sensitive" not in json.dumps(payload)

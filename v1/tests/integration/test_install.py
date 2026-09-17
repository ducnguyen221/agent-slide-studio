import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


ENV = {
    **os.environ,
    "PYTHONPATH": str(Path(__file__).parents[2] / "src"),
    "PYTHONUTF8": "1",
}


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "presentation_studio.cli", *args],
        text=True,
        encoding="utf-8",
        capture_output=True,
        env=ENV,
    )


def test_cli_json_reports_missing_profile_without_fake_success(tmp_path: Path) -> None:
    subprocess.run(
        [
            sys.executable,
            "-m",
            "presentation_studio.cli",
            "init",
            "--workspace",
            str(tmp_path),
            "--title",
            "Deck",
        ],
        check=True,
        env=ENV,
    )
    project = tmp_path / "project.yaml"
    text = project.read_text(encoding="utf-8").replace(
        "profile_ref: null", "profile_ref: builtin:missing@1.0.0"
    )
    project.write_text(text, encoding="utf-8")
    result = _run("build", "--workspace", str(tmp_path), "--json")
    payload = json.loads(result.stdout)
    assert result.returncode == 2
    assert payload["status"] == "failed"
    assert payload["errors"][0]["code"] == "PROFILE_NOT_FOUND"


def test_backend_without_dispatch_is_unavailable(tmp_path: Path) -> None:
    result = _run(
        "build", "--workspace", str(tmp_path), "--backend", "not-installed", "--json"
    )
    assert result.returncode == 3
    assert json.loads(result.stdout)["status"] == "failed"


def test_init_derives_valid_id_from_unicode_workspace(tmp_path: Path) -> None:
    workspace = tmp_path / "Dự án Một"
    result = _run("init", "--workspace", str(workspace), "--title", "Deck", "--json")
    assert result.returncode == 0
    assert json.loads(result.stdout)["data"]["project"]["project_id"] == "du-an-mot"


def test_render_without_registered_backend_is_unavailable(tmp_path: Path) -> None:
    result = _run(
        "render", "--workspace", str(tmp_path), "--build", "b01", "--json"
    )
    assert result.returncode == 3
    assert json.loads(result.stdout)["errors"][0]["code"] == "CAPABILITY_UNAVAILABLE"


def test_station_init_without_workspace_returns_json(tmp_path: Path) -> None:
    result = _run(
        "init",
        "--home",
        str(tmp_path),
        "--project",
        "foo",
        "--title",
        "Foo",
        "--json",
    )
    assert result.returncode == 0
    assert (tmp_path / "projects" / "foo" / "project.yaml").is_file()


@pytest.mark.parametrize(
    "args",
    [
        ("init", "--home", "HOME", "--title", "Foo", "--json"),
        (
            "init",
            "--workspace",
            "WORKSPACE",
            "--project",
            "foo",
            "--title",
            "Foo",
            "--json",
        ),
        ("init", "--title", "Foo", "--json"),
    ],
)
def test_invalid_init_forms_return_one_json_object(
    tmp_path: Path, args: tuple[str, ...]
) -> None:
    rendered = tuple(
        str(tmp_path) if value in {"HOME", "WORKSPACE"} else value for value in args
    )
    result = _run(*rendered)
    assert result.returncode == 2
    assert json.loads(result.stdout)["errors"][0]["code"] == "INVALID_INPUT"
    assert len([line for line in result.stdout.splitlines() if line.strip()]) == 1
    assert result.stderr == ""


def test_argparse_error_in_json_mode_is_one_json_object() -> None:
    result = _run("build", "--json")
    assert result.returncode == 2
    assert json.loads(result.stdout)["errors"][0]["code"] == "INVALID_INPUT"
    assert result.stderr == ""


def test_cli_configures_utf8_stdout_on_legacy_windows_code_page(tmp_path: Path) -> None:
    env = {
        key: value
        for key, value in os.environ.items()
        if key not in {"PYTHONUTF8", "PYTHONIOENCODING"}
    }
    env["PYTHONPATH"] = str(Path(__file__).parents[2] / "src")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "presentation_studio.cli",
            "init",
            "--workspace",
            str(tmp_path / "Dự án"),
            "--title",
            "Bản kiểm sạch",
            "--json",
        ],
        text=True,
        encoding="utf-8",
        capture_output=True,
        env=env,
    )
    assert result.returncode == 0
    assert json.loads(result.stdout)["data"]["project"]["title"] == "Bản kiểm sạch"


def test_invalid_project_yaml_returns_one_json_object(tmp_path: Path) -> None:
    (tmp_path / "project.yaml").write_text("title: [", encoding="utf-8")
    result = _run("build", "--workspace", str(tmp_path), "--json")
    assert result.returncode == 2
    assert json.loads(result.stdout)["errors"][0]["code"] == "INVALID_INPUT"
    assert len([line for line in result.stdout.splitlines() if line.strip()]) == 1
    assert result.stderr == ""


def test_conflicting_reinit_returns_conflict_without_mutation(tmp_path: Path) -> None:
    first = _run("init", "--workspace", str(tmp_path), "--title", "First", "--json")
    assert first.returncode == 0
    before = (tmp_path / "project.yaml").read_bytes()
    second = _run("init", "--workspace", str(tmp_path), "--title", "Second", "--json")
    assert second.returncode == 6
    assert json.loads(second.stdout)["errors"][0]["code"] == "PROJECT_CONFLICT"
    assert (tmp_path / "project.yaml").read_bytes() == before

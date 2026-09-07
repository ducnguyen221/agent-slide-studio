import json
import os
import subprocess
import sys
from pathlib import Path

ENV = {**os.environ, "PYTHONPATH": str(Path(__file__).parents[2] / "src"), "PYTHONUTF8": "1"}

def test_cli_json_reports_missing_profile_without_fake_success(tmp_path: Path) -> None:
    subprocess.run([sys.executable, "-m", "presentation_studio.cli", "init", "--workspace", str(tmp_path), "--title", "Deck"], check=True, env=ENV)
    project = tmp_path / "project.yaml"
    text = project.read_text(encoding="utf-8").replace("profile_ref: null", "profile_ref: builtin:missing@1.0.0")
    project.write_text(text, encoding="utf-8")
    result = subprocess.run([sys.executable, "-m", "presentation_studio.cli", "build", "--workspace", str(tmp_path), "--json"], text=True, capture_output=True, env=ENV)
    payload = json.loads(result.stdout)
    assert result.returncode == 2
    assert payload["status"] == "failed"
    assert payload["errors"][0]["code"] == "PROFILE_NOT_FOUND"


def test_backend_without_dispatch_is_unavailable(tmp_path: Path) -> None:
    result = subprocess.run([sys.executable, "-m", "presentation_studio.cli", "build", "--workspace", str(tmp_path), "--backend", "not-installed", "--json"], text=True, capture_output=True, env=ENV)
    assert result.returncode == 3
    assert json.loads(result.stdout)["status"] == "failed"

def test_init_derives_valid_id_from_unicode_workspace(tmp_path: Path) -> None:
    workspace = tmp_path / "Dự án Một"
    result = subprocess.run([sys.executable, "-m", "presentation_studio.cli", "init", "--workspace", str(workspace), "--title", "Deck", "--json"], text=True, capture_output=True, env=ENV)
    assert result.returncode == 0
    assert json.loads(result.stdout)["data"]["project"]["project_id"] == "du-an-mot"

def test_render_without_registered_backend_is_unavailable(tmp_path: Path) -> None:
    result = subprocess.run([sys.executable, "-m", "presentation_studio.cli", "render", "--workspace", str(tmp_path), "--build", "b01", "--json"], text=True, capture_output=True, env=ENV)
    assert result.returncode == 3
    assert json.loads(result.stdout)["errors"][0]["code"] == "CAPABILITY_UNAVAILABLE"

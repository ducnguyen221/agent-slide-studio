import json
import subprocess
import sys
from pathlib import Path


def test_legacy_migration_dry_run_does_not_write_or_delete(tmp_path: Path) -> None:
    source = tmp_path / "legacy"
    target = tmp_path / "target"
    source.mkdir()
    original = source / "sample.yaml"
    original.write_text("title: Legacy\nsubject: AI\nslides:\n  - slide_id: slide_01\n    title: Intro\n", encoding="utf-8")
    before = original.read_bytes()
    script = Path(__file__).parents[2] / "scripts" / "migrate-legacy.py"
    result = subprocess.run([sys.executable, str(script), "--source", str(source), "--workspace", str(target), "--dry-run"], text=True, capture_output=True, check=True)
    payload = json.loads(result.stdout)
    assert payload["status"] == "passed" and payload["data"]["planned_files"] == 1
    assert not target.exists()
    assert original.read_bytes() == before

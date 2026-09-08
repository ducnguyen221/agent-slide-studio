import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from presentation_studio.migration import MigrationLimits, migrate


ENV = {
    **os.environ,
    "PYTHONPATH": str(Path(__file__).parents[2] / "src"),
    "PYTHONUTF8": "1",
}
SCRIPT = Path(__file__).parents[2] / "scripts" / "migrate-legacy.py"


def _legacy_deck(path: Path) -> None:
    path.write_text(
        """title: Legacy
subject: AI
target_audience: Team
profile_name: tech-dark
metadata:
  course_code: AI-101
slides:
  - slide_id: slide-01
    title: Intro
    subtitle: Opening
    archetype: cards-grid
    speaker_notes: YAML note
    bloom_verb: Understand
    objective_id: lo1
    cards:
      - title: Card A
        points: [One, Two]
""",
        encoding="utf-8",
    )


def _run_script(source: Path, target: Path, mode: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--source",
            str(source),
            "--workspace",
            str(target),
            mode,
        ],
        text=True,
        encoding="utf-8",
        capture_output=True,
        env=ENV,
    )


def test_legacy_migration_dry_run_does_not_write_or_delete(tmp_path: Path) -> None:
    source = tmp_path / "legacy"
    target = tmp_path / "target"
    source.mkdir()
    original = source / "sample.yaml"
    _legacy_deck(original)
    before = original.read_bytes()

    result = _run_script(source, target, "--dry-run")
    payload = json.loads(result.stdout)

    assert result.returncode == 0
    assert payload["status"] == "passed"
    assert payload["data"]["planned_files"] == 1
    assert payload["data"]["files"][0]["sha256"] == hashlib.sha256(before).hexdigest()
    assert payload["data"]["files"][0]["bytes"] == len(before)
    assert not target.exists()
    assert original.read_bytes() == before


def test_legacy_apply_maps_yaml_markdown_notes_learning_and_source_order(
    tmp_path: Path,
) -> None:
    source = tmp_path / "legacy"
    target = tmp_path / "target"
    source.mkdir()
    original = source / "deck.yaml"
    markdown = source / "slide-01.md"
    _legacy_deck(original)
    markdown.write_text("# Presenter detail\n\nMarkdown note.\n", encoding="utf-8")

    result = _run_script(source, target, "--apply")
    payload = json.loads(result.stdout)
    deck = yaml.safe_load((target / "storyboard" / "deck.yaml").read_text(encoding="utf-8"))

    assert result.returncode == 0
    assert payload["status"] == "passed"
    assert deck["audience"] == "Team"
    assert deck["purpose"] == "AI"
    assert deck["slides"][0]["slide_id"] == "slide-01"
    assert deck["slides"][0]["notes"] == "YAML note\n\n# Presenter detail\n\nMarkdown note."
    assert deck["slides"][0]["learning"] == {
        "objective_ids": ["lo1"],
        "bloom_verb": "Understand",
    }
    assert [source_ref["uri"] for source_ref in deck["sources"]] == [
        "sources/originals/deck.yaml",
        "sources/originals/slide-01.md",
    ]
    assert (target / "sources" / "originals" / "deck.yaml").read_bytes() == original.read_bytes()
    report = json.loads((target / "migration-report.json").read_text(encoding="utf-8"))
    assert "profile_name" in report["unmapped_fields"]
    assert "metadata" in report["unmapped_fields"]


def test_legacy_apply_refuses_existing_target_without_mutation(tmp_path: Path) -> None:
    source = tmp_path / "legacy"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()
    marker = target / "keep.txt"
    marker.write_text("keep", encoding="utf-8")
    _legacy_deck(source / "deck.yaml")

    result = _run_script(source, target, "--apply")

    assert result.returncode == 6
    assert json.loads(result.stdout)["errors"][0]["code"] == "MIGRATION_CONFLICT"
    assert marker.read_text(encoding="utf-8") == "keep"
    assert list(target.iterdir()) == [marker]


def test_legacy_symlink_candidate_is_rejected(tmp_path: Path) -> None:
    source = tmp_path / "legacy"
    source.mkdir()
    outside = tmp_path / "outside.yaml"
    _legacy_deck(outside)
    link = source / "link.yaml"
    try:
        link.symlink_to(outside)
    except OSError:
        pytest.skip("symlink privilege unavailable")

    result = _run_script(source, tmp_path / "target", "--dry-run")

    assert result.returncode == 2
    assert json.loads(result.stdout)["errors"][0]["code"] == "MIGRATION_INPUT_INVALID"


@pytest.mark.skipif(os.name != "nt", reason="Windows junction behavior")
def test_legacy_junction_candidate_is_rejected(tmp_path: Path) -> None:
    source = tmp_path / "legacy"
    outside = tmp_path / "outside"
    source.mkdir()
    outside.mkdir()
    _legacy_deck(outside / "deck.yaml")
    junction = source / "linked"
    created = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(junction), str(outside)],
        text=True,
        capture_output=True,
    )
    if created.returncode != 0:
        pytest.skip("junction creation unavailable")
    try:
        result = _run_script(source, tmp_path / "target", "--dry-run")
        assert result.returncode == 2
        assert json.loads(result.stdout)["errors"][0]["code"] == "MIGRATION_INPUT_INVALID"
    finally:
        os.rmdir(junction)


def test_migration_bounds_candidate_count_and_total_bytes(tmp_path: Path) -> None:
    source = tmp_path / "legacy"
    source.mkdir()
    _legacy_deck(source / "one.yaml")
    _legacy_deck(source / "two.yaml")
    with pytest.raises(ValueError):
        migrate(source, tmp_path / "target", apply=False, limits=MigrationLimits(max_files=1))
    with pytest.raises(ValueError):
        migrate(
            source,
            tmp_path / "target",
            apply=False,
            limits=MigrationLimits(max_total_bytes=10),
        )


def test_invalid_candidate_fails_whole_migration_without_target(tmp_path: Path) -> None:
    source = tmp_path / "legacy"
    target = tmp_path / "target"
    source.mkdir()
    _legacy_deck(source / "deck.yaml")
    (source / "broken.yaml").write_text("slides: [", encoding="utf-8")

    result = _run_script(source, target, "--apply")

    assert result.returncode == 2
    assert json.loads(result.stdout)["status"] == "failed"
    assert not target.exists()
    assert not list(tmp_path.glob(".target.migration-*"))


def test_staging_write_failure_does_not_promote_partial_target(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "legacy"
    target = tmp_path / "target"
    source.mkdir()
    _legacy_deck(source / "deck.yaml")

    from presentation_studio import migration

    original_write = migration._write_bytes
    calls = 0

    def fail_second_write(path: Path, payload: bytes) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("synthetic write failure")
        original_write(path, payload)

    monkeypatch.setattr(migration, "_write_bytes", fail_second_write)
    result = migration.migrate_result(source, target, apply=True)

    assert result.exit_code == 5
    assert result.errors[0].code == "FILESYSTEM_FAILURE"
    assert not target.exists()
    assert not list(tmp_path.glob(".target.migration-*"))


def test_package_cli_exposes_migration(tmp_path: Path) -> None:
    source = tmp_path / "legacy"
    source.mkdir()
    _legacy_deck(source / "deck.yaml")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "presentation_studio.cli",
            "migrate",
            "--source",
            str(source),
            "--workspace",
            str(tmp_path / "target"),
            "--dry-run",
            "--json",
        ],
        text=True,
        encoding="utf-8",
        capture_output=True,
        env=ENV,
    )
    assert result.returncode == 0
    assert json.loads(result.stdout)["command"] == "migrate"

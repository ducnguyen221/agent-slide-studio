import hashlib
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier

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
    original.write_text(
        original.read_text(encoding="utf-8").replace(
            "    speaker_notes: YAML note\n",
            "    speaker_notes: YAML note\n    notes_file: slide-01.md\n",
        ),
        encoding="utf-8",
    )
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
    _legacy_deck(source / "ignored.yaml")
    (source / "deck.yaml").write_text("slides: [", encoding="utf-8")

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


def test_migration_uses_scanned_bytes_when_source_changes_before_parse(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from presentation_studio import migration

    source = tmp_path / "legacy"
    target = tmp_path / "target"
    source.mkdir()
    original = source / "deck.yaml"
    _legacy_deck(original)
    scanned = original.read_bytes()
    original_scan = migration._scan_candidates

    def scan_then_swap(
        source_path: Path, limits: MigrationLimits
    ) -> list[migration.Candidate]:
        candidates = original_scan(source_path, limits)
        original.write_text("slides: [changed after scan]", encoding="utf-8")
        return candidates

    monkeypatch.setattr(migration, "_scan_candidates", scan_then_swap)

    result = migration.migrate_result(source, target, apply=True)

    assert result.exit_code == 0
    deck = yaml.safe_load((target / "storyboard" / "deck.yaml").read_text("utf-8"))
    assert deck["title"] == "Legacy"
    assert (target / "sources" / "originals" / "deck.yaml").read_bytes() == scanned


def test_migration_target_creation_race_preserves_foreign_target(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from presentation_studio import migration

    source = tmp_path / "legacy"
    target = tmp_path / "target"
    source.mkdir()
    _legacy_deck(source / "deck.yaml")
    original_promote = migration._promote_staging

    def create_target_then_promote(stage: Path, destination: Path) -> None:
        destination.mkdir()
        (destination / "foreign.txt").write_text("foreign", encoding="utf-8")
        original_promote(stage, destination)

    monkeypatch.setattr(migration, "_promote_staging", create_target_then_promote)

    result = migration.migrate_result(source, target, apply=True)

    assert result.exit_code == 6
    assert result.errors[0].code == "MIGRATION_CONFLICT"
    assert (target / "foreign.txt").read_text("utf-8") == "foreign"
    assert not (target / "project.yaml").exists()
    assert not list(tmp_path.glob(".target.migration-*"))


def test_migration_target_creation_race_preserves_empty_foreign_target(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from presentation_studio import migration

    source = tmp_path / "legacy"
    target = tmp_path / "target"
    source.mkdir()
    _legacy_deck(source / "deck.yaml")
    original_promote = migration._promote_staging

    def create_empty_target_then_promote(stage: Path, destination: Path) -> None:
        destination.mkdir()
        original_promote(stage, destination)

    monkeypatch.setattr(
        migration, "_promote_staging", create_empty_target_then_promote
    )

    result = migration.migrate_result(source, target, apply=True)

    assert result.exit_code == 6
    assert result.errors[0].code == "MIGRATION_CONFLICT"
    assert target.is_dir() and not list(target.iterdir())
    assert not list(tmp_path.glob(".target.migration-*"))


def test_two_concurrent_migrations_never_replace_the_winner(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from presentation_studio import migration

    first_source = tmp_path / "legacy-a"
    second_source = tmp_path / "legacy-b"
    target = tmp_path / "target"
    first_source.mkdir()
    second_source.mkdir()
    _legacy_deck(first_source / "deck.yaml")
    _legacy_deck(second_source / "deck.yaml")
    second_deck = second_source / "deck.yaml"
    second_deck.write_text(
        second_deck.read_text(encoding="utf-8").replace(
            "title: Legacy", "title: Second"
        ),
        encoding="utf-8",
    )
    barrier = Barrier(2)
    original_promote = migration._promote_staging

    def simultaneous_promote(stage: Path, destination: Path) -> None:
        barrier.wait(timeout=5)
        original_promote(stage, destination)

    monkeypatch.setattr(migration, "_promote_staging", simultaneous_promote)

    def run(source: Path) -> str:
        try:
            migration.migrate(source, target, apply=True)
            return "committed"
        except migration.MigrationConflict:
            return "conflict"

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(run, (first_source, second_source)))

    assert sorted(outcomes) == ["committed", "conflict"]
    deck = yaml.safe_load((target / "storyboard" / "deck.yaml").read_text("utf-8"))
    assert deck["title"] in {"Legacy", "Second"}
    assert not (target / ".migration-claim").exists()
    assert not list(tmp_path.glob(".target.migration-*"))


def test_atomic_promotion_failure_leaves_target_absent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from presentation_studio import migration

    source = tmp_path / "legacy"
    target = tmp_path / "target"
    source.mkdir()
    _legacy_deck(source / "deck.yaml")
    def fail_promotion(source_path: Path, destination_path: Path) -> None:
        raise OSError("synthetic promotion failure")

    monkeypatch.setattr(migration, "_rename_noreplace", fail_promotion)

    result = migration.migrate_result(source, target, apply=True)

    assert result.exit_code == 5
    assert result.errors[0].code == "FILESYSTEM_FAILURE"
    assert not target.exists()
    assert not list(tmp_path.glob(".target.migration-*"))


def test_migration_internal_error_emits_correlated_sanitized_diagnostic(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    from presentation_studio import migration

    def fail(*args: object, **kwargs: object) -> dict[str, object]:
        raise RuntimeError(r"token=synthetic-secret path=C:\private\deck.yaml")

    monkeypatch.setattr(migration, "migrate", fail)

    result = migration.migrate_result(tmp_path / "source", tmp_path / "target", apply=True)
    captured = capsys.readouterr()

    assert result.exit_code == 5
    assert result.errors[0].code == "MIGRATION_INTERNAL_ERROR"
    diagnostic_ref = result.errors[0].evidence_ref
    assert diagnostic_ref is not None and diagnostic_ref.startswith("diagnostic:")
    diagnostic_id = diagnostic_ref.removeprefix("diagnostic:")
    assert f"diagnostic_id={diagnostic_id}" in captured.err
    assert "exception_type=RuntimeError" in captured.err
    assert "synthetic-secret" not in captured.err
    assert "private" not in captured.err


@pytest.mark.parametrize(
    ("mutate", "field"),
    [
        (lambda data: data.update(title={"bad": "shape"}), "title"),
        (
            lambda data: data["slides"][0].update(title=["bad"]),
            "slides[0].title",
        ),
        (
            lambda data: data["slides"][0].update(
                timeline_nodes=[{"time_label": {"bad": "shape"}, "title": "Now"}]
            ),
            "slides[0].timeline_nodes[0].time_label",
        ),
        (
            lambda data: data["slides"][0].update(
                visual_asset={"asset_id": "image-1", "alt_text": ["bad"]}
            ),
            "slides[0].visual_asset.alt_text",
        ),
    ],
)
def test_migration_rejects_non_scalar_fields_with_location(
    tmp_path: Path, mutate: object, field: str
) -> None:
    source = tmp_path / "legacy"
    source.mkdir()
    legacy = source / "deck.yaml"
    _legacy_deck(legacy)
    data = yaml.safe_load(legacy.read_text("utf-8"))
    mutate(data)  # type: ignore[operator]
    legacy.write_text(yaml.safe_dump(data), encoding="utf-8")

    result = _run_script(source, tmp_path / "target", "--dry-run")
    payload = json.loads(result.stdout)

    assert result.returncode == 2
    assert payload["errors"][0]["code"] == "MIGRATION_INPUT_INVALID"
    assert payload["errors"][0]["field"] == field


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


def test_migration_skips_unreferenced_private_hidden_and_config_files(
    tmp_path: Path,
) -> None:
    source = tmp_path / "legacy"
    source.mkdir()
    _legacy_deck(source / "deck.yaml")
    (source / "private.md").write_text("private note", encoding="utf-8")
    (source / "private.yaml").write_text(
        "api_key: ignored-private-material\n", encoding="utf-8"
    )
    (source / ".cache").mkdir()
    (source / ".cache" / "cached.yaml").write_text("token: cached-secret", encoding="utf-8")
    (source / "config").mkdir()
    (source / "config" / "settings.yaml").write_text("password: hidden", encoding="utf-8")

    result = migrate(source, tmp_path / "target", apply=True)

    assert result["planned_files"] == 1
    originals = tmp_path / "target" / "sources" / "originals"
    assert sorted(path.name for path in originals.rglob("*")) == ["deck.yaml"]


def test_unselected_invalid_yaml_is_not_read(tmp_path: Path) -> None:
    source = tmp_path / "legacy"
    source.mkdir()
    _legacy_deck(source / "deck.yaml")
    (source / "private.yaml").write_text("slides: [", encoding="utf-8")

    result = migrate(source, tmp_path / "target", apply=False)

    assert result["planned_files"] == 1
    assert result["files"][0]["relative_path"] == "deck.yaml"


def test_migration_rejects_hidden_or_config_reference(tmp_path: Path) -> None:
    source = tmp_path / "legacy"
    source.mkdir()
    deck = source / "deck.yaml"
    _legacy_deck(deck)
    deck.write_text(
        deck.read_text(encoding="utf-8") + "source_files: [.cache/private.md]\n",
        encoding="utf-8",
    )
    (source / ".cache").mkdir()
    (source / ".cache" / "private.md").write_text("private", encoding="utf-8")

    with pytest.raises(ValueError, match="reference is invalid"):
        migrate(source, tmp_path / "target", apply=False)


@pytest.mark.parametrize(
    "credential",
    [
        "auth:\n  authorization: Bearer synthetic-token-123456\n",
        "provider_token: sk-syntheticprovider000000000\n",
        "database:\n  connection_string: postgresql://user:pass@host/db\n",
        "aws_secret_access_key: syntheticAwsSecretValue123\n",
    ],
)
def test_recursive_credential_scanner_quarantines_selected_source(
    tmp_path: Path, credential: str
) -> None:
    source = tmp_path / "legacy"
    source.mkdir()
    deck = source / "deck.yaml"
    _legacy_deck(deck)
    deck.write_text(deck.read_text(encoding="utf-8") + credential, encoding="utf-8")
    target = tmp_path / "target"

    with pytest.raises(ValueError, match="credential"):
        migrate(source, target, apply=True)
    assert not target.exists()


def test_discovery_counts_all_candidates_before_reading(tmp_path: Path) -> None:
    source = tmp_path / "legacy"
    source.mkdir()
    _legacy_deck(source / "deck.yaml")
    (source / "private-one.md").write_text("one", encoding="utf-8")
    (source / "private-two.md").write_text("two", encoding="utf-8")

    with pytest.raises(ValueError, match="candidate count limit"):
        migrate(
            source,
            tmp_path / "target",
            apply=False,
            limits=MigrationLimits(max_files=2),
        )


def test_explicit_yaml_reference_shares_aggregate_node_budget(tmp_path: Path) -> None:
    source = tmp_path / "legacy"
    source.mkdir()
    deck = source / "deck.yaml"
    _legacy_deck(deck)
    deck.write_text(
        deck.read_text(encoding="utf-8") + "source_files: [facts.yaml]\n",
        encoding="utf-8",
    )
    (source / "facts.yaml").write_text(
        "facts:\n" + "".join(f"  - fact-{index}\n" for index in range(100)),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="aggregate YAML node budget"):
        migrate(
            source,
            tmp_path / "target",
            apply=False,
            limits=MigrationLimits(max_yaml_nodes=80),
        )


def test_ambiguous_selection_does_not_read_candidate_content(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from presentation_studio import migration

    source = tmp_path / "legacy"
    source.mkdir()
    _legacy_deck(source / "one.yaml")
    _legacy_deck(source / "two.yaml")
    (source / "zz-unrelated.yaml").write_text("value: later\n", encoding="utf-8")
    original_read = migration._read_candidate
    inspected: list[str] = []

    def record_read(path: Path, root: Path, limits: MigrationLimits) -> bytes:
        inspected.append(path.name)
        return original_read(path, root, limits)

    monkeypatch.setattr(migration, "_read_candidate", record_read)
    with pytest.raises(ValueError, match="selection is ambiguous"):
        migrate(source, tmp_path / "target", apply=False)

    assert inspected == []


def test_migration_fails_closed_on_credential_material_without_echo(
    tmp_path: Path,
) -> None:
    source = tmp_path / "legacy"
    source.mkdir()
    deck = source / "deck.yaml"
    _legacy_deck(deck)
    secret = "synthetic-secret-value-12345"
    deck.write_text(
        deck.read_text(encoding="utf-8") + f"api_key: {secret}\n",
        encoding="utf-8",
    )

    result = _run_script(source, tmp_path / "target", "--dry-run")

    assert result.returncode == 2
    assert json.loads(result.stdout)["errors"][0]["code"] == "MIGRATION_INPUT_INVALID"
    assert secret not in result.stdout + result.stderr


def test_migration_has_aggregate_yaml_node_budget(tmp_path: Path) -> None:
    source = tmp_path / "legacy"
    source.mkdir()
    _legacy_deck(source / "deck.yaml")

    with pytest.raises(ValueError, match="aggregate YAML node budget"):
        migrate(
            source,
            tmp_path / "target",
            apply=False,
            limits=MigrationLimits(max_yaml_nodes=5),
        )


def test_staging_cleanup_refuses_replaced_directory_identity(tmp_path: Path) -> None:
    from presentation_studio import migration

    parent = tmp_path / "parent"
    parent.mkdir()
    stage_path = parent / ".target.migration-owned"
    stage_path.mkdir()
    staging = migration._capture_staging(stage_path)
    stage_path.rmdir()
    stage_path.mkdir()
    marker = stage_path / "foreign.txt"
    marker.write_text("foreign", encoding="utf-8")

    with pytest.raises(migration.MigrationConflict):
        migration._remove_staging(staging, parent, "target")

    assert marker.read_text(encoding="utf-8") == "foreign"


def test_staging_capture_closes_both_bindings_when_identity_read_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from presentation_studio import migration

    class FakeBinding:
        def __init__(self, descriptor: int) -> None:
            self.descriptor = descriptor
            self.closed = False

        def close(self) -> None:
            self.closed = True

    parent_binding = FakeBinding(10)
    directory_binding = FakeBinding(20)
    bindings = iter((parent_binding, directory_binding))
    monkeypatch.setattr(
        migration.BoundDirectory,
        "open",
        lambda path, **kwargs: next(bindings),
    )

    def fail_parent_identity(descriptor: int) -> os.stat_result:
        if descriptor == parent_binding.descriptor:
            raise OSError("synthetic parent identity failure")
        return os.stat_result((0o040000, 1, 1, 0, 0, 0, 0, 0, 0, 0))

    monkeypatch.setattr(migration.os, "fstat", fail_parent_identity)

    with pytest.raises(OSError, match="synthetic parent identity failure"):
        migration._capture_staging(tmp_path / "stage")

    assert directory_binding.closed
    assert parent_binding.closed

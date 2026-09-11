from importlib.resources.abc import Traversable
import os
from pathlib import Path
import subprocess

import pytest

from presentation_studio.workspace import (
    InputLimitError,
    PathOutsideWorkspace,
    ProjectConflict,
    init_project,
    load_deck,
    load_yaml_bounded,
    resolve_paths,
    resolve_profile,
    safe_path,
)
from presentation_studio.fs import BoundDirectory


def test_direct_workspace_does_not_create_station(tmp_path: Path) -> None:
    station = tmp_path / "station"
    project = tmp_path / "Dự án có dấu"
    paths = resolve_paths(home=station, workspace=project)
    init_project(paths, project_id="bao-cao-quy", title="Báo cáo quý")
    assert project.joinpath("project.yaml").is_file()
    assert not station.exists()
    assert isinstance(paths.package_resources, Traversable)


def test_station_project_is_created_only_when_explicitly_selected(tmp_path: Path) -> None:
    paths = resolve_paths(
        home=tmp_path / "station", workspace=None, project_id="bao-cao-quy"
    )
    init_project(paths, project_id="bao-cao-quy", title="Báo cáo quý")
    assert paths.project_root == tmp_path / "station" / "projects" / "bao-cao-quy"
    assert paths.home is not None and paths.home.is_dir()


def test_safe_path_blocks_escape_and_absolute_input(tmp_path: Path) -> None:
    with pytest.raises(PathOutsideWorkspace):
        safe_path(tmp_path / "project", "../outside.txt")
    with pytest.raises(PathOutsideWorkspace):
        safe_path(tmp_path / "project", tmp_path / "outside.txt")


def test_init_is_idempotent_and_conflict_does_not_mutate(tmp_path: Path) -> None:
    paths = resolve_paths(workspace=tmp_path / "project")
    first = init_project(paths, project_id="same", title="Same")
    before = {
        path.relative_to(paths.project_root): path.read_bytes()
        for path in paths.project_root.rglob("*")
        if path.is_file()
    }
    assert init_project(paths, project_id="same", title="Same") == first
    with pytest.raises(ProjectConflict):
        init_project(paths, project_id="same", title="Different")
    after = {
        path.relative_to(paths.project_root): path.read_bytes()
        for path in paths.project_root.rglob("*")
        if path.is_file()
    }
    assert after == before


@pytest.mark.parametrize(
    ("contents", "limits"),
    [
        (b"x" * 101, {"max_bytes": 100}),
        (b"a: &x [1]\nb: *x\n", {}),
        (b"a: {b: {c: {d: 1}}}\n", {"max_depth": 3}),
        (b"[1, 2, 3, 4]\n", {"max_nodes": 3}),
    ],
)
def test_yaml_bounds_size_aliases_depth_and_nodes(
    tmp_path: Path, contents: bytes, limits: dict[str, int]
) -> None:
    path = tmp_path / "input.yaml"
    path.write_bytes(contents)
    with pytest.raises(InputLimitError):
        load_yaml_bounded(path, **limits)


def test_managed_directory_symlink_escape_is_rejected_before_project_write(
    tmp_path: Path,
) -> None:
    project = tmp_path / "project"
    outside = tmp_path / "outside"
    project.mkdir()
    outside.mkdir()
    try:
        (project / "builds").symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("symlink privilege unavailable")
    with pytest.raises(PathOutsideWorkspace):
        init_project(resolve_paths(workspace=project), project_id="safe", title="Safe")
    assert not (project / "project.yaml").exists()


@pytest.mark.skipif(os.name != "nt", reason="Windows junction behavior")
def test_managed_directory_junction_escape_is_rejected_before_project_write(
    tmp_path: Path,
) -> None:
    project = tmp_path / "project"
    outside = tmp_path / "outside"
    project.mkdir()
    outside.mkdir()
    junction = project / "exports"
    result = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(junction), str(outside)],
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        pytest.skip("junction creation unavailable")
    try:
        with pytest.raises(PathOutsideWorkspace):
            init_project(
                resolve_paths(workspace=project), project_id="safe", title="Safe"
            )
        assert not (project / "project.yaml").exists()
    finally:
        os.rmdir(junction)


def test_load_deck_resolves_stored_path_inside_workspace(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    outside = tmp_path / "outside.yaml"
    outside.write_text("title: outside", encoding="utf-8")
    with pytest.raises(PathOutsideWorkspace):
        load_deck(project, "../outside.yaml")


@pytest.mark.parametrize(
    "ref",
    [
        "builtin:../escape@1.0.0",
        "builtin:valid@../1.0.0",
        "builtin:valid@latest",
        "project:C:/escape@1.0.0",
    ],
)
def test_profile_ref_rejects_traversal_and_invalid_version(
    tmp_path: Path, ref: str
) -> None:
    with pytest.raises(ValueError):
        resolve_profile(ref, resolve_paths(workspace=tmp_path))


def test_project_profile_resolves_to_verified_lock(tmp_path: Path) -> None:
    profile = tmp_path / "profiles" / "editorial-light" / "1.0.0" / "profile.yaml"
    profile.parent.mkdir(parents=True)
    profile.write_text(
        """schema_version: '1.0'
id: editorial-light
version: 1.0.0
display_name: Sáng biên tập
description: Trung tính
""",
        encoding="utf-8",
    )
    lock = resolve_profile(
        "project:editorial-light@1.0.0", resolve_paths(workspace=tmp_path)
    )
    assert lock.resolved_ref == "project:editorial-light@1.0.0"
    assert lock.source_scope == "project"
    assert len(lock.sha256) == 64


def test_yaml_and_profile_reads_do_not_use_unbounded_path_helpers(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    yaml_path = tmp_path / "input.yaml"
    yaml_path.write_text("value: safe\n", encoding="utf-8")

    def reject_unbounded_read(path: Path) -> bytes:
        raise AssertionError(f"unbounded read attempted: {path.name}")

    monkeypatch.setattr(Path, "read_bytes", reject_unbounded_read)
    assert load_yaml_bounded(yaml_path) == {"value": "safe"}

    profile = tmp_path / "profiles" / "editorial-light" / "1.0.0" / "profile.yaml"
    profile.parent.mkdir(parents=True)
    profile.write_text(
        "schema_version: '1.0'\nid: editorial-light\nversion: 1.0.0\n"
        "display_name: Safe\ndescription: Safe\n",
        encoding="utf-8",
    )
    lock = resolve_profile(
        "project:editorial-light@1.0.0", resolve_paths(workspace=tmp_path)
    )
    assert len(lock.sha256) == 64


def test_bound_directory_keeps_mutation_on_captured_parent(tmp_path: Path) -> None:
    parent = tmp_path / "parent"
    parent.mkdir()
    with BoundDirectory.open(parent) as binding:
        if os.name == "nt":
            moved = tmp_path / "moved"
            parent.rename(moved)
            parent.mkdir()
            with pytest.raises(OSError):
                binding.open_file(
                    "owned.tmp", os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600
                )
            assert not (parent / "owned.tmp").exists()
            assert not (moved / "owned.tmp").exists()
            return
        moved = tmp_path / "moved"
        parent.rename(moved)
        parent.mkdir()
        descriptor = binding.open_file(
            "owned.tmp", os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600
        )
        os.close(descriptor)
        binding.link("owned.tmp", "project.yaml")
        binding.unlink("owned.tmp")
        assert (moved / "project.yaml").is_file()
        assert not (parent / "project.yaml").exists()

from importlib.resources.abc import Traversable
from pathlib import Path

import pytest

from presentation_studio.workspace import PathOutsideWorkspace, init_project, resolve_paths, safe_path


def test_direct_workspace_does_not_create_station(tmp_path: Path) -> None:
    station = tmp_path / "station"
    project = tmp_path / "Dự án có dấu"
    paths = resolve_paths(home=station, workspace=project)
    init_project(paths, project_id="bao-cao-quy", title="Báo cáo quý")
    assert project.joinpath("project.yaml").is_file()
    assert not station.exists()
    assert isinstance(paths.package_resources, Traversable)


def test_station_project_is_created_only_when_explicitly_selected(tmp_path: Path) -> None:
    paths = resolve_paths(home=tmp_path / "station", workspace=None, project_id="bao-cao-quy")
    init_project(paths, project_id="bao-cao-quy", title="Báo cáo quý")
    assert paths.project_root == tmp_path / "station" / "projects" / "bao-cao-quy"
    assert paths.home.is_dir()


def test_safe_path_blocks_escape(tmp_path: Path) -> None:
    with pytest.raises(PathOutsideWorkspace):
        safe_path(tmp_path / "project", "../outside.txt")


from __future__ import annotations
from dataclasses import dataclass
from importlib.resources import files
from importlib.resources.abc import Traversable
from pathlib import Path
import yaml
from .models import DeckSpec, ProjectConfig

class PathOutsideWorkspace(ValueError): pass

@dataclass(frozen=True)
class WorkspacePaths:
    home: Path | None
    project_root: Path
    package_resources: Traversable
    builds_dir: Path
    exports_dir: Path
    state_dir: Path

def resolve_paths(*, home: Path | None = None, workspace: Path | None = None, project_id: str | None = None) -> WorkspacePaths:
    resolved_home = home.expanduser().resolve() if home else None
    if workspace is not None:
        root = workspace.expanduser().resolve()
    elif resolved_home is not None and project_id:
        ProjectConfig(project_id=project_id, title="validation")
        root = resolved_home / "projects" / project_id
    else:
        raise ValueError("workspace hoặc home + project_id là bắt buộc")
    return WorkspacePaths(resolved_home, root, files("presentation_studio").joinpath("resources"), root / "builds", root / "exports", root / ".presentation")

def safe_path(root: Path, relative: str | Path) -> Path:
    root = root.resolve()
    candidate = (root / relative).resolve()
    if not candidate.is_relative_to(root): raise PathOutsideWorkspace(str(candidate))
    return candidate

def init_project(paths: WorkspacePaths, *, project_id: str, title: str) -> ProjectConfig:
    config = ProjectConfig(project_id=project_id, title=title)
    if paths.home is not None and paths.project_root.is_relative_to(paths.home / "projects"):
        paths.home.mkdir(parents=True, exist_ok=True)
    for folder in (paths.project_root / "storyboard", paths.project_root / "design", paths.project_root / "assets" / "files", paths.builds_dir, paths.exports_dir, paths.state_dir):
        folder.mkdir(parents=True, exist_ok=True)
    target = safe_path(paths.project_root, "project.yaml")
    if target.exists(): raise FileExistsError(target)
    target.write_text(yaml.safe_dump(config.model_dump(mode="json"), allow_unicode=True, sort_keys=False), encoding="utf-8")
    return config

def load_project(root: Path) -> ProjectConfig:
    path = safe_path(root, "project.yaml")
    return ProjectConfig.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))

def load_deck(path: Path) -> DeckSpec:
    return DeckSpec.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))

def resolve_profile(ref: str, paths: WorkspacePaths) -> Path:
    try: scope, rest = ref.split(":", 1); name, version = rest.rsplit("@", 1)
    except ValueError as exc: raise ValueError(f"profile ref không hợp lệ: {ref}") from exc
    if scope == "project": base = paths.project_root / "profiles"
    elif scope == "user" and paths.home: base = paths.home / "profiles"
    elif scope == "builtin":
        resource = paths.package_resources.joinpath("profiles", name, version, "profile.yaml")
        if resource.is_file(): return Path(str(resource))
        raise FileNotFoundError(ref)
    else: raise FileNotFoundError(ref)
    candidate = safe_path(base, Path(name) / version / "profile.yaml")
    if not candidate.is_file(): raise FileNotFoundError(ref)
    return candidate


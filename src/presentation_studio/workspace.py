from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
from importlib.resources import files
from importlib.resources.abc import Traversable
import os
from pathlib import Path, PureWindowsPath
import re
import tempfile
from typing import Any

from pydantic import ValidationError
import yaml
from yaml.events import AliasEvent, MappingEndEvent, MappingStartEvent, ScalarEvent, SequenceEndEvent, SequenceStartEvent

from .models import DeckSpec, Profile, ProfileLock, ProjectConfig


DEFAULT_MAX_YAML_BYTES = 5 * 1024 * 1024
DEFAULT_MAX_YAML_DEPTH = 64
DEFAULT_MAX_YAML_NODES = 100_000
_PROFILE_REF = re.compile(
    r"^(?P<scope>builtin|user|project):(?P<name>[a-z0-9][a-z0-9-]{0,63})@(?P<version>\d+\.\d+\.\d+)$"
)


class WorkspaceInputError(ValueError):
    pass


class PathOutsideWorkspace(WorkspaceInputError):
    pass


class InputLimitError(WorkspaceInputError):
    pass


class InvalidYAML(WorkspaceInputError):
    pass


class ProjectConflict(RuntimeError):
    pass


@dataclass(frozen=True)
class WorkspacePaths:
    home: Path | None
    project_root: Path
    package_resources: Traversable
    builds_dir: Path
    exports_dir: Path
    state_dir: Path


def resolve_paths(
    *,
    home: Path | None = None,
    workspace: Path | None = None,
    project_id: str | None = None,
) -> WorkspacePaths:
    resolved_home = home.expanduser().resolve() if home else None
    if workspace is not None:
        root = workspace.expanduser().resolve()
    elif resolved_home is not None and project_id:
        ProjectConfig(project_id=project_id, title="validation")
        root = (resolved_home / "projects" / project_id).resolve()
    else:
        raise WorkspaceInputError("workspace hoặc home + project_id là bắt buộc")
    return WorkspacePaths(
        home=resolved_home,
        project_root=root,
        package_resources=files("presentation_studio").joinpath("resources"),
        builds_dir=root / "builds",
        exports_dir=root / "exports",
        state_dir=root / ".presentation",
    )


def safe_path(root: Path, relative: str | Path) -> Path:
    text = os.fspath(relative)
    if Path(text).is_absolute() or PureWindowsPath(text).is_absolute():
        raise PathOutsideWorkspace("absolute paths are not allowed")
    resolved_root = root.resolve()
    candidate = (resolved_root / text).resolve()
    if not candidate.is_relative_to(resolved_root):
        raise PathOutsideWorkspace(str(candidate))
    return candidate


def load_yaml_bytes_bounded(
    raw: bytes,
    *,
    max_bytes: int,
    max_depth: int,
    max_nodes: int,
) -> Any:
    if len(raw) > max_bytes:
        raise InputLimitError(f"YAML exceeds {max_bytes} bytes")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise InputLimitError("YAML must be UTF-8") from exc
    depth = 0
    nodes = 0
    try:
        for event in yaml.parse(text, Loader=yaml.SafeLoader):
            if isinstance(event, AliasEvent):
                raise InputLimitError("YAML aliases are not allowed")
            if isinstance(event, (MappingStartEvent, SequenceStartEvent)):
                depth += 1
                nodes += 1
                if depth > max_depth:
                    raise InputLimitError(f"YAML exceeds depth {max_depth}")
            elif isinstance(event, (MappingEndEvent, SequenceEndEvent)):
                depth -= 1
            elif isinstance(event, ScalarEvent):
                nodes += 1
            if nodes > max_nodes:
                raise InputLimitError(f"YAML exceeds {max_nodes} nodes")
        return yaml.safe_load(text)
    except InputLimitError:
        raise
    except yaml.YAMLError as exc:
        raise InvalidYAML("YAML không hợp lệ") from exc


def load_yaml_bounded(
    path: Path,
    *,
    max_bytes: int = DEFAULT_MAX_YAML_BYTES,
    max_depth: int = DEFAULT_MAX_YAML_DEPTH,
    max_nodes: int = DEFAULT_MAX_YAML_NODES,
) -> Any:
    try:
        size = path.stat().st_size
    except OSError:
        raise
    if size > max_bytes:
        raise InputLimitError(f"YAML exceeds {max_bytes} bytes")
    return load_yaml_bytes_bounded(
        path.read_bytes(),
        max_bytes=max_bytes,
        max_depth=max_depth,
        max_nodes=max_nodes,
    )


def _atomic_create_text(path: Path, text: str) -> None:
    payload = text.encode("utf-8")
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            prefix=f".{path.name}.",
            suffix=".tmp",
            dir=path.parent,
            delete=False,
        ) as stream:
            temporary = Path(stream.name)
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)
        temporary.unlink()
        temporary = None
    finally:
        if temporary is not None:
            try:
                temporary.unlink()
            except FileNotFoundError:
                pass


def _load_existing_project(target: Path) -> ProjectConfig:
    try:
        return ProjectConfig.model_validate(load_yaml_bounded(target))
    except (ValidationError, ValueError, OSError) as exc:
        raise ProjectConflict("project.yaml hiện có không hợp lệ") from exc


def init_project(
    paths: WorkspacePaths, *, project_id: str, title: str
) -> ProjectConfig:
    config = ProjectConfig(project_id=project_id, title=title)
    target = safe_path(paths.project_root, "project.yaml")
    if target.exists():
        existing = _load_existing_project(target)
        if existing == config:
            return existing
        raise ProjectConflict("project.yaml đã tồn tại với cấu hình khác")

    managed = [
        safe_path(paths.project_root, relative)
        for relative in (
            "storyboard",
            "design",
            "assets/files",
            "builds",
            "exports",
            ".presentation",
        )
    ]
    if paths.home is not None and paths.project_root.is_relative_to(
        (paths.home / "projects").resolve()
    ):
        paths.home.mkdir(parents=True, exist_ok=True)
    paths.project_root.mkdir(parents=True, exist_ok=True)
    for folder in managed:
        checked = safe_path(paths.project_root, folder.relative_to(paths.project_root))
        checked.mkdir(parents=True, exist_ok=True)

    rendered = yaml.safe_dump(
        config.model_dump(mode="json"), allow_unicode=True, sort_keys=False
    )
    try:
        _atomic_create_text(safe_path(paths.project_root, "project.yaml"), rendered)
    except FileExistsError:
        existing = _load_existing_project(target)
        if existing == config:
            return existing
        raise ProjectConflict("project.yaml đã được tạo với cấu hình khác") from None
    return config


def load_project(root: Path) -> ProjectConfig:
    path = safe_path(root, "project.yaml")
    return ProjectConfig.model_validate(load_yaml_bounded(path))


def load_deck(
    root: Path, relative_path: str | Path = "storyboard/deck.yaml"
) -> DeckSpec:
    path = safe_path(root, relative_path)
    return DeckSpec.model_validate(load_yaml_bounded(path))


def resolve_profile(ref: str, paths: WorkspacePaths) -> ProfileLock:
    match = _PROFILE_REF.fullmatch(ref)
    if match is None:
        raise WorkspaceInputError(f"profile ref không hợp lệ: {ref}")
    scope = match.group("scope")
    name = match.group("name")
    version = match.group("version")

    if scope == "builtin":
        resource = paths.package_resources.joinpath(
            "profiles", name, version, "profile.yaml"
        )
        if not resource.is_file():
            raise FileNotFoundError(ref)
        raw = resource.read_bytes()
    else:
        if scope == "project":
            base = paths.project_root / "profiles"
        elif paths.home is not None:
            base = paths.home / "profiles"
        else:
            raise FileNotFoundError(ref)
        path = safe_path(base, f"{name}/{version}/profile.yaml")
        if not path.is_file():
            raise FileNotFoundError(ref)
        raw = path.read_bytes()

    profile = Profile.model_validate(
        load_yaml_bytes_bounded(
            raw,
            max_bytes=DEFAULT_MAX_YAML_BYTES,
            max_depth=DEFAULT_MAX_YAML_DEPTH,
            max_nodes=DEFAULT_MAX_YAML_NODES,
        )
    )
    if profile.id != name or profile.version != version:
        raise WorkspaceInputError("profile identity không khớp reference")
    return ProfileLock(
        resolved_ref=ref,
        source_scope=scope,
        version=version,
        sha256=hashlib.sha256(raw).hexdigest(),
        applied_overrides={},
        font_resolution={},
        created_at=datetime.now(timezone.utc),
    )

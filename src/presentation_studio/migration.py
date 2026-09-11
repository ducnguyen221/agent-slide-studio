from __future__ import annotations

import argparse
import ctypes
from dataclasses import dataclass
import errno
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import sys
import tempfile
import unicodedata
from typing import Any
from uuid import uuid4

from pydantic import ValidationError
import yaml

from .fs import BoundDirectory
from .models import CLIError, CLIResult, DeckSpec, ProjectConfig
from .workspace import (
    DEFAULT_MAX_YAML_BYTES,
    DEFAULT_MAX_YAML_DEPTH,
    DEFAULT_MAX_YAML_NODES,
    load_yaml_bytes_bounded,
)


class MigrationInputError(ValueError):
    def __init__(self, message: str, *, location: str | None = None):
        super().__init__(message)
        self.location = location


class MigrationConflict(RuntimeError):
    pass


@dataclass(frozen=True)
class MigrationLimits:
    max_files: int = 512
    max_entries: int = 4096
    max_file_bytes: int = 10 * 1024 * 1024
    max_total_bytes: int = 50 * 1024 * 1024
    max_yaml_nodes: int = 200_000


@dataclass(frozen=True)
class Candidate:
    path: Path
    relative_path: str
    raw: bytes
    sha256: str
    source_id: str
    parsed_yaml: Any | None = None

    def report(self) -> dict[str, str | int]:
        return {
            "relative_path": self.relative_path,
            "sha256": self.sha256,
            "bytes": len(self.raw),
        }


@dataclass(frozen=True)
class StagingArea:
    path: Path
    device: int
    inode: int
    parent_device: int
    parent_inode: int
    parent_binding: BoundDirectory
    directory_binding: BoundDirectory

    def close(self) -> None:
        first_error: OSError | None = None
        for binding in (self.directory_binding, self.parent_binding):
            try:
                binding.close()
            except OSError as exc:
                if first_error is None:
                    first_error = exc
        if first_error is not None:
            raise first_error


def _fsync_directory(directory: Path) -> None:
    with BoundDirectory.open(directory) as binding:
        binding.fsync()


def _rename_noreplace(source: Path, destination: Path) -> None:
    """Atomically rename a directory while refusing every existing destination."""
    if os.name == "nt":
        os.rename(source, destination)
        return

    library = ctypes.CDLL(None, use_errno=True)
    encoded_source = os.fsencode(source)
    encoded_destination = os.fsencode(destination)
    if sys.platform.startswith("linux"):
        rename = getattr(library, "renameat2", None)
        if rename is None:
            raise OSError(errno.ENOTSUP, "atomic no-replace rename is unavailable")
        rename.argtypes = [
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_uint,
        ]
        rename.restype = ctypes.c_int
        result = rename(-100, encoded_source, -100, encoded_destination, 1)
    elif sys.platform == "darwin":
        rename = getattr(library, "renamex_np", None)
        if rename is None:
            raise OSError(errno.ENOTSUP, "atomic no-replace rename is unavailable")
        rename.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint]
        rename.restype = ctypes.c_int
        result = rename(encoded_source, encoded_destination, 4)
    else:
        raise OSError(errno.ENOTSUP, "atomic no-replace rename is unavailable")
    if result != 0:
        error_number = ctypes.get_errno()
        raise OSError(error_number, os.strerror(error_number), destination)


def _slug(value: str, *, fallback: str) -> str:
    value = value.replace("Đ", "D").replace("đ", "d")
    ascii_value = (
        unicodedata.normalize("NFKD", value)
        .encode("ascii", "ignore")
        .decode()
        .lower()
    )
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_value).strip("-")
    return (slug or fallback)[:64].rstrip("-")


def _scalar_text(
    value: Any,
    *,
    location: str,
    default: str = "",
) -> str:
    if value is None:
        return default
    if isinstance(value, (str, int, float, bool)):
        return str(value)
    raise MigrationInputError(
        f"{location} must be a scalar value", location=location
    )


def _field_text(
    values: dict[str, Any],
    key: str,
    *,
    location: str,
    default: str = "",
    fallback_key: str | None = None,
) -> str:
    value = values.get(key)
    if value is None or value == "":
        value = values.get(fallback_key) if fallback_key is not None else None
    return _scalar_text(value, location=location, default=default)


def _is_link_or_junction(path: Path) -> bool:
    is_junction = getattr(path, "is_junction", None)
    return path.is_symlink() or bool(is_junction and is_junction())


_EXCLUDED_DIRECTORIES = {
    ".git",
    ".hg",
    ".svn",
    ".cache",
    "__pycache__",
    "cache",
    "config",
    "node_modules",
}
_SENSITIVE_PATTERNS = (
    re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(
        rb"(?i)\b(?:password|passwd|secret|client_secret|api[_-]?key|access[_-]?token|refresh[_-]?token)\b\s*[:=]\s*['\"]?[^\s'\"#]{4,}"
    ),
    re.compile(rb"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(rb"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(rb"(?i)\bbearer\s+[A-Za-z0-9._~+/=-]{8,}"),
    re.compile(rb"\b(?:sk-[A-Za-z0-9_-]{16,}|AIza[0-9A-Za-z_-]{20,}|xox[baprs]-[A-Za-z0-9-]{10,})\b"),
    re.compile(rb"(?i)\b(?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?|mssql|redis)://[^\s]+"),
)

_SENSITIVE_KEYS = {
    "authorization",
    "bearer",
    "password",
    "passwd",
    "secret",
    "client_secret",
    "api_key",
    "access_token",
    "refresh_token",
    "provider_token",
    "aws_secret_access_key",
    "connection_string",
    "database_url",
}


def _reference_is_forbidden(relative: Path) -> bool:
    return any(
        part.startswith(".") or part.casefold() in _EXCLUDED_DIRECTORIES
        for part in relative.parts
    )


def _discover_deck(
    source: Path, limits: MigrationLimits, explicit: str | None
) -> Path:
    root_candidates: list[Path] = []
    entry_count = 0
    candidate_count = 0
    stack = [source]
    while stack:
        directory = stack.pop()
        with os.scandir(directory) as entries:
            for entry in entries:
                entry_count += 1
                if entry_count > limits.max_entries:
                    raise MigrationInputError("source exceeds discovery entry limit")
                path = Path(entry.path)
                if entry.is_symlink() or _is_link_or_junction(path):
                    raise MigrationInputError("source contains a linked entry")
                if entry.is_dir(follow_symlinks=False):
                    if not _reference_is_forbidden(path.relative_to(source)):
                        stack.append(path)
                    continue
                if path.suffix.lower() not in {".yaml", ".yml", ".md"}:
                    continue
                candidate_count += 1
                if candidate_count > limits.max_files:
                    raise MigrationInputError("source exceeds candidate count limit")
                if path.parent == source and not _reference_is_forbidden(
                    path.relative_to(source)
                ):
                    root_candidates.append(path)

    if explicit is not None:
        relative = Path(explicit)
        if (
            relative.is_absolute()
            or ".." in relative.parts
            or _reference_is_forbidden(relative)
            or relative.suffix.lower() not in {".yaml", ".yml", ".md"}
        ):
            raise MigrationInputError("explicit legacy deck path is invalid")
        selected = source / relative
        if not selected.is_file():
            raise MigrationInputError("explicit legacy deck does not exist")
        return selected

    by_name = {
        path.name.casefold(): path
        for path in root_candidates
        if path.name.casefold()
        in {
            "deck.yaml",
            "deck.yml",
            "presentation.yaml",
            "presentation.yml",
            "slides.yaml",
            "slides.yml",
        }
    }
    if len(by_name) == 1:
        return next(iter(by_name.values()))
    if len(by_name) > 1:
        raise MigrationInputError("multiple allowlisted legacy decks found")
    root_yaml = [
        path for path in root_candidates if path.suffix.lower() in {".yaml", ".yml"}
    ]
    if len(root_yaml) == 1:
        return root_yaml[0]
    if len(root_yaml) > 1:
        raise MigrationInputError("legacy deck selection is ambiguous; use --deck")
    markdown = [
        path
        for path in root_candidates
        if path.name.casefold() in {"deck.md", "presentation.md", "slides.md"}
    ]
    if len(markdown) == 1:
        return markdown[0]
    raise MigrationInputError("no deterministic legacy deck was found")


def _read_candidate(path: Path, source: Path, limits: MigrationLimits) -> bytes:
    if _is_link_or_junction(path) or not path.resolve().is_relative_to(source):
        raise MigrationInputError("source candidate escapes the source directory")
    flags = (
        os.O_RDONLY
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_BINARY", 0)
    )
    descriptor = os.open(path, flags)
    try:
        opened = os.fstat(descriptor)
        current = path.lstat()
        if (
            not stat.S_ISREG(opened.st_mode)
            or opened.st_nlink != 1
            or _is_link_or_junction(path)
            or (opened.st_dev, opened.st_ino) != (current.st_dev, current.st_ino)
        ):
            raise MigrationInputError("source candidate has an unsafe identity")
        if opened.st_size > limits.max_file_bytes:
            raise MigrationInputError("source candidate exceeds file size limit")
        remaining = limits.max_file_bytes + 1
        chunks: list[bytes] = []
        while remaining:
            chunk = os.read(descriptor, min(64 * 1024, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        raw = b"".join(chunks)
        if len(raw) > limits.max_file_bytes:
            raise MigrationInputError("source candidate exceeds file size limit")
        after = path.lstat()
        if (opened.st_dev, opened.st_ino) != (after.st_dev, after.st_ino):
            raise MigrationInputError("source candidate changed during scan")
        return raw
    finally:
        os.close(descriptor)


def _reject_sensitive(raw: bytes, relative: str) -> None:
    if any(pattern.search(raw) for pattern in _SENSITIVE_PATTERNS):
        raise MigrationInputError(
            "source candidate contains sensitive credential material",
            location=relative,
        )


def _reject_sensitive_tree(value: Any, relative: str, key: str | None = None) -> None:
    if key is not None:
        normalized = re.sub(r"[^a-z0-9]+", "_", key.casefold()).strip("_")
        if normalized in _SENSITIVE_KEYS and value not in (None, "", False):
            raise MigrationInputError(
                "selected source contains credential material", location=relative
            )
    if isinstance(value, dict):
        for child_key, child in value.items():
            _reject_sensitive_tree(child, relative, str(child_key))
    elif isinstance(value, list):
        for child in value:
            _reject_sensitive_tree(child, relative)
    elif isinstance(value, str):
        encoded = value.encode("utf-8", errors="ignore")
        if any(pattern.search(encoded) for pattern in _SENSITIVE_PATTERNS[4:]):
            raise MigrationInputError(
                "selected source contains credential material", location=relative
            )


def _explicit_references(data: dict[str, Any]) -> list[str]:
    refs: list[str] = []
    top_level = data.get("source_files", [])
    if top_level is not None:
        if not isinstance(top_level, list):
            raise MigrationInputError("source_files must be a list", location="source_files")
        refs.extend(
            _scalar_text(value, location=f"source_files[{index}]")
            for index, value in enumerate(top_level)
        )
    slides = data.get("slides", [])
    if isinstance(slides, list):
        for index, slide in enumerate(slides):
            if not isinstance(slide, dict):
                continue
            for key in ("notes_file", "speaker_notes_file"):
                if key in slide:
                    refs.append(
                        _scalar_text(slide[key], location=f"slides[{index}].{key}")
                    )
    return refs


def _scan_candidates(
    source: Path, limits: MigrationLimits, *, deck_path: str | None = None
) -> list[Candidate]:
    if _is_link_or_junction(source):
        raise MigrationInputError("source cannot be a link or junction")
    if not source.is_dir():
        raise MigrationInputError("source directory does not exist")
    source = source.resolve()
    selected_deck = _discover_deck(source, limits, deck_path)
    candidates_by_path: dict[Path, Candidate] = {}
    total_bytes = 0
    used_ids: set[str] = set()
    node_budget = [limits.max_yaml_nodes]

    def scan(path: Path, index: int, *, parse_yaml: bool) -> Candidate:
        nonlocal total_bytes
        raw = _read_candidate(path, source, limits)
        total_bytes += len(raw)
        if total_bytes > limits.max_total_bytes:
            raise MigrationInputError("source exceeds total size limit")
        relative = path.relative_to(source).as_posix()
        base_id = _slug(path.stem, fallback=f"source-{index}")
        source_id = base_id
        suffix = 2
        while source_id in used_ids:
            suffix_text = f"-{suffix}"
            source_id = f"{base_id[: 64 - len(suffix_text)]}{suffix_text}"
            suffix += 1
        used_ids.add(source_id)
        parsed: Any | None = None
        if parse_yaml:
            try:
                parsed = load_yaml_bytes_bounded(
                    raw,
                    max_bytes=min(DEFAULT_MAX_YAML_BYTES, limits.max_file_bytes),
                    max_depth=DEFAULT_MAX_YAML_DEPTH,
                    max_nodes=DEFAULT_MAX_YAML_NODES,
                    node_budget=node_budget,
                )
            except ValueError as exc:
                raise MigrationInputError(
                    str(exc) if "aggregate YAML node budget" in str(exc) else f"invalid legacy YAML: {relative}",
                    location=relative,
                ) from exc
            if parsed is not None and not isinstance(parsed, dict):
                raise MigrationInputError(
                    f"legacy YAML must contain a mapping: {relative}", location=relative
                )
        candidate = Candidate(
            path=path,
            relative_path=relative,
            raw=raw,
            sha256=hashlib.sha256(raw).hexdigest(),
            source_id=source_id,
            parsed_yaml=parsed,
        )
        candidates_by_path[path] = candidate
        return candidate

    deck = scan(
        selected_deck,
        1,
        parse_yaml=selected_deck.suffix.lower() in {".yaml", ".yml"},
    )
    _reject_sensitive(deck.raw, deck.relative_path)
    if deck.parsed_yaml is not None:
        _reject_sensitive_tree(deck.parsed_yaml, deck.relative_path)
    selected = [deck]
    if isinstance(deck.parsed_yaml, dict):
        for ref in _explicit_references(deck.parsed_yaml):
            ref_path = Path(ref)
            if (
                ref_path.is_absolute()
                or ".." in ref_path.parts
                or _reference_is_forbidden(ref_path)
                or ref_path.suffix.lower() not in {".yaml", ".yml", ".md"}
            ):
                raise MigrationInputError("legacy source reference is invalid")
            path = source / ref_path
            if not path.is_file():
                raise MigrationInputError("referenced legacy source does not exist")
            candidate = candidates_by_path.get(path)
            if candidate is None:
                if len(candidates_by_path) >= limits.max_files:
                    raise MigrationInputError("source exceeds candidate count limit")
                candidate = scan(
                    path,
                    len(candidates_by_path) + 1,
                    parse_yaml=path.suffix.lower() in {".yaml", ".yml"},
                )
            _reject_sensitive(candidate.raw, candidate.relative_path)
            if candidate.parsed_yaml is not None:
                _reject_sensitive_tree(candidate.parsed_yaml, candidate.relative_path)
            if candidate not in selected:
                selected.append(candidate)
    return selected


def _source_ref(candidate: Candidate) -> dict[str, str]:
    return {
        "id": candidate.source_id,
        "kind": "legacy-source",
        "title": candidate.relative_path,
        "uri": f"sources/originals/{candidate.relative_path}",
        "sha256": candidate.sha256,
    }


def _markdown_notes(candidate: Candidate) -> str:
    try:
        return (
            candidate.raw.decode("utf-8")
            .replace("\r\n", "\n")
            .replace("\r", "\n")
            .strip()
        )
    except UnicodeDecodeError as exc:
        raise MigrationInputError("legacy Markdown must be UTF-8") from exc


def _text_content(
    item: dict[str, Any], *, location: str
) -> tuple[dict[str, Any], list[str]]:
    known = {"title", "subtitle", "points", "value", "label"}
    title = _field_text(
        item,
        "title",
        fallback_key="value",
        location=f"{location}.title",
    )
    subtitle = _field_text(item, "subtitle", location=f"{location}.subtitle")
    points = item.get("points")
    if points is None:
        points = []
    if not isinstance(points, list):
        raise MigrationInputError(
            f"{location}.points must be a list", location=f"{location}.points"
        )
    return {
        "text": title,
        "label": _field_text(
            item,
            "label",
            location=f"{location}.label",
            default=subtitle,
        )
        or None,
        "items": [
            _scalar_text(point, location=f"{location}.points[{index}]")
            for index, point in enumerate(points)
        ],
    }, sorted(set(item) - known)


def _map_elements(slide: dict[str, Any], slide_index: int) -> tuple[list[dict[str, Any]], list[str]]:
    elements: list[dict[str, Any]] = []
    unmapped: list[str] = []
    element_index = 1

    for role, field in (("card", "cards"), ("metric", "metrics")):
        values = slide.get(field)
        if values is None:
            values = []
        if not isinstance(values, list):
            location = f"slides[{slide_index}].{field}"
            raise MigrationInputError(
                f"{location} must be a list", location=location
            )
        for item_index, item in enumerate(values):
            if not isinstance(item, dict):
                location = f"slides[{slide_index}].{field}[{item_index}]"
                raise MigrationInputError(
                    f"{location} must be a mapping", location=location
                )
            content, extra = _text_content(
                item, location=f"slides[{slide_index}].{field}[{item_index}]"
            )
            elements.append(
                {
                    "element_id": f"e{element_index:02d}",
                    "kind": "text",
                    "role": role,
                    "content": content,
                }
            )
            unmapped.extend(f"{field}.{name}" for name in extra)
            element_index += 1

    process_steps = slide.get("process_steps")
    if process_steps is None:
        process_steps = []
    if not isinstance(process_steps, list):
        location = f"slides[{slide_index}].process_steps"
        raise MigrationInputError(
            f"{location} must be a list", location=location
        )
    if process_steps:
        mapped_steps = []
        for index, step in enumerate(process_steps, start=1):
            if not isinstance(step, dict):
                location = f"slides[{slide_index}].process_steps[{index - 1}]"
                raise MigrationInputError(
                    f"{location} must be a mapping", location=location
                )
            location = f"slides[{slide_index}].process_steps[{index - 1}]"
            mapped_steps.append(
                {
                    "id": _slug(
                        _scalar_text(
                            step.get("id"),
                            location=f"{location}.id",
                            default=f"step-{index}",
                        ),
                        fallback=f"step-{index}",
                    ),
                    "title": _scalar_text(
                        step.get("title"),
                        location=f"{location}.title",
                        default=f"Step {index}",
                    ),
                    "description": _scalar_text(
                        step.get("description"),
                        location=f"{location}.description",
                    )
                    or None,
                }
            )
            unmapped.extend(
                f"process_steps.{name}"
                for name in sorted(
                    set(step) - {"id", "step_number", "title", "description"}
                )
            )
        elements.append(
            {
                "element_id": f"e{element_index:02d}",
                "kind": "process",
                "role": "process",
                "content": {"steps": mapped_steps, "connector": "sequence"},
            }
        )
        element_index += 1

    timeline = slide.get("timeline_nodes")
    if timeline is None:
        timeline = []
    if not isinstance(timeline, list):
        location = f"slides[{slide_index}].timeline_nodes"
        raise MigrationInputError(
            f"{location} must be a list", location=location
        )
    if timeline:
        items = []
        for item_index, item in enumerate(timeline):
            if not isinstance(item, dict):
                location = f"slides[{slide_index}].timeline_nodes[{item_index}]"
                raise MigrationInputError(
                    f"{location} must be a mapping", location=location
                )
            location = f"slides[{slide_index}].timeline_nodes[{item_index}]"
            items.append(
                {
                    "time_label": _field_text(
                        item, "time_label", location=f"{location}.time_label"
                    ),
                    "title": _field_text(
                        item, "title", location=f"{location}.title"
                    ),
                    "description": _field_text(
                        item, "description", location=f"{location}.description"
                    )
                    or None,
                }
            )
            unmapped.extend(
                f"timeline_nodes.{name}"
                for name in sorted(set(item) - {"time_label", "title", "description"})
            )
        elements.append(
            {
                "element_id": f"e{element_index:02d}",
                "kind": "timeline",
                "role": "timeline",
                "content": {"items": items},
            }
        )
        element_index += 1

    visual = slide.get("visual_asset")
    if visual is not None and not isinstance(visual, dict):
        location = f"slides[{slide_index}].visual_asset"
        raise MigrationInputError(
            f"{location} must be a mapping", location=location
        )
    if visual:
        location = f"slides[{slide_index}].visual_asset"
        asset_ref = _slug(
            _field_text(
                visual,
                "asset_id",
                location=f"{location}.asset_id",
                default=f"legacy-image-{slide_index + 1}",
            ),
            fallback=f"legacy-image-{slide_index + 1}",
        )
        elements.append(
            {
                "element_id": f"e{element_index:02d}",
                "kind": "image",
                "role": _slug(
                    _field_text(
                        visual,
                        "slot_type",
                        location=f"{location}.slot_type",
                        default="image",
                    ),
                    fallback="image",
                ),
                "alt_text": _field_text(
                    visual,
                    "alt_text",
                    location=f"{location}.alt_text",
                    default="Legacy image",
                ),
                "content": {"asset_ref": asset_ref},
            }
        )
        unmapped.extend(
            f"visual_asset.{name}"
            for name in sorted(
                set(visual) - {"asset_id", "slot_type", "alt_text"}
            )
        )
    return elements, unmapped


def _map_yaml_deck(
    data: dict[str, Any], deck_source: Candidate, candidates: list[Candidate]
) -> tuple[DeckSpec, list[str]]:
    slides = data.get("slides")
    if not isinstance(slides, list) or not slides:
        raise MigrationInputError(
            "legacy deck requires a non-empty slides list", location="slides"
        )
    candidates_by_relative = {
        candidate.relative_path: candidate
        for candidate in candidates
    }
    mapped_slides: list[dict[str, Any]] = []
    unmapped = sorted(
        set(data)
        - {"title", "subject", "target_audience", "slides", "source_files"}
    )
    known_slide_fields = {
        "slide_id",
        "title",
        "subtitle",
        "archetype",
        "layout",
        "speaker_notes",
        "speaker_notes_file",
        "notes_file",
        "notes",
        "objective_id",
        "bloom_verb",
        "cards",
        "metrics",
        "process_steps",
        "timeline_nodes",
        "visual_asset",
    }
    for index, legacy_slide in enumerate(slides):
        if not isinstance(legacy_slide, dict):
            location = f"slides[{index}]"
            raise MigrationInputError(
                f"{location} must be a mapping", location=location
            )
        slide_location = f"slides[{index}]"
        slide_id = _slug(
            _field_text(
                legacy_slide,
                "slide_id",
                location=f"{slide_location}.slide_id",
                default=f"slide-{index + 1}",
            ),
            fallback=f"slide-{index + 1}",
        )
        elements, element_unmapped = _map_elements(legacy_slide, index)
        source_refs = [deck_source.source_id]
        notes = _field_text(
            legacy_slide,
            "speaker_notes",
            fallback_key="notes",
            location=f"{slide_location}.speaker_notes",
        ).strip()
        notes_ref = legacy_slide.get("notes_file")
        if notes_ref is None:
            notes_ref = legacy_slide.get("speaker_notes_file")
        markdown = None
        if notes_ref is not None:
            notes_relative = _scalar_text(
                notes_ref, location=f"{slide_location}.notes_file"
            ).replace("\\", "/")
            markdown = candidates_by_relative.get(notes_relative)
            if markdown is None:
                raise MigrationInputError(
                    "referenced legacy notes were not selected",
                    location=f"{slide_location}.notes_file",
                )
        if markdown is not None:
            markdown_text = _markdown_notes(markdown)
            notes = "\n\n".join(value for value in (notes, markdown_text) if value)
            source_refs.append(markdown.source_id)
        objective = legacy_slide.get("objective_id")
        bloom = legacy_slide.get("bloom_verb")
        objective_text = _scalar_text(
            objective,
            location=f"{slide_location}.objective_id",
        )
        bloom_text = _scalar_text(
            bloom,
            location=f"{slide_location}.bloom_verb",
        )
        archetype = _field_text(
            legacy_slide,
            "archetype",
            fallback_key="layout",
            location=f"{slide_location}.archetype",
            default="content",
        )
        mapped_slides.append(
            {
                "slide_id": slide_id,
                "title": _field_text(
                    legacy_slide,
                    "title",
                    location=f"{slide_location}.title",
                    default=f"Slide {index + 1}",
                ),
                "message": _field_text(
                    legacy_slide,
                    "subtitle",
                    location=f"{slide_location}.subtitle",
                )
                or None,
                "layout_ref": f"legacy:{_slug(archetype, fallback='content')}@1.0.0",
                "elements": elements,
                "notes": notes or None,
                "source_refs": source_refs,
                "learning": {
                    "objective_ids": [
                        _slug(objective_text, fallback=f"objective-{index + 1}")
                    ]
                    if objective_text
                    else [],
                    "bloom_verb": bloom_text or None,
                }
                if objective_text or bloom_text
                else None,
            }
        )
        unmapped.extend(
            f"slides[{index}].{name}"
            for name in sorted(set(legacy_slide) - known_slide_fields)
        )
        unmapped.extend(
            f"slides[{index}].{name}" for name in element_unmapped
        )
    deck = DeckSpec(
        title=_field_text(
            data, "title", location="title", default="Imported legacy deck"
        ),
        audience=_field_text(
            data, "target_audience", location="target_audience", default="General"
        ),
        purpose=_field_text(
            data, "subject", location="subject", default="Imported legacy deck"
        ),
        sources=[_source_ref(candidate) for candidate in candidates],
        slides=mapped_slides,
    )
    return deck, sorted(set(unmapped))


def _map_markdown_deck(candidate: Candidate) -> DeckSpec:
    text = _markdown_notes(candidate)
    title_match = re.search(r"^#\s+(.+)$", text, flags=re.MULTILINE)
    title = title_match.group(1).strip() if title_match else candidate.path.stem
    headings = list(re.finditer(r"^##\s+(.+)$", text, flags=re.MULTILINE))
    slides: list[dict[str, Any]] = []
    if headings:
        for index, match in enumerate(headings):
            end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
            notes = text[match.end() : end].strip()
            slides.append(
                {
                    "slide_id": f"slide-{index + 1}",
                    "title": match.group(1).strip(),
                    "layout_ref": "legacy:content@1.0.0",
                    "elements": [],
                    "notes": notes or None,
                    "source_refs": [candidate.source_id],
                }
            )
    else:
        slides.append(
            {
                "slide_id": "slide-1",
                "title": title,
                "layout_ref": "legacy:content@1.0.0",
                "elements": [],
                "notes": text,
                "source_refs": [candidate.source_id],
            }
        )
    return DeckSpec(
        title=title,
        audience="General",
        purpose="Imported legacy deck",
        sources=[_source_ref(candidate)],
        slides=slides,
    )


def _parse_deck(candidates: list[Candidate]) -> tuple[DeckSpec, list[str]]:
    yaml_decks: list[tuple[Candidate, dict[str, Any]]] = []
    for candidate in candidates:
        if candidate.path.suffix.lower() not in {".yaml", ".yml"}:
            continue
        data = candidate.parsed_yaml
        if data is None:
            try:
                data = load_yaml_bytes_bounded(
                    candidate.raw,
                    max_bytes=DEFAULT_MAX_YAML_BYTES,
                    max_depth=DEFAULT_MAX_YAML_DEPTH,
                    max_nodes=DEFAULT_MAX_YAML_NODES,
                )
            except (ValueError, yaml.YAMLError) as exc:
                raise MigrationInputError(
                    f"invalid legacy YAML: {candidate.relative_path}",
                    location=candidate.relative_path,
                ) from exc
        if data is not None and not isinstance(data, dict):
            raise MigrationInputError(
                f"legacy YAML must contain a mapping: {candidate.relative_path}",
                location=candidate.relative_path,
            )
        if isinstance(data, dict) and "slides" in data:
            yaml_decks.append((candidate, data))
    if len(yaml_decks) > 1:
        raise MigrationInputError("multiple legacy deck YAML files found")
    if yaml_decks:
        candidate, data = yaml_decks[0]
        return _map_yaml_deck(data, candidate, candidates)
    markdown = next(
        (candidate for candidate in candidates if candidate.path.suffix.lower() == ".md"),
        None,
    )
    if markdown is None:
        raise MigrationInputError("no legacy deck was found")
    return _map_markdown_deck(markdown), []


def _write_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())


def _write_json(path: Path, value: Any) -> None:
    _write_bytes(
        path,
        (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode(
            "utf-8"
        ),
    )


def _write_yaml(path: Path, value: Any) -> None:
    _write_bytes(
        path,
        yaml.safe_dump(value, allow_unicode=True, sort_keys=False).encode("utf-8"),
    )


def _capture_staging(stage: Path) -> StagingArea:
    parent_binding = BoundDirectory.open(stage.parent)
    directory_binding: BoundDirectory | None = None
    try:
        directory_binding = BoundDirectory.open(stage, allow_delete=True)
        info = os.fstat(directory_binding.descriptor)
        parent_info = os.fstat(parent_binding.descriptor)
        if _is_link_or_junction(stage) or not stat.S_ISDIR(info.st_mode):
            raise MigrationConflict("migration staging directory has an unsafe identity")
        return StagingArea(
            path=stage,
            device=info.st_dev,
            inode=info.st_ino,
            parent_device=parent_info.st_dev,
            parent_inode=parent_info.st_ino,
            parent_binding=parent_binding,
            directory_binding=directory_binding,
        )
    except BaseException:
        try:
            if directory_binding is not None:
                directory_binding.close()
        finally:
            parent_binding.close()
        raise


def _remove_staging(stage: StagingArea, parent: Path, target_name: str) -> None:
    try:
        if (
            stage.path.parent.absolute() != parent.absolute()
            or not stage.path.name.startswith(f".{target_name}.migration-")
        ):
            raise RuntimeError("refusing to remove unexpected staging path")
        try:
            stage.parent_binding.verify()
            stage.directory_binding.verify()
        except OSError as exc:
            raise MigrationConflict("migration staging identity changed") from exc
        current = stage.parent_binding.lstat(stage.path.name)
        if (
            not stat.S_ISDIR(current.st_mode)
            or (current.st_dev, current.st_ino) != (stage.device, stage.inode)
        ):
            raise MigrationConflict("migration staging identity changed")
        quarantine = f".{target_name}.cleanup-{uuid4().hex}"
        stage.parent_binding.replace(stage.path.name, quarantine)
        moved = stage.parent_binding.lstat(quarantine)
        if (moved.st_dev, moved.st_ino) != (stage.device, stage.inode):
            stage.parent_binding.replace(quarantine, stage.path.name)
            raise MigrationConflict("migration staging identity changed during cleanup")
        if os.name == "nt":
            shutil.rmtree(parent / quarantine)
        else:
            shutil.rmtree(quarantine, dir_fd=stage.parent_binding.descriptor)
        stage.parent_binding.fsync()
    except FileNotFoundError:
        return
    finally:
        stage.close()


def _promote_staging(stage: Path, target: Path) -> None:
    """Move a complete staged directory atomically without replacing a target."""
    try:
        _rename_noreplace(stage, target)
        _fsync_directory(target.parent)
    except FileExistsError as exc:
        raise MigrationConflict("migration target appeared during promotion") from exc
    except OSError as exc:
        if exc.errno in {errno.EEXIST, errno.ENOTEMPTY} or target.exists():
            raise MigrationConflict("migration target appeared during promotion") from exc
        raise


def _emit_internal_diagnostic(exc: Exception) -> str:
    diagnostic_id = uuid4().hex
    exception_type = re.sub(r"[^A-Za-z0-9_]", "_", type(exc).__name__)[:64]
    print(
        "technical-error "
        f"diagnostic_id={diagnostic_id} command=migrate category=internal "
        f"exception_type={exception_type or 'Exception'}",
        file=sys.stderr,
    )
    return diagnostic_id


def migrate(
    source: Path,
    target: Path,
    *,
    apply: bool,
    limits: MigrationLimits | None = None,
    deck_path: str | None = None,
) -> dict[str, Any]:
    limits = limits or MigrationLimits()
    source = source.expanduser().absolute()
    target = target.expanduser().absolute()
    if target.exists():
        raise MigrationConflict("migration target already exists")
    if target.resolve().is_relative_to(source.resolve()):
        raise MigrationInputError("migration target cannot be inside source")

    candidates = (
        _scan_candidates(source, limits, deck_path=deck_path)
        if deck_path is not None
        else _scan_candidates(source, limits)
    )
    try:
        deck, unmapped = _parse_deck(candidates)
    except ValidationError as exc:
        errors = exc.errors(include_url=False)
        location = (
            ".".join(str(part) for part in errors[0]["loc"]) if errors else None
        )
        raise MigrationInputError(
            "legacy content cannot satisfy the v1 schema", location=location
        ) from exc
    data = {
        "dry_run": not apply,
        "planned_files": len(candidates),
        "files": [candidate.report() for candidate in candidates],
        "unmapped_fields": unmapped,
    }
    if not apply:
        return data

    target.parent.mkdir(parents=True, exist_ok=True)
    stage = _capture_staging(
        Path(tempfile.mkdtemp(prefix=f".{target.name}.migration-", dir=target.parent))
    )
    try:
        project = ProjectConfig(
            project_id=_slug(target.name, fallback="imported-project"),
            title=deck.title,
        )
        _write_yaml(stage.path / "project.yaml", project.model_dump(mode="json"))
        _write_yaml(
            stage.path / "storyboard" / "deck.yaml", deck.model_dump(mode="json")
        )
        for candidate in candidates:
            _write_bytes(
                stage.path / "sources" / "originals" / candidate.relative_path,
                candidate.raw,
            )
        _write_json(
            stage.path / "migration-report.json",
            {
                "schema_version": "1.0",
                "source_files": [candidate.report() for candidate in candidates],
                "unmapped_fields": unmapped,
            },
        )
        _promote_staging(stage.path, target)
        stage.close()
        stage = None
    finally:
        if stage is not None:
            _remove_staging(stage, target.parent, target.name)
    return data


def migrate_result(
    source: Path, target: Path, *, apply: bool, deck_path: str | None = None
) -> CLIResult:
    try:
        data = migrate(source, target, apply=apply, deck_path=deck_path)
    except MigrationConflict:
        return CLIResult(
            command="migrate",
            status="failed",
            exit_code=6,
            errors=[
                CLIError(
                    code="MIGRATION_CONFLICT",
                    message_vi="Đích migration đã tồn tại; không có file nào bị ghi đè.",
                )
            ],
        )
    except MigrationInputError as exc:
        return CLIResult(
            command="migrate",
            status="failed",
            exit_code=2,
            errors=[
                CLIError(
                    code="MIGRATION_INPUT_INVALID",
                    message_vi="Nguồn migration không hợp lệ hoặc vượt giới hạn.",
                    field=exc.location,
                )
            ],
        )
    except ValidationError as exc:
        errors = exc.errors(include_url=False)
        location = (
            ".".join(str(part) for part in errors[0]["loc"]) if errors else None
        )
        return CLIResult(
            command="migrate",
            status="failed",
            exit_code=2,
            errors=[
                CLIError(
                    code="MIGRATION_INPUT_INVALID",
                    message_vi="Nguồn migration không hợp lệ hoặc vượt giới hạn.",
                    field=location,
                )
            ],
        )
    except PermissionError:
        return CLIResult(
            command="migrate",
            status="failed",
            exit_code=3,
            errors=[
                CLIError(
                    code="PERMISSION_DENIED",
                    message_vi="Không đủ quyền đọc nguồn hoặc ghi đích migration.",
                )
            ],
        )
    except OSError:
        return CLIResult(
            command="migrate",
            status="failed",
            exit_code=5,
            errors=[
                CLIError(
                    code="FILESYSTEM_FAILURE",
                    message_vi="Migration thất bại khi thao tác hệ thống tệp.",
                )
            ],
        )
    except Exception as exc:
        diagnostic_id = _emit_internal_diagnostic(exc)
        return CLIResult(
            command="migrate",
            status="failed",
            exit_code=5,
            errors=[
                CLIError(
                    code="MIGRATION_INTERNAL_ERROR",
                    message_vi=(
                        "Migration gặp lỗi nội bộ đã được lọc; mã chẩn đoán "
                        "đã được ghi vào stderr."
                    ),
                    evidence_ref=f"diagnostic:{diagnostic_id}",
                )
            ],
        )
    return CLIResult(
        command="migrate", status="passed", exit_code=0, data=data
    )


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise MigrationInputError(message)


def main(argv: list[str] | None = None) -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8")
    parser = _Parser(prog="migrate-legacy")
    parser.add_argument("--source", required=True)
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--deck")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    try:
        args = parser.parse_args(argv)
        result = migrate_result(
            Path(args.source),
            Path(args.workspace),
            apply=args.apply,
            deck_path=args.deck,
        )
    except MigrationInputError:
        result = CLIResult(
            command="migrate",
            status="failed",
            exit_code=2,
            errors=[
                CLIError(
                    code="MIGRATION_INPUT_INVALID",
                    message_vi="Tham số migration không hợp lệ.",
                )
            ],
        )
    print(result.model_dump_json())
    raise SystemExit(result.exit_code)


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
import unicodedata
from typing import Any

from pydantic import ValidationError
import yaml

from .models import CLIError, CLIResult, DeckSpec, ProjectConfig
from .workspace import load_yaml_bounded


class MigrationInputError(ValueError):
    pass


class MigrationConflict(RuntimeError):
    pass


@dataclass(frozen=True)
class MigrationLimits:
    max_files: int = 512
    max_file_bytes: int = 10 * 1024 * 1024
    max_total_bytes: int = 50 * 1024 * 1024


@dataclass(frozen=True)
class Candidate:
    path: Path
    relative_path: str
    raw: bytes
    sha256: str
    source_id: str

    def report(self) -> dict[str, str | int]:
        return {
            "relative_path": self.relative_path,
            "sha256": self.sha256,
            "bytes": len(self.raw),
        }


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


def _is_link_or_junction(path: Path) -> bool:
    is_junction = getattr(path, "is_junction", None)
    return path.is_symlink() or bool(is_junction and is_junction())


def _candidate_paths(source: Path) -> list[Path]:
    candidates: list[Path] = []
    for root, directories, filenames in os.walk(source, followlinks=False):
        root_path = Path(root)
        for directory in list(directories):
            child = root_path / directory
            if _is_link_or_junction(child):
                raise MigrationInputError("source contains a linked directory")
        for filename in filenames:
            path = root_path / filename
            if path.suffix.lower() in {".yaml", ".yml", ".md"}:
                candidates.append(path)
    return sorted(candidates, key=lambda item: item.relative_to(source).as_posix())


def _scan_candidates(source: Path, limits: MigrationLimits) -> list[Candidate]:
    if _is_link_or_junction(source):
        raise MigrationInputError("source cannot be a link or junction")
    if not source.is_dir():
        raise MigrationInputError("source directory does not exist")
    source = source.resolve()
    paths = _candidate_paths(source)
    if not paths:
        raise MigrationInputError("source contains no supported YAML or Markdown")
    if len(paths) > limits.max_files:
        raise MigrationInputError("source exceeds candidate count limit")

    candidates: list[Candidate] = []
    total_bytes = 0
    used_ids: set[str] = set()
    for index, path in enumerate(paths, start=1):
        if _is_link_or_junction(path) or not path.resolve().is_relative_to(source):
            raise MigrationInputError("source candidate escapes the source directory")
        try:
            size = path.stat().st_size
        except OSError:
            raise
        if size > limits.max_file_bytes:
            raise MigrationInputError("source candidate exceeds file size limit")
        total_bytes += size
        if total_bytes > limits.max_total_bytes:
            raise MigrationInputError("source exceeds total size limit")
        raw = path.read_bytes()
        if len(raw) != size or _is_link_or_junction(path):
            raise MigrationInputError("source candidate changed during scan")
        relative = path.relative_to(source).as_posix()
        base_id = _slug(path.stem, fallback=f"source-{index}")
        source_id = base_id
        suffix = 2
        while source_id in used_ids:
            suffix_text = f"-{suffix}"
            source_id = f"{base_id[: 64 - len(suffix_text)]}{suffix_text}"
            suffix += 1
        used_ids.add(source_id)
        candidates.append(
            Candidate(
                path=path,
                relative_path=relative,
                raw=raw,
                sha256=hashlib.sha256(raw).hexdigest(),
                source_id=source_id,
            )
        )
    return candidates


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


def _text_content(item: dict[str, Any]) -> dict[str, Any]:
    known = {"title", "subtitle", "points", "value", "label"}
    title = str(item.get("title") or item.get("value") or "")
    subtitle = str(item.get("subtitle") or "")
    points = item.get("points") or []
    if not isinstance(points, list):
        points = [str(points)]
    return {
        "text": title,
        "label": str(item.get("label") or subtitle) or None,
        "items": [str(point) for point in points],
    }, sorted(set(item) - known)


def _map_elements(slide: dict[str, Any], slide_index: int) -> tuple[list[dict[str, Any]], list[str]]:
    elements: list[dict[str, Any]] = []
    unmapped: list[str] = []
    element_index = 1

    for role, field in (("card", "cards"), ("metric", "metrics")):
        values = slide.get(field) or []
        if values and not isinstance(values, list):
            raise MigrationInputError(f"slides[{slide_index}].{field} must be a list")
        for item in values:
            if not isinstance(item, dict):
                raise MigrationInputError(f"slides[{slide_index}].{field} item must be a mapping")
            content, extra = _text_content(item)
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

    process_steps = slide.get("process_steps") or []
    if process_steps:
        if not isinstance(process_steps, list):
            raise MigrationInputError(f"slides[{slide_index}].process_steps must be a list")
        mapped_steps = []
        for index, step in enumerate(process_steps, start=1):
            if not isinstance(step, dict):
                raise MigrationInputError("process step must be a mapping")
            mapped_steps.append(
                {
                    "id": _slug(str(step.get("id") or f"step-{index}"), fallback=f"step-{index}"),
                    "title": str(step.get("title") or f"Step {index}"),
                    "description": str(step.get("description")) if step.get("description") is not None else None,
                }
            )
            unmapped.extend(
                f"process_steps.{name}"
                for name in sorted(set(step) - {"id", "step_number", "title", "description"})
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

    timeline = slide.get("timeline_nodes") or []
    if timeline:
        if not isinstance(timeline, list):
            raise MigrationInputError(f"slides[{slide_index}].timeline_nodes must be a list")
        items = []
        for item in timeline:
            if not isinstance(item, dict):
                raise MigrationInputError("timeline item must be a mapping")
            items.append(
                {
                    "time_label": str(item.get("time_label") or ""),
                    "title": str(item.get("title") or ""),
                    "description": str(item.get("description")) if item.get("description") is not None else None,
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
    if visual:
        if not isinstance(visual, dict):
            raise MigrationInputError(f"slides[{slide_index}].visual_asset must be a mapping")
        asset_ref = _slug(
            str(visual.get("asset_id") or f"legacy-image-{slide_index + 1}"),
            fallback=f"legacy-image-{slide_index + 1}",
        )
        elements.append(
            {
                "element_id": f"e{element_index:02d}",
                "kind": "image",
                "role": _slug(str(visual.get("slot_type") or "image"), fallback="image"),
                "alt_text": str(visual.get("alt_text") or "Legacy image"),
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
        raise MigrationInputError("legacy deck requires a non-empty slides list")
    markdown_by_stem = {
        _slug(candidate.path.stem, fallback="markdown"): candidate
        for candidate in candidates
        if candidate.path.suffix.lower() == ".md"
    }
    mapped_slides: list[dict[str, Any]] = []
    unmapped = sorted(
        set(data)
        - {"title", "subject", "target_audience", "slides"}
    )
    known_slide_fields = {
        "slide_id",
        "title",
        "subtitle",
        "archetype",
        "layout",
        "speaker_notes",
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
            raise MigrationInputError(f"slides[{index}] must be a mapping")
        slide_id = _slug(
            str(legacy_slide.get("slide_id") or f"slide-{index + 1}"),
            fallback=f"slide-{index + 1}",
        )
        elements, element_unmapped = _map_elements(legacy_slide, index)
        source_refs = [deck_source.source_id]
        notes = str(
            legacy_slide.get("speaker_notes") or legacy_slide.get("notes") or ""
        ).strip()
        markdown = markdown_by_stem.get(slide_id)
        if markdown is not None:
            markdown_text = _markdown_notes(markdown)
            notes = "\n\n".join(value for value in (notes, markdown_text) if value)
            source_refs.append(markdown.source_id)
        objective = legacy_slide.get("objective_id")
        bloom = legacy_slide.get("bloom_verb")
        mapped_slides.append(
            {
                "slide_id": slide_id,
                "title": str(legacy_slide.get("title") or f"Slide {index + 1}"),
                "message": str(legacy_slide.get("subtitle")) if legacy_slide.get("subtitle") is not None else None,
                "layout_ref": f"legacy:{_slug(str(legacy_slide.get('archetype') or legacy_slide.get('layout') or 'content'), fallback='content')}@1.0.0",
                "elements": elements,
                "notes": notes or None,
                "source_refs": source_refs,
                "learning": {
                    "objective_ids": [_slug(str(objective), fallback=f"objective-{index + 1}")] if objective else [],
                    "bloom_verb": str(bloom) if bloom else None,
                }
                if objective or bloom
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
        title=str(data.get("title") or "Imported legacy deck"),
        audience=str(data.get("target_audience") or "General"),
        purpose=str(data.get("subject") or "Imported legacy deck"),
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
        try:
            data = load_yaml_bounded(candidate.path)
        except (ValueError, yaml.YAMLError) as exc:
            raise MigrationInputError(
                f"invalid legacy YAML: {candidate.relative_path}"
            ) from exc
        if data is not None and not isinstance(data, dict):
            raise MigrationInputError(
                f"legacy YAML must contain a mapping: {candidate.relative_path}"
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


def _remove_staging(stage: Path, parent: Path, target_name: str) -> None:
    resolved_stage = stage.resolve()
    resolved_parent = parent.resolve()
    if (
        resolved_stage.parent != resolved_parent
        or not resolved_stage.name.startswith(f".{target_name}.migration-")
    ):
        raise RuntimeError("refusing to remove unexpected staging path")
    shutil.rmtree(resolved_stage)


def migrate(
    source: Path,
    target: Path,
    *,
    apply: bool,
    limits: MigrationLimits | None = None,
) -> dict[str, Any]:
    limits = limits or MigrationLimits()
    source = source.expanduser().absolute()
    target = target.expanduser().absolute()
    if target.exists():
        raise MigrationConflict("migration target already exists")
    if target.resolve().is_relative_to(source.resolve()):
        raise MigrationInputError("migration target cannot be inside source")

    candidates = _scan_candidates(source, limits)
    try:
        deck, unmapped = _parse_deck(candidates)
    except ValidationError as exc:
        raise MigrationInputError("legacy content cannot satisfy the v1 schema") from exc
    data = {
        "dry_run": not apply,
        "planned_files": len(candidates),
        "files": [candidate.report() for candidate in candidates],
        "unmapped_fields": unmapped,
    }
    if not apply:
        return data

    target.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(
        tempfile.mkdtemp(prefix=f".{target.name}.migration-", dir=target.parent)
    )
    try:
        project = ProjectConfig(
            project_id=_slug(target.name, fallback="imported-project"),
            title=deck.title,
        )
        _write_yaml(stage / "project.yaml", project.model_dump(mode="json"))
        _write_yaml(stage / "storyboard" / "deck.yaml", deck.model_dump(mode="json"))
        for candidate in candidates:
            _write_bytes(
                stage / "sources" / "originals" / candidate.relative_path,
                candidate.raw,
            )
        _write_json(
            stage / "migration-report.json",
            {
                "schema_version": "1.0",
                "source_files": [candidate.report() for candidate in candidates],
                "unmapped_fields": unmapped,
            },
        )
        os.replace(stage, target)
        stage = Path()
    finally:
        if stage != Path() and stage.exists():
            _remove_staging(stage, target.parent, target.name)
    return data


def migrate_result(source: Path, target: Path, *, apply: bool) -> CLIResult:
    try:
        data = migrate(source, target, apply=apply)
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
    except (MigrationInputError, ValidationError):
        return CLIResult(
            command="migrate",
            status="failed",
            exit_code=2,
            errors=[
                CLIError(
                    code="MIGRATION_INPUT_INVALID",
                    message_vi="Nguồn migration không hợp lệ hoặc vượt giới hạn.",
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
    except Exception:
        return CLIResult(
            command="migrate",
            status="failed",
            exit_code=5,
            errors=[
                CLIError(
                    code="MIGRATION_INTERNAL_ERROR",
                    message_vi="Migration gặp lỗi nội bộ đã được lọc.",
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
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    try:
        args = parser.parse_args(argv)
        result = migrate_result(
            Path(args.source), Path(args.workspace), apply=args.apply
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

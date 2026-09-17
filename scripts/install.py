#!/usr/bin/env python3
"""Install the explicit skill payload; dry-run unless --apply is supplied."""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import stat
import sys
import uuid
from pathlib import Path

from build_manifest import PACKAGE_NAME, package_files, payload_files


NAME = PACKAGE_NAME


def _is_linklike(candidate: Path) -> bool:
    is_junction = getattr(candidate, "is_junction", None)
    junction = callable(is_junction) and is_junction()
    try:
        attributes = getattr(os.lstat(candidate), "st_file_attributes", 0)
    except OSError:
        attributes = 0
    reparse = bool(
        attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    )
    return candidate.is_symlink() or junction or reparse


def ancestors_safe(path: Path) -> None:
    for candidate in (path, *path.parents):
        if _is_linklike(candidate):
            raise ValueError(
                f"Từ chối ghi qua symlink/junction/reparse point: {candidate}. "
                "Hãy cài thủ công có kiểm soát."
            )


def inside(path: Path, other: Path) -> bool:
    try:
        path.relative_to(other)
        return True
    except ValueError:
        return False


def ensure_scoped_destination(base: Path, destination: Path) -> None:
    """Reject redirection outside the selected project/home immediately before use."""
    ancestors_safe(destination)
    resolved = destination.resolve(strict=False)
    if not inside(resolved, base):
        raise ValueError(f"Đích thoát scope qua link/reparse point: {destination}")


def make_plan(source: Path, host: str, scope: str, base: Path):
    hosts = ["codex", "claude", "antigravity"] if host == "all" else [host]
    plan: list[tuple[Path, Path]] = []
    seen: set[str] = set()
    for current_host in hosts:
        if scope == "project":
            parent = (
                base / ".claude/skills"
                if current_host == "claude"
                else base / ".agents/skills"
            )
        else:
            parent = {
                "codex": base / ".agents/skills",
                "claude": base / ".claude/skills",
                "antigravity": base / ".gemini/config/skills",
            }[current_host]
        destination = parent / NAME
        key = os.path.normcase(str(destination))
        if key not in seen:
            plan.append((source, destination))
            seen.add(key)
    return plan


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_integrity(root: Path, *, strict: bool) -> None:
    """Validate hashes from the package being checked, not from the source repo."""
    root = root.resolve()
    manifest_path = root / "manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Không đọc được manifest tại {root}: {exc}") from exc
    if manifest.get("package") != NAME or not isinstance(manifest.get("files"), list):
        raise ValueError(f"Manifest không đúng package {NAME}: {root}")
    declared = [item.get("path") for item in manifest["files"]]
    expected = [path.relative_to(root).as_posix() for path in payload_files(root)]
    if declared != expected:
        raise ValueError(f"Manifest không khớp explicit payload tại {root}")
    for item in manifest["files"]:
        path = root / item["path"]
        if (
            not path.is_file()
            or path.stat().st_size != item.get("bytes")
            or _sha256(path) != item.get("sha256")
        ):
            raise ValueError(f"Hash payload sai: {item['path']}")
    if strict:
        expected_package = {
            path.relative_to(root).as_posix() for path in package_files(root)
        }
        actual_package = {
            path.relative_to(root).as_posix()
            for path in root.rglob("*")
            if path.is_file()
        }
        if actual_package != expected_package:
            extra = sorted(actual_package - expected_package)
            missing = sorted(expected_package - actual_package)
            raise ValueError(
                f"Installed package không đúng explicit payload; "
                f"extra={extra}, missing={missing}"
            )


def _check_source_symlinks(source: Path) -> None:
    for path in package_files(source):
        current = path
        while True:
            if _is_linklike(current):
                raise ValueError(
                    f"Nguồn có symlink/junction/reparse point không được tự sao chép: {current}"
                )
            if current == source:
                break
            current = current.parent


def _copy_package(source: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=False)
    for source_file in package_files(source):
        relative = source_file.relative_to(source)
        destination_file = destination / relative
        destination_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_file, destination_file)


def _remove_destination(destination: Path) -> None:
    if destination.is_dir() and not destination.is_symlink():
        shutil.rmtree(destination)
    elif destination.exists() or destination.is_symlink():
        destination.unlink()


def rollback_destinations(
    completed: list[tuple[Path, Path | None]],
) -> list[str]:
    """Attempt every rollback and return secondary errors without hiding the cause."""
    errors: list[str] = []
    for destination, backup in reversed(completed):
        try:
            _remove_destination(destination)
        except Exception as exc:
            errors.append(f"remove {destination}: {exc}")
        if backup is not None and backup.exists():
            try:
                os.replace(backup, destination)
            except Exception as exc:
                errors.append(f"restore {backup} → {destination}: {exc}")
    return errors


def configure_utf8_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="replace")


def main(argv: list[str] | None = None) -> int:
    configure_utf8_stdio()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--host",
        choices=["codex", "claude", "antigravity", "all"],
        default="codex",
    )
    parser.add_argument("--scope", choices=["project", "user"], default="project")
    parser.add_argument(
        "--target", type=Path, help="Gốc dự án đích, bắt buộc khi scope=project."
    )
    parser.add_argument(
        "--home",
        type=Path,
        help="Gốc user thay thế, chỉ dùng scope=user; hữu ích cho kiểm thử.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Cho phép ghi; bỏ cờ này chỉ xem kế hoạch.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Cho phép nâng cấp bản có sẵn, có backup ngoài vùng discovery.",
    )
    args = parser.parse_args(argv)
    source = Path(__file__).resolve().parents[1]
    try:
        # The checkout may be named agent-slide-studio or anything else;
        # identity comes from the skill and manifest, never the source basename.
        if not (source / "SKILL.md").is_file():
            raise ValueError("Nguồn thiếu SKILL.md.")
        skill_header = (source / "SKILL.md").read_text(encoding="utf-8")
        skill_name = re.search(r"(?m)^name:\s*([a-z0-9-]+)\s*$", skill_header)
        if not skill_name or skill_name.group(1) != NAME:
            raise ValueError(f"SKILL.md không khai báo name: {NAME}")
        validate_integrity(source, strict=False)
        _check_source_symlinks(source)
        if args.scope == "project":
            if not args.target:
                raise ValueError("--target là bắt buộc cho scope=project.")
            if args.home:
                raise ValueError("--home chỉ dành cho scope=user.")
            base = args.target.expanduser().absolute()
        else:
            if args.target:
                raise ValueError("Dùng --home thay --target cho scope=user.")
            base = (args.home or Path.home()).expanduser().absolute()
        ancestors_safe(base)
        base = base.resolve()
        if base.exists() and not base.is_dir():
            raise ValueError("Đích gốc không phải thư mục.")
        plan = make_plan(source, args.host, args.scope, base)
        for _, destination in plan:
            ensure_scoped_destination(base, destination)
            resolved = destination.resolve()
            if inside(resolved, source) or inside(source, resolved):
                raise ValueError(f"Đích chồng lấn nguồn: {destination}")
            if destination.exists():
                if not destination.is_dir():
                    raise ValueError(f"Đích skill không là thư mục: {destination}")
                if not args.overwrite:
                    raise FileExistsError(
                        f"Đích đã có: {destination}. "
                        "Chỉ nâng cấp với --overwrite; sẽ tạo backup."
                    )
        print("ÁP DỤNG" if args.apply else "CHỈ XEM KẾ HOẠCH — chưa ghi tệp")
        for _, destination in plan:
            print(f"  skill: {destination}")
        print(
            "Chỉ cài explicit payload; không ghi AGENTS.md, CLAUDE.md, "
            "GEMINI.md hoặc cấu hình host."
        )
        if not args.apply:
            return 0
        token = (
            datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            + "-"
            + uuid.uuid4().hex[:8]
        )
        staging = base / ".aia-skill-staging" / token
        backups = base / ".aia-skill-backups" / token
        ancestors_safe(staging)
        ancestors_safe(backups)
        staging.mkdir(parents=True, exist_ok=False)
        staged: list[tuple[Path, Path, int]] = []
        completed: list[tuple[Path, Path | None]] = []
        try:
            # Stage and validate every destination package before replacing any
            # discovered skill.
            for index, (_, destination) in enumerate(plan):
                temporary = staging / str(index)
                _copy_package(source, temporary)
                validate_integrity(temporary, strict=True)
                staged.append((temporary, destination, index))
            for temporary, destination, index in staged:
                ensure_scoped_destination(base, destination)
                destination.parent.mkdir(parents=True, exist_ok=True)
                ensure_scoped_destination(base, destination)
                backup = None
                if destination.exists():
                    backup = backups / f"{index}-{destination.name}"
                    backup.parent.mkdir(parents=True, exist_ok=True)
                    os.replace(destination, backup)
                try:
                    os.replace(temporary, destination)
                    ensure_scoped_destination(base, destination)
                    validate_integrity(destination, strict=True)
                except Exception as original_error:
                    rollback_errors = rollback_destinations([(destination, backup)])
                    if rollback_errors:
                        raise RuntimeError(
                            f"Install failed: {original_error}; rollback errors: "
                            + "; ".join(rollback_errors)
                        ) from original_error
                    raise
                completed.append((destination, backup))
            print(
                f"Đã cài và xác minh {len(completed)} đích. "
                "Codex và Antigravity dùng chung một bản khi cài trong dự án."
            )
            if backups.exists():
                print(f"Backup: {backups}")
        except Exception as original_error:
            rollback_errors = rollback_destinations(completed)
            if rollback_errors:
                raise RuntimeError(
                    f"Install failed: {original_error}; rollback errors: "
                    + "; ".join(rollback_errors)
                ) from original_error
            raise
        finally:
            shutil.rmtree(staging, ignore_errors=True)
            try:
                staging.parent.rmdir()
            except OSError:
                pass
        return 0
    except (
        ValueError,
        FileExistsError,
        OSError,
        RuntimeError,
        KeyError,
        TypeError,
    ) as exc:
        print(f"LỖI: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Build deterministic checksums for the explicit install payload."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import sys
import tempfile
from pathlib import Path


PACKAGE_NAME = "agent-slide-studio"
PACKAGE_VERSION = "2.1.0"
INTEGRITY_FILES = ("manifest.json",)

# This allowlist is the package contract. Repository governance, plans, v1,
# superseded-v2, render outputs and arbitrary new files are not installed merely
# because they happen to exist beside the skill.
PAYLOAD_FILES = (
    "README.md",
    "SKILL.md",
    "INSTALL.md",
    "CHANGELOG.md",
    "NOTICE.md",
    "02-references/INDEX.md",
    "plugin/openai.yaml",
    "02-references/tooling/host-compatibility.md",
    "02-references/tooling/frontmatter-policy.md",
    "scripts/README.md",
    "scripts/install.py",
    "scripts/validate.py",
    "scripts/test_package.py",
    "scripts/build_manifest.py",
    "scripts/test_gallery.py",
    "scripts/requirements-check.txt",
)
PAYLOAD_TREES = (
    "01-design",
    "02-references/layouts",
    "02-references/images",
    "02-references/gallery",
    # INDEX.md points readers to these two preserved source collections. They
    # remain inactive and are excluded from active scans. superseded-v2 is not
    # part of the payload.
    "02-references/sources/originals",
    "02-references/sources/legacy",
    "03-workflow",
    "04-templates",
    "plugin",
)
TRANSIENT_PARTS = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".cache",
    "cache",
    "caches",
    ".tmp",
    "tmp",
    "temp",
    "output",
    "outputs",
}
TRANSIENT_SUFFIXES = {".pyc", ".pyo"}


def _is_transient(relative: Path) -> bool:
    return (
        any(part.lower() in TRANSIENT_PARTS for part in relative.parts)
        or relative.suffix.lower() in TRANSIENT_SUFFIXES
        or relative.name == ".DS_Store"
    )


def _is_junction_or_reparse(path: Path) -> bool:
    is_junction = getattr(path, "is_junction", None)
    if callable(is_junction) and is_junction():
        return True
    try:
        attributes = getattr(os.lstat(path), "st_file_attributes", 0)
    except OSError:
        return False
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return bool(attributes & reparse_flag)


def assert_safe_source(
    path: Path, *, root: Path | None = None, require_file: bool = False
) -> None:
    """Reject link-like package sources and multiply-linked regular files."""
    if root is not None:
        try:
            path.relative_to(root)
        except ValueError as exc:
            raise ValueError(f"Payload path escapes root: {path}") from exc
        current = path
        while True:
            if current.is_symlink() or _is_junction_or_reparse(current):
                raise ValueError(
                    f"Refuse symlink/junction/reparse payload ancestor: {current}"
                )
            if current == root:
                break
            current = current.parent
    elif path.is_symlink() or _is_junction_or_reparse(path):
        raise ValueError(f"Refuse symlink/junction/reparse payload path: {path}")
    if require_file:
        if not path.is_file():
            raise FileNotFoundError(f"Missing declared payload file: {path}")
        if os.lstat(path).st_nlink > 1:
            raise ValueError(f"Refuse hardlinked payload file: {path}")


def payload_files(root: Path) -> list[Path]:
    """Return the sorted, explicit payload; fail if a declared item is absent."""
    root = root.resolve()
    selected: set[Path] = set()
    for relative_name in PAYLOAD_FILES:
        path = root / relative_name
        if not path.is_file():
            raise FileNotFoundError(f"Missing declared payload file: {relative_name}")
        assert_safe_source(path, root=root, require_file=True)
        selected.add(path)
    for relative_name in PAYLOAD_TREES:
        tree = root / relative_name
        if not tree.is_dir():
            raise FileNotFoundError(f"Missing declared payload tree: {relative_name}")
        assert_safe_source(tree, root=root)
        tree_files = []
        for path in tree.rglob("*"):
            assert_safe_source(path, root=root, require_file=False)
            if path.is_file() and not _is_transient(path.relative_to(root)):
                assert_safe_source(path, root=root, require_file=True)
                tree_files.append(path)
        if not tree_files:
            raise FileNotFoundError(f"Declared payload tree is empty: {relative_name}")
        selected.update(tree_files)
    return sorted(selected, key=lambda path: path.relative_to(root).as_posix())


def package_files(root: Path) -> list[Path]:
    """Return payload plus generated integrity files used by the installer."""
    root = root.resolve()
    files = payload_files(root)
    for name in INTEGRITY_FILES:
        path = root / name
        if not path.is_file():
            raise FileNotFoundError(f"Missing integrity file: {name}")
        files.append(path)
    return sorted(files, key=lambda path: path.relative_to(root).as_posix())


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(root: Path) -> dict[str, object]:
    root = root.resolve()
    items = [
        {
            "path": path.relative_to(root).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        for path in payload_files(root)
    ]
    manifest: dict[str, object] = {
        "package": PACKAGE_NAME,
        "version": PACKAGE_VERSION,
        "algorithm": "SHA-256",
        "payload_policy": "scripts/build_manifest.py allowlist",
        "files": items,
    }
    return manifest


def _write_temp(directory: Path, prefix: str, data: bytes) -> Path:
    descriptor, name = tempfile.mkstemp(prefix=prefix, suffix=".tmp", dir=directory)
    path = Path(name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
    except Exception:
        path.unlink(missing_ok=True)
        raise
    return path


def write_manifest(root: Path, manifest: dict[str, object]) -> None:
    """Write manifest atomically and restore the previous file on failure."""
    manifest_path = root / "manifest.json"
    if manifest_path.exists():
        assert_safe_source(manifest_path, root=root, require_file=True)
    original = manifest_path.read_bytes() if manifest_path.exists() else None
    encoded_manifest = (
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    ).encode("utf-8")
    manifest_temp = _write_temp(root, ".manifest-", encoded_manifest)
    try:
        os.replace(manifest_temp, manifest_path)
    except Exception as original_error:
        if original is None:
            manifest_path.unlink(missing_ok=True)
        else:
            restore = _write_temp(root, ".manifest-restore-", original)
            try:
                os.replace(restore, manifest_path)
            finally:
                restore.unlink(missing_ok=True)
        raise
    finally:
        manifest_temp.unlink(missing_ok=True)


def configure_utf8_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="replace")


def main(argv: list[str] | None = None) -> int:
    configure_utf8_stdio()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "root",
        nargs="?",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    args = parser.parse_args(argv)
    root = args.root.resolve()
    manifest = build(root)
    write_manifest(root, manifest)
    print(f"{len(manifest['files'])} payload files hashed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

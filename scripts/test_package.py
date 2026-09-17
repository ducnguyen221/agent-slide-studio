#!/usr/bin/env python3
"""Regression-test install, payload, manifest and active validator in temp dirs."""
from __future__ import annotations

import contextlib
import io
import json
import os
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TESTS: list[dict[str, str]] = []

for _stream in (sys.stdout, sys.stderr):
    _reconfigure = getattr(_stream, "reconfigure", None)
    if callable(_reconfigure):
        _reconfigure(encoding="utf-8", errors="replace")


def add(identifier: str, passed: bool, detail: str) -> None:
    TESTS.append(
        {"id": identifier, "status": "PASS" if passed else "FAIL", "detail": detail}
    )


def run_installer(
    *args: object, environment: dict[str, str] | None = None
) -> tuple[int, str]:
    process = subprocess.run(
        [sys.executable, str(ROOT / "scripts/install.py"), *map(str, args)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=environment,
    )
    return process.returncode, process.stdout + process.stderr


def run_validator(package: Path) -> tuple[int, dict[str, object]]:
    process = subprocess.run(
        [
            sys.executable,
            str(package / "scripts/validate.py"),
            str(package),
            "--require-manifest",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    try:
        result = json.loads(process.stdout)
    except json.JSONDecodeError:
        result = {"status": "INVALID_OUTPUT", "errors": [process.stdout, process.stderr]}
    return process.returncode, result


with tempfile.TemporaryDirectory(prefix="agent-slide-studio-test-") as temporary_root:
    temp = Path(temporary_root)
    project = temp / "project"
    return_code, output = run_installer(
        "--host", "all", "--scope", "project", "--target", project
    )
    add(
        "I01",
        return_code == 0 and not project.exists() and "CHỈ XEM KẾ HOẠCH" in output,
        "Dry-run là mặc định và không tạo thư mục đích.",
    )
    cp1252_environment = os.environ.copy()
    cp1252_environment["PYTHONIOENCODING"] = "cp1252"
    return_code, output = run_installer(
        "--host",
        "codex",
        "--scope",
        "project",
        "--target",
        temp / "encoding-check",
        environment=cp1252_environment,
    )
    add(
        "U01",
        return_code == 0 and "CHỈ XEM KẾ HOẠCH" in output,
        "CLI ép UTF-8 an toàn khi stdout bị redirect với PYTHONIOENCODING=cp1252.",
    )

    project.mkdir()
    protected = {
        "AGENTS.md": "KEEP AGENTS\n",
        "CLAUDE.md": "KEEP CLAUDE\n",
        "GEMINI.md": "KEEP GEMINI\n",
        ".codex/config.toml": "keep = true\n",
    }
    for relative, content in protected.items():
        path = project / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return_code, output = run_installer(
        "--host", "all", "--scope", "project", "--target", project, "--apply"
    )
    shared = project / ".agents/skills/agent-slide-studio"
    claude = project / ".claude/skills/agent-slide-studio"
    add(
        "I02",
        return_code == 0
        and (shared / "SKILL.md").is_file()
        and (claude / "SKILL.md").is_file()
        and len(list((project / ".agents/skills").iterdir())) == 1
        and "Đã cài và xác minh 2 đích" in output,
        "Cài all/project từ repo tên khác skill, tạo hai đích và tự xác minh.",
    )
    if return_code != 0 or not shared.is_dir() or not claude.is_dir():
        result = {
            "status": "FAIL",
            "scope": "Temp project/user installation and active static validation; not host runtime",
            "tests": TESTS,
            "setup_error": output,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        raise SystemExit(1)
    add(
        "I03",
        all((project / relative).read_text(encoding="utf-8") == content for relative, content in protected.items()),
        "Không sửa governance hoặc host config của dự án đích.",
    )
    forbidden = (
        "AGENTS.md",
        "CLAUDE.md",
        "GEMINI.md",
        "v1",
        "slide-design",
        ".superpowers",
        "docs/plans",
        "02-references/sources/superseded-v2",
        "scripts/render_previews.py",
        "scripts/render_classified.py",
    )
    add(
        "I04",
        all(not (shared / relative).exists() for relative in forbidden),
        "Installed explicit payload loại governance, v1, plans, superseded-v2 và renderer nguồn.",
    )
    validate_code, validate_result = run_validator(shared)
    add(
        "I05",
        validate_code == 0 and validate_result.get("status") == "PASS",
        "Validator nằm trong destination kiểm chính installed package.",
    )

    marker = shared / "TEST_MARKER.txt"
    marker.write_text("old install", encoding="utf-8")
    return_code, _ = run_installer(
        "--host", "all", "--scope", "project", "--target", project, "--apply"
    )
    add(
        "I06",
        return_code == 2 and marker.exists(),
        "Từ chối ghi đè khi chưa có --overwrite.",
    )
    return_code, _ = run_installer(
        "--host",
        "all",
        "--scope",
        "project",
        "--target",
        project,
        "--overwrite",
        "--apply",
    )
    backups = list((project / ".aia-skill-backups").rglob("TEST_MARKER.txt"))
    add(
        "I07",
        return_code == 0
        and not marker.exists()
        and len(backups) == 1
        and backups[0].read_text(encoding="utf-8") == "old install",
        "Nâng cấp tạo backup ngoài vùng skill discovery và bảo toàn bản cũ.",
    )

    user_home = temp / "userhome"
    (user_home / "AGENTS.md").parent.mkdir(parents=True, exist_ok=True)
    (user_home / "AGENTS.md").write_text("KEEP USER\n", encoding="utf-8")
    return_code, _ = run_installer(
        "--host", "all", "--scope", "user", "--home", user_home, "--apply"
    )
    expected_user = (
        ".agents/skills/agent-slide-studio/SKILL.md",
        ".claude/skills/agent-slide-studio/SKILL.md",
        ".gemini/config/skills/agent-slide-studio/SKILL.md",
    )
    add(
        "I08",
        return_code == 0
        and all((user_home / relative).is_file() for relative in expected_user)
        and (user_home / "AGENTS.md").read_text(encoding="utf-8") == "KEEP USER\n",
        "All/user cài ba skill package nhưng giữ nguyên governance user.",
    )
    return_code, _ = run_installer(
        "--host", "codex", "--scope", "project", "--target", ROOT, "--apply"
    )
    add(
        "I09",
        return_code == 2 and not (ROOT / ".agents").exists(),
        "Từ chối đích nằm trong nguồn để tránh tự sao chép vòng lặp.",
    )

    unsafe = temp / "unsafe"
    unsafe.mkdir()
    symlink_supported = True
    try:
        (unsafe / ".agents").symlink_to(temp / "elsewhere", target_is_directory=True)
    except OSError:
        symlink_supported = False
    if symlink_supported:
        return_code, _ = run_installer(
            "--host", "codex", "--scope", "project", "--target", unsafe, "--apply"
        )
        symlink_ok = return_code == 2 and not (temp / "elsewhere").exists()
    else:
        symlink_ok = True
    add(
        "I10",
        symlink_ok,
        "Từ chối symlink đích; môi trường không hỗ trợ symlink được ghi rõ là không áp dụng.",
    )
    junction_project = temp / "junction-project"
    junction_outside = temp / "junction-outside"
    (junction_project / ".agents").mkdir(parents=True)
    junction_outside.mkdir()
    junction_supported = False
    if os.name == "nt":
        junction_process = subprocess.run(
            [
                "cmd",
                "/c",
                "mklink",
                "/J",
                str(junction_project / ".agents/skills"),
                str(junction_outside),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        junction_supported = junction_process.returncode == 0
    if junction_supported:
        return_code, _ = run_installer(
            "--host",
            "codex",
            "--scope",
            "project",
            "--target",
            junction_project,
            "--apply",
        )
        junction_ok = (
            return_code == 2
            and not (junction_outside / "agent-slide-studio").exists()
        )
    else:
        junction_ok = True
    add(
        "I11",
        junction_ok,
        "Từ chối Windows junction thoát project scope; môi trường khác ghi không áp dụng.",
    )
    return_code, _ = run_installer(
        "--host",
        "claude",
        "--scope",
        "project",
        "--target",
        temp / "invalid",
        "--with-claude-agents",
    )
    add(
        "I12",
        return_code == 2 and not (temp / "invalid").exists(),
        "Không còn cài agent/config ngoài explicit skill payload.",
    )

    fixture = temp / "fixtures/arbitrary-source-name"
    fixture.parent.mkdir()
    shutil.copytree(shared, fixture)

    source_junction_root = temp / "source-junction-package"
    shutil.copytree(shared, source_junction_root)
    external_references = temp / "external-references"
    shutil.copytree(source_junction_root / "02-references", external_references)
    shutil.rmtree(source_junction_root / "02-references")
    source_junction_supported = False
    if os.name == "nt":
        junction_process = subprocess.run(
            [
                "cmd",
                "/c",
                "mklink",
                "/J",
                str(source_junction_root / "02-references"),
                str(external_references),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        source_junction_supported = junction_process.returncode == 0
    if source_junction_supported:
        junction_build = subprocess.run(
            [
                sys.executable,
                str(source_junction_root / "scripts/build_manifest.py"),
                str(source_junction_root),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        source_junction_ok = (
            junction_build.returncode != 0
            and "payload ancestor" in (junction_build.stdout + junction_build.stderr)
        )
    else:
        source_junction_ok = True
    add(
        "I13",
        source_junction_ok,
        "Manifest/package policy chặn intermediate junction trong source payload.",
    )

    skill = fixture / "SKILL.md"
    original = skill.read_bytes()
    skill.write_bytes(
        original.replace(
            b"name: agent-slide-studio\n",
            b"name: agent-slide-studio\nname: duplicate\n",
            1,
        )
    )
    code, result = run_validator(fixture)
    add(
        "V01",
        code == 1 and any("trùng" in error for error in result["errors"]),
        "Validator phát hiện khóa YAML frontmatter trùng.",
    )
    skill.write_bytes(original)

    readme = fixture / "README.md"
    original = readme.read_bytes()
    readme.write_bytes(original + b"\n[bad](no_such_file.md)\n")
    code, result = run_validator(fixture)
    add(
        "V02",
        code == 1 and any("Link" in error for error in result["errors"]),
        "Validator phát hiện active Markdown link hỏng/ngoài payload.",
    )
    readme.write_bytes(original)

    registry = fixture / "02-references/layouts/archetypes/registry.json"
    original = registry.read_bytes()
    registry_value = json.loads(original)
    registry_value[1]["id"] = registry_value[0]["id"]
    registry.write_text(json.dumps(registry_value, ensure_ascii=False), encoding="utf-8")
    code, result = run_validator(fixture)
    add(
        "V03",
        code == 1 and any("L01–L48" in error for error in result["errors"]),
        "Validator phát hiện ID layout trùng/thiếu.",
    )
    registry.write_bytes(original)

    original = registry.read_bytes()
    registry_value = json.loads(original)
    registry_value[0]["preview_png"] = "../../outside.png"
    registry.write_text(json.dumps(registry_value, ensure_ascii=False), encoding="utf-8")
    code, result = run_validator(fixture)
    add(
        "V04",
        code == 1 and any("path thoát package" in error for error in result["errors"]),
        "Validator chặn traversal registry trước mọi I/O ngoài package.",
    )
    registry.write_bytes(original)

    original = readme.read_bytes()
    readme.write_bytes(b"\xef\xbb\xbf" + original)
    code, result = run_validator(fixture)
    add(
        "V05",
        code == 1 and any("BOM" in error for error in result["errors"]),
        "Validator phát hiện UTF-8 BOM trong active payload.",
    )
    readme.write_bytes(original)

    preview = fixture / "02-references/gallery/layouts/L01.png"
    original = preview.read_bytes()
    preview.write_bytes(original[:16] + struct.pack(">I", 1400) + original[20:])
    code, result = run_validator(fixture)
    add(
        "V06",
        code == 1 and any("PNG không 16:9" in error for error in result["errors"]),
        "Validator phát hiện preview sai tỷ lệ.",
    )
    preview.write_bytes(original)

    compiler = fixture / "03-workflow/03-prompt-and-imagegen.md"
    original = compiler.read_bytes()
    compiler.write_bytes(original.replace(b"CANVAS |", b"OBJECTIVE |", 1))
    code, result = run_validator(fixture)
    add(
        "V07",
        code == 1 and any("Prompt compiler" in error for error in result["errors"]),
        "Validator phát hiện prompt compiler không còn đúng bảy section có thứ tự.",
    )
    compiler.write_bytes(original)

    ready_prompt = fixture / "04-templates/generation-ready-test.md"
    ready_prompt.write_text(
        "---\n"
        "title: \"Generation-ready test\"\n"
        "description: \"Temporary validator fault injection.\"\n"
        "document_type: test-fixture\n"
        "status: active\n"
        "---\n\n"
        "# Ready\n\n```text\n"
        + "\n".join(f"{section} | TODO" for section in (
            "CANVAS", "OBJECTIVE", "COMPOSITION", "STYLE", "CONTENT", "CONSTRAINTS", "NEGATIVE"
        ))
        + "\n```\n",
        encoding="utf-8",
    )
    code, result = run_validator(fixture)
    add(
        "V08",
        code == 1 and any("Generation-ready prompt còn placeholder" in error for error in result["errors"]),
        "Validator cho phép template trống nhưng chặn prompt generation-ready còn placeholder.",
    )
    ready_prompt.unlink()

    code, result = run_validator(fixture)
    add(
        "V09",
        code == 0 and result.get("status") == "PASS",
        "Fixture installed trở lại PASS sau khi phục hồi mọi fault injection.",
    )

    hardlink_backing = temp / "hardlink-backing.md"
    hardlink_backing.write_bytes(readme.read_bytes())
    readme_original = readme.read_bytes()
    readme.unlink()
    hardlink_supported = True
    try:
        os.link(hardlink_backing, readme)
    except OSError:
        hardlink_supported = False
        readme.write_bytes(readme_original)
    if hardlink_supported:
        code, result = run_validator(fixture)
        hardlink_ok = code == 1 and any(
            "hardlinked payload" in error for error in result["errors"]
        )
        readme.unlink()
        readme.write_bytes(readme_original)
    else:
        hardlink_ok = True
    add(
        "V10",
        hardlink_ok,
        "Validator/package policy từ chối hardlinked payload file khi filesystem hỗ trợ.",
    )

    import install as installer

    rollback_root = temp / "rollback"
    destination_one = rollback_root / "one"
    destination_two = rollback_root / "two"
    backup_one = rollback_root / "backup-one"
    backup_two = rollback_root / "backup-two"
    for path, marker_text in (
        (destination_one, "new-one"),
        (destination_two, "new-two"),
        (backup_one, "old-one"),
        (backup_two, "old-two"),
    ):
        path.mkdir(parents=True)
        (path / "marker.txt").write_text(marker_text, encoding="utf-8")
    original_rmtree = installer.shutil.rmtree

    def flaky_rmtree(path, *args, **kwargs):
        if Path(path) == destination_two:
            raise OSError("simulated locked destination")
        return original_rmtree(path, *args, **kwargs)

    installer.shutil.rmtree = flaky_rmtree
    try:
        rollback_errors = installer.rollback_destinations(
            [(destination_one, backup_one), (destination_two, backup_two)]
        )
    finally:
        installer.shutil.rmtree = original_rmtree
    add(
        "R01",
        bool(rollback_errors)
        and (destination_one / "marker.txt").read_text(encoding="utf-8") == "old-one"
        and backup_two.exists(),
        "Rollback tiếp tục phục hồi destination còn lại và báo secondary error khi một cleanup bị khóa.",
    )

    cli_rollback_target = temp / "rollback-cli-project"
    cli_rollback_target.mkdir()
    original_validate_integrity = installer.validate_integrity
    original_rollback_destinations = installer.rollback_destinations

    def fail_promoted_destination(root, *, strict):
        candidate = Path(root)
        if strict and candidate.name == "agent-slide-studio" and ".agents" in candidate.parts:
            raise RuntimeError("simulated destination validation failure")
        return original_validate_integrity(candidate, strict=strict)

    def fail_current_rollback(completed):
        if completed:
            return ["simulated rollback cleanup failure"]
        return []

    installer.validate_integrity = fail_promoted_destination
    installer.rollback_destinations = fail_current_rollback
    try:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(
            io.StringIO()
        ):
            rollback_cli_code = installer.main(
                [
                    "--host",
                    "codex",
                    "--scope",
                    "project",
                    "--target",
                    str(cli_rollback_target),
                    "--apply",
                ]
            )
    finally:
        installer.validate_integrity = original_validate_integrity
        installer.rollback_destinations = original_rollback_destinations
    add(
        "R02",
        rollback_cli_code == 2,
        "Secondary rollback RuntimeError giữ hợp đồng CLI: thông báo có kiểm soát, exit 2.",
    )

    import build_manifest as manifest_builder

    integrity_root = temp / "integrity-rollback"
    integrity_root.mkdir()
    integrity_manifest = integrity_root / "manifest.json"
    integrity_manifest.write_text("OLD MANIFEST\n", encoding="utf-8")
    original_replace = manifest_builder.os.replace

    def fail_manifest_replace(source, destination):
        raise OSError("simulated manifest replace failure")

    manifest_builder.os.replace = fail_manifest_replace
    integrity_failed = False
    try:
        manifest_builder.write_manifest(
            integrity_root,
            {"package": "test", "files": []},
        )
    except OSError:
        integrity_failed = True
    finally:
        manifest_builder.os.replace = original_replace
    add(
        "M00",
        integrity_failed
        and integrity_manifest.read_text(encoding="utf-8") == "OLD MANIFEST\n"
        and not list(integrity_root.glob(".*.tmp")),
        "Atomic manifest writer giữ bản cũ khi replace lỗi.",
    )

    manifest_before = (fixture / "manifest.json").read_bytes()
    build_command = [sys.executable, str(fixture / "scripts/build_manifest.py"), str(fixture)]
    first = subprocess.run(build_command, capture_output=True, text=True, encoding="utf-8")
    first_manifest = (fixture / "manifest.json").read_bytes()
    second = subprocess.run(build_command, capture_output=True, text=True, encoding="utf-8")
    add(
        "M01",
        first.returncode == 0
        and second.returncode == 0
        and first_manifest == (fixture / "manifest.json").read_bytes()
        and manifest_before == first_manifest,
        "Manifest tái tạo từ explicit payload là deterministic.",
    )

result = {
    "status": "PASS" if all(test["status"] == "PASS" for test in TESTS) else "FAIL",
    "scope": "Temp project/user installation and active static validation; not host runtime",
    "tests": TESTS,
}
print(json.dumps(result, ensure_ascii=False, indent=2))
if result["status"] != "PASS":
    raise SystemExit(1)

#!/usr/bin/env python3
"""Validate the active ImageGen knowledge package and its explicit payload."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote, urlsplit

try:
    import yaml
except ImportError as exc:
    raise SystemExit(
        "Thiếu PyYAML. Kiểm tra scripts/requirements-check.txt; "
        "chỉ cài khi người dùng cho phép."
    ) from exc

from build_manifest import PACKAGE_NAME, payload_files


PROMPT_SECTIONS = (
    "CANVAS",
    "OBJECTIVE",
    "COMPOSITION",
    "STYLE",
    "CONTENT",
    "CONSTRAINTS",
    "NEGATIVE",
)
INACTIVE_PREFIXES = ("02-references/sources/",)
PROMPT_PLACEHOLDER = re.compile(
    r"(?i)(?:TODO|TBD|PLACEHOLDER|FILL\s+ME|CHƯA\s+ĐIỀN|ĐIỀN\s+VÀO|"
    r"CẦN\s+ĐIỀN|\{\{[^}\n]+\}\}|<[^>\n]+>)"
)


class UniqueLoader(yaml.SafeLoader):
    pass


def unique_mapping(loader, node, deep=False):
    loader.flatten_mapping(node)
    mapping = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise ValueError(f"Khóa YAML trùng: {key}")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping
)


def json_unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Khóa JSON trùng: {key}")
        result[key] = value
    return result


def load_json(path: Path):
    return json.loads(
        path.read_text(encoding="utf-8"), object_pairs_hook=json_unique
    )


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def is_active(relative: str) -> bool:
    return not relative.startswith(INACTIVE_PREFIXES)


def _markdown_targets(text: str) -> list[str]:
    without_fences = re.sub(r"```[^\n]*\n.*?```", "", text, flags=re.S)
    without_fences = re.sub(r"~~~[^\n]*\n.*?~~~", "", without_fences, flags=re.S)
    return re.findall(r"\[[^\]\n]*\]\(([^)\n]+)\)", without_fences)


def _prompt_blocks(text: str) -> list[list[tuple[str, str]]]:
    blocks = []
    for block in re.findall(r"```(?:text)?\s*\n(.*?)```", text, flags=re.S):
        rows = []
        for line in block.splitlines():
            match = re.match(
                r"^\s*(CANVAS|OBJECTIVE|COMPOSITION|STYLE|CONTENT|"
                r"CONSTRAINTS|NEGATIVE)\s*\|(.*)$",
                line,
            )
            if match:
                rows.append((match.group(1), match.group(2).strip()))
        if rows:
            blocks.append(rows)
    return blocks


def _png_size(path: Path) -> tuple[int, int]:
    raw = path.read_bytes()
    if len(raw) < 24 or raw[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("PNG signature/IHDR không hợp lệ")
    return struct.unpack(">II", raw[16:24])


def _svg_size(path: Path) -> tuple[float, float]:
    svg = ET.fromstring(path.read_text(encoding="utf-8"))
    view_box = [float(value) for value in svg.attrib.get("viewBox", "").split()]
    if len(view_box) != 4:
        raise ValueError("SVG thiếu viewBox bốn số")
    return view_box[2], view_box[3]


def check(root: Path, require_manifest: bool = False):
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    stats = {
        "payload_files": 0,
        "active_files": 0,
        "active_markdown": 0,
        "local_links": 0,
        "layouts": 0,
        "infographics": 0,
        "preview_png": 0,
        "preview_svg": 0,
        "full_size_samples": 0,
        "generation_ready_prompts": 0,
    }

    def fail(message: str) -> None:
        errors.append(message)

    try:
        files = payload_files(root)
    except (FileNotFoundError, OSError, ValueError) as exc:
        return {
            "status": "FAIL",
            "scope": "Active package and explicit payload; not host runtime or model behavior",
            "stats": stats,
            "errors": [str(exc)],
            "warnings": warnings,
            "manifest_checked": False,
        }

    relative_files = {path.relative_to(root).as_posix() for path in files}
    package_targets = set(relative_files) | {"manifest.json"}
    package_directories = {
        parent.as_posix()
        for relative in package_targets
        for parent in Path(relative).parents
        if parent.as_posix() != "."
    }
    active_files = [
        path
        for path in files
        if is_active(path.relative_to(root).as_posix())
    ]
    stats["payload_files"] = len(files)
    stats["active_files"] = len(active_files)

    active_skill_files = [
        path.relative_to(root).as_posix()
        for path in active_files
        if path.name == "SKILL.md"
    ]
    if active_skill_files != ["SKILL.md"]:
        fail(f"Cần đúng một active SKILL.md ở root; thấy {active_skill_files}")

    expected_design = {"01-design/principles.md", "01-design/design-system.md"}
    actual_design = {
        path.relative_to(root).as_posix()
        for path in (root / "01-design").glob("*.md")
        if path.is_file()
    }
    if actual_design != expected_design:
        fail(f"Cần đúng hai design file; thấy {sorted(actual_design)}")
    if "02-references/INDEX.md" not in relative_files:
        fail("Thiếu reference INDEX canonical: 02-references/INDEX.md")
    expected_workflow = {
        f"03-workflow/{name}"
        for name in (
            "01-read-and-map.md",
            "02-lock-style-and-content.md",
            "03-prompt-and-imagegen.md",
            "04-review-and-handoff.md",
        )
    }
    actual_workflow = {
        path.relative_to(root).as_posix()
        for path in (root / "03-workflow").glob("*.md")
        if path.is_file()
    }
    if actual_workflow != expected_workflow:
        fail(f"Cần đúng bốn workflow file; thấy {sorted(actual_workflow)}")
    expected_templates = {
        f"04-templates/{name}"
        for name in ("deck-plan.md", "slide-prompt.md", "review-and-handoff.md")
    }
    actual_templates = {
        path.relative_to(root).as_posix()
        for path in (root / "04-templates").glob("*.md")
        if path.is_file()
    }
    if actual_templates != expected_templates:
        fail(f"Cần đúng ba template file; thấy {sorted(actual_templates)}")

    def local_link(source: Path, target: str) -> None:
        target = target.strip().split(' "', 1)[0].strip("<>")
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc or not parsed.path:
            return
        destination = (source.parent / unquote(parsed.path)).resolve()
        stats["local_links"] += 1
        try:
            relative = destination.relative_to(root).as_posix()
        except ValueError:
            fail(f"Link thoát gói: {source.relative_to(root)} → {target}")
            return
        if relative not in package_targets and relative not in package_directories:
            fail(
                f"Link không thuộc explicit payload: "
                f"{source.relative_to(root)} → {target}"
            )
        elif not destination.exists():
            fail(f"Link hỏng: {source.relative_to(root)} → {target}")

    for path in active_files:
        relative = path.relative_to(root).as_posix()
        suffix = path.suffix.lower()
        if path.is_symlink():
            fail("Symlink không được đóng gói: " + relative)
        if suffix in {".docx", ".doc", ".ttf", ".otf", ".woff", ".woff2", ".zip", ".pyc"}:
            fail("Tệp không được phép: " + relative)
        if suffix not in {".md", ".yaml", ".yml", ".json", ".py", ".html", ".svg", ".txt"}:
            continue
        raw = path.read_bytes()
        if raw.startswith(b"\xef\xbb\xbf"):
            fail("UTF-8 BOM: " + relative)
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            fail("Không phải UTF-8: " + relative)
            continue
        if suffix == ".md":
            stats["active_markdown"] += 1
            frontmatter = None
            if text.startswith("---\n") or text.startswith("---\r\n"):
                match = re.match(
                    r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)", text, flags=re.S
                )
                if not match:
                    fail("Frontmatter không đóng đúng: " + relative)
                else:
                    try:
                        frontmatter = yaml.load(match.group(1), Loader=UniqueLoader)
                    except Exception as exc:
                        fail(f"YAML frontmatter lỗi {relative}: {exc}")
            if relative == "SKILL.md":
                if not isinstance(frontmatter, dict):
                    fail("SKILL.md thiếu frontmatter mapping")
                else:
                    if set(frontmatter) != {"name", "description"}:
                        fail("SKILL.md không dùng đúng header name/description")
                    name = frontmatter.get("name")
                    description = frontmatter.get("description")
                    if name != PACKAGE_NAME:
                        fail(f"name của SKILL.md phải là {PACKAGE_NAME}")
                    if not isinstance(description, str) or not description.strip() or len(description) > 1024:
                        fail("description của SKILL.md không hợp lệ")
            else:
                required = {"title", "description", "document_type", "status"}
                allowed = required | {"id", "step", "host"}
                if not isinstance(frontmatter, dict):
                    fail("Active Markdown thiếu frontmatter mapping: " + relative)
                else:
                    missing = required - set(frontmatter)
                    extra = set(frontmatter) - allowed
                    if missing:
                        fail(f"Frontmatter thiếu {sorted(missing)}: {relative}")
                    if extra:
                        fail(f"Frontmatter có trường ngoài schema {sorted(extra)}: {relative}")
                    for key in ("title", "description", "document_type"):
                        if not isinstance(frontmatter.get(key), str) or not frontmatter[key].strip():
                            fail(f"Frontmatter {key} không hợp lệ: {relative}")
                    if frontmatter.get("status") != "active":
                        fail("Frontmatter status phải là active: " + relative)
            for target in _markdown_targets(text):
                local_link(path, target)
        elif suffix in {".yaml", ".yml"}:
            try:
                value = yaml.load(text, Loader=UniqueLoader)
                if relative == "plugin/openai.yaml":
                    if not isinstance(value, dict) or not isinstance(value.get("interface"), dict):
                        fail("plugin/openai.yaml thiếu interface")
                    if value.get("policy", {}).get("allow_implicit_invocation") is not True:
                        fail("plugin/openai.yaml policy sai profile")
            except Exception as exc:
                fail(f"Lỗi YAML {relative}: {exc}")
        elif suffix == ".json":
            try:
                load_json(path)
            except Exception as exc:
                fail(f"Lỗi JSON {relative}: {exc}")
        elif suffix == ".html":
            for target in re.findall(r"(?:href|src)=[\"']([^\"']+)[\"']", text):
                local_link(path, target)

    # The canonical compiler and blank template use the same exact seven-section
    # contract. Blank template fields are intentional; completed prompt blocks in
    # other active Markdown are treated as generation-ready and may not retain
    # placeholders.
    compiler_path = root / "03-workflow/03-prompt-and-imagegen.md"
    template_path = root / "04-templates/slide-prompt.md"
    compiler_blocks = _prompt_blocks(compiler_path.read_text(encoding="utf-8"))
    template_blocks = _prompt_blocks(template_path.read_text(encoding="utf-8"))
    expected_order = list(PROMPT_SECTIONS)
    if len(compiler_blocks) != 1 or [row[0] for row in compiler_blocks[0]] != expected_order:
        fail("Prompt compiler phải có đúng bảy section theo thứ tự canonical")
    if len(template_blocks) != 1 or [row[0] for row in template_blocks[0]] != expected_order:
        fail("Template slide prompt phải có đúng bảy section theo thứ tự canonical")
    elif any(body for _, body in template_blocks[0]):
        fail("Template slide prompt phải để trống bảy trường để người dùng điền")
    for path in active_files:
        relative = path.relative_to(root).as_posix()
        if path.suffix.lower() != ".md" or relative in {
            "03-workflow/03-prompt-and-imagegen.md",
            "04-templates/slide-prompt.md",
        }:
            continue
        text = path.read_text(encoding="utf-8")
        for block in _prompt_blocks(text):
            if [row[0] for row in block] != expected_order:
                fail(f"Prompt trong {relative} sai thứ tự/bộ bảy section")
                continue
            stats["generation_ready_prompts"] += 1
            bodies = [body for _, body in block]
            if any(not body for body in bodies) or PROMPT_PLACEHOLDER.search("\n".join(bodies)):
                fail(f"Generation-ready prompt còn placeholder: {relative}")

    try:
        layout_registry = load_json(
            root / "02-references/layouts/archetypes/registry.json"
        )
        infographic_registry = load_json(
            root / "02-references/layouts/infographics/registry.json"
        )
        if not isinstance(layout_registry, list) or not isinstance(infographic_registry, list):
            raise ValueError("Registry phải là JSON array")
        layout_ids = [item["id"] for item in layout_registry]
        infographic_ids = [item["id"] for item in infographic_registry]
        expected_layouts = {f"L{index:02d}" for index in range(1, 49)}
        expected_infographics = {f"I{index:02d}" for index in range(1, 13)}
        if len(layout_ids) != len(set(layout_ids)) or set(layout_ids) != expected_layouts:
            fail("Registry layout phải chứa duy nhất L01–L48")
        if len(infographic_ids) != len(set(infographic_ids)) or set(infographic_ids) != expected_infographics:
            fail("Registry infographic phải chứa duy nhất I01–I12")
        stats["layouts"] = len(layout_registry)
        stats["infographics"] = len(infographic_registry)
        all_entries = layout_registry + infographic_registry
        by_id = {item["id"]: item for item in all_entries}
        for entry in all_entries:
            identifier = entry["id"]
            resolved_paths: dict[str, tuple[str, Path]] = {}
            for key in ("spec_path", "preview_png", "preview_svg"):
                relative = entry.get(key)
                if not isinstance(relative, str):
                    fail(f"Registry {identifier} thiếu payload path {key}: {relative}")
                    continue
                candidate = (root / relative).resolve()
                try:
                    normalized = candidate.relative_to(root).as_posix()
                except ValueError:
                    fail(f"Registry {identifier} path thoát package {key}: {relative}")
                    continue
                if normalized not in relative_files:
                    fail(f"Registry {identifier} path ngoài explicit payload {key}: {relative}")
                    continue
                resolved_paths[key] = (normalized, candidate)
            if len(resolved_paths) != 3:
                continue
            spec_relative, _ = resolved_paths["spec_path"]
            png_relative, png_path = resolved_paths["preview_png"]
            svg_relative, svg_path = resolved_paths["preview_svg"]
            if entry.get("file") != Path(spec_relative).name:
                fail(f"Registry file/spec_path không khớp: {identifier}")
            if png_path.is_file():
                try:
                    width, height = _png_size(png_path)
                    stats["preview_png"] += 1
                    if width * 9 != height * 16:
                        fail(f"PNG không 16:9: {png_relative} {width}x{height}")
                except Exception as exc:
                    fail(f"PNG không hợp lệ {png_relative}: {exc}")
            if svg_path.is_file():
                try:
                    width, height = _svg_size(svg_path)
                    stats["preview_svg"] += 1
                    if abs(width * 9 - height * 16) > 0.001:
                        fail(f"SVG không 16:9: {svg_relative}")
                except Exception as exc:
                    fail(f"SVG không hợp lệ {svg_relative}: {exc}")
            if any(base not in expected_layouts for base in entry.get("base_layouts", [])):
                fail(f"Mã nền không tồn tại: {identifier}")
        layout_specs = {
            path.stem.split("_", 1)[0]
            for path in (root / "02-references/layouts/archetypes").glob("L*.md")
        }
        infographic_specs = {
            path.stem.split("_", 1)[0]
            for path in (root / "02-references/layouts/infographics").glob("I*.md")
        }
        if layout_specs != expected_layouts:
            fail("Tập đặc tả layout không đúng L01–L48")
        if infographic_specs != expected_infographics:
            fail("Tập đặc tả infographic không đúng I01–I12")

        groups = load_json(root / "02-references/layouts/taxonomy/groups.json")
        members = [member for group in groups for member in group["members"]]
        all_ids = expected_layouts | expected_infographics
        if len(groups) != 10 or any(len(group["members"]) != 6 for group in groups):
            fail("Bảng nhóm cần 10 bảng x 6 mẫu")
        if len(members) != len(set(members)) or set(members) != all_ids:
            fail("Nhóm taxonomy thiếu hoặc trùng mã L/I")
        for group in groups:
            preview = group.get("preview")
            if not isinstance(preview, str) or preview not in relative_files:
                fail(f"Thiếu group preview: {group.get('id')}")
            for identifier in group["members"]:
                if identifier in by_id and by_id[identifier].get("home_group") != group["id"]:
                    fail(f"home_group không khớp: {identifier}")

        index_text = (root / "02-references/INDEX.md").read_text(encoding="utf-8")
        index_targets = set()
        for target in _markdown_targets(index_text):
            parsed = urlsplit(target.strip().split(' "', 1)[0].strip("<>"))
            if parsed.path:
                destination = (
                    (root / "02-references" / unquote(parsed.path)).resolve()
                    .relative_to(root)
                    .as_posix()
                )
                index_targets.add(destination)
        for entry in all_entries:
            for key in ("spec_path", "preview_png"):
                if entry[key] not in index_targets:
                    fail(f"Reference INDEX thiếu link {key} cho {entry['id']}")

        sample_registry = load_json(
            root / "02-references/images/user-infographics/registry.json"
        )
        for item in sample_registry:
            declared_sample = item.get("path")
            if not isinstance(declared_sample, str):
                fail(f"Thiếu ảnh mẫu full-size: {item['id']}")
                continue
            sample_path = (root / declared_sample).resolve()
            try:
                normalized_sample = sample_path.relative_to(root).as_posix()
            except ValueError:
                fail(f"Ảnh mẫu thoát package: {item['id']} → {declared_sample}")
                continue
            if normalized_sample not in relative_files or not sample_path.is_file():
                fail(f"Thiếu ảnh mẫu full-size: {item['id']}")
                continue
            if sha256(sample_path) != item["sha256"]:
                fail(f"Ảnh mẫu full-size đã đổi byte: {item['id']}")
            if normalized_sample not in index_targets:
                fail(f"Reference INDEX thiếu link ảnh mẫu: {item['id']}")
            stats["full_size_samples"] += 1
        reference_images = sorted(
            (root / "02-references/images/reference-set").glob("*.png")
        )
        reference_readme = root / "02-references/images/reference-set/README.md"
        reference_targets = {
            (
                (reference_readme.parent / unquote(urlsplit(target).path))
                .resolve()
                .relative_to(root)
                .as_posix()
            )
            for target in _markdown_targets(reference_readme.read_text(encoding="utf-8"))
            if urlsplit(target).path
        }
        for image in reference_images:
            relative = image.relative_to(root).as_posix()
            if relative not in reference_targets:
                fail(f"Reference-set README thiếu link ảnh full-size: {relative}")
            stats["full_size_samples"] += 1
    except Exception as exc:
        fail("Không đọc được registry: " + str(exc))

    manifest_path = root / "manifest.json"
    manifest_checked = False
    if manifest_path.exists():
        manifest_checked = True
        try:
            manifest = load_json(manifest_path)
            items = manifest["files"]
            declared = [item["path"] for item in items]
            expected = [path.relative_to(root).as_posix() for path in files]
            if declared != expected or len(declared) != len(set(declared)):
                fail("Manifest không khớp tập explicit payload có thứ tự")
            for item in items:
                path = root / item["path"]
                if (
                    not path.is_file()
                    or path.stat().st_size != item["bytes"]
                    or sha256(path) != item["sha256"]
                ):
                    fail("Manifest hash sai: " + item["path"])
        except Exception as exc:
            fail("Lỗi manifest: " + str(exc))
    elif require_manifest:
        fail("Thiếu manifest.json")

    governance = [
        name for name in ("AGENTS.md", "CLAUDE.md", "GEMINI.md") if (root / name).exists()
    ]
    if governance:
        warnings.append(
            "Governance repository-only được loại khỏi install payload và được "
            "kiểm riêng tại repository root: " + ", ".join(governance)
        )
    return {
        "status": "PASS" if not errors else "FAIL",
        "scope": "Active package and explicit payload; not host runtime or model behavior",
        "stats": stats,
        "errors": errors,
        "warnings": warnings,
        "manifest_checked": manifest_checked,
    }


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "root",
        nargs="?",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--require-manifest", action="store_true")
    args = parser.parse_args(argv)
    result = check(args.root, args.require_manifest)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

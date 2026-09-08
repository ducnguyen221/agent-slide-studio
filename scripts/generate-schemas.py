from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "src"))

from presentation_studio.models import (
    AssetManifest,
    BackendCapabilities,
    BuildInput,
    BuildResult,
    CLIResult,
    DeckSpec,
    ProcessResult,
    Profile,
    ProfileLock,
    ProjectConfig,
    QAReport,
    RenderResult,
    TemplateDraft,
    TemplatePack,
)


SCHEMA_MODELS = (
    ProjectConfig,
    DeckSpec,
    Profile,
    ProfileLock,
    TemplateDraft,
    TemplatePack,
    AssetManifest,
    BackendCapabilities,
    BuildInput,
    ProcessResult,
    BuildResult,
    RenderResult,
    QAReport,
    CLIResult,
)


def _write_atomic(path: Path, content: str) -> None:
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            prefix=f".{path.name}.",
            suffix=".tmp",
            dir=path.parent,
            delete=False,
        ) as stream:
            temporary = Path(stream.name)
            stream.write(content)
        temporary.replace(path)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main() -> None:
    root = ROOT / "schemas"
    root.mkdir(exist_ok=True)
    expected = set()
    for model in SCHEMA_MODELS:
        path = root / f"{model.__name__}.schema.json"
        expected.add(path.name)
        content = json.dumps(
            model.model_json_schema(), ensure_ascii=False, sort_keys=True, indent=2
        ) + "\n"
        _write_atomic(path, content)
    for stale in root.glob("*.schema.json"):
        if stale.name not in expected:
            stale.unlink()


if __name__ == "__main__":
    main()

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from presentation_studio.models.visual import VisualAssetBrief


def fixture_json(name: str) -> dict:
    root = Path(__file__).parent / "fixtures" / "visual" / "core"
    return json.loads((root / f"{name}.json").read_text(encoding="utf-8"))


def load_brief(mode: str = "IMAGE") -> VisualAssetBrief:
    from presentation_studio.models.visual import VisualAssetBrief

    fixture_name = {
        "IMAGE": "brief-image",
        "HTML-RECONSTRUCTION": "brief-html",
    }.get(mode)
    if fixture_name is None:
        raise ValueError(f"unsupported visual mode: {mode}")
    return VisualAssetBrief.model_validate(fixture_json(fixture_name))

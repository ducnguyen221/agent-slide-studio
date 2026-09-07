from __future__ import annotations
import json
from pathlib import Path
from presentation_studio.models import AssetManifest, DeckSpec, Profile, ProjectConfig, QAReport, TemplatePack
def main():
    root=Path(__file__).parents[1] / "schemas"; root.mkdir(exist_ok=True)
    for model in (ProjectConfig, DeckSpec, Profile, TemplatePack, AssetManifest, QAReport):
        (root / f"{model.__name__}.schema.json").write_text(json.dumps(model.model_json_schema(), ensure_ascii=False, sort_keys=True, indent=2)+"\n", encoding="utf-8")
if __name__ == "__main__": main()

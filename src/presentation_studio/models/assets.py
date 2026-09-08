from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator

from .common import Identifier, RelativePath, SHA256, SchemaVersion, StrictModel


class Generation(StrictModel):
    provider: Identifier
    model_id: str
    model_revision: str | None = None
    prompt_hash: SHA256
    seed: int | None = None
    deterministic: bool
    style_profile_hash: SHA256
    request_id: str
    actual_cost: float | None = Field(default=None, ge=0)


class RightsMetadata(StrictModel):
    license: str | None = None
    attribution: str | None = None
    redistributable: bool = False
    source_url: str | None = None


class Asset(StrictModel):
    id: Identifier
    relative_path: RelativePath
    sha256: SHA256
    media_type: str
    width: int | None = Field(default=None, gt=0)
    height: int | None = Field(default=None, gt=0)
    role: Identifier
    alt_text: str
    source_kind: Literal["user", "generated", "public", "builtin"]
    source_ref: str | None = None
    rights: RightsMetadata = Field(default_factory=RightsMetadata)
    generation: Generation | None = None

    @model_validator(mode="after")
    def generated_assets_have_generation_metadata(self) -> Asset:
        if self.source_kind == "generated" and self.generation is None:
            raise ValueError("generated assets require generation metadata")
        return self


class AssetManifest(StrictModel):
    schema_version: SchemaVersion = "1.0"
    assets: list[Asset] = Field(default_factory=list)

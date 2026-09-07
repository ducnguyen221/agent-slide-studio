from typing import Any, Literal
from pydantic import Field
from .common import Identifier, SchemaVersion, StrictModel
class Generation(StrictModel):
    provider: str
    model_id: str
    model_revision: str | None = None
    prompt_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    seed: int | None = None
    style_profile_hash: str
    request_id: str
    actual_cost: float | None = Field(default=None, ge=0)
class Asset(StrictModel):
    id: Identifier
    relative_path: str
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    media_type: str
    width: int | None = Field(default=None, gt=0)
    height: int | None = Field(default=None, gt=0)
    role: str
    alt_text: str
    source_kind: Literal["user", "generated", "public", "builtin"]
    source_ref: str | None = None
    rights: dict[str, Any] = Field(default_factory=dict)
    generation: Generation | None = None
class AssetManifest(StrictModel):
    schema_version: SchemaVersion = "1.0"
    assets: list[Asset] = Field(default_factory=list)


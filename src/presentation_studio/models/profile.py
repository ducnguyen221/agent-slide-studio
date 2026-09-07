from typing import Any
from pydantic import Field, model_validator
from .common import EvidenceRef, Identifier, ObservedValue, SchemaVersion, StrictModel
class Profile(StrictModel):
    schema_version: SchemaVersion = "1.0"
    id: Identifier
    version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    display_name: str
    description: str
    palette_by_role: dict[str, ObservedValue] = Field(default_factory=dict)
    typography: dict[str, ObservedValue] = Field(default_factory=dict)
    spacing: dict[str, Any] = Field(default_factory=dict)
    composition: dict[str, Any] = Field(default_factory=dict)
    image_style: dict[str, Any] = Field(default_factory=dict)
    motion: dict[str, Any] = Field(default_factory=dict)
    constraints: dict[str, Any] = Field(default_factory=dict)
    provenance: list[EvidenceRef] = Field(default_factory=list)
    @model_validator(mode="after")
    def inferred_values_have_evidence(self):
        if any(v.origin == "inferred" and not v.evidence for v in [*self.palette_by_role.values(), *self.typography.values()]):
            raise ValueError("inferred profile values require evidence")
        return self
class ProfileLock(StrictModel):
    ref: str
    resolved_id: Identifier
    version: str
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    source: str


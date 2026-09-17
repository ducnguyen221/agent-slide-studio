from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import Field, model_validator

from .common import (
    EvidenceRef,
    Identifier,
    ObservedValue,
    SHA256,
    SchemaVersion,
    SemVer,
    StrictModel,
)


class Profile(StrictModel):
    schema_version: SchemaVersion = "1.0"
    id: Identifier
    version: SemVer
    display_name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    palette_by_role: dict[str, ObservedValue] = Field(default_factory=dict)
    typography: dict[str, ObservedValue] = Field(default_factory=dict)
    spacing: dict[str, ObservedValue] = Field(default_factory=dict)
    composition: dict[str, ObservedValue] = Field(default_factory=dict)
    image_style: dict[str, ObservedValue] = Field(default_factory=dict)
    motion: dict[str, ObservedValue] = Field(default_factory=dict)
    constraints: dict[str, ObservedValue] = Field(default_factory=dict)
    provenance: list[EvidenceRef] = Field(default_factory=list)

    @model_validator(mode="after")
    def inferred_values_have_evidence(self) -> Profile:
        sections = (
            self.palette_by_role,
            self.typography,
            self.spacing,
            self.composition,
            self.image_style,
            self.motion,
            self.constraints,
        )
        if any(
            value.origin == "inferred" and not value.evidence
            for section in sections
            for value in section.values()
        ):
            raise ValueError("inferred profile values require evidence")
        return self


class ProfileLock(StrictModel):
    resolved_ref: str
    source_scope: Literal["builtin", "user", "project"]
    version: SemVer
    sha256: SHA256
    applied_overrides: dict[str, ObservedValue] = Field(default_factory=dict)
    font_resolution: dict[str, str] = Field(default_factory=dict)
    created_at: datetime

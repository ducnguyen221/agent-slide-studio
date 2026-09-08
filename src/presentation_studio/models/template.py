from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator

from .common import EvidenceRef, Identifier, RelativePath, SHA256, SchemaVersion, SemVer, StrictModel
from .deck import Canvas


class CapacityHint(StrictModel):
    min_characters: int | None = Field(default=None, ge=0)
    max_characters: int | None = Field(default=None, ge=1)
    max_lines: int | None = Field(default=None, ge=1)


class TemplateSlot(StrictModel):
    id: Identifier
    kind: Identifier
    required: bool = False
    min_items: int | None = Field(default=None, ge=0)
    max_items: int | None = Field(default=None, ge=1)
    capacity_hint: CapacityHint | None = None
    placement_ref: str | None = None

    @model_validator(mode="after")
    def item_range_is_valid(self) -> TemplateSlot:
        if (
            self.min_items is not None
            and self.max_items is not None
            and self.min_items > self.max_items
        ):
            raise ValueError("min_items cannot exceed max_items")
        return self


class RepeatGroup(StrictModel):
    id: Identifier
    members: list[Identifier] = Field(min_length=1)
    min_items: int = Field(default=0, ge=0)
    max_items: int = Field(ge=1)
    reflow_policy: Literal["fixed", "compact", "wrap", "switch-layout"]

    @model_validator(mode="after")
    def item_range_is_valid(self) -> RepeatGroup:
        if self.min_items > self.max_items:
            raise ValueError("min_items cannot exceed max_items")
        return self


class LockedElement(StrictModel):
    id: Identifier
    reason: str


class TemplateConstraints(StrictModel):
    min_font_size: float | None = Field(default=None, gt=0)
    max_slides: int | None = Field(default=None, ge=1)


class TemplateCertification(StrictModel):
    status: Literal["candidate", "certified", "rejected"] = "candidate"
    rights_verified: bool = False
    render_evidence: list[EvidenceRef] = Field(default_factory=list)


class TemplatePack(StrictModel):
    schema_version: SchemaVersion = "1.0"
    id: Identifier
    version: SemVer
    backends: list[Identifier] = Field(min_length=1)
    canvas: Canvas
    files: list[RelativePath] = Field(min_length=1)
    slots: list[TemplateSlot]
    repeat_groups: list[RepeatGroup] = Field(default_factory=list)
    locked_elements: list[LockedElement] = Field(default_factory=list)
    constraints: TemplateConstraints = Field(default_factory=TemplateConstraints)
    preview: RelativePath | None = None
    provenance: list[EvidenceRef] = Field(default_factory=list)
    certification: TemplateCertification = Field(default_factory=TemplateCertification)


class StructureObservation(StrictModel):
    kind: Identifier
    description: str
    evidence: list[EvidenceRef] = Field(default_factory=list)


class TemplateDraft(StrictModel):
    schema_version: SchemaVersion = "1.0"
    source_ref: str
    source_sha256: SHA256
    extracted_structure: list[StructureObservation] = Field(default_factory=list)
    observations: list[StructureObservation] = Field(default_factory=list)
    uncertain: list[StructureObservation] = Field(default_factory=list)
    unsupported: list[StructureObservation] = Field(default_factory=list)
    previews: list[RelativePath] = Field(default_factory=list)

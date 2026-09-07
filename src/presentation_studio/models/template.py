from typing import Any
from pydantic import Field
from .common import EvidenceRef, Identifier, SchemaVersion, StrictModel
from .deck import Canvas
class TemplateSlot(StrictModel):
    id: Identifier
    kind: Identifier
    required: bool = False
    capacity: int | None = Field(default=None, ge=1)
class TemplatePack(StrictModel):
    schema_version: SchemaVersion = "1.0"
    id: Identifier
    version: str
    backends: list[Identifier] = Field(min_length=1)
    canvas: Canvas
    files: list[str]
    slots: list[TemplateSlot]
    repeat_groups: list[dict[str, Any]] = Field(default_factory=list)
    locked_elements: list[str] = Field(default_factory=list)
    constraints: dict[str, Any] = Field(default_factory=dict)
    preview: str | None = None
    provenance: list[EvidenceRef] = Field(default_factory=list)
    certification: dict[str, Any] = Field(default_factory=dict)
TemplateDraft = TemplatePack


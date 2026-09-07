from typing import Any, Literal
from pydantic import Field, model_validator
from .common import Identifier, SchemaVersion, StrictModel
class Canvas(StrictModel):
    width: float = Field(default=13.333, gt=0)
    height: float = Field(default=7.5, gt=0)
    unit: Literal["inch", "px"] = "inch"
class SourceRef(StrictModel):
    id: Identifier
    uri: str
    title: str | None = None
class SlideSpec(StrictModel):
    slide_id: Identifier
    title: str = Field(min_length=1)
    layout: Identifier
    subtitle: str | None = None
    body: list[str] = Field(default_factory=list)
    speaker_notes: str | None = None
    source_ids: list[Identifier] = Field(default_factory=list)
    content: dict[str, Any] = Field(default_factory=dict)
class DeckSpec(StrictModel):
    schema_version: SchemaVersion = "1.0"
    title: str = Field(min_length=1)
    audience: str = Field(min_length=1)
    purpose: str = Field(min_length=1)
    canvas: Canvas = Field(default_factory=Canvas)
    slides: list[SlideSpec] = Field(min_length=1)
    sources: list[SourceRef] = Field(default_factory=list)
    @model_validator(mode="after")
    def unique_references(self):
        ids = [s.slide_id for s in self.slides]
        if len(ids) != len(set(ids)): raise ValueError("slide_id must be unique")
        known = {s.id for s in self.sources}
        missing = {r for s in self.slides for r in s.source_ids if r not in known}
        if missing: raise ValueError(f"unknown source ids: {sorted(missing)}")
        return self


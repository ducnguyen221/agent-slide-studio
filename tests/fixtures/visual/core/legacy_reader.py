from __future__ import annotations

from pathlib import PurePosixPath, PureWindowsPath
from typing import Annotated, Literal

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, model_validator


SchemaVersion = Literal["1.0"]
Identifier = Annotated[
    str, Field(pattern=r"^[a-z0-9][a-z0-9-]{0,63}$", min_length=1, max_length=64)
]
SHA256 = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]


def _relative_path(value: object) -> object:
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        raise ValueError("path must be a normalized relative POSIX path")
    path = PurePosixPath(value)
    if (
        path.is_absolute()
        or ".." in path.parts
        or PureWindowsPath(value).is_absolute()
        or path.as_posix() != value
    ):
        raise ValueError("path must be relative and traversal-free")
    return value


RelativePath = Annotated[str, BeforeValidator(_relative_path)]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class Canvas(StrictModel):
    ratio: Literal["16:9", "4:3", "custom"] = "16:9"
    width: float | None = Field(default=None, gt=0)
    height: float | None = Field(default=None, gt=0)
    unit: Literal["inch", "px"] = "inch"

    @model_validator(mode="after")
    def custom_size_is_complete(self) -> Canvas:
        if self.ratio == "custom" and (self.width is None or self.height is None):
            raise ValueError("custom canvas requires width and height")
        if self.ratio != "custom" and (self.width is not None or self.height is not None):
            raise ValueError("width and height are only valid for custom canvas")
        return self


class SourceRef(StrictModel):
    id: Identifier
    kind: Identifier = "document"
    title: str = Field(min_length=1)
    uri: str | None = None
    sha256: SHA256 | None = None


class Learning(StrictModel):
    objective_ids: list[Identifier] = Field(default_factory=list)
    bloom_verb: str | None = None


class TextContent(StrictModel):
    text: str = ""
    label: str | None = None
    items: list[str] = Field(default_factory=list)


class ImageContent(StrictModel):
    asset_ref: Identifier | None = None
    uri: RelativePath | None = None

    @model_validator(mode="after")
    def has_source(self) -> ImageContent:
        if self.asset_ref is None and self.uri is None:
            raise ValueError("image content requires asset_ref or uri")
        return self


class ChartDatum(StrictModel):
    label: str
    value: float


class ChartContent(StrictModel):
    chart_type: Identifier
    data: list[ChartDatum] = Field(min_length=1)
    unit: str | None = None
    source_ref: Identifier | None = None


class TableContent(StrictModel):
    columns: list[str] = Field(min_length=1)
    rows: list[list[str | float | int | bool | None]] = Field(default_factory=list)

    @model_validator(mode="after")
    def rows_match_columns(self) -> TableContent:
        if any(len(row) != len(self.columns) for row in self.rows):
            raise ValueError("table rows must match column count")
        return self


class ProcessStep(StrictModel):
    id: Identifier
    title: str
    description: str | None = None


class ProcessContent(StrictModel):
    steps: list[ProcessStep] = Field(min_length=1)
    connector: Literal["sequence", "cycle", "branch"] = "sequence"


class TimelineItem(StrictModel):
    time_label: str
    title: str
    description: str | None = None


class TimelineContent(StrictModel):
    items: list[TimelineItem] = Field(min_length=1)


class QuoteContent(StrictModel):
    quote: str
    attribution: str | None = None


class CodeContent(StrictModel):
    code: str
    language: Identifier | None = None


class ElementBase(StrictModel):
    element_id: Identifier
    role: Identifier | None = None
    alt_text: str | None = None


class TextElement(ElementBase):
    kind: Literal["text"]
    content: str | TextContent


class ImageElement(ElementBase):
    kind: Literal["image"]
    content: ImageContent
    alt_text: str = Field(min_length=1)


class ChartElement(ElementBase):
    kind: Literal["chart"]
    content: ChartContent


class TableElement(ElementBase):
    kind: Literal["table"]
    content: TableContent


class ProcessElement(ElementBase):
    kind: Literal["process"]
    content: ProcessContent


class TimelineElement(ElementBase):
    kind: Literal["timeline"]
    content: TimelineContent


class QuoteElement(ElementBase):
    kind: Literal["quote"]
    content: QuoteContent


class CodeElement(ElementBase):
    kind: Literal["code"]
    content: CodeContent


SlideElement = Annotated[
    TextElement
    | ImageElement
    | ChartElement
    | TableElement
    | ProcessElement
    | TimelineElement
    | QuoteElement
    | CodeElement,
    Field(discriminator="kind"),
]


class SlideSpec(StrictModel):
    slide_id: Identifier
    title: str = Field(min_length=1)
    message: str | None = None
    layout_ref: str = Field(min_length=1)
    elements: list[SlideElement] = Field(default_factory=list)
    notes: str | None = None
    source_refs: list[Identifier] = Field(default_factory=list)
    learning: Learning | None = None
    html_ref: RelativePath | None = None


class DeckSpec(StrictModel):
    schema_version: SchemaVersion = "1.0"
    title: str = Field(min_length=1)
    audience: str = Field(min_length=1)
    purpose: str = Field(min_length=1)
    canvas: Canvas = Field(default_factory=Canvas)
    slides: list[SlideSpec] = Field(min_length=1)
    sources: list[SourceRef] = Field(default_factory=list)

    @model_validator(mode="after")
    def unique_references(self) -> DeckSpec:
        slide_ids = [slide.slide_id for slide in self.slides]
        if len(slide_ids) != len(set(slide_ids)):
            raise ValueError("slide_id must be unique")
        source_ids = [source.id for source in self.sources]
        if len(source_ids) != len(set(source_ids)):
            raise ValueError("source id must be unique")
        known = set(source_ids)
        missing = {
            ref for slide in self.slides for ref in slide.source_refs if ref not in known
        }
        if missing:
            raise ValueError(f"unknown source ids: {sorted(missing)}")
        return self

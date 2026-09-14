from __future__ import annotations

from decimal import Decimal, InvalidOperation
import re
from typing import Annotated, Literal, TypeAlias
import unicodedata

from pydantic import BeforeValidator, ConfigDict, Field, model_validator

from .common import EvidenceRef, Identifier, RelativePath, SHA256, SemVer, StrictModel
from .profile import ProfileLock


def _normalize_nfc(value: object) -> object:
    if isinstance(value, str):
        return unicodedata.normalize("NFC", value)
    return value


Text4000 = Annotated[
    str, BeforeValidator(_normalize_nfc), Field(max_length=4000)
]
NonEmptyText4000 = Annotated[
    str, BeforeValidator(_normalize_nfc), Field(min_length=1, max_length=4000)
]
Text1000 = Annotated[
    str, BeforeValidator(_normalize_nfc), Field(max_length=1000)
]
NonEmptyText1000 = Annotated[
    str, BeforeValidator(_normalize_nfc), Field(min_length=1, max_length=1000)
]
ColorHex = Annotated[str, Field(pattern=r"^#[0-9A-Fa-f]{6}$")]
LanguageTag = Annotated[
    str,
    Field(
        min_length=2,
        max_length=35,
        pattern=r"^[A-Za-z]{2,8}(?:-[A-Za-z0-9]{1,8})*$",
    ),
]
BudgetAmount = Annotated[
    str, Field(pattern=r"^(?:0|[1-9]\d{0,11})(?:\.\d{1,6})?$")
]
Currency = Annotated[str, Field(pattern=r"^[A-Z]{3}$")]
UnitFraction = Annotated[float, Field(ge=0, le=1)]


class _VisualModel(StrictModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True, strict=True)


NonChartField = Literal[
    "slide-title",
    "slide-message",
    "deck-audience",
    "deck-purpose",
    "text-content",
    "text-label",
    "text-item",
    "process-title",
    "process-description",
    "quote-text",
    "code-text",
    "table-cell",
    "image-content",
    "image-alt",
    "semantic-node",
    "slide-notes",
]
ChartField = Literal[
    "chart-label", "chart-value", "chart-unit", "display-unit"
]


class ContentBinding(_VisualModel):
    slide_id: Identifier
    element_id: Identifier | None = None
    field: NonChartField
    item_id: Identifier | None = None
    item_index: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def valid_binding_shape(self) -> ContentBinding:
        field = self.field
        no_element = {
            "slide-title",
            "slide-message",
            "deck-audience",
            "deck-purpose",
            "slide-notes",
        }
        element_scalar = {
            "text-content",
            "text-label",
            "quote-text",
            "code-text",
            "image-content",
            "image-alt",
        }
        if field in no_element:
            if (
                self.element_id is not None
                or self.item_id is not None
                or self.item_index is not None
            ):
                raise ValueError(f"{field} does not accept element or item selectors")
        elif field in element_scalar:
            if self.element_id is None or self.item_id is not None or self.item_index is not None:
                raise ValueError(f"{field} requires only element_id")
        elif field == "text-item":
            if self.element_id is None or self.item_index is None or self.item_id is not None:
                raise ValueError("text-item requires element_id and item_index")
        elif field in {"process-title", "process-description"}:
            if self.element_id is None or self.item_id is None or self.item_index is not None:
                raise ValueError(f"{field} requires element_id and item_id")
        elif field == "table-cell":
            if (
                self.element_id is None
                or self.item_id is None
                or self.item_index is None
                or re.fullmatch(r"col-\d+", self.item_id) is None
            ):
                raise ValueError(
                    "table-cell requires element_id, row item_index, and col-N item_id"
                )
        elif field == "semantic-node":
            if self.element_id is not None or self.item_id is None or self.item_index is not None:
                raise ValueError("semantic-node requires only item_id")
        return self


class ChartBinding(ContentBinding):
    element_id: Identifier
    field: ChartField

    @model_validator(mode="after")
    def valid_chart_shape(self) -> ChartBinding:
        if self.field in {"chart-label", "chart-value"}:
            if self.item_index is None or self.item_id is not None:
                raise ValueError(
                    f"{self.field} requires item_index and forbids item_id"
                )
        elif self.item_index is not None or self.item_id is not None:
            raise ValueError(
                f"{self.field} forbids item_index and item_id"
            )
        return self


AnyContentBinding: TypeAlias = Annotated[
    ContentBinding | ChartBinding, Field(discriminator="field")
]


class Fact(_VisualModel):
    id: Identifier
    binding: AnyContentBinding
    value_type: Literal["string", "decimal"]
    value: NonEmptyText1000
    source_ref: Identifier

    @model_validator(mode="after")
    def value_matches_binding(self) -> Fact:
        field = self.binding.field
        if field == "display-unit":
            raise ValueError("display-unit cannot own a duplicate unit fact")
        if field == "chart-value" and self.value_type != "decimal":
            raise ValueError("chart-value facts must use decimal values")
        if field in {"chart-label", "chart-unit"} and self.value_type != "string":
            raise ValueError(f"{field} facts must use string values")
        if self.value_type == "decimal":
            if re.fullmatch(r"-?(?:0|[1-9]\d*)(?:\.\d+)?", self.value) is None:
                raise ValueError("decimal fact value must be canonical and ungrouped")
            try:
                value = Decimal(self.value)
            except InvalidOperation as error:
                raise ValueError("decimal fact value is invalid") from error
            if not value.is_finite():
                raise ValueError("decimal fact value must be finite")
        return self


class Box(_VisualModel):
    x: UnitFraction
    y: UnitFraction
    width: Annotated[float, Field(gt=0, le=1)]
    height: Annotated[float, Field(gt=0, le=1)]

    @model_validator(mode="after")
    def stays_inside_canvas(self) -> Box:
        if self.x + self.width > 1 or self.y + self.height > 1:
            raise ValueError("box must stay within normalized canvas bounds")
        return self


VisualNodeKind = Literal[
    "title", "text", "group", "icon", "shape", "image", "data-label"
]


class SemanticNode(_VisualModel):
    id: Identifier
    kind: VisualNodeKind
    content_binding: AnyContentBinding
    parent_id: Identifier | None = None
    visible: bool
    required: bool
    semantic_role: Annotated[
        str, BeforeValidator(_normalize_nfc), Field(min_length=1, max_length=128)
    ]
    facts: list[Fact] = Field(default_factory=list)
    asset_ref: Identifier | None = None


class VisualNode(SemanticNode):
    text: Text4000 | None = None
    preferred_box: Box | None = None


class VisualRelation(_VisualModel):
    id: Identifier
    from_id: Identifier
    to_id: Identifier
    kind: Literal["sequence", "branch", "cycle", "contains", "compares", "associates"]
    label: Text1000 | None = None
    required: bool


def _binding_pointer(binding: AnyContentBinding) -> tuple[object, ...]:
    field = "chart-unit" if binding.field == "display-unit" else binding.field
    return (
        binding.slide_id,
        binding.element_id,
        field,
        binding.item_id,
        binding.item_index,
    )


def _validate_graph(
    nodes: list[SemanticNode],
    relations: list[VisualRelation],
    reading_order: list[Identifier],
) -> None:
    node_ids = [node.id for node in nodes]
    if len(node_ids) != len(set(node_ids)):
        raise ValueError("visual node ids must be unique")
    known_nodes = set(node_ids)

    relation_ids = [relation.id for relation in relations]
    if len(relation_ids) != len(set(relation_ids)):
        raise ValueError("visual relation ids must be unique")
    if any(
        relation.from_id not in known_nodes or relation.to_id not in known_nodes
        for relation in relations
    ):
        raise ValueError("visual relation endpoint is unknown")

    if len(reading_order) != len(set(reading_order)):
        raise ValueError("reading_order cannot contain duplicates")
    visible_ids = {node.id for node in nodes if node.visible}
    if set(reading_order) != visible_ids or len(reading_order) != len(visible_ids):
        raise ValueError("reading_order must contain every visible node exactly once")

    parent_edges: set[tuple[Identifier, Identifier]] = set()
    parent_by_node: dict[Identifier, Identifier] = {}
    for node in nodes:
        if node.parent_id is not None:
            if node.parent_id not in known_nodes or node.parent_id == node.id:
                raise ValueError("parent_id must reference a different known node")
            parent_edges.add((node.parent_id, node.id))
            parent_by_node[node.id] = node.parent_id
        if node.content_binding.field == "semantic-node":
            if node.kind not in {"group", "shape"}:
                raise ValueError("semantic-node binding is reserved for group/shape decoration")
            if node.content_binding.item_id != node.id:
                raise ValueError("semantic-node binding item_id must equal its node id")
        elif node.kind in {"group", "shape"}:
            raise ValueError("group/shape decoration requires semantic-node binding")

    contains_edges = {
        (relation.from_id, relation.to_id)
        for relation in relations
        if relation.kind == "contains"
    }
    if contains_edges != parent_edges:
        raise ValueError("contains relations must match parent_id exactly")

    for start in parent_by_node:
        seen: set[Identifier] = set()
        current = start
        while current in parent_by_node:
            if current in seen:
                raise ValueError("parent hierarchy cannot contain a cycle")
            seen.add(current)
            current = parent_by_node[current]

    facts = [fact for node in nodes for fact in node.facts]
    fact_ids = [fact.id for fact in facts]
    if len(fact_ids) != len(set(fact_ids)):
        raise ValueError("fact ids must be unique within a visual graph")
    pointers = [_binding_pointer(fact.binding) for fact in facts]
    if len(pointers) != len(set(pointers)):
        raise ValueError("each canonical scalar pointer can have only one fact owner")
    if any(
        fact.binding.slide_id != node.content_binding.slide_id
        for node in nodes
        for fact in node.facts
    ):
        raise ValueError("node facts must bind to the same slide as their owner")


class VisualSemantics(_VisualModel):
    nodes: list[SemanticNode] = Field(min_length=1, max_length=200)
    relations: list[VisualRelation] = Field(default_factory=list, max_length=400)
    reading_order: list[Identifier]

    @model_validator(mode="after")
    def graph_is_consistent(self) -> VisualSemantics:
        _validate_graph(self.nodes, self.relations, self.reading_order)
        return self


class NumberFormatter(_VisualModel):
    formatter_id: Literal["fixed-decimal"] = "fixed-decimal"
    version: SemVer = "1.0.0"
    locale: Literal["vi-VN", "en-US"]
    precision: int = Field(ge=0, le=12)
    rounding: Literal["reject-inexact", "half-even", "half-up"] = "reject-inexact"
    grouping: bool = False
    trim_trailing_zeros: bool = False
    approximation_marker: Literal["none", "prefix"] = "none"


class DeckBinding(_VisualModel):
    deck_ref: RelativePath
    deck_raw_sha256: SHA256
    slide_content_hash: SHA256
    projection_version: Literal["1.0"]


class SafeArea(_VisualModel):
    top: Annotated[float, Field(ge=0, le=0.25)]
    right: Annotated[float, Field(ge=0, le=0.25)]
    bottom: Annotated[float, Field(ge=0, le=0.25)]
    left: Annotated[float, Field(ge=0, le=0.25)]


class VisualCanvas(_VisualModel):
    width_px: int = Field(ge=64, le=8192)
    height_px: int = Field(ge=64, le=8192)
    safe_area: SafeArea
    background: ColorHex

    @model_validator(mode="after")
    def area_is_bounded(self) -> VisualCanvas:
        if self.width_px * self.height_px > 33_554_432:
            raise ValueError("canvas area exceeds 33,554,432 pixels")
        return self


class VisualReference(_VisualModel):
    asset_ref: Identifier
    sha256: SHA256
    role: Literal["composition", "style", "content", "locked-design"]
    inspection: Literal["measured", "inferred", "unverified"]
    evidence_refs: list[EvidenceRef] = Field(default_factory=list)
    locked_features: list[
        Literal[
            "content",
            "relations",
            "geometry",
            "palette",
            "typography",
            "decoration",
        ]
    ] = Field(default_factory=list)

    @model_validator(mode="after")
    def inspected_claims_have_evidence(self) -> VisualReference:
        if self.inspection in {"measured", "inferred"} and not self.evidence_refs:
            raise ValueError("measured and inferred references require evidence")
        if len(self.locked_features) != len(set(self.locked_features)):
            raise ValueError("locked_features must be unique")
        return self


class VisualStyle(_VisualModel):
    preset_id: Identifier | None = None
    archetype: Identifier
    density: Literal["sparse", "balanced", "dense"]
    palette_roles: dict[Identifier, ColorHex]
    font_roles: dict[Identifier, Annotated[str, Field(min_length=1)]]
    icon_family: Identifier | None = None
    constraints: list[NonEmptyText1000] = Field(default_factory=list, max_length=50)


class Editability(_VisualModel):
    required_node_ids: list[Identifier] = Field(default_factory=list)
    target: Literal["raster", "html-source", "pptx-native", "mixed"]
    allow_raster_decoration: bool


class Crop(_VisualModel):
    reference_asset_id: Identifier
    x: UnitFraction
    y: UnitFraction
    width: Annotated[float, Field(gt=0, le=1)]
    height: Annotated[float, Field(gt=0, le=1)]

    @model_validator(mode="after")
    def stays_inside_reference(self) -> Crop:
        if self.x + self.width > 1 or self.y + self.height > 1:
            raise ValueError("crop must stay within normalized reference bounds")
        return self


class Motion(_VisualModel):
    enabled: bool
    adapter: Literal["hyperframes"] | None = None
    duration_seconds: float | None = Field(default=None, gt=0, le=120)
    fps: int | None = Field(default=None, ge=1, le=60)


class VisualExecution(_VisualModel):
    network: Literal["offline", "provider-only"] = "offline"
    image_source: Literal["generate", "import", "cache-only"]
    import_asset_id: Identifier | None = None
    provider_id: Annotated[str, Field(min_length=1)] | None = None
    model_id: Annotated[str, Field(min_length=1)] | None = None
    max_provider_calls: int = Field(default=0, ge=0, le=6)
    accounting_mode: Literal["none", "host-quota", "monetary"]
    budget_amount: BudgetAmount | None = "0"
    currency: Currency | None = None
    timeout_seconds: int = Field(default=120, ge=1, le=600)
    reference_egress_allowed: bool = False
    grant_ref: RelativePath | None = None

    @model_validator(mode="after")
    def source_and_accounting_are_consistent(self) -> VisualExecution:
        if self.accounting_mode == "none":
            if self.image_source == "generate":
                raise ValueError("generation requires quota or monetary accounting")
            if self.currency is not None:
                raise ValueError("none accounting cannot declare currency")
        elif self.accounting_mode == "host-quota":
            if self.budget_amount is not None or self.currency is not None:
                raise ValueError("host-quota requires null amount and currency")
            if self.grant_ref is None:
                raise ValueError("host-quota requires an explicit grant_ref")
        elif self.budget_amount is None or self.currency is None:
            raise ValueError("monetary accounting requires amount and currency")

        if self.image_source == "generate":
            if (
                self.network != "provider-only"
                or self.import_asset_id is not None
                or self.provider_id is None
                or self.model_id is None
                or self.max_provider_calls < 1
                or self.grant_ref is None
            ):
                raise ValueError(
                    "generation requires provider-only network, provider/model, calls, and grant"
                )
            if (
                self.accounting_mode == "monetary"
                and self.budget_amount is not None
                and Decimal(self.budget_amount) == 0
            ):
                raise ValueError("zero budget always blocks generation")
        elif self.image_source == "import":
            if (
                self.import_asset_id is None
                or self.max_provider_calls != 0
                or self.provider_id is not None
                or self.model_id is not None
            ):
                raise ValueError("import requires one asset and forbids provider calls")
        elif (
            self.network != "offline"
            or self.import_asset_id is not None
            or self.max_provider_calls != 0
        ):
            raise ValueError("cache-only must remain offline and make no provider calls")
        return self


class Accessibility(_VisualModel):
    alt_text: NonEmptyText4000
    transcript: Annotated[
        str, BeforeValidator(_normalize_nfc), Field(max_length=20_000)
    ]
    notes: Annotated[
        str, BeforeValidator(_normalize_nfc), Field(max_length=20_000)
    ]


class FidelityTolerances(_VisualModel):
    box_tolerance_px: float | None = Field(default=None, ge=0, le=256)
    ssim_min: float | None = Field(default=None, ge=0, le=1)
    iou_min: float | None = Field(default=None, ge=0, le=1)
    delta_e_max: float | None = Field(default=None, ge=0, le=100)


class QAPolicy(_VisualModel):
    required_rule_ids: list[Identifier]
    max_repair_rounds: int = Field(default=2, ge=0, le=2)
    fidelity_tolerances: FidelityTolerances

    @model_validator(mode="after")
    def rules_are_unique(self) -> QAPolicy:
        if len(self.required_rule_ids) != len(set(self.required_rule_ids)):
            raise ValueError("required_rule_ids must be unique")
        return self


class Approval(_VisualModel):
    scope: Literal["brief", "reference", "design"]
    approved_content_hash: SHA256
    evidence: EvidenceRef


class VisualAssetBrief(_VisualModel):
    schema_version: Literal["1.0"]
    id: Identifier
    slide_id: Identifier
    deck_binding: DeckBinding
    revision: int = Field(ge=1)
    mode: Literal["IMAGE", "HTML-RECONSTRUCTION"]
    purpose: NonEmptyText4000
    audience: NonEmptyText4000
    message: Text4000 | None
    language: LanguageTag
    proper_names: list[Annotated[str, BeforeValidator(_normalize_nfc), Field(min_length=1)]]
    canvas: VisualCanvas
    text_policy: Literal["baked", "overlay", "none"]
    nodes: list[VisualNode] = Field(min_length=1, max_length=200)
    relations: list[VisualRelation] = Field(default_factory=list, max_length=400)
    reading_order: list[Identifier]
    references: list[VisualReference] = Field(default_factory=list, max_length=8)
    reconstruction_policy: Literal["faithful", "inspired-redesign"] | None
    style: VisualStyle
    number_formatters: dict[Identifier, NumberFormatter]
    profile_lock: ProfileLock
    editability: Editability
    fit_policy: Literal["reject", "contain", "crop-approved"] = "reject"
    crop: Crop | None
    motion: Motion
    execution: VisualExecution
    deliverables: list[Literal["png", "html-source", "pptx", "motion-video"]] = Field(
        min_length=1
    )
    accessibility: Accessibility
    qa_policy: QAPolicy
    approval: Approval | None

    @model_validator(mode="after")
    def nodes_and_relations_are_consistent(self) -> VisualAssetBrief:
        _validate_graph(self.nodes, self.relations, self.reading_order)
        if len(self.proper_names) != len(set(self.proper_names)):
            raise ValueError("proper_names must be unique")
        node_ids = {node.id for node in self.nodes}
        if any(
            node.content_binding.slide_id != self.slide_id
            or any(fact.binding.slide_id != self.slide_id for fact in node.facts)
            for node in self.nodes
        ):
            raise ValueError("all brief bindings must target the brief slide_id")
        required_ids = self.editability.required_node_ids
        if len(required_ids) != len(set(required_ids)) or not set(required_ids) <= node_ids:
            raise ValueError("editability required_node_ids must be unique known nodes")
        if self.editability.target == "pptx-native":
            raise ValueError("specialist v1 cannot claim pptx-native editability")
        if self.editability.target == "mixed" and not required_ids:
            raise ValueError("mixed editability requires declared editable nodes")
        reference_ids = [reference.asset_ref for reference in self.references]
        if len(reference_ids) != len(set(reference_ids)):
            raise ValueError("visual references must use unique asset ids")
        return self

    @model_validator(mode="after")
    def mode_text_and_deliverables_are_consistent(self) -> VisualAssetBrief:
        if len(self.deliverables) != len(set(self.deliverables)):
            raise ValueError("deliverables must be unique")
        if "png" not in self.deliverables:
            raise ValueError("png is always required")
        if self.mode == "HTML-RECONSTRUCTION":
            if self.text_policy == "baked" or self.reconstruction_policy is None:
                raise ValueError("reconstruction requires overlay/none and a policy")
        elif self.reconstruction_policy is not None:
            raise ValueError("IMAGE requires null reconstruction_policy")

        source_required = self.mode == "HTML-RECONSTRUCTION" or self.text_policy == "overlay"
        if source_required and "html-source" not in self.deliverables:
            raise ValueError("reconstruction and overlay require html-source")

        visible_text = [
            node.text
            for node in self.nodes
            if node.visible and node.text not in {None, ""}
        ]
        relation_labels = [
            relation.label for relation in self.relations if relation.label not in {None, ""}
        ]
        if self.text_policy == "none":
            if visible_text or relation_labels or self.accessibility.transcript != "":
                raise ValueError("none text policy forbids visible text, labels, and transcript")
        else:
            for node in self.nodes:
                if (
                    node.visible
                    and node.kind in {"title", "text", "data-label"}
                    and not node.text
                ):
                    raise ValueError("visible text-bearing nodes require non-empty text")
            required_transcript_values = [*visible_text, *relation_labels]
            required_transcript_values.extend(
                fact.value
                for node in self.nodes
                if node.required
                for fact in node.facts
            )
            if any(
                value not in self.accessibility.transcript
                for value in required_transcript_values
            ):
                raise ValueError("transcript must preserve visible text and required facts")

        numeric_pointers = {
            _binding_pointer(fact.binding)
            for node in self.nodes
            for fact in node.facts
            if fact.value_type == "decimal"
        }
        numeric_nodes = {
            node.id
            for node in self.nodes
            if node.visible
            and self.text_policy != "none"
            and (
                node.content_binding.field == "chart-value"
                or (
                    node.content_binding.field == "table-cell"
                    and _binding_pointer(node.content_binding) in numeric_pointers
                )
            )
        }
        if set(self.number_formatters) != numeric_nodes:
            raise ValueError("number_formatters must map exactly the visible numeric nodes")
        return self

    @model_validator(mode="after")
    def canvas_crop_and_motion_are_consistent(self) -> VisualAssetBrief:
        reference_ids = {reference.asset_ref for reference in self.references}
        if self.fit_policy == "crop-approved":
            if (
                self.crop is None
                or self.approval is None
                or self.crop.reference_asset_id not in reference_ids
            ):
                raise ValueError("crop-approved requires an approved known reference crop")
        elif self.crop is not None:
            raise ValueError("crop is only valid with crop-approved fit policy")

        motion_fields = (
            self.motion.adapter,
            self.motion.duration_seconds,
            self.motion.fps,
        )
        if self.motion.enabled:
            if (
                any(value is None for value in motion_fields)
                or "motion-video" not in self.deliverables
            ):
                raise ValueError("enabled motion requires adapter, duration, fps, and video")
        elif (
            any(value is not None for value in motion_fields)
            or "motion-video" in self.deliverables
        ):
            raise ValueError("disabled motion requires null motion fields and no video")
        return self

    @model_validator(mode="after")
    def execution_and_approval_are_consistent(self) -> VisualAssetBrief:
        reference_ids = {reference.asset_ref for reference in self.references}
        if self.mode == "HTML-RECONSTRUCTION":
            if not any(
                reference.role in {"composition", "content", "locked-design"}
                for reference in self.references
            ):
                raise ValueError("reconstruction requires a content-bearing reference")
            if (
                self.execution.image_source != "import"
                or self.execution.import_asset_id not in reference_ids
                or self.execution.max_provider_calls != 0
            ):
                raise ValueError(
                    "reconstruction v1 imports its primary reference with zero calls"
                )
            if self.approval is not None and self.approval.scope not in {
                "reference",
                "design",
            }:
                raise ValueError("reconstruction approval must cover reference or design")
        elif self.approval is not None and self.approval.scope not in {
            "brief",
            "design",
        }:
            raise ValueError("IMAGE approval must cover brief or design")
        return self


class VisualError(ValueError):
    def __init__(self, code: str, exit_code: int, message_vi: str) -> None:
        super().__init__(f"{code}: {message_vi}")
        self.code = code
        self.exit_code = exit_code
        self.message_vi = message_vi

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import re
import unicodedata
from typing import Any, Iterable

from presentation_studio.models.deck import (
    ChartElement,
    CodeElement,
    DeckSpec,
    ImageElement,
    ProcessElement,
    QuoteElement,
    SlideElement,
    SlideSpec,
    TableElement,
    TextContent,
    TextElement,
    TimelineElement,
)
from presentation_studio.models.visual import (
    AnyContentBinding,
    ChartBinding,
    ContentBinding,
    Fact,
    SemanticNode,
    VisualAssetBrief,
    VisualError,
    VisualNode,
    VisualRelation,
)
from presentation_studio.state import hash_inputs

from .formatting import format_number


_CHART_FIELDS = {"chart-label", "chart-value", "chart-unit", "display-unit"}
_TEXT_NODE_KINDS = {"title", "text", "data-label"}
_RELATION_ALT_PHRASES = {
    "sequence": "đứng trước",
    "branch": "phân nhánh tới",
    "cycle": "quay lại",
    "contains": "chứa",
    "compares": "so sánh với",
    "associates": "liên kết với",
}


@dataclass(frozen=True)
class ResolvedContent:
    pointer: str
    scalar: str | Decimal | None
    source_ref: str | None


def _content_error(message: str) -> VisualError:
    return VisualError("CONTENT_PARITY_FAILED", 2, message)


def _migration_error(message: str) -> VisualError:
    return VisualError("MIGRATION_REQUIRED", 2, message)


def _nfc(value: str | None) -> str | None:
    if value is None:
        return None
    return unicodedata.normalize("NFC", value)


def _nfc_object(value: Any) -> Any:
    if isinstance(value, str):
        return unicodedata.normalize("NFC", value)
    if isinstance(value, list):
        return [_nfc_object(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_nfc_object(item) for item in value)
    if isinstance(value, dict):
        return {key: _nfc_object(item) for key, item in value.items()}
    return value


def _decimal(value: object, *, pointer: str) -> Decimal:
    if isinstance(value, bool):
        raise _content_error(f"{pointer} không phải giá trị số canonical.")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as error:
        raise _content_error(f"{pointer} không phải số thập phân hợp lệ.") from error
    if not result.is_finite():
        raise _content_error(f"{pointer} phải là số hữu hạn.")
    return result


def _decimal_text(value: Decimal) -> str:
    return format(value, "f")


def _find_slide(deck: DeckSpec, slide_id: str) -> SlideSpec:
    matches = [slide for slide in deck.slides if slide.slide_id == slide_id]
    if len(matches) != 1:
        raise _content_error(
            f"slide_id {slide_id!r} phải xuất hiện đúng một lần trong DeckSpec."
        )
    return matches[0]


def _find_element(slide: SlideSpec, element_id: str | None) -> SlideElement:
    if element_id is None:
        raise _content_error("Binding element cần element_id.")
    matches = [
        element for element in slide.elements if element.element_id == element_id
    ]
    if len(matches) != 1:
        raise _content_error(
            f"element_id {element_id!r} phải xuất hiện đúng một lần "
            f"trong slide {slide.slide_id!r}."
        )
    return matches[0]


def _element_pointer(slide_id: str, element_id: str) -> str:
    return f"/slides/{slide_id}/elements/{element_id}"


def _require_index(values: list[Any], index: int | None, pointer: str) -> Any:
    if index is None or index < 0 or index >= len(values):
        raise _content_error(f"Binding vượt giới hạn tại {pointer}.")
    return values[index]


def resolve_binding(
    deck: DeckSpec, binding: ContentBinding | ChartBinding
) -> ResolvedContent:
    """Resolve an allowlisted typed binding to a stable, read-only pointer."""

    slide = _find_slide(deck, binding.slide_id)
    slide_pointer = f"/slides/{slide.slide_id}"
    field = binding.field

    if field == "slide-title":
        return ResolvedContent(f"{slide_pointer}/title", _nfc(slide.title), None)
    if field == "slide-message":
        return ResolvedContent(f"{slide_pointer}/message", _nfc(slide.message), None)
    if field == "deck-audience":
        return ResolvedContent("/audience", _nfc(deck.audience), None)
    if field == "deck-purpose":
        return ResolvedContent("/purpose", _nfc(deck.purpose), None)
    if field == "slide-notes":
        return ResolvedContent(
            f"{slide_pointer}/notes", _nfc(slide.notes) or "", None
        )
    if field == "semantic-node":
        if slide.visual_semantics is None:
            raise _content_error(
                f"Slide {slide.slide_id!r} không có visual_semantics."
            )
        if not any(node.id == binding.item_id for node in slide.visual_semantics.nodes):
            raise _content_error(
                f"Không tìm thấy semantic node {binding.item_id!r}."
            )
        return ResolvedContent(
            f"{slide_pointer}/visual_semantics/nodes/{binding.item_id}", None, None
        )

    element = _find_element(slide, binding.element_id)
    base = _element_pointer(slide.slide_id, element.element_id)

    if field in _CHART_FIELDS:
        if not isinstance(binding, ChartBinding) or not isinstance(element, ChartElement):
            raise _content_error(
                f"Binding {field!r} phải trỏ đến ChartElement bằng ChartBinding."
            )
        source_ref = element.content.source_ref
        if field in {"chart-label", "chart-value"}:
            datum = _require_index(
                element.content.data, binding.item_index, f"{base}/content/data"
            )
            if field == "chart-label":
                return ResolvedContent(
                    f"{base}/content/data/{binding.item_index}/label",
                    _nfc(datum.label),
                    source_ref,
                )
            pointer = f"{base}/content/data/{binding.item_index}/value"
            return ResolvedContent(
                pointer,
                _decimal(datum.value, pointer=pointer),
                source_ref,
            )
        return ResolvedContent(
            f"{base}/content/unit", _nfc(element.content.unit), source_ref
        )

    if field in {"text-content", "text-label", "text-item"}:
        if not isinstance(element, TextElement):
            raise _content_error(f"Binding {field!r} phải trỏ đến TextElement.")
        content = element.content
        if field == "text-content":
            scalar = content if isinstance(content, str) else content.text
            suffix = "" if isinstance(content, str) else "/text"
            return ResolvedContent(f"{base}/content{suffix}", _nfc(scalar), None)
        if not isinstance(content, TextContent):
            raise _content_error(f"Binding {field!r} cần TextContent có cấu trúc.")
        if field == "text-label":
            return ResolvedContent(
                f"{base}/content/label", _nfc(content.label), None
            )
        item = _require_index(content.items, binding.item_index, f"{base}/content/items")
        return ResolvedContent(
            f"{base}/content/items/{binding.item_index}", _nfc(item), None
        )

    if field in {"process-title", "process-description"}:
        if not isinstance(element, ProcessElement):
            raise _content_error(f"Binding {field!r} phải trỏ đến ProcessElement.")
        matches = [
            step for step in element.content.steps if step.id == binding.item_id
        ]
        if len(matches) != 1:
            raise _content_error(
                f"Process step {binding.item_id!r} phải xuất hiện đúng một lần."
            )
        step = matches[0]
        attribute = "title" if field == "process-title" else "description"
        return ResolvedContent(
            f"{base}/content/steps/{step.id}/{attribute}",
            _nfc(getattr(step, attribute)),
            None,
        )

    if field == "table-cell":
        if not isinstance(element, TableElement):
            raise _content_error("Binding 'table-cell' phải trỏ đến TableElement.")
        row = _require_index(
            element.content.rows, binding.item_index, f"{base}/content/rows"
        )
        match = re.fullmatch(r"col-(\d+)", binding.item_id or "")
        if match is None:
            raise _content_error("Binding table-cell cần item_id dạng col-N.")
        column = int(match.group(1))
        cell = _require_index(row, column, f"{base}/content/rows/{binding.item_index}")
        pointer = f"{base}/content/rows/{binding.item_index}/col-{column}"
        if isinstance(cell, bool) or cell is None:
            scalar: str | Decimal | None = None if cell is None else str(cell).lower()
        elif isinstance(cell, (int, float, Decimal)):
            scalar = _decimal(cell, pointer=pointer)
        else:
            scalar = _nfc(cell)
        return ResolvedContent(pointer, scalar, None)

    if field == "quote-text":
        if not isinstance(element, QuoteElement):
            raise _content_error("Binding 'quote-text' phải trỏ đến QuoteElement.")
        return ResolvedContent(f"{base}/content/quote", _nfc(element.content.quote), None)

    if field == "code-text":
        if not isinstance(element, CodeElement):
            raise _content_error("Binding 'code-text' phải trỏ đến CodeElement.")
        return ResolvedContent(f"{base}/content/code", _nfc(element.content.code), None)

    if field in {"image-content", "image-alt"}:
        if not isinstance(element, ImageElement):
            raise _content_error(f"Binding {field!r} phải trỏ đến ImageElement.")
        if field == "image-content":
            return ResolvedContent(
                f"{base}/content/asset_ref", element.content.asset_ref, None
            )
        return ResolvedContent(f"{base}/alt_text", _nfc(element.alt_text), None)

    raise _content_error(f"Binding field {field!r} chưa được hỗ trợ.")


def _binding_payload(binding: AnyContentBinding) -> dict[str, Any]:
    return _nfc_object(binding.model_dump(mode="json"))


def _used_source_ids(slide: SlideSpec) -> set[str]:
    source_ids = set(slide.source_refs)
    for element in slide.elements:
        if isinstance(element, ChartElement) and element.content.source_ref is not None:
            source_ids.add(element.content.source_ref)
    if slide.visual_semantics is not None:
        source_ids.update(
            fact.source_ref
            for node in slide.visual_semantics.nodes
            for fact in node.facts
        )
    return source_ids


def _validate_source(
    deck: DeckSpec, slide: SlideSpec, source_ref: str, *, context: str
) -> None:
    known = {source.id for source in deck.sources}
    if source_ref not in known:
        raise _content_error(f"{context} trỏ source_ref không tồn tại {source_ref!r}.")
    if source_ref not in slide.source_refs:
        raise _content_error(
            f"{context} trỏ source_ref {source_ref!r} ngoài source_refs của slide."
        )


def _fact_payload(
    deck: DeckSpec,
    slide: SlideSpec,
    fact: Fact,
) -> dict[str, Any]:
    resolved = resolve_binding(deck, fact.binding)
    if resolved.scalar is None:
        raise _content_error(f"Fact {fact.id!r} trỏ giá trị canonical null.")
    if isinstance(resolved.scalar, Decimal):
        expected_type = "decimal"
        expected_value = _decimal_text(resolved.scalar)
    else:
        expected_type = "string"
        expected_value = resolved.scalar
    if fact.value_type != expected_type or _nfc(fact.value) != expected_value:
        raise _content_error(
            f"Fact {fact.id!r} lệch value/type tại {resolved.pointer}."
        )
    _validate_source(deck, slide, fact.source_ref, context=f"Fact {fact.id!r}")
    if isinstance(fact.binding, ChartBinding):
        if resolved.source_ref is None:
            raise _content_error(
                f"Fact {fact.id!r} không được bịa nguồn cho chart chưa có source_ref."
            )
        if fact.source_ref != resolved.source_ref:
            raise _content_error(
                f"Fact {fact.id!r} dùng source_ref khác canonical chart."
            )
    return {
        "id": fact.id,
        "binding": _binding_payload(fact.binding),
        "pointer": resolved.pointer,
        "value_type": fact.value_type,
        "value": expected_value,
        "source_ref": fact.source_ref,
    }


def _validate_chart_groups(
    deck: DeckSpec,
    slide: SlideSpec,
    nodes: Iterable[SemanticNode | VisualNode],
) -> None:
    datum_fields: dict[tuple[str, int], set[str]] = {}
    node_pointers: set[str] = set()
    fact_pointers: dict[str, int] = {}
    unit_elements: set[str] = set()

    for node in nodes:
        for fact in node.facts:
            pointer = resolve_binding(deck, fact.binding).pointer
            fact_pointers[pointer] = fact_pointers.get(pointer, 0) + 1
        binding = node.content_binding
        if not isinstance(binding, ChartBinding):
            continue
        resolved = resolve_binding(deck, binding)
        node_pointers.add(resolved.pointer)
        if binding.field in {"chart-label", "chart-value"}:
            assert binding.item_index is not None
            datum_fields.setdefault(
                (binding.element_id, binding.item_index), set()
            ).add(binding.field)
        else:
            unit_elements.add(binding.element_id)

    for (element_id, item_index), fields in datum_fields.items():
        if fields != {"chart-label", "chart-value"}:
            raise _content_error(
                "Chart label/value phải cùng datum; "
                f"{element_id!r} index {item_index} chỉ có {sorted(fields)}."
            )

    for element_id in {
        element_id for element_id, _ in datum_fields
    } | unit_elements:
        element = _find_element(slide, element_id)
        if not isinstance(element, ChartElement):
            raise _content_error(f"{element_id!r} không phải ChartElement.")
        source_ref = element.content.source_ref
        relevant_pointers = {
            pointer
            for pointer in node_pointers
            if pointer.startswith(
                f"/slides/{slide.slide_id}/elements/{element_id}/content/"
            )
        }
        if element_id in unit_elements and element.content.unit is None:
            raise _content_error(
                f"Chart {element_id!r} có display-unit nhưng canonical unit là null."
            )
        if source_ref is None:
            if any(fact_pointers.get(pointer, 0) for pointer in relevant_pointers):
                raise _content_error(
                    f"Chart {element_id!r} chưa có source_ref nên không được có Fact."
                )
            continue
        _validate_source(deck, slide, source_ref, context=f"Chart {element_id!r}")
        for pointer in relevant_pointers:
            if fact_pointers.get(pointer, 0) != 1:
                raise _content_error(
                    f"Canonical pointer {pointer} phải có đúng một Fact owner."
                )


def _semantics_payload(deck: DeckSpec, slide: SlideSpec) -> dict[str, Any] | None:
    semantics = slide.visual_semantics
    if semantics is None:
        return None
    fact_ids: set[str] = set()
    fact_pointers: set[str] = set()
    nodes: list[dict[str, Any]] = []
    for node in sorted(semantics.nodes, key=lambda item: item.id):
        if node.content_binding.slide_id != slide.slide_id:
            raise _content_error(
                f"Node {node.id!r} trỏ slide khác slide canonical."
            )
        facts: list[dict[str, Any]] = []
        for fact in sorted(node.facts, key=lambda item: item.id):
            projected = _fact_payload(deck, slide, fact)
            if fact.id in fact_ids or projected["pointer"] in fact_pointers:
                raise _content_error("Fact ID và canonical pointer phải có một owner.")
            fact_ids.add(fact.id)
            fact_pointers.add(projected["pointer"])
            facts.append(projected)
        if node.content_binding.field == "image-content":
            resolved = resolve_binding(deck, node.content_binding)
            if node.asset_ref != resolved.scalar:
                raise _content_error(
                    f"Node {node.id!r} có asset_ref lệch ImageElement canonical."
                )
        nodes.append(
            {
                "id": node.id,
                "kind": node.kind,
                "content_binding": _binding_payload(node.content_binding),
                "parent_id": node.parent_id,
                "visible": node.visible,
                "required": node.required,
                "semantic_role": _nfc(node.semantic_role),
                "facts": facts,
                "asset_ref": node.asset_ref,
            }
        )
    _validate_chart_groups(deck, slide, semantics.nodes)
    relations = [
        {
            "id": relation.id,
            "from_id": relation.from_id,
            "to_id": relation.to_id,
            "kind": relation.kind,
            "label": _nfc(relation.label),
            "required": relation.required,
        }
        for relation in sorted(semantics.relations, key=lambda item: item.id)
    ]
    return {
        "nodes": nodes,
        "relations": relations,
        "reading_order": list(semantics.reading_order),
    }


def _project_cell(cell: str | float | int | bool | None, pointer: str) -> Any:
    if isinstance(cell, str):
        return _nfc(cell)
    if isinstance(cell, bool) or cell is None:
        return cell
    return _decimal_text(_decimal(cell, pointer=pointer))


def _element_payload(slide: SlideSpec, element: SlideElement) -> dict[str, Any]:
    base: dict[str, Any] = {
        "element_id": element.element_id,
        "kind": element.kind,
        "role": element.role,
        "alt_text": _nfc(element.alt_text),
    }
    if isinstance(element, TextElement):
        if isinstance(element.content, str):
            content: Any = _nfc(element.content)
        else:
            content = {
                "text": _nfc(element.content.text),
                "label": _nfc(element.content.label),
                "items": [_nfc(item) for item in element.content.items],
            }
    elif isinstance(element, ImageElement):
        content = {"asset_ref": element.content.asset_ref}
    elif isinstance(element, ChartElement):
        content = {
            "chart_type": element.content.chart_type,
            "data": [
                {
                    "label": _nfc(datum.label),
                    "value": _decimal_text(
                        _decimal(
                            datum.value,
                            pointer=(
                                f"/slides/{slide.slide_id}/elements/"
                                f"{element.element_id}/content/data/{index}/value"
                            ),
                        )
                    ),
                }
                for index, datum in enumerate(element.content.data)
            ],
            "unit": _nfc(element.content.unit),
            "source_ref": element.content.source_ref,
        }
    elif isinstance(element, TableElement):
        content = {
            "columns": [_nfc(column) for column in element.content.columns],
            "rows": [
                [
                    _project_cell(
                        cell,
                        (
                            f"/slides/{slide.slide_id}/elements/{element.element_id}/"
                            f"content/rows/{row_index}/col-{column_index}"
                        ),
                    )
                    for column_index, cell in enumerate(row)
                ]
                for row_index, row in enumerate(element.content.rows)
            ],
        }
    elif isinstance(element, ProcessElement):
        content = {
            "steps": [
                {
                    "id": step.id,
                    "title": _nfc(step.title),
                    "description": _nfc(step.description),
                }
                for step in element.content.steps
            ],
            "connector": element.content.connector,
        }
    elif isinstance(element, TimelineElement):
        content = {
            "items": [
                {
                    "time_label": _nfc(item.time_label),
                    "title": _nfc(item.title),
                    "description": _nfc(item.description),
                }
                for item in element.content.items
            ]
        }
    elif isinstance(element, QuoteElement):
        content = {
            "quote": _nfc(element.content.quote),
            "attribution": _nfc(element.content.attribution),
        }
    elif isinstance(element, CodeElement):
        content = {
            "code": _nfc(element.content.code),
            "language": element.content.language,
        }
    else:  # pragma: no cover - SlideElement is a closed discriminated union.
        raise _content_error(f"Element kind {element.kind!r} chưa được hỗ trợ.")
    base["content"] = content
    return base


def content_projection(deck: DeckSpec, slide_id: str) -> dict[str, Any]:
    """Return the v1 semantic allowlist for exactly one canonical slide."""

    slide = _find_slide(deck, slide_id)
    source_id_list = [source.id for source in deck.sources]
    if len(source_id_list) != len(set(source_id_list)):
        raise _content_error("DeckSpec có source ID trùng nên không thể chiếu canonical.")
    element_ids = [element.element_id for element in slide.elements]
    if len(element_ids) != len(set(element_ids)):
        raise _content_error("Slide có element_id trùng nên không thể chiếu canonical.")
    for element in slide.elements:
        if isinstance(element, ChartElement) and element.content.source_ref is not None:
            _validate_source(
                deck,
                slide,
                element.content.source_ref,
                context=f"Chart {element.element_id!r}",
            )
    semantics = _semantics_payload(deck, slide)
    source_ids = _used_source_ids(slide)
    sources_by_id = {source.id: source for source in deck.sources}
    missing = source_ids - set(sources_by_id)
    if missing:
        raise _content_error(f"Slide dùng source_ref không tồn tại: {sorted(missing)}.")
    return {
        "projection_version": "1.0",
        "deck": {
            "title": _nfc(deck.title),
            "audience": _nfc(deck.audience),
            "purpose": _nfc(deck.purpose),
        },
        "slide": {
            "slide_id": slide.slide_id,
            "title": _nfc(slide.title),
            "message": _nfc(slide.message),
            "elements": [
                _element_payload(slide, element)
                for element in sorted(slide.elements, key=lambda item: item.element_id)
            ],
            "notes": _nfc(slide.notes) or "",
            "source_refs": sorted(source_ids),
            "visual_semantics": semantics,
        },
        "sources": [
            {
                "id": source.id,
                "kind": source.kind,
                "title": _nfc(source.title),
                "sha256": source.sha256,
            }
            for source in sorted(
                (sources_by_id[source_id] for source_id in source_ids),
                key=lambda item: item.id,
            )
        ],
    }


def _relation_payload(relation: VisualRelation) -> dict[str, Any]:
    return {
        "id": relation.id,
        "from_id": relation.from_id,
        "to_id": relation.to_id,
        "kind": relation.kind,
        "label": _nfc(relation.label),
        "required": relation.required,
    }


def _semantic_node_signature(node: SemanticNode | VisualNode) -> dict[str, Any]:
    return {
        "id": node.id,
        "kind": node.kind,
        "content_binding": _binding_payload(node.content_binding),
        "parent_id": node.parent_id,
        "visible": node.visible,
        "required": node.required,
        "semantic_role": _nfc(node.semantic_role),
        "asset_ref": node.asset_ref,
    }


def _expected_node_text(
    deck: DeckSpec,
    brief: VisualAssetBrief,
    node: SemanticNode | VisualNode,
) -> tuple[str | None, bool]:
    if brief.text_policy == "none" or not node.visible:
        return None, False
    resolved = resolve_binding(deck, node.content_binding)
    if isinstance(resolved.scalar, Decimal):
        formatter = brief.number_formatters.get(node.id)
        if formatter is None:
            raise _content_error(
                f"Numeric node {node.id!r} thiếu NumberFormatter."
            )
        return format_number(resolved.scalar, formatter)
    if node.id in brief.number_formatters:
        raise _content_error(
            f"Node không phải số {node.id!r} không được có NumberFormatter."
        )
    if node.content_binding.field in {"semantic-node", "image-content"}:
        return None, False
    if resolved.scalar is None:
        if node.visible and node.kind in _TEXT_NODE_KINDS:
            raise _content_error(
                f"Node hiển thị {node.id!r} trỏ canonical value null."
            )
        return None, False
    return resolved.scalar, False


def _legacy_binding_order(
    deck: DeckSpec,
    slide: SlideSpec,
    node: VisualNode,
) -> tuple[int, int, int, int, str]:
    binding = node.content_binding
    if binding.field == "semantic-node":
        raise _migration_error(
            "DeckSpec 1.0 không chứng minh được semantic-node; cần migrate sang 1.1."
        )
    resolve_binding(deck, binding)
    top_level = {
        "slide-title": 0,
        "slide-message": 1,
        "deck-purpose": 2,
        "deck-audience": 3,
    }
    if binding.field in top_level:
        return (top_level[binding.field], 0, 0, 0, node.id)
    if binding.field == "slide-notes":
        return (5, 0, 0, 0, node.id)

    element = _find_element(slide, binding.element_id)
    element_index = next(
        index
        for index, candidate in enumerate(slide.elements)
        if candidate is element
    )
    item_index = binding.item_index or 0
    field_order = 0
    if isinstance(binding, ChartBinding):
        if binding.field in {"chart-unit", "display-unit"}:
            item_index = len(element.content.data) if isinstance(element, ChartElement) else 0
            field_order = 0 if binding.field == "chart-unit" else 1
        else:
            field_order = 0 if binding.field == "chart-label" else 1
    elif binding.field in {"process-title", "process-description"}:
        assert isinstance(element, ProcessElement)
        item_index = next(
            index
            for index, step in enumerate(element.content.steps)
            if step.id == binding.item_id
        )
        field_order = 0 if binding.field == "process-title" else 1
    elif binding.field == "table-cell":
        match = re.fullmatch(r"col-(\d+)", binding.item_id or "")
        assert match is not None
        field_order = int(match.group(1))
    else:
        field_order = {
            "text-label": 0,
            "text-content": 1,
            "text-item": 2,
            "image-content": 0,
            "image-alt": 1,
            "quote-text": 0,
            "code-text": 0,
        }[binding.field]
    return (4, element_index, item_index, field_order, node.id)


def _legacy_reading_order(
    deck: DeckSpec,
    slide: SlideSpec,
    nodes: Iterable[VisualNode],
    relations: Iterable[VisualRelation],
) -> list[str]:
    node_list = list(nodes)
    if list(relations) or any(node.parent_id is not None for node in node_list):
        raise _migration_error(
            "DeckSpec 1.0 không chứng minh được graph relation; cần migrate sang 1.1."
        )
    ordered = sorted(
        (node for node in node_list if node.visible),
        key=lambda node: _legacy_binding_order(deck, slide, node),
    )
    for node in node_list:
        if not node.visible:
            _legacy_binding_order(deck, slide, node)
    return [node.id for node in ordered]


def _assert_fact_sets(
    deck: DeckSpec,
    slide: SlideSpec,
    canonical: SemanticNode,
    projected: VisualNode,
) -> None:
    canonical_ids = [fact.id for fact in canonical.facts]
    projected_ids = [fact.id for fact in projected.facts]
    if len(canonical_ids) != len(set(canonical_ids)) or len(projected_ids) != len(
        set(projected_ids)
    ):
        raise _content_error(f"Node {canonical.id!r} có Fact ID trùng.")
    canonical_facts = {
        fact.id: _fact_payload(deck, slide, fact)
        for fact in canonical.facts
    }
    projected_facts = {
        fact.id: _fact_payload(deck, slide, fact)
        for fact in projected.facts
    }
    if canonical_facts != projected_facts:
        raise _content_error(f"Facts của node {canonical.id!r} lệch canonical.")


def _projected_alt_text(
    deck: DeckSpec,
    slide: SlideSpec,
    reading_order: list[str],
    nodes: list[VisualNode],
    relations: list[VisualRelation],
) -> str:
    nodes_by_id = {node.id: node for node in nodes}
    content_parts: list[str] = []
    for node_id in reading_order:
        node = nodes_by_id[node_id]
        value = node.text
        if value is None:
            binding = node.content_binding
            if binding.field == "image-content":
                binding = ContentBinding(
                    slide_id=binding.slide_id,
                    element_id=binding.element_id,
                    field="image-alt",
                )
            scalar = resolve_binding(deck, binding).scalar
            if isinstance(scalar, Decimal):
                value = _decimal_text(scalar)
            elif isinstance(scalar, str):
                value = _nfc(scalar)
        if value:
            content_parts.append(value)

    sentences: list[str] = []
    if content_parts:
        sentences.append(
            f"Nội dung theo thứ tự đọc: {'; '.join(content_parts)}."
        )
    relation_parts: list[str] = []
    for relation in sorted(relations, key=lambda item: item.id):
        description = (
            f"{relation.from_id} {_RELATION_ALT_PHRASES[relation.kind]} "
            f"{relation.to_id}"
        )
        if relation.label:
            description += f" ({relation.label})"
        relation_parts.append(description)
    if relation_parts:
        sentences.append(f"Quan hệ: {'; '.join(relation_parts)}.")
    if not sentences:
        fallback = _nfc(slide.message) or _nfc(slide.title) or _nfc(deck.title)
        sentences.append(f"Nội dung slide: {fallback}.")
    return " ".join(sentences)


def _assert_alt_text(
    deck: DeckSpec,
    slide: SlideSpec,
    brief: VisualAssetBrief,
) -> None:
    expected = _projected_alt_text(
        deck,
        slide,
        brief.reading_order,
        brief.nodes,
        brief.relations,
    )
    if brief.accessibility.alt_text != expected:
        raise _content_error(
            "accessibility.alt_text lệch canonical projection."
        )


def _assert_transcript(
    brief: VisualAssetBrief,
    nodes: dict[str, VisualNode],
    rounded_source_values: dict[str, str],
) -> None:
    if brief.text_policy == "none":
        if brief.accessibility.transcript != "":
            raise _content_error("Text policy none yêu cầu transcript rỗng.")
        return
    position = 0
    for node_id in brief.reading_order:
        text = nodes[node_id].text
        if text in {None, ""}:
            continue
        next_position = brief.accessibility.transcript.find(text, position)
        if next_position < 0:
            raise _content_error(
                f"Transcript thiếu text của node {node_id!r} theo reading_order."
            )
        position = next_position + len(text)
    for node in nodes.values():
        if not node.required:
            continue
        for fact in node.facts:
            if fact.value not in brief.accessibility.transcript:
                raise _content_error(
                    f"Transcript thiếu canonical Fact {fact.id!r}."
                )
    for node_id, source_value in rounded_source_values.items():
        if f"giá trị nguồn {source_value}" not in brief.accessibility.transcript:
            raise _content_error(
                f"Transcript thiếu giá trị nguồn của rounded node {node_id!r}."
            )
    expected = _projected_transcript(
        brief.text_policy,
        brief.reading_order,
        sorted(nodes.values(), key=lambda item: item.id),
        sorted(brief.relations, key=lambda item: item.id),
        rounded_source_values,
    )
    if brief.accessibility.transcript != expected:
        raise _content_error(
            "Transcript chứa nội dung semantic ngoài canonical projection."
        )


def assert_content_parity(deck: DeckSpec, brief: VisualAssetBrief) -> None:
    """Fail closed when the brief is not an exact canonical content projection."""

    slide = _find_slide(deck, brief.slide_id)
    projection = content_projection(deck, brief.slide_id)
    expected_hash = hash_inputs(projection)
    if brief.deck_binding.slide_content_hash != expected_hash:
        raise _content_error(
            "deck_binding.slide_content_hash đã stale; cần project lại từ DeckSpec."
        )
    if _nfc(brief.purpose) != _nfc(deck.purpose):
        raise _content_error("brief.purpose lệch DeckSpec.purpose.")
    if _nfc(brief.audience) != _nfc(deck.audience):
        raise _content_error("brief.audience lệch DeckSpec.audience.")
    if _nfc(brief.message) != _nfc(slide.message):
        raise _content_error("brief.message lệch SlideSpec.message.")
    if brief.accessibility.notes != (_nfc(slide.notes) or ""):
        raise _content_error("brief.accessibility.notes lệch SlideSpec.notes.")

    nodes_by_id = {node.id: node for node in brief.nodes}
    if len(nodes_by_id) != len(brief.nodes):
        raise _content_error("Brief có node ID trùng.")
    semantics = slide.visual_semantics
    rounded_source_values: dict[str, str] = {}
    expected_formatter_ids = {
        node.id
        for node in brief.nodes
        if brief.text_policy != "none"
        and node.visible
        and isinstance(resolve_binding(deck, node.content_binding).scalar, Decimal)
    }
    if set(brief.number_formatters) != expected_formatter_ids:
        raise _content_error(
            "number_formatters phải ánh xạ đúng các numeric node đang hiển thị."
        )
    if semantics is not None:
        canonical_by_id = {node.id: node for node in semantics.nodes}
        if set(nodes_by_id) != set(canonical_by_id):
            raise _content_error("Brief node IDs lệch visual_semantics canonical.")
        for node_id, canonical in canonical_by_id.items():
            projected = nodes_by_id[node_id]
            if _semantic_node_signature(projected) != _semantic_node_signature(canonical):
                raise _content_error(f"Node {node_id!r} lệch canonical semantics.")
            _assert_fact_sets(deck, slide, canonical, projected)
            expected_text, rounded = _expected_node_text(deck, brief, canonical)
            if _nfc(projected.text) != expected_text:
                raise _content_error(f"Node text {node_id!r} lệch canonical/formatter.")
            if rounded:
                resolved = resolve_binding(deck, canonical.content_binding)
                assert isinstance(resolved.scalar, Decimal)
                rounded_source_values[node_id] = _decimal_text(resolved.scalar)
        canonical_relations = {
            relation.id: _relation_payload(relation)
            for relation in semantics.relations
        }
        projected_relations = {
            relation.id: _relation_payload(relation)
            for relation in brief.relations
        }
        if len(canonical_relations) != len(semantics.relations) or len(
            projected_relations
        ) != len(brief.relations):
            raise _content_error("Brief hoặc canonical có relation ID trùng.")
        if canonical_relations != projected_relations:
            raise _content_error("Brief relations lệch visual_semantics canonical.")
        if brief.reading_order != semantics.reading_order:
            raise _content_error("Brief reading_order lệch canonical.")
        _validate_chart_groups(deck, slide, brief.nodes)
    else:
        expected_reading_order = _legacy_reading_order(
            deck, slide, brief.nodes, brief.relations
        )
        if brief.reading_order != expected_reading_order:
            raise _content_error(
                "Brief reading_order lệch deterministic DeckSpec 1.0 adapter."
            )
        for node in brief.nodes:
            if node.content_binding.slide_id != slide.slide_id:
                raise _content_error(f"Node {node.id!r} trỏ slide khác.")
            for fact in node.facts:
                _fact_payload(deck, slide, fact)
            expected_text, rounded = _expected_node_text(deck, brief, node)
            if _nfc(node.text) != expected_text:
                raise _content_error(f"Node text {node.id!r} lệch canonical/formatter.")
            if rounded:
                resolved = resolve_binding(deck, node.content_binding)
                assert isinstance(resolved.scalar, Decimal)
                rounded_source_values[node.id] = _decimal_text(resolved.scalar)
        _validate_chart_groups(deck, slide, brief.nodes)
    _assert_transcript(brief, nodes_by_id, rounded_source_values)
    _assert_alt_text(deck, slide, brief)


def _projected_transcript(
    text_policy: str,
    reading_order: list[str],
    nodes: list[VisualNode],
    relations: list[VisualRelation],
    rounded_source_values: dict[str, str],
) -> str:
    if text_policy == "none":
        return ""
    nodes_by_id = {node.id: node for node in nodes}
    parts: list[str] = []
    for node_id in reading_order:
        value = nodes_by_id[node_id].text
        if value:
            parts.append(value)
    for relation in relations:
        if relation.label and relation.label not in parts:
            parts.append(relation.label)
    for node in nodes:
        if not node.required:
            continue
        for fact in node.facts:
            if fact.value_type == "decimal":
                if rounded_source_values.get(node.id) != fact.value:
                    parts.append(f"giá trị nguồn {fact.value}")
            elif fact.value not in parts:
                parts.append(fact.value)
    for node_id in reading_order:
        if node_id in rounded_source_values:
            parts.append(f"giá trị nguồn {rounded_source_values[node_id]}")
    if rounded_source_values:
        parts.append("giá trị hiển thị được làm tròn")
    return "; ".join(parts) + ("." if parts else "")


def project_brief(
    deck: DeckSpec,
    brief: VisualAssetBrief,
    deck_raw_sha256: str,
) -> VisualAssetBrief:
    """Copy canonical content into a new brief while retaining design choices."""

    slide = _find_slide(deck, brief.slide_id)
    projection = content_projection(deck, brief.slide_id)
    semantics = slide.visual_semantics
    design_by_id = {node.id: node for node in brief.nodes}
    if len(design_by_id) != len(brief.nodes):
        raise _content_error("Brief có node ID trùng nên không thể giữ design.")
    if semantics is not None:
        canonical_ids = {node.id for node in semantics.nodes}
        if canonical_ids != set(design_by_id):
            raise _content_error(
                "Không thể giữ design khi brief node IDs lệch canonical semantics."
            )
        source_nodes: Iterable[SemanticNode | VisualNode] = sorted(
            semantics.nodes, key=lambda item: item.id
        )
        relations = [
            relation.model_copy(deep=True)
            for relation in sorted(semantics.relations, key=lambda item: item.id)
        ]
        reading_order = list(semantics.reading_order)
    else:
        source_nodes = sorted(brief.nodes, key=lambda item: item.id)
        reading_order = _legacy_reading_order(
            deck, slide, brief.nodes, brief.relations
        )
        relations = []

    nodes: list[VisualNode] = []
    rounded_source_values: dict[str, str] = {}
    for source_node in source_nodes:
        preferred_box = design_by_id[source_node.id].preferred_box
        text, rounded = _expected_node_text(deck, brief, source_node)
        if rounded:
            resolved = resolve_binding(deck, source_node.content_binding)
            assert isinstance(resolved.scalar, Decimal)
            rounded_source_values[source_node.id] = _decimal_text(resolved.scalar)
        node_payload = source_node.model_dump(mode="python")
        node_payload.update(
            {
                "facts": [
                    fact.model_copy(deep=True)
                    for fact in sorted(source_node.facts, key=lambda item: item.id)
                ],
                "text": text,
                "preferred_box": (
                    preferred_box.model_copy(deep=True)
                    if preferred_box is not None
                    else None
                ),
            }
        )
        nodes.append(VisualNode.model_validate(node_payload))

    accessibility = brief.accessibility.model_dump(mode="python")
    accessibility.update(
        {
            "alt_text": _projected_alt_text(
                deck,
                slide,
                reading_order,
                nodes,
                relations,
            ),
            "notes": _nfc(slide.notes) or "",
            "transcript": _projected_transcript(
                brief.text_policy,
                reading_order,
                nodes,
                relations,
                rounded_source_values,
            ),
        }
    )
    deck_binding = brief.deck_binding.model_dump(mode="python")
    deck_binding.update(
        {
            "deck_raw_sha256": deck_raw_sha256,
            "slide_content_hash": hash_inputs(projection),
            "projection_version": "1.0",
        }
    )
    payload = brief.model_dump(mode="python")
    payload.update(
        {
            "purpose": _nfc(deck.purpose),
            "audience": _nfc(deck.audience),
            "message": _nfc(slide.message),
            "nodes": nodes,
            "relations": relations,
            "reading_order": reading_order,
            "accessibility": accessibility,
            "deck_binding": deck_binding,
        }
    )
    try:
        projected = VisualAssetBrief.model_validate(payload)
    except (TypeError, ValueError) as error:
        if isinstance(error, VisualError):
            raise
        raise _content_error(
            "Brief projected không vượt qua strict model validation."
        ) from error
    assert_content_parity(deck, projected)
    return projected


def project_build_deck(deck: DeckSpec, brief: VisualAssetBrief) -> DeckSpec:
    """Create the isolated one-slide DeckSpec passed to a visual backend."""

    assert_content_parity(deck, brief)
    slide = _find_slide(deck, brief.slide_id)
    source_ids = _used_source_ids(slide)
    payload = {
        "schema_version": deck.schema_version,
        "title": deck.title,
        "audience": deck.audience,
        "purpose": deck.purpose,
        "canvas": {
            "ratio": "custom",
            "width": float(brief.canvas.width_px),
            "height": float(brief.canvas.height_px),
            "unit": "px",
        },
        "slides": [slide.model_dump(mode="python")],
        "sources": [
            source.model_dump(mode="python")
            for source in deck.sources
            if source.id in source_ids
        ],
    }
    try:
        return DeckSpec.model_validate(payload)
    except (TypeError, ValueError) as error:
        if isinstance(error, VisualError):
            raise
        raise _content_error(
            "Build deck projected không vượt qua strict model validation."
        ) from error

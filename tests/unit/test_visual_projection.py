from __future__ import annotations

from copy import deepcopy
from decimal import Decimal
import json
import unicodedata

import pytest

from presentation_studio.models import (
    ChartBinding,
    ChartDatum,
    ContentBinding,
    DeckSpec,
    SourceRef,
    VisualAssetBrief,
    VisualError,
    VisualRelation,
)
from presentation_studio.state import hash_inputs
from presentation_studio.visual.formatting import format_number
from presentation_studio.visual.projection import (
    assert_content_parity,
    content_projection,
    project_brief,
    project_build_deck,
    resolve_binding,
)
from tests.visual_support import fixture_json, load_brief


RAW_DECK_HASH = "b" * 64


def _chart_deck() -> DeckSpec:
    return DeckSpec.model_validate(fixture_json("deck-chart-1.1"))


def _node(brief: VisualAssetBrief, node_id: str):
    return next(node for node in brief.nodes if node.id == node_id)


def _semantic_node(deck: DeckSpec, node_id: str):
    semantics = deck.slides[0].visual_semantics
    assert semantics is not None
    return next(node for node in semantics.nodes if node.id == node_id)


def _set_chart_value(deck: DeckSpec, value: float, fact_value: str) -> None:
    chart = deck.slides[0].elements[0]
    assert chart.kind == "chart"
    chart.content.data[0].value = value
    _semantic_node(deck, "value-a").facts[0].value = fact_value


def _set_chart_unit(deck: DeckSpec, value: str) -> None:
    chart = deck.slides[0].elements[0]
    assert chart.kind == "chart"
    chart.content.unit = value
    _semantic_node(deck, "unit").facts[0].value = value


def _assert_error(error: pytest.ExceptionInfo[VisualError], code: str) -> None:
    assert error.value.code == code
    assert error.value.exit_code == 2


def test_vietnamese_value_is_not_fact_value() -> None:
    # The formatter registry is keyed by canonical node ID (§5.1), not field name.
    fmt = load_brief().number_formatters["value-a"]

    assert format_number(Decimal("18.5"), fmt) == ("18,5", False)
    fmt = fmt.model_copy(update={"precision": 2})
    assert format_number(Decimal("18.5"), fmt) == ("18,50", False)


@pytest.mark.parametrize(
    ("updates", "value", "expected"),
    [
        ({"locale": "en-US", "precision": 2}, "1234.5", ("1234.50", False)),
        (
            {"locale": "en-US", "precision": 2, "grouping": True},
            "1234.5",
            ("1,234.50", False),
        ),
        (
            {"locale": "vi-VN", "precision": 2, "grouping": True},
            "1234.5",
            ("1.234,50", False),
        ),
        (
            {
                "locale": "vi-VN",
                "precision": 2,
                "grouping": True,
                "trim_trailing_zeros": True,
            },
            "1234.5",
            ("1.234,5", False),
        ),
        (
            {
                "precision": 0,
                "rounding": "half-even",
                "approximation_marker": "prefix",
            },
            "18.5",
            ("≈18", True),
        ),
        (
            {
                "precision": 0,
                "rounding": "half-up",
                "approximation_marker": "prefix",
            },
            "18.5",
            ("≈19", True),
        ),
    ],
)
def test_fixed_decimal_formatting_is_locale_independent(
    updates: dict[str, object], value: str, expected: tuple[str, bool]
) -> None:
    formatter = load_brief().number_formatters["value-a"].model_copy(
        update=updates
    )

    assert format_number(Decimal(value), formatter) == expected


@pytest.mark.parametrize("value", [Decimal("NaN"), Decimal("Infinity")])
def test_formatter_rejects_non_finite_values(value: Decimal) -> None:
    formatter = load_brief().number_formatters["value-a"]

    with pytest.raises(VisualError) as error:
        format_number(value, formatter)

    _assert_error(error, "CONTENT_PARITY_FAILED")


def test_formatter_rejects_inexact_values_and_unknown_registry_versions() -> None:
    formatter = load_brief().number_formatters["value-a"].model_copy(
        update={"precision": 0}
    )
    with pytest.raises(VisualError) as error:
        format_number(Decimal("18.5"), formatter)
    _assert_error(error, "CONTENT_PARITY_FAILED")

    formatter = formatter.model_copy(
        update={"rounding": "half-even", "approximation_marker": "none"}
    )
    with pytest.raises(VisualError) as error:
        format_number(Decimal("18.5"), formatter)
    _assert_error(error, "CONTENT_PARITY_FAILED")

    formatter = formatter.model_copy(update={"version": "1.1.0"})
    with pytest.raises(VisualError) as error:
        format_number(Decimal("18.5"), formatter)
    assert error.value.code == "CAPABILITY_UNAVAILABLE"
    assert error.value.exit_code == 3


@pytest.mark.parametrize(
    "updates",
    [
        {"precision": -1},
        {"precision": 13},
        {"precision": True},
        {"locale": "fr-FR"},
        {"rounding": "floor"},
        {"approximation_marker": "suffix"},
    ],
)
def test_formatter_rechecks_strict_configuration_at_the_runtime_boundary(
    updates: dict[str, object],
) -> None:
    formatter = load_brief().number_formatters["value-a"].model_copy(
        update=updates
    )

    with pytest.raises(VisualError) as error:
        format_number(Decimal("18.5"), formatter)

    _assert_error(error, "CONTENT_PARITY_FAILED")


def test_resolver_uses_ids_then_emits_a_read_only_canonical_pointer() -> None:
    deck = _chart_deck()
    label = resolve_binding(
        deck,
        ChartBinding(
            slide_id="s03",
            element_id="c1",
            field="chart-label",
            item_index=0,
        ),
    )
    value = resolve_binding(
        deck,
        ChartBinding(
            slide_id="s03",
            element_id="c1",
            field="chart-value",
            item_index=0,
        ),
    )
    unit = resolve_binding(
        deck,
        ChartBinding(slide_id="s03", element_id="c1", field="chart-unit"),
    )
    display_unit = resolve_binding(
        deck,
        ChartBinding(slide_id="s03", element_id="c1", field="display-unit"),
    )

    assert label.pointer == "/slides/s03/elements/c1/content/data/0/label"
    assert label.scalar == "Nhóm A"
    assert label.source_ref == "measurement-source"
    assert value.pointer == "/slides/s03/elements/c1/content/data/0/value"
    assert value.scalar == Decimal("18.5")
    assert value.source_ref == "measurement-source"
    assert unit.pointer == "/slides/s03/elements/c1/content/unit"
    assert display_unit.pointer == unit.pointer
    assert display_unit.scalar == "điểm"


def test_resolver_normalizes_text_but_never_uses_display_text_as_fact_value() -> None:
    deck = _chart_deck()
    chart = deck.slides[0].elements[0]
    assert chart.kind == "chart"
    chart.content.data[0].label = unicodedata.normalize("NFD", "Nhóm A")

    resolved = resolve_binding(
        deck,
        ChartBinding(
            slide_id="s03",
            element_id="c1",
            field="chart-label",
            item_index=0,
        ),
    )

    assert resolved.scalar == "Nhóm A"
    assert unicodedata.is_normalized("NFC", resolved.scalar)


def test_resolver_rejects_ambiguous_element_ids() -> None:
    deck = _chart_deck()
    deck.slides[0].elements.append(deck.slides[0].elements[0].model_copy(deep=True))

    with pytest.raises(VisualError) as error:
        resolve_binding(
            deck,
            ChartBinding(
                slide_id="s03",
                element_id="c1",
                field="chart-value",
                item_index=0,
            ),
        )

    _assert_error(error, "CONTENT_PARITY_FAILED")


def test_resolver_rejects_ambiguous_slide_ids() -> None:
    deck = _chart_deck()
    deck.slides.append(deck.slides[0].model_copy(deep=True))

    with pytest.raises(VisualError) as error:
        resolve_binding(deck, ContentBinding(slide_id="s03", field="slide-title"))

    _assert_error(error, "CONTENT_PARITY_FAILED")


def test_resolver_dispatches_non_chart_allowlist_without_jsonpath() -> None:
    deck = DeckSpec.model_validate(
        {
            "schema_version": "1.0",
            "title": "Deck",
            "audience": "Audience",
            "purpose": "Purpose",
            "canvas": {"ratio": "16:9"},
            "sources": [{"id": "source", "title": "Source"}],
            "slides": [
                {
                    "slide_id": "s01",
                    "title": "Title",
                    "message": None,
                    "layout_ref": "layout",
                    "notes": None,
                    "source_refs": ["source"],
                    "elements": [
                        {
                            "element_id": "plain",
                            "kind": "text",
                            "content": "Plain text",
                        },
                        {
                            "element_id": "rich",
                            "kind": "text",
                            "content": {
                                "text": "Body",
                                "label": "Label",
                                "items": ["First", "Second"],
                            },
                        },
                        {
                            "element_id": "process",
                            "kind": "process",
                            "content": {
                                "steps": [
                                    {
                                        "id": "step-a",
                                        "title": "Step title",
                                        "description": "Step body",
                                    }
                                ]
                            },
                        },
                        {
                            "element_id": "table",
                            "kind": "table",
                            "content": {
                                "columns": ["Label", "Value"],
                                "rows": [["A", 18.5]],
                            },
                        },
                        {
                            "element_id": "quote",
                            "kind": "quote",
                            "content": {"quote": "Quoted"},
                        },
                        {
                            "element_id": "code",
                            "kind": "code",
                            "content": {"code": "print(1)"},
                        },
                        {
                            "element_id": "image",
                            "kind": "image",
                            "content": {"asset_ref": "asset-a"},
                            "alt_text": "Image alt",
                        },
                    ],
                }
            ],
        }
    )
    cases = [
        (ContentBinding(slide_id="s01", field="slide-title"), "Title"),
        (ContentBinding(slide_id="s01", field="slide-message"), None),
        (ContentBinding(slide_id="s01", field="deck-audience"), "Audience"),
        (ContentBinding(slide_id="s01", field="deck-purpose"), "Purpose"),
        (
            ContentBinding(
                slide_id="s01", element_id="plain", field="text-content"
            ),
            "Plain text",
        ),
        (
            ContentBinding(
                slide_id="s01", element_id="rich", field="text-label"
            ),
            "Label",
        ),
        (
            ContentBinding(
                slide_id="s01",
                element_id="rich",
                field="text-item",
                item_index=1,
            ),
            "Second",
        ),
        (
            ContentBinding(
                slide_id="s01",
                element_id="process",
                field="process-title",
                item_id="step-a",
            ),
            "Step title",
        ),
        (
            ContentBinding(
                slide_id="s01",
                element_id="process",
                field="process-description",
                item_id="step-a",
            ),
            "Step body",
        ),
        (
            ContentBinding(
                slide_id="s01",
                element_id="table",
                field="table-cell",
                item_id="col-1",
                item_index=0,
            ),
            Decimal("18.5"),
        ),
        (
            ContentBinding(
                slide_id="s01", element_id="quote", field="quote-text"
            ),
            "Quoted",
        ),
        (
            ContentBinding(slide_id="s01", element_id="code", field="code-text"),
            "print(1)",
        ),
        (
            ContentBinding(
                slide_id="s01", element_id="image", field="image-content"
            ),
            "asset-a",
        ),
        (
            ContentBinding(
                slide_id="s01", element_id="image", field="image-alt"
            ),
            "Image alt",
        ),
        (ContentBinding(slide_id="s01", field="slide-notes"), ""),
    ]

    assert [resolve_binding(deck, binding).scalar for binding, _ in cases] == [
        expected for _, expected in cases
    ]


def test_content_projection_is_a_strict_one_slide_allowlist() -> None:
    deck = _chart_deck()
    deck.sources[0].uri = "private/source/path.csv"
    deck.sources[0].sha256 = "a" * 64
    deck.slides[0].html_ref = "source/index.html"
    deck.slides[0].layout_ref = "changed-layout"

    projection = content_projection(deck, "s03")

    assert projection["projection_version"] == "1.0"
    assert projection["deck"] == {
        "title": "Biểu đồ chất lượng",
        "audience": "Nhóm vận hành",
        "purpose": "Đối chiếu số đo",
    }
    assert projection["slide"]["slide_id"] == "s03"
    assert projection["slide"]["elements"][0]["content"]["data"][0] == {
        "label": "Nhóm A",
        "value": "18.5",
    }
    assert [node["id"] for node in projection["slide"]["visual_semantics"]["nodes"]] == [
        "chart-a",
        "label-a",
        "unit",
        "value-a",
    ]
    assert [
        relation["id"]
        for relation in projection["slide"]["visual_semantics"]["relations"]
    ] == ["contains-label", "contains-unit", "contains-value"]
    assert projection["slide"]["visual_semantics"]["reading_order"] == [
        "label-a",
        "value-a",
        "unit",
    ]
    assert projection["sources"] == [
        {
            "id": "measurement-source",
            "kind": "synthetic",
            "title": "Nguồn số đo trung tính",
            "sha256": "a" * 64,
        }
    ]
    serialized = json.dumps(projection, ensure_ascii=False)
    assert "layout_ref" not in serialized
    assert "html_ref" not in serialized
    assert "private/source/path.csv" not in serialized


def test_projection_sorts_sets_but_preserves_semantic_reading_order() -> None:
    baseline = _chart_deck()
    reordered = _chart_deck()
    semantics = reordered.slides[0].visual_semantics
    assert semantics is not None
    semantics.nodes.reverse()
    semantics.relations.reverse()

    assert content_projection(reordered, "s03") == content_projection(
        baseline, "s03"
    )

    semantics.reading_order.reverse()
    assert content_projection(reordered, "s03") != content_projection(
        baseline, "s03"
    )


def test_projection_excludes_unselected_slides_and_unused_sources() -> None:
    payload = fixture_json("deck-chart-1.1")
    payload["sources"].append(
        {
            "id": "unused-source",
            "kind": "synthetic",
            "title": "UNSELECTED SOURCE",
            "sha256": "f" * 64,
        }
    )
    for index in range(4):
        payload["slides"].append(
            {
                "slide_id": f"x{index + 1:02d}",
                "title": f"UNSELECTED SLIDE {index + 1}",
                "message": None,
                "layout_ref": "private-layout",
                "elements": [],
                "notes": "UNSELECTED NOTES",
                "source_refs": ["unused-source"],
                "visual_semantics": None,
            }
        )
    deck = DeckSpec.model_validate(payload)

    projection = content_projection(deck, "s03")

    assert len(deck.slides) == 5
    assert "UNSELECTED" not in json.dumps(projection)
    assert [source["id"] for source in projection["sources"]] == [
        "measurement-source"
    ]


def test_projection_rejects_ambiguous_used_source_ids() -> None:
    deck = _chart_deck()
    deck.sources.append(deck.sources[0].model_copy(deep=True))

    with pytest.raises(VisualError) as error:
        content_projection(deck, "s03")

    _assert_error(error, "CONTENT_PARITY_FAILED")


def test_project_brief_copies_canonical_content_and_preserves_design() -> None:
    deck = _chart_deck()
    template = load_brief()
    original_template = template.model_dump(mode="json")

    projected = project_brief(deck, template, RAW_DECK_HASH)

    assert projected is not template
    assert template.model_dump(mode="json") == original_template
    assert projected.deck_binding.deck_raw_sha256 == RAW_DECK_HASH
    assert projected.deck_binding.slide_content_hash == hash_inputs(
        content_projection(deck, "s03")
    )
    assert projected.purpose == deck.purpose
    assert projected.audience == deck.audience
    assert projected.message == deck.slides[0].message
    assert _node(projected, "label-a").text == "Nhóm A"
    assert _node(projected, "value-a").text == "18,5"
    assert _node(projected, "value-a").facts[0].value == "18.5"
    assert _node(projected, "unit").text == "điểm"
    assert _node(projected, "chart-a").preferred_box == _node(
        template, "chart-a"
    ).preferred_box
    assert projected.accessibility.notes == deck.slides[0].notes
    assert "18.5" in projected.accessibility.transcript
    assert_content_parity(deck, projected)


def test_project_brief_revalidates_the_supplied_raw_hash() -> None:
    with pytest.raises(VisualError) as error:
        project_brief(_chart_deck(), load_brief(), "not-a-sha256")

    _assert_error(error, "CONTENT_PARITY_FAILED")


def test_reprojection_uses_new_canonical_reading_order_in_transcript() -> None:
    deck = _chart_deck()
    semantics = deck.slides[0].visual_semantics
    assert semantics is not None
    semantics.reading_order = ["unit", "value-a", "label-a"]

    projected = project_brief(deck, load_brief(), RAW_DECK_HASH)

    assert projected.reading_order == ["unit", "value-a", "label-a"]
    assert projected.accessibility.transcript.index("điểm") < (
        projected.accessibility.transcript.index("18,5")
    )
    assert projected.accessibility.transcript.index("18,5") < (
        projected.accessibility.transcript.index("Nhóm A")
    )
    assert_content_parity(deck, projected)


def test_projected_transcript_preserves_repeated_visible_text() -> None:
    deck = _chart_deck()
    _set_chart_unit(deck, "Nhóm A")

    projected = project_brief(deck, load_brief(), RAW_DECK_HASH)

    assert projected.accessibility.transcript.count("Nhóm A") == 2
    assert_content_parity(deck, projected)


def test_project_brief_normalizes_semantic_set_order() -> None:
    baseline = _chart_deck()
    reordered = _chart_deck()
    semantics = reordered.slides[0].visual_semantics
    assert semantics is not None
    semantics.nodes.reverse()
    semantics.relations.reverse()

    baseline_projection = project_brief(baseline, load_brief(), RAW_DECK_HASH)
    reordered_projection = project_brief(reordered, load_brief(), RAW_DECK_HASH)

    assert reordered_projection.model_dump(mode="json") == baseline_projection.model_dump(
        mode="json"
    )


def test_only_brief_edit_fails_and_only_canonical_edit_is_stale() -> None:
    deck = _chart_deck()
    projected = project_brief(deck, load_brief(), RAW_DECK_HASH)

    altered_brief = projected.model_copy(deep=True)
    _node(altered_brief, "value-a").text = "19,5"
    with pytest.raises(VisualError) as error:
        assert_content_parity(deck, altered_brief)
    _assert_error(error, "CONTENT_PARITY_FAILED")

    altered_deck = deck.model_copy(deep=True)
    _set_chart_value(altered_deck, 19.5, "19.5")
    with pytest.raises(VisualError) as error:
        assert_content_parity(altered_deck, projected)
    _assert_error(error, "CONTENT_PARITY_FAILED")


def test_reprojection_updates_value_fact_text_transcript_and_hash() -> None:
    deck = _chart_deck()
    before = project_brief(deck, load_brief(), RAW_DECK_HASH)
    _set_chart_value(deck, 19.5, "19.5")

    after = project_brief(deck, before, "c" * 64)

    assert _node(after, "value-a").facts[0].value == "19.5"
    assert _node(after, "value-a").text == "19,5"
    assert _node(after, "label-a").text == "Nhóm A"
    assert _node(after, "unit").text == "điểm"
    assert "19.5" in after.accessibility.transcript
    assert after.deck_binding.slide_content_hash != before.deck_binding.slide_content_hash
    assert after.deck_binding.deck_raw_sha256 == "c" * 64
    assert_content_parity(deck, after)


def test_reprojection_updates_the_single_shared_unit_owner() -> None:
    deck = _chart_deck()
    before = project_brief(deck, load_brief(), RAW_DECK_HASH)
    _set_chart_unit(deck, "lần")

    after = project_brief(deck, before, "c" * 64)

    unit = _node(after, "unit")
    assert unit.text == "lần"
    assert unit.facts[0].value == "lần"
    assert sum(
        fact.binding.field == "chart-unit"
        for node in after.nodes
        for fact in node.facts
    ) == 1
    assert "lần" in after.accessibility.transcript
    assert_content_parity(deck, after)


@pytest.mark.parametrize(
    ("updates", "expected"),
    [
        ({"locale": "en-US"}, "18.5"),
        ({"precision": 2}, "18,50"),
        ({"precision": 2, "trim_trailing_zeros": True}, "18,5"),
        ({"grouping": True}, "18,5"),
        (
            {
                "precision": 0,
                "rounding": "half-even",
                "approximation_marker": "prefix",
            },
            "≈18",
        ),
    ],
)
def test_reprojection_uses_formatter_without_rewriting_source_or_fact(
    updates: dict[str, object], expected: str
) -> None:
    deck = _chart_deck()
    template = load_brief()
    template.number_formatters["value-a"] = template.number_formatters[
        "value-a"
    ].model_copy(update=updates)

    projected = project_brief(deck, template, RAW_DECK_HASH)

    chart = deck.slides[0].elements[0]
    assert chart.kind == "chart"
    assert chart.content.data[0].value == 18.5
    assert _node(projected, "value-a").facts[0].value == "18.5"
    assert _node(projected, "value-a").text == expected
    assert "18.5" in projected.accessibility.transcript
    assert_content_parity(deck, projected)


def test_parity_rejects_a_missing_approximation_marker() -> None:
    deck = _chart_deck()
    template = load_brief()
    template.number_formatters["value-a"] = template.number_formatters[
        "value-a"
    ].model_copy(
        update={
            "precision": 0,
            "rounding": "half-up",
            "approximation_marker": "prefix",
        }
    )
    projected = project_brief(deck, template, RAW_DECK_HASH)
    _node(projected, "value-a").text = "19"

    with pytest.raises(VisualError) as error:
        assert_content_parity(deck, projected)

    _assert_error(error, "CONTENT_PARITY_FAILED")


@pytest.mark.parametrize(
    ("field", "replacement"),
    [
        ("transcript", None),
        ("alt_text", "Nhóm A đạt 999 điểm."),
    ],
)
def test_parity_rejects_accessibility_numbers_outside_canonical_projection(
    field: str,
    replacement: str | None,
) -> None:
    deck = _chart_deck()
    projected = project_brief(deck, load_brief(), RAW_DECK_HASH)
    if field == "transcript":
        projected.accessibility.transcript += " 999 điểm."
    else:
        assert replacement is not None
        projected.accessibility.alt_text = replacement

    with pytest.raises(VisualError) as error:
        assert_content_parity(deck, projected)

    _assert_error(error, "CONTENT_PARITY_FAILED")


def test_parity_rejects_a_structured_contradictory_alt_relation() -> None:
    deck = _chart_deck()
    projected = project_brief(deck, load_brief(), RAW_DECK_HASH)
    projected.accessibility.alt_text = (
        "unit contains chart-a; Nhóm A đạt 18,5 điểm."
    )

    with pytest.raises(VisualError) as error:
        assert_content_parity(deck, projected)

    _assert_error(error, "CONTENT_PARITY_FAILED")


def test_parity_rejects_a_formatter_for_an_unknown_node() -> None:
    deck = _chart_deck()
    projected = project_brief(deck, load_brief(), RAW_DECK_HASH)
    projected.number_formatters["ghost"] = projected.number_formatters[
        "value-a"
    ].model_copy()

    with pytest.raises(VisualError) as error:
        assert_content_parity(deck, projected)

    _assert_error(error, "CONTENT_PARITY_FAILED")


def test_parity_rejects_an_unreconciled_canonical_fact_conflict() -> None:
    deck = _chart_deck()
    chart = deck.slides[0].elements[0]
    assert chart.kind == "chart"
    chart.content.data[0].value = 19.5

    with pytest.raises(VisualError) as error:
        project_brief(deck, load_brief(), RAW_DECK_HASH)

    _assert_error(error, "CONTENT_PARITY_FAILED")


def test_parity_rejects_duplicate_unit_owner_source_conflict_and_null_unit() -> None:
    duplicate = _chart_deck()
    unit_node = _semantic_node(duplicate, "unit")
    unit_node.facts.append(
        unit_node.facts[0].model_copy(update={"id": "unit-fact-copy"})
    )
    with pytest.raises(VisualError) as error:
        project_brief(duplicate, load_brief(), RAW_DECK_HASH)
    _assert_error(error, "CONTENT_PARITY_FAILED")

    source_conflict = _chart_deck()
    source_conflict.sources.append(SourceRef(id="other-source", title="Other"))
    source_conflict.slides[0].source_refs.append("other-source")
    _semantic_node(source_conflict, "label-a").facts[0].source_ref = "other-source"
    with pytest.raises(VisualError) as error:
        project_brief(source_conflict, load_brief(), RAW_DECK_HASH)
    _assert_error(error, "CONTENT_PARITY_FAILED")

    null_unit = _chart_deck()
    chart = null_unit.slides[0].elements[0]
    assert chart.kind == "chart"
    chart.content.unit = None
    _semantic_node(null_unit, "unit").facts.clear()
    with pytest.raises(VisualError) as error:
        project_brief(null_unit, load_brief(), RAW_DECK_HASH)
    _assert_error(error, "CONTENT_PARITY_FAILED")


def test_parity_rejects_label_and_value_joined_from_different_data() -> None:
    deck = _chart_deck()
    chart = deck.slides[0].elements[0]
    assert chart.kind == "chart"
    chart.content.data.append(ChartDatum(label="Nhóm B", value=20.0))
    value_node = _semantic_node(deck, "value-a")
    value_node.content_binding = ChartBinding(
        slide_id="s03",
        element_id="c1",
        field="chart-value",
        item_index=1,
    )
    value_node.facts[0].binding = value_node.content_binding
    value_node.facts[0].value = "20.0"

    with pytest.raises(VisualError) as error:
        project_brief(deck, load_brief(), RAW_DECK_HASH)

    _assert_error(error, "CONTENT_PARITY_FAILED")


def test_missing_chart_source_never_invents_facts() -> None:
    deck = _chart_deck()
    chart = deck.slides[0].elements[0]
    assert chart.kind == "chart"
    chart.content.source_ref = None
    deck.slides[0].source_refs.clear()
    deck.sources.clear()
    semantics = deck.slides[0].visual_semantics
    assert semantics is not None
    for node in semantics.nodes:
        node.facts.clear()

    projected = project_brief(deck, load_brief(), RAW_DECK_HASH)

    assert all(not node.facts for node in projected.nodes)
    assert _node(projected, "value-a").text == "18,5"
    assert _node(projected, "unit").text == "điểm"
    assert_content_parity(deck, projected)


def test_rounded_node_without_fact_preserves_resolved_source_scalar() -> None:
    deck = _chart_deck()
    chart = deck.slides[0].elements[0]
    assert chart.kind == "chart"
    chart.content.source_ref = None
    deck.sources.clear()
    deck.slides[0].source_refs.clear()
    semantics = deck.slides[0].visual_semantics
    assert semantics is not None
    for node in semantics.nodes:
        node.facts.clear()
    _semantic_node(deck, "value-a").required = False
    template = load_brief()
    template.number_formatters["value-a"] = template.number_formatters[
        "value-a"
    ].model_copy(
        update={
            "precision": 0,
            "rounding": "half-even",
            "approximation_marker": "prefix",
        }
    )

    projected = project_brief(deck, template, RAW_DECK_HASH)

    value_node = _node(projected, "value-a")
    assert value_node.facts == []
    assert value_node.text == "≈18"
    assert "giá trị nguồn 18.5" in projected.accessibility.transcript
    assert_content_parity(deck, projected)

    projected.accessibility.transcript = (
        "Nhóm A; ≈18; điểm; giá trị hiển thị được làm tròn."
    )
    with pytest.raises(VisualError) as error:
        assert_content_parity(deck, projected)
    _assert_error(error, "CONTENT_PARITY_FAILED")


def test_hidden_numeric_node_does_not_require_a_display_formatter() -> None:
    deck = _chart_deck()
    value_node = _semantic_node(deck, "value-a")
    value_node.visible = False
    semantics = deck.slides[0].visual_semantics
    assert semantics is not None
    semantics.reading_order.remove("value-a")
    template_payload = fixture_json("brief-image")
    template_value = next(
        node for node in template_payload["nodes"] if node["id"] == "value-a"
    )
    template_value["visible"] = False
    template_value["text"] = None
    template_payload["reading_order"].remove("value-a")
    template_payload["number_formatters"] = {}
    template_payload["accessibility"]["transcript"] = (
        "Nhóm A; điểm; giá trị nguồn 18.5."
    )
    template = VisualAssetBrief.model_validate(template_payload)

    projected = project_brief(deck, template, RAW_DECK_HASH)

    assert _node(projected, "value-a").text is None
    assert projected.number_formatters == {}
    assert "18.5" in projected.accessibility.transcript
    assert_content_parity(deck, projected)


def _table_case() -> tuple[DeckSpec, VisualAssetBrief]:
    deck_payload = fixture_json("deck-chart-1.1")
    slide = deck_payload["slides"][0]
    slide["elements"] = [
        {
            "element_id": "t1",
            "kind": "table",
            "content": {
                "columns": ["Nhóm", "Giá trị"],
                "rows": [["Nhóm A", 18.5]],
            },
        }
    ]
    semantics = slide["visual_semantics"]
    semantics["nodes"] = semantics["nodes"][:3]
    semantics["relations"] = semantics["relations"][:2]
    semantics["reading_order"] = ["label-a", "value-a"]
    semantics["nodes"][1]["content_binding"] = {
        "slide_id": "s03",
        "element_id": "t1",
        "field": "table-cell",
        "item_id": "col-0",
        "item_index": 0,
    }
    semantics["nodes"][1]["facts"][0]["binding"] = deepcopy(
        semantics["nodes"][1]["content_binding"]
    )
    semantics["nodes"][2]["content_binding"] = {
        "slide_id": "s03",
        "element_id": "t1",
        "field": "table-cell",
        "item_id": "col-1",
        "item_index": 0,
    }
    semantics["nodes"][2]["facts"][0]["binding"] = deepcopy(
        semantics["nodes"][2]["content_binding"]
    )

    brief_payload = fixture_json("brief-image")
    brief_payload["nodes"] = brief_payload["nodes"][:3]
    brief_payload["relations"] = brief_payload["relations"][:2]
    brief_payload["reading_order"] = ["label-a", "value-a"]
    brief_payload["nodes"][1]["content_binding"] = deepcopy(
        semantics["nodes"][1]["content_binding"]
    )
    brief_payload["nodes"][1]["facts"][0]["binding"] = deepcopy(
        semantics["nodes"][1]["content_binding"]
    )
    brief_payload["nodes"][2]["content_binding"] = deepcopy(
        semantics["nodes"][2]["content_binding"]
    )
    brief_payload["nodes"][2]["facts"][0]["binding"] = deepcopy(
        semantics["nodes"][2]["content_binding"]
    )
    brief_payload["accessibility"]["transcript"] = (
        "Nhóm A; 18,5; giá trị nguồn 18.5."
    )
    brief_payload["editability"]["required_node_ids"] = ["label-a", "value-a"]

    return (
        DeckSpec.model_validate(deck_payload),
        VisualAssetBrief.model_validate(brief_payload),
    )


def _legacy_chart_case() -> tuple[DeckSpec, VisualAssetBrief]:
    deck_payload = fixture_json("deck-chart-1.1")
    deck_payload["schema_version"] = "1.0"
    deck_payload["slides"][0]["visual_semantics"] = None

    brief_payload = fixture_json("brief-image")
    brief_payload["nodes"] = brief_payload["nodes"][1:3]
    for node in brief_payload["nodes"]:
        node["parent_id"] = None
    brief_payload["relations"] = []
    brief_payload["reading_order"] = ["label-a", "value-a"]
    brief_payload["editability"]["required_node_ids"] = ["label-a", "value-a"]
    brief_payload["accessibility"]["transcript"] = (
        "Nhóm A; 18,5; giá trị nguồn 18.5."
    )

    return (
        DeckSpec.model_validate(deck_payload),
        VisualAssetBrief.model_validate(brief_payload),
    )


def test_legacy_adapter_rejects_two_node_reading_order_from_the_brief() -> None:
    deck, template = _legacy_chart_case()
    template.reading_order.reverse()
    template.accessibility.transcript = (
        "18,5; Nhóm A; giá trị nguồn 18.5."
    )
    projected = project_brief(deck, template, RAW_DECK_HASH)
    assert projected.reading_order == ["label-a", "value-a"]
    assert projected.accessibility.transcript == (
        "Nhóm A; 18,5; giá trị nguồn 18.5."
    )

    projected.reading_order.reverse()
    projected.accessibility.transcript = (
        "18,5; Nhóm A; giá trị nguồn 18.5."
    )

    with pytest.raises(VisualError) as error:
        assert_content_parity(deck, projected)

    _assert_error(error, "CONTENT_PARITY_FAILED")


def test_legacy_adapter_rejects_an_unprovable_relation_for_migration() -> None:
    deck, template = _legacy_chart_case()
    template.relations.append(
        VisualRelation(
            id="legacy-order",
            from_id="label-a",
            to_id="value-a",
            kind="sequence",
            label="tiếp theo",
            required=True,
        )
    )
    template.accessibility.transcript = (
        "Nhóm A; 18,5; tiếp theo; giá trị nguồn 18.5."
    )

    with pytest.raises(VisualError) as error:
        project_brief(deck, template, RAW_DECK_HASH)

    assert error.value.code == "MIGRATION_REQUIRED"
    assert error.value.exit_code == 2


def test_numeric_table_cells_use_the_same_formatter_contract() -> None:
    deck, template = _table_case()

    projected = project_brief(deck, template, RAW_DECK_HASH)

    assert _node(projected, "label-a").text == "Nhóm A"
    assert _node(projected, "value-a").text == "18,5"
    assert _node(projected, "value-a").facts[0].value == "18.5"
    assert_content_parity(deck, projected)


def test_numeric_table_cell_without_fact_uses_the_resolved_scalar() -> None:
    deck, template = _table_case()
    _semantic_node(deck, "value-a").facts.clear()
    _node(template, "value-a").facts.clear()

    projected = project_brief(deck, template, RAW_DECK_HASH)

    assert _node(projected, "value-a").facts == []
    assert _node(projected, "value-a").text == "18,5"
    assert_content_parity(deck, projected)


def test_table_formatter_is_rejected_when_the_resolved_cell_is_a_string() -> None:
    deck, template = _table_case()
    table = deck.slides[0].elements[0]
    assert table.kind == "table"
    table.content.rows[0][1] = "18.5"
    _semantic_node(deck, "value-a").facts.clear()
    _node(template, "value-a").facts.clear()

    with pytest.raises(VisualError) as error:
        project_brief(deck, template, RAW_DECK_HASH)

    _assert_error(error, "CONTENT_PARITY_FAILED")


def test_build_projection_deep_copies_only_the_selected_original_slide() -> None:
    payload = fixture_json("deck-chart-1.1")
    payload["sources"].append(
        {"id": "unused-source", "kind": "synthetic", "title": "Unused"}
    )
    for index in range(4):
        payload["slides"].append(
            {
                "slide_id": f"x{index + 1:02d}",
                "title": f"Slide {index + 1}",
                "message": None,
                "layout_ref": "layout",
                "elements": [],
                "notes": None,
                "source_refs": ["unused-source"],
                "visual_semantics": None,
            }
        )
    deck = DeckSpec.model_validate(payload)
    brief = project_brief(deck, load_brief(), RAW_DECK_HASH)

    projected = project_build_deck(deck, brief)

    assert [slide.slide_id for slide in projected.slides] == ["s03"]
    assert [source.id for source in projected.sources] == ["measurement-source"]
    assert projected.canvas.ratio == "custom"
    assert projected.canvas.width == 1920
    assert projected.canvas.height == 1080
    assert projected.canvas.unit == "px"
    assert projected.title == deck.title
    assert projected.audience == deck.audience
    assert projected.purpose == deck.purpose
    assert len(deck.slides) == 5
    assert deck.canvas.ratio == "16:9"
    assert projected.slides[0] is not deck.slides[0]
    projected.slides[0].title = "Changed only in build input"
    assert deck.slides[0].title == "Điểm theo nhóm"


def test_build_projection_never_serializes_the_whole_source_deck() -> None:
    class GuardedDeck(DeckSpec):
        def model_dump(self, *args, **kwargs):  # type: ignore[no-untyped-def]
            raise AssertionError("whole-deck serialization exposed unselected slides")

    source = _chart_deck()
    brief = project_brief(source, load_brief(), RAW_DECK_HASH)
    guarded = GuardedDeck.model_validate(source.model_dump(mode="python"))

    projected = project_build_deck(guarded, brief)

    assert [slide.slide_id for slide in projected.slides] == ["s03"]

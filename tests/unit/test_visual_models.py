from __future__ import annotations

from copy import deepcopy
import json

import pytest
from pydantic import ValidationError

from presentation_studio.models import (
    AssetManifest,
    ChartBinding,
    ContentBinding,
    DeckSpec,
    ProfileLock,
    VisualAssetBrief,
    VisualError,
    VisualSemantics,
    serialize_deck,
)
from tests.fixtures.visual.core.legacy_reader import DeckSpec as OldDeck
from tests.visual_support import fixture_json, load_brief


def test_writer_10_omits_new_field() -> None:
    deck = DeckSpec.model_validate(fixture_json("deck-1.0"))

    output = serialize_deck(deck, "1.0")

    assert b"visual_semantics" not in output
    payload = json.loads(output)
    assert payload["slides"][1]["message"] is None
    OldDeck.model_validate_json(output)


def test_old_reader_rejects_even_null_new_field() -> None:
    deck = DeckSpec.model_validate(fixture_json("deck-1.0"))
    payload = json.loads(serialize_deck(deck, "1.0"))
    payload["slides"][0]["visual_semantics"] = None

    with pytest.raises(ValidationError):
        OldDeck.model_validate(payload)


def test_writer_selects_11_only_for_semantics_and_rejects_lossy_downgrade() -> None:
    deck = DeckSpec.model_validate(fixture_json("deck-chart-1.1"))

    output = serialize_deck(deck)

    assert json.loads(output)["schema_version"] == "1.1"
    assert b"visual_semantics" in output
    with pytest.raises(ValidationError):
        OldDeck.model_validate_json(output)
    with pytest.raises(VisualError) as error:
        serialize_deck(deck, "1.0")
    assert error.value.code == "LOSSY_DOWNGRADE"
    assert error.value.exit_code == 2


def test_writer_refuses_11_when_visual_semantics_are_absent() -> None:
    deck = DeckSpec.model_validate(fixture_json("deck-1.0"))

    with pytest.raises(VisualError) as error:
        serialize_deck(deck, "1.1")

    assert error.value.code == "SCHEMA_VERSION_MISMATCH"
    assert error.value.exit_code == 2


def test_writer_does_not_treat_an_empty_target_version_as_auto() -> None:
    deck = DeckSpec.model_validate(fixture_json("deck-1.0"))

    with pytest.raises(VisualError) as error:
        serialize_deck(deck, "")

    assert error.value.code == "UNSUPPORTED_SCHEMA_VERSION"
    assert error.value.exit_code == 2


def test_deck_10_rejects_non_null_visual_semantics() -> None:
    payload = fixture_json("deck-chart-1.1")
    payload["schema_version"] = "1.0"

    with pytest.raises(ValidationError):
        DeckSpec.model_validate(payload)


def test_deck_10_accepts_explicit_null_visual_semantics() -> None:
    payload = fixture_json("deck-1.0")
    payload["slides"][0]["visual_semantics"] = None

    deck = DeckSpec.model_validate(payload)

    assert deck.slides[0].visual_semantics is None


def test_content_bindings_enforce_the_dispatch_allowlist_and_chart_shape() -> None:
    label = ChartBinding(
        slide_id="s03",
        element_id="c1",
        field="chart-label",
        item_index=0,
    )
    assert label.item_index == 0

    with pytest.raises(ValidationError):
        ContentBinding(slide_id="s03", field="unknown-field")
    with pytest.raises(ValidationError):
        ChartBinding(
            slide_id="s03", element_id="c1", field="chart-value"
        )
    with pytest.raises(ValidationError):
        ChartBinding(
            slide_id="s03",
            element_id="c1",
            field="chart-unit",
            item_index=0,
        )
    with pytest.raises(ValidationError):
        ChartBinding(
            slide_id="s03",
            element_id="c1",
            field="chart-label",
            item_index="0",
        )


def test_chart_fixture_has_typed_label_value_unit_and_one_fact_owner() -> None:
    deck = DeckSpec.model_validate(fixture_json("deck-chart-1.1"))
    semantics = deck.slides[0].visual_semantics
    assert semantics is not None

    nodes = {node.id: node for node in semantics.nodes}
    assert isinstance(nodes["label-a"].content_binding, ChartBinding)
    assert isinstance(nodes["value-a"].content_binding, ChartBinding)
    assert isinstance(nodes["unit"].content_binding, ChartBinding)
    assert nodes["value-a"].facts[0].value == "18.5"
    assert nodes["unit"].facts[0].binding.field == "chart-unit"
    assert sum(len(node.facts) for node in semantics.nodes) == 3


def test_graph_rejects_unknown_ids_contains_mismatch_and_parent_cycles() -> None:
    baseline = fixture_json("deck-chart-1.1")["slides"][0]["visual_semantics"]

    unknown = deepcopy(baseline)
    unknown["relations"][0]["to_id"] = "missing"
    with pytest.raises(ValidationError):
        VisualSemantics.model_validate(unknown)

    mismatch = deepcopy(baseline)
    mismatch["relations"][0]["from_id"] = "label-a"
    with pytest.raises(ValidationError):
        VisualSemantics.model_validate(mismatch)

    cycle = deepcopy(baseline)
    cycle["nodes"][0]["parent_id"] = "label-a"
    cycle["relations"].append(
        {
            "id": "contains-back",
            "from_id": "label-a",
            "to_id": "chart-a",
            "kind": "contains",
            "label": None,
            "required": True,
        }
    )
    with pytest.raises(ValidationError):
        VisualSemantics.model_validate(cycle)


def test_graph_allows_semantic_cycle_relations_but_not_duplicate_fact_pointers() -> None:
    baseline = fixture_json("deck-chart-1.1")["slides"][0]["visual_semantics"]
    graph_cycle = deepcopy(baseline)
    graph_cycle["relations"].append(
        {
            "id": "feedback-loop",
            "from_id": "label-a",
            "to_id": "value-a",
            "kind": "cycle",
            "label": "phản hồi",
            "required": True,
        }
    )
    VisualSemantics.model_validate(graph_cycle)

    duplicate = deepcopy(baseline)
    copied_fact = deepcopy(duplicate["nodes"][2]["facts"][0])
    copied_fact["id"] = "unit-fact-copy"
    duplicate["nodes"][1]["facts"].append(copied_fact)
    with pytest.raises(ValidationError):
        VisualSemantics.model_validate(duplicate)


def test_semantic_node_binding_is_reserved_for_group_and_shape_decoration() -> None:
    wrong_kind = fixture_json("deck-chart-1.1")["slides"][0]["visual_semantics"]
    wrong_kind["nodes"][0]["kind"] = "text"
    with pytest.raises(ValidationError):
        VisualSemantics.model_validate(wrong_kind)

    wrong_binding = fixture_json("deck-chart-1.1")["slides"][0]["visual_semantics"]
    wrong_binding["nodes"][0]["content_binding"] = {
        "slide_id": "s03",
        "element_id": None,
        "field": "slide-title",
        "item_id": None,
        "item_index": None,
    }
    with pytest.raises(ValidationError):
        VisualSemantics.model_validate(wrong_binding)

    wrong_self_binding = fixture_json("deck-chart-1.1")["slides"][0][
        "visual_semantics"
    ]
    wrong_self_binding["nodes"][0]["content_binding"]["item_id"] = "label-a"
    with pytest.raises(ValidationError):
        VisualSemantics.model_validate(wrong_self_binding)


@pytest.mark.parametrize("kind", ["group", "shape"])
def test_decorative_group_and_shape_nodes_cannot_carry_text(kind: str) -> None:
    payload = fixture_json("brief-image")
    decoration = payload["nodes"][0]
    decoration["kind"] = kind
    decoration["visible"] = True
    decoration["text"] = "Trang trí"
    payload["reading_order"].insert(0, decoration["id"])
    payload["accessibility"]["transcript"] = (
        "Trang trí; " + payload["accessibility"]["transcript"]
    )

    with pytest.raises(ValidationError):
        VisualAssetBrief.model_validate(payload)


def test_visual_brief_fixtures_and_supporting_contracts_are_strict() -> None:
    image = load_brief()
    html = load_brief("HTML-RECONSTRUCTION")
    ProfileLock.model_validate(fixture_json("profile-lock"))
    AssetManifest.model_validate(fixture_json("asset-manifest"))

    assert image.mode == "IMAGE"
    assert html.mode == "HTML-RECONSTRUCTION"
    assert image.canvas.width_px == 1920
    assert image.canvas.height_px == 1080
    assert image.canvas.safe_area.top == 0.05

    unknown = fixture_json("brief-image")
    unknown["style"]["surprise"] = True
    with pytest.raises(ValidationError):
        VisualAssetBrief.model_validate(unknown)


def test_brief_rejects_unknown_reading_order_id_and_none_with_visible_text() -> None:
    unknown_id = fixture_json("brief-image")
    unknown_id["reading_order"].append("missing")
    with pytest.raises(ValidationError):
        VisualAssetBrief.model_validate(unknown_id)

    none_with_text = fixture_json("brief-image")
    none_with_text["text_policy"] = "none"
    none_with_text["accessibility"]["transcript"] = ""
    none_with_text["number_formatters"] = {}
    with pytest.raises(ValidationError):
        VisualAssetBrief.model_validate(none_with_text)


def test_no_text_brief_is_valid_when_visible_text_and_transcript_are_absent() -> None:
    payload = fixture_json("brief-image")
    payload["text_policy"] = "none"
    payload["number_formatters"] = {}
    payload["accessibility"]["transcript"] = ""
    for node in payload["nodes"]:
        node["text"] = None
    for relation in payload["relations"]:
        relation["label"] = None

    VisualAssetBrief.model_validate(payload)


def test_transcript_preserves_visible_text_order_from_reading_order() -> None:
    payload = fixture_json("brief-image")
    payload["accessibility"]["transcript"] = (
        "điểm; 18,5; Nhóm A; giá trị nguồn 18.5."
    )

    with pytest.raises(ValidationError):
        VisualAssetBrief.model_validate(payload)


def test_brief_rejects_reconstruction_baked_and_overlay_without_source() -> None:
    baked = fixture_json("brief-html")
    baked["text_policy"] = "baked"
    with pytest.raises(ValidationError):
        VisualAssetBrief.model_validate(baked)

    no_source = fixture_json("brief-image")
    no_source["deliverables"] = ["png"]
    with pytest.raises(ValidationError):
        VisualAssetBrief.model_validate(no_source)


def test_brief_rejects_incomplete_motion_and_unapproved_crop() -> None:
    motion = fixture_json("brief-image")
    motion["motion"] = {
        "enabled": True,
        "adapter": "hyperframes",
        "duration_seconds": None,
        "fps": 24,
    }
    motion["deliverables"].append("motion-video")
    with pytest.raises(ValidationError):
        VisualAssetBrief.model_validate(motion)

    crop = fixture_json("brief-image")
    crop["fit_policy"] = "crop-approved"
    crop["crop"] = {
        "reference_asset_id": "reference-main",
        "x": 0.1,
        "y": 0.1,
        "width": 0.8,
        "height": 0.8,
    }
    crop["approval"] = None
    with pytest.raises(ValidationError):
        VisualAssetBrief.model_validate(crop)


def test_brief_rejects_oversized_canvas_and_invalid_execution_policy() -> None:
    oversized = fixture_json("brief-image")
    oversized["canvas"]["width_px"] = 8192
    oversized["canvas"]["height_px"] = 8192
    with pytest.raises(ValidationError):
        VisualAssetBrief.model_validate(oversized)

    generation_without_budget = fixture_json("brief-image")
    generation_without_budget["execution"].update(
        {
            "network": "provider-only",
            "image_source": "generate",
            "import_asset_id": None,
            "provider_id": "provider",
            "model_id": "model",
            "max_provider_calls": 1,
            "accounting_mode": "monetary",
            "budget_amount": "0",
            "currency": "USD",
            "grant_ref": "grants/image.json",
        }
    )
    with pytest.raises(ValidationError):
        VisualAssetBrief.model_validate(generation_without_budget)


def test_brief_requires_exact_formatter_keys_for_visible_numeric_nodes() -> None:
    missing = fixture_json("brief-image")
    missing["number_formatters"] = {}
    with pytest.raises(ValidationError):
        VisualAssetBrief.model_validate(missing)

    extra = fixture_json("brief-image")
    extra["number_formatters"]["label-a"] = deepcopy(
        extra["number_formatters"]["value-a"]
    )
    with pytest.raises(ValidationError):
        VisualAssetBrief.model_validate(extra)


def test_table_cell_formatter_is_required_only_for_numeric_canonical_values() -> None:
    string_cell = fixture_json("brief-image")
    value_node = next(node for node in string_cell["nodes"] if node["id"] == "value-a")
    value_node["content_binding"] = {
        "slide_id": "s03",
        "element_id": "t1",
        "field": "table-cell",
        "item_id": "col-0",
        "item_index": 0,
    }
    value_node["facts"][0]["binding"] = deepcopy(value_node["content_binding"])
    value_node["facts"][0]["value_type"] = "string"
    value_node["facts"][0]["value"] = "Tên nhóm"
    value_node["text"] = "Tên nhóm"
    string_cell["accessibility"]["transcript"] = (
        "Nhóm A; Tên nhóm; điểm."
    )
    string_cell["number_formatters"] = {}

    VisualAssetBrief.model_validate(string_cell)

    decimal_cell = deepcopy(string_cell)
    decimal_cell["nodes"][2]["facts"][0]["value_type"] = "decimal"
    decimal_cell["nodes"][2]["facts"][0]["value"] = "18.5"
    decimal_cell["nodes"][2]["text"] = "18,5"
    decimal_cell["accessibility"]["transcript"] = (
        "Nhóm A; 18,5; giá trị nguồn 18.5; điểm."
    )
    with pytest.raises(ValidationError):
        VisualAssetBrief.model_validate(decimal_cell)

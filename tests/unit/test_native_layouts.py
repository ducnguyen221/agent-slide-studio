import pytest

from presentation_studio.layout.native import preflight_deck
from presentation_studio.models import DeckSpec


def _deck(*, layout_ref: str = "builtin:content@1.0.0", elements: list[dict] | None = None) -> DeckSpec:
    return DeckSpec(
        title="Bộ trình bày kiểm thử",
        audience="Nhóm vận hành",
        purpose="Nghiệm thu native",
        slides=[
            {
                "slide_id": "s01",
                "title": "Một thông điệp rõ ràng",
                "layout_ref": layout_ref,
                "elements": elements or [],
            }
        ],
    )


def test_unknown_layout_is_rejected_instead_of_falling_back() -> None:
    issues = preflight_deck(_deck(layout_ref="builtin:unknown@1.0.0"))

    assert [(issue.code, issue.slide_id) for issue in issues] == [
        ("UNSUPPORTED_LAYOUT", "s01")
    ]
    assert "không được hỗ trợ" in issues[0].message_vi


def test_unsupported_element_is_reported_with_exact_location() -> None:
    issues = preflight_deck(
        _deck(
            elements=[
                {
                    "element_id": "e-image",
                    "kind": "image",
                    "content": {"uri": "assets/hero.png"},
                    "alt_text": "Minh họa trung tính",
                }
            ]
        )
    )

    assert [(issue.code, issue.slide_id, issue.element_id) for issue in issues] == [
        ("UNSUPPORTED_ELEMENT", "s01", "e-image")
    ]


def test_process_over_capacity_reports_count_without_truncating() -> None:
    steps = [
        {"id": f"buoc-{index}", "title": f"Bước {index}", "description": "Mô tả"}
        for index in range(1, 6)
    ]
    issues = preflight_deck(
        _deck(
            layout_ref="builtin:process@1.0.0",
            elements=[
                {
                    "element_id": "e-process",
                    "kind": "process",
                    "content": {"steps": steps, "connector": "sequence"},
                }
            ],
        )
    )

    assert len(issues) == 1
    issue = issues[0]
    assert (issue.code, issue.element_id, issue.actual, issue.capacity) == (
        "CAPACITY_OVERFLOW",
        "e-process",
        5,
        4,
    )
    assert issue.suggested_action_vi == "Chia nội dung sang slide khác hoặc chọn bố cục có sức chứa lớn hơn."


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("title", "Tiêu đề rất dài " * 24),
        ("message", "Thông điệp phụ phải được giữ nguyên và không được cắt. " * 18),
        ("body", "Nội dung tiếng Việt cần giữ nguyên và không được cắt. " * 38),
    ],
)
def test_long_text_returns_structured_overflow_issue(field: str, value: str) -> None:
    slide = {
        "slide_id": "s01",
        "title": value if field == "title" else "Tiêu đề",
        "message": value if field == "message" else None,
        "layout_ref": "builtin:content@1.0.0",
        "elements": []
        if field == "title"
        else [{"element_id": "e-body", "kind": "text", "content": value}],
    }
    deck = DeckSpec(
        title="Bộ trình bày kiểm thử",
        audience="Nhóm vận hành",
        purpose="Nghiệm thu native",
        slides=[slide],
    )

    issues = preflight_deck(deck)

    assert len(issues) == 1
    assert issues[0].code == "TEXT_OVERFLOW"
    assert issues[0].slide_id == "s01"
    assert issues[0].element_id == ("e-body" if field == "body" else None)


def test_allocated_geometry_rejects_four_eight_line_text_blocks() -> None:
    eight_lines = "\n".join(f"Dòng {index}" for index in range(1, 9))
    deck = _deck(
        elements=[
            {"element_id": f"e-{index}", "kind": "text", "content": eight_lines}
            for index in range(1, 5)
        ]
    )

    issues = preflight_deck(deck)

    assert [issue.element_id for issue in issues if issue.code == "TEXT_OVERFLOW"] == [
        "e-1",
        "e-2",
        "e-3",
        "e-4",
    ]
    assert all(issue.capacity is not None for issue in issues)


def test_aptos_near_boundary_seventeen_lines_are_rejected_conservatively() -> None:
    seventeen_lines = "\n".join(f"Dòng {index}" for index in range(1, 18))
    issues = preflight_deck(
        _deck(
            elements=[
                {
                    "element_id": "e-boundary",
                    "kind": "text",
                    "content": seventeen_lines,
                }
            ]
        )
    )

    assert [
        (issue.code, issue.element_id) for issue in issues
    ] == [("TEXT_OVERFLOW", "e-boundary")]


@pytest.mark.parametrize(
    ("case", "slide", "expected_element", "message_fragment"),
    [
        (
            "title",
            {
                "slide_id": "s01",
                "title": "Tiêu đề vừa phải nhưng không thể nằm trên canvas rất hẹp",
                "layout_ref": "builtin:content@1.0.0",
            },
            None,
            "Tiêu đề",
        ),
        (
            "message",
            {
                "slide_id": "s01",
                "title": "Tiêu đề",
                "message": "Thông điệp này phải được đo theo đúng chiều rộng và chiều cao thực tế",
                "layout_ref": "builtin:content@1.0.0",
            },
            None,
            "Thông điệp",
        ),
        (
            "metric",
            {
                "slide_id": "s01",
                "title": "Tiêu đề",
                "layout_ref": "builtin:content@1.0.0",
                "elements": [
                    {
                        "element_id": "e-metric",
                        "kind": "text",
                        "role": "metric",
                        "content": "123456789 123456789 123456789",
                    },
                    {"element_id": "e-2", "kind": "text", "content": "Ngắn"},
                    {"element_id": "e-3", "kind": "text", "content": "Ngắn"},
                    {"element_id": "e-4", "kind": "text", "content": "Ngắn"},
                ],
            },
            "e-metric",
            None,
        ),
        (
            "process",
            {
                "slide_id": "s01",
                "title": "Tiêu đề",
                "layout_ref": "builtin:process@1.0.0",
                "elements": [
                    {
                        "element_id": "e-process",
                        "kind": "process",
                        "content": {
                            "steps": [
                                {
                                    "id": "step-1",
                                    "title": "Bước rất dài",
                                    "description": "Mô tả " * 120,
                                }
                            ]
                        },
                    }
                ],
            },
            "e-process",
            None,
        ),
        (
            "timeline",
            {
                "slide_id": "s01",
                "title": "Tiêu đề",
                "layout_ref": "builtin:timeline@1.0.0",
                "elements": [
                    {
                        "element_id": "e-timeline",
                        "kind": "timeline",
                        "content": {
                            "items": [
                                {
                                    "time_label": "2026",
                                    "title": "Mốc rất dài",
                                    "description": "Mô tả " * 120,
                                }
                            ]
                        },
                    }
                ],
            },
            "e-timeline",
            None,
        ),
        (
            "quote-attribution",
            {
                "slide_id": "s01",
                "title": "Tiêu đề",
                "layout_ref": "builtin:quote@1.0.0",
                "elements": [
                    {
                        "element_id": "e-quote",
                        "kind": "quote",
                        "content": {
                            "quote": "Một trích dẫn ngắn.",
                            "attribution": "Tên người phát biểu " * 80,
                        },
                    }
                ],
            },
            "e-quote",
            None,
        ),
        (
            "table-cell",
            {
                "slide_id": "s01",
                "title": "Tiêu đề",
                "layout_ref": "builtin:data@1.0.0",
                "elements": [
                    {
                        "element_id": "e-table",
                        "kind": "table",
                        "content": {
                            "columns": ["Cột A", "Cột B"],
                            "rows": [["Ô dữ liệu " * 100, "Ngắn"]],
                        },
                    }
                ],
            },
            "e-table",
            None,
        ),
        (
            "chart-label-details",
            {
                "slide_id": "s01",
                "title": "Tiêu đề",
                "layout_ref": "builtin:data@1.0.0",
                "elements": [
                    {
                        "element_id": "e-chart",
                        "kind": "chart",
                        "content": {
                            "chart_type": "column",
                            "data": [{"label": "Nhãn biểu đồ " * 40, "value": 1}],
                            "unit": "đơn vị diễn giải rất dài " * 20,
                            "source_ref": "source-very-long-but-valid",
                        },
                    }
                ],
            },
            "e-chart",
            None,
        ),
        (
            "source-footer",
            {
                "slide_id": "s01",
                "title": "Tiêu đề",
                "layout_ref": "builtin:content@1.0.0",
                "source_refs": [
                    "source-" + "a" * 57,
                    "source-" + "b" * 57,
                    "source-" + "c" * 57,
                    "source-" + "d" * 57,
                ],
            },
            None,
            "Nguồn",
        ),
    ],
)
def test_every_text_surface_is_fit_checked_against_allocated_geometry(
    case: str,
    slide: dict,
    expected_element: str | None,
    message_fragment: str | None,
) -> None:
    source_ids = slide.get("source_refs", [])
    deck = DeckSpec(
        title="Kiểm tra hình học",
        audience="A",
        purpose="P",
        canvas={"ratio": "custom", "width": 5, "height": 2.8125, "unit": "inch"},
        sources=[{"id": source_id, "title": source_id} for source_id in source_ids],
        slides=[slide],
    )

    issues = preflight_deck(deck)

    matching = [
        issue
        for issue in issues
        if issue.code == "TEXT_OVERFLOW"
        and issue.element_id == expected_element
        and (message_fragment is None or message_fragment in issue.message_vi)
    ]
    assert matching, case

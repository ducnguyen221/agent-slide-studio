from __future__ import annotations

from dataclasses import dataclass

from PIL import ImageFont

from presentation_studio.models import (
    Canvas,
    ChartElement,
    DeckSpec,
    ProcessElement,
    QuoteElement,
    TableElement,
    TextContent,
    TextElement,
    TimelineElement,
)


SUPPORTED_LAYOUTS: dict[str, frozenset[str]] = {
    "builtin:content@1.0.0": frozenset(
        {"chart", "process", "quote", "table", "text", "timeline"}
    ),
    "builtin:metric-and-explanation@1.0.0": frozenset({"text"}),
    "builtin:data@1.0.0": frozenset({"chart", "table", "text"}),
    "builtin:process@1.0.0": frozenset({"process", "text"}),
    "builtin:timeline@1.0.0": frozenset({"text", "timeline"}),
    "builtin:quote@1.0.0": frozenset({"quote", "text"}),
}
SUPPORTED_ELEMENTS = frozenset(
    {"chart", "process", "quote", "table", "text", "timeline"}
)
SUPPORTED_CHART_TYPES = frozenset({"bar", "column", "line", "pie"})
MAX_ELEMENTS_PER_SLIDE = 4
MAX_PROCESS_STEPS = 4
MAX_TIMELINE_ITEMS = 4
MAX_TABLE_ROWS = 12
MAX_CHART_POINTS = 8

TITLE_FONT_PT = 30.0
MESSAGE_FONT_PT = 13.0
TEXT_FONT_PT = 18.0
METRIC_FONT_PT = 30.0
SHAPE_FONT_PT = 18.0
QUOTE_FONT_PT = 24.0
TABLE_HEADER_FONT_PT = 15.0
TABLE_BODY_FONT_PT = 14.0
CHART_LABEL_FONT_PT = 10.0
CHART_DETAIL_FONT_PT = 9.0
SOURCE_FONT_PT = 8.0


@dataclass(frozen=True)
class NativeBox:
    left: float
    top: float
    width: float
    height: float


def canvas_inches(canvas: Canvas) -> tuple[float, float]:
    if canvas.ratio == "16:9":
        return 13.333333, 7.5
    if canvas.ratio == "4:3":
        return 10.0, 7.5
    assert canvas.width is not None and canvas.height is not None
    if canvas.unit == "px":
        return canvas.width / 96.0, canvas.height / 96.0
    return canvas.width, canvas.height


def title_box(canvas_width: float, canvas_height: float) -> NativeBox:
    margin = canvas_width * 0.054
    return NativeBox(
        margin,
        canvas_height * 0.0613,
        canvas_width - (2 * margin),
        canvas_height * 0.1093,
    )


def message_box(canvas_width: float, canvas_height: float) -> NativeBox:
    margin = canvas_width * 0.054
    return NativeBox(
        margin,
        canvas_height * 0.1667,
        canvas_width - (2 * margin),
        canvas_height * 0.0453,
    )


def source_box(canvas_width: float, canvas_height: float) -> NativeBox:
    margin = canvas_width * 0.054
    return NativeBox(
        margin,
        canvas_height * 0.9493,
        canvas_width - (2 * margin),
        canvas_height * 0.0293,
    )


def content_boxes(
    slide: object, canvas_width: float, canvas_height: float
) -> list[NativeBox]:
    count = max(1, len(slide.elements))
    margin = canvas_width * 0.054
    top = canvas_height * 0.2293
    width = canvas_width - (2 * margin)
    total_height = canvas_height * 0.6907
    gap = canvas_height * 0.0213
    height = (total_height - gap * (count - 1)) / count
    return [NativeBox(margin, top + index * (height + gap), width, height) for index in range(count)]


@dataclass(frozen=True)
class LayoutIssue:
    code: str
    message_vi: str
    slide_id: str
    element_id: str | None = None
    actual: int | None = None
    capacity: int | None = None
    suggested_action_vi: str = ""


def _font(font_size_pt: float) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    size_px = max(1, round(font_size_pt * 96 / 72))
    for candidate in ("aptos.ttf", "arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(candidate, size_px)
        except OSError:
            continue
    return ImageFont.load_default(size=size_px)


def _wrapped_line_count(text: str, *, font: object, width_px: float) -> int:
    if not text:
        return 0
    lines = 0
    for paragraph in text.split("\n"):
        if not paragraph:
            lines += 1
            continue
        current = ""
        for word in paragraph.split(" "):
            candidate = word if not current else f"{current} {word}"
            if font.getlength(candidate) <= width_px:
                current = candidate
                continue
            if current:
                lines += 1
                current = ""
            fragment = ""
            for character in word:
                candidate = fragment + character
                if fragment and font.getlength(candidate) > width_px:
                    lines += 1
                    fragment = character
                else:
                    fragment = candidate
            current = fragment
        if current:
            lines += 1
    return lines


def _fit_text(
    text: str,
    *,
    box: NativeBox,
    font_size_pt: float,
    horizontal_margin: float = 0.16,
    vertical_margin: float = 0.10,
) -> tuple[bool, int, int]:
    font = _font(font_size_pt)
    width_px = (box.width - 2 * horizontal_margin) * 96
    height_px = (box.height - 2 * vertical_margin) * 96
    if width_px <= 0 or height_px <= 0:
        return False, 1 if text else 0, 0
    bounds = font.getbbox("AgÁyj")
    font_size_px = font_size_pt * 96 / 72
    line_height = max(
        1.0,
        (bounds[3] - bounds[1]) * 1.08,
        font_size_px * 1.22,
    )
    actual = _wrapped_line_count(text, font=font, width_px=width_px)
    capacity = max(0, int(height_px // line_height))
    return actual <= capacity, actual, capacity


def _text_value(element: TextElement) -> str:
    if isinstance(element.content, str):
        return element.content
    content: TextContent = element.content
    parts = [part for part in (content.label, content.text) if part]
    parts.extend(content.items)
    return "\n".join(parts)


def _overflow(
    *,
    slide_id: str,
    element_id: str | None,
    actual: int,
    capacity: int,
    noun_vi: str,
) -> LayoutIssue:
    return LayoutIssue(
        code="CAPACITY_OVERFLOW",
        message_vi=f"{noun_vi} có {actual} mục, vượt sức chứa {capacity} mục của bố cục.",
        slide_id=slide_id,
        element_id=element_id,
        actual=actual,
        capacity=capacity,
        suggested_action_vi="Chia nội dung sang slide khác hoặc chọn bố cục có sức chứa lớn hơn.",
    )


def _text_overflow(
    *,
    slide_id: str,
    element_id: str | None,
    text: str,
    box: NativeBox,
    font_size_pt: float,
    surface_vi: str,
    horizontal_margin: float = 0.16,
    vertical_margin: float = 0.10,
) -> LayoutIssue | None:
    fits, actual, capacity = _fit_text(
        text,
        box=box,
        font_size_pt=font_size_pt,
        horizontal_margin=horizontal_margin,
        vertical_margin=vertical_margin,
    )
    if fits:
        return None
    return LayoutIssue(
        code="TEXT_OVERFLOW",
        message_vi=(
            f"{surface_vi} cần {actual} dòng theo font và hình học canvas, "
            f"nhưng vùng được phân bổ chỉ chứa an toàn {capacity} dòng."
        ),
        slide_id=slide_id,
        element_id=element_id,
        actual=actual,
        capacity=capacity,
        suggested_action_vi="Rút gọn hoặc chia nội dung sang slide khác; backend không tự cắt chữ.",
    )


def preflight_deck(deck: DeckSpec) -> list[LayoutIssue]:
    """Kiểm tra toàn bộ deck trước khi tạo bất kỳ artifact nào."""
    issues: list[LayoutIssue] = []
    canvas_width, canvas_height = canvas_inches(deck.canvas)
    for slide in deck.slides:
        allowed = SUPPORTED_LAYOUTS.get(slide.layout_ref)
        if allowed is None:
            issues.append(
                LayoutIssue(
                    code="UNSUPPORTED_LAYOUT",
                    message_vi=f"Bố cục không được hỗ trợ: {slide.layout_ref}",
                    slide_id=slide.slide_id,
                    suggested_action_vi="Chọn một bố cục native đã được công bố trong capability matrix.",
                )
            )
            continue

        title_issue = _text_overflow(
            slide_id=slide.slide_id,
            element_id=None,
            text=slide.title,
            box=title_box(canvas_width, canvas_height),
            font_size_pt=TITLE_FONT_PT,
            surface_vi="Tiêu đề",
            vertical_margin=0.05,
        )
        if title_issue:
            issues.append(title_issue)

        if slide.message:
            message_issue = _text_overflow(
                slide_id=slide.slide_id,
                element_id=None,
                text=slide.message,
                box=message_box(canvas_width, canvas_height),
                font_size_pt=MESSAGE_FONT_PT,
                surface_vi="Thông điệp phụ",
                vertical_margin=0.01,
            )
            if message_issue:
                issues.append(message_issue)

        source_text = "Nguồn: " + ", ".join(slide.source_refs) if slide.source_refs else ""
        if source_text:
            source_issue = _text_overflow(
                slide_id=slide.slide_id,
                element_id=None,
                text=source_text,
                box=source_box(canvas_width, canvas_height),
                font_size_pt=SOURCE_FONT_PT,
                surface_vi="Nguồn chân trang",
                vertical_margin=0.01,
            )
            if source_issue:
                issues.append(source_issue)

        if len(slide.elements) > MAX_ELEMENTS_PER_SLIDE:
            issues.append(
                _overflow(
                    slide_id=slide.slide_id,
                    element_id=None,
                    actual=len(slide.elements),
                    capacity=MAX_ELEMENTS_PER_SLIDE,
                    noun_vi="Slide",
                )
            )

        boxes = content_boxes(slide, canvas_width, canvas_height)
        for element, box in zip(slide.elements, boxes):
            if element.kind not in SUPPORTED_ELEMENTS or element.kind not in allowed:
                issues.append(
                    LayoutIssue(
                        code="UNSUPPORTED_ELEMENT",
                        message_vi=(
                            f"Phần tử {element.kind} không được hỗ trợ trong bố cục "
                            f"{slide.layout_ref}."
                        ),
                        slide_id=slide.slide_id,
                        element_id=element.element_id,
                        suggested_action_vi="Đổi loại phần tử hoặc chọn backend có capability phù hợp.",
                    )
                )
                continue

            if isinstance(element, TextElement):
                issue = _text_overflow(
                    slide_id=slide.slide_id,
                    element_id=element.element_id,
                    text=_text_value(element),
                    box=box,
                    font_size_pt=(METRIC_FONT_PT if element.role == "metric" else TEXT_FONT_PT),
                    surface_vi=("Chỉ số metric" if element.role == "metric" else "Nội dung chữ"),
                )
                if issue:
                    issues.append(issue)
            elif isinstance(element, ProcessElement) and len(element.content.steps) > MAX_PROCESS_STEPS:
                issues.append(
                    _overflow(
                        slide_id=slide.slide_id,
                        element_id=element.element_id,
                        actual=len(element.content.steps),
                        capacity=MAX_PROCESS_STEPS,
                        noun_vi="Quy trình",
                    )
                )
            elif isinstance(element, ProcessElement):
                text = "\n".join(
                    f"{index}. {step.title}"
                    + (f" — {step.description}" if step.description else "")
                    for index, step in enumerate(element.content.steps, start=1)
                )
                issue = _text_overflow(
                    slide_id=slide.slide_id,
                    element_id=element.element_id,
                    text=text,
                    box=box,
                    font_size_pt=SHAPE_FONT_PT,
                    surface_vi="Nội dung quy trình",
                )
                if issue:
                    issues.append(issue)
            elif isinstance(element, TimelineElement) and len(element.content.items) > MAX_TIMELINE_ITEMS:
                issues.append(
                    _overflow(
                        slide_id=slide.slide_id,
                        element_id=element.element_id,
                        actual=len(element.content.items),
                        capacity=MAX_TIMELINE_ITEMS,
                        noun_vi="Dòng thời gian",
                    )
                )
            elif isinstance(element, TimelineElement):
                text = "\n".join(
                    f"{item.time_label}: {item.title}"
                    + (f" — {item.description}" if item.description else "")
                    for item in element.content.items
                )
                issue = _text_overflow(
                    slide_id=slide.slide_id,
                    element_id=element.element_id,
                    text=text,
                    box=box,
                    font_size_pt=SHAPE_FONT_PT,
                    surface_vi="Nội dung dòng thời gian",
                )
                if issue:
                    issues.append(issue)
            elif isinstance(element, TableElement) and len(element.content.rows) > MAX_TABLE_ROWS:
                issues.append(
                    _overflow(
                        slide_id=slide.slide_id,
                        element_id=element.element_id,
                        actual=len(element.content.rows),
                        capacity=MAX_TABLE_ROWS,
                        noun_vi="Bảng",
                    )
                )
            elif isinstance(element, TableElement):
                row_count = len(element.content.rows) + 1
                column_count = len(element.content.columns)
                cell_box = NativeBox(
                    box.left,
                    box.top,
                    box.width / column_count,
                    box.height / row_count,
                )
                values = [element.content.columns, *element.content.rows]
                unsafe = False
                for row_index, row in enumerate(values):
                    size = TABLE_HEADER_FONT_PT if row_index == 0 else TABLE_BODY_FONT_PT
                    for value in row:
                        issue = _text_overflow(
                            slide_id=slide.slide_id,
                            element_id=element.element_id,
                            text="" if value is None else str(value),
                            box=cell_box,
                            font_size_pt=size,
                            surface_vi="Ô bảng",
                            horizontal_margin=0.08,
                            vertical_margin=0.03,
                        )
                        if issue:
                            issues.append(issue)
                            unsafe = True
                            break
                    if unsafe:
                        break
            elif isinstance(element, ChartElement):
                if element.content.chart_type not in SUPPORTED_CHART_TYPES:
                    issues.append(
                        LayoutIssue(
                            code="UNSUPPORTED_CHART_TYPE",
                            message_vi=f"Loại biểu đồ chưa được hỗ trợ: {element.content.chart_type}",
                            slide_id=slide.slide_id,
                            element_id=element.element_id,
                            suggested_action_vi="Dùng bar, column, line hoặc pie.",
                        )
                    )
                elif len(element.content.data) > MAX_CHART_POINTS:
                    issues.append(
                        _overflow(
                            slide_id=slide.slide_id,
                            element_id=element.element_id,
                            actual=len(element.content.data),
                            capacity=MAX_CHART_POINTS,
                            noun_vi="Biểu đồ",
                        )
                    )
                else:
                    point_count = len(element.content.data)
                    if element.content.chart_type == "bar":
                        label_box = NativeBox(
                            box.left,
                            box.top,
                            box.width * 0.30,
                            max(0.1, (box.height - 0.34) / point_count),
                        )
                    else:
                        label_box = NativeBox(
                            box.left,
                            box.top,
                            max(0.1, box.width / point_count),
                            min(0.42, max(0.1, box.height * 0.20)),
                        )
                    for datum in element.content.data:
                        issue = _text_overflow(
                            slide_id=slide.slide_id,
                            element_id=element.element_id,
                            text=datum.label,
                            box=label_box,
                            font_size_pt=CHART_LABEL_FONT_PT,
                            surface_vi="Nhãn biểu đồ",
                            horizontal_margin=0.01,
                            vertical_margin=0.01,
                        )
                        if issue:
                            issues.append(issue)
                            break
                    details = []
                    if element.content.unit:
                        details.append(f"Đơn vị: {element.content.unit}")
                    if element.content.source_ref:
                        details.append(f"Nguồn: {element.content.source_ref}")
                    if details:
                        detail_issue = _text_overflow(
                            slide_id=slide.slide_id,
                            element_id=element.element_id,
                            text=" · ".join(details),
                            box=NativeBox(box.left, box.top + box.height - 0.30, box.width, 0.28),
                            font_size_pt=CHART_DETAIL_FONT_PT,
                            surface_vi="Chi tiết biểu đồ",
                            horizontal_margin=0.02,
                            vertical_margin=0.01,
                        )
                        if detail_issue:
                            issues.append(detail_issue)
            elif isinstance(element, QuoteElement):
                text = f"“{element.content.quote}”"
                if element.content.attribution:
                    text += f"\n— {element.content.attribution}"
                issue = _text_overflow(
                    slide_id=slide.slide_id,
                    element_id=element.element_id,
                    text=text,
                    box=box,
                    font_size_pt=QUOTE_FONT_PT,
                    surface_vi="Trích dẫn và ghi công",
                )
                if issue:
                    issues.append(issue)
    return issues

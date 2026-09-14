from __future__ import annotations

from decimal import (
    Decimal,
    InvalidOperation,
    ROUND_HALF_EVEN,
    ROUND_HALF_UP,
    localcontext,
)

from presentation_studio.models.visual import NumberFormatter, VisualError


_FIXED_DECIMAL_VERSION = "1.0.0"


def _content_error(message: str) -> VisualError:
    return VisualError("CONTENT_PARITY_FAILED", 2, message)


def _group_integer(value: str, separator: str) -> str:
    sign = ""
    if value.startswith(("+", "-")):
        sign, value = value[0], value[1:]
    groups: list[str] = []
    while value:
        groups.append(value[-3:])
        value = value[:-3]
    return sign + separator.join(reversed(groups or ["0"]))


def format_number(
    value: Decimal, formatter: NumberFormatter
) -> tuple[str, bool]:
    """Format one canonical decimal without consulting the host locale.

    The returned boolean records a numeric value change, not the addition or
    removal of insignificant zeroes.
    """

    if (
        formatter.formatter_id != "fixed-decimal"
        or formatter.version != _FIXED_DECIMAL_VERSION
    ):
        raise VisualError(
            "CAPABILITY_UNAVAILABLE",
            3,
            (
                "Không có formatter fixed-decimal phiên bản "
                f"{formatter.version!r}; chỉ hỗ trợ {_FIXED_DECIMAL_VERSION}."
            ),
        )
    if (
        isinstance(formatter.precision, bool)
        or not isinstance(formatter.precision, int)
        or not 0 <= formatter.precision <= 12
        or formatter.locale not in {"vi-VN", "en-US"}
        or formatter.rounding not in {"reject-inexact", "half-even", "half-up"}
        or not isinstance(formatter.grouping, bool)
        or not isinstance(formatter.trim_trailing_zeros, bool)
        or formatter.approximation_marker not in {"none", "prefix"}
    ):
        raise _content_error("Cấu hình fixed-decimal không đúng registry 1.0.0.")
    if not isinstance(value, Decimal) or not value.is_finite():
        raise _content_error("Giá trị số canonical phải là Decimal hữu hạn.")

    quantum = Decimal(1).scaleb(-formatter.precision)
    rounding_mode = {
        "reject-inexact": ROUND_HALF_EVEN,
        "half-even": ROUND_HALF_EVEN,
        "half-up": ROUND_HALF_UP,
    }[formatter.rounding]
    digits = len(value.as_tuple().digits)
    required_precision = digits + max(0, value.adjusted()) + formatter.precision + 4
    try:
        with localcontext() as context:
            context.prec = max(context.prec, required_precision)
            quantized = value.quantize(quantum, rounding=rounding_mode)
    except InvalidOperation as error:
        raise _content_error("Không thể lượng tử hóa giá trị số canonical.") from error

    rounded = quantized != value
    if rounded and formatter.rounding == "reject-inexact":
        raise _content_error(
            "Formatter reject-inexact không được làm mất chữ số canonical."
        )
    if rounded and formatter.approximation_marker != "prefix":
        raise _content_error(
            "Giá trị bị làm tròn phải dùng approximation_marker=prefix."
        )

    rendered = format(quantized, f".{formatter.precision}f")
    if formatter.trim_trailing_zeros and "." in rendered:
        rendered = rendered.rstrip("0").rstrip(".")

    integer, dot, fraction = rendered.partition(".")
    thousands = "," if formatter.locale == "en-US" else "."
    decimal = "." if formatter.locale == "en-US" else ","
    if formatter.grouping:
        integer = _group_integer(integer, thousands)
    rendered = integer + (decimal + fraction if dot else "")
    if rounded:
        rendered = "≈" + rendered
    return rendered, rounded

"""OpenXML and shape enhancement helpers for python-pptx."""
import re
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt


def hex_to_rgb(hex_str: str) -> RGBColor:
    """Convert hex string '#RRGGBB' or 'RRGGBB' to pptx RGBColor."""
    clean_hex = hex_str.lstrip("#")
    if len(clean_hex) != 6:
        clean_hex = "000000"
    r = int(clean_hex[0:2], 16)
    g = int(clean_hex[2:4], 16)
    b = int(clean_hex[4:6], 16)
    return RGBColor(r, g, b)


def style_text_frame(tf, margin_inch: float = 0.15):
    """Set zero/consistent internal margins and word wrapping for a text frame."""
    tf.word_wrap = True
    tf.margin_left = Inches(margin_inch)
    tf.margin_right = Inches(margin_inch)
    tf.margin_top = Inches(margin_inch)
    tf.margin_bottom = Inches(margin_inch)

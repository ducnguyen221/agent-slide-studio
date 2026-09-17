"""WCAG 2.1 Contrast Ratio calculations for Slidecraft."""
import math
from typing import Tuple


def hex_to_relative_luminance(hex_str: str) -> float:
    """Calculate relative luminance according to WCAG 2.1 formula."""
    clean_hex = hex_str.lstrip("#")
    if len(clean_hex) != 6:
        return 0.0
    
    r = int(clean_hex[0:2], 16) / 255.0
    g = int(clean_hex[2:4], 16) / 255.0
    b = int(clean_hex[4:6], 16) / 255.0
    
    def adjust(c):
        return c / 12.92 if c <= 0.03928 else math.pow((c + 0.055) / 1.055, 2.4)
    
    r_adj = adjust(r)
    g_adj = adjust(g)
    b_adj = adjust(b)
    
    return 0.2126 * r_adj + 0.7152 * g_adj + 0.0722 * b_adj


def calculate_contrast_ratio(hex1: str, hex2: str) -> float:
    """Calculate the contrast ratio between two hex colors (1:1 to 21:1)."""
    lum1 = hex_to_relative_luminance(hex1)
    lum2 = hex_to_relative_luminance(hex2)
    
    lighter = max(lum1, lum2)
    darker = min(lum1, lum2)
    
    return (lighter + 0.05) / (darker + 0.05)


class ContrastChecker:
    """Audits color palette contrast compliance against WCAG standards."""
    
    WCAG_AA_BODY = 4.5
    WCAG_AA_LARGE = 3.0
    PROJECTOR_RECOMMENDED = 7.0
    
    @classmethod
    def audit_palette(cls, bg_hex: str, text_hex: str) -> Tuple[float, bool, str]:
        ratio = calculate_contrast_ratio(bg_hex, text_hex)
        passes_aa = ratio >= cls.WCAG_AA_BODY
        
        if ratio >= cls.PROJECTOR_RECOMMENDED:
            status = "EXCELLENT (Ideal for classroom/projector)"
        elif ratio >= cls.WCAG_AA_BODY:
            status = "GOOD (Passes WCAG AA Body)"
        elif ratio >= cls.WCAG_AA_LARGE:
            status = "WARNING (Passes only for Large Text)"
        else:
            status = "FAIL (Insufficient contrast)"
            
        return ratio, passes_aa, status

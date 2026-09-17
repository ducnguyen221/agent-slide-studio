"""Text measurement and estimation utilities for preventing overflow."""
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class TextDimension:
    estimated_lines: int
    required_height_pt: float
    is_overflow: bool


class TextMetrics:
    """Estimates text dimensions based on character width heuristics and font metrics."""
    
    # Average character width ratio relative to font size (approx 0.52 for sans-serif fonts)
    AVG_CHAR_WIDTH_RATIO = 0.50
    LINE_HEIGHT_MULTIPLIER = 1.35
    PARAGRAPH_SPACING_PT = 6.0
    
    @classmethod
    def estimate_lines(cls, text: str, font_size_pt: float, container_width_inch: float) -> int:
        """Estimate the number of wrapped lines for a text string inside a container."""
        if not text:
            return 0
        
        container_width_pt = container_width_inch * 72.0
        avg_char_width_pt = font_size_pt * cls.AVG_CHAR_WIDTH_RATIO
        max_chars_per_line = max(1, int(container_width_pt / avg_char_width_pt))
        
        paragraphs = text.split("\n")
        total_lines = 0
        
        for p in paragraphs:
            words = p.split()
            if not words:
                total_lines += 1
                continue
            
            current_line_chars = 0
            for word in words:
                word_len = len(word)
                if current_line_chars + word_len + (1 if current_line_chars > 0 else 0) <= max_chars_per_line:
                    current_line_chars += word_len + (1 if current_line_chars > 0 else 0)
                else:
                    total_lines += 1
                    current_line_chars = word_len
            
            if current_line_chars > 0:
                total_lines += 1
                
        return total_lines

    @classmethod
    def calculate_bullets_height(
        cls, 
        bullets: List[str], 
        font_size_pt: float, 
        container_width_inch: float, 
        max_height_inch: float
    ) -> TextDimension:
        """Calculate total height required for a bullet list and detect overflow."""
        total_lines = 0
        total_paragraphs = len(bullets)
        
        for b in bullets:
            lines = cls.estimate_lines(b, font_size_pt, container_width_inch)
            total_lines += lines
            
        line_height_pt = font_size_pt * cls.LINE_HEIGHT_MULTIPLIER
        total_height_pt = (total_lines * line_height_pt) + (max(0, total_paragraphs - 1) * cls.PARAGRAPH_SPACING_PT)
        max_height_pt = max_height_inch * 72.0
        
        is_overflow = total_height_pt > max_height_pt
        return TextDimension(
            estimated_lines=total_lines,
            required_height_pt=total_height_pt,
            is_overflow=is_overflow
        )

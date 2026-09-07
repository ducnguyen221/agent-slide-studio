"""Cognitive Load & Pedagogical Rule Checker for Slidecraft."""
from typing import List, Dict, Any
from slidecraft.ir.deck import DeckSchema, SlideSchema


class CognitiveAuditor:
    """Audits presentation content against Mayer's Multimedia & Cognitive Load rules."""
    
    MAX_WORDS_PER_SLIDE = 55
    MAX_BULLETS_PER_CARD = 5
    MAX_WORDS_PER_BULLET = 15
    
    @classmethod
    def audit_slide(cls, slide: SlideSchema) -> Dict[str, Any]:
        warnings = []
        info = []
        
        total_words = len(slide.title.split())
        if slide.subtitle:
            total_words += len(slide.subtitle.split())
            
        if slide.cards:
            for card in slide.cards:
                total_words += len(card.title.split())
                if len(card.points) > cls.MAX_BULLETS_PER_CARD:
                    warnings.append(f"Card '{card.title}' has {len(card.points)} bullets (recommended <= {cls.MAX_BULLETS_PER_CARD}).")
                for p in card.points:
                    w_count = len(p.split())
                    total_words += w_count
                    if w_count > cls.MAX_WORDS_PER_BULLET:
                        warnings.append(f"Bullet '{p[:25]}...' has {w_count} words (recommended <= {cls.MAX_WORDS_PER_BULLET}).")
                        
        if total_words > cls.MAX_WORDS_PER_SLIDE:
            warnings.append(f"Total slide word count is {total_words} (exceeds recommended {cls.MAX_WORDS_PER_SLIDE} words).")
        else:
            info.append(f"Slide word count: {total_words} (Optimal).")
            
        return {
            "slide_id": slide.slide_id,
            "title": slide.title,
            "total_words": total_words,
            "warnings": warnings,
            "info": info,
            "passed": len(warnings) == 0
        }

    @classmethod
    def generate_report(cls, deck: DeckSchema) -> str:
        lines = [f"# Pedagogy & Cognitive Load Audit: {deck.title}\n"]
        total_slides = len(deck.slides)
        passed_slides = 0
        
        for slide in deck.slides:
            res = cls.audit_slide(slide)
            if res["passed"]:
                passed_slides += 1
            status_emoji = "✅ PASS" if res["passed"] else "⚠️ WARN"
            lines.append(f"### {status_emoji} Slide: {res['title']} (`{res['slide_id']}`)")
            lines.append(f"- **Word Count:** {res['total_words']} words")
            if res["warnings"]:
                lines.append("- **Issues to refine:**")
                for w in res["warnings"]:
                    lines.append(f"  - {w}")
            lines.append("")
            
        lines.append(f"**Overall Health Score:** {passed_slides}/{total_slides} slides compliant ({int((passed_slides/total_slides)*100)}%)\n")
        return "\n".join(lines)

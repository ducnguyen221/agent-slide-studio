---
name: slide-craft
description: Autonomous engine to create high-quality PowerPoint lecture and infographic presentations using Native Shapes and consistent AI visuals.
---

# Slidecraft: Presentation & Infographic Creation Skill

Use this skill whenever the user requests the creation, refactoring, or optimization of slide decks, lecture materials, or infographic presentations.

## 3-Gateway Workflow

```
[User Request / Syllabus]
       │
       ▼
[GATEWAY 1: OUTLINE & PEDAGOGY REVIEW] 
  - Break raw content into 5-10 structured slides.
  - Assign Bloom verbs & clear learning objectives.
  - Present outline to user for fast confirmation.
       │
       ▼
[GATEWAY 2: CANONICAL DECK.YAML SPECIFICATION]
  - Assign layout archetype to each slide:
    * `cards_grid`: 2 to 4 structured comparison/concept cards.
    * `process_flow`: Step-by-step workflow with chevron badges.
    * `horizontal_timeline`: Milestone and phase progression.
    * `kpi_grid`: Highlighted metrics and statistics.
    * `split_content_visual`: Conceptual text on left + Style-locked AI illustration on right.
  - Write `deck.yaml` adhering strictly to cognitive chunking (<= 50 words/slide).
       │
       ▼
[GATEWAY 3: NATIVE PPTX COMPILATION & AUDIT]
  - Run CLI: `python -m slidecraft.cli.main build --deck deck.yaml --output presentation.pptx --profile academic_light`
  - Ensure 100% of shapes and text boxes are native and editable on PowerPoint.
```

## Supported Design Profiles
- `academic_light`: Clean, university lecture style with white/light gray background and cobalt/mint accents.
- `tech_dark_modern`: Dark navy background with cyan & violet neon accents for AI/Computer Science topics.

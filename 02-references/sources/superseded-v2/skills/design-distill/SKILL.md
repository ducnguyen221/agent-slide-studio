---
name: design-distill
description: Reverse engineers sample PowerPoint (.pptx) decks or Infographic images into reusable Design Profiles (themes, style DNA, declarative components).
---

# Design Distill: Reverse Engineering Skill

Use this skill when the user provides an existing PowerPoint file or infographic image and wants to save it as a reusable presentation style.

## Distillation Execution
1. Run CLI command:
   ```bash
   python -m slidecraft.cli.main distill --input ./my_sample.pptx --name "my_custom_theme"
   ```
2. The system automatically inspects slide dimensions, color palettes, fonts, and geometry.
3. A new profile directory `profiles/<name>/` is populated with `theme.yaml` and ready for use in `slidecraft build`.

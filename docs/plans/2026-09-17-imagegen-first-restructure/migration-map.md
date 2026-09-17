---
title: "Migration map — ImageGen-first restructure"
description: "Tài liệu Migration map — ImageGen-first restructure trong agent-slide-studio."
document_type: implementation-plan
status: active
---

# Migration map — ImageGen-first restructure

## Quyết định nguồn

Root v2.1 là nguồn canonical duy nhất cho L01–L48, I01–I12, taxonomy, gallery và user references. `v1/` là snapshot bất biến. `skills/slide-infographic/` chỉ là nguồn cũ để chắt lọc. Đường dẫn `slide-design/` được nêu trong spec nhưng không tồn tại trong working tree tại HEAD `c0979ab468a98c3a57b73de896abc24c9a18b583`; vì vậy không có file nào từ cây đó được giả định hoặc ánh xạ.

Các nhãn đối chiếu trong `inventory.json` có nghĩa:

- `identical`: SHA-256 bằng nhau.
- `root_newer`: root có tài liệu cùng vai trò và là bản hiện hành v2.1; nội dung hữu ích còn thiếu vẫn phải được rà trước khi bỏ nguồn cũ.
- `source_only`: nội dung chỉ có ở nguồn cũ và phải được chắt lọc hoặc lưu làm reference.
- `conflict`: hai nguồn cùng vai trò nhưng khác hợp đồng; spec là trọng tài.

## Markdown nhập vào các file canonical

| Canonical đích | Markdown nguồn phải đọc và hợp nhất |
|---|---|
| `01-design/principles.md` | `references/originals/01_tu_duy_kien_truc_slide.md`; `references/legacy/v18/REFERENCES/01_tu_duy_kien_truc_slide.md`; `agents/instructional-designer.md`; `agents/information-architect.md`; `agents/visual-director.md`; `presentations/INDEX.md`; `presentations/P01.md`; `presentations/P02.md`; `presentations/P03.md`; `presentations/P04.md`; `presentations/P05.md`; `presentations/P06.md`; `references/template_patterns.md`; `skills/slide-infographic/references/style-library/index.md`. |
| `01-design/design-system.md` | `references/design_system.md`; `references/previous_design_system.md`; `references/originals/02_thiet_ke_infographic_va_prompts.md`; `references/compact_infographic_rules.md`; `references/smartart_mapping.md`; `agents/visual-director.md`; `skills/slide-infographic/references/image.md`; `skills/slide-infographic/references/style-library/complex-process-flow.md`; `skills/slide-infographic/references/style-library/light-corporate-cards.md`; `skills/slide-infographic/references/style-library/style-card-template.md`. |
| `02-references/INDEX.md` | `archetypes/INDEX.md`; `archetypes/CATALOG.md`; `infographics/INDEX.md`; `taxonomy/README.md`; `previews/README.md`; `references/images/README.md`; `references/user-infographics/INDEX.md`; `processes/archetype_selection.md`; `processes/classified_layout_selection.md`; `processes/reference_image_usage.md`; `references/classification_migration.md`; `skills/slide-infographic/assets/style-examples/POLICY.md`; `skills/slide-infographic/workflows/distill-style-reference.md`. |
| `03-workflow/01-read-and-map.md` | `processes/intake_and_chunking.md`; `processes/archetype_selection.md`; `processes/classified_layout_selection.md`; `processes/research_and_fact_checking.md`; `agents/instructional-designer.md`; `agents/information-architect.md`; `agents/fact-checker.md`; `skills/slide-infographic/agents/slide-infographic-agent.md`; `skills/slide-infographic/workflows/create-slide-infographic.md`. |
| `03-workflow/02-lock-style-and-content.md` | `processes/content_lock_and_edit_scope.md`; `processes/vietnamese_localization.md`; `processes/reference_image_usage.md`; `agents/vietnamese-editor.md`; `agents/fact-checker.md`; `agents/visual-director.md`; `references/evidence_matrix.md`; `skills/slide-infographic/references/image.md`; `skills/slide-infographic/workflows/distill-style-reference.md`. |
| `03-workflow/03-prompt-and-imagegen.md` | `processes/infographic_prompt_generation.md`; `prompts/README.md`; `prompts/full-slide.md`; `prompts/no-text.md`; `prompts/title-reserved.md`; `prompts/edit-scope.md`; `prompts/editable-overlay.md`; `prompts/previous_examples.md`; `skills/slide-infographic/references/prompt-compiler.md`; `skills/slide-infographic/references/image.md`; `skills/slide-infographic/workflows/create-slide-infographic.md`. Spec bỏ các mode/fallback trái với direct-text ImageGen-only và giữ đúng bảy phần prompt. |
| `03-workflow/04-review-and-handoff.md` | `processes/qa_and_accessibility.md`; `processes/powerpoint_assembly.md`; `qa/design_review.md`; `qa/classification_review.md`; `qa/previous_review.md`; `qa/runtime_smoke_tests.md`; `agents/qa-reviewer.md`; `skills/slide-infographic/references/qa.md`; `skills/slide-infographic/evals/cases.md`; `skills/slide-infographic/evals/rubric.md`; `skills/slide-infographic/evals/style-fidelity-cases.md`. |
| `04-templates/deck-plan.md` | `templates/presentation_plan.md`; `templates/classified_slide_brief.md`; `templates/slide_brief.md`; `templates/project_state.md`; `templates/research_log.md`. |
| `04-templates/slide-prompt.md` | `templates/content_lock.md`; `templates/image_prompt.md`; `templates/edit_request.md`; `prompts/edit-scope.md`; `prompts/full-slide.md`; `prompts/no-text.md`; `prompts/title-reserved.md`; `prompts/editable-overlay.md`; `skills/slide-infographic/references/prompt-compiler.md`. |
| `04-templates/review-and-handoff.md` | `templates/qa_report.md`; `templates/powerpoint_handoff.md`; `qa/design_review.md`; `skills/slide-infographic/references/qa.md`; `skills/slide-infographic/evals/rubric.md`. |

Role Markdown may feed more than one destination because each destination receives a different, named concern. The implementation must remove duplicated normative paragraphs after the split.

## File-preserving moves for Task 2

| Nguồn hiện hành | Đích dự kiến | Quy tắc |
|---|---|---|
| `archetypes/L01_cover.md` … `archetypes/L48_actionplan.md`, `archetypes/registry.json` | `02-references/layouts/archetypes/` | Root v2.1 wins; preserve IDs and verify hashes before/after each move. The dedicated subfolder prevents collision with the infographic registry. |
| `infographics/I01_cycle_gate.md` … `infographics/I12_four_cards.md`, `infographics/registry.json` | `02-references/layouts/infographics/` | Root v2.1 wins; preserve IDs. The dedicated subfolder prevents collision with the archetype registry. |
| `previews/layouts/L01.{png,svg}` … `L48.{png,svg}`; `previews/infographics/I01.{png,svg}` … `I12.{png,svg}`; contact sheets, group previews and `previews/index.html` | `02-references/gallery/` | Preserve readable preview links; never overwrite unequal bytes silently. |
| `references/images/*`; `references/user-infographics/*` | `02-references/images/` | Preserve registry/contact sheets; images teach visual properties only, never facts/text. |
| `references/originals/**` | `02-references/sources/originals/` | Historical comparison only; preserve the originals namespace and keep it off the normal reading path. |
| `references/legacy/**` | `02-references/sources/legacy/` | Historical comparison only; preserve the legacy namespace and keep it off the normal reading path. |
| `taxonomy/build.json`; `taxonomy/facets.json`; `taxonomy/groups.json` | `02-references/layouts/` or reference-index support location chosen in Task 2 | Root v2.1 wins; links from the single reference index. |

## Entrypoints and non-merge files

`README.md`, `SKILL.md`, `agents/openai.yaml`, host adapters, installer scripts and package metadata are rewritten or consolidated in Tasks 3–4; they are not silently folded into the ten knowledge files above. `references/sources.md`, `references/migration.md`, `NOTICE.md` and `CHANGELOG.md` remain provenance/history inputs. QA reports under `qa/archive-v2.0/` and `qa/validation_report.md` are evidence, not normative sources.

No source was moved or edited in Task 1.

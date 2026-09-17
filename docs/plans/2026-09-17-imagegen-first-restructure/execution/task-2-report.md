---
title: "Task 2 report — compact knowledge package"
description: "Tài liệu Task 2 report — compact knowledge package trong agent-slide-studio."
document_type: execution-record
status: active
---

# Task 2 report — compact knowledge package

## Status

Implemented the Task 2 knowledge/package restructure. No commit, reset, deletion, governance edit, entrypoint edit, adapter edit, script edit, manifest edit, or `v1/**` edit was performed.

## Canonical knowledge created

- `01-design/principles.md`: slide purpose, action titles, cognitive organization, density, source discipline, deck rhythm and retained P01–P06 patterns.
- `01-design/design-system.md`: canvas/grid, font appearance, color roles, surfaces, icon/connector language, reference handling and style lock.
- `02-references/INDEX.md`: the single selection index for L01–L48 and I01–I12, with direct links to specs, full-size previews and real reference images plus explicit learn/do-not-learn scope.
- `03-workflow/01-read-and-map.md`: full-deck reading, source mapping, claim handling and layout selection.
- `03-workflow/02-lock-style-and-content.md`: brand/style/content/reference/edit locks and anchor-slide gate.
- `03-workflow/03-prompt-and-imagegen.md`: exact seven-section prompt, direct-text ImageGen-only path, native host tool use, `CAPABILITY_UNAVAILABLE` and `OUTCOME_UNKNOWN` handling.
- `03-workflow/04-review-and-handoff.md`: full-size visual QA, exact-text/topology checks, deck consistency and honest handoff.
- `04-templates/deck-plan.md`, `slide-prompt.md`, `review-and-handoff.md`: only fields consumed by the four workflows.

Normative duplication was removed by assigning each concern to one canonical file: design reasoning → principles; visual mechanics → design-system; lookup → reference INDEX; execution → four workflows; records → three templates. Legacy TEXT_SAFE/overlay/Python-renderer paths were not carried into the canonical ImageGen-first workflow.

## Sources merged

Read and distilled the migration-map inputs across:

- design/reference sources: original and legacy design-thinking docs, design systems, compact rules, SmartArt mapping, template patterns and style-library profiles;
- role sources: instructional designer, information architect, visual director, Vietnamese editor, fact checker and QA reviewer;
- deck sources: presentation INDEX and P01–P06;
- process sources: intake/chunking, layout selection, fact checking, content/edit lock, localization, reference use, prompt generation, PowerPoint and QA;
- prompt/compiler sources: root prompt examples and the legacy seven-section compiler;
- QA/eval sources: design/classification/runtime review, image QA, decision rubric and style-fidelity cases;
- template sources: presentation/slide/project/research/content/prompt/edit/QA/handoff records.

The specification was used as conflict authority where legacy modes or fallback renderers disagreed with direct-text, native ImageGen-only behavior.

## Paths moved

All moves resolved absolute source/destination paths under the repository and used PowerShell `Move-Item -LiteralPath`. Existing destinations were rejected; unequal hashes were never overwritten.

- `archetypes/L01–L48 + registry.json` → `02-references/layouts/archetypes/`
- `infographics/I01–I12 + registry.json` → `02-references/layouts/infographics/`
- taxonomy JSON → `02-references/layouts/taxonomy/`
- `previews/**` → `02-references/gallery/**`
- `references/images/**` → `02-references/images/reference-set/**`
- `references/user-infographics/**` → `02-references/images/user-infographics/**`
- `references/originals/**` → `02-references/sources/originals/**`
- `references/legacy/**` → `02-references/sources/legacy/**`
- old `agents/*.md`, `processes/**`, `prompts/**`, `templates/**`, `qa/**`, `presentations/**`, selected old reference/index Markdown and `skills/slide-infographic/**` → namespaced `02-references/sources/superseded-v2/**`
- `agents/openai.yaml` remains at its original path as required.

Moved layout Markdown, registries and gallery navigation were relinked to the new canonical paths. Empty read-only source directories may remain as filesystem shells; they contain no active competing guidance. `slide-design/` was absent and was not recreated.

## Verification

### Passed

- Canonical/new Markdown local links: `0` broken (sources/superseded excluded from active-path check).
- Active knowledge counts: design `2`, reference INDEX `1`, workflow `4`, templates `3`.
- Layout counts: `48` L specs + `48` PNG + `48` SVG; `12` I specs + `12` PNG + `12` SVG.
- Registry uniqueness: `48/48` unique L IDs and `12/12` unique I IDs.
- P IDs found: `P01, P02, P03, P04, P05, P06`.
- JSON parse: archetype registry, infographic registry, taxonomy build/facets/groups and user-reference registry all pass.
- `v1/`: `281` files, `0` missing/changed versus every hash and byte count in inventory; recorded baseline tree SHA-256 remains `9e537498a83b9167a68a98af156a8aecc44bdcc58337ecb472eef1d3dc12c8d4`.

### Existing validators currently fail pending Tasks 3–4

- `PYTHONIOENCODING=utf-8 python scripts/validate.py .` runs but fails because the unchanged validator and unchanged manifest still require old root paths (`agents/README.md`, `processes/`, `templates/`, `prompts/`, `qa/`, `archetypes/registry.json`, `previews/`) and scan superseded historical links/frontmatter as active. Updating scripts/manifest was explicitly outside Task 2 ownership.
- `python scripts/test_gallery.py .` with installed Chrome reaches the script, then fails because the unchanged script still opens `previews/index.html`. Updating that script is Task 4 scope.
- Without `PYTHONIOENCODING=utf-8`, the existing validator also hits a Windows cp1252 console encoding error before printing its result.

## Self-review

- Checked that each normative concern has one canonical home and that templates mirror workflow fields rather than re-explain rules.
- Confirmed the reference INDEX requires opening real images and recording both what to learn and what not to learn.
- Confirmed canonical generation has exactly seven prompt sections and no Python/SVG/HTML/screenshot fallback.
- Confirmed brand defaults are not silently imposed and font claims are limited to appearance unless a real editable artifact proves metadata.
- Confirmed no files under `v1/**` changed and no tracked/user changes were reverted.

## Concerns for follow-up

1. Task 3 must update `README.md`, `SKILL.md` and adapters to point only to the new canonical path; their old links are temporarily broken as explicitly allowed by the brief.
2. Task 4 must update validators, gallery test paths and manifest/SHA records to the new structure, and decide whether validators should skip `02-references/sources/superseded-v2/**`.
3. Historical superseded Markdown intentionally preserves original content and therefore may contain historical relative links that no longer resolve in-place; it is outside the normal reading path. Canonical/new active files and moved layout specs have valid links.

## Fix round after Task 2 review

### Changes

- Removed `EDITABLE_OVERLAY`, `TITLE_RESERVED` and legacy `output_modes` policy from every active L layout and both active layout registries.
- Replaced registry policy with `imagegen_policy`: `NATIVE_IMAGEGEN_DIRECT_TEXT` for slides with text and `NATIVE_IMAGEGEN_NO_TEXT` only for the dedicated no-text background layout. Taxonomy facets now state the native ImageGen-only contract and explicitly reject overlay/Python/SVG/HTML/screenshot renderer fallbacks.
- Updated all 48 L and 12 I specs so palette values are examples only when no deck style lock exists; the deck style lock overrides palette, font appearance, icon and surface. Prompt behavior now routes to `03-workflow/03-prompt-and-imagegen.md` instead of selecting a renderer mode in layout files.
- Restored P02–P06 semantics from the preserved presentation sources: process guidance, architecture/capability, change proposal, data report and workshop. A new unmatched deck thread uses `custom` rather than redefining P01–P06.
- Removed generation from workflow step 02. Step 02 now selects the anchor and locks its brief. Step 03 owns preflight, the first/only anchor generation point, anchor visual QA gate and dependent-slide generation.

### Verification

- Active canonical search excluding `02-references/sources/**` and `v1/**`: zero `EDITABLE_OVERLAY`, zero `TITLE_RESERVED`, zero legacy `output_modes`.
- JSON parse: archetype registry, infographic registry, taxonomy build/facets/groups and user-reference registry pass.
- Active links: zero broken.
- Counts remain design `2`, reference INDEX `1`, workflow `4`, templates `3`; L specs/PNG/SVG `48/48/48`; I specs/PNG/SVG `12/12/12`.
- IDs remain unique: L `48`, I `12`; P01–P06 all present.
- `v1/` remains `281` files with zero byte/hash changes versus inventory baseline `9e537498a83b9167a68a98af156a8aecc44bdcc58337ecb472eef1d3dc12c8d4`.

### L20 no-text consistency fix

- Replaced the inherited direct-text sentence in `L20_background.md` with the registry-aligned `NATIVE_IMAGEGEN_NO_TEXT` directive.
- The prompt now explicitly forbids every visible word, number, filename, textual logo, watermark, programming symbol and pseudo-character, including text-like details on objects, screens, books, labels and decoration.
- L20 still routes preflight/generation/visual QA through the canonical native ImageGen workflow and offers no renderer fallback.
- Scoped verification: L20 policy is internally consistent, active links and JSON pass, and all 281 `v1/` files remain byte/hash-identical to the inventory baseline.

### Final L20 D0 consistency fix

- Removed inherited title/body/label density guidance from L20 and made `D0` mandatory.
- L20 now permits only geometry, light, material, whitespace and non-text-bearing objects. Its prompt and checklist prohibit every visible letter, number, label, word, text-like symbol glyph, filename, textual logo, watermark, programming symbol, real character and pseudo-character with no visible-text exception.
- Preserved `NATIVE_IMAGEGEN_NO_TEXT`, purely visual layout constraints and the canonical workflow link.

### Cross-task group-preview path fix

- Updated all ten `preview` values in `02-references/layouts/taxonomy/groups.json` from the removed `previews/groups/` root to `02-references/gallery/groups/`.
- Verified every referenced G01–G08/G09A/G09B PNG exists, the JSON parses, active registry file references resolve, and `v1/` remains byte/hash-identical to the inventory baseline.

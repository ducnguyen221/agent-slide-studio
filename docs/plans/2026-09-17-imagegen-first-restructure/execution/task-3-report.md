---
title: "Task 3 report — Root entrypoint and native ImageGen adapters"
description: "Tài liệu Task 3 report — Root entrypoint and native ImageGen adapters trong agent-slide-studio."
document_type: execution-record
status: active
---

# Task 3 report — Root entrypoint and native ImageGen adapters

## Status

Task 3 implementation is complete within its file scope. Root `SKILL.md` is the only active skill entrypoint outside `v1/` and `02-references/sources/`. Static package validation remains blocked by the pre-Task-4 validator/manifest and one governance pointer that Task 3 was forbidden to edit.

## Changes

- Rewrote `README.md` around the current ImageGen-first root, with separate sections for the active package, immutable `v1/`, and optional Python validation/install/package/gallery tools.
- Rewrote `SKILL.md` as a concise router with the mandatory read order: two design files → full-deck map → L/I selection → real bundled sample images → one-round style question → seven-section prompt → native ImageGen adapter → full-image and whole-deck QA.
- Made `CONTENT` an exhaustive exact-visible-text allowlist and required every visible string to have an ID.
- Added fail-closed native host routing: `CAPABILITY_UNAVAILABLE` for missing ImageGen, `OUTCOME_UNKNOWN` for unclear completion, no invented tool/model/API names, and no Python/HTML/SVG/browser/screenshot/PPTX-overlay renderer fallback.
- Added active flat adapters `adapters/codex.md` and `adapters/antigravity.md`; reduced `adapters/README.md` to the two canonical links.
- Kept `adapters/antigravity/README.md` only as a short redirect because the unmodified governance file `GEMINI.md` still points there. It contains no independent operating rules.
- Preserved the previous nested Codex, Antigravity and Claude Code adapter material under `02-references/sources/superseded-v2/adapters/`, then removed it from the active adapter path.
- After collision-safe absolute source/destination checks, moved the pre-existing `skills/design-distill/SKILL.md` and `skills/slide-craft/SKILL.md` into `02-references/sources/superseded-v2/skills/`. No redirect was recreated, so the stale `slide-craft` policy and its link to the absent infographic skill are no longer active.
- Preserved `agents/openai.yaml` unchanged because its skill name and default prompt still resolve to the root `SKILL.md`.
- Did not recreate `slide-design/SKILL.md` or `skills/slide-infographic/SKILL.md`.

## Verification

### Router and policy assertions

Fresh assertion scan result:

```text
POLICY_ASSERTIONS=PASS
ACTIVE_SKILL_COUNT=1
ACTIVE_SKILL=SKILL.md
INVENTED_NAME_HITS=0
```

The assertions checked full-deck mapping, L/I choice, real bundled image opening, one-round user question, seven sections in exact order, exact-visible-text allowlist, fail-closed states, ImageGen edit/regenerate repair, full-image re-QA, explicit fallback bans, absence of invented product/model names, and absence of the two prohibited legacy entrypoint files.

### Links and mandatory read paths

```text
OWNED_LINKS=PASS files=6
MANDATORY_READ_PATHS=PASS count=12
```

The 12 paths are the two design files, reference index, four workflow files, three templates and two flat adapters.

A broader canonical read-graph scan covered 79 Markdown files and 483 local links. It found one error:

```text
CANONICAL_MARKDOWN_FILES=79
CANONICAL_LOCAL_LINKS=483
CANONICAL_LINK_ERRORS=1
AGENTS.md -> references/design_system.md
```

This is an existing governance pointer; Task 3 did not edit it.

### Immutable v1

Compared all files against `inventory.json`, then recomputed the aggregate with ordinal path sorting, LF separators and UTF-8 without BOM:

```text
V1_FILE_COUNT=281
V1_MISMATCHES=0
V1_AGGREGATE=9e537498a83b9167a68a98af156a8aecc44bdcc58337ecb472eef1d3dc12c8d4
V1_EXPECTED=9e537498a83b9167a68a98af156a8aecc44bdcc58337ecb472eef1d3dc12c8d4
V1_MATCH=True
```

### Repository validator

`python scripts/validate.py .` first hit the Windows cp1252 output limitation. Rerunning with `PYTHONIOENCODING=utf-8` executed the validator and returned `FAIL`. The current validator still expects the superseded unnumbered package (`agents/README.md`, `processes/README.md`, old registries/previews), scans preserved source archives as active content, and checks the stale pre-restructure manifest. These are Task 4 concerns; Task 3 did not edit scripts or manifest.

## Concerns

1. `AGENTS.md` still links to `references/design_system.md`. Governance alignment must update this pointer only after the required Task 6 approval.
2. `scripts/validate.py`, `manifest.json` and `SHA256SUMS` are not yet aligned to the numbered package and superseded-source exclusions. Until Task 4 completes, whole-package validation must not be reported as passing.
3. Archived adapter and skill files intentionally preserve their former content, including historical relative links/frontmatter/encoding. They must remain excluded from active entrypoint, link and payload validation rather than being rewritten as current instructions.

## Rollback

Restore the previous root `README.md`, `SKILL.md` and nested adapter/skill locations from version control or reverse the recorded moves. Do not alter `v1/`; its verified aggregate is the rollback invariant.

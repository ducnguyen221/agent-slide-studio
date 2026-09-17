---
title: "Task 1 report — Inventory and canonical source"
description: "Tài liệu Task 1 report — Inventory and canonical source trong agent-slide-studio."
document_type: execution-record
status: active
---

# Task 1 report — Inventory and canonical source

## Status

PASS with one source-availability concern: the planned legacy tree `slide-design/` is absent from the working tree. No source file was moved or edited.

## Files changed

- Created `docs/plans/2026-09-17-imagegen-first-restructure/inventory.json`.
- Created `docs/plans/2026-09-17-imagegen-first-restructure/migration-map.md`.
- Created this report, `.superpowers/sdd/plan/task-1-report.md`.

No changes were made under `v1/**`, `skills/slide-infographic/**`, `slide-design/**`, package source, or governance files.

## Baseline captured

- Branch: `feat/presentation-studio`
- HEAD: `c0979ab468a98c3a57b73de896abc24c9a18b583`
- Git status: captured verbatim in `inventory.json` before Task 1 outputs were added.
- `v1/`: 281 files, individual SHA-256 + byte length for every file.
- Aggregate v1 manifest hash: `9e537498a83b9167a68a98af156a8aecc44bdcc58337ecb472eef1d3dc12c8d4`.
- Canonical root asset baseline: L01–L48, I01–I12, taxonomy, previews/gallery, user references and reference images, each with SHA-256 + byte length.
- Nested `skills/slide-infographic/`: 17 source files classified as `root_newer`, `source_only`, or `conflict`; there were no byte-identical matches.
- `slide-design/`: explicitly recorded as unavailable; no fabricated comparison rows.

## Commands and outputs

1. Cold start and authority reads:

   - Read `~/.opcos/AGENTS.md`, Brain `AGENTS.md`, Brain `INDEX.md`, Brain `00_SELF/README.md`, repository `AGENTS.md`, Task 1 brief, spec and plan.
   - Result: root v2.1 is canonical; `v1/` and legacy sources are read-only; governance files are excluded.

2. Repository state:

   ```text
   git branch --show-current
   feat/presentation-studio

   git rev-parse HEAD
   c0979ab468a98c3a57b73de896abc24c9a18b583

   git status --short
   105 tracked deletions plus the existing root v2.1/untracked relocation, captured verbatim in inventory.json
   ```

3. Source discovery:

   ```text
   rg --files v1 slide-design skills/slide-infographic
   rg: slide-design: The system cannot find the file specified. (os error 2)
   v1 and skills/slide-infographic files enumerated successfully
   ```

4. Hash generation:

   - PowerShell `Get-FileHash -Algorithm SHA256` over every `v1/` file and every canonical asset.
   - Aggregate hash uses records sorted by path with ordinal Unicode comparison. Each record is `path<TAB>sha256<TAB>bytes`, paths use `/`, hashes use lowercase hex, records use LF, there is no final newline, and the payload is UTF-8 without BOM before SHA-256.
   - Result: 281 v1 entries; aggregate hash shown above.

5. JSON/path/hash verification:

   ```json
   {
     "json_parse": "PASS",
     "all_recorded_paths_exist": true,
     "v1_file_count": 281,
     "v1_hash_mismatches": 0,
     "v1_tree_hash": "9e537498a83b9167a68a98af156a8aecc44bdcc58337ecb472eef1d3dc12c8d4",
     "v1_tree_matches": true,
     "layout_count": 48,
     "infographic_count": 12
   }
   ```

   The intentionally absent `slide-design` is stored as `requested_path` with `exists: false`, not as an existing `path`.

6. Encoding check:

   - First attempt used `Get-Content -Encoding Byte`, which PowerShell 7 rejected because `Byte` is not an encoding name.
   - Corrected with `[IO.File]::ReadAllBytes(...)`.
   - Inventory prefix bytes are `123,10,32` (`{`, LF, space), so the file is UTF-8-compatible and has no BOM.

7. Source immutability check:

   ```text
   git status --short -- v1 slide-design skills/slide-infographic
   ?? v1/
   ```

   `v1/` was already untracked in the working tree, so Git cannot establish a historical before/after diff. The freshly recorded per-file and aggregate hashes are the reliable baseline for later tasks. `skills/slide-infographic/` showed no Task 1 changes.

## Self-review

- Inventory is machine-readable and contains branch, HEAD, porcelain status, per-file v1 hashes, canonical-asset hashes and legacy comparison classifications.
- Every concrete path stored in inventory exists and was checked.
- Migration map names the Markdown inputs for all ten canonical spec files and separates file-preserving asset moves from semantic merges.
- Conflicts are resolved by the spec, especially direct-text ImageGen-only and the seven-section prompt contract.
- The migration map does not turn historical QA reports into normative sources.
- No source, governance file, skill entrypoint or package code was edited.

## Concerns

1. `slide-design/` is absent. A later task must either supply that tree or accept the recorded gap; Task 1 cannot compare nonexistent bytes.
2. `v1/` is untracked at current HEAD. Its baseline is complete for future byte-level checks, but cannot prove provenance before this Task 1 run.
3. The working tree contains extensive pre-existing tracked deletions and untracked root v2.1 files. They were preserved exactly; later workers must continue avoiding reset/restore.

## Review-fix report — Important findings

### Changes

- Split the two layout registries into exact destinations: `02-references/layouts/archetypes/` and `02-references/layouts/infographics/`.
- Split historical source namespaces into `02-references/sources/originals/` and `02-references/sources/legacy/`.
- Corrected the prompt-compiler comparison: it already has all seven prompt sections. The conflict is only its text/mode policy; Task 2 must retain the seven-section structure and replace that policy with the spec's direct-text ImageGen-only rule.
- Replaced the aggregate hash recipe with a deterministic ordinal-sort contract and recomputed the hash as `9e537498a83b9167a68a98af156a8aecc44bdcc58337ecb472eef1d3dc12c8d4`.

### Verification rerun

- Parsed `inventory.json` successfully.
- Verified all 281 recorded files against their individual SHA-256 values: 0 mismatches.
- Reproduced the aggregate from the inventory records using ordinal path sort, tab-delimited fields, forward-slash paths, lowercase hex, LF separators, UTF-8 without BOM and no final newline: exact match.
- Independently reproduced the same aggregate with Python `json` + `sorted(..., key=path)` + `hashlib.sha256`: 281 files, `matches=True`, `final_newline=False`.
- Checked every concrete inventory path: 0 missing.
- Confirmed 48 layout Markdown files and 12 infographic Markdown files.

### Remaining concern

`slide-design/` remains absent from the working tree, so its comparison remains explicitly unavailable.

---
title: "SDD ledger — plan: docs/plans/2026-09-17-imagegen-first-restructure/plan.md"
description: "Tài liệu SDD ledger — plan: docs/plans/2026-09-17-imagegen-first-restructure/plan.md trong agent-slide-studio."
document_type: execution-record
status: active
---

# SDD ledger — plan: docs/plans/2026-09-17-imagegen-first-restructure/plan.md

## Preflight

| Task | Shared files/interfaces | Check |
|---|---|---|
| 1 → 2 | `inventory.json`, `migration-map.md` | Task 2 must consume the Task 1 mapping and preserve all source files in the first wave. |
| 2 → 3 | numbered canonical paths | Task 3 must update only paths created by Task 2 and leave governance untouched. |
| 3 → 4 | active SKILL/README/adapters | Task 4 validators must validate these current paths, not legacy paths. |
| 4 → 5 | validators and manifest | Task 5 records the exact Task 4 verification commands and results. |
| 1–5 | `v1/**` | Read-only in every task; before/after byte hashes are the invariant. |
| 6 | governance pointers | Blocked until explicit user approval; no earlier task may edit these files. |

Ruling: root is canonical because the user explicitly moved the current package outward and asked to complete the outer folder — cost if wrong: installed-skill packaging paths need a later migration.

Ruling: the package is documentation-first and intentionally does not add a new runtime/schema framework — cost if wrong: future automation may require a separate project rather than extending this refactor.

Task 1: fix round 1/5 (3 addressed, 0 open — collision-free mappings, accurate prompt-compiler classification, reproducible v1 aggregate hash).

Task 1: complete (review clean; no commits by instruction).
Task 2: complete (review clean after scoped fixes; no commits by instruction).
Task 3: complete (review clean; one active root SKILL; no commits by instruction).
Task 4: support tools packaged and tested; three script hardening findings deferred by explicit user request.
Task 5: pilot image generation skipped by explicit user request; final scope is Markdown structure, references, and native ImageGen routing.

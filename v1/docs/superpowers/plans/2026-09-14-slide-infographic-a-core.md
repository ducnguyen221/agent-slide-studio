# Slide Infographic A — Core Contract Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Cung cấp contract và CLI an toàn, kiểm thử được offline bằng fake host trước khi có backend ảnh/HTML.

**Architecture:** DeckSpec canonical được chiếu một slide vào VisualAssetBrief; hash nội dung tách integrity và policy. Request, reservation, dispatch và settlement là transaction payload của StateStore/RunLock hiện có, không thêm lifecycle. Registry visual tách khỏi handler native để không đổi WP04.

**Tech Stack:** Python >=3.12, Pydantic >=2.12,<3, pytest >=9,<10, Decimal, SHA-256, identity-bound filesystem hiện có.

**Spec:** [Design 1.1.1](../specs/2026-09-14-slide-infographic-design.md), §5–10, §12; [roadmap](2026-09-14-slide-infographic-roadmap.md).

**Phase:** Phase1 thực thi core cần IMAGE; HTML chỉ model/two-mode contract và typed unavailable stubs, không parser/browser dependency. Bổ sung yêu cầu hiện hành: deterministic compact PromptPack tối ưu token, IMAGE overlay mặc định. Không sửa spec file trong task plan này.

## Global Constraints

- `VisualAssetBrief.schema_version="1.0"`; DeckSpec reader nhận `1.0`/`1.1`; writer 1.0 bỏ hẳn `visual_semantics`, kể cả null.
- `extra=forbid`; canvas `64–8192`, diện tích ≤`33,554,432`; node `1–200`, edge `0–400`, references `0–8`.
- `fixed-decimal/1.0.0`, locale `vi-VN|en-US`, precision `0–12`, không scale/đổi unit ngầm.
- Project defaults `max_image_requests=0`, `max_repair_rounds=0`; brief calls `0–6`, repairs `0–2` chỉ siết.
- Money là Decimal string: tối đa 12 chữ số nguyên, 6 thập phân, không exponent; `None` không unlimited; không FX.
- `build passed/0`, render capability thiếu `failed/3`, audit thiếu evidence `unverified/4`, audit QA lỗi `failed/4`, process/provider `5`, conflict `6`, input `2`.
- Một visual có đúng một slide giữ original slide ID; assembly là build khác.
- BoundDirectory/RunLock/StateStore là primitive bắt buộc; không sửa WP04 native, không network/download tự động, không commit/push/deploy khi chỉ viết plan.

---

## File map và ownership

Owner **Sol — contract owner duy nhất**. Astra phản biện semantic/eval, không edit runtime. C/D không sửa các file sau ngoài change request được owner nhận.

| File | Trách nhiệm |
|---|---|
| `src/presentation_studio/models/visual.py` | Binding, graph, formatter, brief và validation §5 |
| `src/presentation_studio/models/deck.py` | Optional semantics, version-aware reader/writer |
| `src/presentation_studio/models/visual_policy.py` | Grant, usage, capability, effective policy |
| `src/presentation_studio/models/visual_request.py` | Immutable request/fulfillment/operation receipt |
| `src/presentation_studio/models/visual_result.py` | Sidecar, mapping, transformations và hash result |
| `src/presentation_studio/visual/{__init__,projection,formatting,hashing,policy,requests,io,resources,process,cli}.py` | Mỗi module một trách nhiệm như tên; không gom thêm renderer |
| `src/presentation_studio/{cli,state}.py` | Dispatch adapter và transaction payload qua primitive cũ |
| `src/presentation_studio/models/{__init__,reports}.py` | Export model mới, validation invariant đã có; giữ schema assets/project 1.0 |
| `scripts/generate-schemas.py`, `schemas/` | Export strict schemas, deterministic generation |
| `tests/visual_support.py`, `tests/fixtures/visual/core/` | Factory/corpus trung tính dùng chung; không production I/O shortcut |
| `tests/unit/test_visual_{models,projection,hashing,policy,resources,cli}.py` | Pure contract/mutation tests |
| `tests/integration/test_visual_{requests,filesystem,process}.py` | WAL/crash/identity/process thật |

Các type ghi trong spec được định nghĩa cùng tên trong model tương ứng. Type bổ sung dưới đây là API tích hợp cố định, không free-form dict field cho brief. `VisualError` có `code: str`, `exit_code: int`, `message_vi: str`; CLI sanitize trước stdout/stderr. Các signature dạng `text` dưới đây là contract phải implement, không code đã tồn tại.

### Task A1: Strict models, chart binding và version-aware DeckSpec

**Files:** Create `models/visual.py`, `tests/visual_support.py`, `tests/fixtures/visual/core/{deck-1.0.json,deck-chart-1.1.json,brief-image.json,brief-html.json,profile-lock.json,asset-manifest.json}` dưới các root trong file map; Create `tests/unit/test_visual_models.py`, `tests/fixtures/visual/core/legacy_reader.py`; Modify `models/deck.py`, `models/__init__.py`.

**Interfaces:** Consumes `StrictModel`, `Identifier`, `RelativePath`, `SHA256`, `ProfileLock`, `DeckSpec`, `ChartContent`, `ChartDatum`. Produces `ContentBinding`, `ChartBinding`, `SemanticNode`, `VisualSemantics`, `NumberFormatter`, `VisualAssetBrief`, `VisualError`; `serialize_deck(deck: DeckSpec, target_version: str | None = None) -> bytes`; test `fixture_json(name: str) -> dict`, `load_brief(mode: str = "IMAGE") -> VisualAssetBrief`.

- [ ] Viết test writer bằng reader 1.0 **được khóa từ baseline**: chép các model deck/common phụ thuộc vào `legacy_reader.py` chỉ trong fixture namespace, giữ extra=forbid; không import DeckSpec mới trong reader cũ. Fixture deck-1.0 lấy fixture native trung tính hiện hữu, xác nhận không có graph trước khi sao.

```python
def test_writer_10_omits_new_field():
    from presentation_studio.models.deck import DeckSpec, serialize_deck
    from tests.fixtures.visual.core.legacy_reader import DeckSpec as OldDeck
    deck = DeckSpec.model_validate(fixture_json("deck-1.0"))
    output = serialize_deck(deck, "1.0")
    assert b"visual_semantics" not in output
    OldDeck.model_validate_json(output)
```

- [ ] RED: `python -m pytest tests/unit/test_visual_models.py -q`; expected ImportError `serialize_deck`/visual models. Lưu failure thực, không tiếp tục authoring fixture mới nếu RED là lỗi environment.
- [ ] Thêm binding/graph typed classes theo toàn bộ bảng §5.1; dispatch field allowlist, chart-label/value bắt element chart + index, chart-unit/display-unit cấm index/item_id; quan hệ contains phải khớp parent, cycle graph hợp lệ nhưng parent cycle bị cấm. Khóa API error:

Graph types trong visual.py không import DeckSpec; deck.py import VisualSemantics, còn parity liên model nằm ở projection.py. Quy tắc này tránh circular import giữa canonical deck và brief.

```python
class VisualError(ValueError):
    def __init__(self, code: str, exit_code: int, message_vi: str) -> None:
        super().__init__(f"{code}: {message_vi}")
        self.code = code
        self.exit_code = exit_code
        self.message_vi = message_vi
```

- [ ] Thêm NumberFormatter và VisualAssetBrief, chia validator theo nodes/relations, mode/text/deliverables, canvas/crop/motion, execution/approval. Mỗi validator dùng fixture mutation để chứng minh unknown field/ID, none có chữ, reconstruction baked, motion thiếu duration, crop chưa approved bị reject. Không thêm field vào `common.SchemaVersion` chung.
- [ ] Viết writer chọn version theo semantics thực, reject LOSSY_DOWNGRADE; chỉ exclude key `visual_semantics` từng slide cho1.0, không exclude_none toàn cục. Thêm negative test inject null key vào byte writer rồi old reader phải ValidationError; semantics object emit1.1; old reader reject1.1.

```text
serialize_deck(deck: DeckSpec, target_version: str | None = None) -> bytes
VisualAssetBrief.model_validate(value: object) -> VisualAssetBrief
```

- [ ] Tạo corpus chart s03/c1 datum “Nhóm A”=18.5, unit “điểm”, source measurement-source; label/value/unit có typed bindings và duy nhất một Fact owner/pointer. Brief IMAGE/HTML dùng đủ field §5, canvas1920×1080, safe0.05; HTML primary reference trung tính, import/calls0; không nguồn riêng. Factory đọc JSON:

```python
from pathlib import Path
import json

def fixture_json(name: str) -> dict:
    root = Path(__file__).parent / "fixtures" / "visual" / "core"
    return json.loads((root / f"{name}.json").read_text(encoding="utf-8"))
```

- [ ] GREEN: `python -m pytest tests/unit/test_visual_models.py tests/unit/test_models.py -q`. Expected pass với AC49/50/51; schema fixture không là output live.
- [ ] Commit scope A1: `git add src/presentation_studio/models/visual.py src/presentation_studio/models/deck.py src/presentation_studio/models/__init__.py tests/visual_support.py tests/fixtures/visual/core tests/unit/test_visual_models.py`; `git commit -m "feat: add versioned visual contracts and deck compatibility"`.

### Task A2: Canonical projection, formatter và parity

**Files:** Create `visual/{__init__,projection,formatting}.py`, `tests/unit/test_visual_projection.py`; Modify `tests/visual_support.py` chỉ để export load_brief đã định nghĩa.

**Interfaces:** Consumes A1 models và `state.hash_inputs(inputs: dict) -> str`. Produces frozen dataclass `ResolvedContent(pointer: str, scalar: str | Decimal | None, source_ref: str | None)`; `resolve_binding(deck: DeckSpec, binding: ContentBinding) -> ResolvedContent`; `format_number(value: Decimal, formatter: NumberFormatter) -> tuple[str, bool]`; `content_projection(deck: DeckSpec, slide_id: str) -> dict` trong projection.py; `project_brief(deck: DeckSpec, brief: VisualAssetBrief, deck_raw_sha256: str) -> VisualAssetBrief`; `assert_content_parity(deck: DeckSpec, brief: VisualAssetBrief) -> None`; `project_build_deck(deck: DeckSpec, brief: VisualAssetBrief) -> DeckSpec`. Tuple formatter = display text, value-rounded flag.

- [ ] Viết exact string test, expected tự viết độc lập formatter:

```python
from decimal import Decimal
from presentation_studio.visual.formatting import format_number
from tests.visual_support import load_brief

def test_vietnamese_value_is_not_fact_value():
    fmt = load_brief().number_formatters["chart-value"]
    assert format_number(Decimal("18.5"), fmt) == ("18,5", False)
    fmt = fmt.model_copy(update={"precision": 2})
    assert format_number(Decimal("18.5"), fmt) == ("18,50", False)
```

- [ ] RED: `python -m pytest tests/unit/test_visual_projection.py -q`; expected missing formatting/projection module.
- [ ] Implement fixed-decimal registry1.0.0 bằng Decimal.quantize, ROUND_HALF_EVEN/HALF_UP; vi-VN comma/dot, en-US dot/comma, precision0–12; reject NaN/Infinity và inexact mặc định. Khi rounded yêu cầu prefix và render `≈18`; transcript vẫn source18.5. Không dùng locale OS.

```text
format_number(value: Decimal, formatter: NumberFormatter) -> tuple[str, bool]
resolve_binding(deck: DeckSpec, binding: ContentBinding) -> ResolvedContent
```

- [ ] Implement resolver allowlist §5.1 bằng typed dispatch; slide/element lookup theo ID rồi mới pointer `/slides/S/elements/E/content/data/i/value`. Scalar Fact decimal lấy `Decimal(str(value))`, không lấy displayed text. Resolve shared unit một lần; dedup Fact owner theo canonical pointer; mismatch datum/source/label/value/unit trả CONTENT_PARITY_FAILED.
- [ ] Implement content_projection trong projection.py theo allowlist §6: NFC text, canonical numeric/facts/graph/notes và used-source hashes, relations sortID, reading_order giữ thứ tự; loại layout/htmlref/path/evidence/timestamp/unselectedslides. Implement project_brief trả model mới, copy canonical text/facts/graph/notes, giữ design; bind rawhash thật và `hash_inputs(content_projection(deck, brief.slide_id))`. A2 tự chạy đầy đủ, không phụ thuộc module A3 chưa tồn tại.
- [ ] Implement project_build_deck deep-copy đúng một slide s03 với canvas custom px và original slide_id; không rewrite canonical source. Thêm test source deck5slides chỉ projection1slide, chưa serialize những slide khác cho provider.
- [ ] Thêm parametrized mutation tests AC32/33/45–48/51: chỉ sửa brief fail; chỉ sửa canonical stale; re-project19.5→Fact19.5/text19,5; unit “lần”; locale/precision/trim/rounding; duplicate unit fact; mismatched label datum. Numeric table cells dùng cùng formatter; missing source không bịa Fact.
- [ ] GREEN: `python -m pytest tests/unit/test_visual_projection.py -q`. Commit `git add src/presentation_studio/visual/__init__.py src/presentation_studio/visual/projection.py src/presentation_studio/visual/formatting.py tests/unit/test_visual_projection.py tests/visual_support.py`; `git commit -m "feat: project canonical visual content and exact numeric display"`.

### Task A3: Hash projections và immutable result mapping

**Files:** Create `visual/hashing.py`, `visual/prompt.py`, `models/visual_prompt.py`, `models/visual_result.py`, `tests/unit/test_visual_hashing.py`, `tests/unit/test_visual_prompt.py`, `tests/fixtures/visual/core/{hash-a.json,hash-b.json,expected-content.json,expected-semantic.json,prompt-verbose.json}`; Modify A2 projection chỉ để chia sẻ encoder NFC/strict với A3 mà giữ hash A2 ổn định, `models/__init__.py`.

**Interfaces:** Consumes A1/A2, đặc biệt `projection.content_projection(deck: DeckSpec, slide_id: str) -> dict`. Produces `VisualResult`, `GenerationObservation`, `Transformation`, `ElementMapping`, `VisualHashes(raw_sha256: str, slide_content_hash: str, semantic_hash: str, input_hash: str)`; `canonical_bytes(value: object) -> bytes`; `compute_visual_hashes(deck: DeckSpec, brief: VisualAssetBrief, brief_raw: bytes, render_inputs: dict) -> VisualHashes`. `render_inputs` nhận đúng allowlist §6, reject unknown key; không extension arbitrary.

Thêm `PromptPack` StrictModel: schema_version1.0, canvas, objective, hierarchy, layout, style, exclusions, prompt_text, prompt_hash, compiler_version, estimator_id/model/version nullable, token_estimate nullable, token_ceiling nullable, compression_rules list và preserved_constraint_ids. `PromptEstimator` port có id/model/version và `estimate(text: str) -> int | None`; `compile_prompt_pack(brief: VisualAssetBrief, estimator: PromptEstimator, token_ceiling: int | None) -> PromptPack`. Không gọi provider/tokenizer network ngầm. Estimator không khả dụng ghi unknown/null, không hứa số token; nếu ceiling bắt buộc mà không thể estimate đáng tin, trả TOKEN_ESTIMATE_UNAVAILABLE/3.

- [ ] Viết RED expected encoder độc lập production:

```python
import hashlib
import json

def test_content_projection_matches_golden():
    from presentation_studio.visual.hashing import canonical_bytes
    from presentation_studio.visual.projection import content_projection
    from presentation_studio.models import DeckSpec
    deck = DeckSpec.model_validate(fixture_json("deck-chart-1.1"))
    expected = fixture_json("expected-content")
    assert content_projection(deck, "s03") == expected
    golden = json.dumps(expected, ensure_ascii=False, sort_keys=True,
                        separators=(",", ":"), allow_nan=False).encode("utf-8")
    assert hashlib.sha256(canonical_bytes(expected)).digest() == hashlib.sha256(golden).digest()
```

- [ ] RED: `python -m pytest tests/unit/test_visual_hashing.py -q`; expected missing hashing module, không tự generate golden bằng production code.
- [ ] Viết prompt compiler RED test: cùng brief/profile/estimator→prompt_text/hash giống nhau; overlay không lặp canonical body text. `python -m pytest tests/unit/test_visual_prompt.py -q` expected missing compiler, không thiếu tokenizer được gọi là behavior RED.

```python
def test_prompt_pack_is_deterministic(prompt_case, fixed_estimator):
    first = compile_prompt_pack(prompt_case, fixed_estimator, 4096)
    second = compile_prompt_pack(prompt_case, fixed_estimator, 4096)
    assert first.prompt_text == second.prompt_text
    assert first.prompt_hash == second.prompt_hash
    assert set(first.preserved_constraint_ids) == set(second.preserved_constraint_ids)
```

`fixed_estimator` là test-only tokenizer giả có id/model/version, dùng cùng estimator cho compact/verbose comparison; không dùng kết quả fake làm actualmodel token claim.
- [ ] Triển khai PromptPack theo block order canvas→objective→hierarchy→layout→style→exclusions; giữ reading_order/relations, canvas/safearea/text policy và locked visual constraints. Normalize whitespace trong prompt prose, exact dedup constraints theo stableID; không normalize/truncate canonical text payload. Overlay chỉ prompt no-text background + geometry/hierarchy, không lặp text sẽ do renderer thêm. Reusable style block lấy resolved profile values compact, không gửi profile provenance dư thừa.
- [ ] Compression chỉ dedup/canonical compact syntax, không bỏ visual-critical constraints hoặc đổi meaning. token_estimate>ceiling sau compression→PROMPT_TOKEN_BUDGET_EXCEEDED/2 trước reserve/dispatch, không truncate âm thầm. prompt_hash=SHA256 đúng UTF-8 prompt_text thực gửi; compiler/estimator/model/version/estimate/ceiling/rules lưu provenance. Unknown tokenizer chỉ báo estimate theo estimator hiện có cùng giới hạn, không gọi đó exactprovider count.
- [ ] Tests constraint preservation, whitespace/dedup stable order, changed style/canvas→hash đổi; verbose fixture có20 đoạn lặp cùng constraints phải compact estimate≤70%verbose theo cùng fixed estimator nhưng đủ protectedfields. Test over-ceiling fail2/calls0; unavailable mandatoryestimator3; không promise mức giảm cho model/tokenizer chưa đo. GREEN `python -m pytest tests/unit/test_visual_prompt.py -q`.
- [ ] Implement NFC recursive canonical encoder; content allowlist loại layout/html ref, evidence/path/timestamps/unselected slides; relations sortID, reading_order giữ thứ tự, canonical Fact pointer theo stableID. Golden A/B đúng fixture §6: title Chuẩn bị, text Đủ4bước, palette#112233; metadata revision/created_at/evidence khác, bytehash khác.
- [ ] Implement semantic allowlist §6 và inputallowlist; profile valuehash không raw metadata; reference/font/source byte hash có thật. Formatter fullconfig vào semantic, implementation bytes vào input. Thêm mutation table AC15/36/37/45–48 với expected tầng đổi/giữ; CSS-only chỉ input; formatterimplementation-only chỉ input.

```text
compute_visual_hashes(deck: DeckSpec, brief: VisualAssetBrief, brief_raw: bytes, render_inputs: dict) -> VisualHashes
content_projection(deck: DeckSpec, slide_id: str) -> dict
```

- [ ] Implement VisualResult/GenerationObservation/Transformation theo §6; unknown provider/model/request dùng sentinel có metadata_known=false, không thay bằng internalrequestID. Sidecar mapping HTML not_applicable+editable_in; reports referencepath+hash; projection retainsoriginindex/hash. Cross-validator checks output matching và immutable snapshot revisions.
- [ ] GREEN: `python -m pytest tests/unit/test_visual_hashing.py tests/unit/test_visual_prompt.py tests/unit/test_visual_projection.py tests/unit/test_visual_models.py -q`. Commit `git add src/presentation_studio/visual/hashing.py src/presentation_studio/visual/prompt.py src/presentation_studio/visual/projection.py src/presentation_studio/models/visual_prompt.py src/presentation_studio/models/visual_result.py src/presentation_studio/models/__init__.py tests/unit/test_visual_hashing.py tests/unit/test_visual_prompt.py tests/fixtures/visual/core`; `git commit -m "feat: compile compact deterministic visual prompts and hashes"`.

### Task A4: Effective policy, trusted grant và aggregate project budget

**Files:** Create `models/visual_policy.py`, `visual/policy.py`, `tests/unit/test_visual_policy.py`, `tests/fixtures/visual/core/{grant.json,usage.json,capabilities.json}`; Modify `models/__init__.py`. Giữ `models/project.py`/`models/assets.py` schema1.0; monetary adapter nằm trong policy.py.

**Interfaces:** Consumes `ProjectConfig`, brief A1, `datetime`. Produces `ExecutionGrant`, `ProjectUsageSnapshot`, `CapabilitySnapshot`, `EffectivePolicy`; `resolve_effective_policy(project: ProjectConfig, grant: ExecutionGrant | None, brief: VisualAssetBrief, usage: ProjectUsageSnapshot, capabilities: CapabilitySnapshot, now: datetime) -> EffectivePolicy`; `verify_grant(paths: WorkspacePaths, grant_ref: str) -> ExecutionGrant`. Policy pure calculator chỉ được dùng làm authorization trong locked caller A6; verify_grant kiểm trusted producer registry identity, không tin file tự viết.

- [ ] Viết policy matrix assertions với factory `policy_inputs(tmp_path)` được thêm vào test module, tạo models từ public core JSON và init ProjectConfig default. Mỗi test thay input bằng model_validate sau mutation, không dùng model_copy để bỏ validator:

```python
def test_project_zero_cannot_be_relaxed(tmp_path):
    values = policy_inputs(tmp_path)
    values["project"].budget.max_image_requests = 0
    with pytest.raises(VisualError) as exc:
        resolve_effective_policy(**values)
    assert exc.value.code == "BUDGET_BLOCKED"
    assert exc.value.exit_code == 3
```

- [ ] RED: `python -m pytest tests/unit/test_visual_policy.py -q`; expected missing policy module/model.
- [ ] Implement strict models đủ §5.2; convert legacy finite numeric money qua Decimal(str(value)), serialize decimal string trong visual monetary models. Không đổi type/schema float legacy của ProjectConfig/Generation và không rewrite YAML; ledger/decision chỉ dùng Decimal, không dùng Generation.actual_cost float làm accountingtruth. None monetaryproject→BUDGET_POLICY_INCOMPLETE; currency firstledgerlock, mismatchreject, hostquota explicitnullmoney.
- [ ] Implement mincaps(project,grant,brief), ANDnetwork/egress, absentgrantgeneration/repair0; policyhash loại remaining/time; ledgerremaining tính spent+reserved+unknown acrossproject/briefrevision/adapter. Request tự claim không trừ reservation của chính nó lần hai.

```text
resolve_effective_policy(project: ProjectConfig, grant: ExecutionGrant | None, brief: VisualAssetBrief, usage: ProjectUsageSnapshot, capabilities: CapabilitySnapshot, now: datetime) -> EffectivePolicy
verify_grant(paths: WorkspacePaths, grant_ref: str) -> ExecutionGrant
```

- [ ] Thêm tests projectdeny/briefallow, briefdeny/projectallow, projectrepair0/brief2; two-brief capremaining; grantmissing/staleexpired/revoked/identity/policyhash; floatNaN; currency mismatch; hostquota nullmoney vs briefzero. Unknown registry→capability3; task không tạo grant từ chat transcript.
- [ ] GREEN: `python -m pytest tests/unit/test_visual_policy.py tests/unit/test_models.py -q`. Commit `git add src/presentation_studio/models/visual_policy.py src/presentation_studio/visual/policy.py src/presentation_studio/models/__init__.py tests/unit/test_visual_policy.py tests/fixtures/visual/core`; `git commit -m "feat: enforce project scoped visual budget ceilings"`.

### Task A5: Identity I/O, resource admission và owned workers

**Files:** Create `models/visual_worker.py`, `visual/{io,resources,process}.py`, `tests/unit/test_visual_resources.py`, `tests/integration/test_visual_filesystem.py`, `tests/integration/test_visual_process.py`; Modify `state.py` để thêm typed resource-operation transaction trên WAL hiện có, `models/__init__.py`.

**Interfaces:** Consumes A1–A4 và BoundDirectory, RunLock, ProcessResult, WorkspacePaths. Produces `ResourceInventory(encoded_bytes: int, decoded_pixels: int, canvas_pixels: int, source_bytes: int, asset_count: int, dom_nodes: int, dom_depth: int, css_rules: int, svg_elements: int, svg_path_commands: int, gradient_stops: int)`; `admit_resources(inventory: ResourceInventory) -> int` returns estimated resident bytes; `read_visual_file(paths: WorkspacePaths, relative_path: str, max_bytes: int) -> bytes`; `promote_visual_files(paths: WorkspacePaths, staging_ref: str, hashes: dict[str,str]) -> None`; `run_visual_worker(paths: WorkspacePaths, operation: WorkerOperation, payload_ref: str, timeout_seconds: int) -> ProcessResult`; `read_worker_result(paths: WorkspacePaths, payload_ref: str) -> VisualWorkerResult`; `inspect_image_asset(paths: WorkspacePaths, relative_path: str, inventory: ResourceInventory) -> ImageInspection`; `decode_image_asset(paths: WorkspacePaths, relative_path: str, inventory: ResourceInventory) -> ImageInspection`; `StateStore.commit_operation(lock: RunLock, expected_revision: int, input_hash: str, operation: dict) -> dict` với resource record strict trước, A6 mở rộng request record sau.

`WorkerOperation` là Literal `image-inspect|image-decode|html-inspect|html-parse|image-build|image-render|image-export|html-build|html-render`. `VisualWorkerJob` strict có schema_version1.0, operation, input_refs(path/raw_sha256/encoded_bytes), inventory, result_ref và timeout_seconds. `VisualWorkerResult` strict có job_sha256, operation, status passed/failed, exit_code, error_code nullable, inventory và output_refs(path/raw_sha256); result JSON≤1MiB. `ImageInspection` strict có raw_sha256, media_type, width, height, decoded_pixels, decoded_verified, worker_result_ref. Payload không chứa shell/code/callable. A5 triển khai image-inspect/image-decode; html-inspect/html-parse đăng ký typed unavailable/3 cho đến D1. A5 không phụ thuộc D1 để GREEN.

- [ ] RED aggregatepixel test:

```python
def test_aggregate_decoded_pixels_rejected():
    inventory = ResourceInventory(1000, 67_108_865, 1920*1080, 100, 3,
                                  1, 1, 1, 1, 1, 0)
    with pytest.raises(VisualError) as exc:
        admit_resources(inventory)
    assert (exc.value.code, exc.value.exit_code) == ("RESOURCE_LIMIT_EXCEEDED", 2)
```

- [ ] Run `python -m pytest tests/unit/test_visual_resources.py -q`; expected missing resources module.
- [ ] Main process chỉ kiểm identity/byte cap và đọc bounded header tối đa64KiB/file; không gọi Pillow.open/load, XML/HTML/CSS parser hoặc decompressor trên input không tin cậy. Header chưa đủ biết dimensions thì reserve resident ceiling768MiB, không đoán0pixel; worker inspect phải xác định kích thước trước full decode. Limits brief1MiB/image32MiB/source4MiB/128assets/encodedtotal128MiB; perimage33,554,432pixels, total67,108,864. Residentformula `256*2**20 + 12*decoded_pixels + 12*canvas_pixels + 8*source_bytes`, reject >768MiB.
- [ ] Sau khi lease/memory/timeout/network isolation đã được gắn vào process tree, chạy typed image-inspect để parse container/header và image-decode để verify/decode thực; kiểm aggregate inventory đã gồm toàn bộ batch, không admission riêng từng ảnh. `inspect_image_asset`/`decode_image_asset` chỉ là parent orchestrator, trả ImageInspection từ bounded worker result; decoded_verified=true chỉ sau image-decode thành công và hash khớp. Không chuyển toàn bộ pixel buffer về parent. D1 html-inspect/html-parse dùng cùng primitive để cung cấp counts DOM10k/depth64/CSS10k/SVG20k/path100k/stops4096/no filters trước browser.
- [ ] Implement read/promote through bound directory handles, verify hash+identity again duringpromotion; refuse traversal/absolute/link/hardlink/reparse/swap. Keep existingoutput on failure; cleanup only staging identity owned byrun.

```text
read_visual_file(paths: WorkspacePaths, relative_path: str, max_bytes: int) -> bytes
run_visual_worker(paths: WorkspacePaths, operation: WorkerOperation, payload_ref: str, timeout_seconds: int) -> ProcessResult
decode_image_asset(paths: WorkspacePaths, relative_path: str, inventory: ResourceInventory) -> ImageInspection
```

- [ ] Implement process launcher explicit argv `sys.executable -m presentation_studio.visual.process` with operation/jobpath; own PID+starttime. Admission lease station→project order, project1worker/station2workers/2GiB totalreserved; hard process-tree1GiB and timeout; Windows Job Object or tested equivalent. Noenforcementcapability→3 beforeuntrustedexecution, not soft-memorypretendpass. Lease reclaim only deadidentity; unrelatedprocess untouched.
- [ ] Trong worker build/render đã có isolation, gọi trực tiếp worker-only decoder/parser routines, không spawn lồng worker để tránh deadlock lease1/project. Parent entrypoints luôn đi qua launcher; không có flag từ brief để nhận là worker. Thêm StateStore.commit_operation cho resource lease record, dùng WAL/revision/RunLock có sẵn; không tạo lifecycle mới và không chờ request module A6.
- [ ] Write real worker memorykill and timeout tests returning ProcessResult started/pid/time/exit/failure_kind, stagefailure5 and priorhashunchanged. Headerbombsmallencodedmanylargepixels fails2 before full decode; competinglease6; symlink/hardlink swaps12; test unsupportedplatform reports unavailable not pass.
- [ ] AC38–40 tests: malformed image/container và decompression bomb trong image-inspect/decode, encoded nhỏ nhưng aggregatepixels lớn, worker allocation vượt1GiB. Assert parentPID vẫn sống, một harmless request tiếp theo chạy được, ownedchild đã chết/lease đã release, staging riêng được cleanup, prioroutput/hash/accounting giữ nguyên. Input/complexity reject có result hợp lệ→2; hard kill/crash/timeout→5; thiếu enforcement→3 trước parse. D1 bổ sung cùng assertions cho source phức tạp.
- [ ] GREEN `python -m pytest tests/unit/test_visual_resources.py tests/integration/test_visual_filesystem.py tests/integration/test_visual_process.py tests/unit/test_state.py -q`. Commit `git add src/presentation_studio/models/visual_worker.py src/presentation_studio/models/__init__.py src/presentation_studio/state.py src/presentation_studio/visual/io.py src/presentation_studio/visual/resources.py src/presentation_studio/visual/process.py tests/unit/test_visual_resources.py tests/integration/test_visual_filesystem.py tests/integration/test_visual_process.py`; `git commit -m "feat: isolate visual inspection and decoding before fulfillment"`.

### Task A6: Durable prepare/reserve/claim-dispatch

**Files:** Create `models/visual_request.py`, `visual/requests.py`, `tests/integration/test_visual_requests.py`; Modify `state.py` transaction payload only, `models/__init__.py`.

**Interfaces:** Consumes A1–A5, StateStore.commit_operation đã có từ A5, RunLock, WorkspacePaths và isolated inspect/admission. Produces `ImageRequest`, `ImageFulfillment`, `RequestReceipt(internal_request_id: str, request_sha256: str, outcome: str, idempotent: bool, claim_token: str | None, host_identity_hash: str | None)`; `prepare_request(paths: WorkspacePaths, brief_ref: str) -> RequestReceipt`; `claim_dispatch(paths: WorkspacePaths, request_id: str, host_identity: str) -> RequestReceipt`. Mở rộng operation validator bằng `VisualOperation` request records reserve/dispatch/fulfill/cancel/recovery, giữ resource records của A5; transactionID và previousrecordhash bắt buộc. Claim token chỉ được giao cho host đã xác minh; public diagnostics/export phải bỏ token, không dùng token làm provider ID.

RequestReceipt là StrictModel, outcome allowlist `prepared|dispatched|succeeded|failed|unknown|cancelled`; đây là derived operation outcome, không bổ sung StateStore lifecycle. ImageRequest/ImageFulfillment có đầy đủ fields §7.1, các byte/request/receipt hash là integrity thật.

- [ ] Viết test two processes contend projectremaining1; trusted testregistry cấp fixturegrant không dùng production fallback. Fixture `request_workspace(tmp_path)` init workspace, install neutral brief/grant using fixture authority adapter bound to test process; chỉ tests được inject verifier.

```python
def test_prepare_does_not_dispatch(request_workspace, fake_host):
    receipt = prepare_request(request_workspace, "storyboard/visuals/pilot/r1/brief.json")
    assert receipt.outcome == "prepared"
    assert fake_host.calls == 0
    assert request_records(request_workspace, receipt.internal_request_id)[-1]["kind"] == "reserve"
```

`request_records(paths: WorkspacePaths, request_id: str) -> list[dict]` là test helper đọc journal snapshot qua StateStore, định nghĩa ngay trong test module; `fake_host` đơn giản có `calls=0` và không đăng ký network.

- [ ] RED: `python -m pytest tests/integration/test_visual_requests.py -q -k "prepare or claim"`; expected missing protocol functions.
- [ ] Extend WAL operation validation/atomic commit để requestfile+ledgerdelta dùng mộttransaction; tái sử dụng existing recovery, revision compare, RunLock ownership. Không thay started/ended/aborted hoặc suy accounting từ file existence.
- [ ] Implement prepare đọc lại identity/policy/rawparity underlock; reserveonecall+upperbound/quota; immutableprompt/referencehash; random internalID; request_sha excludesonlyitself. Release lock trước host. Implement claim single-use owner token, recheckfreshgrantcapability and rawbinding; duplicateclaim6.
- [ ] Prepare tiêu thụ A3 PromptPack đã compile/estimate theo locked provider capability; bind prompt_ref/raw_sha256 bằng đúng prompt_text/hash, không thay bằng brief hash. Prompt ceiling/constraint failure chặn trước reserve. Một primary generation là mục tiêu; repair chỉ sau QA issue có ID và effective repair/call/cost bounds, không retry chỉ vì chưa đúng thẩm mỹ mà không QA/budget.

```text
prepare_request(paths: WorkspacePaths, brief_ref: str) -> RequestReceipt
claim_dispatch(paths: WorkspacePaths, request_id: str, host_identity: str) -> RequestReceipt
```

- [ ] Test crashafterreserve, stalegrantbeforeclaim, two-brief/twoprocess lastcall exactlyonewinner, missingauthority0dispatch, request providerID absent. Error during journalpromotion leaves previousoutputs untouched. Transaction fault hooks only injected in tests, not configurable from brief.
- [ ] GREEN: `python -m pytest tests/integration/test_visual_requests.py tests/unit/test_state.py -q -k "prepare or claim or state or journal or lock"`; then full requestmodule. Commit `git add src/presentation_studio/models/visual_request.py src/presentation_studio/visual/requests.py src/presentation_studio/state.py src/presentation_studio/models/__init__.py tests/integration/test_visual_requests.py`; `git commit -m "feat: reserve image requests atomically before host dispatch"`.

### Task A7: Fulfill/recover/cancel và truthful accounting

**Files:** Modify `visual/requests.py`, `models/visual_request.py`, `state.py` recovery payload, `tests/integration/test_visual_requests.py`; Create `tests/integration/test_visual_request_crashes.py`.

**Interfaces:** Consumes A6 và A5 `admit_resources`, `inspect_image_asset`, `decode_image_asset`, `run_visual_worker`, `promote_visual_files`. Produces `fulfill_request(paths: WorkspacePaths, request_id: str, fulfillment_ref: str) -> RequestReceipt`; `recover_request(paths: WorkspacePaths, request_id: str) -> RequestReceipt`; `cancel_request(paths: WorkspacePaths, request_id: str) -> RequestReceipt`; `read_request(paths: WorkspacePaths, request_id: str) -> ImageRequest`. Receipt is verified host evidence+bytes, not model-written succeeded flag.

- [ ] Viết duplicate settle test với helper `fulfilled_case(tmp_path)` tạo durableprepared+claimedrequest, neutralPNG+receipt đủ hash bằng fake host fixture; không call thật:

```python
def test_duplicate_fulfillment_is_accounted_once(tmp_path):
    paths, request_id, receipt_ref = fulfilled_case(tmp_path)
    first = fulfill_request(paths, request_id, receipt_ref)
    second = fulfill_request(paths, request_id, receipt_ref)
    assert first.outcome == second.outcome == "succeeded"
    assert second.idempotent is True
    assert settlement_count(paths, request_id) == 1
```

Helpers `fulfilled_case(Path) -> tuple[WorkspacePaths,str,str]` và `settlement_count(WorkspacePaths,str) -> int` định nghĩa trong crash test module, dùng A6 public protocol và journal reader, không mutate ledger trực tiếp.

- [ ] RED: `python -m pytest tests/integration/test_visual_request_crashes.py -q`; expected missing fulfillment functions.
- [ ] Match request/hash/claim dưới RunLock trước side effect; ghi staging identity/in-flight revision rồi nhả lock. Tổng hợp batch inventory, gọi A5 image-inspect/image-decode trong isolated worker; không decode trong fulfillment parent. Lấy lại lock, kiểm revision/rawhash/identity và decoded_verified trước promotion/atomic receipt+settlement WAL. Parse/decode failure giữ request reservation khi outcome/cost chưa đối soát, không promote asset lỗi. Duplicate exactfulfillmenthash idempotent; sameIDdifferentbytes/cost6. Brief đổi vẫn settle request cũ, không attach build mới.

```text
fulfill_request(paths: WorkspacePaths, request_id: str, fulfillment_ref: str) -> RequestReceipt
recover_request(paths: WorkspacePaths, request_id: str) -> RequestReceipt
cancel_request(paths: WorkspacePaths, request_id: str) -> RequestReceipt
```

- [ ] Implement unknown accounting: timeoutafterdispatch keepscall+money/quotareservation, noauto-retry; preparedcancel releasesonce; dispatchedcancelintent cannotrefundwithoutproof. Knownactualsettlesonce; actualoverreserve recordsfullobligation+ACCOUNTING_OVERRUNblocksnewgeneration; hostquota costnull not0.
- [ ] Crashinject at before/afterreserve, dispatchintent, toolreceiptbeforefulfill, before/afterWALsettlementcommit; recover each twice and assert deltaonce, notoolrepeat. WrongrequestA→B unchangedboth; stalegrantsettleallowedno newdispatch. Diskerror diagnostics scrub prompt/provider IDs.
- [ ] Thêm fulfillment tests malformed image/decompression bomb/decoder memorykill; parent sống và xử lý recover tiếp theo, previousoutput nguyên vẹn, decoded_verified=false không được promote, worker/staging cleanup đúng identity. Cost unknown giữ reserve, không suy decoder failure là provider no-charge.
- [ ] GREEN: `python -m pytest tests/integration/test_visual_requests.py tests/integration/test_visual_request_crashes.py tests/unit/test_state.py -q`. Commit `git add src/presentation_studio/visual/requests.py src/presentation_studio/models/visual_request.py src/presentation_studio/state.py tests/integration/test_visual_requests.py tests/integration/test_visual_request_crashes.py`; `git commit -m "feat: recover image fulfillment without duplicate spend"`.

### Task A8: CLI seam, schemas và command-status contract

**Files:** Create `visual/cli.py`, `tests/unit/test_visual_cli.py`, `tests/integration/test_visual_contract.py`; Modify `cli.py` parser/_run_command only, `models/reports.py` only compatible validators, `models/__init__.py`, `scripts/generate-schemas.py`; regenerate exact schema files for A models under `schemas/`. No changes `backends/pptx_native.py`.

**Interfaces:** Consumes A1–A7 and existing `CLIResult`, `BuildInput/Result`, `RenderResult`, `QAReport`, `PresentationBackend`. Produces `register_visual_backend(backend_id: str, build: Callable[[BuildInput, WorkspacePaths], BuildResult], render: Callable[[WorkspacePaths,str], RenderResult], export: Callable[[WorkspacePaths,str,str], BuildResult]) -> None`; `dispatch_visual(args: argparse.Namespace) -> CLIResult`; `load_visual_brief(build_input: BuildInput, paths: WorkspacePaths) -> VisualAssetBrief`; `aggregate_review(build: BuildResult, render: RenderResult | None, qa: QAReport | None) -> tuple[str,int]`. Absenthandlers have capabilityunavailable result, not dummyoutput. C/D register through this seam; contract owner alone integrates registry call sites.

- [ ] Write CLI RED tests `validate --visual-brief`, build --deck selection honored, image-request subcommands; stdout exactlyoneJSONresult. Statusparamtest fixes independent command outcomes:

```python
@pytest.mark.parametrize("command,condition,status,exit_code", [
    ("build", "outputs_valid", "passed", 0),
    ("render", "capability_missing", "failed", 3),
    ("audit", "evidence_missing", "unverified", 4),
    ("audit", "qa_failed", "failed", 4),
    ("render", "worker_failed", "failed", 5),
])
def test_status_boundary(command, condition, status, exit_code, visual_cli_case):
    result = visual_cli_case(command, condition)
    assert (result.status, result.exit_code) == (status, exit_code)
```

Fixture `visual_cli_case(command: str, condition: str) -> CLIResult` registers minimal test handlers emitting validated models/real workerresult for build, asserts existing BuildResult kept passed after subsequentrenderfailure; never productionfakeProcessResult.

- [ ] RED `python -m pytest tests/unit/test_visual_cli.py -q`; expected parser rejects visualflag or absentdispatch.
- [ ] Add exact CLI options §7: `validate/build --visual-brief`, `image-request prepare --visual-brief` mutuallyexclusive with `prepare --request --claim-dispatch`, fulfill requiresrequest+fulfillment, recover/cancelrequest; existingworkspace/json convention. No new aggregate command. Build consumes fulfilled/import/cache, neverdispatchestool.
- [ ] Implement handlerregistry and dispatcher, doctor feature-specific capabilities for image-import/host-image/static-html/renderer/image-deck/motion. Register image-deck/html-static only when C/D provide handlers; unknowncap3. Keep native Handler(paths) and Renderer(paths,buildid) unchanged. ExpectedonevisualIDs/outputcount enforces invariant before promotion.

- [ ] Khóa payload adapter: visual build/render/export trả `CLIResult.data.build_id`; audit thêm `data.review_state` và immutable reportref. `BuildInput.backend_options.extensions` chỉ thêm scalar keys `visual-brief-ref`, `visual-brief-sha256`, `visual-semantic-hash`; `load_visual_brief` kiểm cả ba qua A I/O/parity, không nhét callable hoặc object vào flat extensions. HTML export đăng ký C4 `export_image_pptx` khi có C4 capability, nếu chưa có dùng typed unavailable handler/3; không báo export native.

```text
load_visual_brief(build_input: BuildInput, paths: WorkspacePaths) -> VisualAssetBrief
aggregate_review(build: BuildResult, render: RenderResult | None, qa: QAReport | None) -> tuple[str,int]
```

- [ ] Extend generator modelregistry, deterministic schemas; add `--check` to generate expected in memory and compare current bytes without deleting files. Tên file mới chính xác theo convention hiện tại: `VisualAssetBrief.schema.json`, `VisualResult.schema.json`, `ExecutionGrant.schema.json`, `ProjectUsageSnapshot.schema.json`, `CapabilitySnapshot.schema.json`, `EffectivePolicy.schema.json`, `ImageRequest.schema.json`, `ImageFulfillment.schema.json`, `RequestReceipt.schema.json`; nested types nằm trong `$defs`. Normalgeneration deletes stale only its own known schema set; old readerfixture never schema cleanup target. Verify model roundtrip and finite Decimal schemas.
- [ ] Thêm `PromptPack.schema.json`, `VisualWorkerJob.schema.json`, `VisualWorkerResult.schema.json`, `ImageInspection.schema.json` từ A3/A5 vào cùng registry/check; không tạo generator riêng. `visual-brief-sha256` là extension key duy nhất cho raw brief hash trong mọi backend/CLI/test; tên field sidecar `brief_raw_sha256` vẫn giữ schema spec.
- [ ] GREEN: `python scripts/generate-schemas.py`; `python scripts/generate-schemas.py --check`; `python -m pytest tests/unit/test_visual_cli.py tests/integration/test_visual_contract.py tests/integration/test_cli.py -q`; `python -m pytest -q`. Fullsuite expected no native regressions; unavailablelive/platformchecks explicitly excluded from evidence claims, not silentlymarkedpassed.
- [ ] Commit stage explicit A8files plus each generatedschemafilename shown by `git status --short schemas`; no unrelated schema. `git commit -m "feat: expose visual contract commands with honest status boundaries"`.

## Acceptance, risks và rollback

AC07–09/12/15/16/18–20/21–44/45–51 map A1–A8; AC38–44 need real process/filesystem evidence, không puremockpass. A2 cung cấp content projection hoàn chỉnh; A3 bổ sung semantic/input hashes và golden mutation tests. A8 gate requires unfiltered A1–A8suite. E1/E4 protocol E2E chạy A6/A7 fake, E2 host thật chưa được claim.

Rủi ro lớn: legacy1.0 serialization, Decimalmigration, WALatomicity, Windowsprocessenforcement. Securityreview policy/grant/WAL/path/process là gate trước C/D liveuse. Rollback disable visualregistry giữ native; giữ ledgerrequest và assetfulfilled; neverrefund unknownreservation; reject newversions clearly. Không dùng gitreset hoặc xóa workspace. Chưa có capabilityhost/renderer thì A vẫn giao CLIvalidate/policy/protocol/fake tests testable và doctor unavailable trung thực.

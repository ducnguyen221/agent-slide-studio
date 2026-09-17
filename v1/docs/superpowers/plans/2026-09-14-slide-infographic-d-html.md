# Slide Infographic D — Static Reconstruction Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Dựng source HTML/CSS/SVG một slide, render offline, kiểm QA và chỉnh sửa/re-import mà không làm lệch DeckSpec canonical.

**Architecture:** Phase2: hoàn thiện plan, chưa triển khai HTML runtime trong Phase1 IMAGE. Source không tin cậy chỉ được parse/allowlist bên trong A5 isolated worker sau khi memory/timeout/network limits đã gắn; backend/renderer giữ snapshot riêng. D4 mở rộng shared audit C4 cho HTML; IMAGE Phase1 overlay không tiêu thụ D.

**Tech Stack:** Python >=3.12, HTMLParser/XML parser chuẩn, tinycss2 >=1.5.1,<2 cho CSS token tree, Playwright >=1.55,<2 với browser đã cài; pytest9, Pillow12. Dependency tùy chọn `visual-html`, phiên bản được khóa tại E3 trước release.

**Spec:** [Design 1.1.1](../specs/2026-09-14-slide-infographic-design.md), §5–12; [roadmap](2026-09-14-slide-infographic-roadmap.md).

## Global Constraints

- `HTML-RECONSTRUCTION` dùng `overlay|none`, `execution.image_source=import`, calls `0`; không generation ngầm.
- `faithful` khóa content/relations; `inspired-redesign` không bị fail vì pixel khác phần không khóa.
- One-slide source bundle, originalslideID; PNG exact canvas/device scale `1`; pilot1920×1080/safe0.05.
- Source≤`4MiB`, DOM≤`10,000`/depth64, CSS≤`10,000`rules, SVG≤`20,000`elements/`100,000`pathcommands/`4096`stops; no filters.
- A5 aggregate pixels≤`67,108,864`, resident estimate≤`768MiB`, hard worker tree`1GiB`, station2workers/2GiB.
- No script/event handler/iframe/external CSS/SVG, no hidden network/download; missing OS isolation/browser→failed3 before execution.
- HTML editability là `not_applicable` legacy enum + `editable_in=html-css-svg`; PPTX không native.
- Build0 không thay audit; missing evidence unverified4, QA lỗi failed4, worker lỗi5; không sửa WP04.

---

## File map / owner

Owner **Sol runtime**, chỉ thực thi D khi Phase2 được giao. Không dependency D chặn Phase1. D sở hữu file HTML mới; validate files đã tạo bởi C4 thì D4 chỉ Modify, không tạo QA engine khác. Contract owner A chỉnh dependency/CLI/A5 worker registry. Không dùng regex để chứng nhận CSS/SVG an toàn.

| Files | Responsibility |
|---|---|
| `src/presentation_studio/visual/html_safety.py` | Tokenized source allowlist, complexity, asset references |
| `src/presentation_studio/visual/html_source.py` | Canonical node mapping, static source/overlay bundle |
| `src/presentation_studio/visual/html_edit.py` | Layout-only checks và canonical candidate import |
| `src/presentation_studio/backends/html_static.py` | HTML backend build/source snapshot |
| `src/presentation_studio/renderers/html.py` | Offline browser worker, fonts/assets readiness/DOM metrics |
| `src/presentation_studio/validate/{__init__,visual,visual_rules}.py` | QA dispatcher, 10 independent gates |
| `tests/unit/test_visual_html_safety.py`, `tests/unit/test_visual_qa.py` | Parser/QA regression |
| `tests/integration/test_visual_html_render.py`, `tests/integration/test_visual_html_edit.py` | Real browser/edit loop |
| `tests/fixtures/visual/html/{four-card.html,four-card.css,relations.svg,README.md}` | Neutral source fixtures/rights |

Browser context mới không dùng profile/cookies cá nhân; đóng context trước browser. CSS phải kiểm token/AST, kể cả escapes và nested functions. Đây là cơ sở lựa chọn API, không chứng minh sandbox: [Playwright Browser API](https://playwright.dev/python/docs/api/class-browser), [tinycss2 API](https://doc.courtbouillon.org/tinycss2/stable/api_reference.html).

### Task D1: Source safety và complexity admission

**Files:** Create html_safety.py, safety tests, HTML fixture files; contract owner thêm optional dependency `visual-html` vào pyproject, không cài browser tự động.

**Interfaces:** Consumes A5 `VisualWorkerJob`, `WorkerOperation`, `run_visual_worker`, `read_worker_result`, `admit_resources` và VisualAssetBrief/AssetManifest. Produces `SourceInspection(files: dict[str,bytes], node_ids: list[str], referenced_assets: list[str], inventory: ResourceInventory)`; parent `inspect_static_source(paths: WorkspacePaths, files: dict[str,bytes], brief: VisualAssetBrief, manifest: AssetManifest) -> SourceInspection`; worker-only `parse_static_source_in_worker(job: VisualWorkerJob) -> SourceInspection`. Parent chỉ boundbytes/stage/hash; typed html-inspect kiểm encoding/container trong worker, html-parse parse HTML/XML/CSS/count/parity ở worker đã cách ly. Dict keys là normalized bundle paths, không URL/absolute path. Main không parse trước isolation.

- [ ] Viết attack test trước parser:

```python
@pytest.mark.parametrize("payload", [
    b'<svg><script>alert(1)</script></svg>',
    b'<svg><use href="https://invalid.example/x.svg#x"/></svg>',
    b'<svg><foreignObject><iframe/></foreignObject></svg>',
])
def test_unsafe_svg_never_reaches_renderer(payload, source_workspace):
    with pytest.raises(VisualError) as exc:
        inspect_static_source(source_workspace, {"graphics.svg": payload}, load_brief("HTML-RECONSTRUCTION"), manifest_fixture())
    assert exc.value.code == "UNSAFE_SOURCE"
```

`manifest_fixture() -> AssetManifest` reads A1 fixture. `source_workspace` fixture init một neutral WorkspacePaths bằng A primitive; test phải gọi isolated parser thật, không direct parser trong pytest parent.
- [ ] RED `python -m pytest tests/unit/test_visual_html_safety.py -q`; expected missing module. Missing tinycss2 là environment/capability chưa cài, không được tính parser RED đã chứng minh.
- [ ] Parse HTML bằng stack, deny unknown tags/attributes, event names case-insensitive, duplicate node IDs. Allowlist HTML là html/head/body/meta/title/style/link/div/section/span/p/h1–h6/ul/ol/li/img/svg/desc; meta chỉ charset=UTF-8 hoặc viewport, link chỉ stylesheet tới manifest-local CSS, không refresh/preload. Thuộc tính HTML cho phép id/class/lang/role/aria-label, style đã qua CSS parser; img thêm src/alt/width/height. Mapping chỉ thêm data-edge-id/data-from/data-to/data-kind/data-label với giá trị đã kiểm parity. XML reject DTD/ENTITY/processing instruction trước parse; SVG allow svg/g/defs/path/rect/circle/ellipse/line/polyline/polygon/text/tspan/title/desc/linearGradient/radialGradient/stop/use; thuộc tính chỉ geometry, viewBox, d/points, fill/stroke/opacity/font/text-anchor/transform và fragment reference đã resolve. SVG use chỉ fragment cùng document và ID có thật; unknown attr/tag fail closed.
- [ ] Parse CSS token tree bằng tinycss2: allow static layout/typography/color/transform, deny @import/animation/external URL; localfont/image URL chỉ resolvedmanifest bytehash. Traverse nested functions/url tokens và decoded CSS escapes; reject parse error/unrecognized declaration. SVG filter/callback/external resources không hỗ trợ. Code boundary:

```text
inspect_static_source(paths: WorkspacePaths, files: dict[str,bytes], brief: VisualAssetBrief, manifest: AssetManifest) -> SourceInspection
parse_static_source_in_worker(job: VisualWorkerJob) -> SourceInspection
```

- [ ] Mọi parser/count chạy trong html-inspect/html-parse worker đã được A5 admission/isolation, trước browser render. Count DOM/depth/CSS/SVG/path/gradient và aggregate inventory; typed parse-result inputfailure2, worker hardkill/timeout5. Không parse source ở main để quyết có cần isolation hay không. Worker build đã cách ly gọi worker-only routine trực tiếp, không spawn lồng lease1/project.
- [ ] AC38–40 tests malformed XML/CSS, compressed payload bomb bị reject, deeply nested DOM/repeated SVG paths và actual parser-memorykill. Assert parentPID sống, harmless nextjob chạy được, ownedchild chết/lease released, cleanup chỉ staging đúngidentity và previousoutputhash nguyên. Không silentlystrip unsafe input rồi pass.
- [ ] GREEN `python -m pytest tests/unit/test_visual_html_safety.py tests/unit/test_visual_resources.py -q`; dependency absent expected capabilityunavailable test, không skip safety assertions. Commit D1files và owner dependencydelta: `git commit -m "feat: validate static slide source before isolated rendering"`.

### Task D2: Canonical source mapping, overlay và one-slide build

**Files:** Create html_source.py, html_static.py; Modify HTML integration test and fixture sources. Contract owner A8 registers `html-static`.

**Interfaces:** Consumes A `assert_content_parity`, `project_build_deck`, NumberFormatter, worker; D1inspection. Produces `build_static_source(deck: DeckSpec, brief: VisualAssetBrief) -> dict[str,bytes]`; `build_overlay_source(deck: DeckSpec, brief: VisualAssetBrief, background: Asset) -> dict[str,bytes]`; `assert_source_parity(files: dict[str,bytes], brief: VisualAssetBrief) -> None`; `HtmlStaticBackend.capabilities() -> BackendCapabilities`, `.build(build_input: BuildInput, paths: WorkspacePaths) -> BuildResult`.

- [ ] Viết parity test với actual nodeID/number/string thay vì chỉ count:

```python
def test_dom_only_number_change_rejected():
    deck = DeckSpec.model_validate(fixture_json("deck-chart-1.1"))
    brief = load_brief("HTML-RECONSTRUCTION")
    files = build_static_source(deck, brief)
    files["index.html"] = files["index.html"].replace("18,5".encode(), "19,5".encode())
    with pytest.raises(VisualError, match="CONTENT_PARITY_FAILED"):
        assert_source_parity(files, brief)
```

- [ ] RED `python -m pytest tests/integration/test_visual_html_render.py -q -k source`; expected missing source functions.
- [ ] Generate escapedtext DOM/SVG with runtime-derived `visual-<nodeID>` IDs; node/edge mapping includes required branch, reading_order explicit, unitshared exactlyonce, no fixed4cardlayout. Use preferredboxes/archetype and profile values, capacityoverflow reported not texttruncated. Overlay inserts only selected rasterbackground, meaningfultext stays DOM.
- [ ] Implement parity canonical→brief→source, numeric formatter/Fact stays A; requirednode IDs/edge endpoints/types/labels checked. Build actualworker sourcebundle with one-slide count, accessibility and inputmanifest; no screenshot as substitute for source. No sourceasset read from outside boundmanifest.

```text
build_overlay_source(deck: DeckSpec, brief: VisualAssetBrief, background: Asset) -> dict[str,bytes]
assert_source_parity(files: dict[str,bytes], brief: VisualAssetBrief) -> None
```

- [ ] Tests fullposterbackground fails requirededitablemapping, missingbranch fail despite mockhighSSIM, title/Fact/unit pair exact, sourcebundle1slide s03, htmlsource not_applicable plus declarededitable_in; until editproof D5 mappingeditable flag remainsfalse/unverified, never claim by DOMexistence alone.
- [ ] GREEN `python -m pytest tests/integration/test_visual_html_render.py -q -k source`; `python -m pytest tests/unit/test_visual_projection.py -q`. Stage D2files explicitly; `git commit -m "feat: build canonical editable static visual sources"`.

### Task D3: Offline browser render và owned lifecycle

**Files:** Create renderers/html.py; Modify HTML render integrationtest. Aowner adds html workeroperation registration and dependency capability handling only.

**Interfaces:** Consumes D1/D2source, A5`run_visual_worker`. Produces `HtmlRenderEvidence(build_id: str, input_hash: str, png_sha256: str, boxes: dict[str,dict], texts: dict[str,str], font_hashes: dict[str,str], asset_hashes: dict[str,str], errors: list[str], renderer_version: str)` strict sidecar; `render_html(paths: WorkspacePaths, build_id: str) -> RenderResult`; `read_html_evidence(paths: WorkspacePaths, build_id: str) -> HtmlRenderEvidence`. Boxes hold x/y/width/height/visible/scroll dimensions only, not arbitrary executable locator.

- [ ] Viết capability and size tests: missingbrowser/isolation→3 with no spawn; installed isolatedbrowser→exactviewport/image dimensions. `html_render_case(tmp_path)` runs D2build with only bundled localassets:

```python
def test_offline_render_exact_canvas(tmp_path, isolated_browser):
    paths, build_id = html_render_case(tmp_path)
    result = render_html(paths, build_id)
    assert result.status == "passed"
    assert result.dimensions is not None
    assert (result.dimensions.width, result.dimensions.height) == (1920, 1080)
    assert list(result.slides) == ["s03"]
    assert read_html_evidence(paths, build_id).errors == []
```

`RenderResult.dimensions` hiện là `RenderDimensions` với hai field width/height; giữ model này, không tạo shape cạnh tranh.
- [ ] RED `python -m pytest tests/integration/test_visual_html_render.py -q -k render`; expected missing renderer. Actualbrowser availability reported separately.
- [ ] Implement freshbrowsercontext with viewportwidth/height, device_scale_factor1, accept_downloadsfalse, service_workersblock; no userprofile, persistentstorage or permissions. Route only synthetic same-origin fixture URLs fulfilled from alreadyboundbyte map, abort all otherrequests and record them; no localHTTPserver needed. OSnetwork isolation A5 remains required even with routeblocking.
- [ ] Trusted renderer readiness script waits fonts.ready and image.decode promises, then two animationframes; document JS from source is forbidden, only fixedpackage instrumentation allowed. Fonts match requested families/resolvedhashes; JS/console/font/asset failures are measured, timeout closes only ownedprocess tree. Capture page screenshot exactviewport, not full_page scrollheight.

```text
render_html(paths: WorkspacePaths, build_id: str) -> RenderResult
read_html_evidence(paths: WorkspacePaths, build_id: str) -> HtmlRenderEvidence
```

- [ ] Test corruptedfont/slowasset/decodeerror/consoleerror/overflow/memorykill/timeout with prioroutput preserved; no externalrequests, downloads, processes remaining. Record realengine/font versions/hash. Motionrequested unavailable3 while staticrevision preserved; no HyperFrames install.
- [ ] GREEN `python -m pytest tests/integration/test_visual_html_render.py tests/integration/test_visual_process.py -q`. Realbrowserless host gives truthful missinggate; puretests may pass but D3visualdelivery remainsunverified. Stage D3files and ownerregistrationdelta; `git commit -m "feat: render static visual slides in an offline owned browser"`.

### Task D4: Ten independent QA gates và immutable audit

**Files:** Modify validate init/visual/visual_rules và QAunit tests đã tạo C4; Modify HTML render integrationtest; Aowner wires HTML audit evidence adapter only. Shared audit contract không đổi, không tạo QA engine song song.

**Interfaces:** Consumes `QAReport`/`QACheck` từ `models/reports.py`, A `aggregate_review`, D3evidence, CRenderResult. Produces `audit_visual(paths: WorkspacePaths, build_id: str) -> QAReport`; `evaluate_visual_rules(brief: VisualAssetBrief, evidence: dict) -> list[QACheck]`. Evidence dict được validate tagged measurement/reviewer records theo rule ID và artifacthash, không nhận arbitraryscore.

- [ ] Write semanticfailnotmasked test:

```python
def test_high_fidelity_cannot_hide_missing_branch():
    checks = evaluate_visual_rules(load_brief("HTML-RECONSTRUCTION"),
                                   evidence_case("missing-branch-high-ssim"))
    semantic = next(c for c in checks if c.rule_id == "visual-semantic")
    assert semantic.status == "failed"
```

`evidence_case(name: str) -> dict` is neutral QAfixture in testmodule; reference lockedbranchr1 missing in measuredmapping, SSIM0.99 applies only geometryregion.
- [ ] RED `python -m pytest tests/unit/test_visual_qa.py -q`; expected missingruleengine.
- [ ] Implement đủ mười rule ID §11: `visual-semantic`, `visual-vietnamese`, `visual-canvas`, `visual-geometry`, `visual-fonts-assets`, `visual-runtime`, `visual-fidelity`, `visual-editability`, `visual-provenance-rights`, `visual-handoff`. Mỗi rule trả passed/failed/unverified/not_applicable với evidence/lý do độc lập. None mode kiểm absence of glyphs qua reviewer/vision; thiếu OCR/vision không thành blanktextpass.
- [ ] Verify evidence input/artifacthash first; DOMhidden/occludedtext is not textpass; compare exactNFCcanonicaltext and visiblegeometry, require manual/vision review for finalrasterreading/fidelity. SSIM/IoU/DeltaE optional lockedregion metrics, no aggregate threshold; inspiredredesign only lockedfeatures. PPTXhandoff checks its artifact not inheritedHTML.

```text
audit_visual(paths: WorkspacePaths, build_id: str) -> QAReport
evaluate_visual_rules(brief: VisualAssetBrief, evidence: dict) -> list[QACheck]
```

- [ ] Write reportrevision underRunLock using A I/O; neveroverwritepreviousQA. Status tests buildpassed0+reviewunverified, auditmissing4unverified, knownfailure4needs_revision even missingreview; maxrepair=minproject/grant/brief, noauto loopbudget0. Rightschange reevaluates despite semantic hash unchanged.
- [ ] GREEN `python -m pytest tests/unit/test_visual_qa.py tests/integration/test_visual_html_render.py tests/unit/test_visual_cli.py -q`. Stage D4files and ownerauditdelta; `git commit -m "feat: audit infographic content fidelity and editability independently"`.

### Task D5: Layout-only edit và semantic candidate re-import

**Files:** Create visual/html_edit.py, HTMLedit integrationtest; Modify html_source.py/rules only for validatededit mappings. Aowner adds CLI `validate --source <relative-dir> --visual-brief` and `--import-candidate <relative-json>` mutuallyexclusive validationmode; importwrites candidateonly, never canonicaloverwrite.

**Interfaces:** Consumes Aprojection/hash, D1–D4. Produces `validate_layout_edit(deck: DeckSpec, brief: VisualAssetBrief, files: dict[str,bytes]) -> None`; `extract_content_candidate(deck: DeckSpec, brief: VisualAssetBrief, files: dict[str,bytes]) -> DeckSpec`. Candidate is sourcechange proposal boundoriginrawhash; producer explicitly accepts into newcanonicalrevision before reproject/build.

- [ ] Write three-source parity test and allowedgeometry test:

```python
def test_layout_move_preserves_content_hash(tmp_path):
    deck, brief, files = editable_case(tmp_path)
    before = content_projection(deck, "s03")
    files["styles.css"] += b"\n#visual-group-a { left: 55%; }\n"
    validate_layout_edit(deck, brief, files)
    assert content_projection(deck, "s03") == before
```

`editable_case(Path) -> tuple[DeckSpec,VisualAssetBrief,dict[str,bytes]]` fixture uses D2source; test adds secondgroup geometrymove while reading_order/edges unchanged, not changingmeaning.
- [ ] RED `python -m pytest tests/integration/test_visual_html_edit.py -q`; expected missingeditmodule.
- [ ] Implement layout-only validation allows position/spacing/decorativecolor/font/icon and visualorder only when semanticreadingorder preserved; text/numeric/unit/semanticicon/edge/readingorder change→CONTENT_PARITY_FAILED2. Sourcebytechange invalidatesinputhash even samecontenthash; oldQA not reused.
- [ ] Implement candidate extraction by stable DOM IDs + typedbindings, numeric cannot parse localizeddisplay into lossycanonicalreplacement: candidate retains rawvalue unless explicit exactnumeric edit supplied; conflict label/value/unit mapped samechartdatum. CandidateJSON reviewed/reconciled then producerwrites canonicalrevision; brief-only/DOM-only modifications fail beforebuild.

```text
extract_content_candidate(deck: DeckSpec, brief: VisualAssetBrief, files: dict[str,bytes]) -> DeckSpec
validate_layout_edit(deck: DeckSpec, brief: VisualAssetBrief, files: dict[str,bytes]) -> None
```

- [ ] E2E edit canonical18.5→19.5/unit“lần”→reproject→render/audit; locale/precision changes keepFact/contenthash and change semantic/input; ≈markerrounding case. Movegroups contenthashsame,inputdifferent; requirednode edit-render evidence enables mappingeditabletrue for thattestedrepresentation; fullposter stillfails.
- [ ] GREEN `python -m pytest tests/integration/test_visual_html_edit.py tests/integration/test_visual_html_render.py tests/unit/test_visual_qa.py tests/unit/test_visual_projection.py -q`; `python -m pytest -q`; schemascheck. Commit D5files and ownerCLI delta explicitly; `git commit -m "feat: preserve canonical content through visual edit and reimport"`.

## Acceptance, risk và rollback

D1coversAC10/12/38/39, D2AC04/05/13/32/34/51, D3AC11/18/20/40/44, D4AC01/04/05/17–19, D5AC06/15/32/33/36/37/45–48 and E3. Platform memory/network isolation is real gate, not Playwright routeclaim. Missing vision/manualreview neverpassed. Rollback disablehtml-static route/versionedQA rules, preserve source/PNG/priorreports; re-audit oldartifacts afterrulefix, no destructiveoverwrite/nativechange.

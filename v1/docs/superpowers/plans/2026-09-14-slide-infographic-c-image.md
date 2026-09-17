# Slide Infographic C — IMAGE Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Tạo pipeline IMAGE import/cache/fulfilled host → exact PNG → raster PowerPoint/notes và assembly có thể kiểm thử offline.

**Architecture:** Phase1 IMAGE chạy ngay, không dependency D. Backend tiêu thụ A projection/policy/request; trusted overlay compiler lấy nguyên text canonical, xuất layout/SVG/source và raster bằng Pillow/font đã khóa. D Phase2 tái dựng reference tùy ý là subsystem khác; raw/build/render/PPTX giữ hash và raster declaration riêng.

**Tech Stack:** Python >=3.12, Pillow >=12.2,<13, python-pptx >=1.0.2,<2, pytest >=9,<10; A isolated image workers, deterministic overlay fonts/layout; không browser dependency Phase1.

**Spec:** [Design 1.1.1](../specs/2026-09-14-slide-infographic-design.md), §5–12; [roadmap](2026-09-14-slide-infographic-roadmap.md).

## Global Constraints

- IMAGE text `baked|overlay|none`; fit `reject|contain|crop-approved`, không stretch.
- Mặc định IMAGE=`overlay`, background generation không chứa body text; canonical text được render deterministic để giữ chính tả/safe margins. Baked best-effort và bắt buộc QA; mục tiêu một primary generation, không guarantee một call hoặc retry ngoài budget.
- PNG final exact canvas, pilot `1920×1080`; raw và final hash/dimensions giữ riêng.
- Mọi generation qua prepare/claim/fulfill; import/cache budget0 gọi provider `0` lần.
- Một visual originalslideID, mọi BuildResult output `slide_count=1`; assemblyN có outputcountN, PNG riêng trong RenderResult.
- PPTX full-slide PNG `editability=raster`; notes_included chỉ true khi notes XML được reopen và đối chiếu.
- Missing prompt/stylehash externalimport→`source_kind=user`, generationnull; unknown model/seed/cost không bịa.
- Memory/input/process giới hạn A5; offline/no hidden download; không sửa WP04 native.

---

## File map / owner

Owner **Sol runtime**. Shared models/CLI/registration do contract owner A8 tích hợp; không sửa chung file cùng worker D.

| Files | Responsibility |
|---|---|
| `src/presentation_studio/assets/__init__.py`, `manifest.py`, `cache.py`, `providers.py` | Import/lineage, validatedcache, providerport |
| `src/presentation_studio/backends/image_deck.py` | Single visual build recipe, PPTX export, assembly |
| `src/presentation_studio/renderers/__init__.py`, `image.py`, `overlay.py` | Pillow final raster, trusted deterministic text overlay/source compiler |
| `src/presentation_studio/validate/{__init__,visual,visual_rules}.py` | C4 shared IMAGE audit contract; D4 mở rộng HTML Phase2 |
| `tests/integration/test_visual_images.py` | Import/fit/cache/provenance |
| `tests/integration/test_visual_host_seam.py` | Fakehost protocol, optionalrealhost boundary |
| `tests/integration/test_visual_image_pptx.py` | Raster/notes/reopen/render/assembly |
| `tests/fixtures/visual/images/README.md` | Proceduralneutralfixture recipe/rights |

Fixtures binary tạo trong test tmpworkspace bằng Pillow từ script inline test, không commit riêng ảnh người dùng. Recipebuild là presentation source JSON strict `schema_version, slide_id, asset_ids, canvas, fit_policy, crop, text_policy, overlay_source_ref, notes_ref, semantic_hash, input_hash`; sourcebundle đóng gói recipe+inputbytes+accessibility cần cho một slide, không gọi QAreport là presentationartifact. IMAGEbaked/none không tạo HTMLsource; bundle khai not_applicable/none, không editable reconstruction. Final PNG do render command tạo; recipebundle đủ BuildResultoutput thực sau workerbuild.

### Task C1: Bounded import và content-addressed cache

**Files:** Create assets init/manifest/cache, image test/fixtureREADME trong map.

**Interfaces:** Consumes A `read_visual_file`, `admit_resources`, `VisualAssetBrief`, `AssetManifest`, `VisualHashes`, `EffectivePolicy`. Produces `import_image(paths: WorkspacePaths, asset_id: str, relative_path: str, brief: VisualAssetBrief) -> Asset`; `lookup_image_cache(paths: WorkspacePaths, cache_key: str, brief: VisualAssetBrief) -> Asset | None`; `store_image_cache(paths: WorkspacePaths, cache_key: str, asset: Asset) -> None`; `image_cache_key(request: ImageRequest, model_revision: str | None, seed: int | None, profile_content_hash: str) -> str`.

- [ ] Write test budget0 explicitimport counts0; corruptioncache rejected. Test helper `image_case(tmp_path)` init workspace/corebrief/manifest and generate RGB300×200 neutralimage, no liveprovider:

```python
def test_import_unknown_generation_stays_user(tmp_path):
    paths, brief, image_ref = image_case(tmp_path)
    asset = import_image(paths, "reference", image_ref, brief)
    assert asset.source_kind == "user"
    assert asset.generation is None
    assert (asset.width, asset.height) == (300, 200)
```

- [ ] RED `python -m pytest tests/integration/test_visual_images.py -q -k "import or cache"`; expected missing assetmodule.
- [ ] Parent chỉ bounded bytes/header/hash qua A5; gọi inspect_image_asset/decode_image_asset trong worker đã enforce memory/timeout/network isolation. Chỉ promote khi decoded_verified và aggregate admission đạt. Worker build/render dùng routine nội bộ trong cùng isolated worker, không decode input untrusted ở main. Rights/metadata có căn cứ, unknown redistributable=false.
- [ ] Implement cachekeyallowlist §6 including actualprompt/rawreferences/requestedsize/modelrevisionknown/profilevaluehash; unknownrevision only explicitworkspaceartifact selection. Cachelookup rehashoutputbytes và reevaluatecurrentrights/policy; corrupt miss/error không auto generation khi budget0.

```text
lookup_image_cache(paths: WorkspacePaths, cache_key: str, brief: VisualAssetBrief) -> Asset | None
store_image_cache(paths: WorkspacePaths, cache_key: str, asset: Asset) -> None
```

- [ ] Test AC07/08/14/15: zero+cachemiss3call0, importwithunknownmetadata, referencebytechangedkey, rightsrevokedreject, knowncachehitcall0; malformed/hugecompressedheader fails A7beforefull decode; twoimportsdedupbytesnotrightsrecord.
- [ ] GREEN `python -m pytest tests/integration/test_visual_images.py -q -k "import or cache"`. Commit `git add src/presentation_studio/assets/__init__.py src/presentation_studio/assets/manifest.py src/presentation_studio/assets/cache.py tests/integration/test_visual_images.py tests/fixtures/visual/images/README.md`; `git commit -m "feat: import and cache visual images with verified lineage"`.

### Task C2: One-slide recipe build và exact PNG render

**Files:** Create `backends/image_deck.py`, `renderers/__init__.py`, `renderers/image.py`, `renderers/overlay.py`; Modify image tests. Contract owner registers `image-deck` A8, worker operations qua A5registry; owner alone changes sharedregistration.

**Interfaces:** Consumes A `PresentationBackend`, `project_build_deck`, `run_visual_worker`; C1assets. Produces `ImageDeckBackend.capabilities() -> BackendCapabilities`, `ImageDeckBackend.build(build_input: BuildInput, paths: WorkspacePaths) -> BuildResult`; `render_image(paths: WorkspacePaths, build_id: str) -> RenderResult`; `render_fitted_image(source: bytes, brief: VisualAssetBrief) -> bytes` (PNG). Build recipebundle onevisual is noneditablepresentation source, not finalPNG/QA report.

Thêm C2 `build_image_overlay_source(brief: VisualAssetBrief, font_assets: dict[str,bytes]) -> dict[str,bytes]`, `render_image_overlay(background_png: bytes, brief: VisualAssetBrief, font_assets: dict[str,bytes]) -> bytes`, đều worker-only. Source gồm escaped trusted index.html/overlay.svg/layout.json với text, box, wrapping và font hashes đồng nhất; không nhận arbitrary HTML/CSS/SVG từ reference. D1 parser không được gọi trong Phase1.

- [ ] Write wrongaspect test before Pillow implementation:

```python
def test_reject_wrong_aspect(tmp_path):
    paths, brief, image_ref = image_case(tmp_path)
    raw = read_visual_file(paths, image_ref, 32 * 2**20)
    with pytest.raises(VisualError) as exc:
        render_fitted_image(raw, brief)
    assert exc.value.code == "CANVAS_MISMATCH"
```

- [ ] RED `python -m pytest tests/integration/test_visual_images.py -q -k "fit or aspect or single_slide"`; expected missing renderfunction.
- [ ] Implement IMAGEbuildworker validates exactoneprojectedslide/approvedbrief/rawasset, freezes recipebundle/inputmanifest/accessibility with hashes. ActualprocessresultfromA7worker required; outputbundlecount1; original s03/index/origindeckhashsidecar. Buildpassed0reviewunverified, no generatedhostcall.
- [ ] Implement fit Pillow path: rejectratio before resize; contain preservesaspect≤1pixelrounding then explicitpadding/background; approvedcrop checks bounds+approval+requiredcontent evidence, then proportionalresize. None/baked not OCRrewrite. Render exactPNG into spec slides/slideID.png and RenderResultdimensions/originID.
- [ ] Overlay compiler dùng text canonical NFC nguyên chuỗi, font bytes/hash từ ProfileLock, measured glyph coverage và pinned layout engine; wrap theo font metrics, giữ safearea, không truncate/rút gọn. Overflow/missing glyph fail QA/input theo boundary, không tự giảm cỡ chữ vô hạn. Pillow render từ cùng positioned runs như SVG; không browser. Source editable chưa có edit-proof ghi unverified, PNG/PPTX luôn raster. Test sửa nhãn canonical/re-project và font-byte/hash invalidation.

```text
render_fitted_image(source: bytes, brief: VisualAssetBrief) -> bytes
render_image(paths: WorkspacePaths, build_id: str) -> RenderResult
```

- [ ] Test contain300×200→1920×1080 width1620, left/right150, no markerlost; raw/finalhashdifferent; rejectnocrop; cropunapproved2. Test s03from5slidesbundlecount1 and no unselectedcontent, corruptedsourcebeforeRenderhashreject, immutablepreviousrevision.
- [ ] GREEN `python -m pytest tests/integration/test_visual_images.py -q`; `python -m pytest tests/integration/test_visual_contract.py -q`. Commit `git add src/presentation_studio/backends/image_deck.py src/presentation_studio/renderers/__init__.py src/presentation_studio/renderers/image.py src/presentation_studio/renderers/overlay.py tests/integration/test_visual_images.py`; contractowner stages only its registrationdelta; `git commit -m "feat: build IMAGE visuals with deterministic text overlay"`.

### Task C3: Fake provider và host seam không implicit dispatch

**Files:** Create `assets/providers.py`, host seam integrationtest; Modify image test if protocolbinding fixtures required.

**Interfaces:** Consumes A6/A7 `prepare_request`, `claim_dispatch`, `read_request`, `fulfill_request`; C1import/cache. Produces `HostImagePort` với `identity: str`, `capabilities() -> CapabilitySnapshot`, `execute(request: ImageRequest, claim: RequestReceipt) -> ImageFulfillment`; `dispatch_host_request(paths: WorkspacePaths, request_id: str, host: HostImagePort) -> RequestReceipt`. Port injection from trustedhostregistry, not brief callable/URL; unavailableport fails3. FakeHost only tests, no production “success” default.

- [ ] Write fakehost protocol test with `FakeHost` counts, emits proceduralPNG+receiptknownquota; capabilityfixturehostquota1:

```python
def test_build_never_calls_host(tmp_path):
    paths, request_id, host = prepared_host_case(tmp_path)
    assert host.calls == 0
    receipt = dispatch_host_request(paths, request_id, host)
    assert receipt.outcome == "succeeded"
    assert host.calls == 1
    assert recover_request(paths, request_id).outcome == "succeeded"
    assert host.calls == 1
```

`prepared_host_case(Path) -> tuple[WorkspacePaths,str,FakeHost]` defined in testmoduleusingAprotocol/trustedtestgrant. Add separate buildbeforefulfill assertionfailed3 withhostcalls0.
- [ ] RED `python -m pytest tests/integration/test_visual_host_seam.py -q`; expected missing providersmodule.
- [ ] Implement bridge nhận request prepared, gọi `claim_dispatch(paths, request_id, host.identity)` đúng một lần rồi xác minh claim/snapshot trước host; request đã dispatch không được helper gọi lại. Hostreturn copied via boundedimport and A6fulfill. Host bên ngoài CLI tự claim/fulfill theo A8, không gọi helper này sau claim. No fallback to ChatGPTUI/networkCLI; missingreceipt/bytehandoff=capability3, notsuccessfromfilename.

```text
dispatch_host_request(paths: WorkspacePaths, request_id: str, host: HostImagePort) -> RequestReceipt
HostImagePort.execute(request: ImageRequest, claim: RequestReceipt) -> ImageFulfillment
```

- [ ] Test success, unknowncosttimeout5+reservationheld, providerratelimit5+noimplicitretry, toolfinishedbeforefulfill recoverreceipt0newcall, stalegrantclaimdeny, briefchangedsettlesold; providerrequestID onlyfulfillment, neverlocalIDsubstitution. Rawgenerationobservations unknownflagscomplete.
- [ ] GREEN `python -m pytest tests/integration/test_visual_host_seam.py tests/integration/test_visual_request_crashes.py -q`; zerorealhostcalls. Commit `git add src/presentation_studio/assets/providers.py tests/integration/test_visual_host_seam.py tests/integration/test_visual_images.py`; `git commit -m "feat: connect image host through durable fulfillment seam"`.

### Task C4: Overlay và raster PPTX/notes handoff

**Files:** Modify `backends/image_deck.py`, `renderers/image.py`; Create PPTXintegrationtest, `validate/{__init__,visual,visual_rules}.py`, `tests/unit/test_visual_qa.py`. Phase1, không depends D. D4 Phase2 sẽ Modify các QA files này thay vì tạo engine khác.

**Interfaces:** Consumes C2 deterministic overlay/PNG và Aresultmapping. Produces `export_image_pptx(paths: WorkspacePaths, build_id: str, format: str) -> BuildResult`; `inspect_image_pptx(pptx_bytes: bytes, expected_slide_ids: list[str], expected_notes: list[str]) -> list[str]`; shared `audit_visual(paths: WorkspacePaths, build_id: str) -> QAReport`, `evaluate_visual_rules(brief: VisualAssetBrief, evidence: dict) -> list[QACheck]`. Đây là QA contract của D4 được hiện thực cho IMAGE Phase1; D4 chỉ bổ sung HTML evidence/measurements Phase2, không chặn C5.

- [ ] Write notesraster test:

```python
def test_pptx_notes_are_embedded(tmp_path):
    paths, build_id = rendered_image_case(tmp_path)
    result = export_image_pptx(paths, build_id, "pptx")
    artifact = result.outputs[0]
    assert artifact.editability == "raster"
    assert artifact.notes_included is True
    pptx = read_visual_file(paths, str(artifact.path), 128 * 2**20)
    assert inspect_image_pptx(pptx, ["s03"], ["Ghi chú trung tính"]) == []
```

`rendered_image_case(Path) -> tuple[WorkspacePaths,str]` fixture runs C2publicbuild/render, source notes exactstring shown; no forgedBuildResult.
- [ ] RED `python -m pytest tests/integration/test_visual_image_pptx.py -q -k "notes or overlay"`; expected missingexportfunction.
- [ ] Thêm shared QA RED test trong `tests/unit/test_visual_qa.py`, fixture `image_audit_case(tmp_path)` chạy C2 build/render nhưng chưa có manual/vision review; không fake report. Run `python -m pytest tests/unit/test_visual_qa.py -q` expected missing audit_visual trước implementation.

```python
def test_image_without_review_remains_unverified(tmp_path):
    paths, build_id = image_audit_case(tmp_path)
    report = audit_visual(paths, build_id)
    assert report.summary.unverified > 0
```

Thêm fixture confirmedoverflow để QA fail dù metric cao; expected review needs_revision/4. Test approved-helper của C5 phải nộp evidence rồi gọi engine thật, không sửa summary bằng tay.
- [ ] Dùng overlay compiler C2, không browser/D fallback. Shared audit thực hiện đủ10 rule IDs §11 với IMAGE evidence: exact canonical text/relations, Vietnamese, canvas/safearea, measured glyph boxes/overflow, lockedfonts/assets, worker runtime, fidelity, editability, rights, handoff. Final raster/vision/manual evidence thiếu→unverified4, confirmedfailure→needs_revision4; bằng chứng đúng input/artifacthash, report immutable. HTML-specific measurement chưa áp dụng phải ghi lý do, không giả HTML passed. Default raster target không yêu cầu editable reconstruction.
- [ ] Implement PPTX worker with python-pptx, samecanvasdimensions, exactlyonepicture/slide plus actualnotes `notes_slide.notes_text_frame.text`; reopen zip/python-pptx verify slideorder/mediahash/notesXML. native/mixedrequired→EDITABILITY_UNSUPPORTED3; notesnotembeddedfalseandhandoffQAfailed4.

```text
export_image_pptx(paths: WorkspacePaths, build_id: str, format: str) -> BuildResult
inspect_image_pptx(pptx_bytes: bytes, expected_slide_ids: list[str], expected_notes: list[str]) -> list[str]
```

- [ ] GREEN `python -m pytest tests/integration/test_visual_image_pptx.py tests/unit/test_visual_qa.py -q`; actual PowerPoint render evidence là E1 platformgate, không thay bằng ZIP reopen. Stage C4 backend/render/test và validate files; `git commit -m "feat: export raster PowerPoint and audit IMAGE handoff"`.

### Task C5: Ordered N-slide assembly và complete IMAGE E2E

**Files:** Modify `backends/image_deck.py`, PPTX/image integrationtests. Acontractowner adds assembly export option `--visual-builds` to A8export onlyafter parser test, not new lifecycle/command.

**Interfaces:** Depends C4 shared audit_visual contract (cùng contract D4, hiện thực IMAGE đã chuyển sang Phase1 C4 theo ưu tiên mới), không chờ HTML runtime. Consumes approved current QA/VisualResult đúng input/artifact hashes cho C2/C4visuals. Produces `assemble_image_deck(paths: WorkspacePaths, visual_build_ids: list[str]) -> BuildResult`; CLI `presentation export --workspace <root> --build <anchor-build> --format pptx --visual-builds <id1,id2> --json`. Rendered nhưng chưa audit bị từ chối; không nới gate.

- [ ] Write orderedinvariant test:

```python
def test_assembly_preserves_explicit_order(tmp_path):
    paths, s03, s01 = two_approved_cases(tmp_path)
    result = assemble_image_deck(paths, [s01, s03])
    assert result.expected_slide_ids == result.actual_slide_ids == ["s01", "s03"]
    assert all(output.slide_count == 2 for output in result.outputs)
    assert all(output.media_type != "image/png" for output in result.outputs)
```

`two_approved_cases(Path) -> tuple[WorkspacePaths,str,str]` chạy hai visual độc lập: build→render→attach neutral test evidence đúng hashes→audit_visual, assert QA failed=0/unverified=0 và currentreview=passed trước trả IDs. Test evidence ghi rõ fake, không phải livepilot; không forge approved sidecar. `two_rendered_cases(Path) -> tuple[WorkspacePaths,str,str]` chỉ build→render cho negative test:

```python
def test_assembly_rejects_rendered_but_unaudited(tmp_path):
    paths, s03, s01 = two_rendered_cases(tmp_path)
    with pytest.raises(VisualError) as exc:
        assemble_image_deck(paths, [s01, s03])
    assert exc.value.exit_code == 4
```

CLI map thiếu audit thành unverified/4, không tạo assemblyoutput; confirmedQA fail thành needs_revision/4. Previousbuild không đổi.
- [ ] RED `python -m pytest tests/integration/test_visual_image_pptx.py -q -k assembly`; expected missingassemblyfunction.
- [ ] Implement approvedorder/canvas/no duplicateID/no staleQA gate; build newNImageElementdeck with originlineage/notes and newbuildID; workerproduces PPTX/bundlecountsN, perPNG onlyRenderResult/manifest/slide_resultspaths. No providerrequest/re-generation.

```text
assemble_image_deck(paths: WorkspacePaths, visual_build_ids: list[str]) -> BuildResult
```

- [ ] Test duplicate/outoforderapproval/canvasmismatch/missingvisual và rendered-but-unaudited failure; sourcebundleN thật, receipts/ledger giữ nguyên. E1 subset: s03 fakefulfill→render→test evidence/audit approved→canonicaledit→newrender→new evidence/audit; s01 cũng audit approved rồi mới assembly. Không dùng QA của revision cũ.
- [ ] GREEN `python -m pytest tests/integration/test_visual_images.py tests/integration/test_visual_host_seam.py tests/integration/test_visual_image_pptx.py -q`; `python -m pytest -q`; `python scripts/generate-schemas.py --check`. Commit C5files and contractownerparserdelta explicitly; `git commit -m "feat: assemble ordered raster visual decks without regeneration"`.

## Acceptance, risk và rollback

C1coversAC07/08/14/15; C2AC01–03/12/18/34; C3AC09/21–31/41–43; C4AC13/17 và shared IMAGE QA; C5AC35/E1. Pillow tests không thay semantic/fidelity review: Phase1 C4 audit+E2 IMAGE evidence required, D4 chỉ HTML Phase2. PNGrecipebundle không là editable reconstruction. Missing platform/livehost giữunverified; rollback disable registration, giữ assets/ledger/oldoutputs, không refund unknown hoặc sửa WP04/push/deploy.

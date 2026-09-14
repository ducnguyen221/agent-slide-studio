# Slide Infographic E — Evidence and Local Release Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Hoàn tất E2E, visual pilots và local package gates với trạng thái thiếu capability trung thực, không push/deploy.

**Architecture:** Phase1 E1 chỉ A/C runtime, không chờ B; E2 IMAGE pilots sau E1+B3, B4 sau E2, E3 IMAGE local release sau E1/E2/B4. Phase2 mới mở rộng E1/E2 sang D; HTML gates Phase1 giữ planned/unverified. Fake tests không thay host thật, không tạo workflow engine.

**Tech Stack:** Python >=3.12/pytest9, wheel/setuptools hiện hữu, PowerPoint renderer thực nếu khả dụng, browser/host image tool đã đăng ký.

**Spec:** [Design 1.1.1](../specs/2026-09-14-slide-infographic-design.md), §12–16; [roadmap](2026-09-14-slide-infographic-roadmap.md).

## Global Constraints

- E1 fake/WAL không thay E2 host thật; platform chưa enforce memory/isolation giữ `unverified`.
- Project/grant kiểm mỗi dispatch; default requests0/repairs0; zero/thiếu capability không provider call.
- Năm pilot: four-card Vietnamese, dense3column12items+branch, dark no-text, reference3:2, edit-then-render.
- Publicfixture trung tính; `redistributable=false` mặc định; request/receipt/approval/host IDs riêng không vào package.
- Build/render/export độc lập audit; thiếu evidence `unverified/4`, QA lỗi `failed/4 needs_revision`.
- Không tự cài browser/dependency từ mạng; không commit secret/privateoutput, push/deploy hoặc sửa canonical WP.
- WP04 native đóng; render PowerPoint dùng capability công khai hoặc driver test riêng, không chỉnh native backend.

---

## File map / ownership

| Files | Owner / responsibility |
|---|---|
| `tests/integration/test_visual_e2e.py` | Sol, E1/E3/E4/E5 command pipeline |
| `tests/integration/test_visual_release.py` | Sol, package/privacy/install |
| `scripts/run-visual-pilots.py` | Sol, explicit station workspace pilot runner |
| `scripts/package-visual-release.py` | Sol, local deterministic bundle/allowlist |
| `docs/visual-infographic.md` | Sol commands/capabilities; Astra claim/style review |
| `docs/visual-infographic-release.md` | Coordinator gate inventory/handoff |
| `tests/fixtures/visual/pilots/cases.json`, `LICENSE.md`, `README.md` | Astra nội dung/rubric; Sol test consumer |
| `pyproject.toml`, `requirements-visual.lock` | Contract owner duy nhất |

Lock được tạo từ explicit dependency resolution có nguồn/hash trong E3, không đoán hash. Offline thiếu wheelhouse thì gate unavailable, không lock giả. Private pilot output ở station, không cạnh testfixture.

### Task E1: Full E2E và failure branches

**Files:** Create test_visual_e2e.py; Modify visual integration tests để tái dùng public fixtures. Runtime failure giao Sol/contract owner sửa task gốc, không thay expected để che lỗi.

**Interfaces:** Phase1 consumes A8 CLI, C1–C5 và A6/A7 WAL, không consume B hoặc E2. Phase2 thêm D1–D5. Produces `run_json(argv: list[str], capsys: pytest.CaptureFixture[str]) -> tuple[int,dict]`; E1/E3/E4/E5 là acceptance IDs của spec, không dependency task E3. Phase1 E1-image subset riêng, không claim full HTML E2E đã đạt.

- [ ] Viết command-flow test thật:

```python
def run_json(argv, capsys):
    from presentation_studio.cli import run
    code = run([*argv, "--json"])
    captured = capsys.readouterr()
    assert len(captured.out.splitlines()) == 1
    return code, json.loads(captured.out)

def test_offline_qa_failure_keeps_build_passed(offline_case, capsys):
    root, brief = offline_case
    code, built = run_json(["build", "--workspace", str(root), "--backend",
                           "image-deck", "--visual-brief", brief], capsys)
    assert code == 0 and built["status"] == "passed"
    build_id = built["data"]["build_id"]
    assert run_json(["render", "--workspace", str(root), "--build", build_id], capsys)[0] == 0
    code, audit = run_json(["audit", "--workspace", str(root), "--build", build_id], capsys)
    assert code == 4 and audit["data"]["review_state"] == "needs_revision"
```

`offline_case` là C IMAGE import/overlay fixture với measured glyph box vượt safearea để shared C4 audit fail, projectcalls0/repairs0 và recorder xác nhận0hostcalls. Không cần D runtime. A8 trả data.build_id; Phase2 thêm html-static equivalent riêng.
- [ ] RED `python -m pytest tests/integration/test_visual_e2e.py -q`; expected missingfixture hoặc integrationfailure thật; đã xanh thì ghi regressionbaseline, không cố phá để tạo RED.
- [ ] Implement fixtures qua CLIinit + neutralinputs. E1: deck5slides→s03→resolve→prepare/claim→fakehost→fulfill→build/render/audit→canonicaledit/reproject→render/audit→assemblys01,s03→PPTXreopen. Assert IDs/counts/hash/ledger tại từng boundary; fake review evidence phải đánh dấu fake, không là pilot.
- [ ] E4 crash injection tại reserve/dispatch/toolreceipt/WALsettlement; restart/recover hai lần, one ledgerdelta/no repeattool. E5 rendererthiếu3/reviewerthiếuunverified4/memorykill5 giữprioroutputhash/ledger; RESOURCE_BUSY6 không spawn. Two briefs chia lastcall, grantrevokedbeforeclaim→0call.
- [ ] Add E3 forcedQAerror/repair0, AC18/19 commandstatus table, numeric/compatibilityAC45–51, motionunavailable3 giữstatic. Missing actualPowerPoint screenshot là featureunverified riêng, không skip rồi passhandoff.
- [ ] Phase1 GREEN `python -m pytest tests/integration/test_visual_e2e.py tests/integration/test_visual_request_crashes.py tests/integration/test_visual_image_pptx.py -q`; `python -m pytest -q`. Phase2 mới thêm `python -m pytest tests/integration/test_visual_html_edit.py tests/integration/test_visual_html_render.py -q`. Stage exact changedtests; `git commit -m "test: verify IMAGE end to end and recovery boundaries"`.

### Task E2: Five visual pilots và real host

**Files:** Create run-visual-pilots.py, ba pilotfixturefiles, docs/visual-infographic.md; Modify test_visual_e2e.py cho pilotrunner tests; không privateoutput trong repo.

**Interfaces:** Depends E1 IMAGE subset và B3, không B4. Phase1 consumes C3HostImagePort+A4realgrant+B3 IMAGE skill+C commands; Phase2 thêm D. Produces `run_pilot(paths: WorkspacePaths, case_id: str, mode: str) -> CLIResult` và evidence cho B4; CLI giữ two-mode nhưng HTML-RECONSTRUCTION Phase1 trả unavailable3. Không auto-run toàn suite. IMAGE mặc định deterministic overlay, baked optional best-effort; một primary generation là mục tiêu, không guarantee call count.

- [ ] Write budget0 runner test:

```python
def test_pilot_zero_budget_never_dispatches(pilot_runner, pilot_workspace, fake_host):
    result = pilot_runner.run_pilot(pilot_workspace, "four-card-vi", "IMAGE")
    assert result.exit_code == 3
    assert fake_host.calls == 0
```

`pilot_runner` load explicit repo script bằng importlib.util; `pilot_workspace` dùng Aprojectdefault và publiccase, không credential.
- [ ] RED `python -m pytest tests/integration/test_visual_e2e.py -q -k pilot`; expected missing run_pilot/script.
- [ ] Astra viết cases: fourcards “Xác định/Chuẩn bị/Thực hiện/Đánh giá” mỗi2câu; dense3groups12items+branchr1; darkhero no chữ/logo; self-created3:2border-marker reference; canonicaledit18.5→19.5+groupmove. Ghi quyền nội dung tự viết; icon/font phải có license riêng, không suy từ URL.
- [ ] Sol implement runner A/C publiccalls Phase1, D chỉ Phase2; realhost chỉ khi durableclaim/grantfinitequota hoặc monetaryupperbound. HosttoolngoàiCLI emit requestaction để approvedhostfulfill, không mởUI/đườngvòng. Record rawsize/modelknownflags/receipt/elapsed/calls/cache/repairs, PromptPack hash/compiler/estimator/model/version và estimate; unknown tokenizer không có exact token promise. Prompt/request IDs riêng ở station.

```text
run_pilot(paths: WorkspacePaths, case_id: str, mode: str) -> CLIResult
```

- [ ] Preflight E2 với producer-issued grant: xác nhận remaining đủ selectedcase, raw/reference egress đã cấp, không tự tăng calls. Thiếu host/vision/browser/font/rights giữ unverified cho đúng nhánh.
- [ ] Phase1 chạy pilot `four-card-vi` IMAGE overlay mặc định; xem PNG fullsize, đủ bốn nhãn/tám câu/quan hệ/safearea. Baked chỉ chạy nếu được chọn và còn grant, QA best-effort không thành spelling guarantee.
- [ ] Phase2 khi reference đã được duyệt mới chạy `four-card-vi` HTML-RECONSTRUCTION; Phase1 giữ planned/unavailable, không chặn IMAGE pilot gate.
- [ ] Chạy `dense-three-column` overlay: 12 mục và branch r1 không mất, overflow phải fail thay vì rút gọn chữ.
- [ ] Chạy `dark-no-text` IMAGE none; kiểm không có glyph/logo ngoài ý muốn và alt text có nghĩa.
- [ ] Chạy `reference-mismatch` với reject: phải phát hiện raw3:2; chọn contain có approval mới rồi render, kiểm border markers còn đủ.
- [ ] Chạy `edit-then-render`: đổi canonical18.5→19.5, re-project và render; kiểm Fact/text/hash trước khi chuyển bước.
- [ ] Chạy layout-only group move trên revision trên; kiểm content hash giữ, input hash đổi và evidence cũ không được dùng lại.
- [ ] Chạy neutralvariant mới của pilot1; ghi case revision riêng, không tái dùng ảnh/evidence lần trước.
- [ ] Chạy neutralvariant mới của pilot5 trước reusableclaim; đối chiếu kết quả với cùng rubric, không hạ ngưỡng sau khi thấy ảnh.
- [ ] GREEN `python -m pytest tests/integration/test_visual_e2e.py -q -k pilot`; livepass cần rawhostreceipt+ledger+render+QA đủ. Không đặt SLA trước baseline. Stage publicscript/cases/docs/test only; `git commit -m "test: add bounded visual pilots and neutral fixtures"`.

### Task E3: Local package/privacy/license/install gates

**Files:** Create package-visual-release.py, release integrationtest, releasedoc; Modify visualdoc; contract owner pyproject/requirements-visual.lock.

**Interfaces:** Depends E1, E2 và B4 completed cho IMAGE Phase1; consumes A8schemas/capabilities, B4scoreboard/quick_validate, E1/E2 IMAGE evidence. Phase2 bổ sung HTML gates trước HTMLreleaseclaim. Produces `package_visual_release(repo_root: Path, output_root: Path) -> dict[str,str]` filenames→SHA256; CLI `python scripts/package-visual-release.py --output <local-release-dir> --json`. Export allowlist, không scan station/privatehash.

- [ ] Write archive test:

```python
def test_package_never_contains_station_records(release_archive):
    names = set(release_archive.namelist())
    assert "skills/slide-infographic/SKILL.md" in names
    assert not any(name.startswith((".presentation/", "builds/", "exports/")) for name in names)
    assert not any("image-fulfillment" in name or "image-request" in name for name in names)
```

- [ ] RED `python -m pytest tests/integration/test_visual_release.py -q`; expected missingpackager. Guidance nói về request không phải dữ liệu riêng: test actualarchivepaths/contentclassification, không cấm toàn bộ từ “request”.
- [ ] Implement sortedallowlist/fixedZIPmetadata; include skillroot+4references, schemas, userdocs, publiclicenses; exclude rawresponses/request/cache/privateUAT. Wheel runtime riêng, source/skillbundle giữ relpath để links chạy; không copy skillglobal. Provenance/rights claims có evidencecurrent, không packageunknownredistributable.

```text
package_visual_release(repo_root: Path, output_root: Path) -> dict[str,str]
```

- [ ] Resolve dependencylock trong explicit authorized setup: Phase1 installed/wheel versions+hashes, font/icon/Pillow/python-pptx và A/provider security review; Phase2 mới thêm tinycss2/Playwright/browser/DHTML review. Không pipdownload trong render/build; offline thiếu wheelhouse→unavailable. IMAGE-only local release không claim optional HTML dependencies hoặc runtime đã kiểm.
- [ ] Build wheel `python -m pip wheel --no-deps --no-build-isolation . --wheel-dir $releaseWheelDir`; biến lấy từ explicit validated releaseoutput, không userhome mặc định. Ghi tên/hash chính xác wheel được tạo.
- [ ] Tạo disposable venv trong releaseoutput và install `--no-index --find-links $approvedWheelhouse` với exactwheel trên; thiếu dependencywheel thì failed install gate, không mở mạng.
- [ ] Đổi cwd ra ngoài repo, chạy installed `presentation --help`, doctor và validate; xác nhận không import nhầm checkout source.
- [ ] Chạy installed import→build→render→audit trên workspace trung tính riêng; thiếu renderer3 không tự download. So PNG/hash/notes với artifact package version.
- [ ] GREEN `python -m pytest tests/integration/test_visual_release.py -q`; `python scripts/generate-schemas.py --check`; `python -m pytest -q`; Bquick_validate/GREEN/forward current; E1–E5gates tách fake/live. ActualPowerPoint reopen/render/notes kiểm riêng; nativefullsuite không giảm.
- [ ] Stage exact E3code/docs/ownerlock files after review; `git commit -m "build: gate local visual release on privacy and capability evidence"`. Không push/deploy; coordinator nhận artifacts/capabilitymatrix/unverifiedgates và quyết publication ở task riêng.

## Release ledger và rollback

Phase1 handoff chỉ được đặt tên **IMAGE MVP ready** khi các IMAGE gates đạt; full spec/HTML reconstruction vẫn planned/unverified cho đến Phase2. Gate nào không thuộc scope IMAGE giữ hàng/trạng thái riêng, không bị chuyển thành passed để làm xanh báo cáo. E1 IMAGE subset/E2 IMAGE pilots không được gọi là full E1/E2 across both modes.

| Gate | Passed cần có | Missing/failure |
|---|---|---|
| Contracts | A1–A8 unfiltered tests, schemas, oldreader1.0 | Block releaseclaim |
| Runtime | E1/E3/E4, process/memory/path thật | Missingplatformunverified |
| Generation | E2 rawhostreceipt/bytes/ledger | Fake không thay |
| Visual/editability | FivepilotQA + edit-render + PPTX-specificchecks | Không globalmetric shortcut |
| Skill | ObservedRED/GREEN/heldout/quick_validate | Structureonly không releasepass |
| Privacy/rights/install | Allowlist/license/fontreview/offlineinstall/securityreview | Unknownrights/privatecontent không publish |

Rollback disable affectedadapter/skillroute, giữ build/report/accounting trước; không xóaassets/refundunknown. Packagingfailure giữ priorreleasehash, dọn chỉ staging taskownidentity. Không push/deploy/nativechanges/canonicalWPupdate trong E.

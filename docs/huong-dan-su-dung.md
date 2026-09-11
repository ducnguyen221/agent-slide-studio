# Hướng dẫn sử dụng

Tài liệu này mô tả CLI đang có trong source checkout. Đây là lõi pre-release: backend build và renderer chưa đăng ký, nên `init`, `doctor` và migration là các luồng có thể kiểm chứng trực tiếp.

## Cài đặt từ source checkout

Chạy các lệnh sau từ thư mục gốc `agent-presentation-studio`:

```powershell
python -m pip install -e ".[test]"
```

Kiểm tra CLI:

```powershell
python -m presentation_studio.cli doctor --workspace . --json
```

Nếu đã cài editable package, có thể dùng lệnh ngắn `presentation` thay cho `python -m presentation_studio.cli`.

## Cây workspace

Một workspace được khởi tạo có dạng:

```text
<workspace>/
├── project.yaml
├── storyboard/
├── design/
├── assets/
│   └── files/
├── builds/
├── exports/
└── .presentation/
```

Station là thư mục chứa nhiều project:

```text
<station>/
└── projects/
    └── <project-id>/       # một workspace như cây trên
```

`~/.presentation` là convention station mặc định. CLI hiện chưa tự đọc `PRESENTATION_HOME` và chưa tự fallback đến đường dẫn đó; hãy truyền `--home` rõ ràng.

## Ví dụ 1: station và project

PowerShell:

```powershell
$station = Join-Path $HOME ".presentation"
presentation init --home $station --project demo --title "Bộ slide mẫu" --json
presentation doctor --workspace (Join-Path $station "projects\demo") --json
```

Kết quả `init` có `data.workspace` trỏ tới `<station>/projects/demo`. Dữ liệu project được lưu ở workspace đó; source code vẫn ở checkout.

## Ví dụ 2: workspace tùy chọn

```powershell
$workspace = Join-Path (Get-Location) ".tmp\presentation-demo"
presentation init --workspace $workspace --title "Workspace thử nghiệm" --json
presentation doctor --workspace $workspace --json
```

Ví dụ này không dùng station. Có thể xóa workspace thử nghiệm sau khi kiểm tra; không dùng đường dẫn đó cho dữ liệu cần giữ lâu dài.

## Migration từ YAML tổng hợp

Tạo một thư mục nguồn có một deck YAML tối thiểu, sau đó chạy dry-run trước apply:

```powershell
$source = Join-Path (Get-Location) ".tmp\legacy-demo"
$target = Join-Path (Get-Location) ".tmp\imported-demo"
New-Item -ItemType Directory -Force $source | Out-Null
Set-Content -Encoding utf8 (Join-Path $source "deck.yaml") @'
title: Demo migration
target_audience: Người xem
subject: Kiểm tra migration
slides:
  - slide_id: intro
    title: Xin chào
    subtitle: Slide đầu tiên
'@
presentation migrate --source $source --workspace $target --dry-run --json
presentation migrate --source $source --workspace $target --apply --json
```

`--dry-run` không tạo workspace đích. `--apply` tạo `project.yaml`, `storyboard/deck.yaml`, bản sao nguồn được chọn và `migration-report.json`; không tạo PPTX. Hãy đọc `migration-report.json` và trường `unmapped_fields` trước khi dùng kết quả.

`--deck` nhận đường dẫn tương đối với thư mục `--source`, chẳng hạn:

```powershell
presentation migrate --source $source --deck deck.yaml --workspace $target --dry-run --json
```

Đường dẫn tuyệt đối, thành phần `..`, symlink/junction, phần tử ẩn và phần mở rộng ngoài YAML/Markdown đều bị từ chối. Nếu không truyền `--deck`, migration tìm deck theo thứ tự deterministic ở ngay thư mục gốc: một tên allowlist (`deck.yaml`, `deck.yml`, `presentation.yaml`, `presentation.yml`, `slides.yaml`, `slides.yml`), rồi một YAML duy nhất, rồi một Markdown có tên `deck.md`, `presentation.md` hoặc `slides.md`. Nhiều ứng viên hoặc không có ứng viên đều trả lỗi; migration không tự chọn sâu trong cây source.

Sau khi chọn deck, migration chỉ đọc deck đó và các file được deck tham chiếu rõ ràng qua `source_files`, `notes_file` hoặc `speaker_notes_file`. Các file khác, kể cả file hợp lệ nằm trong source nhưng không được chọn, không được đọc và không được sao chép. Các giới hạn discovery, số file, kích thước và tổng số node YAML vẫn áp dụng cho bước tìm ứng viên; YAML thực tế chỉ được parse khi là deck hoặc reference được chọn.

Khi `--apply` ghi workspace, file được flush bằng fsync trước khi promote. Windows không hỗ trợ flush directory entry với handle hiện tại, nên tài liệu chỉ bảo đảm fsync file; không diễn đạt đây là bảo đảm bền vững directory entry trên Windows. Linux runtime chưa khả dụng trong môi trường smoke/release hiện tại; hành vi primitive tương ứng trên Linux chưa được xác minh ở đây.

## Đọc kết quả JSON và lưu dữ liệu

Mọi lệnh có `--json` in một object `CLIResult` gồm `command`, `status`, `exit_code`, `data`, `errors` và `warnings`.

| Exit code | Ý nghĩa |
|---:|---|
| 0 | Lệnh không báo lỗi. Kiểm thêm `status` và `warnings`; `status=unverified` vẫn có thể đi cùng exit 0 và không được suy ra là đã xác minh. |
| 2 | Input hoặc tham số không hợp lệ, thiếu nguồn, YAML không hợp lệ. |
| 3 | Capability chưa có hoặc không đủ quyền. |
| 4 | Kết quả chưa xác minh (`unverified`); hiện là mã dành cho contract, không phải build success. |
| 5 | Lỗi filesystem, backend hoặc lỗi nội bộ đã lọc; xem diagnostic ID ở stderr nếu có. |
| 6 | Conflict state/project/migration; không ghi đè đích. |

Sau mỗi lệnh, kiểm tra cả mã thoát và JSON:

```powershell
$json = presentation doctor --workspace $workspace --json
$commandExit = $LASTEXITCODE
if ($commandExit -ne 0) { throw "doctor failed: $commandExit" }
$result = $json | ConvertFrom-Json
if ($result.status -eq "failed" -or $result.errors.Count -gt 0) { throw "CLI result has errors" }
```

Giữ `project.yaml`, `storyboard/`, `assets/`, `builds/`, `exports/`, `.presentation/` và migration report trong workspace/station tương ứng. Không đưa profile cá nhân, output, state hoặc dữ liệu riêng vào public source checkout. Dọn `.tmp/` sau smoke; không coi thư mục tạm là nơi lưu trữ sản phẩm.

## Giới hạn hiện tại

`doctor` chỉ báo capability registry. Khi `backends` hoặc `renderers` rỗng, `build`, `render`, `audit` và `export` có thể trả `CAPABILITY_UNAVAILABLE`; kết quả đó không phải lỗi cài đặt. Chưa có bằng chứng runtime cho PPTX/HTML/reveal, speaker notes, overflow, editability hoặc visual UAT.

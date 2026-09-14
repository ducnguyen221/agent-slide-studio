# Agent Presentation Studio

Agent Presentation Studio là lõi chuẩn hóa workspace, schema, state và migration cho quy trình tạo presentation bằng agent. Repo hiện cung cấp package `presentation_studio` và lệnh `presentation`; backend dựng slide và renderer chưa được đăng ký trong bản hiện tại.

## Cài đặt

Yêu cầu Python 3.12 trở lên.

```bash
python -m venv .venv
# PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
cd agent-presentation-studio
python -m pip install -e .
```

Để chạy bộ kiểm thử:

```bash
python -m pip install -e ".[test]"
python -m pytest -q -p no:cacheprovider
```

Xem [hướng dẫn sử dụng chi tiết](docs/huong-dan-su-dung.md) để biết cấu trúc workspace, exit code và migration.

## Station và project

Convention của studio là station mặc định `~/.presentation/`. Một station chứa các project dưới `projects/<project-id>/`; dữ liệu cá nhân, profile, asset, output và state nên nằm ở station hoặc project, không đưa vào source public.

CLI hiện chưa tự đọc biến môi trường `PRESENTATION_HOME` và chưa tự suy ra `~/.presentation`. Vì vậy phải truyền station bằng `--home` khi tạo project:

```bash
presentation init --home "$HOME/.presentation" --project demo --title "Bộ slide mẫu" --json
```

Trên Windows PowerShell, dùng đường dẫn tương ứng:

```powershell
presentation init --home "$HOME\.presentation" --project demo --title "Bộ slide mẫu" --json
```

Hoặc tạo một workspace độc lập bằng đường dẫn cụ thể:

```bash
presentation init --workspace ./my-presentation --title "Bộ slide mẫu" --json
```

`init` tạo `project.yaml`, `storyboard/`, `design/`, `assets/files/`, `builds/`, `exports/` và `.presentation/`. Chạy lại với cùng cấu hình là no-op; cấu hình khác trả lỗi conflict.

## Kiểm tra và capability

`doctor` chỉ báo registry capability của lõi, backend và renderer đã đăng ký. Kết quả `passed` của doctor không chứng minh dependency, workspace, build hoặc render đã sẵn sàng:

```bash
presentation doctor --workspace ./my-presentation --json
```

Ở bản hiện tại, `backends` và `renderers` có thể là mảng rỗng. Vì vậy các lệnh dưới đây có thể trả `CAPABILITY_UNAVAILABLE`:

```bash
presentation build --workspace ./my-presentation --json
presentation render --workspace ./my-presentation --build demo-build --json
presentation audit --workspace ./my-presentation --build demo-build --json
presentation export --workspace ./my-presentation --build demo-build --format pptx --json
```

`validate` và `audit` hiện là tên lệnh CLI, nhưng chưa có pipeline sản phẩm end-to-end. Chưa có bằng chứng runtime cho PPTX/HTML/reveal, notes, overflow, editability, image-deck hay visual UAT.

## Migration legacy

Migration nhận thư mục nguồn legacy và một workspace đích mới. `--dry-run` chỉ quét và báo kế hoạch; `--apply` tạo project, deck schema mới, bản sao các file nguồn đã chọn và `migration-report.json`. Đích đã tồn tại sẽ bị từ chối để tránh ghi đè.

```bash
presentation migrate --source ./legacy-deck --workspace ./imported-deck --dry-run --json
presentation migrate --source ./legacy-deck --workspace ./imported-deck --apply --json
```

`--deck` là đường dẫn tương đối với `--source` (ví dụ `--deck decks/demo.yaml`); đường dẫn tuyệt đối, đi lên bằng `..`, symlink/junction và thư mục ẩn đều bị từ chối. Khi bỏ `--deck`, CLI chỉ chọn một file deck ở ngay thư mục gốc theo allowlist tên chuẩn (`deck.*`, `presentation.*`, `slides.*`), hoặc một YAML duy nhất ở gốc; lựa chọn mơ hồ bị từ chối. CLI chỉ đọc deck đã chọn và các file được deck tham chiếu rõ ràng (`source_files`, `notes_file`, `speaker_notes_file`); file khác trong source không được đọc hay sao chép.

Migration đang được hoàn thiện; hãy dùng `--dry-run` trước và kiểm tra `migration-report.json` sau khi áp dụng. File được ghi dùng fsync; trên Windows, fsync mục directory không được hệ điều hành hỗ trợ nên chỉ độ bền của file được bảo đảm. Linux runtime chưa có trong môi trường phát hành hiện tại. Migration không phải là bộ biên dịch slide và không tạo PPTX.

## Cấu trúc source

```text
src/presentation_studio/     # package public: CLI, models, workspace, state, migration
src/slidecraft/               # prototype legacy, chưa phải entry point public của studio
tests/                        # unit/integration tests cho core hiện có
schemas/                      # schema artifacts
```

Các thư mục profile, output, state và dữ liệu người dùng thuộc station/project. `skills/` và phần prototype legacy vẫn còn trong source để giữ tương thích và provenance; chúng không phải bằng chứng rằng các workflow/backend tương ứng đã chạy.

## Trạng thái phát hành

Luồng [infographic bằng Codex Image](skills/slide-infographic/SKILL.md) có [quy trình và mẫu prompt/QA](processes/slide-infographic-image.md) dạng Markdown cho host Codex. Đây chưa phải backend CLI; ảnh raster và bảng chữ overlay-ready không đồng nghĩa PowerPoint native. Xem [trạng thái eval](evals/slide-infographic/cases.md); HTML reconstruction là Phase 2 planned.

Đây là lõi pre-release. Backend/renderer, build/render end-to-end và visual UAT chưa được cung cấp trong bản hiện tại.

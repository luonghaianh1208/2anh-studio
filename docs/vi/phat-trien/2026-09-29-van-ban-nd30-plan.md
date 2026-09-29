# Soạn văn bản hành chính theo ND30 — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Loại việc thứ 11 của PPT Master bản Việt: AI soạn văn bản hành chính đúng thể thức Nghị định 30/2020. Cách làm:
- nhúng nguyên bộ mã `kanazawahere/nd30` (MIT, commit `b683ff9a3d74221802d073dcd10bd2aa3823087d`);
- bọc bằng lệnh `tools/vi/van_ban.py`;
- viết hướng dẫn tiếng Việt cho AI.

**Spec:** `docs/vi/phat-trien/2026-09-29-van-ban-nd30-design.md` (D1–D9 bắt buộc).

**Cách viết:** Mỗi task nêu giao diện và test. Người thực hiện làm theo TDD. Tên, số và chuỗi trong kế hoạch là bắt buộc.

## Global Constraints

- **Không sửa:** `skills/`, `LICENSE` gốc của repo, `SPONSORS*`, mọi `requirements*.txt`, `attribution_guard.py`, các file đã nhúng trong `tools/vi/nd30/`. Không commit `projects/`.
- **Thư viện:** Python chỉ dùng thư viện chuẩn và `python-docx` (import lười, báo `error.step: "docx"` khi thiếu). Không thêm PyYAML: ND30 tự dùng giá trị dự phòng khi thiếu.
- **Hợp đồng dòng lệnh:**
  - Mọi CLI in đúng một dòng JSON.
  - `error = {step, message, fix}`.
  - `step` thuộc `input|json|the-thuc|docx|write|internal`.
- **Chạy test:**
  - `venv\Scripts\python.exe -m unittest discover -s tools/vi/tests`.
  - Không dùng pytest. Test gốc của ND30 không được nhúng.
- **Commit:** trailer `Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>`. `git add` từng đường dẫn cụ thể; message qua file (`git commit -F`). Không push.
- **Nguồn ND30:** bản sao sạch ở `%TEMP%\nd30` (đúng commit trên). Nếu mất thì `git clone https://github.com/kanazawahere/nd30.git` rồi `git checkout b683ff9a3d74221802d073dcd10bd2aa3823087d`.

## Review Focus

1. **Không bịa.** Kịch bản thiếu người ký, số văn bản hoặc ngày thì vẫn ra bản nháp với `[CẦN BỔ SUNG]`, `ban_nhap: true`, và cảnh báo liệt kê từng ô. Không có đường nào xuất "thành phẩm" còn ô trống. Pin ở Task 2.
2. **Tên file và đường dẫn tiếng Việt có dấu, có khoảng trắng** (`projects\_van-ban\Công văn tập huấn AI`). Lệnh chạy được, đầu ra đúng chỗ, không lỗi mã hoá stdout trên console Windows. Pin ở Task 2.
3. **Mã nhúng không bị sửa.** Đổi 1 byte trong `tools/vi/nd30/scripts/build_docx.py` thì test SHA-256 báo đúng file. Pin ở Task 1.
4. **"Báo cáo" mơ hồ.** Hướng dẫn và `AGENTS.vi.md` hỏi đúng một câu phân loại Word hay slide; bảng loại việc ở ba nơi khớp nhau. Pin ở Task 3.
5. **Văn bản quy phạm HĐND/UBND.** `examples/nghi_quyet_hdnd.json` và `quyet_dinh_ubnd_qppl.json` sinh được qua `van_ban.py` với profile đúng (lấy từ `profile` trong JSON). Pin ở Task 2.

---

### Task 1: Nhúng mã ND30

**Files:** tạo `tools/vi/nd30/**` (theo D1), `tools/vi/nd30/NGUON.md`; test `tools/vi/tests/test_nd30_nhung.py`.

**Interfaces:**
- `NGUON.md` gồm:
  - repo, commit, ngày lấy (2026-09-29), giấy phép;
  - danh sách file và thư mục bỏ kèm lý do;
  - bảng `| đường dẫn tương đối | sha256 |` cho mọi file nhúng (trừ chính `NGUON.md`), sắp theo đường dẫn, dấu `/`.
- File nhúng chép byte-cho-byte. Không chép `__pycache__`, `.gitignore` bên trong.
- Test đọc bảng trong `NGUON.md`, so với file thật:
  - mọi file trong bảng tồn tại và khớp SHA-256;
  - mọi file trong `tools/vi/nd30/` (trừ `NGUON.md` và `__pycache__`) có trong bảng;
  - `LICENSE` chứa "MIT License" và "Nguyễn Minh Phát".
- Nếu `.gitattributes` của repo có thể đổi CRLF và làm lệch SHA-256, thêm dòng `tools/vi/nd30/** -text` (hoặc `binary` cho `.docx`) vào `.gitattributes` gốc. Kiểm bằng cách commit rồi `git checkout` lại và chạy test.
- `tools/vi/tests/test_vi_layer.py` `ALLOWED_CHANGES`: thêm đường dẫn nếu test ranh giới yêu cầu.

- [ ] Test trước (thấy trượt vì chưa có file), chép, sinh bảng SHA-256 bằng script một lần, test đạt.
- [ ] Test sửa 1 byte (trong thư mục tạm, không sửa repo): hàm kiểm trả đúng tên file lệch.
- [ ] Commit `feat(vi): vendor the nd30 Decree 30 document engine (MIT)`.

### Task 2: Lệnh `tools/vi/van_ban.py`

**Files:** tạo `tools/vi/van_ban.py`; test `tools/vi/tests/test_van_ban.py`.

**Interfaces:**
- `python tools/vi/van_ban.py <thư_mục> [--nhap]`: đọc `<thư_mục>/noi-dung.json`, ghi `<thư_mục>/van-ban.docx` và `<thư_mục>/kiem-tra.md`, in một dòng JSON theo spec D3.
- Import ND30 bằng cách thêm `tools/vi/nd30/scripts` vào `sys.path` bên trong hàm (import lười), rồi dùng các hàm của `generate_docx` và `validate_docx`. Đọc hai file đó để tìm API đúng: `generate_docx` có hàm dựng từ dict; `validate_docx` có hàm trả danh sách mục `{status, label, detail}` (dạng `--json`). Nếu chỉ có CLI thì gọi `main([...])` với argv, bắt `SystemExit`, và bắt stdout vào `io.StringIO` để giữ đúng một dòng JSON của mình.
- Tất cả output của ND30 (print tiếng Việt, emoji) không được lọt ra stdout. stdout chỉ có dòng JSON cuối, ghi UTF-8 an toàn như `tools/vi/de_thi.py` (xem cách `emit` ở đó và bản vá `7534f614` của `video.py`).
- Trường `profile`: lấy từ JSON (mặc định `administrative`), truyền cho bộ kiểm tra.
- Đếm ô: số lần xuất hiện `[CẦN BỔ SUNG` và `???` trong nội dung và chữ ký.
- Lỗi thể thức nặng: nếu mọi lỗi nặng chỉ là placeholder thì là bản nháp (`ready: true`, `ban_nhap: true`); còn lỗi nặng khác thì `error.step: "the-thuc"`, liệt kê nhãn lỗi, và xoá `van-ban.docx` vừa ghi để không giao nhầm.
- `kiem-tra.md` (tiếng Việt): loại văn bản, luật thể thức đã áp, bảng từng mục kiểm (✓/⚠/✗), danh sách ô cần bổ sung, dòng nhắc "Văn bản chưa đóng dấu, chưa ký; soát và điền đủ trước khi ban hành."
- Ghi file: ghi ra file tạm cùng thư mục rồi `os.replace`; `PermissionError` → `write` với fix "Đóng file Word đang mở rồi chạy lại."
- `--nhap` chỉ đổi lời cảnh báo cho rõ đây là bản nháp có chủ đích; không tắt kiểm tra.

- [ ] Test (thư mục tạm):
  - ví dụ `cong_van.json` đã điền đủ các ô → `ban_nhap: false`;
  - bản gốc (2 ô) → `ban_nhap: true`, `so_o_can_bo_sung: 2`;
  - mọi file trong `tools/vi/nd30/examples/` sinh được file;
  - thư mục tên tiếng Việt có dấu và khoảng trắng chạy được qua `subprocess` và stdout parse được JSON;
  - JSON hỏng → `json` kèm dòng; thiếu `header.ky_hieu` → `json` nêu trường;
  - thiếu `noi-dung.json` → `input`;
  - ghi bị khoá (giả `os.replace` ném `PermissionError`) → `write`;
  - lỗi nặng không phải placeholder (ví dụ JSON có màu chữ hoặc bullet nếu schema cho phép; nếu không dựng được thì giả hàm kiểm trả một lỗi nặng) → `the-thuc` và không còn `van-ban.docx`.
- [ ] Commit `feat(vi): van_ban.py wraps nd30 with the Vietnamese-layer JSON contract`.

### Task 3: Hướng dẫn và nối luật

**Files:**
- Tạo `docs/vi/tro-ly/van-ban-hanh-chinh.md` và `docs/vi/van-ban-hanh-chinh.md`.
- Sửa:
  - `docs/vi/tro-ly/quy-trinh-hoi.md` (bảng loại việc thêm dòng 11);
  - `docs/vi/tro-ly/mau-ho-so-don-vi.md` (D6);
  - `AGENTS.vi.md` (mục 3 câu kích hoạt, mục 10 bảng và đoạn loại việc không có bước xác nhận, mục 16 mới);
  - `.agents/rules/ppt-master-vi.md` (bảng loại việc và 3–4 dòng luật viết thẳng);
  - `README.md` (ghi công ND30);
  - `CHANGELOG-VI.md` (mục "Chưa phát hành").
- Test: `tools/vi/tests/test_vi_layer.py`.

**Nội dung bắt buộc:**
- Hướng dẫn theo khuôn các loại việc khác (xem `docs/vi/tro-ly/de-khtn-tieng-anh.md`):
  - "## Khi nào dùng", "## Câu hỏi bắt buộc" (đúng 7 câu, mỗi câu có "Gợi ý:"), "## Luật không bịa", "## Chọn loại văn bản", "## Viết noi-dung.json", "## Chạy lệnh và đọc kết quả" (bảng `error.step` đủ 6 bước), "## Điều cấm", "## Ghi vào brief".
  - Nói rõ: văn bản quy phạm HĐND/UBND đọc `tools/vi/nd30/references/the-thuc-qppl-*.md`; văn bản Đảng và Đoàn không hỗ trợ.
  - Câu phân loại "báo cáo/kế hoạch" giữa Word và slide.
- `AGENTS.vi.md` mục 16 theo khuôn mục 12–13: các bước đánh số, bảng `error.step`, điều cấm (D8).
- Luật Antigravity: dòng bảng loại việc và luật viết thẳng (không bịa; chạy `tools\vi\van_ban.py`; câu phân loại báo cáo; không sửa `tools/vi/nd30/`); vẫn dưới 12 000 ký tự.
- README: mục ghi công thêm "ND30 — © 2026 Nguyễn Minh Phát, MIT (tools/vi/nd30)".

- [ ] Test trước:
  - bảng loại việc có 11 dòng ở ba nơi và khớp nhau (sửa các test đếm hiện có);
  - hướng dẫn có đủ các mục trên, 7 câu hỏi, và bảng `error.step` khớp tập bước trong `van_ban.py` (đọc bằng regex từ mã);
  - `AGENTS.vi.md` có "## 16." và câu phân loại;
  - luật Antigravity dưới 12 000 ký tự và có `van_ban.py`;
  - hồ sơ đơn vị có "Cơ quan chủ quản".
- [ ] Commit `docs(vi): Decree 30 administrative documents as task type 11`.

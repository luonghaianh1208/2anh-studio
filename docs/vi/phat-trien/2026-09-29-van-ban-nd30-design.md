# Thiết kế: Soạn văn bản hành chính theo Nghị định 30 (loại việc thứ 11)

Ngày 2026-09-29. Chủ repo muốn tích hợp skill ND30 vào PPT Master bản Việt, bỏ phần văn bản Đoàn. Nguồn là repo `kanazawahere/nd30` (giấy phép MIT, © 2026 Nguyễn Minh Phát), commit `b683ff9a3d74221802d073dcd10bd2aa3823087d` (2026-08-27). Đây là bộ công cụ gồm ba phần:

- phân loại 27+ loại văn bản;
- phỏng vấn lấy dữ liệu mà không tự bịa;
- sinh `.docx` đúng thể thức Nghị định 30/2020/NĐ-CP rồi kiểm tra bằng script.

Chủ repo chọn:

- **Phạm vi:** toàn bộ văn bản hành chính theo ND30, gồm cả văn bản quy phạm của HĐND/UBND mà bản gốc hỗ trợ.
- **Bỏ:** văn bản Đoàn. Văn bản Đảng bản gốc chưa hỗ trợ nên cũng nằm ngoài.
- **Cách làm:** nhúng nguyên bộ mã ND30 vào repo và bọc thêm một lớp tiếng Việt (cách 1).

## 1. Tiêu chí thành công

1. Thầy cô nhờ AI (Antigravity, Codex, Claude Code) soạn văn bản hành chính và nhận `van-ban.docx` mở Word sửa được, đúng thể thức ND30, đã qua bộ kiểm tra của ND30.
2. **Không bịa.** Số và ký hiệu văn bản, ngày ban hành, người ký, căn cứ pháp lý, số tiền, số liệu không có trong lời thầy cô đều để `[CẦN BỔ SUNG: …]`. Còn ô trống thì file là **bản nháp** và lời bàn giao nói rõ; lỗi thể thức nặng thì không giao.
3. **Hỏi một lượt, tối đa 7 câu.** Tên đơn vị, cơ quan chủ quản và địa danh lấy từ hồ sơ đơn vị.
4. **Một lệnh duy nhất** `tools/vi/van_ban.py`, in đúng một dòng JSON theo hợp đồng chung của bản Việt.
5. **Mã ND30 nhúng nguyên trạng**, có giấy phép, ghi nguồn và SHA-256; một test phát hiện mã nhúng bị sửa.
6. **Không lẫn với loại việc khác:** "báo cáo" hay "kế hoạch" mơ hồ giữa văn bản Word và slide thì hỏi đúng một câu.
7. **Ranh giới:**
   - Không sửa `skills/`, không thêm thư viện: ND30 chỉ cần `python-docx`, đã có trong `tools/vi/requirements-vi.txt`; PyYAML là tuỳ chọn, bản gốc tự dùng giá trị dự phòng.
   - Không commit gì trong `projects/`.

## 2. Quyết định

| # | Quyết định | Lý do |
|---|---|---|
| D1 | Chép vào `tools/vi/nd30/`: `scripts/` (kể cả `rules/`), `templates/`, `examples/`, `references/`, `schemas/`, `LICENSE`, `SKILL.md`, `README.md`, `llms.txt`, `PHAN-LUONG.md`. Bỏ `SPARK-INSTRUCTIONS.md`, `pack-for-spark.sh`, `README.en/ja/zh.md`, `_linh-moi-2026-08-27.md`, `assets/samples/` và `tests/` (test gốc cần pytest). `tools/vi/nd30/NGUON.md` ghi repo, commit, ngày lấy, danh sách file bỏ, và bảng SHA-256 của mọi file nhúng. | Dùng ngay bộ sinh và bộ kiểm tra đã được thử thật; giữ nguyên để cập nhật lại được |
| D2 | Lệnh `python tools/vi/van_ban.py <thư_mục> [--nhap]`. Thư mục chứa `noi-dung.json` do AI viết theo schema ND30 (`tools/vi/nd30/schemas/nd30-input.schema.json`, ví dụ trong `tools/vi/nd30/examples/`). Lệnh gọi `generate_docx` rồi `validate_docx` của ND30 qua import (không subprocess), ghi `van-ban.docx` và `kiem-tra.md`. | Một cửa vào quen thuộc, giống `de_thi.py`, `giao_an.py` |
| D3 | JSON đầu ra: `{ready, files, loai_van_ban, profile, so_o_can_bo_sung, ban_nhap, kiem_tra: {dat, canh_bao, loi}, warnings, error}`. `error.step`: `input` (thiếu thư mục hoặc file), `json` (JSON sai cú pháp hoặc sai schema, nêu đúng trường), `the-thuc` (bộ kiểm tra báo lỗi nặng ngoài ô cần bổ sung), `docx` (thiếu `python-docx`), `write` (file Word đang mở), `internal`. | Cùng hợp đồng với các công cụ khác |
| D4 | Còn `[CẦN BỔ SUNG` hoặc `???`: mặc định vẫn xuất, `ready: true`, `ban_nhap: true`, và `warnings` liệt kê từng ô. Tương đương `--allow-placeholder` của ND30 nhưng không giấu. `--nhap` không bắt buộc; không có cờ nào tắt được kiểm tra. | Thầy cô cần bản nháp để điền tiếp; không bao giờ giao "thành phẩm" còn ô trống |
| D5 | Hướng dẫn cho AI `docs/vi/tro-ly/van-ban-hanh-chinh.md`, gồm:<ul><li>khi nào dùng;</li><li>7 câu hỏi (loại văn bản; gửi ai và nơi nhận; nội dung chính và số liệu; người ký và chức vụ; số và ký hiệu; ngày ban hành; căn cứ pháp lý);</li><li>luật cứng không bịa;</li><li>cách chọn loại văn bản theo `tools/vi/nd30/references/danh-muc-loai-vb.md`;</li><li>cách viết `noi-dung.json` (đọc ví dụ đúng loại trước);</li><li>văn bản quy phạm HĐND/UBND theo `the-thuc-qppl-*.md`;</li><li>văn bản Đảng và Đoàn: nói rõ không hỗ trợ;</li><li>bảng `error.step`.</li></ul>Không chép nguyên `SKILL.md` của ND30 vì nó nhắc công cụ riêng của tác giả (`/biensoan`, `/atp-deliver`). | Hướng dẫn đúng môi trường bản Việt |
| D6 | Hồ sơ đơn vị (`mau-ho-so-don-vi.md`) thêm ba dòng tuỳ chọn: "Cơ quan chủ quản", "Địa danh", "Ký hiệu viết tắt của đơn vị". Chưa có thì hỏi trong câu 1. | Không hỏi lại mỗi lần soạn |
| D7 | Loại việc thứ 11 "Soạn văn bản hành chính (Nghị định 30)". Được thêm vào bảng loại việc ở `quy-trinh-hoi.md`, `AGENTS.vi.md` mục 10 và luật Antigravity (viết thẳng); `AGENTS.vi.md` có mục 16. Câu kích hoạt: "công văn", "tờ trình", "quyết định", "thông báo", "giấy mời", "biên bản", "văn bản hành chính", "Nghị định 30", "ND30", "đúng thể thức". Câu chỉ có "báo cáo" hoặc "kế hoạch" thì hỏi đúng một câu: "Thầy cô cần văn bản Word đúng thể thức Nghị định 30, hay slide trình chiếu?" | Tránh đụng loại việc "Báo cáo – tổng kết" (slide) |
| D8 | Loại việc này không có bước xác nhận của upstream (không phải PPTX), như đề thi và giáo án. Điều cấm:<ul><li>không chạy `project_manager.py init`;</li><li>không tạo SVG;</li><li>không chạm `skills/`;</li><li>không sửa file trong `tools/vi/nd30/`;</li><li>không tự điền số, ký hiệu, ngày, người ký, căn cứ, số tiền;</li><li>không commit `projects/`.</li></ul> | Giữ ranh giới như các loại việc xuất Word |
| D9 | Tài liệu cho thầy cô `docs/vi/van-ban-hanh-chinh.md` (ngắn: làm được gì, câu lệnh mẫu, nhớ điền ô cần bổ sung, đóng dấu và ký theo quy trình văn thư). README ghi công ND30 trong mục ghi công. | Minh bạch nguồn và giấy phép |

## 3. Kiểm thử

- **Mã nhúng:** SHA-256 của mọi file trong `tools/vi/nd30/` khớp `NGUON.md`; `LICENSE` MIT có tên tác giả.
- **`van_ban.py`** (thư mục tạm, không mạng):
  - `examples/cong_van.json` bản đủ dữ liệu → `ready`, `ban_nhap: false`, có `van-ban.docx` và `kiem-tra.md`.
  - Bản gốc còn 2 ô `[CẦN BỔ SUNG]` → `ban_nhap: true`, `so_o_can_bo_sung: 2`, cảnh báo nêu từng ô.
  - Mỗi ví dụ của ND30 sinh được file.
  - JSON hỏng → `json` kèm dòng; thiếu trường bắt buộc → `json` nêu tên trường.
  - Thiếu `noi-dung.json` → `input`.
  - File đích đang bị khoá → `write`, test bằng file giả lập khoá hoặc giả hàm ghi.
  - Lỗi thể thức nặng không phải ô trống → `the-thuc`.
- **Tài liệu:**
  - Bảng loại việc 11 dòng khớp giữa `quy-trinh-hoi.md`, `AGENTS.vi.md` và luật Antigravity (test đã có, cập nhật số dòng).
  - Hướng dẫn có ≤ 7 câu hỏi, có luật "không bịa" và bảng `error.step` khớp mã.
  - Luật Antigravity dưới 12 000 ký tự.

## 4. Ngoài phạm vi

Văn bản Đảng (Hướng dẫn 36-HD/VPTW), văn bản Đoàn, xuất PDF, ký số, đánh số văn bản tự động, học mẫu Word riêng của trường (`learn_template.py` có trong mã nhúng nhưng chưa đưa vào hướng dẫn).

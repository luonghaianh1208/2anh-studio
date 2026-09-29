# PHÂN LUỒNG /nd30 — bản đồ luồng việc (chạy /graph 2026-08-27)

> Bộ từ + phương pháp: `.claude/skills/graph/SKILL.md`. Doctrine: `01_book/SOPs/luat-phai-thanh-cong.md`.

## Trạm phân luồng (trả lời trước khi soạn)

| Câu hỏi | Rẽ đi đâu |
|---|---|
| VB **hành chính** hay **QPPL** hay **cơ quan Đảng**? | hành chính → NĐ30 (luồng chính) · QPPL → NĐ78+187, CHỈ Mẫu 17/18/19/20 đã phủ, khác → HỎI · Đảng → HD 36-HD/VPTW, CHƯA phủ → HỎI |
| User chủ động đòi bỏ phỏng vấn? | có → Quick Mode (Luật #1 vẫn nguyên) · không → Guided |
| Cơ quan có mẫu .docx riêng? | có → `inspect_docx` + `learn_template`, mẫu HỌ thắng mặc định |
| Loại VB nằm trong cheat-sheet? | có → khỏi mở references/ · không (biên bản, phiếu biểu quyết...) → `the-thuc-nd30.md` |
| Môi trường có filesystem? | có (Claude Code) → chế độ A · không (Spark) → chế độ B, sinh JSON nhỏ, CẤM transcribe file dài |
| Case phức tạp generate_docx chưa cover? | → import helper `build_docx.py` viết riêng |

## Nối giả (đã soi — luồng này ÍT nối giả)
Pha 1→2→3→4→5 là phụ thuộc dữ liệu THẬT (phỏng vấn cần loại VB; sinh cần data; validate cần file)
— không cắt song song được. Nối giả duy nhất đáng kể: **đọc references chuẩn bị ↔ phỏng vấn user**
(chờ user trả lời là thời gian chết → đọc reference trong lúc chờ).

## Cổng theo 3 làn

| Làn | Cổng | Dạng |
|---|---|---|
| 1 (sai-sửa-rẻ) | schema JSON validate lúc generate · đuôi file ≠ .docx bị từ chối | máy, có sẵn |
| 2 (sai-lan-rộng) | **Pha 4 validate: MẶC ĐỊNH BẬT từ 2026-08-27** (fail-loud exit 2; trước là cờ opt-in = luật "BẮT BUỘC" chỉ là chữ). Tắt phải chủ động `--no-validate` + ăn cảnh báo "KHÔNG bàn giao bản này" | **máy — cổng điểm nghẽn, vá đợt này** |
| 2 | placeholder `[CẦN BỔ SUNG]`/`???` còn sót → validate bắt | máy, có sẵn |
| 3 (KHÔNG MỞ) | **Luật #1 KHÔNG BỊA** (số VB, căn cứ, người ký, tiền, ngày): máy không phân biệt được số-thật vs số-bịa → đây là **nhắc-by-design**, gate thật = placeholder bắt buộc + NGƯỜI điền. Đừng cố tự động hoá | người |
| 3 | Bàn giao ra ngoài (giao khách/ban hành) | người |

## Đường học (đang sống)
Mẫu cơ quan học được (`learn_template`) → thắng mặc định lần sau · gotcha mới → SKILL.md Gotcha ·
`SKILL_VERSION` chống bản cache.

## Việc /graph đã làm đợt này
`generate_docx.py`: validate opt-in → **opt-out** (`--no-validate`), `--validate` cũ giữ tương thích.
Test: default exit 2 khi lỗi nặng · no-validate cảnh báo rõ · 33/33 pytest pass.

## Chưa làm / không làm
- KHÔNG cổng-hoá Luật #1 (không bịa) — máy không kiểm được tính-thật của con số, đúng loại nhắc-by-design.
- Chế độ B (Spark) không enforce được từ phía mình (sandbox người khác) — chỉ có `SKILL_VERSION` làm
  vân tay + prompt khuyến nghị. Chấp nhận.

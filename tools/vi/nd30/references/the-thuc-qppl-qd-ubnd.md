<!-- nha-van:exempt — tài liệu tham chiếu kỹ thuật nội bộ, không phải văn bản gửi ra ngoài -->
# Thể thức VBQPPL — Quyết định của UBND cấp tỉnh (Mẫu số 19 + 20, NĐ 78/2025/NĐ-CP Phụ lục I)

> **Nguồn: PDF Phụ lục I NĐ 78/2025/NĐ-CP chính thức** (tải + `pdftotext` 2026-08-20). Chưa đối
> chiếu với Phụ lục III NĐ 187/2025 cho riêng 2 mẫu này (khác Mẫu 17 đã đối chiếu 2 nguồn) — nếu
> có sửa đổi tương tự ("cấp tỉnh" → "cấp các cấp") thì cần cập nhật, hiện ghi đúng theo NĐ78 gốc.

## Khác biệt so với Nghị quyết HĐND (Mẫu 17/18)

- **"Theo đề nghị của..."** thay vì "Xét Tờ trình...; Báo cáo thẩm tra..." — dòng này nêu đơn vị
  chủ trì soạn thảo (Sở/ngành), cùng kiểu trình bày với Căn cứ (nghiêng, kết thúc `;`).
- **Chữ ký khác hẳn**: NQ HĐND ký đơn giản "CHỦ TỊCH" — QĐ UBND ký **"TM. ỦY BAN NHÂN DÂN"** (dòng 1)
  + **"CHỦ TỊCH"** (dòng 2), vì UBND là cơ quan hành chính tập thể (Chủ tịch ký thay mặt cả UBND,
  khác HĐND nơi Chủ tịch HĐND ký với tư cách cá nhân đứng đầu cơ quan dân cử).
  Trong `generate_docx.py`: `signature.quyen_han="TM."`, `signature.chuc_vu_thay="ỦY BAN NHÂN DÂN"`,
  `signature.chuc_vu="CHỦ TỊCH"`.
- **Không có dòng đóng "...đã được... thông qua ngày..."** (dòng đó chỉ có ở Nghị quyết của cơ
  quan dân cử — HĐND/Quốc hội — vì phải "thông qua" tại kỳ họp; Quyết định của UBND là văn bản
  hành chính-điều hành, không qua biểu quyết tập thể tại kỳ họp nên không có dòng này).

## Mẫu số 19 — Quyết định UBND tỉnh (quy định trực tiếp)

Cấu trúc: Quốc hiệu/Tiêu ngữ + tên cơ quan (giống Mẫu 17/18) → "QUYẾT ĐỊNH" + tên gọi → Căn cứ +
"Theo đề nghị của..." → "Ủy ban nhân dân ban hành Quyết định [tên gọi]" → Phần/Chương/Mục/Tiểu mục
(nếu có) → Điều 1., Điều 2.... → chữ ký "TM. ỦY BAN NHÂN DÂN / CHỦ TỊCH" (không có dòng "đã được...
thông qua").

## Mẫu số 20 — Quyết định UBND tỉnh (ban hành Quy định/Quy chế)

Giống quan hệ Mẫu 17↔18: Quyết định ngắn (chỉ "Điều 1. Ban hành kèm theo Quyết định này [tên Quy
định/Quy chế]", "Điều 2..." hiệu lực) + văn bản Quy định/Quy chế đính kèm riêng (đóng dấu treo,
có khối "(Ban hành kèm theo Quyết định số .../20.../QĐ-UBND ngày...tháng...năm... của Ủy ban nhân
dân tỉnh...)"). Sinh 2 file riêng trong `generate_docx.py`, không gộp — cùng lý do như Mẫu 18.

## Cách sinh bằng `generate_docx.py`

Dùng `header.ky_hieu="QĐ-UBND"`, `header.ten_loai_in_hoa="QUYẾT ĐỊNH"`, `header.co_quan_ban_hanh`
= "ỦY BAN NHÂN DÂN TỈNH ..." (để `co_quan_chu_quan` trống, giống HĐND). Body dùng `can_cu` cho cả
"Căn cứ..." và "Theo đề nghị của..." (gộp chung 1 list, thứ tự đúng như văn bản thật). KHÔNG dùng
`italic_paragraph` "Nghị quyết này đã được..." (mẫu QĐ không có dòng đó). Chữ ký dùng
`quyen_han="TM."`, `chuc_vu_thay="ỦY BAN NHÂN DÂN"`, `chuc_vu="CHỦ TỊCH"`.

Ví dụ đầy đủ: [`examples/quyet_dinh_ubnd_qppl.json`](../examples/quyet_dinh_ubnd_qppl.json).

⚠️ Cùng nợ kỹ thuật như Mẫu 17: `validate_docx.py` chưa có profile riêng cho VBQPPL, dùng
`--profile administrative` sẽ có vài cảnh báo không hoàn toàn chính xác cho loại văn bản này.

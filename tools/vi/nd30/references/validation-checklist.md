<!-- nha-van:exempt — checklist kỹ thuật nội bộ, không phải văn bản gửi ra ngoài -->
# Validation checklist — kiểm trước khi bàn giao .docx

**Lệnh bắt buộc chạy trước mọi lần bàn giao:**
```bash
python3 scripts/validate_docx.py <file.docx> --profile administrative
```
Exit code: `0` sạch · `1` chỉ có cảnh báo (⚠) · `2` có lỗi nặng (✗) → **KHÔNG bàn giao**.

---

## A. Script tự kiểm (đã code trong `validate_docx.py`)

| # | Mục | Ngưỡng | Mức |
|---|---|---|---|
| 1 | Khổ giấy A4 | 21.0 × 29.7 cm (sai số ±0.5) | ✗ |
| 2 | Lề trái | 3.0 – 3.5 cm | ✗ |
| 3 | Lề phải | 1.5 – 2.0 cm | ✗ |
| 4 | Lề trên / lề dưới | 2.0 – 2.5 cm | ✗ |
| 5 | Màu chữ đen | mọi run, kể cả trong bảng và header/footer | ✗ |
| 6 | Font Times New Roman | mọi run, kể cả trong bảng và header/footer | ✗ |
| 7 | Bullet tự động | không có ký tự `•`, không có `w:numPr` (List Bullet/Number) | ✗ |
| 8 | Placeholder còn sót | `[CẦN BỔ SUNG...]`, `???`, `<...>` | ✗ |
| 9 | Shading ô bảng | không tô nền ô trong profile hành chính | ✗ |
| 10 | Bảng tràn lề | tổng bề rộng bảng ≤ vùng nội dung (21 − lề trái − lề phải) | ✗ |
| 11 | Quốc hiệu + Tiêu ngữ | có đủ 2 dòng | ✗ |
| 12 | Tên cơ quan ban hành | có ≥1 dòng IN HOA khớp `UBND / ỦY BAN / BỘ / SỞ / HĐND / VĂN PHÒNG / ...` | ⚠ |
| 13 | Số, ký hiệu | khớp `Số: <số?>/<KÝ HIỆU>`; chỗ số để trống → ⚠ (văn thư điền sau) | ✗ / ⚠ |
| 14 | Tên loại + trích yếu | khớp từ khoá tên loại, hoặc có `V/v` (công văn) | ⚠ |
| 15 | Chức vụ người ký | có chức vụ IN HOA (`CHỦ TỊCH`, `GIÁM ĐỐC`, `KT. ...`) | ⚠ |
| 16 | Nơi nhận + Lưu | có `Nơi nhận:` và dòng `Lưu: VT, ...` | ✗ / ⚠ |
| 17 | Phụ lục | nội dung nhắc "kèm theo" thì phải có `PHỤ LỤC <số La Mã>` | ⚠ |

Biểu mẫu nội bộ (Phiếu ghi ý kiến / Phiếu biểu quyết / Phiếu thẩm định) được **miễn** mục 13 và 16
— script tự nhận diện qua tên phiếu.

## B. Người phải soi bằng MẮT (script không kiểm được)

Render ra ảnh rồi xem, đừng tin log:
```bash
python3 scripts/render_docx.py <file.docx> --png
```
- [ ] Quốc hiệu/Tiêu ngữ **bên phải**, tên cơ quan **bên trái**, 2 khối không lệch cột.
- [ ] Có kẻ ngang ngắn dưới tên cơ quan ban hành (1/3–1/2 dòng) và dưới trích yếu.
- [ ] Tên loại IN HOA canh giữa; `Nơi nhận` bên trái đối xứng khối chữ ký bên phải.
- [ ] Cỡ chữ từng thành phần đúng bảng ở `the-thuc-nd30.md` — python-docx đọc cỡ chữ qua
      style-inheritance không đáng tin, phải xem ảnh.
- [ ] **Dấu / chữ ký số**: đóng đè 1/3 chữ ký về bên trái (script luôn để mục này cho người).
- [ ] Căn cứ pháp lý: các dòng trên `;`, dòng cuối `.` — và số hiệu văn bản viện dẫn **có thật**.
- [ ] Không vỡ chữ (thiếu font Việt khi render), không có dòng mồ côi 1–2 chữ.
- [ ] Nội dung đúng loại VB user yêu cầu và đủ phần bắt buộc của loại đó.

## C. Quy tắc bàn giao
1. Còn mục ✗ → sửa, KHÔNG bàn giao.
2. Còn `[CẦN BỔ SUNG]` → được bàn giao **nhưng phải liệt kê rõ từng field còn thiếu**.
3. Không tuyên bố "chuẩn 100% NĐ30" khi còn placeholder hoặc còn mục ⚠ chưa soi tay.

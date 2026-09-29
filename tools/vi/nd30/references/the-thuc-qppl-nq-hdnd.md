<!-- nha-van:exempt — tài liệu tham chiếu kỹ thuật nội bộ, không phải văn bản gửi ra ngoài -->
# Thể thức VBQPPL — Nghị quyết HĐND các cấp (Mẫu số 17 + 18, NĐ 78/2025 sửa bởi NĐ 187/2025)

> **Nguồn: 2 PDF chính thức, đối chiếu trực tiếp** (tải + `pdftotext`/`tesseract` 2026-08-20,
> KHÔNG suy đoán từ tóm tắt web):
> - **Nghị định 78/2025/NĐ-CP, Phụ lục I** — bản gốc, Mẫu số 17 ghi *"Nghị quyết của Hội đồng
>   nhân dân **cấp tỉnh** (quy định trực tiếp)"*.
> - **Nghị định 187/2025/NĐ-CP, Phụ lục III** — bản SỬA ĐỔI (ban hành 01/7/2025, sau NĐ78), Mẫu
>   số 17 đổi thành *"Nghị quyết của Hội đồng nhân dân **cấp các cấp** (quy định trực tiếp)"* —
>   **mở rộng phạm vi áp dụng cho cả huyện/xã, không chỉ tỉnh**. NĐ187 ban hành SAU nên **THẮNG**
>   NĐ78 ở điểm này — dùng "cấp các cấp" làm chuẩn hiện hành, không dùng "cấp tỉnh" nữa.
>
> **Phạm vi tài liệu này: Mẫu số 17 + Mẫu số 18** (NQ HĐND quy định trực tiếp + NQ HĐND ban hành
> kèm Quy định/Quy chế). QĐ/CT của UBND tỉnh xem file riêng
> [`the-thuc-qppl-qd-ubnd.md`](./the-thuc-qppl-qd-ubnd.md). **CHƯA phủ**: luật/pháp lệnh/nghị
> quyết Quốc hội, thông tư, văn bản Đảng. Đây là track VBQPPL cho cấp địa phương (tỉnh/huyện/xã),
> không phủ toàn bộ NĐ 78/2025 + NĐ 187/2025 (37 mẫu, gồm cả luật/pháp lệnh cấp trung ương).

## Mẫu số 18 — Nghị quyết HĐND ban hành kèm Quy định/Quy chế

Khác Mẫu 17 (quy định trực tiếp trong thân NQ), Mẫu 18 tách làm **2 văn bản**:
1. **Nghị quyết** (ngắn) — chỉ có "Điều 1. Ban hành kèm theo Nghị quyết này [tên Quy định/Quy chế]",
   "Điều 2..." (hiệu lực thi hành), rồi kết + ký — giống hệt Mẫu 17 về thể thức, KHÔNG có phần
   "Phần I/Chương I/Điều 1. (Tên điều)..." chi tiết (những cái đó nằm trong văn bản Quy định/Quy
   chế đính kèm, không nằm trong Nghị quyết).
2. **Quy định/Quy chế đính kèm** (văn bản riêng, đóng dấu treo) — có khối
   `(Ban hành kèm theo Nghị quyết số .../20.../NQ-HĐND ngày...tháng...năm... của Hội đồng nhân dân
   tỉnh...)` ngay dưới tên Quy định/Quy chế, rồi mới tới Phần/Chương/Mục/Điều như Mẫu 17.
   Đóng dấu treo (dấu treo = dấu đóng lên góc trái tên cơ quan, không đè lên chữ ký — khác dấu
   thường của Nghị quyết chính).

Trong `generate_docx.py`, sinh 2 file riêng cho Mẫu 18 (1 file "nghị quyết" ngắn + 1 file
"Quy định/Quy chế" dài) — KHÔNG gộp làm 1 vì chúng là 2 văn bản có tình trạng hiệu lực khác nhau
theo luật ban hành.

## Khác biệt với NĐ30 cần lưu ý

- **Lề trang**: trên/dưới/phải 15-20mm, trái 30-35mm (NĐ30: trên/dưới 20-25mm, phải 15-20mm,
  trái 30-35mm) — **trùng khoảng với NĐ30 ở giá trị 2cm/3cm đã dùng làm mặc định**, nên
  `setup_page()` hiện có (2cm/2cm/2cm/3cm) đã nằm gọn trong dải QPPL, KHÔNG cần hàm riêng.
- **Không có "V/v" trích yếu** — chỉ có "NGHỊ QUYẾT" (tên loại) + tên gọi bên dưới, không phải
  "Số: .../TTr-UBND — V/v ...".
- **Không có dòng "QUYẾT NGHỊ:"** cho Mẫu 17 HĐND (khác luật/NQ Quốc hội) — sau phần Căn cứ
  + "Xét Tờ trình...; Báo cáo thẩm tra...; ý kiến thảo luận..." là câu **"Hội đồng nhân dân ban
  hành Nghị quyết ...(tên gọi)..."** viết thường, không phải dòng riêng in hoa.
- **Dòng đóng riêng biệt**: *"Nghị quyết này đã được Hội đồng nhân dân ...Khóa...Kỳ họp thứ...
  thông qua ngày...tháng...năm..."* — chữ nghiêng, đặt ngay dưới Điều cuối cùng. NĐ30 không có
  dòng này.

## Thông số theo từng thành phần (trích Phụ lục I NĐ 78/2025, phạm vi áp dụng theo Phụ lục III NĐ 187/2025)

| Thành phần | Font | Cỡ chữ | Kiểu | Ghi chú |
|---|---|---|---|---|
| Quốc hiệu | Times New Roman | 12-13pt | ĐẬM, IN HOA | Phía trên-phải trang 1 |
| Tiêu ngữ | Times New Roman | 13-14pt | ĐẬM | Dưới Quốc hiệu, gạch chân full-width |
| Tên cơ quan (HĐND tỉnh/huyện/xã...) | Times New Roman | 12-13pt | ĐẬM, IN HOA | Trên-trái trang 1, gạch chân 1/3-1/2 width |
| Số, ký hiệu | Times New Roman | 13pt | thường | `Số: .../20../NQ-HĐND` |
| Địa danh, ngày tháng | Times New Roman | 13-14pt | NGHIÊNG | Cùng dòng/hàng với Số-ký hiệu (2 cột) |
| Tên loại VB "NGHỊ QUYẾT" | Times New Roman | 14pt | ĐẬM, IN HOA | Canh giữa |
| Tên gọi nghị quyết | Times New Roman | 13-14pt | ĐẬM | Dưới tên loại, canh giữa, gạch chân 1/3-1/2 |
| Căn cứ ban hành | Times New Roman | 14pt | NGHIÊNG | Mỗi căn cứ 1 dòng, `;` cuối dòng trên, `.` dòng cuối — GIỐNG NĐ30 |
| "Điều 1." + tên điều | Times New Roman | 13-14pt | ĐẬM, đứng | Cách lề trái 1-1,27cm — GIỐNG NĐ30 |
| Khoản (1., 2.) | Times New Roman | 13-14pt | đứng | Số Ả Rập + `.` |
| Điểm (a), b)) | Times New Roman | 13-14pt | đứng | Chữ cái + `)` |
| Nội dung thường | Times New Roman | 13-14pt | đứng | Justify, thụt đầu dòng 1-1,27cm — GIỐNG NĐ30 |
| Dòng "Nghị quyết này đã được..." | Times New Roman | 13-14pt | NGHIÊNG | Dưới Điều cuối cùng, KHÔNG có ở NĐ30 |
| Chức vụ ký (CHỦ TỊCH) | Times New Roman | 13pt | ĐẬM, IN HOA | Giống NĐ30 |
| Nơi nhận | Times New Roman | 11-12pt | đứng | Giống NĐ30 |

## Bố cục Mẫu số 17 (trích nguyên văn từ Phụ lục III NĐ 187/2025 — bản "cấp các cấp", đã bỏ chú thích ghi chú)

```
HỘI ĐỒNG NHÂN DÂN ...(1)             CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM
        -------                            Độc lập - Tự do - Hạnh phúc
                                                   ---------------
   Số:.../20.../NQ-HĐND                    ..., ngày...tháng...năm 20...

                            NGHỊ QUYẾT
                          ...(tên gọi)...

Căn cứ Luật Tổ chức chính quyền địa phương ngày ... tháng ... năm ...;
Căn cứ ...;
Xét Tờ trình ...; Báo cáo thẩm tra của ...; ý kiến thảo luận của đại
biểu Hội đồng nhân dân tại kỳ họp;

Hội đồng nhân dân ban hành Nghị quyết ...(tên gọi)...

Điều 1. (Tên của điều)
1. ...
   a) ...
Điều ... (Tên của điều)
...

Nghị quyết này đã được Hội đồng nhân dân ...Khóa...Kỳ họp thứ... thông
qua ngày...tháng...năm...

                                                          CHỦ TỊCH
Nơi nhận:                                              (Chữ ký, dấu)
- ...;
- Lưu: VT, ...
                                                          Họ và tên
```
(1) Tên HĐND ban hành — có thể là tỉnh/thành phố trực thuộc trung ương, huyện/quận/thị xã, hoặc
xã/phường/thị trấn (Phụ lục III NĐ 187/2025 mở phạm vi cho "cấp các cấp", không còn giới hạn
riêng cấp tỉnh như bản gốc Phụ lục I NĐ 78/2025).

## Cách sinh bằng `generate_docx.py`

Dùng `"profile": "administrative"` như bình thường (margin trùng khoảng), thêm 2 điểm khác:
1. `header.co_quan_chu_quan` để trống (không có dòng "cơ quan chủ quản" cho HĐND).
2. Body item mới `{"type": "italic_paragraph", "text": "Nghị quyết này đã được..."}` cho dòng
   đóng — KHÁC NĐ30, chưa có trong schema `body` types trước bản này.

Ví dụ đầy đủ: [`examples/nghi_quyet_hdnd.json`](../examples/nghi_quyet_hdnd.json).

⚠️ **Validate:** `validate_docx.py` hiện tại kiểm theo mặc định NĐ30 (mong đợi "V/v" hoặc tên loại
chuẩn hành chính) — CHƯA có profile riêng cho VBQPPL. Dùng `--profile administrative` sẽ báo một
số cảnh báo không chính xác 100% cho VBQPPL (vd không nhận diện "NGHỊ QUYẾT" như tên loại chuẩn).
Đây là nợ kỹ thuật đã biết — coi kết quả validate là THAM KHẢO, vẫn phải soi mắt kỹ hơn cho VBQPPL
so với văn bản hành chính thường.

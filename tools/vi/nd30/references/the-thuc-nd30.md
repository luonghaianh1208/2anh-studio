<!-- nha-van:exempt — tài liệu tham chiếu kỹ thuật nội bộ, không phải văn bản gửi ra ngoài -->
# Thể thức văn bản hành chính — thông số theo NĐ 30/2020/NĐ-CP

> **Nguồn duy nhất của các con số dưới đây: Nghị định 30/2020/NĐ-CP, Phụ lục I**
> (văn bản pháp luật công khai). Phần "hình dạng thật + lỗi hay gặp" lấy từ repo `vbhc`
> (biencuong/vbhc, Unlicense/public domain) — xem mục "Nguồn gốc" trong `README.md`.
> **Phạm vi:** chỉ văn bản HÀNH CHÍNH. Văn bản QPPL và văn bản cơ quan Đảng có thể thức riêng
> (xem Luật cứng #2 trong `SKILL.md`) — đừng bê khuôn này sang.

## I. Thông số kỹ thuật bắt buộc

| Thông số | Giá trị | Vị trí trong NĐ30 PL I |
|---|---|---|
| Khổ giấy | A4 (210 × 297 mm) | I.1 |
| Chiều trình bày | theo chiều dài khổ A4 | I.2 |
| Lề trên | 20 – 25 mm | I.3 |
| Lề dưới | 20 – 25 mm | I.3 |
| Lề trái | 30 – 35 mm | I.3 |
| Lề phải | 15 – 20 mm | I.3 |
| Phông chữ | Times New Roman, bộ mã Unicode TCVN 6909:2001 | I.4 |
| Màu chữ | đen (`#000000`) toàn bộ | I.4 |
| Giãn dòng | tối thiểu dòng đơn, tối đa 1,5 lines | II.6.e |
| Khoảng cách đoạn | tối thiểu 6pt | II.6.e |
| Thụt đầu dòng | 1 cm hoặc 1,27 cm | II.6.e |
| Số trang | chữ số Ả Rập, cỡ 13–14, đứng, canh giữa lề trên; **không hiện số ở trang 1** | I.7 |
| Dấu cuối mỗi căn cứ | `;` — riêng dòng căn cứ cuối dùng `.` | II.6.a |

**Giá trị `scripts/build_docx.py` chọn mặc định** (nằm trong dải trên): A4 · lề trái 3cm ·
lề phải 2cm · trên 2cm · dưới 2cm · Times New Roman 13pt đen.

## II. Chín thành phần thể thức — cỡ chữ, kiểu, vị trí

| # | Thành phần | Cỡ | Kiểu | Vị trí |
|---|---|---|---|---|
| 1 | Quốc hiệu `CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM` | 12–13 | in hoa, đứng, đậm | trên cùng, **nửa PHẢI** trang đầu |
| 1 | Tiêu ngữ `Độc lập - Tự do - Hạnh phúc` | 13–14 | in thường, đứng, đậm | ngay dưới Quốc hiệu, có kẻ ngang dài bằng dòng chữ |
| 2 | Tên cơ quan chủ quản trực tiếp (nếu có) | 12–13 | in hoa, đứng | **nửa TRÁI**, canh giữa nửa trái |
| 2 | Tên cơ quan ban hành | 12–13 | in hoa, đứng, **đậm** | dưới chủ quản; kẻ ngang dài **1/3–1/2** dòng chữ, cân đối |
| 3 | `Số: ...` + ký hiệu | 13 | số in thường đứng, ký hiệu in hoa | canh giữa dưới tên cơ quan ban hành |
| 4 | Địa danh, ngày tháng năm | 13–14 | in thường, **nghiêng** | cùng dòng với số/ký hiệu, canh giữa dưới Quốc hiệu |
| 5a | Tên loại văn bản | 13–14 | in hoa, đứng, đậm | canh giữa trang |
| 5a | Trích yếu nội dung | 13–14 | in thường, đứng, đậm | ngay dưới tên loại; kẻ ngang 1/3–1/2 dòng chữ |
| 5b | Trích yếu **công văn** (sau `V/v`) | 12–13 | in thường, đứng | canh giữa dưới số/ký hiệu, cách dòng 6pt |
| 6 | Lời văn nội dung | 13–14 | in thường, đứng, **canh đều 2 lề** | thân văn bản |
| 6 | Căn cứ ban hành | 13–14 | in thường, **nghiêng** | đầu phần nội dung |
| 7 | Quyền hạn ký (`TM.` `Q.` `KT.` `TL.` `TUQ.`) | 13–14 | in hoa, đứng, đậm | khối chữ ký, **bên PHẢI** |
| 7 | Chức vụ người ký | 13–14 | in hoa, đứng, đậm | dưới quyền hạn |
| 7 | Họ tên người ký | 13–14 | in thường, đứng, đậm | dưới chữ ký |
| 8 | `Kính gửi:` + nơi nhận (tờ trình/báo cáo/công văn) | 13–14 | in thường, đứng | trên phần nội dung, canh giữa |
| 9 | Từ `Nơi nhận:` | 12 | in thường, nghiêng, đậm | cuối văn bản, **bên TRÁI**, đối xứng khối chữ ký |
| 9 | Danh sách nơi nhận | 11 | in thường, đứng | dưới từ `Nơi nhận:`; dòng cuối `Lưu: VT, <đơn vị soạn>.` |

Quy tắc chi tiết ít người để ý:
- Quốc hiệu và Tiêu ngữ cách nhau **dòng đơn**; chữ đầu mỗi cụm viết hoa, giữa các cụm là
  gạch nối `-` **có cách chữ** (không dùng em-dash `—`).
- Số văn bản < 10 phải thêm số 0 (`05`). Giữa số và ký hiệu là `/`; giữa các nhóm trong
  ký hiệu là `-` **không cách chữ**.
- Ngày/tháng < 10 cũng thêm số 0: `ngày 05 tháng 01 năm 2026`.
- **Công văn KHÔNG có tên loại** — không viết dòng "CÔNG VĂN".
- Trích yếu tối đa 4 dòng.

## III. Ký hiệu viết tắt loại văn bản (dùng cho phần `Số:`)

**Format:** `Số: <số>/<viết tắt loại VB>-<viết tắt cơ quan ban hành>`

| Loại VB | Viết tắt | Ví dụ |
|---|---|---|
| Nghị quyết | NQ | `Số: 22/NQ-HĐND` |
| Quyết định | QĐ | `Số: 145/QĐ-UBND` |
| Chỉ thị | CT | `Số: 03/CT-UBND` |
| Thông báo | TB | `Số: 12/TB-UBND` |
| Hướng dẫn | HD | `Số: 05/HD-SNV` |
| Kế hoạch | KH | `Số: 40/KH-UBND` |
| Báo cáo | BC | `Số: 88/BC-SGDĐT` |
| Tờ trình | TTr | `Số: 09/TTr-UBND` |
| Biên bản | BB | `Số: 02/BB-HĐ` |
| Công văn | *(không có viết tắt loại)* | `Số: 1488/VP-KH&CĐS` |

Chưa vào sổ văn thư → **để trống chỗ số**, giữ dấu `/`: `Số:        /TTr-UBND`. Không bịa số.

## IV. Hình dạng thật của từng khối

Khối đầu trang (2 cột, cột trái tên cơ quan · cột phải Quốc hiệu — dựng bằng bảng ẩn viền):
```
UBND HUYỆN X                    CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM
  UBND XÃ Y                          Độc lập - Tự do - Hạnh phúc
  ─────────                     ───────────────────────────────

Số:        /TTr-UBND                  Xã Y, ngày     tháng 08 năm 2026
```
Khối cuối trang (Nơi nhận trái · chữ ký phải):
```
Nơi nhận:                                    CHỦ TỊCH
- UBND huyện X;
- Lưu: VT, VP.
                                       (chữ ký, dấu đè 1/3 về bên trái)

                                        Nguyễn Văn A
```
Ký thay: dòng trên `KT. CHỦ TỊCH`, dòng dưới `PHÓ CHỦ TỊCH`.
Thừa lệnh: `TL. CHỦ TỊCH` / `CHÁNH VĂN PHÒNG`. Thừa uỷ quyền `TUQ.` cần giấy uỷ quyền.

Viện dẫn văn bản **lần đầu** phải đủ: số/ký hiệu + ngày tháng năm + tên cơ quan ban hành +
tên văn bản; các lần sau chỉ ghi số/ký hiệu.

Phụ lục: đặt sau văn bản chính, số La Mã (Phụ lục I, II, III), mỗi phụ lục có tên riêng,
trang đánh số riêng không nối tiếp văn bản chính.

## V. Lỗi hay gặp — soi trước khi bàn giao

**Lỗi thể thức**
1. Thiếu `Nơi nhận:` hoặc thiếu dòng `Lưu: VT, <đơn vị>.`
2. Thiếu phần Căn cứ (bắt buộc với quyết định); dòng căn cứ cuối dùng `;` thay vì `.`
3. Thiếu Quốc hiệu, hoặc đặt Quốc hiệu bên trái (phải bên PHẢI).
4. Tên cơ quan ban hành không đậm; thiếu kẻ ngang dưới tên cơ quan / dưới trích yếu.
5. Tên loại không IN HOA; hoặc viết "CÔNG VĂN" như tên loại.
6. Ngày/tháng/số < 10 thiếu số 0.
7. Bịa số văn bản khi chưa vào sổ.
8. Lề trái < 3cm (không đủ chỗ đóng quyển).
9. Dùng `•` hoặc bullet tự động của Word (phải dùng tiền tố tay `-`, `+`, `a)`).
10. Ghi "(để báo cáo)"/"(để phối hợp)" trong ngoặc ở Nơi nhận — NĐ30 không quy định.

**Lỗi câu chữ** (chi tiết trong `editorial-quality-vi.md`)
11. Dùng từ nói thường thay động từ hành chính (`làm` thay vì `tổ chức thực hiện`).
12. Câu quá dài, nhiều mệnh đề lồng.
13. Lạm dụng bị động thay vì nêu rõ chủ thể thực hiện.
14. Xưng hô không nhất quán trong cùng văn bản.
15. Viện dẫn sai số hiệu (viết `NĐ 30/2002` thay `NĐ 30/2020`) hoặc thiếu thành phần lần đầu.

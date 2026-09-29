<!-- nha-van:exempt — tài liệu tham chiếu kỹ thuật nội bộ -->
# Profile — cờ `--profile` của `validate_docx.py`

Mỗi profile là một bộ luật kiểm khác nhau. Chọn sai profile thì validate báo sai.

| Profile | Dùng cho | Luật đặc thù |
|---|---|---|
| `administrative` *(mặc định)* | Công văn, tờ trình, quyết định, kế hoạch, báo cáo, thông báo, giấy mời — mọi VB hành chính gửi ra ngoài | Đủ 9 thành phần thể thức · lề/A4/font/màu theo NĐ30 · **cấm** bullet tự động và `•` · cấm shading ô bảng · bắt buộc `Nơi nhận:` + `Lưu:` |
| `bieu-mau-noi-bo` | Phiếu ghi ý kiến, phiếu biểu quyết, phiếu thẩm định (form lưu hành nội bộ) | Như `administrative` nhưng **miễn** `Số:` và **miễn** `Nơi nhận:` (form không vào sổ) |
| `minutes-administrative` | Biên bản họp có thể thức hành chính | Như `administrative`; thêm mục soi tay: thành phần dự họp, kết luận, chữ ký chủ trì + thư ký |
| `academic` | Báo cáo/giáo án/tài liệu học thuật — **không** phải VB hành chính | Giữ A4 + Times New Roman + màu đen; **cho phép** bullet tự động và `•`; **không** đòi Quốc hiệu / Số VB / Nơi nhận |
| `general` | Tài liệu nội bộ tự do (ghi chú, dự thảo nháp) | Chỉ kiểm A4 + lề + font + màu + placeholder còn sót |

## Chọn profile thế nào
1. Văn bản gửi ra ngoài cơ quan, có Quốc hiệu → `administrative`.
2. Là "PHIẾU ..." lưu hành nội bộ → `bieu-mau-noi-bo` (script cũng tự nhận diện qua tên phiếu).
3. Là biên bản họp → `minutes-administrative`.
4. Không phải văn bản hành chính (giáo án, báo cáo học thuật) → `academic`. Lúc này **đừng**
   nói "đúng thể thức NĐ30", vì NĐ30 không áp cho loại này.
5. Không rõ → hỏi user, đừng đoán.

Văn bản QPPL (nghị quyết HĐND, quyết định QPPL của UBND) và văn bản cơ quan Đảng **không có
profile ở đây** — thể thức riêng, xem Luật cứng #2 trong `SKILL.md`, phải hỏi trước khi soạn.

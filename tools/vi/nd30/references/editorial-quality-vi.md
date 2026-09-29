<!-- nha-van:exempt — hướng dẫn kỹ thuật nội bộ về câu chữ, không phải văn bản gửi ra ngoài -->
# Chất lượng câu chữ tiếng Việt trong văn bản hành chính

Thể thức đúng mà câu chữ dở thì cán bộ vẫn phải sửa tay. Mục này lo phần **câu chữ**;
phần thông số nằm ở `the-thuc-nd30.md`.

> Cần **SÁNG TÁC** đoạn văn mới (lời mở, lập luận, thuyết minh dài) → theo Luật Viết trong
> `CLAUDE.md`: gọi `/nha-van` rồi `/humanizer`. File này chỉ là thước đo để soi bản nháp.

## 1. Giọng
- Ngôi thứ ba khách quan. Cơ quan tự gọi mình bằng tên viết tắt (`UBND xã`, `Sở`), **không** "tôi/chúng tôi/mình".
- Trang trọng, trung tính. Không cảm thán, không câu hỏi tu từ, không emoji.
- Không tự khen, không quảng cáo ("bước đột phá", "vô cùng hiệu quả", "mang tính lịch sử").

## 2. Động từ hành chính — dùng đúng từ, đừng nói thường

| Đừng viết | Viết |
|---|---|
| làm | tổ chức thực hiện · triển khai |
| coi / để ý | kiểm tra · giám sát · theo dõi |
| nói cho biết | thông báo · báo cáo |
| gửi lên xin | trình · đề nghị xem xét, phê duyệt |
| họp lại bàn | tổ chức hội nghị · lấy ý kiến |
| xong rồi | đã hoàn thành |
| cho phép | phê duyệt · chấp thuận chủ trương |

## 3. Câu
- Một câu một ý. Câu > 40 chữ hoặc có ≥ 3 mệnh đề lồng → tách.
- **Chủ động, nêu rõ chủ thể**: "UBND xã tổ chức thực hiện" — đừng "việc thực hiện được tiến hành".
- Mỗi nhiệm vụ phải rõ **ai làm – làm gì – xong khi nào**. Thiếu chủ thể hoặc thiếu mốc thời gian
  là văn bản chưa dùng được.
- Đa dạng từ nối: *đồng thời, bên cạnh đó, ngoài ra, mặt khác, trên cơ sở đó*.

## 4. Mẫu câu cố định hay dùng
- Mở đầu căn cứ: `Căn cứ <tên VB> số <...> ngày <...> của <cơ quan> về <...>;`
- Dẫn nhập tờ trình: `Thực hiện <VB chỉ đạo>, UBND xã ... báo cáo và trình ... như sau:`
- Đề nghị: `Kính đề nghị <cơ quan> xem xét, phê duyệt ...`
- Kết công văn: `Đề nghị <cơ quan> quan tâm, phối hợp thực hiện./.`
- Kết tờ trình: `UBND xã ... kính trình <cơ quan> xem xét, quyết định./.`

## 5. Định lượng
- Mục tiêu phải có số đo được: "100% hộ dân được phổ biến", "hoàn thành trước 30/11/2026".
- Không có số thật → **placeholder** `[CẦN BỔ SUNG: chỉ tiêu ...]`, tuyệt đối không bịa.

## 6. Blacklist — dấu hiệu văn AI / văn rỗng
`nhằm mục đích tối ưu hóa` · `giải pháp toàn diện` · `nâng cao một cách sâu sắc` ·
`đóng vai trò then chốt` · `không chỉ ... mà còn ...` (lặp nhiều lần) ·
liệt kê ba-thứ-một-nhịp máy móc · em-dash `—` trong văn hành chính (dùng dấu phẩy hoặc `-`).

## 7. Soi nhanh trước khi bàn giao
- [ ] Không có "tôi/mình/chúng ta thân mật" trong thân văn bản.
- [ ] Mọi nhiệm vụ có chủ thể + mốc thời gian.
- [ ] Không câu nào > 40 chữ mà không tách được.
- [ ] Không từ trong blacklist mục 6.
- [ ] Xưng hô, cách gọi tên cơ quan nhất quán từ đầu đến cuối.

# Bộ câu hỏi phỏng vấn user

> Dùng khi pha 3 của workflow. Câu hỏi đã được thiết kế ngắn, có option sẵn,
> phù hợp với `AskUserQuestion`.

## Câu hỏi chung (mọi loại VB)

### Q1 — Mục đích
- Mở: *"Văn bản này dùng để làm gì? Mô tả ngắn gọn 1-2 câu."*
- Có option (nếu loại VB đã rõ):
  - Phiếu biểu quyết: Đồng ý / Không đồng ý / Đồng ý có điều kiện
  - Tờ trình: Phê duyệt mới / Sửa đổi / Bãi bỏ / Xin chủ trương
  - Báo cáo: Định kỳ / Đột xuất / Theo yêu cầu cấp trên

### Q2 — Người ký
- *"Ai sẽ ký? (Họ tên đầy đủ + chức vụ chính xác)"*
- Nếu có sẵn `tri-thuc/05-thong-tin-co-quan.yaml`:
  - Liệt kê các người ký có thẩm quyền dạng option.
  - Thêm option "Người khác" để user nhập tay.

### Q3 — Nơi gửi (chính)
- *"Văn bản gửi cho ai? (cơ quan / cá nhân nhận chính)"*

### Q4 — Nơi nhận (sao gửi)
- *"Có gửi sao cho ai khác không? (cấp trên / đơn vị phối hợp / lưu VT...)"*
- Default nếu user không trả lời: `- Như trên; - Lưu: VT, [Đơn vị soạn]`

### Q5 — Số văn bản
- *"Số văn bản đã có chưa? (vd: 1488/VP-KH&CĐS) — nếu chưa, tôi để trống cho VPHC điền sau khi vào sổ."*

### Q6 — Ngày ký
- *"Ngày ký dự kiến? (mặc định hôm nay: [today])"*

---

## Câu hỏi đặc thù theo loại VB

### Công văn xin ý kiến

- *"Xin ý kiến về cái gì? (dự thảo VB / chủ trương / đề án...)"*
- *"Hạn phản hồi đến ngày nào?"*
- *"Đính kèm tài liệu gì? (dự thảo, biểu, báo cáo nền...)"*

### Phiếu biểu quyết / Phiếu ghi ý kiến

- *"Quan điểm: Đồng ý hay Không đồng ý?"* (BẮT BUỘC — không default)
- Nếu Không đồng ý → *"Lý do cụ thể?"*
- *"Có ý kiến bổ sung gì không? (vd: 'đề nghị bỏ cụm từ X tại Điều Y')"*
- *"Hạn nộp phiếu?"*

### Tờ trình

- *"Trình lên ai? (cấp nào: UBND xã / huyện / tỉnh / Sở / Bộ)"*
- *"Xin phê duyệt nội dung gì cụ thể?"*
- *"Căn cứ pháp lý chính? (NĐ, TT, QĐ nào)"*
- *"Đề xuất phương án mấy? (1 phương án / nhiều phương án so sánh)"*

### Quyết định

- *"Loại QĐ: Cá biệt (nội bộ) hay Quy phạm pháp luật?"*
- *"Đối tượng điều chỉnh: cá nhân nào / tổ chức nào / phạm vi?"*
- *"Hiệu lực: ngày ký / ngày cụ thể?"*
- *"Có bãi bỏ VB cũ không? (cần ghi rõ số VB cũ)"*

### Báo cáo

- *"Kỳ báo cáo: Tháng / Quý / 6 tháng / Năm / Đột xuất?"*
- *"Báo cáo cho ai? (cấp trên / cuộc họp / theo yêu cầu)"*
- *"Trọng tâm: Kết quả thực hiện / Khó khăn vướng mắc / Đề xuất / Tổng hợp?"*

### Thông báo / Kết luận

- *"Nguồn gốc: Kết luận cuộc họp ngày X / Ý kiến chỉ đạo của Y / Thông báo nội bộ?"*
- *"Đối tượng nhận để biết / để thực hiện / để phối hợp?"*

### Báo cáo góp ý dự thảo theo đề cương cứng

- *"Cấp trên (Bộ/Sở) đã gửi đề cương báo cáo chưa? File nào?"* — đề cương BẮT BUỘC để biết cấu trúc.
- *"Có file khảo sát ý kiến (Excel) đã thu thập sẵn không?"* — nếu có, dùng `aggregate_survey.py` trước.
- *"Quan điểm chung về dự thảo: Cơ bản nhất trí / Có điều chỉnh lớn / Không đồng tình?"*
- Nếu Cơ bản nhất trí → *"Bạn muốn nêu mấy ý kiến cụ thể? Ý nào ưu tiên đưa vào bảng?"*
  - Đề nghị sàng lọc: chỉ chọn 5-10 ý kiến quan trọng nhất, gom các ý trùng lặp.
- *"Có đề xuất bổ sung điều khoản mới nào không? (vd: cơ chế kinh phí, cơ chế phối hợp)"*
- *"Người ký là Thủ trưởng (GĐ/Trưởng) hay cấp phó? Ký KT./TL.?"*

### Kế hoạch

- *"Kế hoạch thực hiện gì? (NQ / QĐ / đề án nào)"*
- *"Thời gian thực hiện: từ ngày — đến ngày?"*
- *"Phân công nhiệm vụ cho ai làm chủ trì / phối hợp?"*

---

## Câu hỏi yêu cầu file nguồn (Pha 4)

### Trigger phrase từ user → câu hỏi tương ứng

| User nói | AI hỏi |
|---|---|
| "Theo NĐ 30/2020" | "Bạn có file NĐ 30 không? Nếu không tôi viện dẫn theo trí nhớ + đánh dấu để bạn duyệt." |
| "Tờ trình số X" | "File tờ trình X có sẵn chứ? Tôi cần đọc để trích đúng số/ngày/nội dung chính." |
| "Quyết định trước đây" | "Bạn cho tôi file QĐ cũ — để bãi bỏ đúng số/ngày, tránh viện dẫn sai." |
| "Theo chỉ đạo của ..." | "Có VB chỉ đạo bằng giấy không? Hay chỉ là chỉ đạo miệng tại cuộc họp?" |
| "Biểu tiếp thu ý kiến" | "Có file biểu tổng hợp chưa? Tôi cần để trích các ý kiến đã có và phương án xử lý." |

---

## Khi user trả lời "tôi không biết"

- Đánh dấu `???` trong `2-du-lieu.yaml` cho field đó.
- Tiếp tục các nhóm câu hỏi khác.
- Trước khi xuất VB cuối cùng → liệt kê tất cả `???` còn sót, hỏi 1 lần cuối.

## Khi user trả lời "tự quyết"

- KHÔNG được tự quyết với:
  - Quan điểm biểu quyết (Đồng ý / Không đồng ý)
  - Mức phê duyệt
  - Số tiền
  - Tên người ký cụ thể
- ĐƯỢC tự quyết với:
  - Câu chữ trong nội dung (viết lại cho chuẩn ND30)
  - Cấu trúc (mở đầu, thân, kết)
  - Format trình bày (font, lề, dãn dòng theo NĐ 30)

## Sau cùng — confirm trước khi soạn

Trước khi vào Pha 5 (fill template), tóm tắt 1 lần:

```
Tôi sẽ soạn:
- Loại: <loại VB>
- Người ký: <tên + chức vụ>
- Mục đích: <1 dòng>
- Quan điểm chính: <1 dòng>
- Nơi gửi: <ai>
- Đính kèm: <X file trong 3-tham-chieu/>
- Số VB: <số / "để trống">
- Ngày: <ngày>

OK soạn chứ? (Y/N hoặc nói chỗ cần sửa)
```

Đợi user xác nhận → mới fill template.

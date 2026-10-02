# Video kiểu Vox — biên bản chạy thử (6.3.2-vi.15)

Biên bản chạy thật của kiểu `phong-cach: vox`, theo thiết kế ở [2026-10-01-video-vox-design.md](2026-10-01-video-vox-design.md) (bản v2 ở mục 12). Máy thử: Windows 11, 9router chạy trên máy, mô hình vẽ `ag/gemini-3.1-flash-image`, giọng Thu Giang của VieNeu 3.6.4.

Đề bài cả hai lần: "video dạng Vox chủ đề giao tiếp với đồng nghiệp, dài 60 giây, khổ ngang 16:9".

## Lần 1 (bản v1) — 2026-10-01

| Mục | Kết quả |
|---|---|
| Thời lượng | 56,1 giây (mục tiêu 60) |
| Giọng | edge-tts, giọng nữ |
| Nền | nền giấy vẽ bằng mã, dùng chung |

Lỗi gặp khi chạy thật, đã sửa trong nhánh:

- `anh_vox.py` treo hơn 5 giờ vì một lần vẽ không trả lời: thêm hạn chót 180 giây cho mỗi lần vẽ.
- Lần chạy bị ngắt làm ảnh API bị ghi nhầm nguồn: `nguon.json` nay ghi sau từng ảnh.
- Phản hồi 200 nhưng rỗng không được thử lại: nay thử lại.
- Ảnh tách nền hỏng chuyển sang khung vẫn còn nền xanh: nay tách nền lên màu giấy trước khi đóng khung.

Nhận xét của chủ repo: chưa đẹp bằng video mẫu, khung hình rung gây nhức mắt, không cần ghi nguồn ảnh trên hình, nội dung nghèo và ít hình, lời đọc rời rạc; đổi sang giọng Thu Giang của VieNeu. Bản v2 sửa đúng các điểm này.

## Lần 2 (bản v2) — 2026-10-03

| Mục | Kết quả |
|---|---|
| Kịch bản | 6 cảnh, 231 từ |
| Thời lượng | 58,27 giây (mục tiêu 60) |
| Giọng | Thu Giang (VieNeu), đo được 4,2–4,3 từ/giây |
| Ảnh AI | 12 ảnh (tính cả nền từng cảnh), vẽ trong 124 giây |
| Dựng video | 125 giây |
| Cảnh báo | không có |
| Nguồn | không hiện trên hình; ghi trong `nguon.txt` cạnh video |

Đã xem khung hình từng cảnh: mỗi cảnh có nền cắt dán riêng, nhãn và cụm hình hiện ngay từ đầu cảnh, không còn rung hay nảy.

## Khác với thiết kế

- Mục 12.3 của thiết kế giữ một cú đẩy máy rất chậm (1,00 → 1,04). Bản đã làm bỏ hẳn phóng to, chỉ để nền trôi ngang chậm sau lớp hình: phóng to từng khung làm chữ nhoè lệch giữa các khung, trôi ngang theo số nguyên điểm ảnh thì không.

## Việc còn lại

- Kiểu `cat-dan` cũ: `clip-path` của chuyển cảnh `xe-giay` trong `chuyen-canh.js` thiếu đơn vị `px`, nên vết xé nhiều khả năng không hiện. Lỗi có từ trước, nằm ngoài phạm vi đợt này.
- Driver card màn hình của máy thử cũ hơn mức NVENC cần, nên chưa đo được mã hoá bằng GPU.

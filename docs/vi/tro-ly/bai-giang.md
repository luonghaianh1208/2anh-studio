# Loại việc: Bài giảng

File dành cho AI. Luôn đọc `docs/vi/tro-ly/quy-trinh-hoi.md` trước file này.

## Khi nào dùng

Thầy cô cần slide cho một bài dạy hoặc tiết học, ở bất kỳ môn và cấp học nào.

Ví dụ câu lệnh:
- "Tạo bài giảng Vật lí 10 bài Chuyển động thẳng đều"
- "Làm slide cho tiết Ngữ văn 7 bài Bầy chim chìa vôi"

## Câu hỏi bắt buộc

1. Môn, lớp, tên bài, và bài thuộc chủ đề hoặc chương nào?
   Gợi ý: lấy từ câu lệnh nếu đã có; chỉ hỏi phần còn thiếu.
2. Thầy cô dạy theo bộ sách nào: Kết nối tri thức với cuộc sống, Chân trời sáng tạo, Cánh diều, hay bộ khác?
   Gợi ý: nếu hồ sơ hoặc lần trước đã có bộ sách thì đề xuất lại bộ đó.
3. Bài dạy trong bao nhiêu tiết, mỗi tiết bao nhiêu phút?
   Gợi ý: 1 tiết × 45 phút (Tiểu học: 35 phút).
4. Mục tiêu về kiến thức, năng lực và phẩm chất của bài là gì?
   Gợi ý: AI đề xuất 2–3 ý cho mỗi nhóm theo chương trình giáo dục phổ thông 2018 để thầy cô sửa.
5. Thầy cô muốn có những hoạt động nào (trò chơi khởi động, thảo luận nhóm, phiếu học tập, câu hỏi trắc nghiệm, video), và slide cần hiệu ứng ở mức nào: không, vừa, hay nhiều? Chữ trên slide nên ít chữ, vừa, hay nhiều chữ?
   Gợi ý: một trò chơi khởi động ngắn, 3–5 câu trắc nghiệm ở phần luyện tập; hiệu ứng mức vừa — hiện từng ý khi bấm, bấm để hiện đáp án, chuyển trang nổi bật khi sang hoạt động mới; ít chữ — mỗi trang một ý, lời giải thích để ở lời giảng.
6. Học sinh của lớp có đặc điểm gì, và phòng học dùng thiết bị gì (máy chiếu 16:9, máy chiếu 4:3, TV)?
   Gợi ý: lớp có trình độ trung bình, dùng máy chiếu 16:9.
7. Thầy cô có tài liệu sẵn không (giáo án Word, ảnh trong sách giáo khoa, đề bài)?
   Gợi ý: không có; AI soạn từ nội dung bài học, tìm ảnh thật và vẽ sơ đồ minh hoạ.

## Câu hỏi tuỳ chọn

- Lớp có học sinh cần hỗ trợ riêng không? Chỉ hỏi khi thầy cô nhắc tới học sinh khuyết tật hoặc học sinh cần kèm cặp.
- Có cần bản in phiếu học tập cho học sinh không? Chỉ hỏi khi thầy cô nhắc tới phiếu học tập.

## Tạo nhanh

1. Môn, lớp và tên bài (câu hỏi bắt buộc 1).
2. Bộ sách (câu hỏi bắt buộc 2).

## Cấu trúc gợi ý

- THCS và THPT: theo 4 hoạt động của Công văn 5512/BGDĐT-GDTrH — Mở đầu → Hình thành kiến thức mới → Luyện tập → Vận dụng. Thêm trang bìa và trang mục tiêu ở đầu, trang tổng kết và dặn dò ở cuối.
- Tiểu học: theo mạch tiết học thầy cô quen dùng; không áp khung 4 hoạt động nếu thầy cô không yêu cầu.
- Mỗi hoạt động nêu rõ nhiệm vụ của học sinh. Câu hỏi trắc nghiệm đặt đáp án ở slide riêng ngay sau câu hỏi.

## Phong cách gợi ý

- Học đường, sáng rõ, nền sáng, tương phản cao để học sinh cuối lớp vẫn đọc được.
- Chữ nội dung từ 28pt; font Segoe UI hoặc Arial.
- Đề xuất mode `instructional` của upstream.
- Khi dùng máy chiếu 4:3 có thể đề xuất layout `presentation_core_43` của upstream.

## Khổ slide

- Mặc định `ppt169`.
- Dùng `ppt43` khi thầy cô dùng máy chiếu 4:3.

## Ghi vào brief

- Loại việc: Bài giảng.
- Thầy cô yêu cầu: môn, lớp, tên bài, bộ sách, số tiết, các hoạt động thầy cô chọn, đặc điểm học sinh, thiết bị, tài liệu có sẵn — ghi đúng lời thầy cô.
- AI đề xuất (thầy cô đã đồng ý): mục tiêu và các gợi ý thầy cô chấp nhận.
- Mức hiệu ứng: không, vừa hoặc nhiều, theo `docs/vi/tro-ly/hieu-ung-lop-hoc.md`; kèm "(AI đề xuất, chưa duyệt)" khi thầy cô chưa chọn.
- Mật độ chữ: ít chữ, vừa hoặc nhiều chữ, theo mục "Mật độ chữ" của `docs/vi/tro-ly/quy-trinh-hoi.md`; kèm "(AI đề xuất, chưa duyệt)" khi thầy cô chưa chọn.
- Cấu trúc gợi ý, Phong cách gợi ý, Khổ slide: theo các mục tương ứng của file này.
- Viết theo mẫu `docs/vi/tro-ly/mau-brief.md`.

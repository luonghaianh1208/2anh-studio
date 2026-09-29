# PPT Master — Bản Việt

> Tạo bài thuyết trình PowerPoint **chỉnh sửa được** từ PDF, Word, trang web hoặc một ý tưởng — chỉ bằng cách trò chuyện với AI.

Đây là bản Việt hoá và đóng gói của [PPT Master](https://github.com/hugohe3/ppt-master) (tác giả **Hugo He**, giấy phép MIT), do **Lương Hải Anh — 2Anh AI Education** thực hiện. Bản này thêm bộ cài một lần bấm cho Windows, quy tắc tiếng Việt cho AI và tài liệu tiếng Việt; phần lõi giữ nguyên dự án gốc.

> **Dành cho AI agent:** người dùng nhờ cài bộ công cụ này (hoặc chỉ dán link repo) thì làm theo [docs/vi/cai-dat-bang-ai.md](docs/vi/cai-dat-bang-ai.md), không tự nghĩ cách cài khác.

Phiên bản: **6.3.2-vi.12** · [Nhật ký thay đổi](CHANGELOG-VI.md)

## Bắt đầu trong 3 bước

1. **Tải về.** Bấm **Code → Download ZIP** rồi giải nén, hoặc dùng Git:
   ```
   git clone https://github.com/luonghaianh1208/PPTmaster.git
   ```
   Tải bằng Git thì sau này cập nhật chỉ bằng một cú bấm.
2. **Cài đặt.** Bấm đúp **`CAI-DAT.bat`**. Bộ cài kiểm tra Python, cài thư viện, tạo file cấu hình và xuất thử một file PPTX. Chi tiết: [Cài đặt trên Windows](docs/vi/cai-dat-windows.md).
3. **Tạo slide.** Mở thư mục này trong Claude Code, Cursor hoặc Antigravity rồi nhắn cho AI, ví dụ `Tạo bài thuyết trình 10 slide giới thiệu trường THPT`. Xem [Bắt đầu nhanh](docs/vi/bat-dau-nhanh.md).

Dùng Antigravity và muốn AI làm hết: mở một thư mục trống rồi dán câu lệnh mẫu trong [Bắt đầu nhanh](docs/vi/bat-dau-nhanh.md#để-ai-tự-cài), AI tự tải, tự cài và báo khi sẵn sàng.

macOS/Linux: chạy `sh tools/vi/setup.sh`.

## Làm được gì

- Hỏi thầy cô một lượt ngắn (môn, lớp, bộ sách, mục tiêu, đơn vị…) trước khi làm bài giảng, báo cáo, hoạt động Đoàn, poster và tập huấn, nên nội dung sát thực tế.
- Tạo PPTX từ PDF, Word, trang web, Markdown hoặc chỉ từ một chủ đề.
- Chữ, hình và biểu đồ là đối tượng PowerPoint thật, sửa trực tiếp được.
- Khổ slide 16:9, 4:3, bài đăng Facebook/TikTok 3:4, ảnh vuông Zalo, story 9:16.
- Hiệu ứng theo mức thầy cô chọn (không, vừa, nhiều): hiện từng ý khi bấm, bấm để hiện đáp án, Morph cho diễn biến thí nghiệm, chuyển trang giữa các hoạt động; bài có ảnh thật và sơ đồ thay vì toàn chữ.
- Thuyết minh bằng giọng tiếng Việt.
- Làm đẹp lại một file PPTX có sẵn.
- Soạn **đề kiểm tra** KHTN/Vật lí/Hoá học/Sinh học bằng tiếng Anh, từ đề tiếng Việt có sẵn hoặc từ đầu, xuất ra file Word.
- Soạn **giáo án** kế hoạch bài dạy theo Công văn 5512, tích hợp năng lực số và năng lực AI, xuất ra file Word.
- Tạo **thí nghiệm ảo** Toán, Vật lí, Hoá học: một file HTML chạy không cần mạng, có bảng số liệu, đồ thị và phiếu học tập Word; 8 mô hình đã kiểm bằng số.
- Dựng **video giải thích** kiểu viết tay từ nội dung bài: chữ, công thức, đồ thị và thí nghiệm ảo được viết dần ra theo giọng đọc tiếng Việt, có phụ đề.
- Soạn **văn bản hành chính** (công văn, tờ trình, quyết định, thông báo, giấy mời, biên bản…) ra file Word đúng thể thức Nghị định 30, có bộ kiểm thể thức; thông tin chưa có để ô cần bổ sung, không tự bịa.

## Ba file bấm đúp

| File | Khi nào dùng |
|---|---|
| `CAI-DAT.bat` | Lần đầu cài đặt, hoặc khi được hướng dẫn cài lại |
| `KIEM-TRA.bat` | Kiểm tra máy đã sẵn sàng chưa, khi gặp lỗi |
| `CAP-NHAT.bat` | Lấy phiên bản mới nhất (chỉ với bản tải bằng Git) |

## Tài liệu

| Tài liệu | Nội dung |
|---|---|
| [Cài đặt trên Windows](docs/vi/cai-dat-windows.md) | Cài Python, tải bộ công cụ, đọc kết quả kiểm tra |
| [Bắt đầu nhanh](docs/vi/bat-dau-nhanh.md) | Từ lúc cài xong đến file PPTX đầu tiên |
| [Câu lệnh mẫu](docs/vi/cau-lenh-mau.md) | Câu lệnh cho bài giảng, báo cáo, poster, thuyết minh |
| [Xử lý lỗi](docs/vi/xu-ly-loi.md) | Lỗi thường gặp và cách sửa |
| [Lấy API key](docs/vi/lay-api-key.md) | Bật tạo ảnh bằng AI |
| [Soạn đề tiếng Anh](docs/vi/soan-de-tieng-anh.md) | Từ đề tiếng Việt hoặc từ đầu, ra ba file Word (hai file nếu không cần bản song ngữ) |
| [Soạn giáo án](docs/vi/soan-giao-an.md) | Kế hoạch bài dạy 5512 tích hợp năng lực số và AI |
| [Làm thí nghiệm ảo](docs/vi/thi-nghiem-ao.md) | File HTML tương tác chạy không cần mạng, kèm phiếu học tập |
| [Làm video giải thích](docs/vi/video-giai-thich.md) | Video viết tay có giọng đọc và phụ đề, dựng từ nội dung bài |
| [Soạn văn bản hành chính](docs/vi/van-ban-hanh-chinh.md) | Công văn, tờ trình, quyết định… ra Word đúng thể thức Nghị định 30 |

Tài liệu gốc (tiếng Anh) của dự án nằm trong [docs/](docs/).

## Cập nhật

- Bản tải bằng Git: bấm đúp `CAP-NHAT.bat`.
- Bản ZIP: tải bản mới rồi chép thư mục `projects\` và file `.env` của bạn sang.
- Từng dùng bản cũ (v2): thư mục `examples/` đã được gỡ bỏ, bộ ví dụ xem tại https://github.com/hugohe3/ppt-master-examples; trạng thái bản cũ vẫn giữ ở tag `v2-vi-legacy`. Chi tiết trong [Nhật ký thay đổi](CHANGELOG-VI.md).

## Giấy phép & Ghi công

- Lõi PPT Master: © 2025-2026 Hugo He, giấy phép MIT — [LICENSE](LICENSE). Nhà tài trợ của dự án gốc: [SPONSORS.md](skills/ppt-master/SPONSORS.md).
- Phần Việt hoá và đóng gói: Lương Hải Anh — 2Anh AI Education, giấy phép MIT. Chi tiết: [NOTICE](NOTICE).
- ND30 — © 2026 Nguyễn Minh Phát, MIT (tools/vi/nd30): bộ sinh và bộ kiểm văn bản hành chính theo Nghị định 30, nhúng nguyên trạng từ https://github.com/kanazawahere/nd30. Giấy phép: [tools/vi/nd30/LICENSE](tools/vi/nd30/LICENSE); nguồn và SHA-256: [tools/vi/nd30/NGUON.md](tools/vi/nd30/NGUON.md).
- Bộ ví dụ của dự án gốc: https://github.com/hugohe3/ppt-master-examples

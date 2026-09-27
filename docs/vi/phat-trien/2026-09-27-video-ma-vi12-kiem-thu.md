# Biên bản kiểm thử: video giải thích vi.12

Máy chủ repo: Windows 11, Intel Core i5-9400F (6 lõi), Chromium headless shell của Playwright, FFmpeg bản Gyan 8.1.2. Nhánh `feat/vi-video-vi12`. Spec: `docs/vi/phat-trien/2026-09-27-video-ma-vi12-design.md`. Kế hoạch: `docs/vi/phat-trien/2026-09-27-video-ma-vi12-plan.md`.

## Task 1: đối tượng khổ và Full HD

### Đo thời gian dựng

Ngày 2026-09-28. Fixture `tools/vi/fixtures/video-mau` (8 cảnh, video 76,8 giây), giọng giả: 8 file `giong/canh-N.mp3` tiếng hồng 8 giây tạo bằng FFmpeg (công cụ coi là giọng thầy cô, không gọi mạng). Lệnh `C:/Users/ADMIN/vmt/v/Scripts/python.exe tools/vi/video_ma.py <bản sao fixture>`, 3 tiến trình Chromium (mặc định của máy 6 lõi), đo bằng `time` (chụp khung và ghép FFmpeg, chưa gồm tạo giọng).

| Lần đo | Mã | Khổ, độ phân giải | Khung tạm | Thời gian |
|---|---|---|---|---|
| 1 | vi.11, trước khi sửa | ngang 1280×720 | PNG | 66,9 s |
| 2 | Task 1 | ngang 1920×1080 | PNG | 116,8 s |
| 3 | Task 1 | ngang 1920×1080 | JPEG chất lượng 95 | 92,0 s |
| 4 | Task 1 | ngang 1280×720 (`do-phan-giai: 720`) | JPEG chất lượng 95 | 53,7 s |
| 5 | Task 1, đo lại lần 3 | ngang 1920×1080 | JPEG chất lượng 95 | 94,5 s |

- Lần 2 chậm hơn 720 cũ **1,75 lần**, vượt ngưỡng 1,6 của kế hoạch.
- Vì vậy khung tạm đổi sang JPEG chất lượng 95 (`page.screenshot(type="jpeg", quality=95)`, ghép bằng `-framerate 30 -i .khung/anh/f%06d.jpg`). Lần 3 và 5 chậm hơn 720 cũ **1,38–1,41 lần**, dưới ngưỡng.
- Ở 720, JPEG còn nhanh hơn PNG cũ (53,7 s so với 66,9 s), nên `do-phan-giai: 720` giữ tốc độ cũ cho máy yếu.
- Ước tính mục tiêu của spec: 76,8 giây video dựng mất khoảng 93 giây ở Full HD, tức khoảng 1,2 lần thời lượng. Video 5 phút mất khoảng 6 phút trên máy này, dưới mốc 12 phút.

### Quyết định

- Khung tạm để ghép là JPEG chất lượng 95 (`chup.DUOI_KHUNG`). Nền cảnh trước của chuyển cảnh đọc lại từ khung JPEG này.
- Ảnh xem trước (`--xem-truoc`) và ảnh tham chiếu vẫn là PNG.
- `ghep.py` không co giãn khung. Trước khi ghép, nó đọc kích thước khung đầu bằng `ffprobe`; khác `rong_xuat`×`cao_xuat` của khổ thì báo lỗi `dung`.

### Ảnh tham chiếu vi.11

Khung cuối mỗi cảnh của `video-mau` (8 cảnh) và `video-hinh` (6 cảnh) được chụp ở 1280×720 bằng mã vi.11 chưa sửa, qua `--xem-truoc` với giọng giả. Ảnh nằm ở `tools/vi/tests/data/tham-chieu-vi11/` (commit riêng, trước mọi thay đổi mã).

`test_video_ma_kho.ChupKhoTest.test_720_giong_anh_tham_chieu_vi11` dựng lại hai fixture với `do-phan-giai: 720` và so từng ảnh bằng Chromium. Ngưỡng: không quá 0,5 % điểm ảnh có một kênh màu lệch quá 16 mức. Kết quả: cả 14 ảnh lệch 0 %, và giống ảnh tham chiếu tới từng byte.

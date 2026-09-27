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

## Task 3: bố cục dọc và giới hạn chữ khổ dọc

### Cách đo

Ngày 2026-09-28. Khổ dọc 720×1280 điểm CSS, vạch phụ đề y 1080, phong cách `viet-tay` (Itim). Mỗi loại cảnh dựng ở số dòng lặp tối đa, mọi trường chữ là chuỗi "Nghiêng nghiễm nhiên " lặp, cắt đúng độ dài (ký tự cuối là khoảng trắng thì thay bằng "n"). Một cảnh qua khi `THI_VIDEO.kiemTran()` rỗng và mọi phần tử của lớp bảng (chữ, nét, hình, ảnh, bản vẽ thí nghiệm, dòng nguồn) nằm trong 720 bề ngang và có đáy ≤ 1080.

- Biến thể đo: biểu đồ `cot`, `duong`, `tron`; dòng thời gian 6 và 3 mốc; câu hỏi 4 và 3 lựa chọn; và bản có hình ở cột phụ cho `tieu-de`, `khai-niem`, `cong-thuc`, `y-tung-y`, `so-do`.
- Bắt đầu từ giới hạn khổ ngang. Loại nào không qua thì hạ đồng loạt các trường của loại đó theo cùng tỉ lệ tới khi qua, rồi nâng từng trường lên hết mức còn qua (tìm nhị phân, hai vòng).
- Test giữ kết quả: `tools/vi/tests/test_video_ma_kho_doc.py` (mọi loại ở `LIMITS_DOC`, có và không có cột phụ).

### Kết quả

Mọi trường không nêu dưới đây qua ở đúng giới hạn khổ ngang, nên `LIMITS_DOC` bằng `LIMITS`.

| Loại, trường | Ngang | Dọc không cột phụ | Dọc có hình ở cột phụ | `LIMITS_DOC` |
|---|---|---|---|---|
| `khai-niem`, `dinh-nghia` | 220 | 220 | 132 | 132 |
| `cong-thuc`, `giai-thich` (4 dòng) | 60 | 60 | 51 | 51 |
| `y-tung-y`, `y` (6 ý) | 60 | 60 | 40 | 40 |
| `bieu-do`, `du-lieu` phần số | parse `SO_DAI` 10 | 8 | — | 8 |

- Ba trường đầu thấp hơn vì ở khổ dọc cột phụ là khối dưới nội dung (y 640–1020), nên ô nội dung hẹp chỉ cao 300.
- Số của `du-lieu` bị giới hạn vì 8 cột trong bề rộng 580 chỉ còn 66 điểm mỗi cột. Số ghi trên cột không được rộng hơn cột.
- Task 4 đo lại với font của `cat-dan` và hạ giới hạn nếu cần.

## Task 4: phong cách cắt dán và font Be Vietnam Pro

### Cách đo

Ngày 2026-09-28. Công cụ đo đã commit: `tools/vi/tests/do_gioi_han.py` (chạy `C:/Users/ADMIN/vmt/v/Scripts/python.exe tools/vi/tests/do_gioi_han.py <ngang|doc> <viet-tay|cat-dan> [loại ...]`, in các trường phải hạ). Cùng chuỗi thử, số dòng lặp tối đa và các biến thể như Task 3, thêm biến thể có hình ở cột phụ ở cả khổ ngang.

- Một loại cảnh qua ở giới hạn hiện tại thì giữ. Không qua thì hạ đồng loạt mọi trường theo cùng tỉ lệ tới khi qua, rồi nâng từng trường lên hết mức còn qua (tìm nhị phân, hai vòng). Giới hạn chỉ hạ.
- Một cảnh qua khi `THI_VIDEO.kiemTran()` rỗng và mọi phần tử của lớp bảng nằm trong khung, đáy không quá vạch phụ đề. Ô chữ đo bằng hộp của chính dòng chữ: vài ô khổ ngang của vi.11 (chú thích ảnh đáy 625, tên trục ngang đồ thị đáy 622) lố vạch dù chữ nằm trên vạch. Nét vẽ tay được lố vạch tới 3 điểm vì khung hộp khổ ngang của vi.11 nằm đúng y 620 và lượn ±2.
- Kiểm chứng công cụ: với `viet-tay`, cả hai khổ ra bảng rỗng (khớp `LIMITS` và `LIMITS_DOC` của Task 3).

### Kết quả

Be Vietnam Pro rộng hơn Itim, nên vài trường phải hạ. Bảng `viet-tay` giữ nguyên; `cat-dan` có bảng riêng `kiem.LIMITS_CAT_DAN`, `LIMITS_HAI_PHAN_CAT_DAN` (ngang) và `LIMITS_CAT_DAN_DOC`, `LIMITS_HAI_PHAN_CAT_DAN_DOC` (dọc), chọn qua `kiem.bang_gioi_han(kho, phong_cach)`. Lỗi vượt giới hạn ghi thêm "(giới hạn phong cách cắt dán)".

| Khổ | Loại, trường | `viet-tay` | `cat-dan` |
|---|---|---|---|
| ngang | `tieu-de`, `chu` | 90 | 88 |
| ngang | `cong-thuc`, `bieu-thuc` | 90 | 89 |
| ngang | `cong-thuc`, `giai-thich` (4 dòng) | 60 | 59 |
| ngang | `y-tung-y`, `y` (6 ý) | 60 | 54 |
| ngang | `anh`, `chu-thich` | 90 | 89 |
| dọc | `khai-niem`, `dinh-nghia` | 132 | 127 |
| dọc | `cong-thuc`, `giai-thich` (4 dòng) | 51 | 45 |
| dọc | `y-tung-y`, `y` (6 ý) | 40 | 34 |
| dọc | `do-thi`, `truc-doc` | 40 | 38 |
| dọc | `bieu-do`, `don-vi` | 12 | 10 |
| dọc | `bieu-do`, `truc-doc` | 40 | 36 |
| dọc | `bieu-do`, `du-lieu` phần số | 8 | 7 |
| dọc | `dong-thoi-gian`, `moc` phần nhãn | 12 | 10 |

- Mọi trường khác qua ở đúng giới hạn `viet-tay` của khổ đó.
- Nhãn tiêu đề cảnh (chữ hoa ExtraBold trên băng dính) dùng cỡ 34, tiêu đề dài hơn 40 ký tự cỡ 26; ở cỡ đó tiêu đề 90 ký tự vừa ô `tieu-de` của cả hai khổ, kể cả khi có cột phụ.
- Test giữ kết quả: `tools/vi/tests/test_video_ma_cat_dan.py` (mọi loại × hai khổ ở bảng `cat-dan`, có và không có cột phụ). Chạy lại test này với bảng `cat-dan` đặt bằng bảng `viet-tay` thì trượt 12 cảnh (5 ngang, 7 dọc).

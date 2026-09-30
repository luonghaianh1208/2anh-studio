# Chụp khung bằng beginFrame — số đo (2026-10-01)

Máy đo: Intel Core i5-9400F (6 lõi), GeForce GTX 1050 (driver 560.94), Chromium 153 của Playwright 1.63, Full HD 30 khung/giây, 3 tiến trình chụp.

## Thời gian đi đâu (trước khi sửa)

Video cắt dán `in-tien-lam-phat-cat-dan`, 92,5 giây:

| Bước | Thời gian |
|---|---|
| Chụp khung (`chup_song_song`) | 234 giây (78 %) |
| Ghép (`ghep_video`: âm thanh, phụ đề, mã hoá H.264) | 59 giây (20 %) |
| Tổng | 302 giây |

Trong mỗi khung, `datThoiDiem(t)` chỉ mất khoảng 3 ms; `page.screenshot` JPEG Full HD mất khoảng 120 ms.

## Các cách đã thử (bản rút gọn 4 cảnh)

| Cách | Kết quả |
|---|---|
| 5 tiến trình thay vì 3 | Không nhanh hơn: CPU đã bận hết. |
| Cờ GPU cho Chromium (ANGLE D3D11, GPU rasterization) | Chụp nhanh hơn khoảng 25 %. |
| `Page.captureScreenshot` với `optimizeForSpeed` | Ở đúng Full HD không nhanh hơn. |
| x264 `veryfast` thay `medium` | Ghép bớt khoảng 4 giây. |
| NVENC, Quick Sync | Không chạy: NVENC của FFmpeg cần driver NVIDIA ≥ 610, Quick Sync không mở được phiên. |
| `HeadlessExperimental.beginFrame` | 120 → 58 ms/khung ở Full HD. Bật thêm GPU thì chậm hơn (66 ms). |

Hai điều cần biết:

- `beginFrame` bỏ qua `device_scale_factor` của context: phải đặt `--force-device-scale-factor` khi mở trình duyệt, nếu không ảnh ra 1280×720.
- Lần gọi đầu sau khi mở trình duyệt chưa có ảnh; các lần sau luôn có, kể cả khi trang không đổi.

## Sau khi sửa (dựng thật cả video)

| Video | Cách cũ | beginFrame |
|---|---|---|
| Cắt dán ngang, 92,5 giây | 243 giây | 127 giây |
| Viết tay ngang, 155,9 giây | 196 giây | 140 giây |
| Khổ dọc, 65,1 giây | 96 giây | 72 giây |
| Viết tay ngang, 155,9 giây, 1 tiến trình | — | 225 giây |

Phần chụp nhanh khoảng 1,7–2,5 lần; phần ghép giữ nguyên nên giờ chiếm khoảng 30–40 % thời gian.

Hình: SSIM giữa hai bản cắt dán là 0,991 trung bình, thấp nhất 0,974 ở từng khung. Ảnh hiệu số chỉ còn viền mép chữ và nét vẽ (khử răng cưa lệch dưới một điểm ảnh), không thấy bằng mắt.

## Cách làm

- `chup.trang_chup(kho)` mở Chromium với `--enable-begin-frame-control`, `--deterministic-mode` và tỉ lệ điểm ảnh của khổ, rồi gọi mồi một khung. Mở không được hoặc không ra ảnh thì dùng `page.screenshot` như cũ.
- `chup.TrangKhung` bọc trang: `anh()` gọi `beginFrame` tối đa 3 lần cho đến khi có ảnh; mọi lệnh khác chuyển cho trang gốc.
- `mo_trang` hỏi `THI_VIDEO.san` theo giờ (50 ms) thay vì theo khung vẽ, vì trang beginFrame không tự vẽ nên `requestAnimationFrame` không chạy.
- Ảnh xem trước (`--xem-truoc`) và bước đo tràn chữ vẫn dùng `trinh_duyet()`/`trang_moi()` như cũ.

## Chưa kiểm

- Máy 2–3 lõi thật: con số "khoảng 1,5 lần" trong hướng dẫn suy từ lần đo một tiến trình trên máy này.
- Chromium ngoài bản của Playwright: nếu thiếu `beginFrame` thì tự quay về cách cũ (có test giả lập), chưa chạy trên máy như vậy.

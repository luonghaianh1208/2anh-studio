# Video ngắn "nhịp hình" — thiết kế

Ngày: 2026-10-19 · Trạng thái: chờ duyệt · Thay cho phong cách `ngan` neon (vi.17–vi.21).

## 1. Vì sao làm lại

Video ngắn hiện tại (`phong-cach: ngan`) bị chê "xấu, không bắt mắt, không thu hút". Đối chiếu 7 video tham khảo của 4 kênh (banlinhmem 0,9–1,3 triệu lượt xem; ainius.net; cuongit96; hoclomai):

| Kênh tham khảo | Video `ngan` hiện tại |
|---|---|
| Hình đổi theo **từng cụm lời**, 1–2 giây một lần: thêm người, đổi tư thế, số tăng, chấm hiện thêm, thẻ trượt vào | Mỗi cảnh 6–8 giây gần như đứng yên sau khi hiện chữ |
| Mỗi màn có **một hình chính chiếm giữa khung** (người que, số khổng lồ, lưới chấm, biểu đồ, tin nhắn, bài báo) | Chữ chiếm phần lớn khung, biểu tượng nhỏ lọt thỏm giữa nền rộng |
| Nhãn tiêu đề to ở trên, phụ đề một dòng ở dưới, thanh tiến độ hoặc "03/11" | Có nhãn kênh, chưa có tiến độ; bố cục 16:9 co vào khổ dọc |
| Giao diện hợp nội dung: pastel phẳng cho kỹ năng sống; nền tối dữ liệu cho tin công nghệ | Một giao diện neon tối cho mọi nội dung |

## 2. Hướng giải quyết

Dựng video ngắn trên **cơ chế nhịp của Vox** (`nhip: <cụm từ> | <vật> | <ô> | <tuỳ chọn>`), vì nó đã làm đúng việc "vật hiện khi giọng đọc tới cụm từ". Thêm bộ giao diện, bố cục khổ dọc riêng và các vật mới; không bắt buộc ảnh AI (nhanh, không tốn tiền), vẫn cho dùng `anh` khi cần.

### 2.1 Khoá đầu

```
phong-cach: ngan
giao-dien: phang-sang | toi-du-lieu
```

- `giao-dien` AI chọn theo nội dung (`docs/vi/tro-ly/video-ngan.md` có bảng chọn): kỹ năng sống, giao tiếp, giáo dục, mẹo học, chuyện đời thường → `phang-sang`; tin công nghệ, số liệu, khoa học, bí ẩn, sự kiện → `toi-du-lieu`. Không ghi thì `phang-sang`.
- Kịch bản `ngan` cũ (không có `nhip`) báo lỗi `parse` chỉ cách viết mới; xưởng Zalo chỉ sinh kịch bản mới.

### 2.2 Hai bộ giao diện

| | `phang-sang` | `toi-du-lieu` |
|---|---|---|
| Nền | màu pastel trơn, đổi màu mỗi cảnh (kem, hồng nhạt, xanh mint, xanh nhạt, vàng nhạt), bóng sàn nhẹ dưới người que | gần đen `#121212`, hạt nhiễu rất nhẹ |
| Nhãn tiêu đề | chữ hoa đậm màu đậm trong khung trắng bo góc viền màu | chữ trắng đậm, không khung, từ khoá màu nhấn |
| Màu nhấn | đỏ gạch, xanh rêu, cam (theo cảnh) | cam `#E8704A` (một màu) |
| Thẻ, tin nhắn | trắng, bóng mềm | xám than `#1E1E1E`, viền mảnh |
| Phụ đề | chữ đen đậm trên viên trắng bo tròn, từ khoá tô vàng | chữ trắng đậm không nền, từ đang đọc màu nhấn |
| Font | Be Vietnam Pro ExtraBold / Regular (đã có) | như trái |
| Tiến độ | dải màu mảnh trên cùng | dải màu nhấn + "03/11" góc trái |

Phụ đề Phudu vàng viền đen (vi.21) bỏ khỏi `ngan`; giữ trong mã để dùng lại nếu cần.

### 2.3 Bố cục khổ dọc cố định (720×1280 điểm CSS)

- Dải tiến độ: y 0–6.
- Nhãn chương tuỳ chọn (`chuong: 1 · VÍ DỤ`): y 40.
- **Nhãn tiêu đề** (`tieu-de` của cảnh, ≤ 40 ký tự, 1–2 dòng): y 70–230.
- **Vùng hình chính**: y 260–960, ô `giua` (cả vùng), `tren`/`duoi` (nửa trên, nửa dưới), `trai`/`phai` (hai cột).
- Phụ đề: tâm y ≈ 1060, một dòng, ≤ 22 ký tự.
- Đáy 1130–1280 để trống cho thanh nút của TikTok/Reels.

### 2.4 Vật

Giữ của Vox: `anh`, `the`, `chu`, `nhan`, `dau`, `mui-ten`, `so`, `cot`, `chu-trinh`, `moc`, `thap`.

Thêm:

| Vật | Nội dung | Hiện ra |
|---|---|---|
| `nguoi` | người que: `<tư thế>` hoặc `<tư thế> + <đồ vật>`; tư thế lấy từ bộ `nhan-vat.js` đã có (`dung`, `chi-tay`, `suy-nghi`, `an-mung`, `buon`…), đồ vật là biểu tượng tabler. Nhịp sau ghi `nguoi` cùng ô thì **đổi tư thế** thay vì thêm người | trượt vào, đổi tư thế mượt |
| `nhom` | 2–4 người que đứng cạnh nhau, ví dụ `chi-tay; dung; suy-nghi` | lần lượt |
| `bieu-tuong` | biểu tượng tabler lớn có màu (bóng đèn, kính lúp, đồng hồ, bia bắn) | phóng nhẹ từ 0,9 lên 1 |
| `luoi-cham` | `<số chấm sáng>/<tổng> \| <chú thích>`, tổng ≤ 200, ví dụ `68/100 \| học sinh thức sau 23 giờ` | chấm sáng dần theo hàng |
| `truoc-sau` | `<số trước> -> <số sau> \| <nhãn trước> \| <nhãn sau>` | số trước hiện, mũi tên vẽ, số sau chạy |
| `tin-nhan` | 1–3 bong bóng `nguoi: …` / `minh: …`, tuỳ chọn `dien-thoai` đặt trong khung điện thoại | từng bong bóng bật lên |
| `thong-bao` | `<ứng dụng> \| <tiêu đề> \| <nội dung>`, thẻ thông báo trên màn hình khoá | trượt từ trên xuống |
| `trich-dan` | `"<câu>" \| <người nói>` | chữ hiện từng từ |

Mỗi vật có giới hạn ký tự như Vox; kiểm bằng Chromium (không tràn ô) như các phong cách khác.

### 2.4b Nhân vật (đã duyệt 2026-10-19: kiểu "minh hoạ phẳng" B)

- Vẽ trên bộ khớp của người que (`THI_NHAN_VAT.dang`), nên 10 tư thế và cách đổi tư thế dùng chung; file `runtime/nhan-vat-phang.js`.
- **Ghép từ bộ phận**, không cố định theo vai: giới (`nam`/`nu`), tóc (`ngan`, `re-ngoi`, `dai`, `duoi-ngua`, `bui`, `troc`), màu tóc, da (`sang`, `vua`, `ngam`), áo (`so-mi`, `so-mi-dai`, `ao-thun`, `hoodie`, `blouse`, `ao-dai`, `ao-ba-ba`, `vest`, `tap-de`, `dong-phuc`, `the-thao`) + màu, dưới (`quan`, `quan-short`, `vay`) + màu, mũ (`mu-bao-ho`, `ke-pi`, `non-la`, `mu-dau-bep`, `luoi-trai`, `bao-hiem`), phụ kiện (`kinh`, `ca-vat`, `khan-do`, `ong-nghe`, `phu-hieu`, `cap-sach`).
- 13 vai làm sẵn là tổ hợp đặt tên (học sinh nam/nữ, thầy giáo, cô giáo áo dài, bác sĩ, nhà khoa học, kỹ sư, văn phòng, bạn trẻ nam/nữ, phụ huynh, ông, bà).
- **AI tự dựng dàn nhân vật theo nội dung** ở khoá đầu, mỗi dòng một nhân vật:
  ```
  nhan-vat: cong-an = nam, tóc ngan, áo so-mi-dai #3D5A2A, dưới quan #3D5A2A, mũ ke-pi, phụ phu-hieu
  nhan-vat: be-an = hoc-sinh-nam
  ```
  Vế phải là tên vai làm sẵn hoặc danh sách bộ phận. Cảnh gọi `nguoi: cong-an chi-tay`. Không ghép được (bộ phận chưa có) thì chọn bộ phận gần nhất và màu hợp vai; vẫn không đạt thì dùng `anh: ve:` cho riêng vai đó.
- Một nhân vật giữ nguyên trang phục suốt video; hai nhân vật cùng cảnh khác màu áo.

### 2.5 Nhịp và độ dày

- Quy tắc cho AI: mỗi cảnh 3–6 nhịp, khoảng cách giữa hai nhịp ≤ 2,5 giây lời đọc; cảnh đầu có nhịp `@dau`.
- `parse` cảnh báo (không chặn) khi một cảnh có khoảng hơn 4 giây không có nhịp mới.
- Mỗi cảnh một hình chính (một vật lớn ở `giua`, hoặc người que + vật phụ).

### 2.6 Chuyển cảnh, chuyển động

- Chuyển cảnh: nền đổi màu trượt ngang 0,35 giây (`phang-sang`), mờ chéo 0,3 giây (`toi-du-lieu`).
- Không rung, không nảy (sở thích của anh): mọi vật vào bằng trượt hoặc mờ dần, đường cong êm.
- Máy quay đứng yên.

## 3. Phạm vi thay đổi

- `tools/vi/video_ma_parts/vox.py`, `parse.py`: nhận `phong-cach: ngan` theo ngữ pháp nhịp, khoá `giao-dien`, `chuong`, các vật mới, bố cục khổ dọc riêng của `ngan`.
- `runtime/vox.js` (hoặc tách `runtime/ngan.js`): dựng vật mới, giao diện, dải tiến độ.
- `runtime/ngan.css`: viết lại thành hai bộ giao diện.
- `karaoke.py`: kiểu phụ đề theo giao diện.
- `docs/vi/tro-ly/video-ngan.md`: viết lại cho AI (bảng chọn giao diện, vật, công thức, ví dụ đầy đủ), cập nhật `video-hap-dan.md`.
- Plugin `2anh-zalo-bot`: `validate.check_video` nhận ngữ pháp mới cho `ngan`; bản duyệt kịch bản (`script_view`) hiện nhịp dạng "🖼 người que chỉ tay → bóng đèn → …".
- Không đổi: `viet-tay`, `cat-dan`, `vox`.

## 4. Kiểm thử

- Test parse cho từng vật mới (hợp lệ, vượt giới hạn, ô sai), cho `giao-dien`, cho kịch bản `ngan` kiểu cũ (lỗi có hướng dẫn).
- Test JS: vật mới dựng đúng ô, chuyển tư thế người que, lưới chấm đếm đúng số chấm, tiến độ.
- Test Chromium: chữ dài nhất mỗi vật không tràn ô ở cả hai giao diện.
- Dựng thật 2 video mẫu (một `phang-sang`, một `toi-du-lieu`) bằng kịch bản AI viết qua xưởng, gửi anh xem trước khi phát hành.

## 5. Thứ tự làm

1. Bộ khung: khoá đầu, bố cục, hai giao diện, tiến độ, phụ đề; dùng lại vật Vox → dựng **một cảnh mẫu mỗi giao diện**, gửi anh duyệt nhìn.
2. Vật mới: `nguoi`/`nhom`, `bieu-tuong`, `luoi-cham`, `truoc-sau`, `tin-nhan`, `thong-bao`, `trich-dan`.
3. Hướng dẫn AI + plugin; dựng 2 video mẫu đầy đủ.
4. Phát hành studio + plugin, cài hai bot.

# Chọn giọng đọc cho video (`giong:`)

File dành cho AI viết `video.md` (mọi phong cách: `viet-tay`, `cat-dan`, `vox`, `ngan`). **Không mặc định một giọng cho mọi video.** Đọc chủ đề, người xem và không khí của kịch bản rồi chọn giọng hợp nhất, ghi vào khối thông tin đầu (`giong: <khoá>`). Người dùng đã nói rõ giọng (nam/nữ, tên giọng, miền) thì theo người dùng.

## Danh mục

Giọng VieNeu đọc trên máy, tự nhiên, không cần mạng. Máy không có VieNeu thì công cụ tự lùi về giọng edge-tts cùng giới và báo trong `warnings`, nên vẫn cứ chọn giọng VieNeu hợp nội dung.

| Khoá | Giọng | Giới · miền | Chất giọng |
|---|---|---|---|
| `thu-giang` | Thu Giang | Nữ · Bắc | MC dẫn chương trình, rõ, tươi |
| `ngoc-huyen` | Ngọc Huyền | Nữ · Bắc | tự nhiên |
| `truc-ly` | Trúc Ly | Nữ · Bắc | tự nhiên |
| `doan-trang` | Đoan Trang | Nữ · Bắc | tự nhiên |
| `ngoc-linh` | Ngọc Linh | Nữ · Bắc | kể chuyện |
| `mai-anh` | Mai Anh | Nữ · Bắc | tin tức |
| `quynh-anh` | Quỳnh Anh | Nữ · Bắc | đọc truyện |
| `ngoc-tran` | Ngọc Trân | Nữ · Trung | tự nhiên |
| `thuc-doan` | Thục Đoan | Nữ · Nam | kể chuyện |
| `thuy-dung` | Thùy Dung | Nữ · Nam | tin tức |
| `my-duyen` | Mỹ Duyên | Nữ · Nam | đọc truyện |
| `kim-thanh` | Kim Thanh | Nữ · Nam | đọc truyện |
| `pham-tuyen` | Phạm Tuyên | Nam · Bắc | tự nhiên |
| `xuan-vinh` | Xuân Vĩnh | Nam · Bắc | tự nhiên |
| `manh-dung` | Mạnh Dũng | Nam · Bắc | tự nhiên |
| `minh-quan` | Minh Quân | Nam · Bắc | tự nhiên |
| `minh-duc` | Minh Đức | Nam · Bắc | tin tức |
| `thanh-binh` | Thanh Bình | Nam · Bắc | kể chuyện |
| `anh-khoi` | Anh Khôi | Nam · Bắc | kể chuyện |
| `quang-son` | Quang Sơn | Nam · Trung | tự nhiên |
| `thai-son` | Thái Sơn | Nam · Nam | kể chuyện |
| `minh-triet` | Minh Triết | Nam · Nam | tin tức |
| `duc-tri` | Đức Trí | Nam · Nam | đọc truyện |
| `adam` | Adam | Nam · Nam | tự nhiên |

Giọng edge-tts (cần mạng): `nu` (nữ, trung tính), `nam` (nam, trung tính), `nu-tuoi` (nữ, cao và nhanh hơn chút — trẻ, vui), `nam-tram` (nam, trầm và chậm hơn chút — nghiêm, sâu).

## Chọn theo nội dung

| Nội dung, không khí | Nên chọn |
|---|---|
| Giải thích kiến thức cho học sinh, mẹo học, video ngắn vui | nữ tự nhiên (`ngoc-huyen`, `truc-ly`, `doan-trang`) hoặc MC `thu-giang`; nam trẻ thì `minh-quan`, `manh-dung` |
| Tin nhanh, thời sự, số liệu, thông báo của trường | giọng tin tức: `mai-anh`, `minh-duc` (Bắc), `thuy-dung`, `minh-triet` (Nam) |
| Kể chuyện lịch sử, nhân vật, hành trình khám phá, bí ẩn khoa học | giọng kể chuyện: `thanh-binh`, `anh-khoi`, `ngoc-linh` (Bắc), `thai-son`, `thuc-doan` (Nam) |
| Văn học, đọc thơ, tóm tắt truyện, cảm xúc nhẹ nhàng | giọng đọc truyện: `quynh-anh`, `my-duyen`, `kim-thanh`, `duc-tri` |
| Chủ đề nghiêm túc: an toàn, sức khoẻ, cảnh báo, tài liệu | `minh-duc`, `pham-tuyen`, hoặc `nam-tram` |
| Người xem ở miền Nam hoặc miền Trung (người dùng nói rõ) | giọng cùng miền trong bảng |
| Video có nhân vật chính là nam/nữ, hoặc người dẫn xưng "anh"/"chị"/"thầy"/"cô" | giọng cùng giới với người dẫn |

Thêm:

- Một **loạt** video (`loat` giống nhau) giữ cùng một giọng để khán giả nhận ra kênh.
- `toc-do` đi cùng giọng: video ngắn, mẹo, tin nhanh → `nhanh`; giải thích cho học sinh nhỏ, đọc thơ, kể chuyện cảm xúc → `vua` hoặc `cham`.
- Khi viết kịch bản để người dùng duyệt, tên giọng hiện trong bản duyệt; người dùng muốn đổi giọng thì đổi đúng khoá `giong`.

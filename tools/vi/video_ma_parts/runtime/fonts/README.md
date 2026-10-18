# Fonts

Itim (đóng gói cho khung hình và phụ đề đốt), tác giả Cadson Demak, giấy phép SIL Open Font License 1.1 (xem `OFL.txt`), nguồn: https://github.com/google/fonts/tree/main/ofl/itim

Be Vietnam Pro (phong cách `cat-dan`), tác giả Lâm Bảo, Tony Le, ViệtAnh Nguyễn (The Be Vietnam Pro Project Authors), giấy phép SIL Open Font License 1.1 (xem `OFL-BeVietnamPro.txt`). Tải một lần từ kho `google/fonts`, thư mục `ofl/bevietnampro/`, commit cố định `c13390277dfb1fcc7415d84ef7ef9cfc1e52f8c1` (2026-03-03), qua `https://raw.githubusercontent.com/google/fonts/c13390277dfb1fcc7415d84ef7ef9cfc1e52f8c1/ofl/bevietnampro/<tên file>`. Phiên bản font (bảng `name`, mục 5): `Version 1.002; ttfautohint (v1.8.3)`.

| File | Độ đậm | SHA-256 |
|---|---|---|
| `BeVietnamPro-Regular.ttf` | 400 | `cd1ef6e9d7db28ad5cdb88a65ccbe693870e60d340b791f349d248342b4fe4c3` |
| `BeVietnamPro-ExtraBold.ttf` | 800 | `44dbfa01553d227bec76ba6446c5618870a76a4a3297f41630dde859d0650d02` |
| `OFL-BeVietnamPro.txt` (`OFL.txt` của thư mục trên) | — | `6b7f8f73609a25ea78c891e34cf37b06f8a676b7ea986e941e43b009110f2a85` |

Trang dựng nhúng font dưới dạng `data:` (base64), không tải gì từ mạng.

Phudu (phụ đề video ngắn `phong-cach: ngan`), tác giả Dương Trần (The Phudu Project Authors), giấy phép SIL Open Font License 1.1 (xem `OFL-Phudu.txt`). Tải từ kho `google/fonts`, `ofl/phudu/Phudu[wght].ttf` (font biến thiên 300–900), cắt bản tĩnh độ đậm 800 bằng `fontTools.varLib.instancer` (`updateFontNames=True`, họ font "Phudu ExtraBold").

| File | Độ đậm |
|---|---|
| `Phudu-ExtraBold.ttf` | 800 |
| `OFL-Phudu.txt` (`OFL.txt` của thư mục trên) | — |

Baloo 2 và Lobster (từ khoá trong phụ đề video ngắn `phong-cach: ngan`), giấy phép SIL Open Font License 1.1 (`OFL-Baloo2.txt`, `OFL-Lobster.txt`), tải từ kho `google/fonts` (`ofl/baloo2/Baloo2[wght].ttf` cắt bản tĩnh độ đậm 800 bằng `fontTools.varLib.instancer`, họ "Baloo 2 ExtraBold"; `ofl/lobster/Lobster-Regular.ttf`). Cả hai đủ dấu tiếng Việt.

| File | Dùng cho |
|---|---|
| `Baloo2-ExtraBold.ttf` | từ khoá tô nền `==…==`, số `{{…}}` |
| `Lobster-Regular.ttf` | từ khoá nhấn kiểu chữ viết `**…**` (xen kẽ với Phudu) |

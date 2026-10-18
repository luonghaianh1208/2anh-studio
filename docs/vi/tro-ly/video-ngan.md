# Video ngắn mạng xã hội (`phong-cach: ngan`)

File dành cho AI viết `video.md`. Đọc cùng `docs/vi/tro-ly/video-hap-dan.md` (hook, nhịp, đa dạng cảnh), `docs/vi/tro-ly/chon-giong.md` (chọn giọng theo nội dung), `docs/vi/tham-khao/video-viet-tay.md` (khối thông tin đầu, giọng, phụ đề) và `docs/vi/tham-khao/canh-video.md` (danh mục loại cảnh, trường, giới hạn chữ, nhấn ý). Phong cách `ngan` dùng đúng các loại cảnh, trường và giới hạn của `cat-dan`; chỉ khác "da": nền neon tối có lưới và quầng sáng, nhãn tiêu đề trên dải màu neon (cyan, hồng, vàng chanh, tím theo số cảnh), thẻ thông tin kiểu kính tối viền sáng, chữ trắng phát sáng. Không ghi `kho` thì khổ dọc 9:16 (TikTok, Reels, Shorts); không ghi `chuyen-canh` thì trượt nhanh; không có bàn tay.

Ba công thức dưới đây gộp cách làm của ba mẫu video ngắn tiếng Việt hay được dùng: giải thích kiến thức (hook → vấn đề → giải pháp → kêu gọi), so sánh hai khái niệm dễ nhầm, và tin nhanh từ một bài báo.

## Khối thông tin đầu

```
---
tieu-de: <tên video, cũng là tiêu đề tệp>
mon: <môn hoặc chủ đề>
lop: <lớp, hoặc "Mọi người">
phong-cach: ngan
loat: <tên kênh hoặc tên loạt, tối đa 30 ký tự — hiện ở góc trái trên như nhãn kênh>
toc-do: nhanh
giong: <khoá giọng chọn theo chon-giong.md>
---
```

- `loat` là nhãn kênh (ví dụ `2ANH AI · HOÁ 11`); người dùng không nói tên kênh thì để tên chủ đề ngắn.
- `toc-do: nhanh` hợp video ngắn; thầy cô muốn đọc chậm cho học sinh nhỏ thì `vua`.
- `giong`: chọn theo nội dung và người xem như `chon-giong.md` — không mặc định một giọng. Ví dụ: mẹo học → `ngoc-huyen`/`thu-giang`; tin nhanh → `mai-anh`/`minh-duc`; chuyện bí ẩn → `thanh-binh`.

## Nhịp chung

- Tổng 30–60 giây, 4–7 cảnh. Mỗi cảnh 1–3 câu lời, mỗi câu tối đa khoảng 14 từ: phụ đề hiện từng dòng ngắn, câu dài bị tách và đọc vội.
- Cảnh 1 là **hook**: câu hỏi gây tò mò hoặc một sự thật bất ngờ, lời đọc xong trong khoảng 3 giây đầu.
- Không có hai cảnh liền nhau cùng `loai`; mỗi cảnh có biểu tượng `hinh`, thẻ số `the` hoặc sơ đồ để nhìn (xem `video-hap-dan.md`).
- Mỗi cảnh nhấn **một** ý bằng `==…==` hoặc `((…))`; con số cần nhớ viết `{{số}}`.
- Cảnh cuối luôn là **kêu gọi**: `loai: tieu-de`, `chu` kiểu "Theo dõi để học tiếp", `phu` nói kênh học gì; lời mời theo dõi, thả tim, lưu video.
- Không chèn địa chỉ web vào bất kỳ trường nào; nguồn ghi ở `tai-lieu` (tên báo, ngày).

## Công thức 1 — Giải thích ngắn

Hợp với một khái niệm, một hiện tượng, một công cụ.

| Cảnh | Loại | Nội dung |
|---|---|---|
| 1 Hook | `tieu-de` | `chu`: câu hỏi tò mò ≤ 40 ký tự; `phu`: lời hứa ("Hiểu trong 45 giây") |
| 2 Vấn đề | `y-tung-y` hoặc `khai-niem` | nỗi khó / hiểu lầm hay gặp, 2–3 ý |
| 3 Giải pháp | `khai-niem` | `thuat-ngu` + `dinh-nghia` ngắn; thêm `the` nếu có một con số đắt giá |
| 4 Cách làm | `quy-trinh` | 3 bước, mỗi bước ≤ 6 từ |
| 5 Lợi ích | `y-tung-y` | 3 ý, mỗi ý bắt đầu bằng động từ |
| 6 Kết | `tieu-de` | kêu gọi |

## Công thức 2 — So sánh A và B

Hợp với cặp khái niệm hay nhầm (axit/bazơ, oxi hoá/khử, thiên thạch/sao băng, Dev/DevOps). Một loạt video giữ cùng nhịp, chỉ đổi nội dung.

| Cảnh | Loại | Nội dung |
|---|---|---|
| 1 Hook | `tieu-de` | `chu`: "A hay ((B))?"; `phu`: "Phân biệt trong 30 giây" |
| 2 So sánh | `so-sanh` | `trai`: A, `phai`: B; 3 dòng `y-trai` và 3 dòng `y-phai` **cùng tiêu chí, cùng thứ tự** (định nghĩa, dấu hiệu nhận biết, ví dụ) |
| 3 Mẹo nhớ | `khai-niem` | một câu mẹo phân biệt; `the` nếu có ngưỡng số (`pH | {{7}} | trung tính`) |
| 4 Kiểm tra nhanh | `cau-hoi` | một câu hỏi 2–3 lựa chọn, `cho: 4` |
| 5 Kết | `tieu-de` | kêu gọi ("Cặp tiếp theo: …?") |

Muốn có người dẫn: thêm `nhan-vat: nguoi-que` ở khối đầu và `tu-the` (`chi-tay`, `suy-nghi`, `an-mung`…) ở cảnh `tieu-de`, `khai-niem`, `y-tung-y` (cảnh có `tu-the` không có `hinh`).

## Công thức 3 — Tin nhanh từ một bài báo

Người dùng gửi link bài báo hoặc dán nội dung: đọc kỹ bài, chỉ dùng thông tin và con số **có trong bài**, không thêm, không đoán.

| Cảnh | Loại | Nội dung |
|---|---|---|
| 1 Tin nóng | `tieu-de` | `chu`: tiêu đề tin rút gọn ≤ 50 ký tự; `phu`: "Tin nhanh · <ngày đăng>" |
| 2 Con số | `khai-niem` (hoặc `bieu-do` nếu bài có 2–5 số liệu so sánh) | `thuat-ngu`: điều được đo; `the: <nhãn> | {{số}} | <đơn vị/so với>` |
| 3 Điểm chính | `y-tung-y` | 3–4 điểm, mỗi điểm ≤ 8 từ |
| 4 Trích dẫn | `khai-niem` | `thuat-ngu`: người phát biểu; `dinh-nghia`: câu trích ngắn trong ngoặc kép |
| 5 Ý nghĩa | `khai-niem` | tin này ảnh hưởng gì tới người xem (học sinh, thầy cô, phụ huynh) |
| 6 Kết | `tieu-de` | kêu gọi; `tai-lieu`: tên báo, ngày đăng |

Bài dài thì chọn ý quan trọng nhất; bài có nhiều mốc thời gian thì thay cảnh 3 bằng `dong-thoi-gian`.

## Ví dụ

```
---
tieu-de: Axit và bazơ khác nhau thế nào
mon: Hoá học
lop: 11
phong-cach: ngan
loat: 2ANH AI · HOÁ 11
toc-do: nhanh
giong: ngoc-huyen
---

## Cảnh 1
loai: tieu-de
chu: Axit hay ((bazơ))?
phu: Phân biệt trong 30 giây
hinh: flask
loi: Chanh chua, xà phòng trơn. Một bên là axit, một bên là bazơ. Phân biệt thế nào cho đúng?

## Cảnh 2
loai: so-sanh
tieu-de: Axit và bazơ
trai: Axit
phai: Bazơ
y-trai: Vị ==chua==
y-trai: Quỳ tím hoá đỏ
y-trai: pH nhỏ hơn 7
y-phai: Vị chát, nhờn
y-phai: Quỳ tím hoá xanh
y-phai: pH lớn hơn 7
loi: Axit có vị chua, làm quỳ tím hoá đỏ, pH nhỏ hơn bảy. Bazơ thì chát và nhờn, làm quỳ hoá xanh, pH lớn hơn bảy.

## Cảnh 3
loai: khai-niem
thuat-ngu: Phản ứng ==trung hoà==
dinh-nghia: Axit gặp bazơ tạo ra muối và nước.
the: pH trung tính | {{7}} | nước nguyên chất
loi: Khi axit gặp bazơ, chúng trung hoà nhau, tạo ra muối và nước, pH tiến về bảy.

## Cảnh 4
loai: tieu-de
chu: Theo dõi để học tiếp
phu: Hoá 11 mỗi ngày một phút
loi: Theo dõi kênh để học Hoá mỗi ngày một phút nhé!
```

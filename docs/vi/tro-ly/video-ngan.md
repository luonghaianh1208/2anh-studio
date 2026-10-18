# Video ngắn "nhịp hình" (`phong-cach: ngan`)

File dành cho AI viết `video.md` cho video ngắn mạng xã hội (TikTok, Reels, Shorts), khổ dọc 9:16. Đọc cùng `video-hap-dan.md` (hook, nhịp, kết) và `chon-giong.md` (chọn giọng). Ngữ pháp ở đây **khác** viết tay/cắt dán: không có `loai`, không có `bo-cuc`; mỗi cảnh là lời đọc + các dòng `nhip`, mỗi nhịp làm hình thay đổi đúng lúc giọng đọc tới một cụm từ.

Nguyên tắc vàng (học từ các kênh triệu lượt xem): **hình đổi theo từng cụm lời, 1–2 giây một lần**; mỗi màn có **một hình chính** to, rõ; chữ trên hình ít, lời đọc kể chuyện.

## Khối thông tin đầu

```
---
tieu-de: <tên video>
phong-cach: ngan
giao-dien: phang-sang
loat: <tên kênh, ≤ 30 ký tự>
giong: <khoá giọng theo chon-giong.md>
toc-do: nhanh
vai: an = hoc-sinh-nam; linh = hoc-sinh-nu, ao so-mi hong
---
```

- Chỉ `tieu-de` bắt buộc. Khổ luôn dọc (không ghi `kho`).
- `giao-dien` — chọn theo nội dung:

| Giao diện | Hợp với | Nhìn |
|---|---|---|
| `phang-sang` | kỹ năng sống, giao tiếp, giáo dục, mẹo học, chuyện đời thường, tình huống có người | nền pastel đổi màu theo cảnh, nhân vật minh hoạ, nhãn tiêu đề trong khung trắng, phụ đề chữ đen trên viên trắng |
| `toi-du-lieu` | tin công nghệ, số liệu, khoa học, bí ẩn, sự kiện, so sánh trước/sau | nền gần đen, một màu nhấn cam, số khổng lồ, lưới chấm, thẻ thông báo, phụ đề chữ trắng |

- `vai` — dàn nhân vật của video (bỏ được nếu chỉ dùng vai làm sẵn). Mỗi vai `<tên> = <mô tả>`, cách nhau bằng `;`. Tên viết thường không dấu, nối `-`.

### Nhân vật: tự nghĩ ra đúng vai nội dung cần

Nội dung có ai thì dựng người đó — công an, đầu bếp, nông dân, vận động viên, ông bà, bác sĩ… Không có sẵn thì **ghép từ bộ phận**:

| Bộ phận | Viết | Lựa chọn |
|---|---|---|
| giới | `nam` hoặc `nu` | (nữ mặc định tóc dài) |
| tóc | `toc <kiểu> [màu]` | kiểu: `ngan`, `re-ngoi`, `dai`, `duoi-ngua`, `bui`, `troc`; màu: `den`, `nau`, `bac`, `vang` |
| da | `da <màu>` | `sang`, `vua`, `ngam` |
| áo | `ao <kiểu> [màu]` | `so-mi`, `so-mi-dai`, `ao-thun`, `hoodie`, `blouse`, `ao-dai`, `ao-ba-ba`, `vest`, `tap-de`, `dong-phuc`, `the-thao` |
| dưới | `duoi <kiểu> [màu]` | `quan`, `quan-short`, `vay` |
| mũ | `mu <kiểu>` | `mu-bao-ho`, `ke-pi`, `non-la`, `mu-dau-bep`, `luoi-trai`, `bao-hiem` |
| phụ kiện | `phu <a> <b> …` | `kinh`, `ca-vat`, `khan-do`, `ong-nghe`, `phu-hieu`, `cap-sach` |

Màu: `do`, `cam`, `vang`, `xanh-la`, `xanh-reu`, `xanh-duong`, `xanh-nhat`, `xanh-than`, `tim`, `hong`, `nau`, `be`, `xam`, `den`, `trang` hoặc mã `#RRGGBB`.

13 vai làm sẵn (gọi thẳng tên, hoặc lấy làm gốc rồi đổi vài bộ phận): `hoc-sinh-nam`, `hoc-sinh-nu`, `thay-giao`, `co-giao` (áo dài), `bac-si`, `nha-khoa-hoc`, `ky-su`, `van-phong-nu`, `ban-tre`, `ban-tre-nu`, `phu-huynh-nu`, `ong`, `ba`.

Ví dụ ghép: `cong-an = nam, toc ngan, ao dong-phuc xanh-reu, duoi quan xanh-reu, mu ke-pi, phu phu-hieu` · `dau-bep = nu, toc bui, ao tap-de, duoi quan den, mu mu-dau-bep` · `nong-dan = nam, da ngam, ao ao-ba-ba nau, duoi quan den, mu non-la` · `vdv = nu, toc duoi-ngua, ao the-thao do, duoi quan-short den`. Hai nhân vật cùng cảnh thì khác màu áo. Một nhân vật giữ nguyên trang phục cả video.

## Cảnh

```
## Cảnh 1
tieu-de: <nhãn tiêu đề ≤ 40 ký tự>
chuong: <nhãn chương ≤ 20 ký tự, ví dụ "1 · VÍ DỤ">
loi: <lời đọc, có dấu nhấn từ khoá và gợi ý ngắt dòng>
nhip: <cụm từ trong lời> | <vật>: <nội dung> | <ô> | <tuỳ chọn>
```

- `tieu-de`, `chuong`, `nguon` (nguồn số liệu, không hiện trên hình), `giu` (giây giữ hình sau lời, 0,5–3) đều bỏ được.
- **3–6 nhịp mỗi cảnh** (tối đa 8), hai nhịp cách nhau không quá ~2,5 giây lời đọc; nhịp đầu là `@dau` (hiện ngay khi vào cảnh).
- `<cụm từ>` chép đúng vài từ liền nhau trong `loi` (bỏ qua dấu nhấn, chữ hoa); các nhịp theo đúng thứ tự lời.

### Vật

| Vật | Nội dung | Giới hạn |
|---|---|---|
| `nguoi` | `<vai> <tư thế>` — vai trong `vai:` hoặc vai làm sẵn. Gọi lại cùng vai ở nhịp sau = **đổi tư thế** (không thêm người) | tư thế: `dung`, `chao`, `chi-tay`, `giai-thich`, `suy-nghi`, `ngac-nhien`, `vo-dau`, `dung-lai`, `an-mung`, `buon` |
| `nhom` | 2–4 người cách nhau `;`: `nhom: an dung; linh chao; binh giai-thich` | |
| `bieu-tuong` | `<tên biểu tượng tabler> \| <nhãn>` (tên tiếng Anh như mục "Bảng tra biểu tượng" của canh-video.md: `bulb`, `alarm`, `heart`, `flask`…) | nhãn ≤ 24 |
| `so` | số chạy `{{số}}` kèm chữ: `so: {{30}} mét` | 24 |
| `luoi-cham` | `<số sáng>/<tổng> \| <chú thích>`: `luoi-cham: 7/10 \| bạn sẽ thông cảm` | tổng ≤ 200, chú thích ≤ 50 |
| `truoc-sau` | `<trước> -> <sau> \| <nhãn trước> \| <nhãn sau>`: `truoc-sau: 80,4% -> 71,8% \| đủ suy luận \| bản tóm tắt` | giá trị ≤ 12, nhãn ≤ 20 |
| `tin-nhan` | 1–3 tin `ban: …` (người kia, trái) / `minh: …` (phải), cách nhau `;`; tuỳ chọn `dien-thoai` đặt trong khung điện thoại | mỗi tin ≤ 70 |
| `thong-bao` | `<ứng dụng> \| <tiêu đề> \| <nội dung>` (thẻ thông báo màn hình khoá) | 16 / 40 / 70 |
| `trich-dan` | `"<câu>" \| <người nói>` | 120 / 40 |
| `chu` | một câu chốt lớn | 40 |
| `the` | `<nhãn> \| <giá trị> \| <chú thích>` | 24 / 16 / 60 |
| `nhan`, `dau` | nhãn màu / con dấu | 30 / 16 |
| `cot` | biểu đồ cột `2022 = 12; 2024 = 45%` (2–5 cột) | như Vox |
| `moc`, `chu-trinh`, `thap` | dòng thời gian / các bước / tháp, mục cách nhau `;` | như Vox |

Không có `anh` ở video ngắn.

### Ô và cách xếp

- Bỏ trống ô (cách thường dùng): vật vào **ô chính** — cả sân khấu khi cảnh không có nhân vật, phần trên sân khấu khi có nhân vật (nhân vật luôn đứng ở sàn phía dưới). **Vật mới vào ô chính thay vật trước** (vật cũ mờ đi): nhờ đó mỗi nhịp là một hình chính mới.
- Muốn hai vật cùng hiện: ghi ô `tren`, `duoi`, `trai`, `phai` (vật sau cùng ô mới thay vật trước ở ô đó).
- Nhân vật tự xếp theo số vai trong cảnh (1 người giữa, 2 người hai bên…); `nguoi: … | trai` để chọn chỗ.

## Phụ đề: từ khoá và ngắt dòng

Phụ đề hiện mỗi lúc một dòng, căn giữa. Trong `loi`, đánh dấu **1–2 từ khoá mỗi câu** để phụ đề nổi bật (giọng đọc bỏ qua các dấu này):

| Viết trong lời | Phụ đề hiện | Dùng cho |
|---|---|---|
| `==nhờ vả==` | tô nền vàng, font tròn | từ khoá chính của câu |
| `((lực hút))` | khoanh vòng vẽ tay | khái niệm, thứ cần chú ý |
| `__lựa chọn khác__` | gạch chân | giải pháp, kết luận |
| `**không dám**` | chữ to, khác font, màu nhấn | cảm xúc, phủ định, cú twist |
| `{{30}}` | số to | con số |

Đổi kiểu nhấn giữa các câu cho đa dạng. Cụm nhấn 1–3 từ.

**Ngắt dòng**: mỗi dòng phụ đề ≤ 26 ký tự. Câu dài hơn thì chèn ` / ` (dấu gạch chéo có khoảng trắng hai bên) vào chỗ ngắt tự nhiên — giữa hai cụm nghĩa, **không bao giờ giữa một từ ghép** ("lực / hút" sai, "có / lực hút" đúng). Dấu này không được đọc.

## Ba công thức

1. **Tình huống – giải pháp** (`phang-sang`): Cảnh 1 tình huống quen (2 nhân vật, tin nhắn), Cảnh 2 hậu quả/cảm xúc (đổi tư thế, `bieu-tuong`), Cảnh 3 giải pháp (`chuong: 2 · GIẢI PHÁP`, `luoi-cham` hoặc `truoc-sau`), Cảnh 4 kết + kêu gọi.
2. **Giải mã số liệu** (`toi-du-lieu`): hook bằng `so` khổng lồ, `luoi-cham` cho tỉ lệ, `truoc-sau` cho thay đổi, `thong-bao`/`trich-dan` làm bằng chứng, kết bằng câu hỏi cho người xem.
3. **Tin nhanh từ link**: chỉ dùng số và câu trích **có trong bài**; `thong-bao` cho tiêu đề tin, `so`/`cot` cho số liệu, `trich-dan` cho phát biểu, `nguon:` ghi tên báo.

## Ví dụ

```
---
tieu-de: Từ chối khéo khi bị nhờ vả
phong-cach: ngan
giao-dien: phang-sang
loat: KỸ NĂNG SỐNG
giong: ngoc-huyen
toc-do: nhanh
vai: an = hoc-sinh-nam; linh = hoc-sinh-nu, ao so-mi hong
---

## Cảnh 1
tieu-de: Bị nhờ vả
chuong: 1 · VÍ DỤ
loi: Bạn có hay bị bạn bè / ==nhờ vả== liên tục / mà **không dám** từ chối? Ví dụ như / nhờ mua giùm đồ ăn mỗi ngày.
nhip: @dau | nguoi: an dung
nhip: bạn bè nhờ vả | nguoi: linh chi-tay
nhip: không dám từ chối | nguoi: an vo-dau
nhip: nhờ mua giùm | tin-nhan: ban: Ê, mua giùm tớ hộp cơm nha!; minh: Ừm… để tớ xem

## Cảnh 2
tieu-de: Cách nói khéo
chuong: 2 · GIẢI PHÁP
loi: Hãy nói rõ / ((lý do)) của mình, rồi đưa ra / một __lựa chọn khác__. {{7}} trên 10 bạn / sẽ **thông cảm** ngay.
nhip: @dau | nguoi: an giai-thich
nhip: lý do của mình | bieu-tuong: message-circle | Nói rõ lý do
nhip: lựa chọn khác | nguoi: linh suy-nghi
nhip: 7 trên 10 | luoi-cham: 7/10 | bạn sẽ thông cảm
nhip: thông cảm ngay | nguoi: linh an-mung
```

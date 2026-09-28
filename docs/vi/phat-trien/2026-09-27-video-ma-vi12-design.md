# Thiết kế: Video giải thích kiểu kể chuyện, cắt dán và khổ dọc (v6.3.2-vi.12)

Ngày 2026-09-27. Chủ repo đưa 4 video mẫu (Quy tắc 2 phút, Nền kinh tế vận hành, MCP là gì, In tiền gây lạm phát) và bảng "Tài liệu video AI" để học cách làm. Kết quả bóc tách:

- Cả 4 video dùng chung một khuôn: đúng 8 cảnh; tên loạt ở góc trái trên, số cảnh "03/08" ở góc phải trên; tiêu đề cảnh là một kết luận ngắn; phụ đề có khung.
- Ba video dùng một **nhân vật dẫn chuyện** xuyên suốt: mỗi cảnh một tư thế và cảm xúc khớp nội dung, đứng trên **nền tranh vẽ kín khung**.
- Video thứ tư theo kiểu **giấy cắt dán Vox**: tiêu đề dạng băng dính màu, thẻ thông tin ba tầng (nhãn, giá trị lớn, chú thích), dòng tài liệu tham khảo, hình dạng sticker, các lớp hiện ra theo thứ tự.
- Lỗi cần tránh: phụ đề trắng không khung trên nền sáng, công thức bị ngắt dòng giữa chừng, phụ đề hai dòng quá dài.

Chủ repo quyết định:

- Tận dụng công cụ tạo ảnh có sẵn của nền tảng: Antigravity có Nano Banana Pro, ChatGPT Codex có GPT Image. AI dùng công cụ đó để vẽ nền và nhân vật cho từng cảnh.
- Chỉ nền tảng không có công cụ vẽ (Claude Code) mới dùng kho mẫu dựng sẵn.
- Làm luôn khổ dọc 9:16 và kiểu Vox đã hẹn từ vi.11.

Cơ chế ảnh AI đi theo đúng "Path B — host-native" của upstream (`skills/ppt-master/references/image-generator.md` §7):

- AI dùng công cụ vẽ của nền tảng và lưu file vào thư mục dự án.
- Công cụ dựng chỉ đọc file, không gọi AI.

## 1. Tiêu chí thành công

1. **Cảnh kể chuyện:** loại cảnh mới `ke-chuyen` gồm:
   - nền kín khung, lấy từ ảnh AI, kho mẫu hoặc ảnh của thầy cô;
   - nhân vật dẫn chuyện đứng ở một tư thế;
   - tiêu đề lớn, tuỳ chọn thẻ thông tin và dòng tài liệu.
   Dựng ra giống khuôn của video mẫu, và chữ tiếng Việt luôn đúng dấu vì không nằm trong ảnh.
2. **Nhân vật dẫn chuyện:**
   - Hai cách có sẵn:
     - `nguoi-que`: người que vẽ bằng SVG, có sẵn trên mọi nền tảng, đổi được màu áo;
     - `ve:`: nhân vật do AI của nền tảng vẽ theo mô tả.
   - Chung một bộ 10 tư thế.
   - Nhân vật nhún thở, chớp mắt, bật vào cảnh; người que còn cử động tay theo tư thế.
3. **Ảnh AI của nền tảng:**
   - Công cụ mới `tools/vi/anh_ai.py` sinh sẵn câu lệnh vẽ thống nhất cho mọi cảnh: cùng một câu phong cách, có nhân vật tham chiếu, ghi rõ không có chữ.
   - Công cụ đó cũng nhận ảnh AI về: tách nền xanh của nhân vật, cắt về đúng khổ, kiểm độ sạch, ghi nguồn.
   - Trên Antigravity và Codex, AI tự vẽ bằng công cụ của mình. Trên Claude Code, tài liệu hướng AI sang kho mẫu.
4. **Kho mẫu:** 8 nền vẽ bằng mã (SVG theo hạt giống cố định). Không có file ảnh, không vướng giấy phép, dựng được không cần mạng.
5. **Phong cách cắt dán:** `phong-cach: cat-dan` áp cho cả 14 loại cảnh cũ và loại mới:
   - nền giấy, mảng giấy xé, chấm lưới, băng dính;
   - tiêu đề cảnh dạng nhãn băng dính màu xoay vòng;
   - hình và ảnh dạng sticker viền trắng;
   - chữ hiện bằng trượt và mờ dần thay cho bút viết;
   - các lớp hiện theo thứ tự nền → hình chính → chữ và thẻ → dòng tài liệu.
6. **Khung loạt bài:** khoá đầu `loat:` hiện tên loạt ở góc trái trên và "0k/N" ở góc phải trên, đứng yên qua camera và chuyển cảnh.
7. **Khổ dọc 9:16, Full HD:**
   - `kho: doc` xuất video 1080×1920; khổ ngang xuất 1920×1080. Cả hai là Full HD thật (chữ và hình vector được vẽ ở độ phân giải đó, không phóng ảnh).
   - Cả 14 loại cảnh cũ và loại mới đều có bố cục dọc.
   - Mọi loại, ở giới hạn chữ của khổ dọc, không tràn khung và không đè vùng phụ đề.
8. **Tránh lỗi đã thấy:**
   - Phụ đề ở `cat-dan` và `kho: doc` luôn có khung nền.
   - Mỗi phần của công thức không bao giờ bị ngắt dòng giữa chừng.
   - Phụ đề dài quá một dòng khổ dọc thì có cảnh báo.
9. **Tương thích:**
   - Kịch bản vi.9–vi.11 dựng được không cần sửa, và bố cục của `viet-tay` khổ ngang không đổi.
   - Mỗi thứ mới tắt được hoặc là tuỳ chọn.
   - Mọi khung vẫn là hàm xác định của `t`.
   - Thời gian dựng ở Full HD được đo so với 720p trước khi sửa. Mục tiêu: video 5 phút không quá 12 phút trên máy chủ repo. `do-phan-giai: 720` giữ tốc độ cũ cho máy yếu.
10. **Ranh giới:**
    - Không sửa `skills/`, `video.py`, `video_parts/`, `thi_nghiem_parts/`.
    - Không thêm thư viện Python hay JavaScript. Xử lý ảnh bằng FFmpeg, vốn đã bắt buộc khi dựng.
    - Trang dựng không dùng địa chỉ web.
    - `video_ma.py` không gọi mạng hay AI.

## 2. Hiện trạng đã kiểm

- **Khung hình:** khung 1280×720 được ghi cứng ở khoảng 10 file:
  - `chup.py` (VIEWPORT);
  - 6 quy tắc trong `viet-tay.css`;
  - viewBox và vùng kiểm tràn trong `khung-video.js`;
  - `may-quay.js` (RONG, CAO, DAY, TAM);
  - chỗ nghỉ của `ban-tay.js`;
  - hằng số lau bảng 1400.
  14 module cảnh đặt vị trí bằng toạ độ tuyệt đối, ví dụ cột phải x = 900, tiêu đề rộng 1160. Chỉ riêng `karaoke.py` đã nhận tham số kích thước.
- **Phong cách:** `phong-cach` chỉ có một giá trị `viet-tay`. Màu được ghi rải rác trong CSS và `ban-tay.js`; font duy nhất là Itim.
- **Ảnh:** `anh.py` chỉ nhận tên file trần trong `anh/`, dạng jpg/png/webp, tối đa 8 MB, và bắt buộc có nguồn (trường `nguon` hoặc `anh/image_sources.json`). Ảnh đi vào trang dưới dạng data URI.
- **Phụ đề:** không dựng trong HTML mà in bằng libass sau khi chụp. `phu-de: hinh` dùng `.srt` với `force_style`; `karaoke` dùng `.ass` với `\kf`.
- **Không có lớp phủ cố định nào** ngoài dòng nguồn nhạc `#nhac-nguon`, vốn đứng yên qua camera. Khung loạt bài sẽ dùng cùng cách này.
- **Test ghim ngữ pháp:**
  - `test_video_ma_parse.py` so khớp chính xác `META_CHOICES`, `META_DEFAULTS` và `SCENE_SPEC` của một số loại cảnh;
  - `test_video_ma_cong_cu.py` so thứ tự 8 loại đầu của `SCENE_TYPES` với bản mẫu.
  Loại mới phải thêm vào cuối `SCENE_SPEC`.
- **Máy chủ repo không có Pillow** (`requirements-vi.txt` chỉ có python-docx). FFmpeg bản đầy đủ có sẵn `colorkey`, `despill`, `scale`, `crop`, `alphaextract` và `signalstats`.
- **Upstream Path B:** câu lệnh lấy từ bản kê. AI chạy vài ảnh một lượt, ghi file vào đúng tên, và không phóng to ảnh để giả kích thước.

## 3. Quyết định

| # | Quyết định | Lý do |
|---|---|---|
| Q1 | Khoá đầu `kho: ngang\|doc` (mặc định `ngang`). Một đối tượng khổ duy nhất `V.kho = {rong, cao, day, tam, le}` sinh từ khoá này thay mọi hằng số rải rác; CSS dùng biến `--rong`/`--cao`. Bố cục tính theo điểm CSS 1280×720 hoặc 720×1280. Khoá đầu `do-phan-giai: 1080\|720` (mặc định `1080`) đặt `deviceScaleFactor` của Chromium là 1,5 hoặc 1. Khung chụp là 1920×1080 hoặc 1080×1920 ở 1080; `ghep.py` giữ đúng kích thước đó. `karaoke.py` giữ `PlayRes` theo điểm CSS vì libass tự co giãn theo khung video. Ảnh AI vẽ ở kích thước xuất (Q10). | Một nguồn sự thật cho khung hình; Full HD thật mà không phải viết lại bố cục; khổ ngang giữ nguyên toạ độ cũ |
| Q2 | Bố cục theo khổ bằng bảng ô đặt tên: `V.o('cot-phai')`, `V.o('tieu-de')`, `V.o('noi-dung')`, `V.o('nhan-vat')`… trả `{x,y,w,h}` theo khổ. Ở khổ dọc, "cột phải" thành khối dưới nội dung; hai cột của `so-sanh` xếp chồng. Module cảnh chuyển từ toạ độ cứng sang ô. Giới hạn chữ khổ dọc là bảng riêng trong `kiem.py`, chốt bằng đo khi làm. | Mười bốn module sửa một lần theo một khuôn, không nhân đôi mã |
| Q3 | `phong-cach` nhận thêm `cat-dan`. Chủ đề là một bộ biến (màu, font, kiểu hiện chữ, kiểu hình) cộng một file `runtime/cat-dan.css` và `runtime/cat-dan.js` (vẽ giấy xé, chấm lưới, băng dính bằng SVG với hạt giống = số cảnh). Ở `cat-dan`: `ban-tay` mặc định `khong`, chuyển cảnh mặc định `xe-giay` (kiểu mới: mép giấy xé quét ngang trên `nenTruoc`), nét vẽ hiện nhanh và đậm. | Giữ một bộ dựng, đổi "da" |
| Q4 | Font chữ cắt dán: **Be Vietnam Pro** (SIL OFL, thiết kế cho tiếng Việt), đóng gói hai độ đậm Regular và ExtraBold vào `runtime/fonts/` kèm OFL, nhúng base64 như Itim; kiểm cmap đủ chữ Việt như vi.10. | Font không chân đậm hợp kiểu Vox; OFL cho phép đóng gói |
| Q5 | Trường tuỳ chọn mới cho `tieu-de`, `khai-niem`, `y-tung-y`, `cong-thuc`, `ke-chuyen`: `the: <nhãn> \| <giá trị> \| <chú thích>` (thẻ thông tin ba tầng; nhãn ≤ 24, giá trị ≤ 16, chú thích ≤ 60) và `tai-lieu: <dòng tài liệu>` (≤ 90, hiện nhỏ góc dưới, khác `nguon` là nguồn ảnh). | Hai thứ giáo dục nhất của video Vox: con số đinh và trích dẫn |
| Q6 | Loại cảnh mới `ke-chuyen` (thêm cuối `SCENE_SPEC`): `tieu-de` (bắt buộc, ≤ 36 ngang / ≤ 28 dọc), `nen` (bắt buộc), `tu-the`, `vi-tri: trai\|giua\|phai` (mặc định xen kẽ phải, trái theo số cảnh), `the`, `tai-lieu`, `loi`. Nền phóng chậm 1,00 → 1,06 suốt cảnh; nhân vật bật vào ở 0,2 s; tiêu đề vào ở 0,4 s; lời chỉ ở phụ đề. | Đúng khuôn 3 video mẫu, cảnh "nói bằng hình" |
| Q7 | Giá trị của `nen`: `mau/<tên>` (kho mẫu), `<file>` trong `anh/` (ảnh có nguồn như cũ), `ve: <mô tả>` (AI vẽ thành `anh/ai/nen-<N>.png`), `nhu-canh <k>` (dùng lại nền cảnh k, như video mẫu dùng lại nền). Kho mẫu vi.12 có 8 nền SVG: `giay`, `bau-troi`, `vu-tru`, `lop-hoc`, `phong-thi-nghiem`, `thanh-pho`, `dong-que`, `vong-tron`. | Một trường cho mọi nguồn nền; kho mẫu luôn dùng được |
| Q8 | Khoá đầu `nhan-vat: khong\|nguoi-que\|ve: <mô tả>` (mặc định `khong`), `mau-ao: <màu>` (8 tên màu Việt, mặc định `vang`). Trường cảnh `tu-the` nhận 10 tên cố định: `dung`, `chao`, `chi-tay`, `giai-thich`, `suy-nghi`, `ngac-nhien`, `vo-dau`, `dung-lai`, `an-mung`, `buon`. Ngoài `ke-chuyen`, `tu-the` chỉ ghi được ở `tieu-de`, `khai-niem`, `y-tung-y`, và loại trừ với `hinh`/`anh` (nhân vật chiếm ô cột phải). `tu-the` khi `nhan-vat: khong` là lỗi `parse`. | Một bộ từ cho cả người que và nhân vật AI, nên đổi nguồn chỉ là đổi khoá đầu |
| Q9 | Người que: `runtime/nhan-vat.js`, hàm thuần `dang(tuThe, t)` trả toạ độ khớp (đầu, vai, khuỷu, tay, hông, gối, chân) và nét mặt; vẽ SVG nét đen, đầu tròn trắng, áo màu. Chuyển động: nhún thở chu kỳ 2,4 s biên độ 1,5 %, chớp mắt theo lịch xác định, cử chỉ lặp nhẹ của tư thế (vẫy, chỉ, gãi đầu) trong 1,2 s đầu. | Cử động được, không cần ảnh, đồng nhất tuyệt đối |
| Q10 | Công cụ mới `tools/vi/anh_ai.py <thư_mục_video>` với hai lệnh. `ke-hoach` đọc `video.md`, ghi `anh/ai/ke-hoach.json` và in một dòng JSON: mỗi mục có `file`, `prompt`, `kich-thuoc`, `tham-chieu`. Nhân vật có một ảnh mẫu `nhan-vat-mau.png` vẽ trước (đứng thẳng, nhìn thẳng), rồi mỗi tư thế đã dùng một ảnh `tu-the-<tên>.png` vẽ kèm ảnh mẫu làm tham chiếu, trên nền xanh lá thuần #00FF00. Câu lệnh ghép từ câu phong cách cố định theo `phong-cach` và `kho`, mô tả của thầy cô, và luôn có "không chữ, không ký tự, không logo, không watermark". `nhan` kiểm mọi file trong kế hoạch rồi xử lý bằng FFmpeg: nền cắt phủ về đúng khổ xuất (1920×1080 hoặc 1080×1920, không phóng to ảnh nhỏ hơn: thiếu điểm ảnh thì cảnh báo), nén JPEG dưới 8 MB; nhân vật tách nền xanh (`colorkey` + `despill`), cắt sát, rồi kiểm alpha (bốn góc trong suốt, phần đục 5–70 %). Ảnh gốc giữ ở `anh/ai/goc/`; nguồn ghi vào `anh/ai/nguon.json` gồm công cụ, mô hình, câu lệnh, ngày. | Đẩy phần dễ sai (câu lệnh thống nhất, tách nền) vào mã xác định; AI chỉ vẽ |
| Q11 | Ảnh AI luôn có dòng nhỏ "Hình minh hoạ tạo bằng AI (<mô hình>)" trong 4 s cuối video, cùng chỗ nguồn nhạc (xếp hai dòng khi có cả hai). `video_ma.py` gặp file AI thiếu thì lỗi `canh` liệt kê đúng file thiếu, kèm cách sửa: chạy `anh_ai.py ke-hoach`; nền tảng không có công cụ vẽ thì đổi sang `nen: mau/...` và `nhan-vat: nguoi-que`. Không tự thay âm thầm. | Minh bạch với học sinh; lỗi chỉ đúng việc cần làm |
| Q12 | Khoá đầu `loat: <tên loạt>` (≤ 30). Có `loat` thì hiện tên loạt góc trái trên và "0k/N" góc phải trên, chữ nhỏ in hoa, lớp đứng yên như `#nhac-nguon`. Không có thì không hiện gì (tương thích). | Đúng khuôn "series" của video mẫu, không động tới kịch bản cũ |
| Q13 | Phụ đề: kiểu `.ass` có khung nền (`BorderStyle=3`, nền đen 60 %, chữ trắng, từ đang đọc tô vàng) cho `cat-dan` và `kho: doc`; `viet-tay` ngang giữ kiểu cũ. Khổ dọc: tối đa 22 ký tự một dòng; câu dài hơn thì tách theo dấu phẩy rồi theo từ và cảnh báo. (Sửa 2026-09-29 theo chủ repo: phụ đề mọi khổ hiện một dòng một lúc, không hai dòng cùng lúc.) Font phụ đề theo chủ đề (Itim hoặc Be Vietnam Pro). | Sửa đúng lỗi phụ đề khó đọc ở video mẫu |
| Q14 | Công thức: mỗi phần của `bieu-thuc` là một khối không ngắt dòng (`white-space: nowrap`); phần quá rộng thì thu cỡ chữ tới 70 % rồi báo lỗi `canh`, không bao giờ ngắt giữa. | Sửa lỗi "M x V = P x / Y" |
| Q15 | Tài liệu: `video-giai-thich.md` hỏi thêm khổ, phong cách, nhân vật; thêm mục "Hình do AI vẽ" theo từng nền tảng; `canh-video.md` thêm `ke-chuyen`, `the`, `tai-lieu`, `tu-the`, `nen`; `AGENTS.vi.md` §15 và luật Antigravity thêm bước `anh_ai.py` và cho phép AI dùng công cụ tạo ảnh của mình cho video. | Luồng trên Antigravity và Codex chạy đúng mà không cần câu khởi động |

## 4. Luồng ảnh AI theo nền tảng

```
video.md có nen: ve: … hoặc nhan-vat: ve: …
  │
  ├─ python tools/vi/anh_ai.py <thư_mục> ke-hoach   → anh/ai/ke-hoach.json (câu lệnh, tên file, tham chiếu)
  │
  ├─ Antigravity / Codex: AI gọi công cụ vẽ của mình cho từng mục, 3–4 ảnh một lượt,
  │  ảnh nhân vật mẫu trước, các tư thế sau (kèm ảnh mẫu làm tham chiếu), lưu vào anh/ai/goc/<file>
  │  Claude Code và nền tảng không có công cụ vẽ: không có bước này; dùng nen: mau/… và nhan-vat: nguoi-que
  │
  ├─ python tools/vi/anh_ai.py <thư_mục> nhan       → tách nền, cắt khổ, kiểm, ghi nguồn
  ├─ python tools/vi/video_ma.py <thư_mục> --xem-truoc   (bắt buộc khi có ảnh AI: AI mở xem từng cảnh; thầy cô duyệt)
  └─ python tools/vi/video_ma.py <thư_mục>
```

`anh_ai.py` in một dòng JSON theo cùng hợp đồng `ready`/`error.step`/`warnings`:

| `error.step` | Nghĩa |
|---|---|
| `input` | Không có thư mục hoặc `video.md` |
| `parse` | Lỗi ngữ pháp `video.md` |
| `thieu` | `nhan` gặp file trong kế hoạch chưa có ở `anh/ai/goc/` |
| `tach-nen` | Ảnh nhân vật tách nền không sạch; cần vẽ lại trên nền xanh thuần |
| `ffmpeg` | Máy chưa có FFmpeg |
| `write` | Không ghi được file |

## 5. Kiến trúc và file

```
tools/vi/anh_ai.py                                   ke-hoach, nhan (FFmpeg), nguon.json
tools/vi/video_ma_parts/kho.py                        đối tượng khổ, ô bố cục cho Python (kiểm tràn, karaoke)
tools/vi/video_ma_parts/runtime/kho.js                V.kho, V.o(ten) theo ngang/doc
tools/vi/video_ma_parts/runtime/cat-dan.css, cat-dan.js   da cắt dán: giấy xé, chấm lưới, băng dính, sticker, nhãn tiêu đề, xe-giay
tools/vi/video_ma_parts/runtime/nhan-vat.js           người que: dang(tuThe, t), vẽ SVG; nhân vật ảnh: bật vào, nhún, đổi tư thế
tools/vi/video_ma_parts/runtime/nen-mau.js            8 nền kho mẫu vẽ bằng SVG theo hạt giống
tools/vi/video_ma_parts/runtime/khung-loat.js         lớp tên loạt và số cảnh
tools/vi/video_ma_parts/runtime/canh/ke-chuyen.js
tools/vi/video_ma_parts/runtime/fonts/BeVietnamPro-Regular.ttf, BeVietnamPro-ExtraBold.ttf (+ OFL)
```

Sửa:

- Python: `parse.py`, `kiem.py` (khoá, trường và giới hạn theo khổ), `anh.py` (đường `ai/`, nguồn AI), `lich.py`, `trang.py`, `chup.py` (khổ), `karaoke.py`/`ghep.py` (kiểu phụ đề có khung, khổ dọc), `phong.py` (font theo chủ đề), `video_ma.py`.
- Runtime: `khung-video.js` (dùng `V.kho`/`V.o`, thẻ, tài liệu), `may-quay.js`, `ban-tay.js`, `chuyen-canh.js` (+ `xe-giay`), cả 14 module `runtime/canh/*.js` (toạ độ → ô), `viet-tay.css` (biến khổ).
- Tài liệu, test, `CHANGELOG-VI.md`.

## 6. Kiểm thử

- **Node** (hàm thuần):
  - `V.o` trả ô nằm trọn trong khung và trên vùng phụ đề, với cả hai khổ.
  - `dang(tuThe, t)` xác định, đủ 10 tư thế, chân chạm đất, không khớp nào ra ngoài ô nhân vật.
  - Giấy xé và nền mẫu cùng hạt giống thì ra cùng SVG.
  - `xe-giay` tại 0 s che toàn bộ bằng nền cũ, tại 0,5 s không còn.
  - Thứ tự hiện của `cat-dan` đúng nền → hình → chữ → tài liệu.
- **Python:**
  - parse/kiem cho mọi khoá, trường và giá trị `nen` mới; lỗi nêu đúng dòng.
  - `tu-the` sai tên thì gợi ý tên đúng.
  - Giới hạn chữ theo khổ.
  - `anh_ai.py ke-hoach` ổn định: cùng `video.md` ra cùng kế hoạch; mọi câu lệnh có câu cấm chữ; tư thế có tham chiếu.
  - `nhan` với ảnh xanh tổng hợp bằng FFmpeg: góc trong suốt; ảnh viền xanh bẩn thì lỗi `tach-nen`.
  - `.ass` có khung và dòng khổ dọc ≤ 22 ký tự.
  - Tương thích: các bản mẫu vi.9–vi.11 parse và lập lịch như cũ.
- **Chromium:**
  - Mỗi loại cảnh × 2 khổ × 2 phong cách, ở giới hạn tối đa: không tràn, không đè phụ đề, chữ tiếng Việt đúng font (kiểm cmap Be Vietnam Pro).
  - Công thức không ngắt giữa phần.
  - Khung loạt đứng yên khi camera chạy.
  - Khung `viet-tay` ngang của bản mẫu vi.11 giống ảnh chụp trước khi sửa (so pixel, sai khác ≤ 0,5 %).
- **Tích hợp:** dựng hai video ngắn bằng giọng giả rồi kiểm bằng `ffprobe`:
  - `cat-dan` + `kho: doc` + người que + nền mẫu;
  - `viet-tay` ngang + `ke-chuyen` với ảnh "AI" giả (ảnh xanh tổng hợp đã qua `nhan`).
- **Bằng mắt:** dựng lại "Vì sao in thêm tiền gây lạm phát" kiểu `cat-dan`, và một bài 9:16 có người que; chủ repo xem. Chạy thật luồng ảnh AI trên Antigravity một lần (chủ repo chạy, AI soạn sẵn) trước khi phát hành.

## 7. Ngoài phạm vi

- Gọi API tạo ảnh từ Claude Code (Path A);
- tự chọn tư thế theo nội dung;
- nhân vật nói nhép môi; nhiều nhân vật trong một cảnh;
- nền AI chuyển động (image-to-video);
- sticker cắt từ ảnh thật bằng mô hình tách nền;
- khổ dọc cho `video.py` (video từ slide).

## 8. Rủi ro

- **Nhân vật AI không đồng nhất giữa các tư thế.** Codex có ảnh tham chiếu; Antigravity chưa kiểm chứng. Đã giảm rủi ro:
  - câu phong cách cố định;
  - ảnh mẫu làm tham chiếu;
  - bước duyệt `--xem-truoc`;
  - luôn có `nguoi-que` để thay.
  Chạy thử thật trên Antigravity là điều kiện phát hành.
- **Tách nền xanh:** công cụ vẽ không luôn cho nền xanh thuần; tóc và viền có thể loang xanh. Đã có `despill`, ngưỡng và bước kiểm alpha; lỗi thì yêu cầu vẽ lại.
- **Giấy phép ảnh AI:** thuộc điều khoản của nền tảng thầy cô dùng. Repo không đóng gói ảnh AI nào (kho mẫu là SVG tự vẽ), và video luôn ghi "tạo bằng AI".
- **Khối lượng lớn:** 14 module chuyển sang ô bố cục là phần nặng nhất. Kế hoạch chia bốn đợt, phát hành cùng lúc:
  - A. khổ, ô bố cục, khổ dọc cho 14 loại;
  - B. cắt dán, font, thẻ, tài liệu, khung loạt, phụ đề có khung;
  - C. người que, `ke-chuyen`, kho mẫu;
  - D. `anh_ai.py`, nguồn AI, tài liệu theo nền tảng.
- **Full HD tăng số điểm ảnh 2,25 lần.** Chụp, mã hoá và dung lượng khung tạm đều tăng. Kế hoạch đo trước ở đợt A. Nếu vượt mục tiêu thì đổi mã hoá khung tạm (JPEG chất lượng cao thay PNG), không hạ độ phân giải mặc định.
- **Ảnh AI và ảnh thật 8 MB** ở Full HD: nền AI được `anh_ai.py nhan` nén về JPEG hoặc WebP dưới 8 MB. Giới hạn cũ giữ nguyên.

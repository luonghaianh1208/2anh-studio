# Loại việc: Video giải thích dựng bằng mã

File dành cho AI. Luôn đọc `docs/vi/tro-ly/quy-trinh-hoi.md` trước file này, và đọc `docs/vi/tro-ly/canh-video.md` trước khi viết cảnh. Đầu ra của loại việc này là một video MP4 kiểu viết tay (chữ và hình được viết dần ra theo lời đọc), không phải PPTX.

## Khi nào dùng

Thầy cô muốn một video giải thích một bài học từ nội dung chữ: video viết tay, video whiteboard, video hoạt hình chữ. Công cụ vẽ từng cảnh bằng mã (tiêu đề, khái niệm, công thức, ý từng ý, quy trình, so sánh, đồ thị, biểu đồ, sơ đồ tư duy, dòng thời gian, câu hỏi nhanh, thí nghiệm ảo, minh hoạ bằng hình vẽ nét, ảnh thật), có bàn tay cầm bút đi theo nét đang vẽ, năm kiểu chuyển cảnh và máy quay phóng vào phần đang nói; ý chính được tô, khoanh hoặc gạch chân đúng lúc giọng đọc nói tới, số liệu chạy từ 0 lên. Công cụ đọc lời bằng giọng máy tiếng Việt hoặc giọng thầy cô thu sẵn, thêm tiếng hiệu ứng nhỏ và nhạc nền nếu thầy cô muốn, rồi ghép thành video có phụ đề tô màu từng từ theo giọng đọc (kiểu karaoke).

Ví dụ câu lệnh:
- "Làm video giải thích bài Con lắc đơn bằng kiểu viết tay"
- "Làm video viết tay giải thích phản ứng trao đổi ion"
- "Làm video whiteboard về hàm số bậc ba cho Toán 12"

Khác loại việc "Video bài giảng": loại đó dựng video từ một bài giảng slide đã có. Câu lệnh chỉ có "làm video" hoặc "xuất video" (không nói rõ từ slide hay video giải thích) thì hỏi đúng một câu trước khi làm gì khác: "Thầy cô muốn làm video từ bài giảng slide đã có, hay dựng video giải thích mới từ nội dung chữ?". Trả lời slide thì dùng video-bai-giang.md; trả lời video mới thì dùng file này.

Không dùng loại việc này cho video do AI sinh hình (Veo, Flow) hay gói câu lệnh cho các công cụ đó. Bản này chỉ có một phong cách `viet-tay`, khổ ngang 16:9; chưa có kiểu Vox, chưa có khổ dọc, không chèn video tư liệu. Nhạc nền chỉ dùng file có giấy phép mở (AI tải bằng `tim_nhac.py`) hoặc file thầy cô đưa kèm nguồn. Ảnh thật thì chèn được (ảnh tĩnh có giấy phép mở hoặc ảnh thầy cô tự chụp). Chữ trong khung hình và phụ đề in dùng font Itim đóng gói sẵn, đủ mọi chữ có dấu; không cần cài font.

## Câu hỏi bắt buộc

1. Môn, lớp, tên bài và nội dung cần giải thích?
   Gợi ý: thầy cô dán nội dung hoặc dàn ý (vài gạch đầu dòng là đủ); em chia thành cảnh để thầy cô duyệt.
2. Sau video, học sinh cần hiểu hoặc làm được gì? Có muốn một câu hỏi nhanh để học sinh tự nghĩ (hiện 2–4 lựa chọn, đếm ngược vài giây rồi đọc đáp án) không?
   Gợi ý: em đề xuất một câu theo yêu cầu cần đạt của bài để thầy cô sửa; có một câu hỏi nhanh ở gần cuối video, em soạn câu hỏi và đáp án để thầy cô duyệt.
3. Video dài khoảng bao lâu?
   Gợi ý: 2–4 phút, tức 6–10 cảnh.
4. Giọng đọc nam hay nữ, tốc độ chậm, vừa hay nhanh? Thầy cô có file giọng thu sẵn cho từng cảnh không?
   Gợi ý: giọng nữ, tốc độ vừa, dùng giọng máy (cần mạng khi dựng).
5. Có muốn chèn một cảnh thí nghiệm ảo không? Có sẵn 8 mẫu: con lắc đơn, ném xiên, mạch điện nối tiếp và song song (Vật lí); chuẩn độ acid – base, cân bằng N~2~O~4~ ⇌ 2NO~2~, tốc độ phản ứng (Hoá học); khảo sát hàm số, xác suất thực nghiệm (Toán).
   Có muốn thêm ảnh chụp thật (sự vật, địa danh, nhân vật có thật) không?
   Gợi ý: thí nghiệm có, nếu bài trùng một mẫu; ảnh thật có, 1–2 ảnh khi bài nói về sự vật có thật (em tải ảnh có giấy phép mở và cho thầy cô xem trước khi dựng). Hình vẽ nét, biểu đồ, sơ đồ tư duy, dòng thời gian và chỗ nhấn ý chính em tự chọn theo bài, không cần hỏi.
6. Phụ đề in lên hình (chữ tô vàng dần theo giọng đọc), để thành file riêng, hay không cần phụ đề?
   Gợi ý: in lên hình, tô vàng theo giọng đọc.
7. Có muốn tiếng hiệu ứng nhỏ (tiếng bút viết, tiếng "ting" khi ý hiện, tích tắc khi đếm ngược) và nhạc nền nhẹ không?
   Gợi ý: tiếng hiệu ứng có (luôn nhỏ hơn giọng đọc, tắt được); nhạc nền không, trừ khi thầy cô muốn: khi đó em tìm một bản nhạc giấy phép mở (cần mạng), ghi tên tác giả ở cuối video và gửi thầy cô nghe thử trước khi dựng, hoặc dùng file nhạc thầy cô gửi kèm nguồn.

## Câu hỏi tuỳ chọn

- Có ý nào cần nhấn mạnh, nhắc lại ở cảnh cuối không? Chỉ hỏi khi video dài trên 4 phút.
- Tên video hiện ở cảnh mở đầu? Chỉ hỏi khi thầy cô muốn khác tên bài.
- Học sinh xem là lớp đại trà, lớp chuyên hay học sinh cần hỗ trợ? Chỉ hỏi khi nội dung có nhiều mức khó.

## Tạo nhanh

1. Môn, lớp, tên bài và nội dung cần giải thích (câu hỏi bắt buộc 1).
2. Video dài khoảng bao lâu (câu hỏi bắt buộc 3).

Tạo nhanh vẫn ghi brief; các câu không hỏi thì dùng gợi ý và ghi kèm "(AI đề xuất, chưa duyệt)". Riêng ảnh thật và nhạc nền: tạo nhanh không tải ảnh hay nhạc trừ khi thầy cô tự yêu cầu trong câu lệnh, vì cả hai cần thầy cô xem hoặc nghe trước; hình vẽ nét, dấu nhấn, biểu đồ, câu hỏi nhanh và tiếng hiệu ứng vẫn dùng như thường.

## Cấu trúc video.md

Viết một file `video.md` trong `projects/_video/<tên_video>/`. File mở đầu bằng khối thông tin giữa hai dòng `---`, rồi mỗi cảnh một mục `## Cảnh N`, đánh số liên tiếp từ 1.

Khối thông tin:

| Khoá | Bắt buộc | Giá trị |
|---|---|---|
| `tieu-de` | có | tên video |
| `mon`, `lop` | có | môn và lớp |
| `phong-cach` | không | `viet-tay` (mặc định, duy nhất ở bản này) |
| `giong` | không | `nu` (mặc định) hoặc `nam` |
| `toc-do` | không | `cham`, `vua` (mặc định) hoặc `nhanh` |
| `phu-de` | không | `karaoke` (mặc định: in lên hình, tô vàng từng từ theo giọng đọc), `hinh` (in lên hình kiểu cũ, cả câu một màu), `file` (file `phu-de.srt` riêng) hoặc `khong` |
| `ban-tay` | không | `co` (mặc định: bàn tay cầm bút đi theo nét và chữ đang viết) hoặc `khong` |
| `may-quay` | không | `co` (mặc định: phóng vào phần đang nói, tối đa 1,35 lần, thu về toàn cảnh trước khi hết cảnh) hoặc `khong` |
| `chuyen-canh` | không | `lau-bang` (mặc định: 0,5 giây đầu mỗi cảnh từ cảnh 2, bàn tay cầm giẻ lau bảng cũ), `lat-trang`, `truot`, `phong`, `mo-man`, `luan-phien` (xoay vòng năm kiểu) hoặc `khong`; cách chuyển ở mục "Chuyển cảnh" của `docs/vi/tro-ly/canh-video.md` |
| `chu-dong` | không | `co` (mặc định: tiêu đề cảnh `tieu-de` nảy vào từng chữ cái, cụm nhấn nảy nhẹ khi nổ) hoặc `khong` |
| `am-thanh` | không | `co` (mặc định: tiếng bút viết, tiếng "ting" khi ý hiện, tiếng chuyển cảnh, tích tắc khi đếm ngược, chuông khi hiện đáp án, tiếng nhỏ khi nhấn ý) hoặc `khong` |
| `kho` | không | `ngang` (mặc định: 16:9) hoặc `doc` (9:16, cho Reels, TikTok, Story) |
| `do-phan-giai` | không | `1080` (mặc định: Full HD, 1920×1080 hoặc 1080×1920) hoặc `720` (1280×720 hoặc 720×1280, dựng nhanh hơn cho máy yếu) |
| `nhac-nen` | không | tên file nhạc trong thư mục `nhac/` của video (`.mp3`, `.m4a`, `.wav`, `.ogg`); không ghi thì không có nhạc |
| `nguon-nhac` | không | dòng nguồn của nhạc nền, chỉ ghi kèm `nhac-nen` khi `nhac/nguon.json` không có bản ghi cho file đó (nhạc thầy cô gửi) |

Các khoá `ban-tay`, `may-quay`, `chuyen-canh`, `chu-dong`, `am-thanh` chỉ ghi khi muốn đổi: không ghi thì đều bật (`chuyen-canh` là lau bảng). Ghi `khong` khi thầy cô thấy rối mắt hay ồn và muốn tắt. Cảnh `thi-nghiem` không có bàn tay, máy quay chỉ đẩy chậm. Kịch bản cũ ghi `phu-de: hinh` vẫn giữ phụ đề kiểu cũ.

Hiệu ứng âm thanh do công cụ tự tạo bằng FFmpeg (không dùng file ngoài, không vướng giấy phép), luôn thấp hơn giọng đọc khoảng 20 dB; tiếng bút không kéo dài quá 40% thời gian mỗi cảnh. Nhạc nền được lặp cho đủ dài, vào và ra dần 1,5 giây, tự nhỏ đi khi có giọng đọc (khoảng 14–24 dB), và dòng nguồn nhạc hiện ở góc dưới bên trái trong 4 giây cuối video (cảnh cuối ngắn hơn 4 giây thì hiện suốt cảnh cuối). Nhạc thiếu nguồn, thiếu file, sai định dạng hay hỏng là lỗi `canh` (thông báo "Cảnh 0: nhạc nền: …" nêu dòng khoá đầu).

Mỗi cảnh:

- Dòng `loai:` là một trong mười bốn loại cảnh ở `docs/vi/tro-ly/canh-video.md`.
- Dòng `loi:` là lời đọc của cảnh, viết trên một dòng, ít nhất một câu.
- Các trường của loại cảnh đó, mỗi dòng dạng `khoá: giá trị`. Trường lặp (ví dụ `y:`, `buoc:`) thì viết nhiều dòng cùng khoá.
- Dòng `chuyen:` tuỳ chọn, từ cảnh 2: kiểu chuyển cảnh riêng của cảnh đó, ghi đè khoá đầu `chuyen-canh`.

Giới hạn chữ (đếm ký tự hiện ra, không tính dấu quy ước và dấu nhấn): tiêu đề cảnh tối đa 90; `khai-niem` thuật ngữ 60, định nghĩa 220; `cong-thuc` biểu thức 90, mỗi giải thích 60; mỗi ý của `y-tung-y` và `so-sanh` 60; mỗi bước của `quy-trinh` 50; tên cột `trai`, `phai` 24; tên trục 40; `bieu-do` nhãn 16; `so-do` trung tâm 30, mỗi nhánh 40; `dong-thoi-gian` nhãn mốc 12, mô tả 60; `cau-hoi` câu hỏi 160, mỗi lựa chọn 60, giải thích 180. Vượt giới hạn là lỗi `canh`. Lời (hoặc lời giải) dài quá 700 ký tự chỉ bị cảnh báo, nhưng nên tách cảnh.

Quy ước chữ: `H~2~SO~4~` cho chỉ số dưới, `m/s^2^` cho chỉ số trên, `**in đậm**`. Không chèn địa chỉ web vào file: công cụ báo lỗi `parse`.

Nhấn ý chính và số chạy (cú pháp đầy đủ ở mục "Nhấn ý chính và số chạy" của `docs/vi/tro-ly/canh-video.md`): `==chữ==` tô vàng, `((chữ))` khoanh tròn, `__chữ__` gạch chân, nổ đúng lúc giọng đọc nói tới cụm đó trong lời; `{{2.01}}` là số chạy từ 0 lên, viết dấu chấm thập phân, hiện "2,01". Tối đa 3 cụm mỗi dòng, không lồng nhau; trong `bieu-thuc` của công thức chỉ `{{số}}` có tác dụng. Viết cụm đúng như trong lời, cùng cách viết dấu ("chu kì" khác "chu kỳ").

Cách chia bài thành cảnh:

- Mỗi cảnh một ý. Lời 1–4 câu; câu đầu nêu ý của cảnh.
- Cảnh có danh sách (`y-tung-y`, `quy-trinh`, `so-sanh`, giải thích và các phần của `cong-thuc`, mục của `bieu-do`, nhánh của `so-do`, mốc của `dong-thoi-gian`): ý thứ k hiện ra khi câu thứ k của lời bắt đầu, nên viết mỗi ý ứng với đúng một câu, theo đúng thứ tự.
- Viết lời để đọc thành tiếng: số và kí hiệu viết thành chữ khi cần ("hai pi", "mười dao động"), không viết kí hiệu mà giọng máy đọc sai.
- Mở đầu bằng một cảnh `tieu-de`; cảnh cuối nên tóm tắt điều học sinh cần nhớ.
- Chọn cảnh theo nội dung: số liệu so sánh dùng `bieu-do`; tóm tắt cuối bài dùng `so-do`; tiến trình lịch sử hay các giai đoạn dùng `dong-thoi-gian`; công thức cần thay số dùng `cong-thuc` hiện từng phần; một `cau-hoi` ở gần cuối video, sau phần tóm tắt.
- Mỗi cảnh nhấn 1–2 ý chính bằng `==`, `((`, `__` và dùng `{{số}}` cho con số cần nhớ; nhấn quá nhiều thì học sinh không còn biết ý nào quan trọng.
- Video từ 6 cảnh nên dùng `chuyen-canh: luan-phien` cho đỡ lặp; hoặc giữ một kiểu và đặt `chuyen:` riêng ở cảnh mở một phần mới.

Hình và ảnh:

- Video nên có hình, không chỉ có chữ: khoảng một nửa số cảnh có `hinh:` hoặc `anh:`, và có ít nhất một cảnh `minh-hoa` khi bài có dụng cụ, sự vật hay các bước cụ thể. Tên biểu tượng tra ở mục "Bảng tra biểu tượng" của `docs/vi/tro-ly/canh-video.md`; chọn hình nói đúng sự vật trong lời, không chọn hình chỉ để trang trí.
- Cảnh `minh-hoa`: hình thứ k hiện khi câu thứ k của lời bắt đầu, nên viết mỗi hình ứng với đúng một câu.
- Ảnh thật (cảnh `anh` hoặc trường `anh:`) chỉ dùng khi thầy cô đồng ý ở câu hỏi 5. AI tải ảnh bằng `image_search.py` vào `anh/` của thư mục video (cách tải và cách ghi nguồn ở mục "Ảnh thật" của `docs/vi/tro-ly/canh-video.md`). Ảnh phải có nguồn; không có nguồn là lỗi `canh`.

Giọng thu sẵn: thầy cô đưa file MP3 thì đặt vào `giong/canh-1.mp3`, `giong/canh-2.mp3`… trong thư mục video, đúng số cảnh. Cảnh có file thì dùng file đó và không cần mạng; công cụ không bao giờ ghi đè file thầy cô đặt. File thầy cô chép đè lên giọng máy cũ vẫn được nhận là file thầy cô, kể cả khi `giong/canh-N.json` của lần trước còn đó; xoá file `.json` đó cũng không sao. Cảnh không có file thì tạo bằng giọng máy (cần mạng). File giọng thu sẵn không có mốc câu hay mốc từng từ nên các ý, dấu nhấn và phụ đề karaoke chạy theo ước lượng (có thể lệch tiếng vài trăm mili giây) và có một cảnh báo "ước lượng" cho cảnh đó. Giọng máy có mốc từng từ thật; khi không khớp được chữ với giọng, công cụ cũng chuyển sang ước lượng kèm cảnh báo. Cảnh `cau-hoi` có thêm giọng lời giải `giong/canh-N-giai.mp3`, theo cùng luật.

Nhạc nền: chỉ dùng khi thầy cô đồng ý ở câu hỏi 7. Nhạc đặt trong thư mục `nhac/` của video. AI tải nhạc giấy phép mở bằng `tim_nhac.py` (mục "Đầu ra"), lệnh tự ghi nguồn vào `nhac/nguon.json` nên chỉ cần ghi `nhac-nen: <tên file>`. Nhạc thầy cô gửi: chép vào `nhac/` rồi ghi thêm `nguon-nhac:` theo lời thầy cô, ví dụ `nguon-nhac: Nhạc: Khúc ca mùa thu · thầy Minh tự sáng tác`. Không dùng nhạc không rõ nguồn hay nhạc tải từ YouTube.

Ví dụ (Hoá học, bốn cảnh, có một cảnh thí nghiệm ảo):

```
---
tieu-de: Chuẩn độ acid – base
mon: Hoá học
lop: 11
giong: nu
toc-do: vua
phu-de: hinh
---

## Cảnh 1
loai: tieu-de
chu: Chuẩn độ acid – base
phu: Hoá học 11
loi: Hôm nay chúng ta tìm hiểu cách xác định nồng độ một dung dịch acid bằng phép chuẩn độ.

## Cảnh 2
loai: khai-niem
thuat-ngu: Điểm tương đương
dinh-nghia: Thời điểm lượng NaOH thêm vào vừa đủ phản ứng hết với lượng acid có trong bình.
loi: Điểm tương đương là lúc lượng NaOH thêm vào vừa đủ phản ứng hết với acid trong bình.

## Cảnh 3
loai: y-tung-y
tieu-de: Ba bước chuẩn độ
y: Lấy chính xác thể tích acid vào bình tam giác
y: Nhỏ từ từ dung dịch NaOH từ burette
y: Dừng khi chất chỉ thị vừa đổi màu
loi: Bước một, lấy chính xác thể tích acid vào bình tam giác. Bước hai, nhỏ từ từ dung dịch NaOH từ burette. Bước ba, dừng lại khi chất chỉ thị vừa đổi màu.

## Cảnh 4
loai: thi-nghiem
mau: hoa-chuan-do
tham-so: 1 the-tich-base 0
tham-so: 6 the-tich-base 30
do: ph
loi: Hãy quan sát pH khi nhỏ thêm NaOH. Gần điểm tương đương, pH tăng vọt rất nhanh.
```

Ví dụ (Vật lí, sáu cảnh, có hình vẽ nét, cảnh minh hoạ và hai ảnh thật). Trước khi dựng, AI đã tải `dong-ho-qua-lac.jpg` vào `anh/` bằng `image_search.py`, nên ảnh ở cảnh 5 lấy nguồn từ `anh/image_sources.json`; ảnh ở cảnh 4 do thầy cô tự chụp và gửi, nên ghi nguồn bằng `nguon:`.

```
---
tieu-de: Con lắc đơn
mon: Vật lí
lop: 11
giong: nu
ban-tay: co
may-quay: co
chuyen-canh: lau-bang
---

## Cảnh 1
loai: tieu-de
chu: Con lắc đơn
phu: Vật lí 11
hinh: clock
loi: Hôm nay chúng ta tìm hiểu con lắc đơn và chu kì dao động của nó.

## Cảnh 2
loai: khai-niem
thuat-ngu: Chu kì T
dinh-nghia: Khoảng thời gian ngắn nhất để con lắc thực hiện một dao động toàn phần, đo bằng giây.
hinh: hourglass
loi: Chu kì là khoảng thời gian ngắn nhất để con lắc thực hiện một dao động toàn phần.

## Cảnh 3
loai: minh-hoa
tieu-de: Dụng cụ đo chu kì
hinh: stopwatch | Đồng hồ bấm giây
hinh: ruler-measure | Thước đo chiều dài
hinh: weight | Quả nặng
loi: Ta cần đồng hồ bấm giây. Ta cần thước đo chiều dài dây. Và một quả nặng.

## Cảnh 4
loai: anh
anh: con-lac-phong-thi-nghiem.jpg
chu-thich: Con lắc đơn ở phòng thí nghiệm Vật lí của trường
nguon: Ảnh: cô Lan chụp
loi: Đây là con lắc đơn ở phòng thí nghiệm của trường. Quả nặng treo vào một sợi dây nhẹ.

## Cảnh 5
loai: y-tung-y
tieu-de: Con lắc trong đời sống
y: Đồng hồ quả lắc đếm giây
y: Máy đo địa chấn
anh: dong-ho-qua-lac.jpg
loi: Đồng hồ quả lắc dùng con lắc để đếm giây. Máy đo địa chấn cũng dùng con lắc.

## Cảnh 6
loai: cong-thuc
bieu-thuc: T = 2π√(l/g)
giai-thich: l là chiều dài dây, đơn vị mét
giai-thich: g là gia tốc trọng trường
hinh: math-function
loi: Chu kì bằng hai pi nhân căn của l chia g. Chữ l là chiều dài dây. Chữ g là gia tốc trọng trường.
```

Ví dụ (Khoa học tự nhiên, sáu cảnh, có dấu nhấn, số chạy, biểu đồ tròn, dòng thời gian, sơ đồ tư duy, câu hỏi nhanh và nhạc nền). Trước khi kiểm, AI đã tải `calm-piano.mp3` vào `nhac/` bằng `tim_nhac.py "calm piano"`, nên nguồn nhạc lấy từ `nhac/nguon.json`.

```
---
tieu-de: Thành phần của không khí
mon: Khoa học tự nhiên
lop: 6
chuyen-canh: luan-phien
am-thanh: co
nhac-nen: calm-piano.mp3
---

## Cảnh 1
loai: tieu-de
chu: Thành phần của ((không khí))
phu: Khoa học tự nhiên 6
hinh: wind
loi: Không khí quanh ta gồm những chất nào? Hôm nay chúng ta cùng tìm hiểu thành phần của không khí.

## Cảnh 2
loai: bieu-do
tieu-de: Thành phần không khí theo thể tích
kieu: tron
du-lieu: Nitrogen | 78
du-lieu: Oxygen | 21
du-lieu: Khí khác | 1
loi: Nitrogen chiếm khoảng bảy mươi tám phần trăm. Oxygen chiếm khoảng hai mươi mốt phần trăm. Các khí khác chỉ khoảng một phần trăm.

## Cảnh 3
loai: y-tung-y
tieu-de: Vai trò của các khí
y: Nitrogen chiếm khoảng {{78}}% thể tích không khí
y: ==Oxygen== duy trì sự cháy và sự hô hấp
y: Carbon dioxide cần cho cây xanh __quang hợp__
loi: Nitrogen chiếm khoảng bảy mươi tám phần trăm thể tích không khí. Oxygen duy trì sự cháy và sự hô hấp. Carbon dioxide cần cho cây xanh quang hợp.

## Cảnh 4
loai: dong-thoi-gian
tieu-de: Tìm ra các khí trong không khí
moc: 1772 | Rutherford tách được nitrogen
moc: 1774 | Priestley điều chế được oxygen
moc: 1894 | Rayleigh và Ramsay tìm ra argon
loi: Năm 1772, Rutherford tách được nitrogen. Năm 1774, Priestley điều chế được oxygen. Năm 1894, Rayleigh và Ramsay tìm ra khí argon.

## Cảnh 5
loai: so-do
trung-tam: Không khí
hinh: wind
nhanh: Nitrogen nhiều nhất
nhanh: ==Oxygen== cho sự cháy và hô hấp
nhanh: Carbon dioxide cho quang hợp
loi: Tóm lại, nitrogen chiếm nhiều nhất. Oxygen cần cho sự cháy và sự hô hấp. Carbon dioxide cần cho quang hợp.

## Cảnh 6
loai: cau-hoi
chuyen: lat-trang
cau-hoi: Khí nào chiếm tỉ lệ thể tích lớn nhất trong không khí?
lua-chon: Oxygen
lua-chon: Nitrogen
lua-chon: Carbon dioxide
dap-an: B
cho: 5
giai-thich: Nitrogen chiếm khoảng {{78}}% thể tích, nhiều hơn hẳn các khí khác.
loi-giai: Đáp án B. Nitrogen chiếm khoảng bảy mươi tám phần trăm thể tích không khí.
loi: Khí nào chiếm tỉ lệ thể tích lớn nhất trong không khí? A, oxygen. B, nitrogen. C, carbon dioxide.
```

## Đầu ra

Thư mục của mỗi video là `projects\_video\<tên_video>\`, chứa `video.md`. Có `venv\Scripts\python.exe` ở thư mục gốc repo thì dùng nó thay cho `python` trong các lệnh dưới.

1. Có ảnh thật: tải từng ảnh trước khi kiểm, bằng `python skills\ppt-master\scripts\image_search.py "<từ khoá tiếng Anh>" --filename <tên>.jpg --orientation landscape -o projects\_video\<tên_video>\anh` (ảnh cột phải dùng `--orientation portrait` hoặc `square`). Mở bản thu nhỏ `anh\.review\<tên>.jpg` xem ảnh có đúng nội dung không; sai thì tải lại với từ khoá khác. Chỉ chạy lệnh này, không sửa gì trong `skills/`.
2. Có nhạc nền (thầy cô đồng ý ở câu hỏi 7) mà thầy cô không gửi file: tìm và tải bằng `python tools\vi\tim_nhac.py "<từ khoá tiếng Anh>" -o projects\_video\<tên_video>\nhac`, ví dụ từ khoá "calm piano", "soft acoustic guitar". Lệnh chỉ lấy bản CC0 hoặc CC BY trên Openverse, dài từ 60 giây, tải qua https, không ghi đè file đã có, và ghi tên bài, tác giả, giấy phép vào `nhac/nguon.json`. Đọc dòng JSON: `ready` là `true` thì ghi `nhac-nen: <tên trong files>` vào khối thông tin, và gửi thầy cô tên bài, tác giả, giấy phép (trong `ban`) kèm đường dẫn file để thầy cô mở nghe thử; thầy cô không ưng thì tải bản khác bằng từ khoá khác. `error.step` là `mang` thì kiểm mạng rồi chạy lại, tối đa một lần; `input` là không tìm được bản phù hợp hoặc `nhac/nguon.json` sai cấu trúc, làm theo `error.fix`; `write` là không ghi được thư mục `nhac`. Không tự sửa hay tự viết bản ghi trong `nhac/nguon.json`.
3. Kiểm cú pháp và giới hạn: `python tools\vi\video_ma.py projects\_video\<tên_video> --plan-only`. Ảnh quá 8 MB hay thiếu nguồn, nhạc thiếu nguồn, tên biểu tượng sai là lỗi `canh`; xử lý theo mục "Ảnh thật" của `docs/vi/tro-ly/canh-video.md` hoặc chọn tên trong các tên mà lỗi gợi ý (tên biểu tượng là tiếng Anh, tra "Bảng tra biểu tượng").
4. Dựng thử: `python tools\vi\video_ma.py projects\_video\<tên_video> --xem-truoc`. Công cụ chụp mỗi cảnh một ảnh ở trạng thái cuối cảnh vào thư mục `xem-truoc`, không tạo giọng, không ghép. Nên chạy trước khi dựng thật và mở xem từng ảnh: chữ chồng lên nhau hay tràn khung thì rút gọn nội dung hoặc chia cảnh rồi chạy lại. Video có ảnh thật thì bước này bắt buộc: gửi thầy cô xem các ảnh cảnh có ảnh thật (và nguồn ảnh) trong khung chat, chờ thầy cô đồng ý rồi mới dựng thật. Cảnh `cau-hoi` trong ảnh xem trước đã hiện đáp án; gửi thầy cô duyệt câu hỏi và đáp án.
5. Dựng thật: `python tools\vi\video_ma.py projects\_video\<tên_video>`. Công cụ chụp 30 khung/giây bằng nhiều tiến trình Chromium song song. Thời gian dựng khoảng 1,5 lần thời lượng video trên máy 6 lõi (video 5 phút mất khoảng 7–8 phút), khoảng 2 lần trên máy 2–3 lõi (khoảng 11 phút), chưa kể tạo giọng; báo trước thầy cô một dòng.
6. Nhắc thầy cô nghe thử video: tiếng hiệu ứng và nhạc nền có vừa tai không. Thấy ồn thì ghi `am-thanh: khong` (tắt tiếng hiệu ứng) hoặc bỏ dòng `nhac-nen` (bỏ nhạc) rồi dựng lại; giọng đã có nên dựng lại nhanh hơn.

Công cụ ghi vào chính thư mục đó:

- `video.mp4`: video 1280×720.
- `phu-de.srt`: chỉ có khi `phu-de: file`. Với `karaoke` và `hinh`, phụ đề in lên hình.
- `giong\canh-N.mp3`: giọng từng cảnh; cảnh `cau-hoi` có thêm `giong\canh-N-giai.mp3`. Lần dựng sau, cảnh có lời không đổi dùng lại giọng cũ; chỉ cảnh bị sửa lời mới tạo giọng lại.

Đọc dòng JSON ở stdout. `ready` là `true` thì báo thầy cô đường dẫn `video.mp4`, số cảnh, thời lượng (`thoi_luong_giay`), nguồn giọng (`giong`: `may` là giọng máy, `co-san` là file thầy cô đưa, `hon-hop` là cả hai), nơi để phụ đề, và đọc nguyên văn các dòng `warnings`.

| `error.step` | Xử lý |
|---|---|
| `input` | Chưa có thư mục hoặc `video.md`, hoặc sai tham số lệnh: viết file rồi chạy lại. |
| `parse` | Sửa đúng dòng `error.message` nêu rồi chạy lại. |
| `canh` | Nội dung cảnh sai (chữ quá dài, tràn khung, mã mẫu hay mã tham số lạ, mốc `tham-so` vượt thời lượng cảnh, tên biểu tượng sai, ảnh thiếu, sai định dạng, quá 8 MB hoặc chưa có nguồn): rút gọn hoặc sửa cảnh đó theo `error.message`. "Cảnh 0: nhạc nền: …" là lỗi file nhạc (thiếu file trong `nhac/`, sai định dạng, hỏng, hoặc chưa có nguồn): tải lại bằng `tim_nhac.py`, hoặc thêm `nguon-nhac:` cho nhạc thầy cô gửi. |
| `giong` | Không tạo được giọng máy, thường do mất mạng: kiểm mạng rồi chạy lại, tối đa một lần; hoặc đặt file giọng thầy cô đưa vào đúng file mà `error.message` nêu (`giong/canh-N.mp3`, hoặc `giong/canh-N-giai.mp3` cho lời giải của cảnh câu hỏi). |
| `chromium` | Chưa cài Chromium: hỏi thầy cô trước (tải 150–300 MB), rồi chạy `powershell -NoProfile -ExecutionPolicy Bypass -File tools\vi\pptmaster.ps1 -Action tool -Name chromium`. |
| `ffmpeg` | Chưa có FFmpeg: cài theo mục "Công cụ tuỳ chọn" của `docs/vi/cai-dat-bang-ai.md`. |
| `dung` | Chụp khung hoặc ghép hỏng: báo nguyên `error.message` cho thầy cô, không tự sửa. |
| `write` | Không ghi được file: xin thầy cô đóng `video.mp4` nếu đang mở, kiểm ổ đĩa còn chỗ, rồi chạy lại. |
| `internal` | Lỗi ngoài dự kiến: dán nguyên `error.message` để báo cho người bảo trì, không tự đoán cách sửa. |

Không tự chạy FFmpeg, không tự ghép hay cắt video theo cách riêng. Không viết HTML hay ảnh cảnh bằng tay, không sửa khung hình trong thư mục tạm: mọi thay đổi đi qua `video.md` rồi chạy lại công cụ.

## Ghi vào brief

- Loại việc: Video giải thích dựng bằng mã.
- Thầy cô yêu cầu: môn, lớp, bài, nội dung cần giải thích, điều học sinh cần đạt, câu hỏi nhanh, độ dài, giọng, tốc độ, cảnh thí nghiệm, phụ đề, giọng thu sẵn, tiếng hiệu ứng, nhạc nền — ghi đúng lời thầy cô.
- AI đề xuất (thầy cô đã đồng ý): danh sách cảnh (loại cảnh và ý chính của từng cảnh), hình vẽ nét và ảnh thật của từng cảnh (từ khoá tải ảnh, tác giả, giấy phép), mẫu thí nghiệm nếu có, câu hỏi nhanh và đáp án, kiểu chuyển cảnh, nhạc nền (từ khoá, tên bài, tác giả, giấy phép), và các gợi ý thầy cô chấp nhận.
- Loại việc này không tạo PPTX: ghi brief vào `projects/_video/<tên_video>/brief.md`; không chạy `import-sources`, không có bước xác nhận của upstream.
- Tin nhắn hỏi vẫn kết thúc bằng dòng chốt cách xác nhận như các loại việc khác, nhưng luôn ở dạng khung chat và không mở trang web xác nhận: "Trước khi dựng, em sẽ gửi danh sách cảnh trong khung chat để thầy cô duyệt. Thầy cô đồng ý nhé?". Tạo nhanh thì bỏ bước duyệt này.
- Viết theo mẫu `docs/vi/tro-ly/mau-brief.md`.

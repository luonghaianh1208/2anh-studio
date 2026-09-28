# Cảnh video giải thích: danh mục mười lăm loại cảnh

File dành cho AI. Đọc cùng `docs/vi/tro-ly/video-giai-thich.md`. Mỗi cảnh trong `video.md` có `loai:`, `loi:` và các trường của loại cảnh dưới đây; trường không có trong danh sách của loại cảnh là lỗi `parse`. Mọi loại cảnh có thêm trường tuỳ chọn `chuyen:` (kiểu chuyển cảnh riêng của cảnh đó, xem mục "Chuyển cảnh").

Quy ước chung:

- Giới hạn tính theo số ký tự hiện ra, không tính dấu quy ước `~`, `^`, `**` và dấu nhấn `==`, `((`, `))`, `__`, `{{`, `}}`; số chạy `{{2.01}}` tính theo chữ hiện ra ("2,01"). Vượt giới hạn là lỗi `canh`.
- Trường lặp viết nhiều dòng cùng khoá, theo đúng thứ tự muốn hiện.
- Cảnh có danh sách: ý thứ k hiện khi câu thứ k của `loi` bắt đầu; lời ít câu hơn số ý thì các ý hiện đều nhau theo thời lượng giọng.
- Không chèn địa chỉ web vào bất kỳ trường nào.
- Bốn loại `tieu-de`, `khai-niem`, `cong-thuc`, `y-tung-y` có thêm trường tuỳ chọn `hinh` (tên một biểu tượng `tabler-outline`, ví dụ `hinh: flask`) hoặc `anh` (tên file trong `anh/`, ví dụ `anh: con-lac.jpg`); một cảnh chỉ được có một trong hai, không cả hai (có cả hai là lỗi `parse`). Cảnh có `anh` ghi thêm được `nguon` (dòng nguồn của ảnh); `nguon` mà không có `anh` là lỗi `parse`.
- Cảnh `tieu-de` có hình: hình 180×180 được vẽ dần ở giữa phía trên, rồi tiêu đề viết bên dưới. Ba loại còn lại: hình hoặc ảnh nằm ở cột phải, chữ thu hẹp về bên trái; giới hạn ký tự giữ nguyên, chữ dài thì cỡ chữ nhỏ lại một chút và công cụ vẫn bắt lỗi tràn khung.
- Ba loại `tieu-de`, `khai-niem`, `y-tung-y` (và cảnh `ke-chuyen`, mục "Kể chuyện") có thêm trường tuỳ chọn `tu-the` (tư thế của nhân vật dẫn chuyện, cần khoá đầu `nhan-vat: nguoi-que` hoặc `nhan-vat: ve: <mô tả>`): một trong mười tên `dung`, `chao`, `chi-tay`, `giai-thich`, `suy-nghi`, `ngac-nhien`, `vo-dau`, `dung-lai`, `an-mung`, `buon`. Nhân vật đứng ở cột phải (khổ dọc: khối dưới nội dung), quay mặt về phía chữ, nên cảnh có `tu-the` không có `hinh` hay `anh`. `tu-the` khi `nhan-vat: khong`, cùng `hinh`/`anh`, hay tên sai (kể cả tên tiếng Anh, thiếu dấu gạch) là lỗi `parse`; lỗi gợi ý tối đa 3 tên đúng. Màu áo người que theo khoá đầu `mau-ao`.
- Tên biểu tượng là tiếng Anh, không có tiền tố thư viện: tra ở mục "Bảng tra biểu tượng" cuối file. Viết `tabler-outline/flask`, `Flask` hay `flask.svg` vẫn được nhận; tên sai hay tên tiếng Việt là lỗi `canh`: lỗi nhắc tên phải là tiếng Anh, chỉ tới bảng tra, và gợi ý tối đa 5 tên (tên tiếng Việt được đối chiếu với cột khái niệm của bảng tra trước; không bao giờ gợi ý biểu tượng thương hiệu `brand-*`).
- Ảnh thật do AI tải về `anh/` của thư mục video bằng `image_search.py` trước khi dựng: xem mục "Ảnh thật".
- Mỗi hình được vẽ dần từng nét như bút vẽ trên bảng; bàn tay cầm bút đi theo nét và chữ đang viết, máy quay phóng vào phần đang nói rồi thu về toàn cảnh trước khi hết cảnh. Tắt được bằng khoá đầu `ban-tay`, `may-quay`, `chuyen-canh`; chữ nảy, tiếng hiệu ứng và phụ đề karaoke tắt bằng `chu-dong`, `am-thanh`, `phu-de` (xem `docs/vi/tro-ly/video-giai-thich.md`).
- Khoá đầu mới của bản này: `chu-dong` và `am-thanh` (mặc định `co`), `phu-de` thêm giá trị `karaoke` (mặc định), `chuyen-canh` thêm bốn kiểu và `luan-phien` (mục "Chuyển cảnh"), `nhac-nen` và `nguon-nhac` cho nhạc nền. Nhạc nền đặt trong `nhac/` của video; AI tải bằng `tim_nhac.py` theo mục "Đầu ra" của `docs/vi/tro-ly/video-giai-thich.md`. Tiếng hiệu ứng gắn với cảnh tự động: tiếng bút khi viết và vẽ, "ting" khi một ý, bước, nhánh, mốc, cột hay lựa chọn hiện ra, tiếng chuyển cảnh, tích tắc và chuông ở cảnh `cau-hoi`, tiếng nhỏ khi nhấn ý; không cần ghi gì trong cảnh.

## Nhấn ý chính và số chạy

Viết ngay trong chữ của các trường hiện trên hình (tiêu đề, định nghĩa, ý, bước, nhánh, mốc, lựa chọn, giải thích…), không thêm trường mới:

| Viết | Hiện ra |
|---|---|
| `==chữ==` | tô nền vàng như bút dạ quang, quét từ trái sang phải |
| `((chữ))` | khoanh bằng một vòng elip đỏ vẽ tay |
| `__chữ__` | gạch chân đỏ vẽ dần |
| `{{số}}` | số chạy từ 0 lên giá trị đó trong 0,8 giây, bắt đầu khi bút viết tới chỗ số |

Cụm nhấn nổ khi giọng đọc tới từ đầu tiên của cụm trong `loi` (hoặc trong `loi-giai` với cảnh `cau-hoi`), không bao giờ trước khi cụm được viết xong. So khớp không phân biệt hoa thường, bỏ dấu câu nhưng **giữ dấu thanh**: `((chu kì))` khớp "Chu kì" trong lời, nhưng không khớp "chu kỳ". Cụm không có trong lời thì nổ 0,3 giây sau khi được viết xong. Vì vậy viết cụm đúng như trong lời, cùng một cách viết dấu. Khoá đầu `chu-dong: co` (mặc định) làm cụm nảy nhẹ khi nổ; `am-thanh: co` thêm một tiếng nhỏ.

Luật:

- Tối đa 3 cụm nhấn mỗi trường (mỗi dòng); không lồng cụm trong cụm; cụm mở thì phải đóng. Sai là lỗi `parse` nêu đúng dòng.
- `**`, `~`, `^` phải nằm trọn trong cụm hoặc trọn ngoài cụm; ngoặc trong `((…))` phải đủ cặp (công thức có ngoặc thì dùng `==…==`).
- Chữ thường, không phải dấu nhấn: `____` (từ ba dấu gạch dưới liền nhau, ô trống để điền) và `==` hay `__` có khoảng trắng hai bên (ví dụ `a == b`). Trong `bieu-thuc` của `cong-thuc`, `==`, `((`, `__` luôn là chữ thường của công thức; chỉ `{{số}}` có tác dụng.
- `{{…}}` chỉ chứa một số, dấu thập phân là **dấu chấm** trong kịch bản (`{{2.01}}`, `{{-40}}`, `{{1500}}`); trên hình số hiện kiểu Việt với dấu phẩy ("2,01"), giữ đúng số chữ số thập phân đã viết, không có dấu phân cách hàng nghìn. Chữ không phải số hay `{{` thiếu `}}` là lỗi `parse`.
- Không cần đánh dấu trong `loi` và `loi-giai`: công cụ bỏ mọi dấu nhấn trước khi đọc.
- Dùng tiết kiệm: 1–2 cụm cho ý quan trọng nhất của cảnh, `{{số}}` cho con số học sinh cần nhớ.

```
## Cảnh 2
loai: khai-niem
thuat-ngu: ((Chu kì)) T
dinh-nghia: Khoảng thời gian ==ngắn nhất== để con lắc thực hiện __một dao động toàn phần__, khoảng {{2.01}} giây với dây dài 1 m.
loi: Chu kì là khoảng thời gian ngắn nhất để con lắc thực hiện một dao động toàn phần. Với dây dài một mét, chu kì khoảng hai giây.
```

## Chuyển cảnh

Từ cảnh 2, nửa giây đầu mỗi cảnh chuyển từ khung cuối của cảnh trước sang cảnh mới. Khoá đầu `chuyen-canh` chọn kiểu cho cả video; trường `chuyen:` trong một cảnh ghi đè kiểu của riêng cảnh đó.

| Giá trị | Cách chuyển |
|---|---|
| `lau-bang` | mặc định: bàn tay cầm giẻ lau sạch bảng cũ |
| `lat-trang` | trang cũ lật sang trái như trang sách |
| `truot` | trang cũ trượt ra bên trái, trang mới trượt vào từ bên phải |
| `phong` | phóng xuyên qua trang cũ, có một chớp sáng trắng ở giữa |
| `mo-man` | trang cũ tách làm hai nửa kéo sang hai bên như mở màn |
| `xe-giay` | mép giấy xé quét từ trái sang phải; mặc định khi `phong-cach: cat-dan` không ghi `chuyen-canh` |
| `khong` | không chuyển, cảnh mới hiện ngay |
| `luan-phien` | chỉ dùng ở khoá đầu: xoay vòng từ cảnh 2 theo thứ tự `lau-bang`, `lat-trang`, `truot`, `phong`, `mo-man`, rồi lặp lại |

- `chuyen:` nhận sáu kiểu trên hoặc `khong`, không nhận `luan-phien`. Cảnh 1 mở đầu video nên không có `chuyen:`; ghi vào cảnh 1 là lỗi `parse`.
- Chỉ `lau-bang` có bàn tay trong lúc chuyển; năm kiểu kia ẩn bàn tay, bút vào sau khi chuyển xong.
- Nên dùng `luan-phien` cho video nhiều cảnh, hoặc giữ một kiểu và dùng `chuyen:` để đánh dấu lúc sang phần mới (ví dụ `chuyen: lat-trang` trước cảnh câu hỏi).

## Tiêu đề

Mã loại: `tieu-de`.

| Trường | Bắt buộc | Giới hạn |
|---|---|---|
| `chu` | có | 90 ký tự |
| `phu` | không | 90 ký tự |
| `hinh` | không | tên biểu tượng `tabler-outline` |
| `anh` | không | tên file trong `anh/` |
| `nguon` | không | dòng nguồn của ảnh ở `anh`; chỉ ghi khi cảnh có `anh` |
| `the` | không | thẻ thông tin `<nhãn> \| <giá trị> \| <chú thích>`: nhãn 24, giá trị 16 (nhận số chạy `{{…}}`), chú thích 60 ký tự (bỏ trống được) |
| `tai-lieu` | không | dòng tài liệu tham khảo, 90 ký tự; tự thêm "Nguồn: " nếu chưa ghi |

Cách hiện: chữ lớn hiện ra giữa khung, dòng phụ hiện bên dưới. Với `chu-dong: co` (mặc định) chữ lớn nảy vào từng chữ cái, không có bàn tay; với `chu-dong: khong` chữ lớn được bút viết ra như các chữ khác. Dùng cho cảnh mở đầu hoặc mở một phần mới.

```
## Cảnh 1
loai: tieu-de
chu: Con lắc đơn và chu kì dao động
phu: Vật lí 11
loi: Hôm nay chúng ta tìm hiểu chu kì của con lắc đơn phụ thuộc vào yếu tố nào.
```

## Khái niệm

Mã loại: `khai-niem`.

| Trường | Bắt buộc | Giới hạn |
|---|---|---|
| `thuat-ngu` | có | 60 ký tự |
| `dinh-nghia` | có | 220 ký tự |
| `hinh` | không | tên biểu tượng `tabler-outline` |
| `anh` | không | tên file trong `anh/` |
| `nguon` | không | dòng nguồn của ảnh ở `anh`; chỉ ghi khi cảnh có `anh` |
| `the` | không | thẻ thông tin `<nhãn> \| <giá trị> \| <chú thích>`: nhãn 24, giá trị 16 (nhận số chạy `{{…}}`), chú thích 60 ký tự (bỏ trống được) |
| `tai-lieu` | không | dòng tài liệu tham khảo, 90 ký tự; tự thêm "Nguồn: " nếu chưa ghi |

Cách hiện: khung được vẽ nét, thuật ngữ rồi định nghĩa được viết vào trong khung.

```
## Cảnh 2
loai: khai-niem
thuat-ngu: Chu kì T
dinh-nghia: Khoảng thời gian ngắn nhất để con lắc thực hiện một dao động toàn phần, đo bằng giây.
loi: Chu kì là khoảng thời gian ngắn nhất để con lắc thực hiện một dao động toàn phần.
```

## Công thức

Mã loại: `cong-thuc`.

| Trường | Bắt buộc | Giới hạn |
|---|---|---|
| `bieu-thuc` | có | 90 ký tự; tách tối đa 4 phần bằng ` \| ` (mỗi dấu tính là một khoảng trắng) |
| `giai-thich` | lặp 0–4 dòng | mỗi dòng 60 ký tự |
| `hinh` | không | tên biểu tượng `tabler-outline` |
| `anh` | không | tên file trong `anh/` |
| `nguon` | không | dòng nguồn của ảnh ở `anh`; chỉ ghi khi cảnh có `anh` |
| `the` | không | thẻ thông tin `<nhãn> \| <giá trị> \| <chú thích>`: nhãn 24, giá trị 16 (nhận số chạy `{{…}}`), chú thích 60 ký tự (bỏ trống được) |
| `tai-lieu` | không | dòng tài liệu tham khảo, 90 ký tự; tự thêm "Nguồn: " nếu chưa ghi |

Cách hiện: biểu thức được viết dần, các dòng giải thích hiện lần lượt theo từng câu của lời. Mỗi phần của biểu thức (cả biểu thức khi không tách) là một khối không bao giờ ngắt dòng giữa chừng; dòng chỉ xuống ở chỗ giữa hai phần. Phần rộng hơn khung thì chữ nhỏ dần tới 70 %; vẫn rộng thì công cụ báo lỗi `canh` "phần công thức … quá dài cho khổ này": tách thành nhiều phần bằng ` | ` hoặc rút gọn.

Công thức hiện từng phần: tách `bieu-thuc` bằng ` | ` (gạch đứng có khoảng trắng hai bên), ví dụ `bieu-thuc: T = 2π√(l/g) | = 2π√(1/9,8) | ≈ {{2.01}} s`. Phần thứ k được viết nối tiếp trên cùng dòng khi câu thứ k của `loi` bắt đầu; dòng giải thích thứ k khi đó hiện ở câu (số phần + k). Không có ` | ` thì như cũ; `|x|` (không có khoảng trắng hai bên) vẫn là chữ thường. Phần trống, quá 4 phần, hoặc `**`, `~`, `^`, `{{…}}` mở ở phần này đóng ở phần khác là lỗi `parse`. Trong `bieu-thuc`, `==`, `((`, `__` là chữ của công thức, không phải dấu nhấn; dấu nhấn dùng được ở `giai-thich`.

```
## Cảnh 3
loai: cong-thuc
bieu-thuc: T = 2π√(l/g)
giai-thich: l là chiều dài dây, đơn vị mét
giai-thich: g là gia tốc trọng trường, khoảng 9,8 m/s^2^
loi: Chu kì bằng hai pi nhân căn của l chia g. Chữ l là chiều dài dây. Chữ g là gia tốc trọng trường.
```

Cùng công thức, hiện từng phần (ba phần ứng với ba câu đầu, rồi dòng giải thích ứng với câu thứ tư):

```
## Cảnh 3
loai: cong-thuc
bieu-thuc: T = 2π√(l/g) | = 2π√(1/9,8) | ≈ {{2.01}} s
giai-thich: __l__ là chiều dài dây, đơn vị mét
loi: Chu kì bằng hai pi căn l chia g. Thay dây dài một mét. Được khoảng hai giây. Chữ l là chiều dài dây.
```

## Ý từng ý

Mã loại: `y-tung-y`.

| Trường | Bắt buộc | Giới hạn |
|---|---|---|
| `tieu-de` | có | 90 ký tự |
| `y` | lặp 1–6 dòng | mỗi ý 60 ký tự |
| `hinh` | không | tên biểu tượng `tabler-outline` |
| `anh` | không | tên file trong `anh/` |
| `nguon` | không | dòng nguồn của ảnh ở `anh`; chỉ ghi khi cảnh có `anh` |
| `the` | không | thẻ thông tin `<nhãn> \| <giá trị> \| <chú thích>`: nhãn 24, giá trị 16 (nhận số chạy `{{…}}`), chú thích 60 ký tự (bỏ trống được) |
| `tai-lieu` | không | dòng tài liệu tham khảo, 90 ký tự; tự thêm "Nguồn: " nếu chưa ghi |

Cách hiện: tiêu đề viết trước, mỗi ý được viết ra khi lời nói tới.

```
## Cảnh 4
loai: y-tung-y
tieu-de: Phản ứng trao đổi ion xảy ra khi
y: Tạo thành chất kết tủa
y: Tạo thành chất khí
y: Tạo thành chất điện li yếu
loi: Thứ nhất, sản phẩm có chất kết tủa. Thứ hai, sản phẩm có chất khí. Thứ ba, sản phẩm có chất điện li yếu.
```

## Quy trình

Mã loại: `quy-trinh`.

| Trường | Bắt buộc | Giới hạn |
|---|---|---|
| `tieu-de` | có | 90 ký tự |
| `buoc` | lặp 2–5 dòng | mỗi bước 50 ký tự |

Cách hiện: các bước và mũi tên nối được vẽ nối tiếp nhau.

```
## Cảnh 5
loai: quy-trinh
tieu-de: Cách đo chu kì
buoc: Treo quả nặng vào dây
buoc: Kéo lệch một góc nhỏ rồi thả
buoc: Đo thời gian 10 dao động
loi: Bước một, treo quả nặng vào dây. Bước hai, kéo lệch một góc nhỏ rồi thả. Bước ba, đo thời gian mười dao động rồi chia cho mười.
```

## So sánh

Mã loại: `so-sanh`.

| Trường | Bắt buộc | Giới hạn |
|---|---|---|
| `tieu-de` | có | 90 ký tự |
| `trai`, `phai` | có | tên cột, mỗi tên 24 ký tự |
| `y-trai` | lặp 1–4 dòng | mỗi ý 60 ký tự |
| `y-phai` | lặp 1–4 dòng | mỗi ý 60 ký tự |

Cách hiện: hai cột được viết lần lượt, cột trái trước rồi cột phải; các ý hiện theo thứ tự câu của lời (hết ý cột trái mới tới ý cột phải).

```
## Cảnh 6
loai: so-sanh
tieu-de: Yếu tố nào ảnh hưởng đến chu kì
trai: Có ảnh hưởng
phai: Không ảnh hưởng
y-trai: Chiều dài dây
y-trai: Gia tốc trọng trường
y-phai: Khối lượng quả nặng
loi: Chiều dài dây ảnh hưởng đến chu kì. Gia tốc trọng trường cũng vậy. Còn khối lượng quả nặng thì không.
```

## Đồ thị

Mã loại: `do-thi`.

| Trường | Bắt buộc | Giới hạn |
|---|---|---|
| `tieu-de` | có | 90 ký tự |
| `truc-ngang`, `truc-doc` | có | tên trục, mỗi tên 40 ký tự |
| `diem` | lặp 2–12 dòng | dạng `x, y`, hai số, dấu thập phân là dấu chấm |

Cách hiện: hai trục được vẽ trước, rồi từng điểm hiện dần và được nối thành đường.

```
## Cảnh 7
loai: do-thi
tieu-de: Chu kì theo chiều dài dây
truc-ngang: Chiều dài l (m)
truc-doc: Chu kì T (s)
diem: 0.25, 1.0
diem: 0.5, 1.42
diem: 1.0, 2.01
diem: 2.0, 2.84
loi: Khi chiều dài tăng từ một phần tư mét đến hai mét, chu kì tăng từ một giây đến gần ba giây.
```

## Thí nghiệm ảo

Mã loại: `thi-nghiem`.

| Trường | Bắt buộc | Giới hạn |
|---|---|---|
| `mau` | có | mã một trong tám mẫu dưới đây |
| `do` | không | tối đa 3 mã đại lượng đo, cách nhau bằng dấu phẩy; không ghi dòng `do` thì hiện hai đại lượng đầu của mẫu |
| `tham-so` | lặp | dạng `<giây> <mã> <giá trị>`, tối đa 3 mã tham số khác nhau |

Tám mã mẫu:

| Môn | Mã | Thí nghiệm |
|---|---|---|
| Vật lí | `li-nem-xien` | Chuyển động ném xiên |
| Vật lí | `li-con-lac-don` | Con lắc đơn |
| Vật lí | `li-mach-ohm` | Đoạn mạch nối tiếp và song song |
| Hoá học | `hoa-chuan-do` | Chuẩn độ acid – base |
| Hoá học | `hoa-can-bang-no2` | Cân bằng N~2~O~4~ ⇌ 2NO~2~ |
| Hoá học | `hoa-toc-do` | Tốc độ phản ứng |
| Toán | `toan-ham-so` | Khảo sát hàm số |
| Toán | `toan-xac-suat` | Xác suất thực nghiệm |

Mã tham số, khoảng cho phép và mã đại lượng đo của từng mẫu nằm ở `docs/vi/tro-ly/mo-hinh-thi-nghiem.md` (mục "Danh mục mẫu"). Video chỉ dùng mẫu có sẵn, không dùng `mau: moi`.

Cách dùng `tham-so: <giây> <mã> <giá trị>`:

- `<giây>` tính từ đầu cảnh. Giá trị của một tham số tại mỗi thời điểm là nội suy tuyến tính giữa hai mốc liền kề của chính tham số đó.
- Trước mốc đầu, tham số giữ giá trị mặc định của mẫu; sau mốc cuối, giữ giá trị của mốc cuối. Tham số không có dòng nào thì giữ mặc định suốt cảnh.
- Giá trị phải nằm trong khoảng cho phép của mẫu (sai là lỗi `parse` nêu đúng dòng). Chỉ dùng được tham số dạng số; tham số lựa chọn (ví dụ `loai-acid`, `kieu-mac`) giữ mặc định.
- Mốc giây vượt thời lượng cảnh là lỗi `canh`. Thời lượng cảnh xấp xỉ thời gian đọc lời cộng khoảng 1,3 giây, nên đặt mốc cuối trước khi lời kết thúc.
- Hai mẫu chạy một lần là `li-nem-xien` và `hoa-toc-do`: mỗi mốc `tham-so` (của bất kỳ tham số nào) làm chuyển động chạy lại từ đầu. Nên đặt mỗi mốc sau khi chuyển động trước đã dừng, để học sinh xem trọn một lần rồi mới thấy lần mới.

Cách hiện: hình vẽ của mẫu chạy trong khung, tham số đổi dần theo các mốc, các đại lượng trong `do` hiện thành số bên cạnh và luôn khớp công thức của mẫu.

```
## Cảnh 8
loai: thi-nghiem
mau: li-con-lac-don
tham-so: 0 chieu-dai 0.4
tham-so: 6 chieu-dai 1.6
do: chu-ki
loi: Hãy quan sát. Khi ta tăng chiều dài dây, chu kì dao động tăng theo.
```

## Minh hoạ

Mã loại: `minh-hoa`.

| Trường | Bắt buộc | Giới hạn |
|---|---|---|
| `tieu-de` | có | 90 ký tự |
| `hinh` | lặp 1–3 dòng | dạng `tên \| nhãn`, tên là biểu tượng `tabler-outline`, nhãn tối đa 30 ký tự |

Cách hiện: tiêu đề viết trước; hình thứ k được vẽ dần từng nét tại mốc câu thứ k của `loi`, nhãn hiện ngay sau khi hình vẽ xong. Các hình dàn đều theo chiều ngang. Viết lời có đúng một câu cho mỗi hình, theo đúng thứ tự. Thiếu dấu `|` hoặc thiếu nhãn là lỗi `canh`.

```
## Cảnh 9
loai: minh-hoa
tieu-de: Dụng cụ đo chu kì
hinh: clock | Đồng hồ bấm giây
hinh: ruler-measure | Thước đo chiều dài
hinh: weight | Quả nặng
loi: Ta cần đồng hồ bấm giây. Thước đo chiều dài dây. Và một quả nặng.
```

## Ảnh thật

Mã loại: `anh`.

| Trường | Bắt buộc | Giới hạn |
|---|---|---|
| `anh` | có | tên file `.jpg`/`.jpeg`/`.png`/`.webp` trong `anh/`, tối đa 8 MB |
| `chu-thich` | có | 90 ký tự |
| `nguon` | không | dòng ghi nguồn; không ghi thì lấy từ bản ghi cùng tên trong `anh/image_sources.json` (tải bằng `image_search.py`); không có nguồn nào là lỗi `canh` |

Cách hiện: ảnh hiện trong khung vẽ tay, vừa khung và không méo (ảnh dọc hay ngang đều được; ảnh điện thoại chụp dọc hiện đúng chiều theo thông tin xoay trong file), phóng hoặc lướt chậm suốt cảnh; dòng nguồn nhỏ ở góc dưới bên phải, trong khung ảnh; chú thích được viết dưới ảnh, chữ dài thì cỡ chữ nhỏ lại. Ảnh ở cột phải của ba loại `khai-niem`, `cong-thuc`, `y-tung-y` thì dòng nguồn nằm ngay dưới khung ảnh, trong bề rộng cột; ảnh ở cảnh `tieu-de` thì dòng nguồn nằm bên phải khung ảnh. Dòng nguồn không bao giờ đè lên chữ và luôn nằm trên vùng phụ đề; dòng nguồn quá dài thì công cụ báo lỗi tràn khung ở mục `nguon`.

```
## Cảnh 10
loai: anh
anh: con-lac-foucault.jpg
chu-thich: Con lắc Foucault ở Paris
loi: Đây là con lắc Foucault, dài 67 mét, dao động rất chậm.
```

Trường `nguon` có ở loại cảnh `anh` và ở bốn loại cảnh kia khi cảnh có `anh:`. Không ghi `nguon:` thì công cụ lấy nguồn từ `anh/image_sources.json` (bỏ mọi địa chỉ web trong bản ghi); file đó sai cấu trúc là lỗi `canh`.

Ảnh thầy cô tự chụp: chép file vào `anh/`, rồi ghi `nguon:` trong cảnh có ảnh đó, ví dụ `nguon: Ảnh: cô Lan chụp`. Cũng được: thêm vào danh sách `items` của `anh/image_sources.json` (chưa có file thì tạo) một bản ghi dạng `{"filename": "<tên file>", "author": "cô Lan", "license_name": "Ảnh tự chụp", "provider": "Trường THPT ..."}`.

Tải ảnh từ kho ảnh mở (Openverse, Wikimedia, không cần khoá), mỗi ảnh một lệnh, sau khi thầy cô đã duyệt danh sách cảnh:

```
python skills\ppt-master\scripts\image_search.py "Foucault pendulum" --filename con-lac-foucault.jpg --orientation landscape -o projects\_video\<tên_video>\anh
```

- Từ khoá viết bằng tiếng Anh, cụ thể (tên sự vật, địa danh); `--orientation` là `landscape` cho cảnh `anh`; ảnh ở cột phải dùng `portrait` hoặc `square`.
- Lệnh ghi ảnh vào `anh/` và thêm bản ghi tác giả, giấy phép vào `anh/image_sources.json`; công cụ dựng lấy dòng nguồn từ đó nên không cần ghi `nguon:`.
- Lệnh còn ghi một bản thu nhỏ để xem vào `anh/.review/<tên>.jpg` (cạnh dài 1024 px). Mở bản này xem ảnh có đúng nội dung không; sai thì tải lại với từ khoá khác.
- Ảnh gốc nặng quá 8 MB là lỗi `canh`. Khi đó chép `anh/.review/<tên>.jpg` đè lên file gốc cùng tên (tên gốc có đuôi `.jpg`); tên gốc có đuôi khác thì chép bản thu nhỏ thành `anh/<tên>.jpg`, sửa dòng `anh:` theo tên mới, và thêm vào `items` của `anh/image_sources.json` một bản ghi chép nguyên bản ghi của file gốc, chỉ đổi `filename` thành tên mới. Không có bản `.review` thì chọn ảnh khác.
- Công cụ dựng không bao giờ tự lên mạng tìm ảnh; không chèn địa chỉ web vào `anh:` hay `nguon:`.

## Biểu đồ

Mã loại: `bieu-do`.

| Trường | Bắt buộc | Giới hạn |
|---|---|---|
| `tieu-de` | có | 90 ký tự |
| `kieu` | có | `cot` (cột), `duong` (đường) hoặc `tron` (hình tròn) |
| `du-lieu` | lặp 2–8 dòng | dạng `<nhãn> \| <số>`; nhãn 16 ký tự; số dấu thập phân là dấu chấm, tối đa 10 ký tự; `tron` chỉ nhận số dương |
| `don-vi` | không | 12 ký tự; không dùng với `tron` |
| `truc-ngang`, `truc-doc` | không | tên trục, mỗi tên 40 ký tự; không dùng với `tron` |

Cách hiện: trục và thang số tròn (bước 1, 2, 5 × 10ⁿ, 4–6 vạch) vẽ trước cùng nhãn các mục. Mục thứ k hiện khi câu thứ k của `loi` bắt đầu: cột mọc từ trục (số âm mọc xuống dưới trục), điểm và đoạn nối của đường vẽ dần, lát tròn mở dần theo góc; số trên cột, trên điểm, phần trăm cạnh lát chạy từ 0 tới giá trị thật và hiện kiểu Việt (dấu phẩy thập phân). Máy quay giữ toàn cảnh biểu đồ để học sinh so sánh được các mục.

- Viết mỗi mục ứng với đúng một câu của `loi`, theo đúng thứ tự; lời ít câu hơn số mục thì các mục mọc đều theo thời lượng giọng.
- Nhãn là chữ, viết dấu phẩy thập phân tuỳ ý (`0,25 m`); số sau `|` luôn dùng dấu chấm. Số chạy trên hình giữ đúng số chữ số thập phân đã viết (`1.0` hiện "1,0").
- `cot`: số âm được, cột âm mọc xuống dưới trục. `duong`: hợp với số liệu thay đổi theo thời gian hay theo một đại lượng. `tron`: chỉ số dương, công cụ tự tính phần trăm; không ghi `don-vi`, `truc-ngang`, `truc-doc` (ghi là lỗi `parse`).
- Số liệu chênh lệch rất lớn (1 và 100000) vẫn vẽ được nhưng cột nhỏ gần như phẳng; nên đổi đơn vị hoặc tách biểu đồ.

```
## Cảnh 11
loai: bieu-do
tieu-de: Chu kì theo chiều dài dây
kieu: cot
don-vi: s
truc-ngang: Chiều dài dây
truc-doc: Chu kì
du-lieu: 0,25 m | 1.0
du-lieu: 0,5 m | 1.42
du-lieu: 1 m | 2.01
du-lieu: 2 m | 2.84
loi: Dây dài một phần tư mét, chu kì một giây. Dây nửa mét, chu kì một phẩy bốn hai giây. Dây một mét, chu kì hai giây. Dây hai mét, chu kì gần ba giây.
```

Biểu đồ tròn:

```
## Cảnh 11
loai: bieu-do
tieu-de: Thành phần không khí theo thể tích
kieu: tron
du-lieu: Nitrogen | 78
du-lieu: Oxygen | 21
du-lieu: Khí khác | 1
loi: Nitrogen chiếm khoảng bảy mươi tám phần trăm. Oxygen chiếm khoảng hai mươi mốt phần trăm. Các khí khác chỉ khoảng một phần trăm.
```

## Sơ đồ tư duy

Mã loại: `so-do`.

| Trường | Bắt buộc | Giới hạn |
|---|---|---|
| `trung-tam` | có | 30 ký tự |
| `nhanh` | lặp 2–6 dòng | mỗi nhánh 40 ký tự |
| `hinh` | không | tên biểu tượng `tabler-outline`, vẽ trong nút trung tâm |

Cách hiện: nút trung tâm vẽ trước; nhánh thứ k (đường cong vẽ tay, mỗi nhánh một màu, tới ô nhãn) hiện khi câu thứ k của `loi` bắt đầu. Các nhánh rải quanh nút theo góc cố định theo số nhánh, nhánh đầu ở phía trên bên phải rồi đi theo chiều kim đồng hồ. Máy quay giữ toàn cảnh sơ đồ. Hợp với cảnh tóm tắt cuối bài; viết mỗi nhánh ứng với đúng một câu của `loi`. Nhánh dùng được dấu nhấn.

```
## Cảnh 12
loai: so-do
trung-tam: Chu kì con lắc đơn
hinh: clock
nhanh: Tăng khi dây ==dài hơn==
nhanh: Giảm khi g lớn hơn
nhanh: Không đổi theo khối lượng
loi: Chu kì tăng khi dây dài hơn. Chu kì giảm khi gia tốc trọng trường lớn hơn. Khối lượng quả nặng không làm đổi chu kì.
```

## Dòng thời gian

Mã loại: `dong-thoi-gian`.

| Trường | Bắt buộc | Giới hạn |
|---|---|---|
| `tieu-de` | có | 90 ký tự |
| `moc` | lặp 2–6 dòng | dạng `<nhãn> \| <mô tả>`; nhãn 12 ký tự, mô tả 60 ký tự |

Cách hiện: trục ngang có mũi tên vẽ trước (0,6 giây); mốc thứ k (chấm, nhãn, rồi mô tả) hiện khi câu thứ k của `loi` bắt đầu. Đến 4 mốc: nhãn trên trục, mô tả dưới trục; từ 5 mốc: các mốc xen kẽ trên và dưới trục. Hợp với tiến trình lịch sử, các giai đoạn phát triển, các bước theo thời gian. Viết các mốc theo thứ tự thời gian, mỗi mốc ứng với đúng một câu của `loi`.

```
## Cảnh 13
loai: dong-thoi-gian
tieu-de: Lịch sử đo thời gian bằng con lắc
moc: 1583 | Galileo nhận ra chu kì con lắc gần như không đổi
moc: 1656 | Huygens chế tạo đồng hồ quả lắc đầu tiên
moc: 1851 | Foucault chứng minh Trái Đất tự quay
loi: Năm 1583, Galileo quan sát chiếc đèn chùm đung đưa. Năm 1656, Huygens làm ra đồng hồ quả lắc. Năm 1851, Foucault dùng con lắc chứng minh Trái Đất tự quay.
```

## Câu hỏi nhanh

Mã loại: `cau-hoi`.

| Trường | Bắt buộc | Giới hạn |
|---|---|---|
| `cau-hoi` | có | 160 ký tự |
| `lua-chon` | lặp 2–4 dòng | mỗi lựa chọn 60 ký tự; tự đánh A, B, C, D theo thứ tự |
| `dap-an` | có | một chữ cái trong số lựa chọn |
| `giai-thich` | có | 180 ký tự |
| `cho` | không | số giây đếm ngược, số nguyên 3–10, mặc định 5 |
| `loi-giai` | có | lời đọc sau khi hiện đáp án |

Cách hiện: bút viết câu hỏi rồi từng lựa chọn theo câu của `loi`; hết lời thì đồng hồ vòng tròn đếm ngược `cho` giây (số giây lớn ở giữa, không có bàn tay, không có phụ đề) để học sinh tự nghĩ; rồi lựa chọn đúng có viền xanh và dấu ✓, các lựa chọn khác mờ đi, giọng đọc `loi-giai` và bút viết `giai-thich` màu xanh. Máy quay không phóng vào từng lựa chọn nên học sinh luôn thấy cả câu hỏi.

- `loi` đọc câu hỏi và các lựa chọn: câu đầu là câu hỏi, mỗi câu sau là một lựa chọn theo thứ tự ("A, tăng gấp bốn. B, tăng gấp hai."). Có thể thêm một câu dẫn trước câu hỏi ("Câu hỏi nhanh."); khi đó mỗi mục hiện sớm hơn một câu, và vẫn được viết xong trước lúc đếm ngược.
- `loi-giai` là lời đọc sau khi hiện đáp án, nên mở đầu bằng đáp án ("Đáp án B.") rồi giải thích ngắn. Dấu nhấn trong `giai-thich` nổ theo giọng của `loi-giai`.
- Thời lượng cảnh = 1 giây dẫn đầu + giọng `loi` + `cho` giây + 0,4 giây + giọng `loi-giai` + 0,6 giây. Không có mốc `tham-so` hay trường thời gian nào khác.
- Giọng lời giải là file riêng `giong/canh-<số>-giai.mp3` (giọng máy tự tạo; thầy cô đặt sẵn thì được dùng, không bị ghi đè). Tạo giọng lời giải lỗi thì báo `giong` nêu đúng tên file đó.
- `dap-an` viết hoa hay thường đều được; chữ cái ngoài số lựa chọn (ví dụ `D` khi chỉ có ba lựa chọn) là lỗi `parse`. `cho` là số nguyên, ngoài 3–10 là lỗi `parse`.
- Công cụ chỉ kiểm đáp án là một trong các lựa chọn; nội dung câu hỏi và đáp án đúng hay sai do thầy cô duyệt. Nên có một cảnh câu hỏi ở gần cuối video, sau phần tóm tắt.

```
## Cảnh 14
loai: cau-hoi
chuyen: lat-trang
cau-hoi: Dây treo dài gấp bốn thì chu kì con lắc đơn thay đổi thế nào?
lua-chon: Tăng gấp bốn
lua-chon: Tăng gấp hai
lua-chon: Không đổi
dap-an: B
giai-thich: T tỉ lệ với ((căn bậc hai)) của l nên l gấp bốn thì T gấp hai.
loi-giai: Đáp án B. Chu kì tỉ lệ với căn bậc hai của chiều dài, nên chu kì tăng gấp hai.
loi: Dây treo dài gấp bốn thì chu kì thay đổi thế nào? A, tăng gấp bốn. B, tăng gấp hai. C, không đổi.
```

## Kể chuyện

Mã loại: `ke-chuyen`.

| Trường | Bắt buộc | Giới hạn |
|---|---|---|
| `tieu-de` | có | 36 ký tự (khổ dọc 28); hiện chữ hoa |
| `nen` | có | `mau/<tên>`, tên file ảnh trong `anh/`, `ve: <mô tả>` (tối đa 200 ký tự) hoặc `nhu-canh <số>` |
| `tu-the` | không | tư thế nhân vật; không ghi thì nhân vật đứng (`dung`) |
| `vi-tri` | không | `trai`, `giua` hoặc `phai`; mặc định cảnh lẻ `trai`, cảnh chẵn `phai` |
| `the` | không | thẻ thông tin như cảnh `tieu-de` |
| `tai-lieu` | không | dòng tài liệu như cảnh `tieu-de` |

Cách hiện: nền phủ kín khung và phóng chậm suốt cảnh; nhân vật dẫn chuyện (khi có khoá đầu `nhan-vat`) bật vào ở 0,2 giây; tiêu đề lớn ở giữa phía trên vào ở 0,4 giây (`viet-tay`: chữ vàng viền đen; `cat-dan`: nhãn trên băng dính). `loi` chỉ đọc và hiện ở phụ đề, không viết lên hình. Máy quay không phóng trong cảnh này.

- `nen: mau/<tên>`: một trong tám nền vẽ sẵn `giay`, `bau-troi`, `vu-tru`, `lop-hoc`, `phong-thi-nghiem`, `thanh-pho`, `dong-que`, `vong-tron`. Tên sai là lỗi `parse`, gợi ý tên gần nhất.
- `nen: <file>`: ảnh thật trong `anh/`, cần nguồn như trường `anh` (bản ghi trong `anh/image_sources.json`); dòng nguồn hiện ở góc phải dưới.
- `nen: ve: <mô tả>`: nền do AI vẽ, file `anh/ai/nen-<số cảnh>.jpg` (tạo bằng `tools/vi/anh_ai.py`). Video có ảnh AI hiện dòng "Hình minh hoạ tạo bằng AI (<mô hình>)" trong 4 giây cuối. Thiếu file AI thì lỗi `canh` liệt kê mọi file còn thiếu.
- `nen: nhu-canh <số>`: dùng lại nền của một cảnh `ke-chuyen` đứng trước. Trỏ tới chính nó, cảnh sau hay cảnh không phải `ke-chuyen` là lỗi `parse`.

```
## Cảnh 15
loai: ke-chuyen
tieu-de: Galileo và chiếc đèn chùm
nen: mau/lop-hoc
loi: Năm 1583, trong nhà thờ Pisa, Galileo nhìn chiếc đèn chùm đung đưa và đếm nhịp bằng mạch đập của mình.
```

## Bảng tra biểu tượng

Tên ở cột cuối là tên file (bỏ đuôi `.svg`) trong `skills/ppt-master/templates/icons/tabler-outline/`; viết đúng tên đó sau `hinh:`. Chọn hình nói đúng sự vật trong lời, không chọn hình chỉ để trang trí. Khái niệm không có trong bảng thì tìm thêm theo từ khoá tiếng Anh, ví dụ:

```
rg --files skills/ppt-master/templates/icons/tabler-outline -g "*flask*"
```

| Môn | Khái niệm | Tên |
|---|---|---|
| Toán | hàm số | `math-function` |
| Toán | đồ thị đường | `chart-line` |
| Toán | biểu đồ cột | `chart-bar` |
| Toán | biểu đồ tròn, tỉ lệ | `chart-pie` |
| Toán | tập điểm, số liệu | `chart-dots` |
| Toán | phần trăm | `percentage` |
| Toán | máy tính cầm tay | `calculator` |
| Toán | tích phân | `math-integral` |
| Toán | số pi | `math-pi` |
| Toán | căn bậc hai | `square-root` |
| Toán | vô cực | `infinity` |
| Toán | tổng, dấu sigma | `sum` |
| Toán | phép chia | `divide` |
| Toán | phân số | `math-x-divide-y` |
| Toán | lũy thừa, số mũ | `superscript` |
| Toán | tam giác | `triangle` |
| Toán | góc | `angle` |
| Toán | hình vuông | `square` |
| Toán | đường tròn | `circle` |
| Toán | khối lập phương | `cube` |
| Toán | hình cầu | `sphere` |
| Toán | hình trụ | `cylinder` |
| Toán | hình nón | `cone` |
| Toán | vectơ | `vector` |
| Toán | trục hoành | `axis-x` |
| Toán | trục tung | `axis-y` |
| Toán | xác suất, xúc xắc | `dice-5` |
| Toán | thống kê, kiểm đếm | `tallymarks` |
| Toán | thước kẻ | `ruler` |
| Vật lí | nguyên tử | `atom` |
| Vật lí | nam châm | `magnet` |
| Vật lí | điện, tia sét | `bolt` |
| Vật lí | pin, acquy | `battery` |
| Vật lí | bóng đèn, ý tưởng | `bulb` |
| Vật lí | phích cắm, nguồn điện | `plug` |
| Vật lí | sóng hình sin, dao động | `wave-sine` |
| Vật lí | sóng trên mặt nước | `ripple` |
| Vật lí | âm thanh, loa | `volume` |
| Vật lí | tai, nghe | `ear` |
| Vật lí | mắt, nhìn | `eye` |
| Vật lí | lăng kính | `prism` |
| Vật lí | tán sắc, cầu vồng | `rainbow` |
| Vật lí | nhiệt kế | `thermometer` |
| Vật lí | nhiệt độ | `temperature` |
| Vật lí | đồng hồ | `clock` |
| Vật lí | đồng hồ bấm giây | `stopwatch` |
| Vật lí | đồng hồ cát | `hourglass` |
| Vật lí | quả nặng, khối lượng | `weight` |
| Vật lí | cân, cân bằng | `scale` |
| Vật lí | thước đo chiều dài | `ruler-measure` |
| Vật lí | trọng lực, rơi xuống | `arrow-big-down-lines` |
| Vật lí | chuyển động nảy | `bounce-right` |
| Vật lí | áp kế, đồng hồ đo | `gauge` |
| Vật lí | tên lửa | `rocket` |
| Vật lí | hành tinh | `planet` |
| Vật lí | Mặt Trời | `sun` |
| Vật lí | Mặt Trăng | `moon` |
| Vật lí | vệ tinh | `satellite` |
| Vật lí | kính thiên văn | `telescope` |
| Vật lí | phóng xạ | `radioactive` |
| Vật lí | sóng vô tuyến | `wifi` |
| Vật lí | ô tô | `car` |
| Vật lí | xe đạp | `bike` |
| Vật lí | thuyền buồm | `sailboat` |
| Hoá học | bình tam giác | `flask` |
| Hoá học | bình cầu | `flask-2` |
| Hoá học | ống nghiệm | `test-pipe` |
| Hoá học | ống nghiệm (kiểu 2) | `test-pipe-2` |
| Hoá học | ngọn lửa, đốt cháy | `flame` |
| Hoá học | giọt chất lỏng | `droplet` |
| Hoá học | nhiều giọt, dung dịch | `droplets` |
| Hoá học | lọc, phễu lọc | `filter` |
| Hoá học | chai hoá chất | `bottle` |
| Hoá học | muối | `salt` |
| Hoá học | mô hình nguyên tử | `atom-2` |
| Hoá học | bình xịt | `spray` |
| Hoá học | bình chữa cháy | `fire-extinguisher` |
| Hoá học | tái chế | `recycle` |
| Hoá học | nhà máy hoá chất | `building-factory` |
| Sinh học | tế bào | `cell` |
| Sinh học | ADN | `dna` |
| Sinh học | ADN (kiểu 2) | `dna-2` |
| Sinh học | kính hiển vi | `microscope` |
| Sinh học | lá cây | `leaf` |
| Sinh học | cây non, nảy mầm | `seedling` |
| Sinh học | cây | `plant` |
| Sinh học | cây gỗ | `tree` |
| Sinh học | rừng | `trees` |
| Sinh học | hoa | `flower` |
| Sinh học | xương rồng | `cactus` |
| Sinh học | tim | `heart` |
| Sinh học | nhịp tim | `heartbeat` |
| Sinh học | phổi | `lungs` |
| Sinh học | não | `brain` |
| Sinh học | xương | `bone` |
| Sinh học | răng | `dental` |
| Sinh học | virus | `virus` |
| Sinh học | côn trùng | `bug` |
| Sinh học | bướm | `butterfly` |
| Sinh học | cá | `fish` |
| Sinh học | chim, lông vũ | `feather` |
| Sinh học | động vật, dấu chân | `paw` |
| Sinh học | chó | `dog` |
| Sinh học | mèo | `cat` |
| Sinh học | nấm | `mushroom` |
| Sinh học | quả táo, trái cây | `apple` |
| Sinh học | trứng | `egg` |
| Sinh học | thuốc | `pill` |
| Sinh học | vắc xin | `vaccine` |
| Sinh học | sơ cứu | `first-aid-kit` |
| Địa lí | quả địa cầu | `globe` |
| Địa lí | thế giới | `world` |
| Địa lí | bản đồ | `map` |
| Địa lí | vị trí trên bản đồ | `map-pin` |
| Địa lí | toạ độ | `current-location` |
| Địa lí | la bàn, phương hướng | `compass` |
| Địa lí | núi | `mountain` |
| Địa lí | núi lửa | `volcano` |
| Địa lí | hải đăng, bờ biển | `building-lighthouse` |
| Địa lí | mây | `cloud` |
| Địa lí | mưa | `cloud-rain` |
| Địa lí | giông bão | `cloud-storm` |
| Địa lí | sương mù | `cloud-fog` |
| Địa lí | tuyết, băng giá | `snowflake` |
| Địa lí | gió | `wind` |
| Địa lí | lốc xoáy | `tornado` |
| Địa lí | bình minh | `sunrise` |
| Địa lí | hoàng hôn | `sunset` |
| Địa lí | mùa mưa | `umbrella` |
| Địa lí | nông nghiệp, máy kéo | `tractor` |
| Địa lí | lương thực, lúa | `wheat` |
| Địa lí | khu dân cư, đô thị | `building-community` |
| Địa lí | công nghiệp | `building-factory-2` |
| Chung | sách | `book` |
| Chung | nhiều sách, thư viện | `books` |
| Chung | vở ghi | `notebook` |
| Chung | bút chì | `pencil` |
| Chung | viết bài | `writing` |
| Chung | trường học | `school` |
| Chung | nhóm học sinh | `users` |
| Chung | một người | `user` |
| Chung | câu hỏi | `question-mark` |
| Chung | mục tiêu | `target` |
| Chung | danh sách việc | `clipboard-list` |
| Chung | kiểm tra từng mục | `list-check` |
| Chung | lịch | `calendar` |
| Chung | báo thức | `alarm` |
| Chung | cờ, đích đến | `flag` |
| Chung | cúp, thành tích | `trophy` |
| Chung | ghép hình, giải đố | `puzzle` |
| Chung | bài trình chiếu | `presentation` |
| Chung | trò chuyện, thảo luận | `message-circle` |
| Chung | tìm kiếm | `search` |
| Chung | thông tin | `info-circle` |
| Chung | cảnh báo, nguy hiểm | `alert-triangle` |
| Chung | đúng | `check` |
| Chung | sai | `x` |
| Chung | mũi tên, dẫn tới | `arrow-right` |
| Chung | chu trình, lặp lại | `refresh` |
| Chung | tăng trưởng | `trending-up` |
| Chung | nhà | `home` |

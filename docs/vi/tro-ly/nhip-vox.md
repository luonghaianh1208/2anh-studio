# Nhịp của video Vox: ngữ pháp và bảng tra

File dành cho AI. Đọc cùng `docs/vi/tro-ly/video-giai-thich.md` (cách viết kịch bản, ảnh, vòng tự kiểm). File này nói đủ cách viết một cảnh Vox: dòng `nhip`, các vật, bố cục và ô, tuỳ chọn, giới hạn, và ví dụ từng bố cục.

## Dòng nhịp

Một cảnh Vox gồm `bo-cuc`, `loi` và 1–6 dòng `nhip`. Mỗi nhịp là một vật hiện ra đúng lúc giọng đọc nói tới một cụm từ trong lời:

```
nhip: <cụm từ trong lời> | <vật>: <nội dung> | <ô> | <tuỳ chọn>
```

- Các phần cách nhau bằng ` | ` (gạch đứng có khoảng trắng hai bên).
- `<ô>` bỏ được: công cụ lấy ô trống kế tiếp của bố cục (mục "Bố cục và ô").
- `<tuỳ chọn>` bỏ được. Nhiều tuỳ chọn viết chung **một** phần, cách nhau bằng khoảng trắng: `| phai | khung duotone`. Bỏ ô mà vẫn có tuỳ chọn thì viết tuỳ chọn ngay sau vật: `| khung duotone`.
- Viết các nhịp theo đúng thứ tự cụm từ xuất hiện trong lời.

Ví dụ: `nhip: để mai tính | anh: ve: bàn tay cầm điện thoại, chụp từ trên xuống | trai`.

## Cụm từ và thời điểm

- Cụm từ là vài từ liền nhau chép từ `loi`. Công cụ so sau khi đưa về chữ thường, bỏ dấu câu, giữ dấu thanh: "Để mai tính," khớp với "để mai tính", nhưng "chu kì" không khớp "chu kỳ".
- Vật hiện khi giọng đọc tới **từ đầu** của cụm (theo mốc từng từ của giọng máy). Chọn cụm là từ gọi tên đúng thứ vật đó cho thấy.
- `@dau` thay cho cụm từ: vật hiện ngay khi vào cảnh, sau đoạn dẫn khoảng 1 giây. Dùng cho ảnh nền `nen` hay cho khung đầu tiên của video.
- Một cụm có mặt nhiều lần trong lời: mỗi nhịp lấy lần xuất hiện đầu tiên **sau** cụm của nhịp đứng trước. Hai nhịp dùng cùng cụm "không" thì nhịp sau gắn vào chữ "không" thứ hai.
- Giọng thu sẵn không có mốc từng từ: vật hiện theo mốc ước lượng, có thể lệch vài trăm mili giây (có cảnh báo).
- Lỗi `parse` kèm số dòng: cụm không có trong lời (thông báo in lại lời của cảnh), cụm nằm trước cụm của nhịp trước, cảnh không có nhịp nào.

## Vật

| Vật | Nội dung | Giới hạn | Kiểu vào |
|---|---|---|---|
| `anh` | `ve: <mô tả>` (AI vẽ), `tim: <từ khoá tiếng Anh>` (ảnh thật giấy phép mở) hoặc tên file trong `anh/` (`.jpg`, `.jpeg`, `.png`, `.webp`) | mô tả `ve:` tối đa 300 ký tự | trượt nhẹ lên kèm mờ dần (không nảy, không rung) |
| `the` | `<nhãn> \| <giá trị> \| <chú thích>`, chú thích bỏ được | nhãn 24, giá trị 16, chú thích 60 ký tự | trượt vào |
| `chu` | một dòng chữ lớn, ý chốt hay câu ngắn | 40 ký tự; tối đa 2 dòng `chu` mỗi cảnh | hiện từng từ |
| `nhan` | nhãn trên băng dính màu | 30 ký tự | dán |
| `dau` | con dấu, thường viết hoa | 16 ký tự | mờ dần, thu nhẹ về đúng cỡ (không rung) |
| `mui-ten` | `<ô> -> <ô>`, hai đầu là ô của bố cục, ví dụ `trai -> phai`; vẽ trên cả khung, không chiếm ô; bố cục `chong` không dùng được | | vẽ dần |
| `so` | một số chạy `{{số}}` kèm chữ trước hoặc sau, ví dụ `{{48}} giờ mỗi tuần` | 24 ký tự | chạy số từ 0 lên |
| `cot` | các cột `<nhãn> = <số><đơn vị>` cách nhau bằng `;`, ví dụ `2022 = 12; 2023 = 30,5; 2024 = 45%` | 2–5 cột; nhãn 14, đơn vị 6 ký tự; số không âm | cột mọc dần từng cột, số chạy |
| `chu-trinh` | các bước cách nhau bằng `;`, ví dụ `Bốc hơi; Ngưng tụ; Mưa; Thấm xuống đất` | 3–6 bước, mỗi bước 16 ký tự | bước hiện lần lượt, cung mũi tên vẽ nối, khép vòng |
| `moc` | các mốc `<mốc>: <nhãn>` cách nhau bằng `;`, ví dụ `1945: Độc lập; 1975: Thống nhất` | 2–5 mốc; mốc 10, nhãn 20 ký tự | trục vẽ dần, mốc hiện khi trục chạy tới |
| `thap` | các tầng từ đỉnh xuống đáy, cách nhau bằng `;`, ví dụ `Tự thể hiện; Tôn trọng; Xã hội; An toàn` | 3–5 tầng, mỗi tầng 24 ký tự | tầng hiện từ đáy lên đỉnh |

- Giới hạn đếm ký tự hiện ra. Vượt giới hạn là lỗi `parse` nêu đúng dòng.
- `so`: viết dấu chấm thập phân (`{{2.5}}`), video hiện dấu phẩy ("2,5"). Cảnh có `so` hay có số liệu trong lời phải có dòng `nguon:` của cảnh.
- `the` hợp với một con số hay một sự thật có ba tầng: tên, giá trị, ghi chú.
- `cot`, `chu-trinh`, `moc`, `thap` cần một ô rộng: `giua` của `mot`, một bên của `hai-ben`, hoặc ô của `toan-canh`; không dùng trong `chong`. Số liệu của `cot` cũng phải có `nguon:` của cảnh.
- `anh: ve:` là ảnh AI, kiểu cắt nền (một vật trên nền giấy, viền giấy xé trắng) trừ khi có tuỳ chọn `khung` hay ở ô `nen`. Mô tả chỉ tả nội dung, phong cách do `phong-anh` thêm; `@nhan-vat` trong mô tả là nhân vật chính của khoá đầu `nhan-vat-chinh`. Ảnh thật `tim:` và ảnh người dùng gửi luôn ở dạng khung.

## Bố cục và ô

| Bố cục | Ô ngang | Ô dọc | Hợp với |
|---|---|---|---|
| `mot` | `giua`, `tren`, `duoi` | `giua`, `tren`, `duoi` | một vật, một khái niệm, một câu chốt |
| `hai-ben` | `trai`, `phai`, `giua` | `tren`, `duoi`, `giua` | so sánh, đối lập, trước và sau |
| `dan-hang` | `1`, `2`, `3`, `4` (xếp ngang) | `1`, `2`, `3`, `4` (xếp dọc) | danh sách, các bước |
| `chong` | không có ô: tự xếp lệch nhau theo cảnh, tối đa 5 vật | như ngang | nhiều yếu tố rối rắm cùng lúc |
| `toan-canh` | `nen` (ảnh phủ kín khung), `giua`, `duoi` | như ngang | nơi chốn, bối cảnh, một khoảnh khắc |
| `dung-canh` | ảnh: `hau-canh`, `phu-2`, `phu`, `chinh`, `tien-canh`; chữ: `tren`, `giua` | như ngang | cảnh kể chuyện có nhân vật: một bức tranh giấy cắt nhiều lớp |

- `mot`: `giua` là ô lớn cho ảnh; `tren` và `duoi` là dải hẹp, dành cho `chu`, `nhan`, `dau`, `so`.
- `hai-ben`: ô `giua` nằm đè lên mép trong của hai bên; chỉ đặt ở đó một `dau` hoặc `nhan` ngắn, không đặt ảnh hay `the`. Con dấu, nhãn được dán đè lên ảnh hai bên (công cụ không tính là đè nhau), nhưng càng dài càng che ảnh: giữ khoảng 8 ký tự (`IM LẶNG`); hai bên là ảnh `khung` thì nên ngắn hơn, như `VS`.
- `dan-hang`: mỗi ô hẹp (ngang khoảng một phần tư khung), hợp với `the`, `nhan`, ảnh cắt nền; chữ dài thì dễ tràn.
- `dung-canh`: mỗi nhịp ghi rõ ô. Ảnh đặt theo vai, mỗi vai một ảnh, xếp từ xa tới gần:
  - `hau-canh`: tranh phủ kín khung, không người (cung điện, phố, lớp học, đồng ruộng); trôi chậm nhất.
  - `phu-2`, `phu`: nhân vật phụ, đứng sau vai chính (phía phải và giữa khung); trượt vào từ mép gần chúng.
  - `chinh`: nhân vật chính, phía trái, đứng trước cùng; trồi lên và thu nhẹ về đúng cỡ.
  - `tien-canh`: vật sát ống kính (cành lá, lan can, rèm, sóng nước), được phóng to và tràn ra ngoài góc khung, trôi ngược chiều để ra chiều sâu.
  - Chữ (`nhan`, `chu`, `the`, `dau`, `so`) ở `tren` (nhãn tiêu đề góc trái) hoặc `giua` (góc phải trên); không dùng `mui-ten`.
  - Nhân vật và tiền cảnh là ảnh cắt rời, không dùng `khung`. Mỗi cảnh cần ít nhất `hau-canh` hoặc `chinh`.
- `toan-canh`: `nen` chỉ nhận `anh` (ảnh được cắt phủ đúng khổ, dạng khung); chữ đè lên ở `giua` hoặc `duoi`.
- Ô sai với bố cục là lỗi `parse`, thông báo liệt kê các ô đúng. Bố cục `chong` mà ghi ô cũng là lỗi.
- Nhịp không ghi ô lấy ô đầu tiên còn trống theo thứ tự trong bảng (bỏ qua `nen` và các ô đã ghi ở nhịp khác của cảnh); hết ô thì dùng ô cuối và dễ đè lên vật khác. Muốn chắc chắn thì ghi ô.
- Khổ dọc: `hai-ben` dùng `tren`, `duoi` thay cho `trai`, `phai`; `dan-hang` xếp dọc.

## Tuỳ chọn

| Tuỳ chọn | Tác dụng |
|---|---|
| `khung` | ảnh trong khung chữ nhật mép xé, có băng dính, thay vì cắt nền. Dùng cho cảnh có bối cảnh (một căn phòng, một con phố), cho vật màu xanh lá, hay khi ảnh tách nền không sạch |
| `duotone` | ảnh hai màu theo `bang-mau` (kiểu in báo) |
| `halftone` | ảnh in chấm tram |
| `xa` | đặt vật ở lớp giữa (trôi ngang chậm cùng ảnh) |
| `gan` | kéo vật lên lớp gần (trước) |
| `dung` | chỉ cho `dau`: con dấu màu xanh (ĐÚNG), đối với con dấu đỏ mặc định (SAI) |

Mặc định ảnh ở lớp giữa; chữ, thẻ, nhãn, dấu ở lớp gần. Ảnh cắt nền được tách trên nền xanh lá #00FF00: vật màu xanh lá (cây, lá, logo xanh) bị ăn mất một phần, công cụ tự chuyển sang `khung` kèm cảnh báo. Tả vật đó màu khác, hoặc ghi sẵn `khung`.

## Giới hạn

- Mỗi cảnh 1–6 nhịp; tối đa 2 nhịp `chu`; bố cục `chong` tối đa 5 vật.
- `loi`: 1–3 câu trên một dòng; lời dài quá 700 ký tự có cảnh báo, nên tách cảnh.
- `nguon:` của cảnh tối đa 90 ký tự. `chuyen:` của cảnh: `xe-giay`, `lia` hoặc `khong`, chỉ từ Cảnh 2.
- `thoi-luong` là số nguyên 10–600 giây.
- `giu:` của cảnh (nhịp im) từ 0,5 đến 3 giây.
- Ở bước `--xem-truoc` và dựng thật, công cụ đo trên hình và báo lỗi `canh` khi chữ của một nhịp tràn ô, hai vật đè nhau quá 30% (giữa hai vật chữ hay giữa hai ảnh; trừ bố cục `chong`, và trừ `dau`, `nhan` dán lên ảnh). Rút chữ, đổi ô hay đổi bố cục rồi chạy lại.

## Ví dụ từng bố cục

`dung-canh`: một cảnh kể chuyện bốn lớp. Vai chính và vai phụ là hai ảnh riêng, hậu cảnh không có người.

```
---
tieu-de: Sơn Tinh, Thủy Tinh
phong-cach: vox
nhan-vat-chinh: Sơn Tinh, chàng trai Việt cổ cao lớn vạm vỡ, tóc búi, mình trần, khố và áo choàng ngắn màu nâu đất, tay cầm cây gậy thần bằng gỗ
---

## Cảnh 1
bo-cuc: dung-canh
loi: Có hai chàng trai cùng đến cầu hôn. Sơn Tinh là chúa vùng núi non, còn Thủy Tinh là chúa vùng nước thẳm.
nhip: @dau | anh: ve: sân lớn trước cung điện thời Hùng Vương, lát đá, cờ phướn hai bên | hau-canh
nhip: Sơn Tinh | anh: ve: @nhan-vat đứng thẳng, ngực ưỡn, nhìn sang phải | chinh
nhip: Thủy Tinh | anh: ve: Thủy Tinh, chàng trai Việt cổ dáng thanh mảnh, áo choàng dài màu xanh biển có hoa văn sóng nước, đội vương miện hình con sóng, đứng nhìn sang trái | phu
nhip: @dau | anh: ve: vài lá sen và một đoá sen hồng vươn lên từ góc dưới | tien-canh
nhip: @dau | nhan: Hai chàng cùng đến | tren
```

`mot`: một vật và một câu chốt. Cảnh có số liệu nên có `nguon`.

```
---
tieu-de: Giờ làm việc
phong-cach: vox
---

## Cảnh 1
bo-cuc: mot
loi: Giờ làm việc bình thường không quá bốn mươi tám giờ mỗi tuần. Làm quá mức đó là làm thêm giờ.
nguon: Bộ luật Lao động 2019, Điều 105
nhip: @dau | anh: ve: chiếc đồng hồ treo tường tròn mặt trắng, kim chỉ sáu giờ chiều, chụp thẳng | giua
nhip: bốn mươi tám giờ | so: {{48}} giờ mỗi tuần | tren
nhip: làm thêm giờ | nhan: Quá mức là làm thêm | duoi
```

`hai-ben`: so sánh hai bên, con dấu rất ngắn ở giữa (hai ảnh đều là khung), ảnh bên phải có hai tuỳ chọn.

```
---
tieu-de: Họp và nhắn tin
phong-cach: vox
bang-mau: bao-cu
---

## Cảnh 1
bo-cuc: hai-ben
loi: Một cuộc họp dài cả tiếng, hay một tin nhắn rõ ràng đọc trong hai phút.
nhip: cuộc họp | anh: ve: phòng họp có bàn dài và nhiều ghế trống, góc rộng từ cửa nhìn vào | trai | khung
nhip: hay | dau: VS | giua
nhip: tin nhắn | anh: ve: bàn tay cầm điện thoại, ngón cái đang gõ, chụp cận từ trên xuống | phai | khung duotone
```

`dan-hang`: các bước theo thứ tự lời, mỗi ô một thẻ.

```
---
tieu-de: Ba bước xin nghỉ phép
phong-cach: vox
---

## Cảnh 1
bo-cuc: dan-hang
loi: Báo trước cho quản lý. Bàn giao việc đang làm. Rồi mới gửi đơn.
nhip: báo trước | the: Bước 1 | Báo quản lý | 1
nhip: bàn giao | the: Bước 2 | Bàn giao việc | 2
nhip: gửi đơn | the: Bước 3 | Gửi đơn | 3
```

`chong`: nhiều thứ rối cùng lúc, không ghi ô.

```
---
tieu-de: Một ngày quá tải
phong-cach: vox
---

## Cảnh 1
bo-cuc: chong
loi: Email chưa đọc, cuộc gọi nhỡ, hạn nộp báo cáo, cuộc họp lúc bốn giờ. Tất cả dồn vào một buổi chiều.
nhip: email chưa đọc | anh: ve: phong bì thư màu kem chất thành chồng, chụp chéo từ trên
nhip: cuộc gọi nhỡ | anh: ve: điện thoại bàn màu đỏ kiểu cũ, ống nghe nhấc lệch, chụp cận
nhip: hạn nộp | nhan: Hạn nộp hôm nay
nhip: cuộc họp | anh: ve: đồng hồ báo thức kim loại màu vàng, chụp nghiêng
nhip: một buổi chiều | dau: QUÁ TẢI
```

`toan-canh`: ảnh thật phủ kín khung, chữ đè lên. Ảnh thật dùng từ khoá tiếng Anh.

```
---
tieu-de: Hồ Gươm buổi sáng
phong-cach: vox
kho: doc
---

## Cảnh 1
bo-cuc: toan-canh
loi: Năm giờ sáng, quanh hồ Gươm đã kín người tập thể dục.
nhip: @dau | anh: tim: Hoan Kiem Lake Hanoi morning | nen
nhip: hồ Gươm | chu: Hà Nội thức dậy | giua
nhip: tập thể dục | nhan: Trước giờ đi làm | duoi
```

Khổ dọc với `hai-ben` dùng `tren` và `duoi`, mũi tên nối hai ô:

```
---
tieu-de: Trước và sau
phong-cach: vox
kho: doc
---

## Cảnh 1
bo-cuc: hai-ben
loi: Trước đây báo cáo nằm trong mười tệp rời. Giờ mọi người cùng sửa một tệp chung.
nhip: mười tệp rời | anh: ve: chồng bìa hồ sơ giấy lộn xộn trên bàn, chụp từ trên xuống | tren
nhip: cùng sửa | mui-ten: tren -> duoi | giua
nhip: một tệp chung | anh: ve: một bìa hồ sơ duy nhất gọn gàng đặt giữa bàn gỗ sạch, chụp từ trên xuống | duoi
```

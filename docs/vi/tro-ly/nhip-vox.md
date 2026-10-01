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
| `anh` | `ve: <mô tả>` (AI vẽ), `tim: <từ khoá tiếng Anh>` (ảnh thật giấy phép mở) hoặc tên file trong `anh/` (`.jpg`, `.jpeg`, `.png`, `.webp`) | mô tả `ve:` tối đa 300 ký tự | cắt nền: bay vào, đập xuống có nảy và bóng đổ; khung: rơi xoay nhẹ rồi băng dính dán lên |
| `the` | `<nhãn> \| <giá trị> \| <chú thích>`, chú thích bỏ được | nhãn 24, giá trị 16, chú thích 60 ký tự | trượt vào |
| `chu` | một dòng chữ lớn, ý chốt hay câu ngắn | 40 ký tự; tối đa 2 dòng `chu` mỗi cảnh | hiện từng từ |
| `nhan` | nhãn trên băng dính màu | 30 ký tự | dán |
| `dau` | con dấu, thường viết hoa | 16 ký tự | đóng mạnh, máy rung nhẹ |
| `mui-ten` | `<ô> -> <ô>`, hai đầu là ô của bố cục, ví dụ `trai -> phai`; vẽ trên cả khung, không chiếm ô; bố cục `chong` không dùng được | | vẽ dần |
| `so` | một số chạy `{{số}}` kèm chữ trước hoặc sau, ví dụ `{{48}} giờ mỗi tuần` | 24 ký tự | chạy số từ 0 lên |

- Giới hạn đếm ký tự hiện ra. Vượt giới hạn là lỗi `parse` nêu đúng dòng.
- `so`: viết dấu chấm thập phân (`{{2.5}}`), video hiện dấu phẩy ("2,5"). Cảnh có `so` hay có số liệu trong lời phải có dòng `nguon:` của cảnh.
- `the` hợp với một con số hay một sự thật có ba tầng: tên, giá trị, ghi chú.
- `anh: ve:` là ảnh AI, kiểu cắt nền (một vật trên nền giấy, viền giấy xé trắng) trừ khi có tuỳ chọn `khung` hay ở ô `nen`. Ảnh thật `tim:` và ảnh người dùng gửi luôn ở dạng khung.

## Bố cục và ô

| Bố cục | Ô ngang | Ô dọc | Hợp với |
|---|---|---|---|
| `mot` | `giua`, `tren`, `duoi` | `giua`, `tren`, `duoi` | một vật, một khái niệm, một câu chốt |
| `hai-ben` | `trai`, `phai`, `giua` | `tren`, `duoi`, `giua` | so sánh, đối lập, trước và sau |
| `dan-hang` | `1`, `2`, `3`, `4` (xếp ngang) | `1`, `2`, `3`, `4` (xếp dọc) | danh sách, các bước |
| `chong` | không có ô: tự xếp lệch nhau theo cảnh, tối đa 5 vật | như ngang | nhiều yếu tố rối rắm cùng lúc |
| `toan-canh` | `nen` (ảnh phủ kín khung), `giua`, `duoi` | như ngang | nơi chốn, bối cảnh, một khoảnh khắc |

- `mot`: `giua` là ô lớn cho ảnh; `tren` và `duoi` là dải hẹp, dành cho `chu`, `nhan`, `dau`, `so`.
- `hai-ben`: ô `giua` nằm đè lên mép trong của hai bên; chỉ đặt ở đó một `dau` hoặc `nhan` ngắn, không đặt ảnh hay `the`. Hai bên là ảnh cắt nền thì con dấu khoảng 8 ký tự vẫn vừa (`IM LẶNG`); hai bên là ảnh `khung` (khung chiếm trọn ô) thì chỉ 2–3 ký tự như `VS`, dài hơn là lỗi `canh` "đè lên nhau quá nhiều".
- `dan-hang`: mỗi ô hẹp (ngang khoảng một phần tư khung), hợp với `the`, `nhan`, ảnh cắt nền; chữ dài thì dễ tràn.
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
| `xa` | đẩy vật ra lớp xa (sau, mờ nhẹ, lệch nhiều khi máy xoay) |
| `gan` | kéo vật lên lớp gần (trước) |

Mặc định ảnh ở lớp giữa; chữ, thẻ, nhãn, dấu ở lớp gần. Ảnh cắt nền được tách trên nền xanh lá #00FF00: vật màu xanh lá (cây, lá, logo xanh) bị ăn mất một phần, công cụ tự chuyển sang `khung` kèm cảnh báo. Tả vật đó màu khác, hoặc ghi sẵn `khung`.

## Giới hạn

- Mỗi cảnh 1–6 nhịp; tối đa 2 nhịp `chu`; bố cục `chong` tối đa 5 vật.
- `loi`: 1–3 câu trên một dòng; lời dài quá 700 ký tự có cảnh báo, nên tách cảnh.
- `nguon:` của cảnh tối đa 90 ký tự. `chuyen:` của cảnh: `xe-giay`, `lia` hoặc `khong`, chỉ từ Cảnh 2.
- `thoi-luong` là số nguyên 15–600 giây.
- Ở bước `--xem-truoc` và dựng thật, công cụ đo trên hình và báo lỗi `canh` khi chữ của một nhịp tràn ô, hai vật đè nhau quá 30% (trừ bố cục `chong`), hoặc dòng nguồn tràn khung. Rút chữ, đổi ô hay đổi bố cục rồi chạy lại.

## Ví dụ từng bố cục

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

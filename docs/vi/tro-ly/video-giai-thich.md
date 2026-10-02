# Loại việc: Video giải thích dựng bằng mã (kiểu Vox)

File dành cho AI. Đọc cùng `docs/vi/tro-ly/nhip-vox.md` (ngữ pháp dòng `nhip`, bảng vật, bố cục và ô). Đầu ra là một video MP4 kiểu Vox: mỗi cảnh một nền cắt dán cổ điển vẽ theo nội dung, cụm hình cắt nền viền giấy xé, nhãn, thẻ và chữ hiện êm đúng lúc giọng đọc nói tới; lời kể liền mạch. Không phải PPTX.

## Khi nào dùng

Người dùng muốn một video ngắn giải thích một chuyện, một khái niệm, một cách làm: chuyện công sở, sức khoẻ, tiền bạc, công nghệ, pháp luật, bài học, sản phẩm. Bộ công cụ không gắn với ngành nào; viết cho người xem bình thường, không giả định họ là ai.

Ví dụ câu lệnh:
- "Tạo video vox 60 giây về giao tiếp với đồng nghiệp"
- "Làm video giải thích kiểu vox vì sao lãi kép quan trọng, khổ dọc để đăng TikTok"
- "Video giải thích 2 phút: Model Context Protocol là gì"
- "Làm video giải thích quy trình xin nghỉ phép, dùng nội dung này: (nội dung)"

Mọi video giải thích mới làm kiểu Vox, kể cả khi câu lệnh nói "video viết tay", "video whiteboard", "video cắt dán" hay "video kể chuyện": làm Vox và nói ngắn một câu trong tin nhắn gửi video rằng video mới đều dựng kiểu này. Người dùng nói rõ vẫn muốn kiểu viết tay cũ, hoặc nhờ sửa một `video.md` cũ có dòng `loai:`, thì làm theo `docs/vi/tham-khao/video-viet-tay.md` và `docs/vi/tham-khao/canh-video.md`.

Câu lệnh chỉ có "làm video" hoặc "xuất video" (không rõ từ slide hay video mới): hỏi đúng câu phân loại ở mục 11 của `AGENTS.vi.md` trước. Video dựng từ slide có sẵn là loại việc "Video bài giảng", không phải file này. Không dùng file này cho video do AI sinh chuyển động (Veo, Flow) hay video tư liệu.

## Hỏi gì

Chỉ hỏi khi câu lệnh thiếu **chủ đề** hoặc thiếu **nội dung** mà AI không tự viết đúng được (ví dụ quy trình nội bộ của một công ty, số liệu riêng của người dùng). Hỏi một tin nhắn, tối đa hai câu, rồi chờ trả lời. Có chủ đề rồi thì không hỏi gì: tự viết kịch bản, tự xem trước, tự sửa, dựng xong mới gửi.

Không hỏi mà dùng mặc định:

| Điều | Mặc định khi câu lệnh không nói |
|---|---|
| Thời lượng | `thoi-luong: 60` |
| Khổ | `kho: ngang` (16:9); "dọc", "TikTok", "Reels", "Shorts" thì `kho: doc` |
| Giọng | giọng Thu Giang của VieNeu, tốc độ vừa (`giong: thu-giang`, mặc định, không cần ghi); máy không có VieNeu thì công cụ tự dùng giọng nữ edge-tts và báo trong `warnings` |
| Phụ đề | `karaoke` (in lên hình, tô vàng từng từ) |
| Tiếng hiệu ứng | có (`am-thanh: co`) |
| Nhạc nền | không; chỉ thêm khi câu lệnh xin |
| Kiểu ảnh | `phong-anh: cat-dan` (tranh cắt dán cổ điển, mặc định); "ảnh chụp", "ảnh thật" thì `chup-that`; "minh hoạ phẳng", "hoạt hình" thì `minh-hoa` |
| Nền cảnh | mỗi cảnh một nền AI riêng (`nen-canh: ve`); máy không có nguồn vẽ ảnh thì `nen-canh: khong` |

Không dừng chờ duyệt kịch bản. Người dùng xin xem kịch bản trước ("cho xem kịch bản trước", "duyệt trước rồi hãy dựng") thì gửi nội dung `video.md` dạng dễ đọc (mỗi cảnh: lời và các vật hiện ra), dừng, và chỉ dựng khi họ đồng ý.

## Nghề viết kịch bản Vox

Video Vox giữ người xem bằng mạch kể, không bằng tiêu đề. Viết theo năm nhịp lớn:

1. **Móc** (3 giây đầu): một tình huống ai cũng gặp, một câu hỏi ngược đời, hoặc một con số có nguồn. Khung đầu tiên đã có hình: nhịp đầu của Cảnh 1 dùng `@dau` hoặc cụm ở ngay đầu lời.
2. **Vấn đề**: vì sao chuyện này đáng bận tâm, nó gây hại hay gây rối ở đâu.
3. **Giải thích** 2–4 ý. Mỗi ý gắn với **một hình ví von cụ thể**: "nợ kỹ thuật" là chồng bát đĩa chưa rửa, "lãi kép" là quả cầu tuyết lăn xuống dốc. Một ý thường là một cảnh.
4. **Lật**: điều người xem không ngờ, đảo lại cách họ vẫn nghĩ ("nghe thì chậm, thật ra nhanh nhất").
5. **Chốt**: một câu để mang về, tốt nhất là một việc làm được ngay.

Không làm:
- Không có cảnh tiêu đề riêng: tên video nằm ở khoá `tieu-de`, video vào thẳng câu móc.
- Không mở bằng "Hôm nay chúng ta…", "Xin chào các bạn", "Trong video này…".
- Không liệt kê "thứ nhất, thứ hai, thứ ba"; nối ý bằng chuyện ("Nhưng…", "Mà…", "Vậy thì…").
- Không có cảnh tóm tắt lặp lại các ý, không hỏi "bạn đã hiểu chưa".

Quỹ từ theo thời lượng. Giọng Thu Giang đọc khoảng 4,3 từ mỗi giây ở tốc độ vừa (`cham` 4,0, `nhanh` 4,7); giọng edge-tts (`nu`, `nam`) đọc chậm hơn nhiều, khoảng 2,7 từ mỗi giây. Mỗi cảnh thêm khoảng 0,55 giây chuyển cảnh:

| `thoi-luong` | Số từ (giọng Thu Giang) | Số từ (giọng edge-tts) | Số cảnh |
|---|---|---|---|
| 30 giây | ≈ 115 từ | ≈ 75 từ | 3–4 cảnh |
| 60 giây | ≈ 230 từ | ≈ 150 từ | 6–8 cảnh |
| 2 phút | ≈ 480 từ | ≈ 300 từ | 12–15 cảnh |
| 3 phút | ≈ 720 từ | ≈ 460 từ | 18–22 cảnh |

Tự ước trước khi chạy lệnh nào: thời lượng ≈ số từ ÷ tốc độ đọc + 0,55 giây × số cảnh. Mỗi cảnh dài 7–12 giây, tức khoảng 30–45 từ với giọng Thu Giang. Đếm từ như giọng đọc: mỗi tiếng cách nhau một khoảng trắng là một từ.

Lời:
- **Lời liền mạch**: câu dài vừa, 10–20 từ, giọng kể như nói với một người ngồi đối diện ("bạn"). Các câu nối ý với nhau bằng "nhưng", "vì thế", "mà", "thế nên", "còn khi"; cảnh sau nối tiếp cảnh trước như một mạch kể. Không băm lời thành nhiều câu cụt ba bốn từ, không đọc như gạch đầu dòng.
- Viết để đọc thành tiếng: chữ viết tắt, kí hiệu viết thành chữ đọc được; có dấu phẩy ở chỗ ngắt tự nhiên để phụ đề ngắt đẹp.
- `loi` mỗi cảnh 2–3 câu nối nhau, viết trên một dòng.
- Người dùng đưa nội dung thì giữ đúng ý, thuật ngữ và số liệu của họ; chỉ viết lại thành lời kể ngắn.

**Không bịa số liệu.** Chỉ dùng con số người dùng đưa, hoặc con số tra được ở một nguồn gọi tên được (luật, cơ quan thống kê, nghiên cứu, tài liệu chính thức). Cảnh có số thì có dòng `nguon:` ghi nguồn đó, tối đa 90 ký tự (nguồn không hiện trên hình mà ghi vào `nguon.txt` cạnh video). Không có nguồn thì nói bằng lời không có số, và không khẳng định mức độ mình không kiểm được: "nhiều người" thay vì "85% người". Con số minh hoạ trong một tình huống giả định ("hạn 17 giờ thứ Sáu") không phải số liệu, nhưng không được trông như kết quả khảo sát.

## Hình khớp thoại

- **Mỗi cảnh mở ra đã có hình**: nền của cảnh, một nhãn tiêu đề (`nhan` ở `tren`) và hình chính đều đặt ở `@dau`; vật phụ (chữ chốt, thẻ, con dấu) mới hiện theo lời. Cảnh mở bằng nền trống là lỗi: `--plan-only` cảnh báo "vật đầu tiên hiện muộn".
- **Nền cảnh**: mỗi cảnh ghi một dòng `nen: <mô tả>` tả một mặt nền cắt dán gợi đúng bối cảnh của lời ("mặt bàn văn phòng nhìn từ trên xuống với giấy tờ, kẹp giấy và phong bì", "bản đồ cũ, la bàn và mảnh giấy xé"). Không ghi thì công cụ tự lập từ tên video và lời của cảnh, kém đúng ý hơn. Cảnh `toan-canh` đã có ảnh ở ô `nen` thì không cần.
- **Hình chính là một cụm vật ghép lại kiểu cắt dán**, không phải một vật lẻ: "cụm cắt dán gồm một chiếc đồng hồ cát lớn đặt cạnh chồng giấy tờ cao nghiêng ngả". Cụm hình to, khoảng nửa khung.
- Câu nào cũng có hình đỡ: câu mở cảnh do nhãn và cụm hình ở `@dau` đỡ, các câu sau không để hai câu liền nhau mà hình không đổi. Nhịp gắn vào đúng từ gọi tên sự vật: lời nói "cốc cà phê nguội" thì ảnh cốc cà phê hiện ra đúng lúc giọng đọc tới "cốc cà phê".
- **Phép thử tắt tiếng**: tắt tiếng đi, người xem vẫn đoán được mỗi cảnh nói gì. Trước khi chạy lệnh, viết cho từng cảnh một dòng nháp "lời nói gì — hình cho thấy gì"; hình không cho thấy ý của lời thì đổi hình.
- Chữ trên hình tối đa khoảng 6 từ, là ý chốt hay nhãn, không chép lại lời (lời đã có ở phụ đề). Mỗi cảnh tối đa 2 dòng `chu`.
- `ve:` tả **vật và hành động** cụ thể: "cụm cắt dán gồm một con rùa cõng chiếc đồng hồ báo thức cổ trên lưng" thay vì "sự chậm rãi". Ảnh cắt nền là một cụm gọn, tách khỏi nền. Không tả không khí chung, không xin chữ, biển hiệu hay màn hình có chữ: ảnh AI không được có chữ.
- Người, địa danh, công trình, sự kiện, sản phẩm có thật: dùng ảnh thật `anh: tim: <từ khoá tiếng Anh>`, không để AI vẽ giả.
- Ý trừu tượng thì tìm vật ví von. Không tìm được vật nào đúng thì dùng `the`, `dau` hoặc `chu`, không chèn ảnh cho có.
- Ảnh cắt nền được tách trên nền xanh lá: vật màu xanh lá (cây, lá, chai xanh, logo xanh) bị ăn mất một phần. Tả vật đó màu khác, hoặc thêm tuỳ chọn `khung`.
- Hai cảnh liền nhau không dùng cùng một bố cục và cùng kiểu vật; đổi nhịp cho mắt nghỉ.

## Chọn bố cục

| Ý của cảnh | `bo-cuc` | Cách dùng |
|---|---|---|
| Một ý với một cụm hình lớn (bố cục chính, giống video mẫu) | `mot` | nhãn tiêu đề ở `tren` (góc trái trên), cụm hình lớn ở `giua` (lệch phải), chữ chốt, thẻ hay con dấu ở `duoi` (bên trái) |
| So sánh, đối lập, trước và sau | `hai-ben` | hai ảnh ở `trai`, `phai` (khổ dọc `tren`, `duoi`); `giua` chỉ cho một `dau` hay `nhan` ngắn, vì ô này đè lên hai bên (hai bên là ảnh `khung` thì chỉ 2–3 ký tự như `VS`) |
| Danh sách, các bước, ba điều cần nhớ | `dan-hang` | ô `1`–`4` theo thứ tự lời, mỗi ô một thẻ hay một ảnh |
| Nhiều thứ rối rắm cùng lúc | `chong` | không ghi ô, tối đa 5 vật tự xếp lệch nhau |
| Nơi chốn, bối cảnh, một khoảnh khắc | `toan-canh` | ảnh phủ kín ở `nen`, chữ đè ở `giua` hoặc `duoi` |

Bảng ô đủ cho hai khổ ở `docs/vi/tro-ly/nhip-vox.md`.

## Cấu trúc video.md

Viết `video.md` trong `projects/_video/<tên_video>/`. File mở đầu bằng khối thông tin giữa hai dòng `---`, rồi mỗi cảnh một mục `## Cảnh N`, đánh số liên tiếp từ 1.

| Khoá | Bắt buộc | Giá trị |
|---|---|---|
| `tieu-de` | có | tên video (không hiện thành cảnh riêng) |
| `phong-cach` | có | `vox` |
| `thoi-luong` | không | số giây mong muốn, số nguyên 15–600; có thì công cụ ước thời lượng và cảnh báo khi lệch quá +15% hay dưới −25% |
| `kho` | không | `ngang` (mặc định, 16:9) hoặc `doc` (9:16 cho TikTok, Reels, Shorts) |
| `do-phan-giai` | không | `1080` (mặc định, Full HD) hoặc `720` (dựng nhanh hơn cho máy yếu) |
| `giong` | không | `thu-giang` (mặc định: giọng Thu Giang của VieNeu, đọc trên máy, không cần mạng), `nu` hoặc `nam` (edge-tts, cần mạng) |
| `toc-do` | không | `cham`, `vua` (mặc định) hoặc `nhanh` |
| `phu-de` | không | `karaoke` (mặc định: in lên hình, tô vàng từng từ, một dòng một lúc), `hinh` (cả câu một màu), `file` (file `phu-de.srt` riêng) hoặc `khong` |
| `am-thanh` | không | `co` (mặc định: tiếng "ting" nhỏ khi vật hiện, tiếng đóng dấu, tiếng chuyển cảnh, luôn nhỏ hơn giọng đọc) hoặc `khong` |
| `phong-anh` | không | `cat-dan` (mặc định: tranh cắt dán kiểu tạp chí cổ, giấy cũ, tranh khắc, tông trầm), `chup-that` (ảnh AI kiểu ảnh chụp thật) hoặc `minh-hoa` (tranh minh hoạ phẳng, màu tươi); áp cho mọi ảnh AI của video |
| `nen-canh` | không | `ve` (mặc định: mỗi cảnh một nền AI riêng) hoặc `khong` (nền giấy vẽ bằng mã, dùng khi máy không có nguồn vẽ ảnh) |
| `bang-mau` | không | `kem` (mặc định: giấy kem, mực đậm, nhấn cam đỏ), `bao-cu` (giấy báo cũ ngả vàng, nhấn đỏ trầm), `dem` (nền xanh đêm, chữ kem, nhấn vàng) hoặc `tuoi` (giấy sáng, nhấn đỏ hồng) |
| `chuyen-canh` | không | `xen-ke` (mặc định: xé giấy và lia nhanh xen nhau), `xe-giay`, `lia` hoặc `khong` |
| `nhac-nen` | không | tên file nhạc trong `nhac/` của video; không ghi thì không có nhạc |
| `nguon-nhac` | không | dòng nguồn của nhạc người dùng gửi, chỉ ghi kèm `nhac-nen` khi `nhac/nguon.json` không có bản ghi cho file đó |
| `loat` | không | tên loạt video, tối đa 30 ký tự; có thì hiện tên loạt và số cảnh ở hai góc trên |

Với `phong-cach: vox` không cần `mon`, `lop`. Các khoá của kiểu viết tay (`ban-tay`, `nhan-vat`, `mau-ao`, `chu-dong`, `may-quay`) không dùng: ghi vào là lỗi `parse`.

Mỗi cảnh:
- `bo-cuc:` một trong `mot`, `hai-ben`, `dan-hang`, `chong`, `toan-canh`.
- `loi:` lời đọc, 1–3 câu trên một dòng.
- `nhip:` 1–6 dòng, dạng `<cụm từ trong lời> | <vật>: <nội dung> | <ô> | <tuỳ chọn>`, theo đúng thứ tự lời. Ô và tuỳ chọn bỏ được; nhiều tuỳ chọn viết chung một ô, cách nhau bằng khoảng trắng (`| phai | khung duotone`). Ngữ pháp đủ, bảng vật, bảng ô và ví dụ từng bố cục ở `docs/vi/tro-ly/nhip-vox.md`.
- `chuyen:` tuỳ chọn, từ Cảnh 2: `xe-giay`, `lia` hoặc `khong`, đổi kiểu chuyển vào riêng cảnh này.
- `nen:` tuỳ chọn, nên có: mô tả nền cắt dán của cảnh, tối đa 300 ký tự.
- `nguon:` tuỳ chọn, bắt buộc khi cảnh có số liệu: nguồn của số liệu, tối đa 90 ký tự; ghi vào `nguon.txt`, không hiện trên hình.

Cảnh Vox không có dòng `loai:`. Không chèn địa chỉ web vào file: công cụ báo lỗi `parse`.

### Ví dụ đầy đủ: "Giao tiếp với đồng nghiệp", 60 giây

Sáu cảnh, 231 từ lời, giọng Thu Giang, dựng ra 58 giây. Mạch: móc (Cảnh 1) → vấn đề (2) → ba ý, mỗi ý một cụm hình (3, 4, 5) → lật và chốt (6). Mỗi cảnh mở bằng nền riêng, nhãn tiêu đề và cụm hình chính ở `@dau`; vật phụ hiện theo lời. Không có số liệu nên không cần `nguon`; "Trưa thứ Năm", "mười giây" chỉ là tình huống mẫu.

```
---
tieu-de: Giao tiếp với đồng nghiệp
phong-cach: vox
thoi-luong: 60
kho: ngang
---

## Cảnh 1
bo-cuc: mot
nen: mặt bàn văn phòng nhìn từ trên xuống với giấy tờ, kẹp giấy, phong bì thư và những mảnh giấy xé
loi: Bạn chỉ hỏi đồng nghiệp một câu rất bình thường: việc ấy xong chưa? Thế mà người kia lại nghe thành một lời trách: sao làm chậm thế? Cùng một câu nói mà hai người hiểu theo hai cách.
nhip: @dau | nhan: Một câu, hai cách hiểu | tren
nhip: @dau | anh: ve: cụm cắt dán gồm hai nhân viên văn phòng đứng quay lưng vào nhau, ở giữa là một bong bóng thoại bị xé làm đôi | giua
nhip: lời trách | dau: HIỂU LẦM | duoi

## Cảnh 2
bo-cuc: hai-ben
nen: những lá thư tay cũ, tem thư và dây điện thoại xoắn nằm rải rác trên giấy ngả màu
loi: Lý do là chữ viết không mang theo giọng nói, cũng không mang theo nét mặt. Người đọc buộc phải tự đoán thái độ của bạn, mà lúc đang bận thì người ta thường đoán theo hướng xấu nhất.
nhip: @dau | anh: ve: cụm cắt dán gồm một chiếc điện thoại bàn cổ và một bong bóng tin nhắn trống bay lên | trai
nhip: nét mặt | anh: ve: cụm cắt dán gồm một chiếc mặt nạ sân khấu trắng không biểu cảm và vài mảnh giấy báo xé | phai
nhip: hướng xấu nhất | dau: ĐOÁN XẤU | giua

## Cảnh 3
bo-cuc: dan-hang
nen: bảng ghim bằng gỗ bần với giấy nhớ trống, đinh ghim và dây kẹp, nhìn chính diện
loi: Vì thế, mỗi khi nhắn giao việc, bạn hãy viết cho đủ ba điều: việc cần làm là gì, hạn chót là khi nào, và ai là người chịu trách nhiệm chính.
nhip: @dau | anh: ve: cụm cắt dán gồm một chiếc bút máy cổ nằm chéo trên xấp giấy nhớ | 1
nhip: việc cần làm | the: Việc gì | Slide báo giá | 2
nhip: hạn chót | the: Hạn chót | Trưa thứ Năm | 3
nhip: ai là người | the: Ai làm | Anh Minh | 4

## Cảnh 4
bo-cuc: mot
nen: mặt đồng hồ cổ, bánh răng đồng và những tờ lịch xé chồng lên nhau ở rìa khung
loi: Còn khi nhận được một tin nhắn chưa rõ, bạn đừng ngồi đoán mà hãy hỏi lại ngay. Hỏi lại chỉ mất mười giây, trong khi đoán sai có thể khiến bạn mất cả buổi chiều làm lại.
nhip: @dau | nhan: Chưa rõ thì hỏi lại | tren
nhip: @dau | anh: ve: cụm cắt dán gồm một chiếc đồng hồ cát lớn đặt cạnh chồng giấy tờ cao nghiêng ngả | giua
nhip: mười giây | chu: Hỏi mười giây, khỏi làm lại | duoi

## Cảnh 5
bo-cuc: toan-canh
loi: Với những chuyện nhạy cảm hoặc dễ gây hiểu lầm thì tốt nhất là đừng nhắn tin. Bạn hãy đến gặp trực tiếp, nói chuyện nhẹ nhàng, rồi gửi lại một dòng tóm tắt để cả hai cùng nhớ.
nhip: @dau | anh: ve: hai đồng nghiệp ngồi trò chuyện vui vẻ bên bàn làm việc cạnh cửa sổ lớn, góc rộng | nen
nhip: gặp trực tiếp | chu: Gặp mặt trước | giua
nhip: một dòng tóm tắt | nhan: Rồi nhắn một dòng chốt | duoi

## Cảnh 6
bo-cuc: mot
nen: con đường quanh co vẽ trên bản đồ cũ, la bàn và những mảnh giấy xé màu đỏ trầm và xanh than
loi: Nghe thì có vẻ mất công hơn, nhưng thật ra một phút nói cho rõ ràng sẽ tiết kiệm cho bạn cả một ngày hiểu lầm. Vì vậy, trước khi bấm gửi, bạn hãy đọc lại tin nhắn như thể mình là người nhận.
nhip: @dau | nhan: Đọc lại trước khi gửi | tren
nhip: @dau | anh: ve: cụm cắt dán gồm một con rùa cõng chiếc đồng hồ báo thức cổ trên lưng | giua
nhip: một phút | chu: Rõ một phút, nhàn cả ngày | duoi
```

## Ảnh

Mọi ảnh của nhịp `anh` đi qua `tools/vi/anh_vox.py`: lệnh lập danh sách ảnh, lấy ảnh từ nguồn dùng được đầu tiên dưới đây, tách nền hoặc làm khung, tính trước viền giấy xé, bóng, `duotone`, `halftone`, và ghi nguồn. `video_ma.py` chỉ đọc kết quả, không bao giờ gọi AI hay lên mạng tìm ảnh. Có `venv\Scripts\python.exe` ở thư mục gốc repo thì dùng nó thay cho `python`.

Nguồn ảnh AI, theo thứ tự:

1. **Công cụ vẽ ảnh của chính nền tảng** (Antigravity, Codex app). Chạy `python tools\vi\anh_vox.py projects\_video\<tên_video> --chi-ke-hoach`, đọc `anh/ai/ke-hoach.json`: mỗi mục có `nguon: "ve"` có `ma`, `prompt` (dán nguyên văn, không dịch, không bớt), `kich_thuoc` và `file_goc`. Vẽ từng mục, 3–4 ảnh một lượt, lưu đúng tên `anh/ai/goc/<ma>.png`. Rồi chạy `anh_vox.py` với `--cong-cu "<nền tảng>" --mo-hinh "<mô hình đã vẽ>"` (ví dụ `--cong-cu Antigravity --mo-hinh "Nano Banana Pro"`): ảnh có sẵn được dùng, không vẽ lại, và cuối video ghi đúng mô hình. Không biết tên mô hình thì bỏ hai cờ: ảnh được ghi "không rõ" mô hình ("chưa rõ mô hình" trong `warnings`); chạy lại với `--mo-hinh` sau cũng điền được.
2. **API tạo ảnh kiểu OpenAI** (cách của Claude Code và mọi nền tảng không tự vẽ được). Cấu hình đọc theo thứ tự: biến môi trường `ANH_AI_URL`, `ANH_AI_KEY`, `ANH_AI_MO_HINH`, rồi file `%USERPROFILE%\.2anh-studio\anh-ai.json` (khoá `url`, `khoa`, `mo_hinh`). Mặc định là 9router trên máy, `http://localhost:20128/v1`, mô hình `ag/gemini-3.1-flash-image` (khoảng 15 giây một ảnh). Khoá API chỉ nằm ở biến môi trường hay file cấu hình trong thư mục người dùng: không ghi khoá vào file nào trong repo hay trong `projects/`, không in ra, không xin người dùng dán khoá vào khung chat. Thiếu khoá thì chỉ người dùng tự đặt: `setx ANH_AI_KEY "<khoá>"` rồi mở lại cửa sổ lệnh.
3. **Không có nguồn vẽ nào** (lỗi `cau-hinh` mà người dùng chưa đặt khoá được): thay nhịp `anh: ve:` bằng `chu`, `the`, `dau`, `so`, hoặc ảnh thật `tim:` khi sự vật có thật; báo người dùng một dòng rằng video chưa có ảnh AI và cách đặt khoá.

Ảnh thật (`anh: tim: <từ khoá tiếng Anh>`): `anh_vox.py` tự chạy `skills/ppt-master/scripts/image_search.py` tải ảnh giấy phép mở vào `anh/`, nguồn lấy từ `anh/image_sources.json` và ghi vào `nguon.txt` cạnh video (không hiện trên hình). Từ khoá tiếng Anh, cụ thể ("Hoan Kiem Lake Hanoi" thay vì "lake"). Ảnh thật và ảnh người dùng gửi (tên file trong `anh/`) luôn ở dạng `khung`. Không dùng ảnh không rõ nguồn.

Lưu đệm và giới hạn:
- Mỗi ảnh AI có mã băm theo câu lệnh và khổ. Sửa mô tả một nhịp thì chỉ ảnh đó vẽ lại; đổi `ANH_AI_MO_HINH` thì ảnh vẽ bằng mô hình cũ được vẽ lại (trừ ảnh nền tảng vẽ).
- Mỗi lần chạy vẽ tối đa 30 ảnh mới, tính cả nền cảnh (`--toi-da N` để nâng), 3 ảnh song song; lỗi mạng, lỗi máy chủ, câu trả lời không có ảnh hay một ảnh quá 180 giây chưa xong thì tự thử lại 2 lần. Lượt chạy bị ngắt giữa chừng: chạy lại, ảnh đã vẽ được dùng lại và vẫn ghi đúng mô hình.
- Ảnh cắt nền tách không sạch thì tự vẽ lại một lần với nền xanh chặt hơn; vẫn hỏng thì chuyển nhịp đó sang `khung` kèm một dòng `warnings`.
- Câu lệnh luôn cấm chữ, nhưng ảnh AI vẫn có thể có chữ lạ hay sai ý: chỉ phát hiện được bằng mắt ở bước xem trước. Sửa mô tả `ve:` (thêm chi tiết, bỏ thứ dễ sinh chữ như biển hiệu, giấy có chữ) rồi chạy lại `anh_vox.py`.
- Video không hiện dòng nguồn nào: mô hình AI, nguồn ảnh thật, nguồn số liệu và nguồn nhạc ghi vào `nguon.txt` cạnh `video.mp4` (gửi kèm khi người dùng đăng video có ảnh thật giấy phép CC BY). `anh/ai/nguon.json` và `anh/ai/vox.json` do `anh_vox.py` ghi; không tự viết hay sửa hai file này.

## Vòng tự kiểm

AI tự kiểm và tự sửa trước khi gửi, không chờ duyệt (trừ khi người dùng xin xem kịch bản trước). Lệnh chạy từ thư mục gốc repo.

1. **Tự ước thời lượng** bằng quỹ từ ở mục "Nghề viết kịch bản Vox" và viết dòng nháp "lời nói gì — hình cho thấy gì" cho từng cảnh; sửa `video.md` tới khi khớp.
2. **Kiểm cú pháp và thời lượng**: `python tools\vi\video_ma.py projects\_video\<tên_video> --plan-only`. Đọc `thoi_luong_uoc` và cảnh báo `thoi-luong` trong `warnings` ("bớt khoảng N từ lời" hoặc "thêm khoảng N từ lời"): sửa lời hay bớt, thêm cảnh, rồi chạy lại bước này tới khi khớp. Bước này chưa cần ảnh: nhịp `anh` chưa có ảnh chỉ hiện cảnh báo "chưa có ảnh; chạy anh_vox.py trước --xem-truoc".
3. **Ảnh**: `python tools\vi\anh_vox.py projects\_video\<tên_video>` (video không có nhịp `anh` thì bỏ bước này). Lỗi `parse` ở đây là lỗi `video.md`, cùng bộ đọc với `video_ma.py`. Sửa `video.md` sau bước này (đổi số cảnh, thứ tự nhịp, mô tả `ve:`, tuỳ chọn ảnh) thì chạy lại `anh_vox.py`: `video_ma.py` báo lỗi `canh` "chưa có ảnh đã xử lý" hoặc "ảnh … đã cũ so với video.md" cho tới khi chạy (chỉ ảnh có mô tả đổi mới vẽ lại).
4. **Xem trước**: `python tools\vi\video_ma.py projects\_video\<tên_video> --xem-truoc`. Công cụ chụp mỗi cảnh hai ảnh vào `xem-truoc/`: `canh-N-giua.png` (giữa cảnh) và `canh-N.png` (cuối cảnh), không tạo giọng. Mở xem từng ảnh theo danh sách:
   - hình có khớp lời của cảnh đó không (phép thử tắt tiếng);
   - chữ có tràn ô, bị cắt hay dính nhau không;
   - vật có chồng lên nhau, che chữ hay che phụ đề không;
   - ảnh AI có chữ, chữ cái lạ, logo, viền xanh hay vật bị ăn mất không;
   - ảnh có sai ý, sai người, sai nơi, hay gây hiểu lầm không.
   Lỗi nào thì sửa `video.md` (rút chữ, đổi ô, đổi bố cục, tả lại `ve:`), chạy lại từ bước 3, xem lại đúng các cảnh đã sửa.
5. **Dựng thật**: báo người dùng một dòng rằng dựng mất khoảng 1,5 lần thời lượng video trên máy 6 lõi (video 60 giây khoảng 90 giây; chưa kể vẽ ảnh và tạo giọng), rồi chạy `python tools\vi\video_ma.py projects\_video\<tên_video>`.
6. **Gửi**: đường dẫn `video.mp4`, thời lượng thật (`thoi_luong_giay`), nội dung `video.md` dạng dễ đọc (lời từng cảnh), nguồn ảnh và số liệu, và đọc nguyên văn các dòng `warnings`. Nhắc người dùng muốn đổi chỗ nào thì nói, AI sửa `video.md` rồi dựng lại.

## Đầu ra

Thư mục của mỗi video là `projects\_video\<tên_video>\`, chứa `video.md`. Lệnh dựng là `python tools\vi\video_ma.py projects\_video\<tên_video>` (thêm `--plan-only` hoặc `--xem-truoc` theo mục "Vòng tự kiểm"). Công cụ ghi vào chính thư mục đó:

- `video.mp4`: 1920×1080 (khổ dọc 1080×1920); `do-phan-giai: 720` thì 1280×720 (khổ dọc 720×1280).
- `nguon.txt`: mô hình AI, nguồn ảnh thật, nguồn số liệu, nguồn nhạc.
- `phu-de.srt`: chỉ có khi `phu-de: file`.
- `giong\canh-N.mp3`: giọng từng cảnh. Lần dựng sau, cảnh có lời không đổi dùng lại giọng cũ. Người dùng gửi giọng thu sẵn thì đặt vào `giong\canh-N.mp3` đúng số cảnh; công cụ không bao giờ ghi đè file đó, và chỗ vật hiện ra chạy theo mốc ước lượng (có cảnh báo).
- `anh\ai\ke-hoach.json`, `anh\ai\goc\`, `anh\ai\xu-ly\`, `anh\ai\vox.json`, `anh\ai\nguon.json`: kế hoạch, ảnh gốc, ảnh đã xử lý, bảng ảnh và nguồn do `anh_vox.py` ghi.
- `xem-truoc\canh-N-giua.png`, `xem-truoc\canh-N.png`: ảnh xem trước.

Nhạc nền chỉ khi người dùng xin: tải bằng `python tools\vi\tim_nhac.py "<từ khoá tiếng Anh>" -o projects\_video\<tên_video>\nhac` (chỉ bản CC0 hoặc CC BY trên Openverse, dài từ 60 giây; nguồn tự ghi vào `nhac/nguon.json`), ghi `nhac-nen: <tên trong files>`, và gửi tên bài, tác giả, giấy phép kèm video để người dùng nghe thử; không ưng thì tải bản khác rồi dựng lại. `error.step` của `tim_nhac.py`: `mang` thì kiểm mạng rồi chạy lại, tối đa một lần; `input`, `write` thì làm theo `error.fix`. Nhạc người dùng gửi: chép vào `nhac/` và ghi `nguon-nhac:` theo lời họ. Thấy ồn thì ghi `am-thanh: khong` hoặc bỏ dòng `nhac-nen` rồi dựng lại.

Dòng JSON của `video_ma.py`: `ready`, `files`, `so_canh`, `thoi_luong_giay`, `thoi_luong_uoc` (chỉ ở `--plan-only`), `phong_cach`, `giong` (`may`, `co-san` hoặc `hon-hop`), `warnings`, `error`.

| `error.step` | Xử lý |
|---|---|
| `input` | Chưa có thư mục hoặc `video.md`, hoặc sai tham số lệnh: viết file rồi chạy lại. |
| `parse` | Sửa đúng dòng `error.message` nêu (cụm không có trong lời, nhịp sai thứ tự, ô sai với bố cục, chữ quá giới hạn, khoá không dùng với Vox) rồi chạy lại. |
| `canh` | Cảnh sai khi kiểm hay khi xem trước: nhịp chưa có ảnh đã xử lý hay ảnh đã cũ so với `video.md` (chạy lại `anh_vox.py`), chữ của nhịp tràn ô, hai vật đè lên nhau quá nhiều, hoặc lỗi file nhạc ("Cảnh 0: nhạc nền: …"). Sửa đúng cảnh đó theo `error.fix`. |
| `giong` | Không tạo được giọng: giọng Thu Giang lỗi thì kiểm VieNeu (biến môi trường `VIENEU_PYTHON`) hoặc ghi `giong: nu`; giọng edge-tts cần mạng, kiểm mạng rồi chạy lại, tối đa một lần; hoặc đặt file giọng người dùng gửi đúng tên `error.message` nêu. |
| `chromium` | Chưa cài Chromium: hỏi người dùng trước (tải 150–300 MB), rồi chạy `powershell -NoProfile -ExecutionPolicy Bypass -File tools\vi\pptmaster.ps1 -Action tool -Name chromium`. |
| `ffmpeg` | Chưa có FFmpeg: cài theo mục "Công cụ tuỳ chọn" của `docs/vi/cai-dat-bang-ai.md`. |
| `dung` | Chụp khung hoặc ghép hỏng: báo nguyên `error.message`, không tự sửa. |
| `write` | Không ghi được file: xin người dùng đóng `video.mp4` nếu đang mở, kiểm ổ đĩa còn chỗ, rồi chạy lại. |
| `internal` | Lỗi ngoài dự kiến: dán nguyên `error.message` để báo người bảo trì, không tự đoán cách sửa. |

Dòng JSON của `anh_vox.py`: `ready`, `files`, `so_anh`, `da_ve`, `dung_lai`, `ke_hoach`, `warnings`, `error`.

| `error.step` | Xử lý |
|---|---|
| `input` | Chưa có thư mục hay `video.md`, video không phải `phong-cach: vox`, thiếu file ảnh người dùng trong `anh/`, hoặc số ảnh cần vẽ quá giới hạn: làm theo `error.fix` (bớt nhịp `anh: ve:` hoặc thêm `--toi-da N`). |
| `parse` | Sửa đúng dòng `error.message` nêu trong `video.md` rồi chạy lại. |
| `cau-hinh` | Khoá thiếu hoặc bị từ chối (401), khoá có ký tự lạ, hoặc file cấu hình hỏng hay sai dạng: nhờ người dùng tự đặt `ANH_AI_KEY` theo `error.fix`; chưa được thì làm theo nguồn 3 ở mục "Ảnh". |
| `mang` | Không gọi được nguồn vẽ (9router chưa chạy, sai `ANH_AI_URL`) hoặc không tải được ảnh thật: kiểm rồi chạy lại, tối đa một lần; ảnh thật thì đổi từ khoá `tim:`. |
| `nha-cung-cap` | Nguồn vẽ báo lỗi (hết hạn mức, từ chối câu lệnh, mô hình không có), trả dữ liệu không phải ảnh, hoặc ảnh thật chưa có nguồn: đọc nguyên văn lỗi; câu lệnh bị từ chối thì tả lại `ve:`, hết hạn mức thì báo người dùng (có thể đổi `ANH_AI_MO_HINH`). |
| `tach-nen` | Máy chưa có FFmpeg: cài theo mục "Công cụ tuỳ chọn" của `docs/vi/cai-dat-bang-ai.md`. FFmpeg không tách nền được một ảnh hoặc ảnh gốc hỏng: xoá ảnh đó trong `anh/ai/goc/` để vẽ lại, hoặc thêm `khung` cho nhịp đó. |
| `write` | Không ghi được file: đóng file đang mở, kiểm ổ đĩa rồi chạy lại. |
| `internal` | Lỗi ngoài dự kiến: dán nguyên `error.message` để báo người bảo trì, không tự đoán cách sửa. |

Không tự chạy FFmpeg, không tự ghép hay cắt video theo cách riêng. Không viết HTML hay ảnh cảnh bằng tay, không sửa khung hình hay ảnh đã xử lý: mọi thay đổi đi qua `video.md` rồi chạy lại công cụ. Ngoại lệ duy nhất: dùng công cụ vẽ ảnh của nền tảng để vẽ ảnh gốc vào `anh/ai/goc/` theo `ke-hoach.json`.

## Ghi vào brief

- Loại việc: Video giải thích dựng bằng mã (kiểu Vox).
- Ghi brief vào `projects/_video/<tên_video>/brief.md`: chủ đề và nội dung người dùng đưa (nguyên văn), thời lượng, khổ, các mặc định đã dùng và ghi "(AI đề xuất, chưa duyệt)" cho điều người dùng không nói.
- Ghi thêm: mạch kể (móc, vấn đề, các ý, lật, chốt), nguồn của từng con số, nguồn vẽ ảnh và mô hình, từ khoá ảnh thật, nhạc nền nếu có.
- Loại việc này không tạo PPTX: không chạy `import-sources`, không có bước xác nhận của upstream, không có dòng chốt cách xác nhận, không mở trang web xác nhận.
- Viết theo mẫu `docs/vi/tro-ly/mau-brief.md`.

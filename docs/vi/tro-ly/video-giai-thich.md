# Loại việc: Video giải thích dựng bằng mã (kiểu Vox)

File dành cho AI. Đọc cùng `docs/vi/tro-ly/nhip-vox.md` (ngữ pháp dòng `nhip`, bảng vật, bố cục và ô). Đầu ra là một video MP4 kiểu Vox: giấy cắt dán nhiều lớp, ảnh cắt nền viền giấy xé, chữ và con dấu đập xuống đúng lúc giọng đọc nói tới. Không phải PPTX.

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
| Giọng | giọng nữ, tốc độ vừa (`giong: nu`, `toc-do: vua`) |
| Phụ đề | `karaoke` (in lên hình, tô vàng từng từ) |
| Tiếng hiệu ứng | có (`am-thanh: co`) |
| Nhạc nền | không; chỉ thêm khi câu lệnh xin |
| Kiểu ảnh | `phong-anh: chup-that`; "minh hoạ", "hoạt hình", "tranh" thì `minh-hoa` |

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

Quỹ từ theo thời lượng (giọng vừa đọc khoảng 2,7 từ mỗi giây, mỗi cảnh thêm khoảng 1,1 giây dẫn vào và nghỉ):

| `thoi-luong` | Số từ của toàn bộ lời | Số cảnh |
|---|---|---|
| 30 giây | ≈ 65 từ | 3–4 cảnh |
| 60 giây | ≈ 130 từ | 5–7 cảnh |
| 2 phút | ≈ 270 từ | 10–14 cảnh |
| 3 phút | ≈ 410 từ | 15–20 cảnh |

Tự ước trước khi chạy lệnh nào: thời lượng ≈ số từ ÷ 2,7 + 1,1 giây × số cảnh (tốc độ `cham` đọc 2,4 từ mỗi giây, `nhanh` 3,1). Mỗi cảnh dài 5–12 giây, tức khoảng 11–30 từ lời. Đếm từ như giọng đọc: mỗi tiếng cách nhau một khoảng trắng là một từ.

Lời:
- Câu ngắn, tối đa khoảng 15 từ, giọng kể như nói với một người ngồi đối diện ("bạn"). Mỗi câu một ý.
- Viết để đọc thành tiếng: chữ viết tắt, kí hiệu viết thành chữ đọc được; có dấu phẩy ở chỗ ngắt tự nhiên để phụ đề ngắt đẹp.
- `loi` mỗi cảnh 1–3 câu, viết trên một dòng.
- Người dùng đưa nội dung thì giữ đúng ý, thuật ngữ và số liệu của họ; chỉ viết lại thành lời kể ngắn.

**Không bịa số liệu.** Chỉ dùng con số người dùng đưa, hoặc con số tra được ở một nguồn gọi tên được (luật, cơ quan thống kê, nghiên cứu, tài liệu chính thức). Cảnh có số thì có dòng `nguon:` ghi nguồn đó, tối đa 90 ký tự. Không có nguồn thì nói bằng lời không có số, và không khẳng định mức độ mình không kiểm được: "nhiều người" thay vì "85% người". Con số minh hoạ trong một tình huống giả định ("hạn 17 giờ thứ Sáu") không phải số liệu, nhưng không được trông như kết quả khảo sát.

## Hình khớp thoại

- Mỗi câu của lời có ít nhất một nhịp. Nhịp gắn vào đúng từ gọi tên sự vật: lời nói "cốc cà phê nguội" thì ảnh cốc cà phê hiện ra đúng lúc giọng đọc tới "cốc cà phê".
- **Phép thử tắt tiếng**: tắt tiếng đi, người xem vẫn đoán được mỗi cảnh nói gì. Trước khi chạy lệnh, viết cho từng cảnh một dòng nháp "lời nói gì — hình cho thấy gì"; hình không cho thấy ý của lời thì đổi hình.
- Chữ trên hình tối đa khoảng 6 từ, là ý chốt hay nhãn, không chép lại lời (lời đã có ở phụ đề). Mỗi cảnh tối đa 2 dòng `chu`.
- `ve:` tả **vật, hành động và góc chụp** cụ thể: "bàn tay cầm điện thoại, màn hình sáng một bong bóng tin nhắn, chụp từ trên xuống" thay vì "giao tiếp hiện đại". Ảnh cắt nền chỉ một vật chính. Không tả không khí chung, không xin chữ, biển hiệu hay màn hình có chữ: ảnh AI không được có chữ.
- Người, địa danh, công trình, sự kiện, sản phẩm có thật: dùng ảnh thật `anh: tim: <từ khoá tiếng Anh>`, không để AI vẽ giả.
- Ý trừu tượng thì tìm vật ví von. Không tìm được vật nào đúng thì dùng `the`, `dau` hoặc `chu`, không chèn ảnh cho có.
- Ảnh cắt nền được tách trên nền xanh lá: vật màu xanh lá (cây, lá, chai xanh, logo xanh) bị ăn mất một phần. Tả vật đó màu khác, hoặc thêm tuỳ chọn `khung`.
- Hai cảnh liền nhau không dùng cùng một bố cục và cùng kiểu vật; đổi nhịp cho mắt nghỉ.

## Chọn bố cục

| Ý của cảnh | `bo-cuc` | Cách dùng |
|---|---|---|
| Một vật, một khái niệm, một câu chốt | `mot` | ảnh ở `giua`, chữ ngắn ở `tren` hoặc `duoi` |
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
| `giong` | không | `nu` (mặc định) hoặc `nam` |
| `toc-do` | không | `cham`, `vua` (mặc định) hoặc `nhanh` |
| `phu-de` | không | `karaoke` (mặc định: in lên hình, tô vàng từng từ, một dòng một lúc), `hinh` (cả câu một màu), `file` (file `phu-de.srt` riêng) hoặc `khong` |
| `am-thanh` | không | `co` (mặc định: tiếng đập, tiếng dán, tiếng chuyển cảnh, luôn nhỏ hơn giọng đọc) hoặc `khong` |
| `phong-anh` | không | `chup-that` (mặc định: ảnh AI kiểu ảnh chụp thật) hoặc `minh-hoa` (tranh minh hoạ phẳng, màu tươi); áp cho mọi ảnh AI của video |
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
- `nguon:` tuỳ chọn, bắt buộc khi cảnh có số liệu: dòng nguồn hiện nhỏ ở góc dưới, tối đa 90 ký tự.

Cảnh Vox không có dòng `loai:`. Không chèn địa chỉ web vào file: công cụ báo lỗi `parse`.

### Ví dụ đầy đủ: "Giao tiếp với đồng nghiệp", 60 giây

Bảy cảnh, 137 từ lời, ước khoảng 58 giây. Mạch: móc (Cảnh 1) → vấn đề (2) → ba ý, mỗi ý một hình (3, 4, 5) → lật (6) → chốt (7). Không có số liệu nên không cần `nguon`; "17 giờ thứ Sáu" chỉ là một hạn trong tình huống mẫu.

```
---
tieu-de: Giao tiếp với đồng nghiệp
phong-cach: vox
thoi-luong: 60
kho: ngang
phong-anh: chup-that
bang-mau: kem
---

## Cảnh 1
bo-cuc: hai-ben
loi: Bạn nhắn "để mai tính". Đồng nghiệp lại đọc thành "anh ấy không định làm". Cả hai cùng bực, mà không ai nói ra.
nhip: để mai tính | anh: ve: bàn tay cầm điện thoại, màn hình sáng một bong bóng tin nhắn ngắn không chữ, chụp từ trên xuống | trai
nhip: không định làm | anh: ve: người đàn ông mặc sơ mi khoanh tay, nhíu mày nhìn màn hình laptop, góc ngang tầm mắt | phai
nhip: không ai nói ra | dau: IM LẶNG | giua

## Cảnh 2
bo-cuc: mot
loi: Tin nhắn càng ngắn, người đọc càng phải tự đoán phần còn thiếu. Mà khi đang mệt, người ta hay đoán theo hướng xấu.
nhip: càng ngắn | nhan: Càng ngắn càng mơ hồ | tren
nhip: tự đoán | anh: ve: người phụ nữ văn phòng cau mày nhìn một tờ giấy nhớ trống dán trên màn hình máy tính, góc ngang vai | giua
nhip: hướng xấu | chu: Thiếu chữ thì thừa đoán | duoi

## Cảnh 3
bo-cuc: dan-hang
loi: Một lời nhắn rõ trả lời đủ ba câu: việc gì, xong lúc nào, ai làm.
nhip: việc gì | the: Việc gì | Báo cáo quý | 1
nhip: lúc nào | the: Xong lúc nào | 17 giờ thứ Sáu | 2
nhip: ai làm | the: Ai làm | Chị Lan | 3

## Cảnh 4
bo-cuc: hai-ben
loi: Chưa chắc thì hỏi lại một câu. Hỏi mất mười giây, đoán sai có khi mất cả buổi chiều.
nhip: hỏi lại | dau: HỎI LẠI | giua
nhip: mười giây | anh: ve: chiếc đồng hồ bấm giây nhỏ màu bạc trên mặt bàn gỗ, chụp cận | trai
nhip: cả buổi chiều | anh: ve: chồng giấy tờ cao ngất nghiêng như sắp đổ, cạnh cốc cà phê đã nguội, chụp chéo từ trên | phai

## Cảnh 5
bo-cuc: toan-canh
loi: Chuyện dễ hiểu lầm thì đừng gõ chữ. Đi tới bàn, nói thẳng, rồi nhắn lại một dòng tóm tắt.
nhip: @dau | anh: ve: góc văn phòng sáng, hai đồng nghiệp ngồi đối diện qua bàn làm việc đang trò chuyện, góc rộng | nen
nhip: đừng gõ chữ | chu: Gặp mặt trước | giua
nhip: tóm tắt | nhan: Rồi nhắn một dòng chốt | duoi

## Cảnh 6
bo-cuc: hai-ben
chuyen: lia
loi: Nghe thì tốn công hơn. Thật ra đó là đường nhanh nhất để khỏi phải làm lại.
nhip: tốn công | anh: ve: con rùa gỗ màu nâu bò trên mặt bàn làm việc, chụp cận ngang mặt bàn | trai
nhip: nhanh nhất | chu: Chậm một nhịp, khỏi làm lại | phai

## Cảnh 7
bo-cuc: mot
loi: Lần tới, trước khi bấm gửi, hãy đọc lại tin nhắn như thể bạn là người nhận.
nhip: bấm gửi | anh: ve: ngón tay dừng lơ lửng trên màn hình điện thoại, chụp cận nghiêng | giua
nhip: người nhận | dau: ĐỌC LẠI | tren
```

## Ảnh

Mọi ảnh của nhịp `anh` đi qua `tools/vi/anh_vox.py`: lệnh lập danh sách ảnh, lấy ảnh từ nguồn dùng được đầu tiên dưới đây, tách nền hoặc làm khung, tính trước viền giấy xé, bóng, `duotone`, `halftone`, và ghi nguồn. `video_ma.py` chỉ đọc kết quả, không bao giờ gọi AI hay lên mạng tìm ảnh. Có `venv\Scripts\python.exe` ở thư mục gốc repo thì dùng nó thay cho `python`.

Nguồn ảnh AI, theo thứ tự:

1. **Công cụ vẽ ảnh của chính nền tảng** (Antigravity, Codex app). Chạy `python tools\vi\anh_vox.py projects\_video\<tên_video> --chi-ke-hoach`, đọc `anh/ai/ke-hoach.json`: mỗi mục có `nguon: "ve"` có `ma`, `prompt` (dán nguyên văn, không dịch, không bớt), `kich_thuoc` và `file_goc`. Vẽ từng mục, 3–4 ảnh một lượt, lưu đúng tên `anh/ai/goc/<ma>.png`. Rồi chạy `anh_vox.py` với `--cong-cu "<nền tảng>" --mo-hinh "<mô hình đã vẽ>"` (ví dụ `--cong-cu Antigravity --mo-hinh "Nano Banana Pro"`): ảnh có sẵn được dùng, không vẽ lại, và cuối video ghi đúng mô hình. Không biết tên mô hình thì bỏ hai cờ: ảnh được ghi "không rõ" mô hình ("chưa rõ mô hình" trong `warnings`); chạy lại với `--mo-hinh` sau cũng điền được.
2. **API tạo ảnh kiểu OpenAI** (cách của Claude Code và mọi nền tảng không tự vẽ được). Cấu hình đọc theo thứ tự: biến môi trường `ANH_AI_URL`, `ANH_AI_KEY`, `ANH_AI_MO_HINH`, rồi file `%USERPROFILE%\.2anh-studio\anh-ai.json` (khoá `url`, `khoa`, `mo_hinh`). Mặc định là 9router trên máy, `http://localhost:20128/v1`, mô hình `ag/gemini-3.1-flash-image` (khoảng 15 giây một ảnh). Khoá API chỉ nằm ở biến môi trường hay file cấu hình trong thư mục người dùng: không ghi khoá vào file nào trong repo hay trong `projects/`, không in ra, không xin người dùng dán khoá vào khung chat. Thiếu khoá thì chỉ người dùng tự đặt: `setx ANH_AI_KEY "<khoá>"` rồi mở lại cửa sổ lệnh.
3. **Không có nguồn vẽ nào** (lỗi `cau-hinh` mà người dùng chưa đặt khoá được): thay nhịp `anh: ve:` bằng `chu`, `the`, `dau`, `so`, hoặc ảnh thật `tim:` khi sự vật có thật; báo người dùng một dòng rằng video chưa có ảnh AI và cách đặt khoá.

Ảnh thật (`anh: tim: <từ khoá tiếng Anh>`): `anh_vox.py` tự chạy `skills/ppt-master/scripts/image_search.py` tải ảnh giấy phép mở vào `anh/`, nguồn lấy từ `anh/image_sources.json` và hiện cạnh ảnh. Từ khoá tiếng Anh, cụ thể ("Hoan Kiem Lake Hanoi" thay vì "lake"). Ảnh thật và ảnh người dùng gửi (tên file trong `anh/`) luôn ở dạng `khung`. Không dùng ảnh không rõ nguồn.

Lưu đệm và giới hạn:
- Mỗi ảnh AI có mã băm theo câu lệnh và khổ. Sửa mô tả một nhịp thì chỉ ảnh đó vẽ lại; đổi `ANH_AI_MO_HINH` thì ảnh vẽ bằng mô hình cũ được vẽ lại (trừ ảnh nền tảng vẽ).
- Mỗi lần chạy vẽ tối đa 20 ảnh mới (`--toi-da N` để nâng), 3 ảnh song song; lỗi mạng hay lỗi máy chủ tự thử lại 2 lần.
- Ảnh cắt nền tách không sạch thì tự vẽ lại một lần với nền xanh chặt hơn; vẫn hỏng thì chuyển nhịp đó sang `khung` kèm một dòng `warnings`.
- Câu lệnh luôn cấm chữ, nhưng ảnh AI vẫn có thể có chữ lạ hay sai ý: chỉ phát hiện được bằng mắt ở bước xem trước. Sửa mô tả `ve:` (thêm chi tiết, bỏ thứ dễ sinh chữ như biển hiệu, giấy có chữ) rồi chạy lại `anh_vox.py`.
- Cuối video hiện "Hình minh hoạ tạo bằng AI (<mô hình>)". `anh/ai/nguon.json` và `anh/ai/vox.json` do `anh_vox.py` ghi; không tự viết hay sửa hai file này.

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
| `canh` | Cảnh sai khi kiểm hay khi xem trước: nhịp chưa có ảnh đã xử lý hay ảnh đã cũ so với `video.md` (chạy lại `anh_vox.py`), chữ của nhịp tràn ô, hai vật đè lên nhau quá nhiều, dòng nguồn tràn khung, hoặc lỗi file nhạc ("Cảnh 0: nhạc nền: …"). Sửa đúng cảnh đó theo `error.fix`. |
| `giong` | Không tạo được giọng máy (edge-tts cần mạng): kiểm mạng rồi chạy lại, tối đa một lần; hoặc đặt file giọng người dùng gửi đúng tên `error.message` nêu. |
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

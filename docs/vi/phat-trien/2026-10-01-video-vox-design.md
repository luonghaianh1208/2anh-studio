# Video Vox — thiết kế (6.3.2-vi.15)

Ngày: 2026-10-01. Trạng thái: chờ chủ repo duyệt.

## 1. Vì sao làm

Chủ repo ra lệnh "tạo 1 video dạng vox chủ đề giao tiếp với đồng nghiệp dài 60s video ngang 16:9". Kết quả (`projects/_video/giao-tiep-dong-nghiep/`) sai ở hai chỗ.

- **Dài 1 phút 55 giây.** Kịch bản có 9 cảnh và 288 từ lời. Giọng máy tốc độ vừa đọc khoảng 2,7 từ/giây, nên riêng tiếng đã 105 giây. Hướng dẫn không có quỹ từ theo thời lượng, và công cụ không biết thời lượng mong muốn.
- **Kịch bản bó theo khuôn bài giảng.**
  - `mon`, `lop` bắt buộc.
  - Hướng dẫn buộc mở bằng cảnh `tieu-de` và chốt bằng tóm tắt, gợi ý luôn có câu hỏi nhanh.
  - Nội dung đổ vào các khuôn `khai-niem`, `y-tung-y`, `quy-trinh`.
  - Nền lấy từ 8 nền mẫu, nên chuyện công sở lại ra nền lớp học.
  - Có số liệu "85%" không rõ nguồn.

Chủ repo muốn bộ công cụ không gắn với ngành hay lĩnh vực nào, và không cần kho mẫu. Ảnh tạo qua API 9router hoặc Codex CLI, kể cả khi chạy trong Claude Code. Video giải thích chỉ còn **một lối là Vox**; trọng tâm là kịch bản, bố cục và hình hiện khớp với lời thoại.

## 2. Quyết định đã chốt

| Câu hỏi | Chốt |
|---|---|
| Kiểu viết tay và các khuôn cảnh cũ | Vẫn dựng được (`video.md` cũ không hỏng, test cũ giữ nguyên) nhưng không còn trong hướng dẫn và luật. |
| Nguồn ảnh | AI trước: công cụ vẽ của nền tảng → API kiểu OpenAI (mặc định 9router, mô hình `ag/gemini-3.1-flash-image`). Người, địa danh, sự kiện có thật thì dùng ảnh thật giấy phép mở. Codex CLI bỏ khỏi chuỗi (máy chủ repo chưa cài, không kiểm được). |
| Cách tả cảnh | Nhịp theo lời thoại: mỗi nhịp gắn một cụm từ trong lời và nói hiện vật gì ở ô nào. |
| Hỏi và duyệt | Chỉ hỏi khi câu lệnh thiếu chủ đề hoặc nội dung. Không dừng chờ duyệt; AI tự xem trước, tự sửa, dựng rồi gửi video kèm kịch bản. Người dùng xin xem kịch bản trước thì mới dừng. |

## 3. Kiến trúc

Giữ đường dựng của `tools/vi/video_ma.py`: parse → kiem → giong (edge-tts, mốc từng từ) → lich → trang → chup (beginFrame) → ghep (FFmpeg, karaoke một dòng, nhạc nền, hiệu ứng âm).

Thêm:

1. `phong-cach: vox` trong `video.md`. Cảnh của video Vox không có `loai:`; mỗi cảnh là `loi` + `bo-cuc` + các `nhip`.
2. Lớp dựng hình Vox trong runtime (file JS và CSS mới cạnh `cat-dan.js`), phát triển từ bản thử 15 giây hôm 2026-10-01.
3. `tools/vi/anh_vox.py`: lập danh sách ảnh từ các nhịp, tạo ảnh, tách nền, ghi nguồn.
4. Kiểm thời lượng theo khoá `thoi-luong`.
5. Hướng dẫn mới cho AI và luật đổi theo.

Hai phong cách cũ (`viet-tay`, `cat-dan`) chạy như trước. Lớp Vox không sửa hành vi của chúng.

## 4. Định dạng `video.md` cho Vox

### 4.1 Khối thông tin

| Khoá | Bắt buộc | Giá trị |
|---|---|---|
| `tieu-de` | có | tên video |
| `phong-cach` | có | `vox` |
| `thoi-luong` | không | số giây mong muốn, 15–600. Có thì công cụ kiểm thời lượng (mục 7). |
| `kho` | không | `ngang` (mặc định) hoặc `doc` |
| `do-phan-giai` | không | `1080` (mặc định) hoặc `720` |
| `giong`, `toc-do`, `phu-de`, `am-thanh`, `nhac-nen`, `nguon-nhac`, `loat` | không | như hiện nay |
| `phong-anh` | không | `chup-that` (mặc định) hoặc `minh-hoa`; đuôi câu lệnh chung cho mọi ảnh AI |
| `bang-mau` | không | một trong vài bộ màu giấy có sẵn (`kem` mặc định, `bao-cu`, `dem`, `tuoi`) |
| `chuyen-canh` | không | `xen-ke` (mặc định: xé giấy và lia nhanh xen nhau), `xe-giay`, `lia` hoặc `khong` |

Với `phong-cach: vox`, `mon` và `lop` không bắt buộc (mọi phong cách khác vẫn bắt buộc như cũ). `ban-tay`, `nhan-vat`, `mau-ao`, `chu-dong`, `may-quay` không dùng; có ghi thì là lỗi `parse` kèm gợi ý bỏ.

### 4.2 Cảnh

```
## Cảnh 2
bo-cuc: hai-ben
loi: Bạn nói "để mai tính", đồng nghiệp lại hiểu là "không làm".
nhip: để mai tính | anh: ve: nhân viên văn phòng nhún vai, tay cầm cốc cà phê | trai
nhip: hiểu | dau: HIỂU LẦM | giua
nhip: không làm | anh: ve: đồng nghiệp khoanh tay, nhíu mày | phai
```

- `loi`: 1–3 câu, viết trên một dòng.
- `bo-cuc`: `mot`, `hai-ben`, `dan-hang`, `chong` hoặc `toan-canh`.
- `nhip`: 1–6 dòng, dạng `<cụm từ> | <vật>: <nội dung> | <ô> | <tuỳ chọn>`. Có thể bỏ ô (công cụ chọn ô trống kế tiếp) và bỏ tuỳ chọn.
- `chuyen`: tuỳ chọn, đổi kiểu chuyển vào cảnh này.
- `nguon`: tuỳ chọn, dòng nguồn số liệu của cảnh (tối đa 90 ký tự), hiện nhỏ ở góc dưới.

### 4.3 Cụm từ và thời điểm

- Cụm từ phải có trong `loi`, so sau khi chuẩn hoá NFC, chữ thường và bỏ dấu câu, theo đúng cách khớp cụm nhấn hiện có (`lich.khoa_so_khop`).
- Vật hiện khi giọng đọc tới từ đầu của cụm, theo mốc từng từ của edge-tts. Giọng thu sẵn thì dùng mốc ước lượng như hiện nay.
- `@dau`: hiện ngay khi vào cảnh, sau đoạn dẫn đầu.
- Cụm cùng xuất hiện nhiều lần trong lời: lấy lần đầu chưa dùng, sau cụm của nhịp trước.
- Lỗi `parse`: cụm không có trong lời; các nhịp không theo thứ tự lời; cảnh không có nhịp nào.

### 4.4 Vật

| Vật | Nội dung | Giới hạn | Kiểu vào mặc định |
|---|---|---|---|
| `anh` | `ve: <mô tả>` (AI vẽ, tối đa 300 ký tự), `<tên file>` trong `anh/`, hoặc `tim: <từ khoá tiếng Anh>` (ảnh thật) | | Cắt nền: bay vào rồi đập xuống, có nảy và bóng đổ. Khung: rơi xoay nhẹ, rồi băng dính dán lên. |
| `the` | `nhãn \| giá trị \| chú thích` | 24 / 16 / 60 ký tự | trượt vào |
| `chu` | dòng chữ lớn | 40 ký tự; tối đa 2 dòng `chu` mỗi cảnh | hiện từng từ |
| `nhan` | nhãn băng dính | 30 ký tự | dán |
| `dau` | con dấu | 16 ký tự | đóng mạnh, máy rung |
| `mui-ten` | `<ô> -> <ô>` | | vẽ dần |
| `so` | `{{số}}` kèm chữ trước hoặc sau | 24 ký tự | chạy số từ 0 |

Chữ đếm ký tự hiện ra như luật giới hạn hiện có. Vượt giới hạn là lỗi `canh`.

### 4.5 Bố cục và ô

| Bố cục | Ô ngang | Ô dọc | Hợp với |
|---|---|---|---|
| `mot` | `giua`, `tren`, `duoi` | `giua`, `tren`, `duoi` | một vật hay một khái niệm |
| `hai-ben` | `trai`, `phai`, `giua` | `tren`, `duoi`, `giua` | so sánh, đối lập |
| `dan-hang` | `1`–`4` | `1`–`4` (xếp dọc) | danh sách, các bước |
| `chong` | tự xếp lệch nhau theo seed của cảnh, tối đa 5 vật | như ngang | nhiều yếu tố rối rắm |
| `toan-canh` | `nen` (ảnh phủ kín khung) + `giua`, `duoi` | như ngang | nơi chốn, bối cảnh |

Ô sai với bố cục là lỗi `parse` kèm danh sách ô đúng. Toạ độ ô nằm trong `runtime/o-bo-cuc.json` cạnh các ô hiện có.

### 4.6 Tuỳ chọn của nhịp

- `khung`: ảnh trong khung chữ nhật mép xé thay vì cắt nền. Ảnh thật và `toan-canh` luôn là khung.
- `duotone`, `halftone`: xử lý in cho ảnh.
- `xa`, `gan`: đổi lớp chiều sâu (mặc định: ảnh ở lớp giữa, chữ, thẻ và dấu ở lớp gần).

## 5. Lớp dựng hình Vox

Mọi khung là hàm thuần của thời điểm t (`datThoiDiem(t)`). Ngẫu nhiên đều có seed theo số cảnh và số nhịp (mulberry32 như `cat-dan.js`).

- **Nền:** giấy có vân theo `bang-mau`, 3–5 mảng giấy xé màu (đa giác mép răng cưa, có sọc hoặc chấm halftone), vị trí theo seed của cảnh.
- **Ảnh cắt nền:** viền giấy xé trắng ngà bao quanh vật. Viền được tính trước ở bước `anh_vox.py` thành PNG (giãn mặt nạ alpha, mép răng cưa theo seed, thớ giấy), không tính lại ở mỗi khung. Có bóng đổ.
- **Ảnh khung:** chữ nhật mép xé 1–2 cạnh, một hoặc hai băng dính. `duotone` và `halftone` cũng tính trước thành PNG.
- **2,5D:** ba lớp sâu (nền giấy xa, mảng giấy giữa, vật gần) trong `perspective`. Camera đẩy từ 1,00 lên 1,06 suốt cảnh, xoay `rotateY` tối đa ±4°; mỗi lớp lệch theo độ sâu. Lớp xa mờ nhẹ, cũng tính trước, không dùng `filter: blur` theo khung.
- **Chuyển động vào:** theo mục 4.4, easeOutBack có nảy. Vật đập xuống kéo theo rung máy 0,15 giây, biên độ tối đa 6 px, theo seed.
- **Chuyển cảnh:** `xe-giay` (có sẵn) và `lia` (trượt nhanh có nhoè hướng, 0,35 giây).
- **Phụ đề:** karaoke một dòng có khung nền tối, như `cat-dan`.
- **Hiệu năng:** bóng đổ, viền xé và độ mờ đều tính trước, để tốc độ dựng không chậm quá 1,5 lần so với `cat-dan` hiện nay (bản thử tính lại mỗi khung, chậm khoảng 7,5 lần thời lượng).
- **Đo tràn** (`kiemTran`): chữ tràn ô, vật đè lên phụ đề, hai vật chồng quá 30% diện tích (trừ bố cục `chong`).

## 6. `tools/vi/anh_vox.py`

`python tools\vi\anh_vox.py <thư mục video> [--chi-ke-hoach] [--toi-da N]` in một dòng JSON: `ready`, `files`, `so_anh`, `da_ve`, `dung_lai`, `ke_hoach`, `warnings`, `error`.

1. **Lập danh sách** từ mọi nhịp `anh: ve:` và `anh: tim:`. Ghi `anh/ai/ke-hoach.json`, gồm mã băm, câu lệnh đầy đủ, khổ và kiểu (cắt nền hay khung) của từng ảnh.
   - Khổ: cắt nền 1024×1024; khung và `toan-canh` 1536×1024 (ngang) hoặc 1024×1536 (dọc).
   - Câu lệnh = mô tả + đuôi `phong-anh` + với ảnh cắt nền "một vật duy nhất, nền xanh lá thuần #00FF00, không bóng, không viền" + luôn "không có chữ, không có chữ cái".
2. **Lưu đệm:** mã băm = SHA-256 của (câu lệnh, khổ), để `video_ma.py` tính lại được tên file mà không cần đọc cấu hình. Đã có `anh/ai/goc/<mã>.png` vẽ bằng đúng mô hình đang cấu hình (so với `nguon.json`) thì không vẽ lại; đổi mô hình thì vẽ lại.
3. **Chọn nguồn vẽ** (dừng ở nguồn đầu tiên dùng được):
   1. Ảnh do nền tảng vẽ sẵn: `anh/ai/goc/<mã>.png` đã có, do AI dùng công cụ vẽ của Antigravity hoặc Codex app lưu vào theo `ke-hoach.json`.
   2. API kiểu OpenAI `POST {url}/images/generations`, thân `{model, prompt, size, n: 1}`, nhận `b64_json` hoặc `url`. Cấu hình lấy theo thứ tự: biến môi trường `ANH_AI_URL`, `ANH_AI_KEY`, `ANH_AI_MO_HINH`, rồi file `%USERPROFILE%\.2anh-studio\anh-ai.json`. Mặc định `http://localhost:20128/v1` (9router) và `ag/gemini-3.1-flash-image`. Khoá không bao giờ nằm trong repo, log hay JSON đầu ra. Mô hình có thể trả khổ khác khổ xin: ảnh luôn được cắt phủ (cover) về đúng tỉ lệ ô.
   3. Không có nguồn nào: lỗi `cau-hinh`, `fix` gợi ý đặt `ANH_AI_KEY` (khoá API của 9router), hoặc dùng `anh: tim:`, hoặc thay ảnh bằng `chu`, `the`.
4. **Ảnh thật** (`tim:`): chạy `skills/ppt-master/scripts/image_search.py` (chỉ chạy, không sửa `skills/`) vào `anh/`, lấy nguồn từ `anh/image_sources.json`.
5. **Tách nền** ảnh cắt nền: dùng lại bộ tách nền xanh của `anh_ai.py` (FFmpeg colorkey và despill, đo màu nền). Ảnh tách không sạch thì vẽ lại một lần với câu lệnh chặt hơn; vẫn hỏng thì chuyển nhịp đó sang `khung` và ghi cảnh báo.
6. **Tính trước** viền xé, bóng đổ, duotone và halftone thành `anh/ai/xu-ly/<mã>-<kiểu>.png`, theo seed của nhịp.
7. **Giới hạn:** mặc định tối đa 20 ảnh mới mỗi lần chạy (`--toi-da`), vẽ song song 3 ảnh, mỗi ảnh tối đa 120 giây. Lỗi mạng hay lỗi 5xx thì tự thử lại 2 lần.
8. **Nguồn:** `anh/ai/nguon.json` (nguồn vẽ, mô hình, câu lệnh, ngày) do lệnh này ghi. Cuối video hiện "Hình minh hoạ tạo bằng AI (<mô hình>)" như dòng nguồn AI hiện có, cùng nguồn ảnh thật.

`error.step`: `input`, `parse`, `cau-hinh`, `mang`, `nha-cung-cap` (thông báo kèm nguyên văn lỗi của API: hết hạn mức, từ chối câu lệnh, mô hình không có), `tach-nen`, `write`, `internal`.

**Đã kiểm (2026-10-01, qua 9router trên máy chủ repo):**
- `Stali/req/gpt-image-2`: nhà cung cấp chỉ có chat, không tạo ảnh.
- `gemini/gemini-2.5-flash-image`: hạn mức gói miễn phí bằng 0.
- `cx/*` (Codex qua ChatGPT): tài khoản không đủ quyền tạo ảnh.
- `ag/gemini-3.1-flash-image` (Antigravity): **chạy được**, khoảng 15 giây mỗi ảnh, trả `b64_json` 1024×1024. Ảnh vật thể trên nền xanh tách sạch bằng bộ lọc `LOC_TACH` hiện có.

Codex CLI chưa cài trên máy chủ repo nên bỏ khỏi chuỗi.

## 7. Kiểm thời lượng

- `--plan-only`: ước tính = tổng số từ của `loi` (và `loi-giai` nếu có) ÷ tốc độ (2,7 từ/giây ở `vua`; `cham` 2,4; `nhanh` 3,1) + 1,1 giây mỗi cảnh. Số đo của video 9 cảnh, 288 từ: 105 giây tiếng, 115 giây video.
- Sau bước giọng: tính lại từ thời lượng cảnh thật.
- Có `thoi-luong`: lệch quá +15% hoặc dưới −25% thì cảnh báo, nêu số giây và khoảng số từ cần cắt hay thêm, ví dụ "Video ước 115 giây, mục tiêu 60 giây: bớt khoảng 150 từ". Đây là cảnh báo (`warnings`), không chặn; luật bắt AI sửa `video.md` trước khi dựng thật.
- Hằng số tốc độ hiệu chỉnh lại bằng ba video mẫu trong Task tương ứng.

## 8. Hướng dẫn và luật

- `docs/vi/tro-ly/video-giai-thich.md` viết lại thành hướng dẫn Vox; giữ đường dẫn để luật, link và test hiện có không vỡ. Nội dung:
  - Câu hỏi: chỉ hỏi chủ đề hoặc nội dung khi thiếu. Còn lại có mặc định: thời lượng 60 giây nếu không nói, khổ ngang, giọng nữ vừa, phụ đề karaoke, tiếng hiệu ứng có, nhạc nền không.
  - Mạch kể: móc (3 giây đầu, có hình ngay khung đầu) → vấn đề → giải thích 2–4 ý, mỗi ý một hình ví von cụ thể → lật → chốt. Không cảnh tiêu đề riêng, không "Hôm nay chúng ta…", không liệt kê "thứ nhất, thứ hai".
  - Quỹ từ: 30 giây ≈ 65 từ, 3–4 cảnh; 60 giây ≈ 130 từ, 5–7 cảnh; 2 phút ≈ 270 từ; 3 phút ≈ 410 từ. Mỗi cảnh 5–12 giây.
  - Lời: câu ngắn, tối đa khoảng 15 từ, giọng kể. Không bịa số liệu: chỉ dùng số người dùng đưa hoặc tra được nguồn, kèm `nguon`.
  - Hình khớp thoại: mỗi câu ít nhất một nhịp; phép thử tắt tiếng; chữ trên hình tối đa khoảng 6 từ, không chép lời; `ve:` nêu vật, hành động và góc chụp cụ thể.
  - Chọn bố cục theo ý (bảng mục 4.5).
  - Vòng tự kiểm: `--plan-only` → `anh_vox.py` → `--xem-truoc` → xem từng cảnh theo danh sách (khớp lời, tràn, chồng, ảnh có chữ hay sai ý, thời lượng) → sửa → dựng thật → gửi video kèm kịch bản và cảnh báo.
- `docs/vi/tro-ly/nhip-vox.md` (mới): ngữ pháp nhịp, bảng vật, bố cục, ô, tuỳ chọn, ví dụ đầy đủ một video 60 giây.
- `docs/vi/tro-ly/canh-video.md` và nội dung viết tay cũ chuyển sang `docs/vi/tham-khao/`, ghi rõ "kiểu cũ, chỉ dùng khi sửa `video.md` cũ".
- `AGENTS.vi.md` §15, `docs/vi/tro-ly/quy-trinh-hoi.md`, `docs/vi/video-giai-thich.md` (cho người dùng) và `.agents/rules/ppt-master-vi.md` sửa theo. Bỏ câu "Claude Code không vẽ thì dùng nền mẫu". Luật Antigravity vẫn dưới 12 000 byte (CRLF). Câu hỏi phân loại "video từ slide hay video mới" ở §11 giữ nguyên.
- Từ kích hoạt thêm "video vox", "kiểu vox".

## 9. Kiểm thử

- **Test đơn vị:**
  - đọc nhịp, khớp cụm từ, thứ tự nhịp, ô theo bố cục, giới hạn chữ;
  - ước tính thời lượng và cảnh báo;
  - `anh_vox.py`: chuỗi nguồn với HTTP giả lập, lưu đệm, khoá không lộ ra đầu ra, tách nền, các `error.step`.
- **Test Chromium:**
  - cùng t ra cùng byte;
  - vật hiện đúng mốc từ;
  - không tràn, đúng khổ ngang, dọc, 720 và 1080;
  - chuyển cảnh `lia`.
- **Không đổi hành vi cũ:** toàn bộ test hiện có (1420) vẫn qua; video `viet-tay` và `cat-dan` mẫu dựng ra giống trước.
- **Kiểm chứng thật:** chạy lại câu lệnh "tạo 1 video dạng vox chủ đề giao tiếp với đồng nghiệp dài 60s video ngang 16:9". Đạt khi:
  - video dài 54–66 giây;
  - mọi nhịp khớp lời, có ảnh AI từ 9router;
  - không có số liệu thiếu nguồn;
  - chủ repo xem và đồng ý.
- **Tốc độ:** video Vox 60 giây dựng không quá khoảng 1,5 lần thời lượng trên máy 6 lõi, chưa kể tạo ảnh và giọng.

## 10. Ngoài phạm vi

- Mô hình tách nền chạy trên máy (ONNX). Ảnh thật không cắt nền mà dùng khung.
- Nhân vật dẫn chuyện người que trong Vox.
- Video tư liệu, ảnh động.
- Xoá kiểu viết tay và các khuôn cảnh cũ.

## 12. Bản v2 sau góp ý của chủ repo (2026-10-02)

Chủ repo xem video kiểm chứng "Giao tiếp với đồng nghiệp" (56 giây) và nhận xét: chưa đẹp bằng video mẫu, hiệu ứng rung nhức mắt, không cần ghi nguồn ảnh hay nguồn tạo ảnh, nội dung không phong phú, ít hình, lời rời rạc ngắt quãng; dùng giọng Thu Giang của VieNeu. So khung hình với video mẫu (`video Vì sao in thêm tiền lại gây lạm phát.mp4`): mẫu có nền cắt dán do AI vẽ theo chủ đề từng cảnh (giấy cũ, tranh khắc, tiền giấy, toà nhà, tem, mảng giấy xé tông trầm), một cụm hình lớn ghép nhiều vật chiếm khoảng nửa khung, bố cục cố định (nhãn tiêu đề góc trái trên, thẻ chữ, hình lớn), gần như không chuyển động, lời liền mạch.

Quyết định đã chốt: mỗi cảnh một nền AI riêng; không hiện nguồn nào trên hình.

### 12.1 Hình
- `phong-anh` thêm giá trị `cat-dan`, là **mặc định** của Vox: đuôi câu lệnh "tranh cắt dán hỗn hợp kiểu tạp chí cổ: giấy cũ ngả màu, tranh khắc chấm lưới, mép giấy xé, tông đỏ trầm, xanh than, vàng đất, kem". `chup-that`, `minh-hoa` giữ nguyên.
- **Nền cảnh AI:** cảnh có thêm trường tuỳ chọn `nen: ve: <mô tả>`. Không ghi thì `anh_vox.py` tự lập câu lệnh nền từ `tieu-de` của video và lời của cảnh. Câu lệnh nền thêm "nền cắt dán phủ kín khung, chừa vùng sáng ít chi tiết ở giữa và bên trái để đặt chữ, không có chữ". Khổ theo khung (1536×1024 hoặc 1024×1536), xử lý trước: cắt phủ, làm tối viền nhẹ. Nền thay cho nền giấy và mảng màu vẽ bằng mã; nền vẽ bằng mã chỉ còn là đường lùi khi không có ảnh nền. Cảnh `toan-canh` có ảnh ô `nen` thì không cần nền AI riêng.
- **Hình chính:** hướng dẫn tả hình chính là một cụm nhiều vật ghép lại kiểu cắt dán ("cái cân, một bên bánh mì và thùng dầu, một bên xấp tiền"). Ô hình chính đủ lớn, khoảng 45–55% khung.
- **Bố cục `mot`** đổi toạ độ theo kiểu video mẫu: `tren` là nhãn tiêu đề góc trái trên, `duoi` là vùng thẻ/chữ bên trái, `giua` là hình chính lớn lệch phải. Các bố cục khác phóng ô ảnh lớn hơn. Toạ độ chỉnh theo mắt khi so với video mẫu.

### 12.2 Bố cục và nhịp
- Đầu mỗi cảnh phải có hình: nền, nhãn tiêu đề và hình chính dùng `@dau` hoặc cụm ở vài từ đầu lời; vật phụ hiện theo lời. `--plan-only` cảnh báo khi vật đầu tiên của cảnh (không tính nền) hiện sau hơn 1,2 giây kể từ đầu cảnh.
- Vật đã hiện thì ở lại tới hết cảnh (như hiện nay).

### 12.3 Chuyển động
- Bỏ rung máy. Bỏ lắc trái phải (sway) và độ lệch thị sai theo lắc. Giữ camera đẩy vào rất chậm, 1,00 → 1,04, bằng CSS `zoom` như hiện nay (khung vẫn tất định).
- Vật vào bằng trượt ngắn kèm mờ dần (0,5 giây, easeOutCubic, không vượt quá đích). Con dấu: mờ dần kèm thu nhỏ từ 1,15 về 1, không rung.
- Chuyển cảnh giữ `xe-giay` và `lia`.

### 12.4 Nguồn
- Không hiện trên hình: dòng "Hình minh hoạ tạo bằng AI", nguồn ảnh thật, dòng `nguon` số liệu của cảnh, dòng nguồn nhạc nền.
- `video_ma.py` ghi `nguon.txt` cạnh `video.mp4`: mô hình AI và nguồn vẽ, nguồn từng ảnh thật (giấy phép CC BY bắt buộc ghi công), nguồn số liệu từng cảnh, nguồn nhạc. Luật "Không bịa số liệu" giữ nguyên; trường `nguon` của cảnh vẫn bắt buộc khi có số và đi vào `nguon.txt`.

### 12.5 Lời liền mạch
- Với Vox, đoạn dẫn đầu cảnh 0,25 giây và đuôi cảnh 0,3 giây (thay 1,0 và 0,6), nên giữa hai cảnh chỉ nghỉ khoảng nửa giây.
- Hướng dẫn: câu 10–20 từ, nối ý bằng "nhưng", "vì thế", "mà", "thế nên"; mỗi cảnh 2–3 câu nối nhau thành một mạch; không băm thành nhiều câu cụt.
- `thoi_luong.MOI_CANH` của Vox và quỹ từ trong hướng dẫn hiệu chỉnh lại theo giọng thật.

### 12.6 Giọng Thu Giang (VieNeu)
- Khoá `giong` thêm giá trị `thu-giang` (giọng "Thu Giang" của VieNeu). Với Vox, mặc định là `thu-giang` khi máy có VieNeu, không có thì dùng `nu` (edge-tts) kèm cảnh báo.
- Python của VieNeu đọc từ biến môi trường `VIENEU_PYTHON`, mặc định `E:\vieneu-tts\Scripts\python.exe` nếu có. `video_ma` gọi một script phụ chạy bằng Python đó để đọc từng cảnh ra wav (48 kHz), rồi đổi sang mp3. Có lưu đệm theo (giọng, lời) như giọng edge.
- VieNeu không trả mốc từng từ. Mốc câu lấy bằng dò khoảng lặng (FFmpeg `silencedetect`) khớp với số câu của lời; mốc từ trong câu chia theo số ký tự. Phụ đề karaoke và lúc hiện vật dùng các mốc này, không kèm cảnh báo "ước lượng" khi khớp đủ số câu.
- Tốc độ đọc đo được khoảng 3,8 từ/giây (23 từ trong 6,1 giây). `thoi_luong.TOC_DO` có bảng riêng cho `thu-giang`, quỹ từ 60 giây khoảng 200 từ; hiệu chỉnh bằng số đo thật.

### 12.7 Kiểm chứng v2
Dựng lại "Giao tiếp với đồng nghiệp, 60 giây, ngang" theo hướng dẫn mới bằng giọng Thu Giang. Đạt khi: dài 54–66 giây; mỗi cảnh có nền AI và hình chính ngay từ đầu cảnh; không rung; không có dòng nguồn trên hình, có `nguon.txt`; lời liền mạch (giữa cảnh nghỉ ≤ 0,6 giây); chủ repo so với video mẫu và đồng ý.

## 11. Rủi ro

- Nguồn vẽ hết hạn mức hoặc tài khoản Antigravity bị khoá: Vox vẫn làm được bằng ảnh thật, `chu`, `the`, `dau`, nhưng kém sinh động. Đổi nguồn chỉ cần đổi `ANH_AI_MO_HINH` (hoặc `ANH_AI_URL`).
- Ảnh AI có chữ hoặc sai ý: không kiểm tự động được; AI phải xem ở bước xem trước.
- Chi phí tạo ảnh: giới hạn 20 ảnh mỗi lần chạy, lưu đệm theo mã băm.
- Tách nền xanh hỏng với vật có màu xanh lá: tự chuyển sang `khung` và cảnh báo.

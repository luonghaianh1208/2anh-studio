---
name: nd30
description: >-
  Engine và quy chuẩn THỂ THỨC văn bản hành chính Việt Nam theo Nghị định 30/2020/NĐ-CP
  (administrative document formatting standard for Vietnamese government). Phân loại 27+ loại
  văn bản (công văn, tờ trình, quyết định, kế hoạch, báo cáo, thông báo, biên bản, giấy mời,
  phiếu biểu quyết), phỏng vấn lấy dữ liệu (không bịa), sinh file .docx ĐÚNG thể thức (font Times
  New Roman, lề theo mm, cỡ chữ, vị trí từng thành phần thật, mở Word sửa được — không phải chữ
  thô nhìn-giống-văn-bản), rồi VALIDATE bằng script. Sử dụng khi người dùng yêu cầu soạn thảo,
  chỉnh sửa, kiểm tra thể thức, hoặc xuất file .docx cho bất kỳ văn bản hành chính nào; hoặc khi
  dạy cán bộ công chức cách dùng AI soạn văn bản đúng chuẩn. Trigger VN — nd30, nghị định 30,
  soạn công văn/tờ trình/quyết định/kế hoạch/báo cáo đúng thể thức, xuất file docx văn bản hành
  chính, kiểm tra thể thức văn bản, validate thể thức, văn bản hành chính. Trigger EN — Vietnamese
  administrative document, Decree 30/2020/NĐ-CP formatting, generate .docx government document
  Vietnam.
---

# nd30 — Engine thể thức văn bản hành chính (NĐ 30/2020)

> ✅ linh-moi PASS 2026-08-27 — lính mới KHÁC-HỌ (agy/Antigravity, Gemini 3.7 Flash, cold-start):
> soạn công văn thật với dữ liệu thiếu → KHÔNG bịa (5 placeholder đúng luật), validate mặc định
> nổ đúng exit 2, tự tìm ra `--allow-placeholder` cho bản nháp, 5/5 câu đố kèm trích file:dòng.
> Bắt được 1 bug thật: example `cong_van.json` ghi "Về việc..." + code chèn "V/v " = double-prefix
> — đã vá cả gốc (build_docx tự strip tiền tố) lẫn example. Report: `_linh-moi-2026-08-27.md`.

Ra **file .docx editable** đúng thể thức NĐ30 (font, cỡ chữ, lề theo mm, vị trí từng thành phần)
và **kiểm chứng được bằng script**, không phải "chữ thô nhìn giống văn bản".

## Phân vai — đừng lẫn với `/biensoan`

| | `/nd30` (đây) | `/biensoan` |
|---|---|---|
| Lo phần | **THỂ THỨC** kỹ thuật + sinh .docx + validate | **NỘI DUNG**: giọng đối tác, căn cứ pháp lý, Đội Đỏ, quan hệ CRM |
| Câu hỏi nó trả lời | "File này có đúng thể thức chưa? Xuất .docx thế nào?" | "Viết gì? Giọng ai? Căn cứ nào? Đã soi lỗi chưa?" |
| Dùng độc lập | ĐƯỢC — cán bộ tự dùng, dạy được trong lớp | Được, nhưng là dịch vụ ghost-writing đầy đủ |

**Kết nối:** `/biensoan` chốt nội dung (B1→B4) → gọi **`/nd30`** ở khâu xuất `.docx` editable + validate.
`/biensoan` vẫn giữ Typst cho PDF-canonical; `/nd30` lo `.docx` (thứ cán bộ mở Word sửa được).

## ⛔ 3 LUẬT CỨNG (vi phạm là hỏng việc thật)

**1. KHÔNG tự bịa — dùng placeholder `[CẦN BỔ SUNG: ...]`:**
số/ký hiệu văn bản · căn cứ pháp lý (số hiệu NĐ/TT/QĐ) · người ký (họ tên, chức vụ) · số tiền/kinh phí ·
ngày ban hành · quan điểm biểu quyết (Đồng ý/Không đồng ý) · mức phê duyệt · số liệu thống kê.
ĐƯỢC tự quyết: câu chữ hành chính, cấu trúc mở-thân-kết, format trình bày theo NĐ30.

**2. Đúng LUẬT cho đúng LOẠI văn bản** — NĐ30 KHÔNG phủ hết:
- **Văn bản hành chính** (công văn, tờ trình, quyết định cá biệt, kế hoạch, báo cáo…) → **NĐ 30/2020/NĐ-CP** ✅ (skill này)
- **Văn bản QPPL** (Nghị quyết HĐND, Quyết định/Chỉ thị QPPL của UBND tỉnh, Thông tư…) → thể thức RIÊNG theo
  **NĐ 78/2025/NĐ-CP + NĐ 187/2025/NĐ-CP**. **KHÔNG bê khuôn NĐ30.** ⚡ **MVP đã có 2026-08-20**: Nghị quyết
  HĐND **các cấp** (tỉnh/huyện/xã, quy định trực tiếp) — Mẫu số 17, **verify thật từ 2 PDF chính thức**:
  Phụ lục I NĐ 78/2025/NĐ-CP (bản gốc, `pdftotext`) + Phụ lục III NĐ 187/2025/NĐ-CP (bản sửa đổi, ảnh
  scan → OCR bằng `tesseract -l vie`, 152 trang). **Phát hiện quan trọng**: NĐ187 (ban hành sau) đổi
  phạm vi Mẫu 17 từ "cấp tỉnh" (NĐ78 gốc) → "**cấp các cấp**" — dùng bản NĐ187 làm chuẩn hiện hành.
  Xem `references/the-thuc-qppl-nq-hdnd.md` + `examples/nghi_quyet_hdnd.json`. **Đã mở rộng thêm**:
  Mẫu 18 (NQ HĐND ban hành kèm Quy định/Quy chế — sinh 2 file riêng, xem
  `examples/nghi_quyet_hdnd_kem_quy_dinh.json`) và Mẫu 19/20 (Quyết định UBND tỉnh, quy định trực
  tiếp hoặc kèm Quy định/Quy chế — chữ ký `quyen_han="TM."` khác NQ HĐND, xem
  `references/the-thuc-qppl-qd-ubnd.md` + `examples/quyet_dinh_ubnd_qppl.json`). Các loại QPPL khác
  (luật, pháp lệnh, NQ Quốc hội, Lệnh/QĐ Chủ tịch nước, Nghị định Chính phủ, thông tư các cấp)
  **CHƯA phủ** — phải hỏi lại nếu gặp (ít dùng ở cấp tỉnh/địa phương nên chưa ưu tiên).
- **Cơ quan ĐẢNG** (Tỉnh ủy/Huyện ủy/Đảng ủy/Ban Đảng) → **Hướng dẫn 36-HD/VPTW**, thể thức khác hẳn.
  **Repo chưa phủ track này → HỎI trước khi soạn.**

**3. Không nói "chuẩn NĐ30" nếu chỉ áp dụng một phần.** Nói rõ đã áp phần nào, còn placeholder nào.

## Quy trình 5 pha

### Pha 1 — Phân loại loại văn bản
Đọc `references/danh-muc-loai-vb.md` (27+ loại + bảng nhận diện theo keyword user nói).
Match rõ 1 loại → confirm 1 dòng rồi đi tiếp. Match 2-3 loại → `AskUserQuestion`.
Không match → hỏi mục đích: *"Văn bản này dùng để làm gì?"* (bảng mục-đích→loại-VB có trong reference).

### Pha 2 — Phỏng vấn lấy dữ liệu

**Mặc định = Guided Mode (đầy đủ).** Đọc `references/interview-questions.md` — có bộ câu hỏi
chung (mục đích/người ký/nơi gửi/nơi nhận/số VB/ngày) + câu hỏi ĐẶC THÙ theo từng loại VB. Gom
câu hỏi, đừng hỏi lắt nhắt nhiều lượt. User nói "không biết" → đánh dấu `???`, hỏi lại 1 lần
cuối trước khi xuất. User nói "tự quyết" → chỉ tự quyết được phần ĐƯỢC PHÉP ở Luật cứng #1.

**⚡ Quick Mode — CHỈ khi user CHỦ ĐỘNG nói rõ muốn bỏ qua phỏng vấn** (vd "làm nhanh giùm, khỏi
hỏi", "bỏ qua hết, demo xem thử cho tôi", "cứ tự điền luôn"). KHÔNG tự ý chuyển sang Quick Mode
chỉ vì yêu cầu ngắn gọn — thiếu tín hiệu rõ ràng từ user thì vẫn đi Guided Mode.

Ngay cả ở Quick Mode, **Luật cứng #1 vẫn áp dụng nguyên vẹn** — KHÔNG được tự bịa số/ký hiệu văn
bản, ngày ban hành, người ký, số tiền, căn cứ pháp lý (đây chính là lý do phải từ chối đề xuất
"Smart Fallback tự điền ngày/số" — văn bản hành chính là rủi ro pháp lý thật, không phải chỗ để
đoán cho nhanh). Quick Mode chỉ được phép tự quyết phần KHÔNG nhạy cảm (câu chữ mở-thân-kết, cấu
trúc, tháng/năm hiện tại nếu ngày cụ thể chưa có — xem `add_so_vb_and_date_section` đã có sẵn quy
tắc này), còn lại vẫn dùng `[CẦN BỔ SUNG: ...]` như Guided Mode. Xuất file xong phải gắn nhãn rõ
*"— BẢN NHÁP NHANH, cần xem lại và điền đủ dữ liệu trước khi ban hành"* trong lời bàn giao Pha 5.

## 📋 Cheat-sheet thể thức (đọc cái này trước — thường KHỎI cần mở `references/`)

Thông số cố định quan trọng nhất theo NĐ30 Phụ lục I — tự chứa ngay trong SKILL.md để agent
chạy trong sandbox không phải mở nhiều file `references/*.md` mới dựng được nội dung:

| Thành phần | Font | Cỡ chữ | Kiểu | Canh lề |
|---|---|---|---|---|
| Quốc hiệu | Times New Roman | 12-13pt | ĐẬM, IN HOA | Giữa |
| Tiêu ngữ | Times New Roman | 13-14pt | ĐẬM | Giữa, có gạch chân ngắn |
| Tên cơ quan chủ quản | Times New Roman | 12-13pt | thường | Giữa |
| Tên cơ quan ban hành | Times New Roman | 12-13pt | ĐẬM, IN HOA | Giữa, có gạch chân ngắn |
| Số, ký hiệu VB | Times New Roman | 13pt | thường | Giữa |
| Địa danh, ngày tháng | Times New Roman | 13-14pt | NGHIÊNG | Giữa |
| Tên loại VB (TỜ TRÌNH...) | Times New Roman | 13-14pt | ĐẬM, IN HOA | Giữa |
| Trích yếu | Times New Roman | 13-14pt | ĐẬM | Giữa |
| Nội dung (body) | Times New Roman | 13-14pt | thường | Đều 2 bên (justify), thụt đầu dòng 1-1.27cm |
| "Nơi nhận:" | Times New Roman | 12pt | ĐẬM + NGHIÊNG | Trái |
| Danh sách nơi nhận | Times New Roman | 11pt | thường | Trái |
| Quyền hạn + chức vụ ký | Times New Roman | 13-14pt | ĐẬM, IN HOA | Giữa |

**Trang & lề (A4):** trên 20-25mm · dưới 20-25mm · trái 30-35mm · phải 15-20mm.
**Cấm:** bullet tự động Word (`•`), số thứ tự Word tự sinh, tô nền bảng, chữ màu khác đen.

Case không nằm trong bảng trên (biên bản, phiếu biểu quyết, bảng góp ý phức tạp...) → mới cần
đọc `references/the-thuc-nd30.md` đầy đủ.

### Pha 3 — Sinh .docx

**Cách sinh — ưu tiên theo thứ tự:**
1. **`scripts/generate_docx.py` (MẶC ĐỊNH, nhất là khi chạy trong sandbox không có filesystem
   riêng, vd Gemini Spark):** tự viết JSON mô tả nội dung — schema đầy đủ ở
   `schemas/nd30-input.schema.json` + docstring đầu file, **ví dụ mẫu sẵn ở
   `examples/input-sample.json`** (= mẫu Tờ trình; còn `cong_van.json`, `quyet_dinh.json`,
   `bien_ban.json`, `thong_bao.json`, `giay_moi.json` cho từng loại VB khác — đọc đúng file theo
   loại đang soạn trước khi tự đoán tên field, khỏi mất công đoán sai).
   3 cách truyền input (chọn 1, khỏi cần tạo file tạm nếu sandbox không tiện):
   ```bash
   python3 scripts/generate_docx.py input.json -o output.docx --validate --profile administrative
   echo '{"header": {...}}' | python3 scripts/generate_docx.py - -o output.docx --validate
   python3 scripts/generate_docx.py --json-string '{"header": {...}}' -o output.docx --validate
   ```
   Cờ `--validate` gọi thẳng `validate_docx.py` bên trong (không cần subprocess riêng), in kết
   quả tóm tắt ngay. Input `.json` KHÔNG cần cài `pyyaml` (chỉ cần khi dùng `.yaml`/`.yml`).
   `-o` bỏ trống được khi dùng input file (tự đặt tên `input.docx`); **bắt buộc** phải nhận đuôi
   `.docx` — truyền đuôi khác (`.doc`, `.pdf`...) script sẽ báo lỗi và dừng, không âm thầm đổi
   định dạng khác (chủ đích: nd30 chỉ bàn giao 1 định dạng duy nhất).
   **ĐỪNG đọc/transcribe toàn bộ `build_docx.py` (1165 dòng) qua giao diện web** — sandbox chỉ
   cần biết SCHEMA JSON, không cần biết bên trong `build_docx.py` viết thế nào.
2. **`scripts/build_docx.py` trực tiếp (khi có filesystem thật, vd Claude Code):** import các hàm
   helper (header 2 cột, số/ký hiệu, tên loại + trích yếu, nội dung căn đều, Nơi nhận + khối chữ ký)
   để tự viết script build riêng cho case phức tạp mà `generate_docx.py` chưa cover (bảng góp ý,
   phiếu biểu quyết...).
3. Có mẫu sẵn trong `templates/` thì ưu tiên fill mẫu (dùng `scripts/fill_template.py`).

Mặc định VB hành chính: A4 · Times New Roman · đen · lề trái 30-35mm, phải 15-20mm, trên/dưới 20-25mm ·
body justify · **KHÔNG dùng bullet tự động của Word** (dùng tiền tố tay `-`, `+`, `a)`).

### Pha 4 — Validate (MẶC ĐỊNH — generate_docx.py TỰ chạy, không bỏ được im lặng)

Từ 2026-08-27 `generate_docx.py` **tự validate sau khi sinh** (fail-loud: lỗi nặng → exit 2,
KHÔNG bàn giao). Muốn file thô chưa kiểm phải chủ động `--no-validate` và chịu cảnh báo.
Validate rời (file có sẵn):
```bash
python3 scripts/validate_docx.py <file.docx> --profile administrative
python3 scripts/validate_docx.py <file.docx> --profile administrative --json   # dạng JSON máy-đọc
```
Cờ `--json` (hoặc `--validate-json` trên `generate_docx.py`) in kết quả dạng
`{overall_status, counts, items: [{status, label, detail}]}` — dùng khi agent muốn tự động đọc lỗi
và tự sửa (self-healing) mà không cần parse chuỗi báo cáo tiếng Việt.

Kiểm: khổ A4 · lề · font/màu (cả bảng + header/footer) · thành phần bắt buộc theo loại VB ·
bullet tự động · bảng tràn lề · placeholder `[CẦN BỔ SUNG]`/`???` còn sót.
Còn lỗi nghiêm trọng → **KHÔNG bàn giao**. Thiếu dữ liệu → nêu rõ field thiếu.

### Pha 5 — Bàn giao
Trả về: file .docx · loại VB + luật thể thức đã áp · kết quả validate · danh sách placeholder còn lại.
Giao file bằng `/atp-deliver` (outbox link), **không** dán local-path Markdown.

## 🌐 2 CHẾ ĐỘ CHẠY — Claude Code (có máy) vs Gemini (Spark/app)

Repo public: **https://github.com/kanazawahere/nd30** → mọi AI có browse/fetch đều dùng được.
Raw base: `https://raw.githubusercontent.com/kanazawahere/nd30/main/`
Chỉ mục gọn cho agent: [`llms.txt`](https://raw.githubusercontent.com/kanazawahere/nd30/main/llms.txt)
(liệt kê đúng file cần đọc theo thứ tự, tránh crawl thừa toàn bộ repo).

**A. Claude Code / máy có Python** (chế độ đầy đủ): chạy y như 5 pha trên — có filesystem, đọc
`references/*.md` trực tiếp, `python3 scripts/validate_docx.py` chấm lỗi trước khi giao.

**B. Gemini Spark / Gemini app** (không có filesystem/internet trực tiếp trong sandbox — sandbox
tự nói "cần một cách để đưa tập lệnh vào môi trường VM do hạn chế kết nối", phải dùng sub-agent
"trình duyệt từ xa" điều khiển bằng vision để đọc GitHub):

⚠️ **Đã đo thật 2026-08-19-2026-08-20 (đội đỏ test trên account Spark hoàn toàn sạch, 3 lần):**
- Prompt yêu cầu nó tự đọc + transcribe **`build_docx.py` (1165 dòng, 49KB)** qua vision-browsing
  → **THẤT BẠI 2/3 lần** ("Something went wrong" hoặc treo vô thời hạn ở bước đọc code dài).
- Prompt tự nhiên ngắn gọn không nêu tên script (để Spark tự quyết cách làm) → ra `.docx` đúng
  thể thức trong ~10 giây, nhưng **hành vi không nhất quán 100%** — có lần Spark tự nhận "không
  truy cập được GitHub" dù cùng skill, cùng account.
- Kết luận: **CÀNG BẮT Spark đọc/transcribe file dài qua vision-browsing càng dễ hỏng.** Đường
  đi ổn định hơn là để nó sinh JSON nhỏ (rẻ, ít lỗi) rồi tự chạy 1 script ngắn.

**Quy trình khuyến nghị cho môi trường B:**
1. Fetch `llms.txt` → `SKILL.md` (đủ cheat-sheet thể thức, không cần fetch thêm `references/*.md`
   trừ case đặc biệt).
2. Fetch `examples/input-sample.json` (ví dụ mẫu, ĐỪNG tự đoán tên field) + docstring đầu
   `scripts/generate_docx.py` (không cần đọc hết code, chỉ cần schema) → **tự viết 1 file JSON
   nội dung** (dễ, ít lỗi hơn code Python nhiều).
3. Trong sandbox: `pip install python-docx` (input `.json` KHÔNG cần `pyyaml`) → fetch nguyên file
   `scripts/generate_docx.py` + `scripts/build_docx.py` + `scripts/validate_docx.py` (3 file, cùng
   thư mục) → chạy **1 lệnh duy nhất**:
   ```bash
   python3 scripts/generate_docx.py input.json -o output.docx --validate --profile administrative
   ```
   (Khỏi cần gọi `validate_docx.py` riêng — cờ `--validate` đã tự làm, in kết quả tóm tắt ngay.)
4. Báo kết quả validate cho người dùng (đã có sẵn từ bước 3).
5. Nếu sandbox không cho `pip install` hoặc không fetch được 3 file script → dùng
   `references/hien-thi-markdown-fallback.md` để hiển thị bố cục 2 cột bằng bảng Markdown, nói
   THẲNG "đây là bản xem trước, chưa phải file .docx đã kiểm máy".
6. Đừng im lặng bỏ bước validate rồi báo "đúng chuẩn NĐ30".

**Dạy cán bộ tự dùng (không cần cài gì):** đưa họ link repo + câu mồi:
> *"Dùng skill ở https://github.com/kanazawahere/nd30 soạn giúp tôi [loại VB] về [việc], xuất .docx."*

## 🔖 Vân tay phiên bản (để kiểm AI có đọc bản MỚI hay đang dùng bản cache)

**SKILL_VERSION: 2026-08-27-v19**

Khi người dùng hỏi *"skill nd30 version bao nhiêu?"* → trả lời ĐÚNG chuỗi `SKILL_VERSION` đọc được
từ file này, không đoán. Số báo về khác số trong repo = đang đọc bản cache.

### ⚠️ GitHub raw CDN cache theo branch — commit mới KHÔNG hiện ra ngay (đã đo thật 2026-08-19)

Bằng chứng đo được ngay sau khi push commit `54cbd27`:

| Cách fetch | Kết quả |
|---|---|
| `raw.githubusercontent.com/kanazawahere/nd30/**main**/SKILL.md` | **bản CŨ** (sau 60s vẫn cũ; thêm `?cb=<timestamp>` cũng không phá được cache) |
| `raw.githubusercontent.com/kanazawahere/nd30/**<commit-sha>**/SKILL.md` | **bản MỚI** ngay lập tức ✅ |
| GitHub API `repos/.../contents/SKILL.md` | **bản MỚI** ngay lập tức ✅ |

**Nghĩa là:** vừa sửa skill xong mà bảo AI (Gemini/Spark/bất kỳ) fetch `/main/` thì nó rất có thể
đọc bản CŨ mà cả hai đều không biết. Cách xử lý, chọn 1:
1. **Đưa URL theo commit SHA** (chắc nhất): lấy SHA mới nhất rồi dùng
   `https://raw.githubusercontent.com/kanazawahere/nd30/<SHA>/SKILL.md`.
2. Hoặc bảo AI đọc trang HTML `https://github.com/kanazawahere/nd30/blob/main/SKILL.md` (cache khác đường).
3. Hoặc đợi vài phút cho CDN hết hạn rồi kiểm lại bằng `SKILL_VERSION`.

**Luôn kiểm bằng `SKILL_VERSION`** trước khi tin là AI đang chạy bản mới — đừng giả định.

## Học từ mẫu cơ quan (khi đối tác đã có khuôn riêng)
Cơ quan có mẫu .docx riêng → mẫu của HỌ thắng mặc định của skill:
```bash
python3 scripts/inspect_docx.py <mau-co-quan.docx>     # soi thông số thật của mẫu
python3 scripts/learn_template.py <mau-co-quan.docx>   # bóc thể thức + placeholder
```
Thứ tự ưu tiên khi xung đột: yêu cầu user → mẫu cơ quan → NĐ30 → mặc định skill.

## Nồi cơm (đọc khi cần)
`llms.txt` (chỉ mục cho agent) · `references/danh-muc-loai-vb.md` (27+ loại) ·
`references/interview-questions.md` (bộ câu hỏi) · `references/the-thuc-nd30.md` (thông số kỹ thuật) ·
`references/validation-checklist.md` · `references/editorial-quality-vi.md` (chất lượng câu chữ tiếng Việt) ·
`references/hien-thi-markdown-fallback.md` (bảng Markdown 2 cột khi chưa xuất file được) ·


## Gotcha
- **python-docx không có "tab stop 2 cột" tự nhiên** cho Quốc hiệu/tên cơ quan → dùng **bảng 2 cột ẩn viền**
  (`build_docx.py` đã có helper). Đừng dùng dấu cách/tab tay — lệch ngay khi đổi máy.
- **Bullet `•` của Word bị NĐ30 loại** với VB hành chính → tiền tố tay. Validate sẽ bắt lỗi này.
- **Số < 10 phải có số 0** (`05`, `01`) ở ngày/tháng và số văn bản.
- Dòng cuối căn cứ dùng dấu `.`, các dòng trên dùng `;`.
- Nói với người dùng thì gọi "văn bản đúng thể thức", đừng khoe "chuẩn 100% NĐ30" khi còn placeholder.

**Bản đồ luồng:** `PHAN-LUONG.md` cùng thư mục (trạm phân luồng · cổng 3 làn · đã /graph 2026-08-27).

> Tạo/đổi skill xong → chạy `/linh-moi nd30` (cold-start audit) — nghi thức bắt buộc.

<!-- nha-van:exempt — README kỹ thuật cho AI agent/dev, ví dụ trong bài là mẫu rỗng minh hoạ, không phải văn bản gửi-đi thật -->
# nd30 — Engine thể thức văn bản hành chính Việt Nam

(Tiếng Việt | [English](./README.en.md) | [中文](./README.zh.md) | [日本語](./README.ja.md))

[![release](https://img.shields.io/github/v/release/kanazawahere/nd30?label=release)](https://github.com/kanazawahere/nd30/releases)
[![license](https://img.shields.io/github/license/kanazawahere/nd30)](./LICENSE)
[![tests](https://img.shields.io/badge/tests-24%20passing-brightgreen)](./tests)
[![last commit](https://img.shields.io/github/last-commit/kanazawahere/nd30)](https://github.com/kanazawahere/nd30/commits/main)

AI skill giúp soạn **file .docx đúng thể thức Nghị định 30/2020/NĐ-CP** — font, cỡ chữ, lề theo mm,
vị trí từng thành phần — rồi **tự kiểm tra bằng script** trước khi giao. Không phải "chữ thô nhìn
giống văn bản hành chính".

Chạy được với **Claude Code, Gemini (app/Spark), Gemini CLI**, hoặc dùng script Python trực tiếp.
Không cần MCP, không cần dựng server.

## Nó làm được gì

- **Phân loại 27+ loại văn bản** (công văn, tờ trình, quyết định, kế hoạch, báo cáo, thông báo,
  biên bản, giấy mời, phiếu biểu quyết…) từ cách người dùng nói chuyện bình thường.
- **Hỏi lấy dữ liệu trước khi soạn** — bộ câu hỏi riêng theo từng loại VB, thay vì đoán rồi bịa.
- **Sinh .docx** đúng thể thức: A4, Times New Roman, lề trái 30–35mm / phải 15–20mm / trên-dưới
  20–25mm, header bảng-2-cột-ẩn-viền (tên cơ quan bên trái, Quốc hiệu–Tiêu ngữ bên phải), phân cấp
  La Mã → số → chữ cái → gạch đầu dòng, Nơi nhận nhóm `b/c`–`t/h`–`p/h`–`Lưu: VT`, khối chữ ký.
- **Validate tự động**: khổ giấy, lề, font/màu (cả trong bảng và header/footer), thành phần bắt buộc
  theo từng loại VB, bullet tự động của Word (NĐ30 không cho dùng), bảng tràn lề, và placeholder còn sót.
- **Học từ mẫu cơ quan**: cơ quan đã có khuôn .docx riêng thì khuôn của họ thắng mặc định của skill.

## 3 luật cứng

**1. Không bịa.** Số/ký hiệu văn bản, căn cứ pháp lý, người ký, số tiền, ngày ban hành, quan điểm
biểu quyết, số liệu thống kê → luôn để `[CẦN BỔ SUNG: ...]` cho người dùng điền. AI chỉ tự quyết
câu chữ hành chính, cấu trúc, và format trình bày.

**2. Đúng luật cho đúng loại văn bản** — NĐ30 không phủ hết:

| Loại | Thể thức theo |
|---|---|
| Văn bản hành chính (công văn, tờ trình, quyết định cá biệt, kế hoạch, báo cáo…) | **NĐ 30/2020/NĐ-CP** ✅ repo này |
| Văn bản quy phạm pháp luật (Nghị quyết HĐND tỉnh, Quyết định/Chỉ thị QPPL của UBND tỉnh, Thông tư…) | **NĐ 78/2025 + NĐ 187/2025** — thể thức riêng, đừng bê khuôn NĐ30 |
| Cơ quan Đảng (Tỉnh ủy, Huyện ủy, Đảng ủy, Ban Đảng) | **Hướng dẫn 36-HD/VPTW** — repo này chưa phủ, phải hỏi lại |

**3. Không nói "chuẩn NĐ30" khi chỉ áp dụng một phần.** Nói rõ đã áp phần nào, còn thiếu gì.

## Dùng thế nào

### Với Gemini (app hoặc Spark) — không cần cài gì
Dán câu này vào Gemini:

> Dùng skill ở https://github.com/kanazawahere/nd30 soạn giúp tôi [loại văn bản] về [việc cần làm], xuất file .docx.

Gemini sẽ tự đọc repo, hỏi lại thông tin còn thiếu, rồi tạo file .docx trong sandbox của nó.

### Với Claude Code
Clone vào thư mục skill rồi gọi `/nd30`:
```bash
git clone https://github.com/kanazawahere/nd30.git ~/.claude/skills/nd30
```

### Dùng script trực tiếp (không cần AI)
```bash
pip install python-docx
python3 scripts/validate_docx.py <file.docx> --profile administrative   # kiểm thể thức file có sẵn
python3 scripts/inspect_docx.py  <file.docx>                            # soi thông số thật (lề, font, cỡ)
python3 scripts/learn_template.py <mau-co-quan.docx>                    # bóc thể thức từ mẫu cơ quan
```

Mẫu rỗng có sẵn trong `templates/`: tờ trình, công văn, quyết định, kế hoạch, báo cáo.

Input cho `generate_docx.py` theo schema JSON tại
[`schemas/nd30-input.schema.json`](./schemas/nd30-input.schema.json) — dùng để AI agent tự sinh
JSON không thiếu trường/sai kiểu, ví dụ đầy đủ theo từng loại VB trong `examples/`:
[Tờ trình](./examples/input-sample.json) · [Công văn](./examples/cong_van.json) ·
[Quyết định](./examples/quyet_dinh.json) · [Biên bản](./examples/bien_ban.json) ·
[Thông báo](./examples/thong_bao.json) · [Giấy mời](./examples/giay_moi.json).

Môi trường chat-only chưa cho tải file → xem trước bố cục 2 cột bằng bảng Markdown, hướng dẫn ở
[`references/hien-thi-markdown-fallback.md`](./references/hien-thi-markdown-fallback.md).

## Cấu trúc

```
SKILL.md            # entry point cho AI agent — quy trình 5 pha
llms.txt            # chỉ mục file cho AI agent (thứ tự nên đọc)
schemas/            # JSON Schema cho input generate_docx.py
examples/           # ví dụ input JSON đầy đủ
references/         # thông số NĐ30, danh mục 27+ loại VB, bộ câu hỏi phỏng vấn, checklist
scripts/            # build / validate / inspect / learn-template / fill-template / generate (JSON-driven)
templates/          # 5 mẫu .docx rỗng, mỗi mẫu tự pass validate
assets/samples/     # ví dụ script dạy học (build_to_trinh_thon_thong_minh.py)
tests/              # pytest
```

## Kiểm thử

```bash
pip install python-docx pytest pyyaml
python3 -m pytest tests/ -v
```

## Giới hạn đã biết

- **Cỡ chữ từng thành phần** chưa kiểm được đáng tin bằng script (python-docx đọc qua
  style-inheritance không chắc) → còn phải soi mắt, đã ghi trong `references/validation-checklist.md`.
- **Văn bản QPPL**: có MVP cho Nghị quyết HĐND (Mẫu 17+18, `references/the-thuc-qppl-nq-hdnd.md`)
  và Quyết định UBND tỉnh (Mẫu 19+20, `references/the-thuc-qppl-qd-ubnd.md`) — chưa phủ luật/pháp
  lệnh/NQ Quốc hội, Lệnh/QĐ Chủ tịch nước, Nghị định Chính phủ, thông tư.
- Chưa phủ thể thức **văn bản Đảng** (HD 36-HD/VPTW).
- Chưa có chữ ký số / con dấu — phần đó thuộc quy trình văn thư của cơ quan.

## FAQ

**Repo này có đủ chưa, cần thêm code/prompt/template gì nữa không?**
Đủ rồi. `SKILL.md` đã là system prompt đầy đủ (3 luật cứng + quy trình 5 pha), `scripts/build_docx.py`
+ `generate_docx.py` đã là engine sinh `.docx`, `templates/*.docx` đã là mẫu thật (không phải khung
Markdown). Trước khi đề xuất "thêm file X" — hãy **mở file trong repo ra đọc trước**, đối chiếu bảng
"Đã làm — đừng đề xuất lại" đầu file [`llms.txt`](./llms.txt).

**Tôi là AI/agent, chỉ đọc được trang chủ GitHub (không fetch được cây thư mục) — làm sao dùng?**
Đây chính là giới hạn đã đo thật (xem `SKILL.md` mục "2 CHẾ ĐỘ CHẠY"): trang chủ GitHub chỉ hiện
README này, không tự động lộ nội dung `SKILL.md`/`scripts/`. Bạn cần **chủ động fetch** từng file
raw (`https://raw.githubusercontent.com/kanazawahere/nd30/main/<đường dẫn>`), bắt đầu từ
[`llms.txt`](./llms.txt) rồi `SKILL.md`. Nếu nền tảng của bạn không tự fetch được link, người dùng
cần dán trực tiếp nội dung `SKILL.md` vào khung chat.

**Tại sao không cần MCP server?**
Cố ý — skill này là script Python thuần, chạy được bằng cách dán link/nội dung vào bất kỳ AI chat
nào có sandbox chạy code (Gemini, Claude, ChatGPT...), không cần cài đặt/host thêm hạ tầng nào.

**Sao biết mình đang đọc bản mới nhất, không phải bản cache cũ?**
Hỏi AI "skill nd30 SKILL_VERSION là bao nhiêu?" — số trả về phải khớp dòng `SKILL_VERSION` trong
[`SKILL.md`](./SKILL.md). Lệch số = đang đọc bản cache (xem cảnh báo GitHub raw CDN cache trong
`SKILL.md`).

**Vì sao margin/font lại ghi "20-25mm" thay vì 1 số cố định?**
Vì Nghị định 30/2020/NĐ-CP Phụ lục I quy định bằng DẢI (khoảng), không phải 1 con số duy nhất —
trích thẳng từ văn bản luật, không tự đoán 1 giá trị cố định.

## Nguồn gốc

Phần nghiệp vụ (danh mục loại VB, bộ câu hỏi phỏng vấn, nền builder/validator) kế thừa từ
[biencuong/vbhc](https://github.com/biencuong/vbhc) — license Unlicense (public domain), tương
thích relicense sang MIT. Thông số thể thức trích thẳng **Phụ lục I Nghị định 30/2020/NĐ-CP**
(văn bản pháp luật công khai, không thuộc bản quyền cá nhân/tổ chức nào).

## License

MIT — xem [LICENSE](./LICENSE).

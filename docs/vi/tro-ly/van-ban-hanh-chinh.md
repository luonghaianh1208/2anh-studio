# Loại việc: Soạn văn bản hành chính (Nghị định 30)

File dành cho AI. Luôn đọc docs/vi/tro-ly/quy-trinh-hoi.md trước file này. Bộ sinh và bộ kiểm thể thức là mã ND30 (© 2026 Nguyễn Minh Phát, giấy phép MIT) nhúng nguyên trạng ở `tools/vi/nd30/`; lệnh duy nhất là `tools/vi/van_ban.py`.

## Khi nào dùng

Thầy cô, cán bộ nhà trường cần một văn bản hành chính ra file Word đúng thể thức Nghị định 30/2020/NĐ-CP: công văn, tờ trình, quyết định, thông báo, giấy mời, biên bản, kế hoạch, báo cáo dạng văn bản… Đầu ra là `van-ban.docx` mở bằng Word sửa được, kèm `kiem-tra.md` ghi kết quả bộ kiểm thể thức.

Ví dụ câu lệnh:
- "Soạn công văn cử giáo viên đi tập huấn ứng dụng AI"
- "Làm tờ trình xin kinh phí mua máy chiếu cho tổ Toán, đúng thể thức Nghị định 30"
- "Soạn giấy mời họp phụ huynh đầu năm"

Câu lệnh chỉ có "báo cáo" hoặc "kế hoạch" (không có "công văn", "văn bản", "Word", "đúng thể thức", "Nghị định 30", "ND30", "slide", "trình chiếu") là ca mơ hồ: hỏi đúng một câu trước khi làm gì khác: "Thầy cô cần văn bản Word đúng thể thức Nghị định 30, hay slide trình chiếu?" Trả lời Word thì theo file này; trả lời slide thì theo docs/vi/tro-ly/bao-cao-tong-ket.md (báo cáo) hoặc loại việc slide gần nhất (kế hoạch). "Kế hoạch bài dạy", "KHBD" là giáo án, không thuộc file này.

Thầy cô gửi kèm tài liệu (văn bản cấp trên, số liệu, biên bản cũ) dạng Word hoặc PDF: đọc bằng `python skills/ppt-master/scripts/source_to_md.py <file> -o <thư_mục_tạm>` trước khi hỏi, rồi chỉ hỏi phần tài liệu không trả lời được. Ảnh chụp thì không đọc được: xin bản PDF hoặc Word, không tự đoán nội dung.

## Câu hỏi bắt buộc

1. Loại văn bản và việc cần làm (ví dụ công văn cử người đi tập huấn, tờ trình xin kinh phí)? Hồ sơ đơn vị chưa có "Cơ quan chủ quản", "Địa danh" hoặc "Ký hiệu viết tắt của đơn vị" thì hỏi luôn ba mục đó trong câu này.
   Gợi ý: loại văn bản em chọn theo danh mục của Nghị định 30 từ câu lệnh; ba mục của hồ sơ để trống cho thầy cô điền, em không đoán tên cơ quan.
2. Gửi ai (dòng "Kính gửi") và nơi nhận (gửi kèm, lưu)?
   Gợi ý: nơi nhận "Như trên; Lưu: VT" cộng đơn vị soạn thảo.
3. Nội dung chính và số liệu cần đưa vào (thời gian, địa điểm, danh sách, số tiền)?
   Gợi ý: thầy cô gửi tài liệu hoặc gõ ngắn từng ý; số liệu nào chưa có em để ô `[CẦN BỔ SUNG: …]`, không tự điền.
4. Người ký là ai, chức vụ gì, có ký thay (KT.), thừa lệnh (TL.) hay thay mặt (TM.) không?
   Gợi ý: Hiệu trưởng ký trực tiếp; chưa chốt họ tên thì em để ô cần bổ sung.
5. Số và ký hiệu văn bản?
   Gợi ý: số để trống cho văn thư điền khi vào sổ; ký hiệu ghép viết tắt tên loại theo Nghị định 30 (TTr, QĐ, TB, GM, BB…) với "Ký hiệu viết tắt của đơn vị" trong hồ sơ.
6. Ngày ban hành?
   Gợi ý: chưa chốt ngày thì em ghi tháng và năm, để trống ngày cho người ký điền khi ban hành.
7. Căn cứ pháp lý hoặc văn bản làm căn cứ (số, ngày, cơ quan ban hành)?
   Gợi ý: chỉ dùng căn cứ thầy cô nêu hoặc có trong tài liệu gửi kèm; không có thì em để ô cần bổ sung, không tự viện dẫn.

Gợi ý hỏi thêm theo từng loại (tờ trình, quyết định, báo cáo, kế hoạch…) nằm ở `tools/vi/nd30/references/interview-questions.md`; chỉ dùng để chọn nội dung cho 7 câu trên, tổng số câu vẫn không quá 7.

Tạo nhanh: câu lệnh có "không cần hỏi lại" hoặc "không hỏi gì" thì không hỏi câu nào; mọi thông tin thầy cô chưa nêu thành ô `[CẦN BỔ SUNG: …]`, file ra là bản nháp. Câu lệnh chỉ có "tạo nhanh" hoặc "làm nhanh": hỏi câu 1 và câu 3 nếu câu lệnh chưa trả lời. Loại việc này không theo `quick-generate.md` của upstream (hồ sơ đó dành cho PPTX).

## Luật không bịa

AI không tự điền những gì thầy cô chưa nói hoặc tài liệu gửi kèm không có:
- số và ký hiệu văn bản, ngày ban hành;
- họ tên, chức vụ người ký;
- căn cứ pháp lý (số hiệu, ngày, cơ quan ban hành của văn bản căn cứ);
- số tiền, số liệu, danh sách người, thời gian, địa điểm.

Chỗ nào còn thiếu thì ghi đúng dạng `[CẦN BỔ SUNG: <mô tả ngắn cần điền gì>]` ngay trong `noi-dung.json`; `???` cũng được công cụ tính là ô trống, nhưng ưu tiên dạng có mô tả. Không viết chữ giả kiểu "Nguyễn Văn A", "số 01/2026", "ngày …/…/2026" để cho đủ ô.

Công cụ đọc lại chính file Word vừa dựng, nên cả ô bộ dựng tự chèn (ví dụ thiếu người ký thì nó ghi `[CẦN BỔ SUNG: họ tên người ký]`) và dạng `<Tên đơn vị>` cũng được đếm. Còn ô nào thì `ban_nhap` là `true`, `so_o_can_bo_sung` là số ô, `warnings` liệt kê từng ô. Bản nháp vẫn được giao để thầy cô điền tiếp, nhưng khi báo phải nói rõ đây là **bản nháp**, chưa phải thành phẩm; điền đủ rồi chạy lại mới ban hành.

Riêng hai chỗ do văn thư và người ký điền tay:
- Số văn bản (`header.so_vb`) để trống là đúng quy trình: văn thư điền khi vào sổ. Công cụ chỉ cảnh báo B3, không coi là bản nháp.
- Ngày ban hành: để trống riêng `ngay` (vẫn ghi `thang`, `nam`) thì Word để khoảng trắng cho ngày, không coi là bản nháp. Bỏ trống cả `ngay`, `thang`, `nam` thì bộ dựng tự in tháng, năm hiện tại, còn công cụ tính một ô "chưa có ngày ban hành" và file là bản nháp. Thiếu riêng `thang` hoặc `nam` thì bộ dựng cũng tự lấy tháng, năm hiện tại: chỉ bỏ trống khi thầy cô đồng ý.

## Chọn loại văn bản

- Chọn loại theo `tools/vi/nd30/references/danh-muc-loai-vb.md` (27 loại văn bản hành chính của Nghị định 30, biểu mẫu nội bộ, bảng nhận diện nhanh từ câu nói của người dùng). Mơ hồ thì dùng bảng "câu hỏi gợi ý phân loại" ở cuối file đó trong câu hỏi 1.
- Mở ví dụ gần nhất trong `tools/vi/nd30/examples/` trước khi viết: `cong_van.json` (công văn), `input-sample.json` (tờ trình), `quyet_dinh.json`, `thong_bao.json`, `giay_moi.json`, `bien_ban.json`. Loại không có ví dụ riêng (kế hoạch, báo cáo, hướng dẫn…) thì đi theo `quyet_dinh.json` hoặc `thong_bao.json` và đổi `ten_loai_in_hoa`.
- Thể thức từng thành phần (quốc hiệu, tên cơ quan, số ký hiệu, trích yếu, nơi nhận) và chữ viết tắt tên loại: `tools/vi/nd30/references/the-thuc-nd30.md`.
- Văn bản quy phạm pháp luật của HĐND, UBND (nghị quyết HĐND, quyết định UBND có tính quy phạm) theo thể thức riêng, không theo Nghị định 30: đọc `tools/vi/nd30/references/the-thuc-qppl-nq-hdnd.md` hoặc `tools/vi/nd30/references/the-thuc-qppl-qd-ubnd.md`, và ví dụ `nghi_quyet_hdnd.json`, `nghi_quyet_hdnd_kem_quy_dinh.json`, `quyet_dinh_ubnd_qppl.json`.
- Văn bản của Đảng và văn bản của Đoàn Thanh niên có thể thức riêng: bản này **không hỗ trợ**. Nói rõ với thầy cô một dòng, không dựng bằng thể thức Nghị định 30 thay thế. Poster, slide cho hoạt động Đoàn thì vẫn theo loại việc "Hoạt động Đoàn – sự kiện".

## Viết noi-dung.json

Tạo thư mục `projects/_van-ban/<tên_văn_bản>/` (tên có dấu và khoảng trắng đều được) và viết `noi-dung.json` ở đó, UTF-8. Thứ tự làm:

1. Đọc ví dụ đúng loại trong `tools/vi/nd30/examples/` và schema `tools/vi/nd30/schemas/nd30-input.schema.json`.
2. Chép khung của ví dụ, thay nội dung bằng câu trả lời của thầy cô (các ý riêng của từng loại văn bản xem `tools/vi/nd30/references/interview-questions.md`); chỗ thiếu ghi `[CẦN BỔ SUNG: …]`.
3. Viết lại câu chữ cho đúng văn phong hành chính là việc AI được làm; quan điểm, mức phê duyệt, số tiền, người ký thì không.

Các trường chính:

| Trường | Ý nghĩa |
|---|---|
| `profile` | Bộ kiểm: `administrative` (mặc định, văn bản gửi ra ngoài), `bieu-mau-noi-bo` (phiếu nội bộ, miễn Số và Nơi nhận), `minutes-administrative` (biên bản), `academic`, `general` |
| `header.co_quan_chu_quan`, `header.co_quan_ban_hanh` | Cơ quan chủ quản (dòng trên) và cơ quan ban hành (dòng dưới, in hoa), lấy từ hồ sơ đơn vị |
| `header.so_vb`, `header.ky_hieu` | Số (thường để trống) và ký hiệu |
| `header.trich_yeu`, `header.dia_danh` | Trích yếu nội dung, địa danh |
| `header.ngay`, `header.thang`, `header.nam` | Ngày ban hành, xem mục "Luật không bịa" |
| `header.is_cong_van` | `true` với công văn (trích yếu "V/v …", không có tên loại) |
| `header.ten_loai_in_hoa` | Tên loại in hoa khi không phải công văn: `TỜ TRÌNH`, `QUYẾT ĐỊNH`, `THÔNG BÁO`… |
| `kinh_gui` | Dòng "Kính gửi" |
| `body` | Danh sách khối theo thứ tự: `heading`, `paragraph`, `bullet`, `table` (`headers`, `rows`), `can_cu` (`items`, danh sách căn cứ), `centered`, `italic_paragraph` |
| `ket_thuc` | Dòng kết thúc, thường `./.` |
| `signature` | `noi_nhan_items`, `phong_viet_tat` (thêm dòng "Lưu: VT, …"), `chuc_vu`, `nguoi_ky`, `quyen_han` (`""`, `KT.`, `TL.`, `TUQ.`, `TM.`), `chuc_vu_thay` |

`italic_paragraph` (đoạn in nghiêng) không có trong file schema nhưng bộ dựng hỗ trợ và các ví dụ văn bản quy phạm dùng; công cụ nhận khối này. Danh sách thì dùng khối `bullet` (bộ dựng tự thêm tiền tố `- `, `+ `, `* ` theo `level`), không gõ ký tự "•" vào chữ: bộ kiểm coi "•" là bullet tự động và báo lỗi `the-thuc`.

Ví dụ một công văn còn ô cần bổ sung (ra bản nháp 3 ô):

```json
{
  "profile": "administrative",
  "header": {
    "co_quan_chu_quan": "UBND XÃ AN BÌNH",
    "co_quan_ban_hanh": "TRƯỜNG THCS AN BÌNH",
    "so_vb": "",
    "ky_hieu": "THCSAB",
    "trich_yeu": "cử giáo viên dự tập huấn ứng dụng AI trong dạy học",
    "dia_danh": "An Bình",
    "ngay": "",
    "thang": "10",
    "nam": "2026",
    "is_cong_van": true
  },
  "kinh_gui": "Phòng Văn hoá – Xã hội xã An Bình",
  "body": [
    {"type": "paragraph", "text": "Thực hiện [CẦN BỔ SUNG: số, ngày văn bản triệu tập tập huấn], Trường THCS An Bình cử giáo viên tham dự lớp tập huấn ứng dụng AI trong dạy học như sau:"},
    {"type": "bullet", "text": "Giáo viên được cử: [CẦN BỔ SUNG: họ tên, môn dạy]."},
    {"type": "paragraph", "text": "Nhà trường đề nghị Quý Phòng tạo điều kiện để giáo viên tham dự đầy đủ."}
  ],
  "ket_thuc": "./.",
  "signature": {
    "noi_nhan_items": ["Như trên"],
    "phong_viet_tat": "VP",
    "chuc_vu": "HIỆU TRƯỞNG",
    "nguoi_ky": "[CẦN BỔ SUNG: họ tên Hiệu trưởng]"
  }
}
```

## Chạy lệnh và đọc kết quả

Như `AGENTS.vi.md` mục 4: có `venv\Scripts\python.exe` ở thư mục gốc repo thì dùng nó thay cho `python`.

```
python tools\vi\van_ban.py "projects\_van-ban\<tên_văn_bản>"
```

Thêm `--nhap` khi thầy cô chủ động muốn một bản nháp để điền tay: chỉ đổi câu cảnh báo đầu thành "Bản nháp có chủ đích", mọi kiểm tra vẫn chạy. Không có cờ nào tắt được bộ kiểm.

Lệnh in đúng một dòng JSON ở stdout: `ready`, `files`, `loai_van_ban`, `profile`, `so_o_can_bo_sung`, `ban_nhap`, `kiem_tra` (`dat`, `canh_bao`, `loi`), `warnings`, `error`.

`ready` là `true`: báo thầy cô
- đường dẫn `van-ban.docx` và `kiem-tra.md`, loại văn bản, số mục đạt / cảnh báo của `kiem_tra`;
- `ban_nhap` là `true`: nói rõ đây là bản nháp, đọc nguyên văn các dòng "Ô cần bổ sung …" trong `warnings` để thầy cô biết điền gì;
- các cảnh báo còn lại trong `warnings`, kèm cách hiểu:
  - B7 (dấu, chữ ký số) lần nào cũng có vì máy không kiểm được: bình thường, nhắc thầy cô soát tay;
  - B3 (số văn bản đang trống) là bình thường: văn thư điền khi vào sổ;
  - B6 "Không phát hiện được chức vụ người ký in hoa" khi chức vụ nằm ngoài danh sách của bộ kiểm (ví dụ HIỆU TRƯỞNG): bình thường nếu `signature.chuc_vu` đã đúng, nhắc thầy cô soát tay;
- câu nhắc cuối: văn bản chưa đóng dấu, chưa ký; soát, điền đủ rồi trình ký và đóng dấu theo quy trình văn thư của đơn vị.

`error` khác `null`: xử lý theo `error.step`:

| `error.step` | Nghĩa | Xử lý |
|---|---|---|
| `input` | Thiếu thư mục hoặc `noi-dung.json`, file không đọc được bằng UTF-8, hoặc sai tham số lệnh | Viết file, lưu lại bằng UTF-8, hoặc sửa lệnh theo `error.fix` rồi chạy lại. |
| `json` | Sai cú pháp JSON (có dòng và cột) hoặc sai schema (nêu đúng tên trường, ví dụ `header.ky_hieu`, `body[3].type`) | Sửa đúng chỗ đó theo schema và ví dụ đúng loại rồi chạy lại. |
| `the-thuc` | Bộ kiểm báo lỗi thể thức nặng không phải ô cần bổ sung; không có `van-ban.docx` (file cũ cũng bị xoá), chỉ có `kiem-tra.md` | Đọc các mục ✗ trong `kiem-tra.md`, sửa `noi-dung.json` rồi chạy lại, tối đa hai lần; vẫn lỗi thì báo nguyên `error.message` cho thầy cô. |
| `docx` | Chưa cài `python-docx` | Có `venv\Scripts\python.exe` thì chạy `venv\Scripts\python.exe -m pip install -r tools/vi/requirements-vi.txt`, không thì `python -m pip install -r tools/vi/requirements-vi.txt`; chạy lại tối đa một lần. |
| `write` | `van-ban.docx` đang mở trong Word, hoặc ổ đĩa không ghi được | Xin thầy cô đóng file Word đang mở, kiểm ổ đĩa còn chỗ, rồi chạy lại. |
| `internal` | Lỗi ngoài dự kiến | Dán nguyên `error.message` để báo cho người bảo trì, không tự đoán cách sửa. |

Thầy cô gửi lại thông tin cho các ô cần bổ sung: sửa đúng các ô đó trong `noi-dung.json` rồi chạy lại lệnh, không soạn lại từ đầu.

## Điều cấm

- Không tự điền số, ký hiệu, ngày ban hành, người ký, căn cứ pháp lý, số tiền hay số liệu thầy cô chưa nêu (xem mục "Luật không bịa").
- Không giao bản nháp như thành phẩm; không bỏ ô `[CẦN BỔ SUNG: …]` để công cụ báo "đạt".
- Không viết hay sửa file Word bằng tay hoặc bằng thư viện khác; chỉ xuất bằng `tools/vi/van_ban.py`.
- Không sửa file nào trong `tools/vi/nd30/` (mã nhúng có kiểm SHA-256).
- Không dùng thể thức Nghị định 30 cho văn bản Đảng, văn bản Đoàn.
- Không chạy `project_manager.py init`, không tạo SVG, không chạm `skills/`, không commit gì trong `projects/`.

## Ghi vào brief

- Loại việc: Soạn văn bản hành chính (Nghị định 30), kèm loại văn bản cụ thể (công văn, tờ trình…).
- Brief lưu tại `projects/_van-ban/<tên_văn_bản>/brief.md`, viết theo đúng bố cục của docs/vi/tro-ly/mau-brief.md; mục "Thầy cô yêu cầu" ghi đúng lời thầy cô cho từng câu hỏi, mục "AI đề xuất" ghi các ô để trống kèm "(AI đề xuất, chưa duyệt)".
- Loại việc này không dùng các bước dành cho PPTX: không kết thúc tin nhắn hỏi bằng dòng chốt cách xác nhận, không chạy `import-sources` hay `project_manager.py init`, và không có bước xác nhận của upstream. Thầy cô trả lời xong lượt hỏi thì viết `noi-dung.json` rồi chạy lệnh ngay.

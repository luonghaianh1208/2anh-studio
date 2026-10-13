# Danh mục kiểu slide

File dành cho AI. Đọc khi làm Bài giảng, Báo cáo – tổng kết, Hoạt động Đoàn – sự kiện, Poster/ấn phẩm Zalo – Facebook, Tập huấn/workshop, sau `docs/vi/tro-ly/quy-trinh-hoi.md` và file của loại việc. Mỗi kiểu là một cách nhìn có tên để thầy cô gọi được bằng một từ ("làm kiểu Bút dạ", "kiểu Lễ hội Đoàn"). Kiểu chỉ quyết định màu, chữ, hoạ tiết và nhịp trang; nội dung, cấu trúc và quy trình vẫn theo file loại việc và upstream.

## Chọn kiểu

| Loại việc | Kiểu mặc định | Kiểu thay thế hay dùng |
|---|---|---|
| Bài giảng THCS, THPT | Học đường sáng | Bút dạ – sổ tay, Cắt dán giấy |
| Bài giảng Tiểu học | Sách tranh tiểu học | Học đường sáng |
| Báo cáo – tổng kết | Ruy băng hành chính | Học thuật – hội thảo |
| Hoạt động Đoàn – sự kiện | Lễ hội Đoàn | Cắt dán giấy, Kính mờ CLB |
| Poster/ấn phẩm Zalo – Facebook | Lễ hội Đoàn (sự kiện), Cắt dán giấy (kiến thức) | Kính mờ CLB |
| Tập huấn/workshop | Bút dạ – sổ tay | Học đường sáng |
| Sinh hoạt chuyên môn, sáng kiến, nghiên cứu khoa học | Học thuật – hội thảo | Ruy băng hành chính |

- Thầy cô gọi tên một kiểu thì dùng kiểu đó, kể cả khi khác bảng trên. Thầy cô tả bằng lời ("trẻ trung", "trang trọng", "dễ thương") thì chọn kiểu gần nhất và nói tên kiểu đã chọn.
- Hồ sơ đơn vị có "Màu chủ đạo" thì thay màu chính của bảng màu bằng màu đó, giữ các màu còn lại.
- Mục "Không hợp với" của kiểu khớp với bài (ví dụ báo cáo nhiều bảng số mà chọn Bút dạ) thì nói với thầy cô một dòng và đề xuất kiểu khác.
- Ghi vào brief, mục "Phong cách gợi ý": `Kiểu nhìn: <tên kiểu> — bảng màu <tên bảng>`, kèm "(thầy cô đồng ý)" hoặc "(AI đề xuất, chưa duyệt)". Ở bước xác nhận của upstream, nêu tên kiểu và bảng màu trong phần phong cách.

## Tám kiểu

### Học đường sáng

- Nhìn: nền trắng hoặc kem rất nhạt, một màu chính đậm cho tiêu đề và khối nhấn, một màu phụ ấm cho điểm cần nhớ; khối nội dung bo góc nhẹ; nhiều khoảng trống; tương phản cao cho học sinh cuối lớp.
- Hợp với: bài giảng mọi môn THCS, THPT; tập huấn ngắn.
- Không hợp với: sự kiện lễ hội cần không khí rộn ràng; báo cáo trang trọng.
- Bảng màu (nền, chữ, chính, nhấn):
  - Xanh trời: `#FFFFFF`, `#1E2430`, `#1F6FB2`, `#F2A541`
  - Lá non: `#FBFCF7`, `#1E2A20`, `#2E8B57`, `#F2C14E`
  - Cam ấm: `#FFFDF8`, `#2B2620`, `#E4572E`, `#2E86AB`
- Chữ: Segoe UI (hoặc Arial), tiêu đề đậm 40–48pt, nội dung từ 28pt.
- Hoạ tiết: ít, chỉ `sao-ve-tay` cho ý cần khen, `mui-ten-ve-tay` chỉ vào hình.
- Nhịp trang: tiêu đề trái, hình phải; trang câu hỏi có ô đáp án riêng; trang hoạt động có nhãn tên hoạt động ở góc.
- Upstream: style `workshop-teaching` hoặc `science-explainer` (môn tự nhiên); layout `presentation_core` (`presentation_core_43` cho máy chiếu 4:3).

### Bút dạ – sổ tay

- Nhìn: nền giấy ấm, tiêu đề rất to, vệt bút dạ màu dưới chữ quan trọng, khung vẽ tay quanh khối nội dung, mũi tên và sao vẽ tay, mảnh giấy kẻ ô làm nền cho công thức; bố cục hơi lệch như trang sổ.
- Hợp với: tập huấn, workshop, bài giảng ôn tập, sơ đồ tư duy, mục tiêu và các bước.
- Không hợp với: báo cáo nhiều bảng số; văn bản trang trọng; trang có nhiều chữ.
- Bảng màu (nền, chữ, chính, nhấn):
  - Bạc hà: `#F6FBF7`, `#1E2430`, `#2A9D8F`, `#F2D16B`
  - Vàng chanh: `#FFFBEA`, `#1E2430`, `#2E5EAA`, `#F2C14E`
  - Xanh mực: `#F7F9FC`, `#1B2A4A`, `#2E5EAA`, `#F28C28`
- Chữ: Segoe UI đậm cho tiêu đề 48–60pt; nội dung 28pt.
- Hoạ tiết: `gach-but-da`, `khung-but-da`, `goc-nguech`, `mui-ten-ve-tay`, `sao-ve-tay`, `o-ke`, `bang-dinh`.
- Nhịp trang: mỗi trang một ý lớn; vệt bút dạ dưới một hai từ khoá, không gạch cả câu.
- Upstream: style `workshop-teaching`; layout `presentation_core`.

### Cắt dán giấy

- Nhìn: nền giấy kem, mảng giấy xé năm màu (xanh than, đỏ son, vàng mù tạt, xanh két) ở mép trang, ảnh cắt rời có viền giấy trắng, băng dính dán góc ảnh, chấm tram ở góc; cùng ngôn ngữ hình với video Vox của bộ công cụ, nên slide và video của một bài trông như một bộ.
- Hợp với: bài giảng Lịch sử, Địa lí, Ngữ văn, GDCD; poster kiến thức; hoạt động Đoàn có ảnh tư liệu.
- Không hợp với: báo cáo cần trang trọng; trang dày chữ.
- Bảng màu (nền, chữ, chính, nhấn):
  - Giấy kem: `#EFE6D2`, `#1E2430`, `#1F3A5F`, `#D9472B`
  - Báo cũ: `#E9DFC8`, `#2B2620`, `#556270`, `#B23A2B`
  - Mù tạt: `#F4ECD8`, `#1E2430`, `#2A7F7A`, `#E3A72F`
- Chữ: Segoe UI đậm cho tiêu đề trên dải giấy sáng; nội dung 28pt.
- Hoạ tiết: `giay-xe-ngang`, `bang-dinh`, `cham-tram`, `o-ke`.
- Ảnh: ảnh AI theo đúng phong cách cắt dán của video Vox (ảnh in chấm lưới, tranh khắc tông sepia).
- Nhịp trang: tiêu đề trên nhãn băng dính; một hình chính lớn mỗi trang.
- Upstream: style `narrative-keynote`; layout `editorial_bleed` hoặc `presentation_core`.

### Sách tranh tiểu học

- Nhìn: màu phấn tươi, góc trang vẽ nguệch ngoạc nhiều màu, khối nội dung bo tròn lớn, tiêu đề tròn đậm thân thiện, tranh minh hoạ nét mực đơn giản; mỗi trang ít chữ.
- Hợp với: bài giảng Tiểu học, hoạt động trải nghiệm, ngoại khoá, buổi họp phụ huynh.
- Không hợp với: THPT; báo cáo; nội dung nhiều số liệu.
- Bảng màu (nền, chữ, chính, nhấn):
  - Kẹo ngọt: `#FFF6F0`, `#2B2B2B`, `#FF6F91`, `#FFC75F`
  - Vườn xanh: `#F4FBF2`, `#23331E`, `#4CAF50`, `#FFB703`
  - Biển xanh: `#F0F8FF`, `#1D2A3A`, `#2A9DF4`, `#FF8C42`
- Chữ: Segoe UI đậm, tiêu đề 48pt, nội dung từ 32pt.
- Hoạ tiết: `goc-nguech`, `sao-ve-tay`, `hoa-giay` (thưa).
- Nhịp trang: một câu hỏi hay một việc mỗi trang; tranh chiếm nửa trang.
- Upstream: style `workshop-teaching`; layout `presentation_core`.

### Ruy băng hành chính

- Nhìn: nền trắng, ruy băng màu đậm cắt chéo mang tiêu đề trang, đường kẻ mảnh, thẻ số liệu gọn, nhiều khoảng trắng; trang trọng mà không khô.
- Hợp với: báo cáo tổng kết năm học, báo cáo hoạt động, giới thiệu trường, quy chế, đào tạo nội bộ.
- Không hợp với: bài giảng tiểu học; sự kiện vui.
- Bảng màu (nền, chữ, chính, nhấn):
  - Xanh đậm: `#FFFFFF`, `#1B2A4A`, `#1F4E9C`, `#C8102E`
  - Đỏ cờ: `#FFFFFF`, `#2B1A1A`, `#B71C1C`, `#F2C14E`
  - Xanh ngọc: `#FFFFFF`, `#16302B`, `#0F766E`, `#D97706`
- Chữ: Segoe UI hoặc Arial; Times New Roman khi thầy cô muốn giống văn bản hành chính; tiêu đề 36–44pt trên ruy băng; số liệu lớn 54pt.
- Hoạ tiết: `ruy-bang` (xoay -4 độ hoặc thẳng).
- Nhịp trang: mỗi phần một trang chương có ruy băng lớn; số liệu dùng biểu đồ thật của upstream.
- Upstream: style `operating-review`; layout `report_core`.

### Lễ hội Đoàn

- Nhìn: nền sáng hoặc màu tươi, ruy băng tiêu đề, hoa giấy rắc ở mép, dải giấy xé chân trang, khẩu hiệu trong khung vẽ tay với dấu ngoặc kép lớn; rộn ràng, trẻ trung.
- Hợp với: hoạt động Đoàn, Đội, ngày hội, lễ kỷ niệm, phát động phong trào, poster sự kiện.
- Không hợp với: báo cáo; bài giảng cần tập trung.
- Bảng màu (nền, chữ, chính, nhấn):
  - Xanh Đoàn: `#FFFFFF`, `#10233F`, `#1F4E9C`, `#E4572E`
  - Rực rỡ: `#FFF3E0`, `#222222`, `#FF4F5A`, `#00A6A6`
  - Đỏ vàng: `#FFF8E7`, `#2B1A1A`, `#C8102E`, `#F2C14E`
- Chữ: Segoe UI đậm, tiêu đề 48–60pt.
- Hoạ tiết: `ruy-bang`, `hoa-giay`, `giay-xe-ngang`, `ngoac-kep`, `khung-but-da`.
- Nhịp trang: ảnh hoạt động lớn; khẩu hiệu một trang riêng.
- Upstream: style `product-launch` hoặc `narrative-keynote`; layout `editorial_bleed`.

### Học thuật – hội thảo

- Nhìn: nền trắng, một màu chính trầm, nhãn phần nhỏ ở góc trên, thanh tiến độ và số trang ở chân trang, chữ to đọc được từ cuối phòng, mảnh giấy kẻ ô cho công thức.
- Hợp với: sinh hoạt chuyên môn, sáng kiến kinh nghiệm, nghiên cứu khoa học của học sinh, bảo vệ đề tài, hội thảo.
- Không hợp với: sự kiện; bài giảng tiểu học.
- Bảng màu (nền, chữ, chính, nhấn):
  - Mòng két: `#FFFFFF`, `#1E2430`, `#0F5E66`, `#E4572E`
  - Tối giản: `#FFFFFF`, `#222222`, `#333F50`, `#1F6FB2`
  - Công thức: `#FBFBF8`, `#1E2430`, `#3D4A8A`, `#D97706`
- Chữ: Segoe UI hoặc Calibri; tiêu đề 36pt, nội dung 24–28pt.
- Hoạ tiết: `o-ke` (nền công thức), `ngoac-kep` (trích dẫn).
- Nhịp trang: động cơ → phương pháp → kết quả → giới hạn → điều rút ra; trang công thức kèm ghi chú người nói đọc từng ký hiệu bằng lời thường; số liệu phải có nguồn.
- Upstream: style `academic-research`; layout `presentation_core`.

### Kính mờ CLB

- Nhìn: nền chuyển màu hai sắc mềm, thẻ nội dung trắng trong mờ (độ đục 55–70 %) viền trắng mảnh, bo góc lớn, ảnh tròn; hiện đại, nhẹ.
- Hợp với: giới thiệu câu lạc bộ, dự án học sinh, tuyển thành viên, tuyển sinh.
- Không hợp với: báo cáo trang trọng; trang nhiều chữ nhỏ (thẻ mờ làm giảm tương phản).
- Bảng màu (nền chuyển từ → tới, chữ, nhấn):
  - Oải hương: `#E9E4FF` → `#FDE7F3`, `#2A2340`, `#7C5CFF`
  - Biển sáng: `#E0F2FE` → `#E9FBF4`, `#12324A`, `#0EA5E9`
  - Đào: `#FFE8DD` → `#FFF6E5`, `#3A2418`, `#F97316`
- Chữ: Segoe UI; tiêu đề 44pt.
- Hoạ tiết: không dùng hoạ tiết vẽ tay; thẻ mờ là `rect` trắng `fill-opacity` 0.55–0.7 với `stroke` trắng.
- Upstream: style `creative-pitch`; layout `presentation_core`.

## Hoạ tiết

Hoạ tiết là hình vẽ tay đóng gói sẵn trong `tools/vi/hoa_tiet/<tên>.svg`, mỗi file một `<symbol id="ht-<tên>">`. Khi xuất, bộ chuyển đổi của upstream nhân bản `<use>` thành hình PowerPoint gốc, nên thầy cô vẫn bấm vào sửa màu, kéo giãn được, không phải ảnh dán.

| Tên | Dùng cho | Kéo giãn |
|---|---|---|
| `bang-dinh` | băng dính dán góc ảnh, góc thẻ | có |
| `giay-xe-ngang` | dải giấy xé phủ chân trang | có |
| `ruy-bang` | ruy băng mang tiêu đề | có |
| `goc-nguech` | cụm vẽ nguệch ngoạc ở góc trang | không |
| `sao-ve-tay` | ngôi sao khen, đánh dấu ý hay | không |
| `mui-ten-ve-tay` | mũi tên cong chỉ vào hình | không |
| `gach-but-da` | vệt bút dạ dưới từ khoá | có |
| `khung-but-da` | khung vẽ tay quanh một khối nội dung | có |
| `hoa-giay` | hoa giấy rắc mép trang | không |
| `cham-tram` | mảng chấm tram ở góc | không |
| `o-ke` | mảnh giấy kẻ ô làm nền công thức | có |
| `ngoac-kep` | dấu ngoặc kép lớn cho trích dẫn | không |

Cách đặt vào trang SVG:

1. Chép nguyên khối `<symbol>…</symbol>` của file hoạ tiết vào `<defs>` của trang. Đổi màu bằng cách sửa giá trị `fill`, `stroke` trong `symbol` sang màu của bảng màu (sáu chữ số hex viết hoa).
2. Hoạ tiết trang trí đứng riêng: đặt ở gốc trang `<use id="p03-goc" data-pptx-role="decoration" href="#ht-goc-nguech" x="…" y="…" width="…" height="…"/>`; `id` duy nhất trong trang.
3. Hoạ tiết thuộc một khối nội dung (vệt bút dạ dưới tiêu đề, khung quanh khẩu hiệu): đặt `<use>` không có `data-pptx-role` bên trong `<g id="…" data-pptx-bounds="x y rộng cao">` của khối đó, đứng trước chữ để chữ nằm trên.
4. Xoay chỉ bằng `transform="rotate(góc cx cy)"`. Hoạ tiết "không kéo giãn" thì giữ tỉ lệ `width`/`height` như `viewBox` của file.
5. Mỗi trang tối đa hai ba loại hoạ tiết; hoạ tiết không che chữ, không đặt dưới chữ nhỏ (trừ `gach-but-da`, `o-ke`).

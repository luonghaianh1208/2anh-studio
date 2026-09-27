# Video kể chuyện, cắt dán, khổ dọc Full HD — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Thêm vào `tools/vi/video_ma.py` (bản v6.3.2-vi.12):

- khổ dọc 9:16 và xuất Full HD cho cả hai khổ;
- phong cách cắt dán kiểu Vox;
- thẻ thông tin, dòng tài liệu, khung loạt bài;
- nhân vật dẫn chuyện (người que SVG hoặc ảnh do AI của nền tảng vẽ);
- loại cảnh `ke-chuyen` với nền kín khung;
- kho 8 nền mẫu vẽ bằng mã;
- công cụ `tools/vi/anh_ai.py` soạn câu lệnh vẽ và nhận ảnh AI về.

**Architecture:** Giữ nguyên đường ống parse → kiem → giong → lich → trang → chup → ghep. Có bảy thay đổi:

1. Một đối tượng khổ duy nhất (`kho.py` và `runtime/kho.js`) thay mọi hằng số 1280×720. Module cảnh đặt chữ và hình vào "ô" đặt tên, không dùng toạ độ cứng.
2. Chromium chụp với `deviceScaleFactor` 1,5, nên bố cục vẫn tính theo điểm CSS mà khung ra Full HD.
3. Chủ đề là một bộ biến cộng lớp "da" `cat-dan`.
4. Nhân vật và nền là lớp riêng dưới nội dung.
5. Ảnh AI do AI của nền tảng vẽ, lưu vào `anh/ai/`. `anh_ai.py` soạn câu lệnh và xử lý ảnh bằng FFmpeg. `video_ma.py` không gọi AI hay mạng.
6. Phụ đề có khung ở chủ đề mới và khổ dọc.
7. Tài liệu theo nền tảng: Antigravity và Codex vẽ ảnh, Claude dùng kho mẫu.

**Tech Stack:** Python thư viện chuẩn + edge-tts + playwright (lười); JS thuần; FFmpeg/libass; font Be Vietnam Pro (OFL).

**Spec:** `docs/vi/phat-trien/2026-09-27-video-ma-vi12-design.md` (có quyền quyết định cuối; Q1–Q15 là các quyết định bắt buộc).

**Cách viết:** Mỗi task nêu giao diện và khẳng định test cụ thể. Người thực hiện tự viết mã theo TDD: viết test trước, thấy trượt, rồi viết mã. Tên, số và chuỗi trong kế hoạch là bắt buộc.

## Global Constraints

- **Không sửa:**
  - `skills/` (chỉ đọc);
  - `tools/vi/video.py`, `tools/vi/video_parts/`, `tools/vi/thi_nghiem_parts/`;
  - `LICENSE`, `SPONSORS*`, mọi `requirements*.txt`, `attribution_guard.py`.
  Không commit gì trong `projects/`.
- **Thư viện:**
  - Python chỉ dùng thư viện chuẩn + `edge-tts` + `playwright` (import lười). Không Pillow, không numpy. Xử lý ảnh bằng FFmpeg.
  - JS thuần, không thư viện; trang dựng không có địa chỉ web.
  - Mọi khung hình là hàm xác định của `t`. Mọi yếu tố "ngẫu nhiên" (giấy xé, chấm lưới, nền mẫu) dùng PRNG có hạt giống = số cảnh.
- **Tương thích:**
  - Kịch bản vi.9–vi.11 dựng được không cần sửa. Fixture `tools/vi/fixtures/video-mau/` và `video-hinh/` giữ nguyên và vẫn qua test.
  - Ở `do-phan-giai: 720`, khung `viet-tay` khổ ngang của các fixture giống ảnh chụp tham chiếu trước khi sửa (sai khác điểm ảnh ≤ 0,5 %).
- **Khoá đầu mới** (thêm vào `META_CHOICES`/`META_FREE`, giữ nguyên khoá cũ):
  - `kho: ngang|doc`, mặc định `ngang`;
  - `do-phan-giai: 1080|720`, mặc định `1080`;
  - `phong-cach` nhận thêm `cat-dan`, mặc định vẫn `viet-tay`;
  - `loat: <chữ ≤ 30>`, không có thì không hiện khung loạt;
  - `nhan-vat: khong|nguoi-que|ve: <mô tả ≤ 200>`, mặc định `khong`;
  - `mau-ao: vang|do|xanh-duong|xanh-la|cam|tim|hong|xam`, mặc định `vang`;
  - `chuyen-canh` nhận thêm `xe-giay`.
- **Mặc định theo phong cách:** ở `cat-dan`, khi kịch bản không ghi thì `ban-tay` mặc định `khong` và `chuyen-canh` mặc định `xe-giay`. Kịch bản ghi rõ thì theo kịch bản.
- **Trường cảnh mới:**
  - `the: nhãn | giá trị | chú thích` và `tai-lieu:` ở `tieu-de`, `khai-niem`, `y-tung-y`, `cong-thuc`, `ke-chuyen`;
  - `tu-the:` ở `tieu-de`, `khai-niem`, `y-tung-y`, `ke-chuyen`;
  - `vi-tri: trai|giua|phai` ở `ke-chuyen`.
- **Loại cảnh mới `ke-chuyen`** thêm vào **cuối** `SCENE_SPEC`, để thứ tự 8 loại đầu không đổi.
- **Mười tư thế** (bắt buộc đúng tên và thứ tự): `dung`, `chao`, `chi-tay`, `giai-thich`, `suy-nghi`, `ngac-nhien`, `vo-dau`, `dung-lai`, `an-mung`, `buon`.
- **Tám nền mẫu** (đúng tên): `giay`, `bau-troi`, `vu-tru`, `lop-hoc`, `phong-thi-nghiem`, `thanh-pho`, `dong-que`, `vong-tron`.
- **Hợp đồng dòng lệnh:** mọi CLI in đúng một dòng JSON `{ready, files, ..., warnings, error}`. `video_ma.py` giữ tập `error.step` cũ. `anh_ai.py` dùng `input|parse|thieu|tach-nen|ffmpeg|write|internal`.
- **Không gọi mạng:** test không bao giờ gọi mạng thật (edge-tts, AI).
- **Chạy test:**
  - `venv\Scripts\python.exe -m unittest discover -s tools/vi/tests`;
  - `C:/Users/ADMIN/vmt/v/Scripts/python.exe -m unittest discover -s tools/vi/tests -p "test_video_ma_*.py"` (Chromium + FFmpeg thật, không mở cửa sổ; thêm `-p "test_anh_ai*.py"` cho Task 11–12);
  - `node --test tools/vi/tests/js/<file>.js` (liệt kê từng file trên Windows).
- **Commit:** trailer `Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>`. `git add` từng đường dẫn cụ thể. Không push; phát hành sau khi chủ repo duyệt.

## Review Focus

1. **Kịch bản cũ không được đổi hình.** Fixture `video-mau` và `video-hinh`, dựng `viet-tay` ngang ở `do-phan-giai: 720`, phải giống ảnh tham chiếu chụp trước khi sửa (≤ 0,5 % điểm ảnh khác). Ở 1080, chúng là cùng bố cục phóng 1,5 lần. Pin ở Task 1 và Task 2.
2. **Chữ Việt dài nhất ở khổ dọc và ở font Be Vietnam Pro** (rộng hơn Itim). Kiểm mọi loại cảnh × 2 khổ × 2 phong cách, với trường ở đúng giới hạn và chữ có nhiều dấu ("Nghiêng nghiễm nhiên"): không tràn khung, không xuống dưới vùng phụ đề. Pin ở Task 3 và Task 4.
3. **`nen` trỏ sai.** Các trường hợp: `nhu-canh 5` trỏ tới chính nó, tới cảnh sau, tới cảnh không phải `ke-chuyen`, hay tới cảnh mà nền lại là `nhu-canh`; `mau/` sai tên; file không có nguồn. Xử lý:
   - Trỏ tới chính nó hoặc cảnh sau: lỗi `parse`, nêu đúng dòng.
   - Chuỗi `nhu-canh`: được giải tới nền gốc.
   - Sai tên mẫu: gợi ý tên gần nhất.
   Pin ở Task 10.
4. **Ảnh AI không như ý.** Các trường hợp:
   - Ảnh vuông 1024×1024 khi cần 16:9: cắt phủ, cảnh báo thiếu điểm ảnh.
   - Nền nhân vật xanh không thuần hoặc có bóng: FFmpeg vẫn tách; góc còn đục thì lỗi `tach-nen`.
   - Nhân vật mặc áo xanh lá: câu lệnh cấm màu xanh lá trên nhân vật.
   - File thiếu, hoặc đuôi `.jpg` khi kế hoạch ghi `.png`: nhận cả hai đuôi, thiếu cả hai thì lỗi `thieu`.
   Pin ở Task 11 và Task 12.
5. **`tu-the` dùng sai.** Các trường hợp: `tu-the` khi `nhan-vat: khong`; `tu-the` cùng cảnh có `hinh` hoặc `anh`; tên tiếng Anh (`point`); tên thiếu dấu gạch (`chitay`). Tất cả báo lỗi `parse`, nêu đúng dòng, gợi ý tối đa 3 tên đúng. Pin ở Task 8.

---

## Đợt A — Khổ, Full HD, ô bố cục, khổ dọc

### Task 1: Đối tượng khổ và Full HD

**Files:**
- Tạo: `tools/vi/video_ma_parts/kho.py`, `runtime/kho.js`.
- Sửa: `parse.py` (khoá `kho`, `do-phan-giai`), `lich.py` (`du["kho"]`), `trang.py` (nạp `kho.js` đầu tiên; CSS biến `--rong`, `--cao`), `chup.py`, `viet-tay.css`, `khung-video.js` (viewBox, vùng kiểm tràn), `may-quay.js`, `ban-tay.js` (chỗ nghỉ), `khung-video.js` (hằng số lau bảng 1400), `karaoke.py` và `ghep.py` (nhận kích thước), `video_ma.py`.
- Test: `test_video_ma_kho.py` (mới), `tools/vi/tests/js/test_kho.js` (mới), bổ sung `test_video_ma_parse.py`.

**Interfaces:**
- `kho.Kho(ten: str, do_phan_giai: int)` (dataclass, frozen), thuộc tính:
  - `rong`, `cao`: điểm CSS. `ngang` = 1280×720, `doc` = 720×1280.
  - `ti_le`: 1,5 khi 1080, 1,0 khi 720.
  - `rong_xuat`, `cao_xuat` = `round(rong*ti_le)`, `round(cao*ti_le)`. Ngang 1080 ra 1920×1080, dọc 1080 ra 1080×1920.
  - `day`: mép trên vùng phụ đề, điểm CSS. `ngang` = 620 (giữ số cũ), `doc` = 1080.
  - `tam`: `(rong/2, day*0.5)`. Ngang ra `(640, 310)`, đúng `TAM` cũ.
- `kho.tu_meta(meta) -> Kho`.
- `du["kho"] = {"ten","rong","cao","day","tamX","tamY"}`.
- `THI_KHO.dat(du.kho)` đặt `V.kho` trước khi các runtime khác dùng. `may-quay.js` đọc `RONG`, `CAO`, `DAY`, `TAM` từ `V.kho`, không còn hằng số. `ban-tay.js` đặt `NGHI = {x: rong - 60, y: cao + 40}`. Lau bảng quét từ `-120` tới `rong + 120`.
- `chup.trang_moi(browser, kho)` tạo context với `viewport={"width": kho.rong, "height": kho.cao}` và `device_scale_factor=kho.ti_le`. Mọi chỗ gọi truyền `kho`.
- `karaoke.tao_ass(cac_lich, rong, cao)` nhận điểm CSS (`PlayRes`). `ghep.lenh_video` không thêm bộ lọc co giãn, và kiểm kích thước khung đầu tiên bằng `ffprobe`: bằng `rong_xuat`×`cao_xuat`, không thì lỗi `dung`.
- `--xem-truoc` ghi PNG ở kích thước xuất.
- **Đo thời gian:** trước khi sửa, dựng fixture `video-mau` (8 cảnh) với giọng giả ở 720 và ghi thời gian. Sau khi sửa, đo ở 1080 và ghi cả hai số vào `docs/vi/phat-trien/2026-09-27-video-ma-vi12-kiem-thu.md` (tạo mới). Nếu 1080 chậm hơn 1,6 lần 720: đổi khung tạm sang JPEG chất lượng 95 (`page.screenshot(type="jpeg", quality=95)`, ghép bằng `-framerate … -i %06d.jpg`) rồi đo lại. Ghi lại quyết định.

- [ ] **Chụp ảnh tham chiếu trước khi sửa mã:** khung cuối mỗi cảnh của `video-mau` và `video-hinh` ở 1280×720, lưu `tools/vi/tests/data/tham-chieu-vi11/<fixture>-canh-<N>.png`. Commit riêng: `test(vi): capture vi.11 reference frames before the canvas change`.
- [ ] **Tests Python:**
  - `Kho("ngang",1080)` cho 1920×1080; `Kho("doc",1080)` cho 1080×1920; `Kho("ngang",720)` cho 1280×720.
  - `parse` nhận `kho: doc`, `do-phan-giai: 720`; giá trị lạ là `ParseError` nêu đúng dòng.
  - `test_video_ma_parse` cập nhật `META_CHOICES` và `META_DEFAULTS`.
- [ ] **Tests Node:** `THI_KHO.dat` và camera: tâm khổ ngang bằng `(640, 310)`; khổ dọc: mọi toạ độ camera kẹp trong `[0, 720] × [0, 1280]`.
- [ ] **Tests Chromium:**
  - Ở `do-phan-giai: 720`, khung cuối từng cảnh của hai fixture giống ảnh tham chiếu (≤ 0,5 % điểm ảnh lệch quá 16 mức).
  - Ở 1080, PNG xem trước có kích thước 1920×1080.
  - Khổ `doc` với một cảnh `tieu-de`: PNG có kích thước 1080×1920.
- [ ] **Test FFmpeg:** video ngắn dựng ở `doc`, `ffprobe` cho 1080×1920 và 30 fps.
- [ ] Commit `feat(vi): one canvas object and Full HD capture for explainer videos`.

### Task 2: Ô bố cục cho 14 loại cảnh (khổ ngang, không đổi hình)

**Files:**
- Sửa: `runtime/kho.js` (bảng ô), `kho.py` (bảng ô giống hệt, cho kiểm tràn và karaoke), `khung-video.js` (`tieuDe`, `cot`, `hinh`, `anh` nhận ô), cả 14 file `runtime/canh/*.js`.
- Test: `tools/vi/tests/js/test_kho.js`, `test_video_ma_kho.py`, Chromium.

**Interfaces:**
- `V.o(ten)` trả `{x, y, w, h}` theo `V.kho.ten`. Tên ô bắt buộc:
  - `tieu-de`, `noi-dung`, `noi-dung-hep` (khi có cột phụ);
  - `cot-phu` (ô hình/ảnh/nhân vật; khổ ngang là cột phải `x 900, y 200, w 320, h 380`);
  - `anh-lon` (`80, 70, 1120, 490` ở ngang);
  - `hai-cot-trai`, `hai-cot-phai`;
  - `bieu-do`, `so-do`, `dong-thoi-gian`, `cau-hoi`, `thi-nghiem`;
  - `the` (thẻ thông tin), `tai-lieu`, `nhan-vat`.
  Giá trị khổ ngang lấy **đúng** toạ độ đang ghi cứng trong các module (người thực hiện đọc từng file và chép sang). Không đổi hình là tiêu chí.
- `kho.O[ten_kho][ten_o]` trong Python là cùng bảng. Một test so khớp hai bảng bằng cách đọc `kho.js` qua Node hoặc qua một file JSON chung. Khuyến nghị: bảng đặt trong `runtime/o-bo-cuc.json`; `kho.js` nhận nó qua `trang.py` nhúng; `kho.py` đọc file đó. Một nguồn duy nhất.
- Mọi số toạ độ trong `runtime/canh/*.js` được thay bằng phép tính trên ô. Ví dụ `cong-thuc.js` `V.hopQua(100,190,cot?760:1080,150,21)` thành `var o = V.o(cot ? 'noi-dung-hep' : 'noi-dung'); V.hopQua(o.x, o.y, o.w, 150, 21)`.

- [ ] **Test Node:** mọi ô của `ngang` nằm trong 1280×720, và đáy của ô nội dung ≤ `day`.
- [ ] **Test grep:** không file nào trong `runtime/canh/*.js` còn chứa số nguyên ≥ 200 dùng làm toạ độ. Viết test Python quét file, cho phép danh sách ngoại lệ có chú thích lý do (ví dụ thời gian tính bằng ms).
- [ ] **Test Chromium:** so ảnh tham chiếu của Task 1 vẫn đạt.
- [ ] Commit `refactor(vi): place explainer scene content in named layout boxes`.

### Task 3: Bố cục dọc cho 14 loại cảnh và giới hạn chữ khổ dọc

**Files:**
- Sửa: `runtime/o-bo-cuc.json` (thêm `doc`), các module cảnh chỉ khi bố cục dọc cần xếp khác, `kiem.py` (`LIMITS_DOC`), `khung-video.js` (kiểm tràn theo `V.kho`).
- Test: Chromium `test_video_ma_kho_doc.py` (mới), `test_video_ma_parse.py`.

**Interfaces:**
- Khổ dọc 720×1280, `day` = 1080, lề 48.
- Quy tắc ô dọc:
  - `tieu-de` ở trên (y 110).
  - `cot-phu` thành khối dưới nội dung: `x 160, y 640, w 400, h 380`.
  - `noi-dung-hep` là `noi-dung` với chiều cao đến y 620.
  - `hai-cot-trai`/`hai-cot-phai` xếp chồng: trên, rồi dưới.
  - `bieu-do`, `so-do`, `dong-thoi-gian` dùng toàn chiều rộng.
  - `dong-thoi-gian` vẫn nằm ngang, mốc so le trên dưới.
  - `cau-hoi`: lựa chọn xếp một cột.
- `kiem.LIMITS_DOC[(loai, truong)]`: bảng giới hạn khổ dọc. Người thực hiện xác định bằng đo. Mỗi giới hạn dọc ≤ giới hạn ngang tương ứng, và là số lớn nhất mà chuỗi thử nghiệm dưới đây vẫn qua ở cả hai phong cách (phong cách `cat-dan` có ở Task 4; đo lại ở Task 4 và hạ nếu cần). Ghi bảng đo vào file kiểm thử.
- `kiem` dùng `LIMITS_DOC` khi `kho: doc`. Lỗi `canh` nêu rõ "giới hạn khổ dọc".

- [ ] **Test Chromium:** với mỗi loại trong `SCENE_TYPES`, dựng một cảnh ở giới hạn khổ dọc. Chuỗi thử là "Nghiêng nghiễm nhiên " lặp cắt đúng độ dài. Kiểm:
  - không phần tử nào ra ngoài 720×1280;
  - không phần tử nội dung nào có đáy > 1080;
  - `kiemTran()` trả rỗng.
- [ ] **Test Python:** vượt `LIMITS_DOC` là `CanhError` nêu đúng dòng; cùng chuỗi đó ở khổ ngang thì qua (khi giới hạn ngang lớn hơn).
- [ ] Commit `feat(vi): vertical 9:16 layouts for every explainer scene type`.

## Đợt B — Cắt dán, thẻ, tài liệu, khung loạt, phụ đề

### Task 4: Font Be Vietnam Pro và phong cách `cat-dan`

**Files:**
- Tạo: `runtime/fonts/BeVietnamPro-Regular.ttf`, `runtime/fonts/BeVietnamPro-ExtraBold.ttf`, `runtime/fonts/OFL-BeVietnamPro.txt`, `runtime/cat-dan.css`, `runtime/cat-dan.js`.
- Sửa: `runtime/fonts/README.md`, `phong.py`, `trang.py`, `khung-video.js` (kiểu hiện chữ theo chủ đề), `parse.py`, `lich.py` (`du["chuDe"]`), `hinh.js` (sticker).
- Test: `test_video_ma_phong.py`, `tools/vi/tests/js/test_cat_dan.js` (mới), Chromium.

**Interfaces:**
- **Font:** tải hai file TTF từ kho `google/fonts` (`ofl/bevietnampro/`, thẻ commit cố định) một lần khi làm task, và ghi rõ nguồn, phiên bản, SHA-256 trong `fonts/README.md`. Kho repo không chứa địa chỉ web nào trong trang dựng.
- `phong.font_css(chu_de)`:
  - `viet-tay`: như cũ;
  - `cat-dan`: nhúng hai độ đậm dưới tên `BeVietnamPro` (weight 400 và 800) và vẫn nhúng Itim (dùng cho phụ đề `viet-tay`).
  - `phong.bang_ma` kiểm cả hai file đủ `CHU_VIET`.
- **Chủ đề `du["chuDe"]`:**
  - `viet-tay` = `{ten, font:'Itim', hienChu:'viet', net:'ve'}`;
  - `cat-dan` = `{ten, font:'BeVietnamPro', hienChu:'truot', net:'nhanh', mauNhan:[...4 màu], giay:'#f3ead7'}`.
  - Bốn màu nhãn: `#e8a33d` (cam), `#1f6f78` (xanh két), `#c8452f` (đỏ gạch), `#2f4f9e` (xanh dương). Màu của cảnh N là `mauNhan[(N-1) % 4]`.
- **`THI_CAT_DAN`** (thuần, chạy được trong Node):
  - `prng(hat)`: mulberry32.
  - `giayXe(hat, x, y, w, h, doRang)`: trả chuỗi `points` của đa giác mép răng cưa, cùng hạt ra cùng chuỗi.
  - `chamLuoi(id, buoc, banKinh)`: `<pattern>` SVG.
  - `bangDinh(hat, x, y, w)`: hình chữ nhật xoay ±6°, mép răng.
  - `nenGiay(hat, kho)`: SVG nền gồm giấy kem, vân mờ (`feTurbulence` với `seed` = hạt), 2–4 mảng giấy xé màu ở mép và một vùng chấm lưới. Không mảng nào che vùng nội dung quá 15 % diện tích.
- **Nhãn tiêu đề cảnh:** chữ hoa ExtraBold trắng, trên dải băng dính màu `mauNhan` của cảnh, ở góc trái trên của ô `tieu-de`. Hiện bằng trượt từ trái 0,35 s.
- **Hiện chữ ở `truot`:** mỗi mục chữ trượt lên 14 px và mờ dần 0,35 s, bắt đầu tại `batDau` của mục. Không có bàn tay. Nhấn ý (`==`, `((`, `__`, `{{}}`) vẫn chạy như vi.11.
- **Sticker (`hinh.js`):** ở `cat-dan`, biểu tượng và ảnh có viền trắng 6 px, bóng đổ `0 6px 14px rgba(0,0,0,.25)`, xoay `(prng(hat)()*6-3)` độ. Hiện bằng `easeOutBack` scale 0,6 → 1 trong 0,45 s.
- **Thứ tự hiện:** nền ở 0 s; hình chính ở 0,3 s; tiêu đề ở 0,4 s; các mục chữ theo `batDau` của chúng (không sớm hơn 0,6 s); thẻ theo Task 6; tài liệu 0,5 s sau mục cuối.
- **Nét vẽ `nhanh`:** mọi `net` vẽ trong `min(thoiLuong, 0.5)` s, độ dày ×1,4.
- `parse` nhận `phong-cach: cat-dan`.

- [ ] **Tests Python:** hai file Be Vietnam Pro đủ `CHU_VIET`; `font_css('cat-dan')` chứa hai `@font-face`.
- [ ] **Tests Node:**
  - `giayXe` cùng hạt ra cùng chuỗi, khác hạt ra khác chuỗi;
  - mọi điểm nằm trong hộp cho trước ± `doRang`;
  - màu nhãn xoay vòng đúng.
- [ ] **Tests Chromium:**
  - Mọi loại cảnh ở `cat-dan` × 2 khổ, ở giới hạn chữ của khổ đó: không tràn, không dưới `day`. Nếu Be Vietnam Pro làm tràn thì hạ `LIMITS`/`LIMITS_DOC` và ghi lý do vào file kiểm thử. Không được hạ giới hạn của `viet-tay` ngang: nếu cần, thêm bảng `LIMITS_CAT_DAN`.
  - `document.fonts.check('800 20px BeVietnamPro', 'Nghiễm')` đúng.
  - Hai lần dựng cùng cảnh cho cùng PNG.
- [ ] Commit `feat(vi): paper-collage style with Be Vietnam Pro for explainer videos`.

### Task 5: Chuyển cảnh `xe-giay` và mặc định theo phong cách

**Files:**
- Sửa: `runtime/chuyen-canh.js`, `parse.py`, `lich.py` (`kieu_chuyen` và mặc định theo phong cách; `CHUYEN_XOAY` không đổi), `ban-tay.js` (không có giẻ ở `xe-giay`).
- Test: `tools/vi/tests/js/test_chuyen_dong.js`, `test_video_ma_lich.py`.

**Interfaces:**
- `THI_CHUYEN.trangThai('xe-giay', t, dai)`: nền cũ bị "xé" bằng một mép răng cưa (`giayXe` với hạt cố định) quét từ trái sang phải. `clipPath` của nền cũ là đa giác phía phải mép. Có bóng dọc mép. Tại `t = 0` nền cũ che toàn bộ; tại `t ≥ dai` không còn.
- **Mặc định:** khi `phong-cach: cat-dan` và kịch bản không ghi `chuyen-canh` thì dùng `xe-giay`; không ghi `ban-tay` thì `khong`. Hàm `lich.mac_dinh(meta, khoa)` tập trung các mặc định theo phong cách, và `du_lieu_canh` dùng nó.
- `luan-phien` giữ đúng 5 kiểu cũ (không thêm `xe-giay`, để không đổi kịch bản cũ).

- [ ] **Tests:**
  - Node: các điểm đầu và cuối của `xe-giay`.
  - Python:
    - `cat-dan` không ghi gì → chuyển `xe-giay`, `banTay` false;
    - `cat-dan` ghi `ban-tay: co` → true;
    - `viet-tay` không ghi → `lau-bang` như cũ.
- [ ] Commit `feat(vi): torn-paper transition and collage defaults`.

### Task 6: Thẻ thông tin, dòng tài liệu, công thức không ngắt, khung loạt

**Files:**
- Tạo: `runtime/khung-loat.js`.
- Sửa: `parse.py` (trường `the`, `tai-lieu`; khoá `loat`), `kiem.py` (giới hạn), `lich.py` (`du["the"]`, `du["taiLieu"]`, `du["loat"] = {ten, so, tong}`), `khung-video.js` (dựng thẻ và tài liệu trong ô `the`, `tai-lieu`), `canh/cong-thuc.js`, `viet-tay.css` và `cat-dan.css`, `trang.py`.
- Test: `test_video_ma_parse.py`, `test_video_ma_lich.py`, Chromium.

**Interfaces:**
- `the: <nhãn> | <giá trị> | <chú thích>` tách ba phần bằng ` | `; phần chú thích được bỏ trống. Giới hạn nhãn ≤ 24, giá trị ≤ 16, chú thích ≤ 60, tính trên chữ hiển thị. Giá trị nhận `{{số}}` (số chạy).
- Dựng thẻ:
  - `cat-dan`: nền giấy trắng ngà, viền đen 2 px, bóng lệch 4 px; nhãn chữ hoa nhỏ màu `mauNhan`; giá trị ExtraBold 44 px; chú thích 16 px.
  - `viet-tay`: khung nét vẽ tay, giá trị viết bằng bút.
  - Thẻ hiện sau mục chữ đầu tiên 0,3 s.
- Ô `the`:
  - Ngang: góc phải trên nội dung khi không có cột phụ; khi có cột phụ thì đặt dưới tiêu đề, bên trái.
  - Dọc: dưới tiêu đề.
  - Không trùng ô nhân vật hay cột phụ; kiểm bằng test giao nhau của ô.
- `tai-lieu: <chữ ≤ 90>`: chữ 12 px (ngang) hoặc 13 px (dọc), dạng "Nguồn: …". Tự thêm "Nguồn: " nếu thiếu. Nằm ở ô `tai-lieu`, trên `day`, không trùng dòng nguồn ảnh.
- **Công thức:** mỗi phần của `bieu-thuc` là `<span class="phan" style="white-space:nowrap">`. Phần rộng hơn ô thì thu cỡ chữ theo bậc 5 % tới 70 %. Vẫn rộng thì `kiemTran()` báo, và Python ra lỗi `canh`: "Cảnh N: phần công thức "<phần>" quá dài cho khổ này".
- **`loat: <≤ 30>`:** lớp `#khung-loat` đứng yên (ngoài `#bang`, giống `#nhac-nguon`).
  - Trái trên: tên loạt, chữ hoa 12 px, giãn chữ 0,12 em.
  - Phải trên: "0k/N" (hai chữ số khi N ≥ 10: "03/12"; N < 10: "03/08").
  - Màu theo chủ đề.
  - Hiện từ khung đầu của mỗi cảnh. Ô `tieu-de` các khổ chừa 40 px phía trên cho lớp này; nếu Task 2 đã đặt tiêu đề sát mép trên thì dời ô tiêu đề **chỉ khi có `loat`**, để kịch bản cũ không đổi hình.

- [ ] **Tests:**
  - parse và kiem các trường mới, lỗi đúng dòng;
  - `the` ở loại cảnh không cho phép → `ParseError`.
  - Chromium:
    - thẻ ở giới hạn không tràn, ở cả 4 tổ hợp khổ × phong cách;
    - công thức "M x V = P x Y" ở khổ dọc: 1 dòng, không bị ngắt;
    - khung loạt: toạ độ màn hình của "03/08" không đổi giữa khung đầu và khung cuối cảnh (camera chạy);
    - không có `loat` thì không có phần tử `#khung-loat`.
- [ ] Commit `feat(vi): info cards, source lines, unbroken formulas and series header`.

### Task 7: Phụ đề có khung, khổ dọc, font theo chủ đề

**Files:** sửa `karaoke.py`, `ghep.py` (`STYLE` theo chủ đề và khổ, font dir chứa Be Vietnam Pro). Test: `test_video_ma_karaoke.py`, FFmpeg.

**Interfaces:**
- `karaoke.kieu_phu_de(chu_de, kho) -> dict {font, co, khung: bool, gioi_han}`:
  - `viet-tay` ngang: như cũ (Itim, không khung, 42 ký tự).
  - `cat-dan` hoặc bất kỳ `doc`: có khung. `.ass` `BorderStyle=3`, `BackColour=&H66000000&` (nền đen 60 %), `OutlineColour` bằng nền để khung liền, chữ trắng, `SecondaryColour` vàng `&H0000D7FF&` cho `\kf`.
  - Font: `BeVietnamPro` ở `cat-dan`, Itim ở `viet-tay`.
  - Giới hạn: 42 ký tự ngang, 22 ký tự dọc, tối đa 2 dòng.
- `phu-de: hinh` (`.srt` + `force_style`) nhận cùng khung khi `kho: doc` hoặc `cat-dan`.
- Câu dài hơn 2 dòng ở khổ dọc: tách thành nhiều sự kiện theo dấu phẩy, rồi theo từ (thời gian chia theo mốc từ), và thêm cảnh báo "Cảnh N: câu phụ đề dài, đã tách thành k phần".

- [ ] **Tests:**
  - `.ass` của `cat-dan` có `BorderStyle=3`;
  - mọi dòng ở `doc` ≤ 22 ký tự hiển thị;
  - tổng `\kf` của các phần bằng thời lượng câu;
  - `viet-tay` ngang ra `.ass` giống hệt vi.11 (so với chuỗi chụp từ `tao_ass` trước khi sửa).
  - FFmpeg: in phụ đề `cat-dan` lên khung 1080×1920 thành công.
- [ ] Commit `feat(vi): boxed subtitles for collage and vertical videos`.

## Đợt C — Nhân vật, kho mẫu, cảnh kể chuyện

### Task 8: Người que và trường `tu-the`

**Files:**
- Tạo: `runtime/nhan-vat.js`.
- Sửa: `parse.py` (khoá `nhan-vat`, `mau-ao`; trường `tu-the`; luật loại trừ), `lich.py` (`du["nhanVat"] = {kieu:'nguoi-que'|'anh', mauAo, tuThe, anh?}`), `khung-video.js` (dựng nhân vật trong ô `nhan-vat`, hoặc `cot-phu` với `tieu-de`, `khai-niem`, `y-tung-y`), `trang.py`.
- Test: `tools/vi/tests/js/test_nhan_vat.js` (mới), `test_video_ma_parse.py`, Chromium.

**Interfaces:**
- `THI_NHAN_VAT.TU_THE`: mảng 10 tên theo đúng thứ tự ở Global Constraints.
- `THI_NHAN_VAT.dang(tuThe, t)` (thuần):
  - Trả `{khop: {dau:{x,y,r}, co, vaiT, vaiP, khuyuT, khuyuP, tayT, tayP, hong, goiT, goiP, chanT, chanP}, mat: {mat:'tron'|'cuoi'|'nham'|'xoay'|'to', mieng:'cuoi'|'mo'|'ngang'|'meo'|'o', may:'ngang'|'nhuong'|'chau'}}`.
  - Toạ độ ở hệ riêng của nhân vật: gốc giữa hai chân, cao 300 đơn vị. Nhân vật được co giãn vào ô.
- **Chuyển động:**
  - Nhún thở: `y` của mọi khớp trên hông dịch `3*sin(2π t / 2.4)` đơn vị.
  - Chớp mắt: `mat` = `nham` trong 0,12 s tại các mốc `1.3 + 3.1*k + 0.4*((k*7) % 3)`.
  - Cử chỉ trong 1,2 s đầu cảnh:
    - `chao`: tay phải vẫy ±25° ba lần;
    - `chi-tay`: tay duỗi dần về phía nội dung;
    - `vo-dau`: hai tay rung ±6° trên đầu;
    - `an-mung`: hai tay giơ lên kèm bật nhảy 12 đơn vị;
    - các tư thế khác: vào tư thế bằng `easeOutBack`.
- **Nét mặt theo tư thế:**
  - `suy-nghi`: tay chạm cằm, mắt nhìn lên;
  - `ngac-nhien`: mắt tròn to, miệng `o`;
  - `vo-dau`: mắt xoáy, miệng `meo`;
  - `buon`: mày chau, miệng `meo`;
  - `dung-lai`: tay phải giơ lòng bàn tay, mày chau;
  - `giai-thich`: tay mở lòng bàn tay về phía nội dung.
- **Vẽ:** SVG. Đầu tròn trắng viền đen 4. Áo là hình thang tròn góc màu `mauAo`. Tay chân là nét đen 7, đầu tròn. Giày là elip xám đậm. Tám màu áo lấy từ bảng hex cố định.
- **Hướng:** nhân vật quay mặt về phía nội dung (lật ngang khi đứng bên phải nội dung).
- **Hiện:** bật vào `easeOutBack` 0,6 → 1 trong 0,4 s, bắt đầu ở 0,2 s.
- **Luật `parse`:**
  - `tu-the` chỉ ở `tieu-de`, `khai-niem`, `y-tung-y`, `ke-chuyen`;
  - không được cùng `hinh` hoặc `anh`;
  - lỗi khi `nhan-vat: khong`;
  - tên sai → gợi ý tối đa 3 tên theo khoảng cách chỉnh sửa trên chữ bỏ dấu và bỏ gạch.

- [ ] **Tests Node:**
  - Mỗi tư thế tại `t` = 0, 0,6, 5: mọi khớp nằm trong hộp `[-150,150] × [-310, 0]`; hai chân có `y` = 0 (± 0,5).
  - Xác định: gọi hai lần ra cùng kết quả.
  - Chớp mắt đúng mốc.
- [ ] **Tests Python:** các trường hợp lỗi ở Review Focus 5.
- [ ] **Tests Chromium:** nhân vật ở `cot-phu` của `khai-niem` (cả 2 khổ) nằm trong ô, không đè chữ (giao hộp bằng 0).
- [ ] Commit `feat(vi): stick-figure narrator with ten poses`.

### Task 9: Kho 8 nền mẫu vẽ bằng mã

**Files:** tạo `runtime/nen-mau.js`. Test: `tools/vi/tests/js/test_nen_mau.js` (mới), Chromium.

**Interfaces:**
- `THI_NEN_MAU.TEN`: đúng 8 tên ở Global Constraints.
- `THI_NEN_MAU.ve(ten, kho, hat)` trả chuỗi SVG kín khổ `kho.rong`×`kho.cao`. Phong cách phẳng, bảng màu dịu, không chữ.
  - `giay`: `THI_CAT_DAN.nenGiay`.
  - `bau-troi`: chuyển sắc trời, mây tròn, đồi xa.
  - `vu-tru`: nền xanh đêm, sao theo PRNG, chòm nối nét mảnh, hành tinh.
  - `lop-hoc`: tường, bảng xanh viền gỗ (bảng trống), bàn phía trước, cửa sổ.
  - `phong-thi-nghiem`: kệ với bình, ống nghiệm dạng hình khối, bàn đá.
  - `thanh-pho`: dãy nhà khối nhiều tầng có cửa sổ, đường.
  - `dong-que`: đồng lúa sọc, hàng tre, núi xa, mặt trời.
  - `vong-tron`: nền kem và các vòng tròn màu viền dày như video mẫu.
- **Quy tắc bố cục:** vùng giữa (ô `noi-dung`) có độ tương phản thấp. Nếu cần thì thêm lớp phủ mờ trắng 25 %, để chữ và nhân vật nổi.
- **Khổ dọc:** không co giãn hình ngang mà bố trí lại (trời cao hơn, cảnh vật ở nửa dưới).

- [ ] **Tests Node:**
  - Mỗi tên × 2 khổ ra SVG có `viewBox` đúng khổ và không có `<text>`;
  - cùng hạt ra cùng chuỗi;
  - tên lạ ném lỗi.
- [ ] **Test Chromium:** chụp mỗi nền × 2 khổ vào `xem-truoc`-style PNG (trong thư mục tạm của test). Độ lệch chuẩn độ sáng của vùng ô `noi-dung` ≤ 40 (thang 0–255), để chữ đọc được.
- [ ] Commit `feat(vi): eight code-drawn backgrounds for story scenes`.

### Task 10: Cảnh `ke-chuyen`, giá trị `nen`, nhân vật ảnh, dòng "tạo bằng AI"

**Files:**
- Tạo: `runtime/canh/ke-chuyen.js`.
- Sửa: `parse.py` (`SCENE_SPEC["ke-chuyen"]` ở cuối; giải `nen`), `kiem.py` (giới hạn `tieu-de` ≤ 36 ngang / ≤ 28 dọc), `anh.py` (đường `ai/`, nguồn từ `anh/ai/nguon.json`), `lich.py`, `khung-video.js` (lớp nền dưới `#bang`, lớp nhân vật; dòng AI cạnh nguồn nhạc), `trang.py`.
- Test: `test_video_ma_parse.py`, `test_video_ma_anh.py`, `test_video_ma_lich.py`, `tools/vi/tests/js/test_canh.js`, Chromium.

**Interfaces:**
- `SCENE_SPEC["ke-chuyen"] = (("tieu-de", "nen"), ("tu-the", "vi-tri", "the", "tai-lieu"), {})`. `loi` như mọi loại.
- `parse.giai_nen(value, so_canh, cac_canh) -> dict`:
  - `{"kieu":"mau","ten":…}`: dạng `mau/<tên>`.
  - `{"kieu":"file","file":…}`: tên file trần trong `anh/`.
  - `{"kieu":"ai","mo_ta":…,"file":"ai/nen-<N>.jpg"}`: dạng `ve: <mô tả ≤ 200>`.
  - `{"kieu":"nhu","canh":k}`: dạng `nhu-canh <k>`. k phải < N và là `ke-chuyen`; chuỗi `nhu` được giải về nền gốc.
  - Lỗi như Review Focus 3.
- **Ảnh nền:** `anh.doc` nhận `ai/<file>`. `_hop_le` cho phép đúng một tiền tố `ai/`, không cho `..`. Nguồn của file `ai/…`:
  - lấy từ `anh/ai/nguon.json` (`[{file, cong_cu, mo_hinh, prompt, ngay}]`, do Task 12 ghi);
  - thiếu thì `AnhError` với cách sửa "chạy `python tools/vi/anh_ai.py <thư_mục> nhan`";
  - file không có thì `CanhError` liệt kê mọi file AI thiếu của cả video trong một lần, kèm cách sửa ở spec Q11.
- **Nhân vật ảnh** (`nhan-vat: ve: …`): cảnh có `tu-the X` dùng `anh/ai/tu-the-X.png` (PNG có alpha). Không có alpha (PNG không kênh alpha, hoặc JPEG) thì lỗi `canh` "chưa tách nền".
- **Dựng `ke-chuyen`:**
  - Nền phủ kín khung (`object-fit: cover` bằng tính toán), phóng 1,00 → 1,06 tuyến tính suốt cảnh quanh tâm ảnh. Lớp nền không chịu camera `may-quay` (camera tắt trong cảnh này), để tránh phóng hai lần.
  - Nhân vật trong ô `nhan-vat` theo `vi-tri`. Mặc định: cảnh chẵn `phai`, cảnh lẻ `trai`; `giua` đặt giữa phía dưới.
  - Tiêu đề: ngang là chữ vàng `#ffd84d` viền đen 3 px ở giữa trên (`viet-tay` và mặc định). Ở `cat-dan` là nhãn băng dính như Task 4.
  - Thẻ và tài liệu như Task 6.
  - `loi` chỉ lên phụ đề.
- **Dòng AI:** `du["nhacNguon"]` mở rộng thành danh sách `du["dongNguon"]`. Có ảnh AI trong video thì thêm "Hình minh hoạ tạo bằng AI (<các mô hình, cách nhau bởi dấu phẩy>)". Hiện 4 s cuối video; hai dòng xếp chồng, dòng AI ở trên.

- [ ] **Tests Python:**
  - `giai_nen` đủ 4 dạng và các lỗi;
  - `anh.doc('ai/nen-2.jpg')` có nguồn AI;
  - `ai/../x` bị chặn;
  - thiếu 3 file AI → một lỗi liệt kê đủ 3.
  - `test_video_ma_cong_cu`: 8 loại đầu không đổi thứ tự.
- [ ] **Tests Node:** các mục của `ke-chuyen` bắt đầu đúng 0,2 / 0,4 / … và không mục nào vượt cuối cảnh 2,5 s.
- [ ] **Tests Chromium:**
  - `ke-chuyen` với `mau/lop-hoc` + người que × 2 khổ × 2 phong cách: không tràn;
  - nền phủ kín (không điểm ảnh trong suốt ở 4 góc khung);
  - nhân vật ảnh giả (PNG alpha tạo bằng FFmpeg) hiện đúng ô.
- [ ] Commit `feat(vi): story scenes with full-bleed backgrounds and a narrator`.

## Đợt D — Ảnh do AI của nền tảng vẽ

### Task 11: `anh_ai.py ke-hoach`

**Files:** tạo `tools/vi/anh_ai.py`, `tools/vi/anh_ai_parts/__init__.py`, `tools/vi/anh_ai_parts/cau_lenh.py`. Test: `tools/vi/tests/test_anh_ai.py` (mới).

**Interfaces:**
- CLI:
  - `python tools/vi/anh_ai.py <thư_mục_video> ke-hoach`
  - `python tools/vi/anh_ai.py <thư_mục_video> nhan [--cong-cu <tên>] [--mo-hinh <tên>]`
  - In đúng một dòng JSON: `{ready, files, so_anh, ke_hoach, warnings, error}`.
- `cau_lenh.PHONG_CACH_ANH`: câu phong cách cố định tiếng Anh theo `phong-cach`:
  - `viet-tay` → `"warm hand-drawn children's book illustration, soft watercolor texture, clean ink outlines, cozy natural light"`;
  - `cat-dan` → `"editorial paper collage, cut-paper shapes, torn edges, halftone dots, vintage print texture, flat bold colors"`.
- `cau_lenh.CAM`: `"No text, no letters, no numbers, no captions, no logos, no watermark, no signature."`.
- `cau_lenh.nen(mo_ta, phong_cach, kho) -> str`: ghép phong cách, "Background scene for an educational explainer video, <16:9 landscape|9:16 portrait> composition, leave the center area calm and uncluttered for a character and titles, no people.", mô tả của thầy cô (giữ nguyên tiếng Việt), `CAM`.
- `cau_lenh.nhan_vat_mau(mo_ta, phong_cach) -> str`: "Character reference sheet: one single full-body character, front view, standing straight, neutral friendly expression, centered, on a solid pure green (#00FF00) background with no shadow and no gradient; the character must not wear or hold anything green." + phong cách + mô tả + `CAM`.
- `cau_lenh.tu_the(ten, mo_ta, phong_cach) -> str`: "The same character as the reference image, same face, hair, clothes and colors; full body, <mô tả tư thế tiếng Anh cố định theo tên>, on a solid pure green (#00FF00) background, no shadow." + `CAM`. Mười mô tả tư thế tiếng Anh cố định trong `cau_lenh.TU_THE_EN`.
- `ke-hoach` ghi `anh/ai/ke-hoach.json`: `{"phong_cach", "kho", "muc": [{"file", "loai": "nen"|"nhan-vat-mau"|"tu-the", "prompt", "kich_thuoc": "1920x1080"|"1080x1920"|"1024x1536", "tham_chieu": null|"goc/nhan-vat-mau.png", "canh": [N...]}]}`.
  - Thứ tự: nhân vật mẫu trước, các tư thế đã dùng (theo thứ tự `TU_THE`), rồi các nền `ve:` theo số cảnh. Mỗi nền `ve:` là một mục; `nhu-canh` không tạo mục.
  - File đích luôn nằm trong `anh/ai/goc/`, trường `file` là tên trần.
- Cùng `video.md` → cùng `ke-hoach.json`, từng byte (sắp khoá, `ensure_ascii=False`, thụt 2).
- Không có mục nào (không `ve:`) → `ready: true`, `so_anh: 0`, cảnh báo "Video không dùng ảnh AI".

- [ ] **Tests:**
  - Kế hoạch cho một `video.md` mẫu có 2 nền `ve:`, 1 nền `nhu-canh`, nhân vật `ve:` dùng 3 tư thế → đúng 6 mục, đúng thứ tự;
  - mọi `prompt` chứa `CAM`;
  - mục tư thế có `tham_chieu`;
  - chạy hai lần ra cùng byte;
  - `video.md` lỗi → `error.step == "parse"`.
- [ ] Commit `feat(vi): plan consistent AI image prompts for explainer videos`.

### Task 12: `anh_ai.py nhan`

**Files:** tạo `tools/vi/anh_ai_parts/xu_ly.py`; sửa `tools/vi/anh_ai.py`. Test: `tools/vi/tests/test_anh_ai.py` (lệnh giả), `tools/vi/tests/test_anh_ai_ffmpeg.py` (FFmpeg thật).

**Interfaces:**
- **Tìm file:** mỗi mục trong kế hoạch được tìm ở `anh/ai/goc/` với các đuôi `.png`, `.jpg`, `.jpeg`, `.webp` (tên gốc không đuôi). Thiếu thì gom tất cả vào **một** lỗi `thieu`, liệt kê đủ.
- **Nền** → `anh/ai/nen-<N>.jpg`:
  - `scale` giữ tỉ lệ để phủ đủ khổ xuất, rồi `crop` giữa, JPEG `-q:v 3`.
  - Nhỏ hơn khổ xuất ở cả hai chiều sau khi phủ: không phóng thêm quá 1,0. Thay vào đó phủ ở kích thước tối đa có thể, rồi cảnh báo "Ảnh nền cảnh N nhỏ hơn Full HD (<w>x<h>)". `video_ma` vẫn phủ kín khi hiển thị.
  - Lớn hơn 8 MB thì giảm chất lượng tới dưới 8 MB.
- **Nhân vật** → `anh/ai/tu-the-<tên>.png` và `anh/ai/nhan-vat-mau.png`:
  - Bộ lọc `colorkey=0x00FF00:0.30:0.08,despill=type=green`.
  - Cắt sát theo hộp alpha: đo bằng `alphaextract,cropdetect` hoặc tương đương.
  - Kiểm:
    - bốn góc 8×8 của ảnh gốc sau khi tách có alpha trung bình < 10;
    - tỉ lệ điểm đục (alpha > 128) trong khung trước khi cắt nằm trong 5–70 %.
    - Không đạt → lỗi `tach-nen` nêu file và lý do.
- **Nguồn:** ghi `anh/ai/nguon.json`: mỗi file đầu ra kèm `cong_cu` (từ `--cong-cu`, mặc định `"công cụ vẽ của nền tảng"`), `mo_hinh` (từ `--mo-hinh`, mặc định `"AI"`), `prompt`, `ngay` (ISO). Ghi nguyên tử (file tạm rồi đổi tên).
- Không có FFmpeg → `error.step == "ffmpeg"` với cách sửa trỏ `docs/vi/cai-dat-bang-ai.md`.

- [ ] **Tests** (FFmpeg thật, ảnh tổng hợp bằng `lavfi`):
  - Nền: ảnh 1024×1024 → đầu ra phủ 16:9, có cảnh báo; ảnh 2400×1350 → đúng 1920×1080.
  - Nhân vật:
    - hình tròn đỏ trên nền #00FF00 → góc trong suốt, cắt sát;
    - nền #33CC55 loang và có dải tối ở góc → lỗi `tach-nen`.
  - Nhận cả `.jpg` khi kế hoạch ghi `.png`.
  - Thiếu 2 file → một lỗi `thieu` liệt kê 2.
  - `nguon.json` đọc được bởi `anh.doc` (Task 10).
- [ ] Commit `feat(vi): key, crop and credit AI images for explainer videos`.

### Task 13: Tài liệu theo nền tảng

**Files:** sửa `docs/vi/tro-ly/video-giai-thich.md`, `docs/vi/tro-ly/canh-video.md`, `AGENTS.vi.md` §15, `.agents/rules/ppt-master-vi.md`, `CHANGELOG-VI.md` ("Chưa phát hành"), `docs/vi/phat-trien/bao-tri.md` (font mới). Test: `tools/vi/tests/test_vi_layer.py`.

**Nội dung bắt buộc:**
- **`video-giai-thich.md`:**
  - Câu hỏi thêm khổ ("ngang để chiếu lớp hay dọc để đăng TikTok/Reels"), phong cách ("viết tay hay cắt dán"), nhân vật ("không, người que, hay nhân vật do AI vẽ theo mô tả"), tên loạt nếu là một loạt bài. Gộp để vẫn tối đa 7 câu.
  - Khuôn `video.md` mẫu có `ke-chuyen`.
  - Mục mới "Hình do AI vẽ" với bảng theo nền tảng:
    - Antigravity/Codex: chạy `anh_ai.py ke-hoach`; dùng công cụ tạo ảnh của mình cho từng mục (nhân vật mẫu trước, tư thế kèm ảnh mẫu làm tham chiếu, 3–4 ảnh một lượt); lưu đúng tên vào `anh/ai/goc/`; chạy `anh_ai.py nhan --cong-cu … --mo-hinh …`; `--xem-truoc` bắt buộc; thầy cô duyệt.
    - Claude Code và nền tảng không có công cụ vẽ: không có bước vẽ; dùng `nen: mau/…` và `nhan-vat: nguoi-que`.
  - Bảng `error.step` của `anh_ai.py`.
  - Cấm: không để ảnh AI có chữ; không tự viết `nguon.json`.
- **`canh-video.md`:** loại cảnh thứ 15 `ke-chuyen`; trường `the`, `tai-lieu`, `tu-the`, `vi-tri`, `nen` (4 dạng); bảng 10 tư thế có mô tả; bảng 8 nền mẫu; giới hạn khổ dọc. Tiêu đề file đổi thành "mười lăm loại cảnh".
- **`AGENTS.vi.md` §15:**
  - Bước 3 thêm: ảnh AI theo mục "Hình do AI vẽ".
  - Điều cấm "không chạm `skills/`" giữ nguyên.
  - Thêm cho phép "dùng công cụ tạo ảnh của chính nền tảng để vẽ ảnh trong `anh/ai/goc/` theo `ke-hoach.json`".
  - Bảng `error.step` của `anh_ai.py`.
- **`.agents/rules/ppt-master-vi.md`** (nội dung ghi thẳng, file < 12 000 ký tự): mục "Video giải thích" thêm 3 dòng. (1) Antigravity có công cụ tạo ảnh thì dùng nó theo `anh_ai.py ke-hoach`. (2) Luôn chạy `anh_ai.py nhan` rồi `--xem-truoc`. (3) Chữ trên video không bao giờ nằm trong ảnh.
- **`CHANGELOG-VI.md`:** mục "Chưa phát hành" liệt kê Q1–Q15 bằng lời cho thầy cô.

- [ ] **Tests `test_vi_layer.py`:**
  - `canh-video.md` liệt kê đủ tên trong `parse.SCENE_TYPES` (test mới, chặn lệch giữa tài liệu và mã);
  - `video-giai-thich.md` có mục "## Hình do AI vẽ" chứa "anh_ai.py ke-hoach", "anh_ai.py nhan", "--xem-truoc", "Claude Code", "nguoi-que";
  - `.agents/rules` có "anh_ai.py" và dưới 12 000 ký tự;
  - các test số câu hỏi (≤ 7) vẫn qua.
- [ ] Commit `docs(vi): story, collage and AI-image steps for explainer videos`.

### Task 14: Tích hợp, demo và gói chạy thử Antigravity

**Files:**
- Tạo: `tools/vi/fixtures/video-ke-chuyen/video.md` (fixture: `cat-dan`, `doc`, `loat`, người que, 3 cảnh `ke-chuyen` với `mau/…` và `nhu-canh`, 1 `khai-niem` có `the` và `tai-lieu`, 1 `cong-thuc`); `docs/vi/phat-trien/2026-09-27-video-ma-vi12-chay-thu-antigravity.md`.
- Sửa: file kiểm thử `2026-09-27-video-ma-vi12-kiem-thu.md`.
- Test: `test_video_ma_tich_hop.py` (bổ sung).

**Nội dung:**
- **Test tích hợp** (giọng giả, không mạng; chạy bằng Python có playwright):
  - (a) fixture mới, dựng thật, `ffprobe` 1080×1920, 30 fps, có âm thanh, thời lượng khớp lịch ±1 khung;
  - (b) `viet-tay` ngang với một cảnh `ke-chuyen` dùng ảnh "AI" giả (lavfi → `anh/ai/goc/` → `anh_ai.py nhan`): 1920×1080; dòng "tạo bằng AI" có trong trang cảnh cuối.
- **Đo thời gian:** video 5 phút (fixture lặp cảnh), `viet-tay` ngang 1080 và `cat-dan` dọc 1080. Ghi số vào file kiểm thử và so với mục tiêu 12 phút.
- **Demo cho chủ repo** (trong `projects/_video/`, không commit):
  - `in-tien-lam-phat-cat-dan`: kiểu `cat-dan` ngang, 8 cảnh theo nội dung video mẫu, thẻ thông tin, tài liệu, người que;
  - `quy-tac-2-phut-doc`: `ke-chuyen` khổ dọc, người que, nền mẫu.
  - Giọng thật edge-tts. Gửi đường dẫn và thời lượng.
- **Gói chạy thử Antigravity:** file markdown có:
  - (1) một `video.md` 3 cảnh với `nhan-vat: ve: …` và 2 nền `ve:`;
  - (2) câu lệnh nguyên văn thầy cô dán vào Antigravity;
  - (3) những gì cần chụp lại gửi về (ảnh `xem-truoc`, JSON của `anh_ai.py`);
  - (4) tiêu chí đạt: nhân vật đồng nhất ở 3 tư thế, tách nền không viền xanh, không có chữ trong ảnh.
  Chủ repo chạy; kết quả quyết định có phát hành phần nhân vật AI không.
- [ ] Commit `test(vi): end-to-end story, collage and vertical explainer videos`.

---

## Self-review

- **Spec coverage:** Q1 → T1; Q2 → T2, T3; Q3 → T4, T5; Q4 → T4; Q5 → T6; Q6, Q7 → T10; Q8, Q9 → T8; Q10 → T11, T12; Q11 → T10, T12; Q12 → T6; Q13 → T7; Q14 → T6; Q15 → T13. Tiêu chí 4 (kho mẫu) → T9. Tiêu chí Full HD và thời gian → T1, T14. Điều kiện phát hành (chạy thật Antigravity) → T14.
- **Thứ tự phụ thuộc:**
  - T2 cần ô từ T1. T3 cần T2.
  - T4 đo lại giới hạn của T3.
  - T6 dùng ô `the`/`tai-lieu` (T2) và màu nhãn (T4).
  - T10 dùng T8 (nhân vật), T9 (nền) và định dạng `nguon.json` do T12 ghi. Định dạng đã cố định trong T10; T12 phải ghi đúng định dạng đó.
  - T11 dùng `parse.giai_nen` (T10).
- **Tên thống nhất:** `V.o`, `V.kho`, `THI_KHO`, `THI_CAT_DAN`, `THI_NHAN_VAT`, `THI_NEN_MAU`, `THI_CHUYEN`, `du["kho"]`, `du["chuDe"]`, `du["nhanVat"]`, `du["dongNguon"]`, `anh/ai/goc/`, `anh/ai/nguon.json`, `anh/ai/ke-hoach.json`.

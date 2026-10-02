# Nhật ký thay đổi — Bản Việt

## 6.3.2-vi.15 — (chưa phát hành)

Video giải thích chỉ còn một lối: **kiểu Vox**. Video cũ dài gấp đôi yêu cầu (lệnh "video 60 giây" ra gần 2 phút) và bị bó vào khuôn bài giảng (bắt buộc môn, lớp, cảnh tiêu đề, nền lớp học cho cả chuyện công sở). Bản này dạy AI viết kịch bản kiểu Vox cho mọi ngành, đúng thời lượng, hình hiện khớp từng cụm lời, ảnh do AI vẽ theo từng câu.

### Thêm
- Nền riêng cho từng cảnh: mỗi cảnh ghi `nen:` tả nền, `anh_vox.py` vẽ một nền cắt dán cổ điển theo nội dung cảnh (tắt bằng `nen-canh: khong`). Kiểu ảnh mặc định là `phong-anh: cat-dan`.
- Giọng `giong: thu-giang` (VieNeu, đọc ngay trên máy, không cần mạng), mặc định của kiểu Vox; máy không có VieNeu thì tự dùng giọng nữ edge-tts kèm cảnh báo. Đường dẫn python của VieNeu đặt bằng biến môi trường `VIENEU_PYTHON`.
- File `nguon.txt` cạnh video ghi mô hình vẽ ảnh, nguồn ảnh thật, nguồn số liệu và nhạc. Video Vox không hiện dòng nguồn nào trên hình.
- Cảnh báo "vật đầu tiên hiện muộn" khi cảnh mở bằng nền trống.
- `phong-cach: vox`: mỗi cảnh là `bo-cuc` (`mot`, `hai-ben`, `dan-hang`, `chong`, `toan-canh`), `loi` và 1–6 dòng `nhip`. Mỗi nhịp gắn một cụm từ trong lời với một vật (ảnh, thẻ, chữ, nhãn, con dấu, mũi tên, số chạy) ở một ô; vật hiện đúng lúc giọng đọc tới cụm đó. Dựng bằng lớp giấy cắt dán 2,5D: ba lớp sâu, máy quay đẩy và nghiêng nhẹ, ảnh cắt nền viền giấy xé có bóng, ảnh khung mép xé dán băng dính, chuyển cảnh xé giấy và lia nhanh xen nhau, bốn bảng màu giấy.
- `tools/vi/anh_vox.py`: lập danh sách ảnh từ các nhịp, vẽ ảnh AI bằng công cụ vẽ của nền tảng (Antigravity, Codex) hoặc qua API kiểu OpenAI (mặc định 9router trên máy, mô hình `ag/gemini-3.1-flash-image`, cấu hình bằng `ANH_AI_URL`, `ANH_AI_KEY`, `ANH_AI_MO_HINH`), tải ảnh thật `tim:` bằng `image_search.py`, tách nền xanh, tính trước viền xé, bóng, duotone, halftone, và ghi nguồn. Lưu đệm theo mã băm câu lệnh: sửa một nhịp chỉ vẽ lại ảnh đó; tối đa 20 ảnh mới mỗi lần chạy (`--toi-da`); ảnh nền tảng vẽ ghi công cụ và mô hình bằng `--cong-cu`, `--mo-hinh`. Khoá API không bao giờ nằm trong repo, log hay JSON đầu ra.
- Khoá `thoi-luong` (15–600 giây): `video_ma.py --plan-only` trả `thoi_luong_uoc` và cảnh báo khi kịch bản dài quá +15% hay ngắn dưới −25%, nêu số từ cần bớt hay thêm, chạy được trước khi có ảnh; sau khi tạo giọng thì kiểm lại bằng thời lượng thật. `--xem-truoc` của video Vox chụp mỗi cảnh hai ảnh, giữa cảnh và cuối cảnh.
- Hướng dẫn cho AI viết lại hoàn toàn (`docs/vi/tro-ly/video-giai-thich.md`) và file mới `docs/vi/tro-ly/nhip-vox.md`: mạch móc → vấn đề → giải thích → lật → chốt, quỹ từ theo thời lượng (60 giây khoảng 130 từ), "Không bịa số liệu" (số nào cũng có nguồn), phép thử tắt tiếng, chữ trên hình tối đa khoảng 6 từ, bảng chọn bố cục, vòng tự kiểm và một video mẫu 60 giây "Giao tiếp với đồng nghiệp". Từ kích hoạt mới "video vox", "kiểu vox". Mục "Tạo ảnh cho video Vox thất bại" trong Xử lý lỗi.

### Đổi
- Chuyển động của kiểu Vox êm hơn: vật trượt nhẹ vào kèm mờ dần, nền trôi ngang chậm; bỏ rung khung hình, nảy và phóng máy.
- Lời đọc của kiểu Vox liền mạch hơn: khoảng lặng đầu và cuối mỗi cảnh rút còn 0,25 và 0,3 giây. Quỹ từ tính theo giọng (60 giây khoảng 230 từ với giọng Thu Giang).
- Mỗi lần chạy `anh_vox.py` vẽ tối đa 30 ảnh mới (tính cả nền từng cảnh).
- Hướng dẫn và luật chỉ dạy kiểu Vox, không còn giả định bối cảnh trường học. AI chỉ hỏi khi câu lệnh thiếu chủ đề hoặc nội dung, không dừng chờ duyệt kịch bản: tự xem trước, tự sửa, dựng xong mới gửi video kèm kịch bản (người dùng xin xem kịch bản trước thì vẫn dừng).
- Với `phong-cach: vox`, `mon` và `lop` không bắt buộc; các khoá của kiểu viết tay (`ban-tay`, `nhan-vat`, `mau-ao`, `chu-dong`, `may-quay`) là lỗi `parse`.
- Hướng dẫn kiểu viết tay cũ và danh mục mười lăm loại cảnh chuyển sang `docs/vi/tham-khao/video-viet-tay.md` và `docs/vi/tham-khao/canh-video.md`, chỉ dùng khi sửa `video.md` cũ. Luật Antigravity gọn lại, khoảng 8 800 byte.

### Không đổi
- Kịch bản cũ (`viet-tay`, `cat-dan`, có dòng `loai:`) dựng ra như trước, không cần sửa; `anh_ai.py` vẫn dùng cho nền và nhân vật AI của kiểu cũ.

### Rủi ro
- Nguồn vẽ ảnh phụ thuộc tài khoản của người dùng (9router, Antigravity): hết hạn mức hay tài khoản bị khoá thì video Vox vẫn làm được bằng ảnh thật, thẻ, chữ, con dấu nhưng kém sinh động; đổi nguồn chỉ cần đổi `ANH_AI_MO_HINH` hoặc `ANH_AI_URL`.
- Ảnh AI có thể có chữ hoặc sai ý; không kiểm tự động được, AI phải xem ở bước `--xem-truoc` và vẽ lại.
- Vật màu xanh lá bị ăn mất khi tách nền xanh: công cụ tự chuyển sang khung kèm cảnh báo.
- Sửa `video.md` sau khi đã vẽ ảnh (đổi số cảnh, thứ tự nhịp, mô tả `ve:`, tuỳ chọn ảnh) làm ảnh cũ: `--xem-truoc` và dựng thật dừng ở lỗi `canh` "đã cũ so với video.md" tới khi chạy lại `anh_vox.py` (`--plan-only` chỉ cảnh báo, nên vẫn ước được thời lượng trước khi vẽ ảnh).
- Ảnh nền tảng tự vẽ chỉ ghi đúng mô hình khi AI nêu `--mo-hinh`; không nêu thì cuối video ghi "không rõ".

## 6.3.2-vi.14 — 2026-09-30

PPT Master bản Việt đổi tên thành **2Anh Studio**. Bộ công cụ nay làm được nhiều hơn slide (poster, video, giáo án, đề kiểm tra, thí nghiệm ảo, văn bản hành chính) và dùng được ở nhiều ngành, nên tên mới không gắn với PowerPoint hay với một nghề.

### Đổi
- Tên sản phẩm: **2Anh Studio** — trợ lý AI làm slide, video, tài liệu và văn bản. README, NOTICE, tài liệu cài đặt, luật Antigravity và bộ kiểm tra môi trường dùng tên mới; AI giới thiệu bộ công cụ bằng tên mới và vẫn hiểu khi người dùng nhắc "PPT Master".
- Repo GitHub đổi thành `luonghaianh1208/2anh-studio`. Link cũ `luonghaianh1208/PPTmaster` tự chuyển sang link mới.

### Không đổi
- Máy đã cài không phải làm gì: `CAP-NHAT.bat` vẫn cập nhật như cũ, tên các file lệnh (`CAI-DAT.bat`, `KIEM-TRA.bat`, `CAP-NHAT.bat`, `tools/vi/pptmaster.ps1`) và mọi câu lệnh cho AI ("tạo PPT", "làm slide", "soạn công văn"…) giữ nguyên. Thư mục cài sẵn tên `PPTmaster` vẫn dùng bình thường.
- Lõi PPT Master của Hugo He (`skills/ppt-master/`, giấy phép MIT) giữ nguyên tên và ghi công.

### Bản vá (2026-09-30, sau khi gắn tag)
- Văn bản hành chính: ví dụ của ND30 còn ghi "UBND HUYỆN", "trên địa bàn huyện", nên AI dễ chép tên đơn vị cũ. Hướng dẫn nay nói rõ từ 1/7/2025 chính quyền địa phương chỉ còn cấp tỉnh và cấp xã, phường, đặc khu; ví dụ chỉ dùng để lấy khuôn. `van_ban.py` cảnh báo (không chặn) khi văn bản có chữ huyện, quận, thị xã, thị trấn, cả trong `warnings` và `kiem-tra.md`. Thêm gợi ý nơi nhận ghi tên cơ quan, gửi lãnh đạo để báo cáo thì ghi "(để b/c)". Máy đã cài nhận bản vá qua `CAP-NHAT.bat`.
- Luật Antigravity (`.agents/rules/ppt-master-vi.md`) viết gọn lại, từ khoảng 12 000 xuống khoảng 9 300 byte, giữ đủ các quy tắc bắt buộc; còn chỗ cho quy tắc mới dưới giới hạn 12 000 của Antigravity.
- Video giải thích dựng nhanh gần gấp đôi (2026-10-01): khi dựng thật, khung hình được chụp bằng `HeadlessExperimental.beginFrame`, tức lấy ảnh ngay từ khung Chromium vừa vẽ, thay cho `page.screenshot`. Trên máy 6 lõi, video cắt dán 92 giây dựng mất 127 giây thay vì 243 giây; video viết tay 156 giây mất 140 giây thay vì 196 giây. Hình không đổi: khác biệt chỉ ở khử răng cưa mép chữ, mắt thường không thấy. Chromium không hỗ trợ `beginFrame` thì tự quay về cách chụp cũ; ảnh xem trước vẫn chụp như cũ. Không cài thêm gì. Số đo ở `docs/vi/phat-trien/2026-10-01-video-ma-begin-frame.md`.

## 6.3.2-vi.13 — 2026-09-30

Soạn văn bản hành chính đúng thể thức Nghị định 30/2020/NĐ-CP: loại việc thứ 11, dựa trên bộ công cụ ND30 mã nguồn mở của Nguyễn Minh Phát (giấy phép MIT), bỏ phần văn bản Đoàn. AI hỏi một lượt, sinh file Word sửa được, tự kiểm thể thức, và không bao giờ tự bịa số, ngày, người ký hay căn cứ.

### Thêm
- Loại việc thứ 11 "Soạn văn bản hành chính (Nghị định 30)": AI hỏi một lượt 7 câu, viết `noi-dung.json`, rồi `tools/vi/van_ban.py` dựng `van-ban.docx` đúng thể thức Nghị định 30/2020/NĐ-CP và chạy bộ kiểm thể thức, ghi `kiem-tra.md`. Bộ sinh và bộ kiểm là ND30 (© 2026 Nguyễn Minh Phát, MIT) nhúng nguyên trạng ở `tools/vi/nd30/`, có kiểm SHA-256. Làm được cả văn bản quy phạm của HĐND, UBND; văn bản Đảng và văn bản Đoàn không hỗ trợ.
- Không bịa: số, ký hiệu, ngày ban hành, người ký, căn cứ, số tiền chưa có thì để `[CẦN BỔ SUNG: …]`; còn ô nào thì file là bản nháp, được giao kèm danh sách từng ô cần điền. Lỗi thể thức nặng thì không giao file Word.
- Bộ kiểm của ND30 chỉ nhận chức vụ người ký khối cơ quan (GIÁM ĐỐC, CHỦ TỊCH…), nên văn bản do HIỆU TRƯỞNG, PHÓ HIỆU TRƯỞNG, TỔ TRƯỞNG ký luôn bị cảnh báo B6 giả. `van_ban.py` nay coi B6 là đạt khi chức vụ trong `signature` viết in hoa và có trong văn bản; chức vụ trống hoặc chưa in hoa vẫn cảnh báo. Mã ND30 nhúng không bị sửa.
- Câu lệnh chỉ có "báo cáo" hoặc "kế hoạch" (ví dụ "làm báo cáo tổng kết năm học") nay được hỏi thêm đúng một câu trước khi xếp loại: văn bản Word đúng thể thức Nghị định 30 hay slide trình chiếu. Trước đây câu này đi thẳng vào slide "Báo cáo – tổng kết". Hồ sơ đơn vị có thêm ba mục tuỳ chọn: cơ quan chủ quản, địa danh, ký hiệu viết tắt của đơn vị.
- Văn bản để trống người ký, chức vụ, cơ quan ban hành, ký hiệu, trích yếu, địa danh, kính gửi, nội dung hay tháng/năm ban hành cũng là bản nháp, với từng ô được nêu tên; công văn không được đổi sang cách kiểm lỏng hơn để qua bộ kiểm. `kiem-tra.md` có mục "Thầy cô đối chiếu" in nguyên văn số, ngày, người ký, cơ quan, căn cứ để thầy cô soát lại những gì công cụ không tự kiểm được.
- Luật ưu tiên khi xếp loại việc: tên loại văn bản đi với động từ soạn ("soạn công văn…", "ra quyết định…") thắng các từ chủ đề như tập huấn, cuộc thi; từ chỉ đầu ra ("poster", "slide", "video") thắng "thông báo". Dùng được cả ngoài trường học (UBND xã, phòng ban).
- Mã ND30 (`kanazawahere/nd30`, © 2026 Nguyễn Minh Phát, giấy phép MIT) được nhúng nguyên bản gốc tại `tools/vi/nd30/`, ghi công trong README và NOTICE; có test báo khi mã nhúng bị sửa.
- Hướng dẫn cho AI `docs/vi/tro-ly/van-ban-hanh-chinh.md`, mục 16 của `AGENTS.vi.md`, luật Antigravity, và tài liệu cho thầy cô `docs/vi/van-ban-hanh-chinh.md`.

### Rủi ro
- Công văn đặt `profile: bieu-mau-noi-bo` thì bộ kiểm bỏ qua số văn bản và nơi nhận. Hướng dẫn cấm đổi profile để qua bộ kiểm, nhưng công cụ chưa chặn; sẽ sửa ở bản sau.
- Bộ kiểm không xác minh được nội dung pháp lý (căn cứ, thẩm quyền ký): thầy cô soát mục "Thầy cô đối chiếu" trong `kiem-tra.md` trước khi trình ký. Dấu và chữ ký số phải kiểm bằng mắt.
- Văn bản Đảng và văn bản Đoàn chưa hỗ trợ.

## 6.3.2-vi.12 — 2026-09-29

Video giải thích kiểu kể chuyện, cắt dán và khổ dọc Full HD, học từ bốn video mẫu: cảnh kể chuyện có nền tranh và nhân vật dẫn chuyện, phong cách giấy cắt dán kiểu Vox, thẻ thông tin và dòng tài liệu, khung loạt bài, khổ 9:16 1080×1920 cho TikTok và Reels. Hình ảnh do AI của chính nền tảng vẽ (Antigravity, Codex); Claude Code dùng tám nền mẫu và người que vẽ bằng mã. Kèm hai việc thầy cô hay gặp ở slide: câu hỏi mật độ chữ, và "làm đẹp mà ít chữ hơn" nay tạo mới từ file thay vì giữ nguyên văn.

### Thêm
- Mật độ chữ cho Bài giảng, Báo cáo – tổng kết, Hoạt động Đoàn – sự kiện, Tập huấn/workshop: câu hỏi hiệu ứng hỏi thêm "ít chữ, vừa, hay nhiều chữ" (vẫn tối đa 7 câu), brief ghi dòng "Mật độ chữ", và mục mới "Mật độ chữ" trong `quy-trinh-hoi.md` quy đổi sang chế độ đọc `presentation` / `balanced` / `text` của upstream. Ít chữ là mặc định cho bài giảng, tập huấn, hoạt động Đoàn; báo cáo mặc định vừa. Ít chữ chuyển phần giải thích vào lời giảng hoặc chia thêm trang, không bỏ thông tin.
- "Làm đẹp slide mà cho ít chữ hơn / rút gọn / tách trang" nay được chỉ rõ là tạo mới từ file cũ, không dùng Beautify (Beautify giữ nguyên văn từng chữ). Quy tắc này có cả trong luật Antigravity, nơi AI trước đây hay kẹt ở chế độ làm đẹp và trả về slide vẫn dày chữ.
- Video giải thích, khổ dọc và Full HD: khoá đầu `kho: doc` dựng video 9:16 (1080×1920) để đăng TikTok, Reels, Story; khổ ngang mặc định nay xuất Full HD 1920×1080. Chữ và hình được vẽ thật ở độ phân giải đó, không phóng ảnh nhỏ. Máy yếu ghi `do-phan-giai: 720` để dựng nhanh như trước. Mọi loại cảnh có bố cục dọc; vài trường có giới hạn chữ thấp hơn ở khổ dọc để chữ không bao giờ tràn khung hay đè phụ đề. Kịch bản làm từ vi.9–vi.11 dựng được không cần sửa, bố cục viết tay khổ ngang giữ nguyên; mọi thứ mới đều là tuỳ chọn.
- Phong cách cắt dán kiểu Vox (`phong-cach: cat-dan`): nền giấy, mảng giấy xé, chấm lưới, tiêu đề cảnh là nhãn trên băng dính màu, hình và ảnh dạng sticker viền trắng, chữ trượt vào thay cho bút viết, chuyển cảnh mép giấy xé (`xe-giay`). Font Be Vietnam Pro (SIL OFL, thiết kế cho tiếng Việt) đóng gói sẵn, đủ mọi chữ có dấu.
- Thẻ thông tin và dòng tài liệu: `the: <nhãn> | <giá trị> | <chú thích>` hiện một con số đinh (ví dụ "Siêu lạm phát · 1923 · Cộng hoà Weimar"), `tai-lieu:` ghi nguồn nội dung ở góc dưới; dùng được ở cảnh tiêu đề, khái niệm, công thức, ý từng ý và kể chuyện.
- Loại cảnh thứ 15 `ke-chuyen` (kể chuyện): nền tranh kín khung phóng chậm, nhân vật dẫn chuyện, tiêu đề lớn là kết luận của cảnh; lời chỉ ở phụ đề. Nền lấy từ tám nền mẫu vẽ bằng mã (lớp học, phòng thí nghiệm, bầu trời, vũ trụ, thành phố, đồng quê, giấy, vòng tròn; không cần mạng, không vướng giấy phép), từ ảnh thật, từ ảnh AI, hoặc dùng lại nền của cảnh trước (`nhu-canh`).
- Nhân vật dẫn chuyện (`nhan-vat`): người que vẽ sẵn (có trên mọi nền tảng, đổi màu áo bằng `mau-ao`, biết nhún thở, chớp mắt, vẫy tay, duỗi tay chỉ, ôm đầu rối rít, nhảy mừng) hoặc nhân vật do AI vẽ theo mô tả của thầy cô. Mười tư thế chung: đứng, chào, chỉ tay, giải thích, suy nghĩ, ngạc nhiên, vò đầu, dừng lại, ăn mừng, buồn. Nhân vật đứng cạnh chữ ở cảnh tiêu đề, khái niệm, ý từng ý khi cảnh ghi `tu-the`.
- Ảnh AI theo nền tảng: `tools/vi/anh_ai.py ke-hoach` soạn sẵn câu lệnh vẽ thống nhất cho mọi ảnh (cùng một câu phong cách, nhân vật mẫu làm tham chiếu, luôn cấm chữ và logo); trên Antigravity và Codex, AI vẽ bằng công cụ tạo ảnh có sẵn của nền tảng; `anh_ai.py nhan` tách nền xanh của nhân vật, cắt nền về đúng khổ, kiểm độ sạch và ghi nguồn. Video có ảnh AI luôn hiện "Hình minh hoạ tạo bằng AI (<mô hình>)" trong 4 giây cuối, và AI bắt buộc cho thầy cô xem trước từng cảnh. Claude Code không có công cụ vẽ nên dùng nền mẫu và người que. Công cụ dựng không bao giờ gọi AI hay lên mạng; thiếu ảnh AI thì báo đúng file thiếu, không tự thay.
- Hình phải khớp lời đọc: hướng dẫn cho AI có mục mới (mỗi cảnh viết một dòng "lời nói gì — hình cho thấy gì"; cảnh kể chuyện trên nền mẫu phải có thẻ nêu ý của lời; chọn nền và tư thế theo lời; nền AI tả đúng sự vật trong lời; không quá hai cảnh kể chuyện liền nhau). `video_ma.py` cảnh báo ba trường hợp dễ làm hình lạc lời: cảnh kể chuyện nền mẫu không có thẻ, ba cảnh kể chuyện liền nhau, nhân vật một tư thế ba cảnh liền. Các ví dụ trong tài liệu đã sửa theo quy tắc này.
- Khung loạt bài: `loat: <tên loạt>` hiện tên loạt ở góc trái trên và số cảnh "03/08" ở góc phải trên, đứng yên khi máy quay chạy.
- Tài liệu cho AI: câu hỏi thêm khổ, phong cách, nhân vật và tên loạt (vẫn tối đa 7 câu); mục "Hình do AI vẽ" theo từng nền tảng; `canh-video.md` có loại cảnh kể chuyện, bảng mười tư thế, bảng tám nền mẫu và bảng giới hạn theo khổ; `AGENTS.vi.md` mục 15 và luật Antigravity cho phép AI dùng công cụ tạo ảnh của nền tảng để vẽ vào `anh/ai/goc/`.

### Sửa
- ChatGPT Codex chỉ tự đọc `AGENTS.md` nên trước đây bỏ qua toàn bộ quy tắc bản Việt (không hỏi trước, không dùng `venv`). Cuối `AGENTS.md` nay có mục "Vietnamese Edition" trỏ sang `AGENTS.vi.md`, nên Codex, Antigravity, Claude Code và Cursor đều đọc cùng một bộ quy tắc mà không cần câu khởi động. Có test báo lỗi nếu một lần đồng bộ bản gốc làm mất mục này.
- Phụ đề video giải thích khó đọc trên nền sáng: ở phong cách cắt dán và khổ dọc, phụ đề nay có khung nền tối bo góc, chữ trắng, từ đang đọc tô vàng. Phụ đề karaoke nay hiện **một dòng một lúc** ở mọi phong cách và khổ (trước đây hai dòng hiện cùng lúc nên học sinh không biết giọng đang đọc tới đâu): dòng sau thay dòng trước đúng lúc giọng đọc tới, các dòng của một câu được chia dài gần bằng nhau, không còn từ mồ côi. Tối đa 22 ký tự một dòng ở khổ dọc, 42 ở khổ ngang; ở khổ dọc câu dài được ngắt ở dấu phẩy trước. Kiểu viết tay khổ ngang giữ font và màu phụ đề như cũ.
- Công thức bị ngắt dòng giữa chừng (kiểu "M x V = P x / Y"): công thức nay chỉ xuống dòng giữa các phần ` | ` hoặc trước dấu `=`, `≈`…; đoạn quá rộng thì chữ nhỏ dần tới 70 % trước khi xuống dòng ở khoảng trắng, và một cụm liền không bao giờ bị cắt đôi (cụm quá dài thì báo lỗi kèm cách sửa).

### Rủi ro
- Nhân vật do AI vẽ (`nhan-vat: ve:`) là **thử nghiệm**: luồng vẽ nhân vật mẫu rồi từng tư thế có ảnh tham chiếu chưa được chạy thật trên Antigravity (gói thử ở `docs/vi/phat-trien/2026-09-27-video-ma-vi12-chay-thu-antigravity.md`). Nhân vật có thể lệch dáng giữa các cảnh; khi đó dùng `nhan-vat: nguoi-que`. Nền do AI vẽ và người que không phụ thuộc rủi ro này.
- Tách nền xanh chạy tốt với nền #00FF00 thuần; ảnh có bóng mềm dưới chân có thể còn vệt mờ. Công cụ báo đúng màu đo được và yêu cầu vẽ lại khi góc ảnh không sạch.
- Khổ dọc cắt dán dựng mất khoảng 2 lần thời lượng video (khổ ngang viết tay khoảng 1,3 lần) trên máy chủ repo; máy 2–3 lõi chậm hơn, có thể dùng `do-phan-giai: 720`.
- Các cảnh báo "hình khớp lời" chỉ bắt được ba trường hợp dễ thấy; hình có khớp lời hay không vẫn cần thầy cô xem bản xem trước.

## 6.3.2-vi.11 — 2026-09-26

Hiệu ứng giáo dục cho video giải thích: nhấn ý chính đúng lúc giọng đọc nói tới, số chạy, biểu đồ, sơ đồ tư duy, dòng thời gian, câu hỏi nhanh, năm kiểu chuyển cảnh, phụ đề karaoke, tiếng hiệu ứng tự tạo và nhạc nền giấy phép mở. Học ý tưởng từ HyperFrames (HeyGen, Apache 2.0) nhưng không nhúng thư viện nào: runtime vẫn là JS thuần, Python chỉ thư viện chuẩn cộng edge-tts và playwright.

### Thêm
- Mốc từng từ: giọng máy dùng `WordBoundary` của edge-tts; mốc câu tính từ từ đầu mỗi câu bằng cách so chữ của lời với chữ edge-tts trả về (số đọc thành nhiều từ, chữ viết tắt vẫn khớp). Không khớp được, hoặc dùng giọng thu sẵn, thì mốc được ước lượng theo tỉ lệ ký tự kèm đúng một cảnh báo cho cảnh đó. Sổ giọng `giong/canh-N.json` lưu thêm `tu`; sổ cũ vẫn dùng được.
- Nhấn ý chính ngay trong chữ: `==chữ==` tô vàng, `((chữ))` khoanh elip đỏ vẽ tay, `__chữ__` gạch chân. Cụm nổ khi giọng đọc tới từ đầu của cụm (không phân biệt hoa thường, giữ dấu thanh), không bao giờ trước khi cụm được viết xong; không có trong lời thì nổ 0,3 giây sau khi viết xong. Tối đa 3 cụm mỗi dòng, không lồng nhau; trong `bieu-thuc` các dấu này là chữ của công thức; `____` và `==`, `__` có khoảng trắng hai bên là chữ thường.
- Số chạy `{{số}}`: chạy từ 0 lên giá trị trong 0,8 giây khi bút viết tới; kịch bản dùng dấu chấm thập phân, trên hình hiện dấu phẩy, bề rộng giữ nguyên nên chữ không nhảy.
- Khoá đầu `chu-dong` (mặc định `co`): tiêu đề cảnh `tieu-de` nảy vào từng chữ cái, cụm nhấn nảy nhẹ khi nổ.
- Năm kiểu chuyển cảnh `lau-bang`, `lat-trang`, `truot`, `phong`, `mo-man` cho khoá `chuyen-canh`, thêm `luan-phien` (xoay vòng từ cảnh 2) và trường `chuyen:` ghi đè ở từng cảnh (không dùng ở cảnh 1).
- Bốn loại cảnh mới, tổng cộng 14: `bieu-do` (cột, đường, tròn; cột âm mọc xuống; thang số tròn 4–6 vạch; máy quay giữ toàn cảnh), `so-do` (2–6 nhánh vẽ tay quanh nút trung tâm), `dong-thoi-gian` (2–6 mốc, xen kẽ trên dưới từ 5 mốc) và `cau-hoi` (2–4 lựa chọn, đếm ngược `cho` 3–10 giây, mặc định 5, rồi khoanh đáp án và đọc `loi-giai` bằng giọng riêng `giong/canh-N-giai.mp3`). `cong-thuc` hiện từng phần khi tách `bieu-thuc` bằng ` | `.
- Phụ đề karaoke: `phu-de` thêm `karaoke` và đây là mặc định mới; file `.ass` tô vàng từng từ theo mốc từ, font Itim. Kịch bản ghi `phu-de: hinh` giữ kiểu cũ; `file` vẫn ra `phu-de.srt`.
- Tiếng hiệu ứng (khoá `am-thanh`, mặc định `co`): tiếng bút, "ting", chuyển cảnh, tích tắc, chuông đáp án, tiếng nhấn. Tạo bằng FFmpeg từ công thức cố định, không dùng file ngoài; thời điểm lấy từ chính runtime (`THI_VIDEO.suKien()`). Đỉnh hiệu ứng thấp hơn đỉnh giọng 20 dB, tiếng bút không quá 40% thời gian cảnh.
- Nhạc nền: khoá `nhac-nen: <file trong nhac/>` và `nguon-nhac:`; nhạc lặp đủ dài, vào ra dần 1,5 giây, nền −24 dB, tự hạ khi có giọng (`sidechaincompress`), dòng nguồn hiện 4 giây cuối video (cảnh cuối ngắn hơn 4 giây thì hiện suốt cảnh cuối). Thiếu nguồn, thiếu file, sai định dạng hay hỏng là lỗi `canh` nêu dòng khoá đầu.
- `tools/vi/tim_nhac.py "<từ khoá>" -o projects\_video\<tên>\nhac`: tìm trên Openverse, chỉ bản CC0 hoặc CC BY, mp3, dài từ 60 giây, chỉ tải qua https, không ghi đè, ghi nguồn vào `nhac/nguon.json`; một dòng JSON, lỗi mạng là `error.step: "mang"`.
- Tài liệu: `docs/vi/tro-ly/video-giai-thich.md` (câu hỏi gộp, vẫn 7 câu; ví dụ thứ ba có đủ hiệu ứng), `docs/vi/tro-ly/canh-video.md` (cú pháp nhấn và số, chuyển cảnh, bốn loại cảnh mới), mục "Hiệu ứng giúp học sinh nhớ bài" cho thầy cô, `AGENTS.vi.md` mục 15 (bước tìm nhạc, nhắc nghe thử), luật Antigravity, mục "Tìm nhạc nền thất bại" trong Xử lý lỗi. Test lớp Việt đọc mọi kịch bản mẫu và mọi cảnh mẫu bằng bộ đọc thật.
- Demo con lắc đơn 11 cảnh, giọng edge-tts thật, nhạc CC BY: 155,93 giây, 12,1 MB, dựng lần đầu 335 giây kể cả tạo giọng, dựng lại 172 giây. Chi tiết ở `docs/vi/phat-trien/2026-09-26-video-ma-hieu-ung-kiem-thu.md`.

### Sửa
- Kịch bản gõ bằng Unikey kiểu "Unicode tổ hợp" (hoặc dán từ Mac, PDF) có chữ dạng NFD: cụm nhấn không tìm thấy lúc giọng đọc tới, mốc câu và karaoke rơi về ước lượng. Nay `video.md` được chuẩn hoá về NFC một lần khi đọc, và khoá so khớp chữ (một hàm dùng chung cho mốc câu, karaoke, nhấn ý) cũng tự chuẩn hoá NFC.
- Phụ đề karaoke: dấu gạch ngược trong chữ (`a\Nb`, `\h`) hiện thành ⧵, không còn bị libass hiểu thành xuống dòng hay khoảng trắng cứng.
- Phụ đề `hinh` và `file` bỏ đủ mọi dấu đánh dấu (`==`, `((`, `))`, `__`, `{{`, `}}` cùng `**`, `~`, `^`), không còn hiện dấu thô.
- Tiếng hiệu ứng luôn thấp hơn đỉnh giọng 20 dB kể cả khi giọng thu rất nhỏ (trước đây mức hiệu ứng bị chặn dưới ở −50 dBFS, giọng −45 dBFS chỉ còn cách 5 dB); cảnh im lặng dùng sàn −80 dBFS.
- Lỗi nhạc nền và dòng nguồn nhạc tràn khung có cách sửa riêng (sửa `nhac-nen`, `nguon-nhac`, `nhac/nguon.json`), không còn gợi ý "rút gọn nội dung cảnh". Mỗi lượt dựng chỉ đo nhạc nền bằng ffprobe một lần.

### Bảo mật
- `tim_nhac.py` chỉ tải qua https (kể cả khi máy chủ chuyển hướng: địa chỉ cuối không phải https thì dừng, không đọc nội dung), từ chối file không phải mp3 hoặc lớn hơn 40 MB. `nhac-nen` không thoát được khỏi thư mục `nhac/`; nguồn nhạc bỏ mọi địa chỉ web.

### Ngoài phạm vi
- Kiểu Vox và khổ dọc 9:16 lùi sang vi.12. Không có bản đồ, 3D, hạt, shader, tự chọn nhạc theo cảm xúc hay ghép video quay thật.

### Rủi ro
- Chưa kiểm: phiên Antigravity thật với luật mới, cài từ đầu trên máy sạch, thời gian dựng trên máy 2 lõi, và chủ repo chưa nghe thử tiếng hiệu ứng và nhạc nền của demo.
- Tiếng hiệu ứng tự tạo có thể nghe "máy"; tắt bằng `am-thanh: khong`.
- Với giọng thu sẵn, nhấn ý và karaoke khớp theo ước lượng, có thể lệch vài trăm mili giây.
- Dự án đã dựng bằng vi.10 có sổ giọng `giong/*.json` chưa có mốc từng từ, nên nhấn ý và karaoke dùng mốc ước lượng cho tới khi xoá các file `giong/*.json` đó; lần dựng sau giọng máy được tạo lại một lần.
- Công cụ chỉ kiểm đáp án của `cau-hoi` là một trong các lựa chọn; tính đúng của câu hỏi do thầy cô duyệt.

## 6.3.2-vi.10 — 2026-09-26

Sửa lỗi font tiếng Việt trong video giải thích và làm video trực quan hơn: hình vẽ nét, ảnh thật, bàn tay cầm bút, lau bảng, máy quay động.

### Sửa
- Chữ tiếng Việt trong video vi.9 bị trộn hai kiểu nét ("Chiều" có "ều" khác nét). Nguyên nhân: Segoe Print thiếu 92 chữ tiếng Việt dựng sẵn (Ink Free thiếu 80, Comic Sans thiếu 92), Chromium lấy từng chữ thiếu từ font khác; phép thử font của vi.9 dùng `document.fonts.check`, hàm này không kiểm độ phủ chữ nên đã nhận sai. Nay đóng gói font Itim (SIL OFL 1.1, kèm `OFL.txt`) trong `tools/vi/video_ma_parts/runtime/fonts/`, nhúng vào trang cảnh, dùng cho cả phụ đề in lên hình và chữ trên canvas thí nghiệm. Có test đọc bảng `cmap` (đủ 134 chữ có dấu) và test Chromium đo độ rộng từng chữ (không chữ nào rơi sang font dự phòng).
- Nghe video trên loa Bluetooth, tai nghe hoặc loa HDMI bị mất âm đầu mỗi câu. Nguyên nhân: giọng máy chèn khoảng 1 giây im lặng tuyệt đối giữa các câu, và nhiều thiết bị tự tắt khi gặp im lặng tuyệt đối, bật lại chậm 0,1–0,2 giây. Nay đường tiếng được trộn một lớp nhiễu hồng rất nhỏ (đỉnh khoảng −57 dBFS, tai gần như không nghe thấy) nên không còn đoạn im lặng tuyệt đối nào; có test dựng tiếng thật bằng FFmpeg để kiểm.

### Thêm
- Hình vẽ nét: trường `hinh:` ở cảnh `tieu-de`, `khai-niem`, `cong-thuc`, `y-tung-y` và loại cảnh mới `minh-hoa` (1–3 hình có nhãn). Hình lấy từ 5.138 biểu tượng `tabler-outline` có sẵn, vẽ dần từng nét, không cần mạng. Tên sai báo lỗi `canh`, nhắc tên là tiếng Anh, chỉ tới bảng tra và gợi ý tối đa 5 tên: tên tiếng Việt ("nam châm") được đối chiếu với bảng tra trước (gợi ý `magnet`), không bao giờ gợi ý biểu tượng thương hiệu `brand-*`; `canh-video.md` có bảng tra 161 khái niệm tiếng Việt theo môn.
- Ảnh thật: loại cảnh mới `anh` và trường `anh:` ở bốn loại cảnh trên. AI tải ảnh có giấy phép mở bằng `image_search.py` vào `anh/`; công cụ dựng không tự lên mạng. Ảnh vừa khung không méo, phóng hoặc lướt chậm suốt cảnh, luôn có dòng nguồn (từ `anh/image_sources.json`, bỏ mọi địa chỉ web, hoặc từ `nguon:`, ghi được ở mọi cảnh có `anh:`); thiếu nguồn, quá 8 MB hay `image_sources.json` sai cấu trúc là lỗi `canh`. Dòng nguồn nằm theo bố cục: trong góc khung ở cảnh `anh`, dưới khung trong bề rộng cột ở cột phải, bên phải khung ở cảnh tiêu đề; không bao giờ đè lên chữ và luôn trên vùng phụ đề. Ảnh điện thoại chụp dọc (thẻ Exif Orientation) có khung đúng chiều. Có ảnh thật thì AI bắt buộc chạy `--xem-truoc` và cho thầy cô xem ảnh trước khi dựng.
- Bàn tay cầm bút (SVG do repo tự vẽ) đi theo nét đang vẽ và chữ đang viết, nghỉ ở góc khi không vẽ.
- Lau bảng: 0,5 giây đầu mỗi cảnh từ cảnh 2, bàn tay cầm giẻ xoá khung cuối của cảnh trước. Dẫn đầu mỗi cảnh tăng từ 0,7 lên 1,0 giây.
- Máy quay: phóng vào phần đang nói (tối đa 1,35 lần), lia sang phần kế, thu về toàn cảnh trong 1,2 giây cuối cảnh; phần đang vẽ luôn nằm trên vạch phụ đề. Cảnh thí nghiệm không có tay, máy quay chỉ đẩy chậm lên 1,06 lần.
- Khoá đầu mới, đều tuỳ chọn và mặc định bật: `ban-tay`, `may-quay`, `chuyen-canh`. Kịch bản vi.9 dựng được không phải sửa.
- Chụp 30 khung/giây (trước là 15) bằng nhiều tiến trình Chromium song song (`min(4, số lõi // 2)`, tối thiểu 1). Máy 6 lõi: video 5 phút dựng khoảng 7,1–7,6 phút; một tiến trình khoảng 10,6 phút. Một tiến trình hỏng thì các dải chưa chạy bị huỷ; Chromium không mở được trong tiến trình con vẫn báo đúng lỗi `chromium`.
- Demo con lắc đơn 10 cảnh, giọng edge-tts thật: 104,3 giây, 8,55 MB, dựng trong 186 giây. Chi tiết ở `docs/vi/phat-trien/2026-09-25-video-ma-hinh-anh-kiem-thu.md`.

### Bảo mật
- Giá trị `hinh:` và `anh:` không còn thoát được khỏi thư mục biểu tượng hay `anh/` bằng `..`, dấu gạch chéo hay tên ổ đĩa.
- Thuộc tính SVG có namespace và thuộc tính `on…` bị bỏ khi vẽ biểu tượng.

### Ngoài phạm vi
- Kiểu Vox và khổ dọc 9:16 lùi sang vi.11. Không có nhạc nền, biểu tượng tô màu, video AI sinh hay tự tìm ảnh bên trong công cụ dựng.

### Rủi ro
- Chưa kiểm: cài Chromium từ đầu trên máy sạch, phiên Antigravity thật với luật mới, thời gian dựng trên máy 2 lõi (ước khoảng 11 phút; câu "khoảng 7 phút" trong spec mục 10 đã được đính chính trong tài liệu).
- Ảnh tải về có thể sai nội dung hoặc nặng quá 8 MB (demo gặp ảnh 8,7 MB); tài liệu cho AI ghi cách dùng bản thu nhỏ trong `anh/.review/`.
- Máy quay khá năng động; tiêu đề cảnh vẫn tự hiện dần trong lúc tay viết mục đầu. Chủ repo cần xem demo để quyết có chỉnh ở bản sau.

## 6.3.2-vi.9 — 2026-09-25

Thêm loại việc thứ 10 cho AI: video giải thích dựng bằng mã (viết tay, không dùng video AI sinh).

### Thêm
- `tools/vi/video_ma.py` và các module trong `tools/vi/video_ma_parts/`: đọc kịch bản cảnh, dựng ra video MP4 1280×720, 30 khung/giây, có tiếng, phụ đề in lên hình hoặc file `.srt` rời.
- Tám loại cảnh: tiêu đề, khái niệm, công thức, ý từng ý, quy trình, so sánh, đồ thị, thí nghiệm. Cảnh thí nghiệm chạy trực tiếp một trong tám mô hình thí nghiệm ảo đã kiểm bằng số (`thi_nghiem_parts/`), tham số nội suy theo thời gian nên đối tượng (ví dụ con lắc) chuyển động thật trong video, không phải ảnh tĩnh.
- Thuyết minh: dùng giọng edge-tts (`vi-VN-HoaiMyNeural`, `vi-VN-NamMinhNeural`) hoặc file mp3 thầy cô tự cung cấp cho từng cảnh; file mp3 có sẵn không bao giờ bị ghi đè.
- Mỗi khung được chụp bằng Chromium headless ở 15 khung/giây rồi ghép ra 30 khung/giây bằng FFmpeg; văn bản xuất hiện dần theo mốc câu trong lời thuyết minh, không hiện hết ngay từ đầu cảnh.
- Dựng thật một video mẫu (bài Con lắc đơn, 8 cảnh, thuyết minh tổng hợp): 74,667 giây, 1,97 MB, dựng trong 99 giây; `ffprobe` xác nhận h264 1280×720 30 khung/giây kèm luồng tiếng aac mono. Ba lỗi thật gặp khi dựng đã sửa: đường gạch chân tiêu đề lệch khỏi chữ, phụ đề in đè lên nội dung cảnh, đường dẫn thư mục tương đối làm FFmpeg không tìm thấy file tiếng. Chi tiết ở `docs/vi/phat-trien/2026-09-25-video-ma-kiem-thu.md`.

### Yêu cầu
- Cần Chromium của Playwright (tải một lần qua `pptmaster.ps1 -Action tool -Name chromium`, khoảng 150–300 MB) và FFmpeg đã có sẵn từ trước.
- Cần mạng khi dùng giọng máy edge-tts; không cần mạng nếu dùng file mp3 thầy cô tự cung cấp.

### Ngoài phạm vi
- Không dựng video AI sinh cảnh (kiểu Veo/Sora); mọi khung hình do mã vẽ ra.
- Không hỗ trợ khổ dọc (9:16) hay các nền tảng như TikTok/Reels; canvas cố định 1280×720.
- Không tạo giọng đọc kiểu lồng tiếng nhân vật (Vox) hay nhiều giọng chồng nhau trong một cảnh.

### Rủi ro
- Giọng edge-tts thật (gọi qua mạng bên trong một lần chạy đầy đủ), cài Chromium từ đầu trên máy sạch, và chạy trong Antigravity thật đều **chưa được kiểm** trong biên bản nghiệm thu này; chủ repo cần tự thử trước khi coi là ổn định.
- Thí nghiệm ảo vẫn là mô hình lí tưởng hoá đã ghi ở `6.3.2-vi.8`; dùng lại nguyên trạng trong cảnh thí nghiệm, không đổi.
- Vài chỗ thẩm mỹ còn để lại, không chặn phát hành: ô quy trình trống khi chữ ngắn, cảnh công thức không có tiêu đề nên đỉnh khung trống, phụ đề hơi sít chữ, con lắc nhỏ khi dây ngắn.

## 6.3.2-vi.8 — 2026-09-21

Thêm thí nghiệm ảo cho Toán, Vật lí, Hoá học: một file HTML tương tác chạy không cần mạng, kèm phiếu học tập Word, dựng từ 8 mô hình đã kiểm bằng số.

### Thêm
- `tools/vi/thi_nghiem.py`: đọc `thi-nghiem.md`, kiểm với khai báo mô hình, ghép ra `thi-nghiem.html`, `phieu-hoc-tap.docx` và `can-soat.md`. Đúng một dòng JSON ở stdout, `error.step` là `input`, `parse`, `model`, `check`, `docx`, `write` hoặc `internal`.
- 8 mô hình trong thư viện: ném xiên, con lắc đơn, đoạn mạch nối tiếp – song song (Vật lí); chuẩn độ acid – base, cân bằng N₂O₄ ⇌ 2NO₂, tốc độ phản ứng (Hoá học); khảo sát hàm số, xác suất thực nghiệm (Toán). Mỗi mô hình được kiểm ba lớp: bản tính lại độc lập bằng Python trong repo, kiểm số qua Node trên máy thầy cô nếu có, và tự kiểm ngay trong trang mỗi lần mở (hiện dải đỏ nếu trượt).
- Khung Dự đoán – Quan sát – Giải thích: học sinh phải chốt dự đoán mới thao tác được, ghi đủ số lần đo mới mở mục Giải thích; có bảng số liệu, đồ thị vẽ từ chính số liệu kèm đường khớp tuyến tính, nút chép số liệu sang Excel, và công tắc bật sai số đo để tập xử lí số liệu. Nút "Chế độ giáo viên" bỏ mọi khoá.
- Phiếu học tập Word: trang học sinh (câu dự đoán, bảng trống, lưới vẽ đồ thị) và trang giáo viên riêng (đáp án, bảng số liệu lí tưởng, công thức, điều kiện áp dụng).
- Mô hình ngoài danh mục do AI viết (`mau: moi`): bắt buộc có công thức, điều kiện áp dụng và bảng số kiểm; `can-soat.md` luôn nhắc thầy cô soát công thức và tính lại bằng máy tính cầm tay trước khi dùng trên lớp.
- Loại việc thứ 9 cho AI: `docs/vi/tro-ly/thi-nghiem-ao.md` (câu hỏi, ngữ pháp `thi-nghiem.md`) và `docs/vi/tro-ly/mo-hinh-thi-nghiem.md` (danh mục mẫu, khuôn mô hình mới); `AGENTS.vi.md` mục 14; nội dung được ghi thẳng vào `.agents/rules/ppt-master-vi.md` để Antigravity nhận được (bài học từ vi.7: Antigravity không chép nội dung file nhắc bằng `@`).
- Tài liệu `docs/vi/thi-nghiem-ao.md` cho thầy cô và mục "Tạo thí nghiệm ảo thất bại" trong Xử lý lỗi.

### Không thay đổi
- Lõi PPT Master v6.3.2 của Hugo He giữ nguyên. Không thêm thư viện Python hay JavaScript nào ngoài `python-docx` đã dùng từ trước; khung chạy và mô hình là JavaScript thuần. Node chỉ cần cho lớp kiểm số thứ hai, không bắt buộc để dùng file HTML.

### Rủi ro
- Thí nghiệm ảo là mô hình lí tưởng hoá, không thay thí nghiệm thật; mỗi trang luôn ghi rõ điều kiện lí tưởng hoá.
- Mô hình do AI viết mới chỉ được bảo vệ bằng bảng số kiểm do chính AI tự tính; bảng đó chỉ bắt được lỗi lập trình, không bắt được lỗi hiểu sai kiến thức, nên lời nhắc thầy cô soát là bắt buộc, không tắt được.
- Học sinh dùng điện thoại không mở được file từ USB; thầy cô cần đưa file lên một trang web tĩnh trước.
- Máy thầy cô không có Node thì bỏ qua lớp kiểm số thứ hai, chỉ còn lớp tự kiểm ngay trong trang.
- Chủ repo đã soát và xác nhận ba mẫu Hoá học (hằng số, nguồn) trước khi phát hành; chưa tự mở phiếu Word bằng giao diện Word thật, thay bằng kiểm cấu trúc file bằng `python-docx` trong buổi kiểm thử.

## 6.3.2-vi.7 — 2026-09-17

Sửa phản ánh của thầy cô: AI không hỏi trước khi làm, slide toàn chữ, ít hiệu ứng, không có hình ảnh.

### Sửa
- AI trong Antigravity không hỏi thầy cô trước khi làm. Nguyên nhân: Antigravity không chép nội dung file nhắc bằng `@` vào luật, nên quy tắc hỏi trong `AGENTS.vi.md` chưa từng tới được AI. File luật `.agents/rules/ppt-master-vi.md` giờ ghi thẳng bước hỏi (đọc hướng dẫn → gửi một tin nhắn hỏi → dừng chờ trả lời), bảng 8 loại việc, quy tắc ảnh và quy tắc hiệu ứng, dưới giới hạn 12.000 ký tự của Antigravity. Turbo Mode hay Always Proceed không còn bị hiểu là "tạo nhanh".
- Slide toàn chữ: mục mới "Ảnh minh hoạ" trong `docs/vi/tro-ly/quy-trinh-hoi.md`. Sự vật, chất, dụng cụ thí nghiệm, địa danh có thật được lên kế hoạch tìm ảnh thật ngay từ đầu bằng `image_search.py` (Openverse, Wikimedia, không cần khoá API); quá trình, cấu tạo, sơ đồ thí nghiệm được vẽ thành sơ đồ; sự kiện riêng của trường dùng ảnh thầy cô gửi. Thiếu khoá tạo ảnh AI không còn là lý do bỏ ảnh.
- `trich-sgk` cắt bài cuối cùng của SGK không có tiêu đề `#` nhưng có mục lục: không còn lấy cả phần từ mục lục tới hết sách.

### Thêm
- Câu hỏi mức hiệu ứng (không, vừa, nhiều) trong bài giảng, báo cáo, hoạt động Đoàn và tập huấn; tạo nhanh mặc định mức vừa. Video bài giảng hỏi giữ hay bỏ hiệu ứng của bài.
- `docs/vi/tro-ly/hieu-ung-lop-hoc.md`: định nghĩa ba mức và cách làm bốn kiểu hiệu ứng bằng cơ chế sẵn có của dự án gốc: hiện từng ý khi bấm, bấm để hiện đáp án, Morph cho diễn biến thí nghiệm, chuyển trang nổi bật giữa các hoạt động.
- `tools/vi/kiem_hieu_ung.py`: đọc file PPTX đã xuất, đếm trang có hiệu ứng, bước bấm, trang Morph, ô bấm hiện đáp án và kiểu chuyển trang; chặn bài không đạt mức đã chọn (mức vừa từ 30% trang nội dung, mức nhiều từ 50%), cảnh báo câu trắc nghiệm chưa có cách hiện đáp án. `--video` chặn hiệu ứng chờ bấm trong bản có thuyết minh.
- Làm video từ bài có hiệu ứng bấm: AI tạo bản `animations_video.json` đổi hiệu ứng sang tự chạy, xuất bản thuyết minh bằng bản đó và kiểm trước khi dựng; bản trình chiếu trên lớp vẫn giữ hiệu ứng bấm.
- Mục "Kiểm hiệu ứng không đạt" trong Xử lý lỗi.

### Không thay đổi
- Lõi PPT Master v6.3.2 của Hugo He giữ nguyên. Hiệu ứng vẫn do `animations.json` và bước `customize-animations` của dự án gốc tạo ra; lớp Việt chỉ quyết định mức và kiểm kết quả.

### Rủi ro
- Chưa chạy thử trong Antigravity sau khi sửa: bằng chứng hiện có là nhật ký phiên cũ (luật tiếng Việt không được nạp) và test khoá nội dung file luật. Cần mở cuộc trò chuyện mới trong Antigravity để xác nhận AI hỏi trước.
- Luật cho Cursor (`.cursor/rules/`) vẫn chỉ trỏ tới `AGENTS.vi.md`; chưa kiểm được Cursor có chép nội dung file đó vào hay không.
- Công thức thẻ lật của dự án gốc đặt mặt trước và mặt sau chồng nhau, nhưng bộ kiểm SVG của dự án gốc chặn hai nhóm chồng nhau. Bản Việt dùng nút và ô đáp án đặt cạnh nhau.
- Bài có sẵn mà các hình nằm rời, không gom nhóm (ví dụ bài Sulfur mẫu), phải gom nhóm lại trước khi làm hiện từng ý.
- Tỉ lệ 30% và 50% là mức sàn để bắt lỗi quên làm hiệu ứng; AI được dặn không thêm chuyển động chỉ để đủ tỉ lệ, nhưng model yếu vẫn có thể làm vậy.

## 6.3.2-vi.6 — 2026-09-13

Soạn giáo án tích hợp năng lực số và năng lực AI: từ giáo án cũ (Word hoặc PDF) hoặc chỉ từ tên bài, ra file Word Kế hoạch bài dạy theo Công văn 5512, cho mọi môn.

### Thêm
- `tools/vi/giao_an.py xuat`: đọc `giao-an.md`, kiểm cấu trúc 5512 và mã năng lực, dựng `giao-an.docx` (A4 dọc, lề 2/2/2,5/2 cm, Times New Roman 14pt, giãn dòng 1,3; phiếu học tập căn trái; rubric dạng bảng) và `can-soat.md` (ghi chú nội bộ, không nằm trong giáo án). `--plan-only` chỉ kiểm. Kết quả trả về dạng JSON cho AI đọc.
- Công cụ chặn giáo án thiếu mục tiêu, nội dung, sản phẩm hoặc bốn bước tổ chức của một hoạt động; chặn giáo án chỉ nhắc năng lực số hay AI ở mục tiêu mà tiến trình không có; chặn mã năng lực không đúng bảng; chặn rubric thiếu mức. Lỗi cấu trúc nêu đúng dòng cần sửa.
- `tools/vi/giao_an.py trich-sgk`: cắt đúng phần một bài ra khỏi SGK đã chuyển sang Markdown, để AI không phải nạp cả quyển; không bao giờ ghi đè file SGK nguồn.
- Khung năng lực số (11 mã của Bộ GD&ĐT) và khung năng lực AI môn Hoá học (lớp 10, 11, 12, hệ chuyên) trong `docs/vi/tro-ly/nang-luc-so-va-ai.md`, do Lương Hải Anh — 2Anh AI Education biên soạn; đây là nguồn mã duy nhất của công cụ. Môn chưa có khung AI thì ô mã ghi "(chưa có khung mã cho môn này)", AI không tự đặt mã.
- Loại việc thứ 8 cho AI: `docs/vi/tro-ly/giao-an.md`; `AGENTS.vi.md` mục 13. Câu lệnh chỉ nói "giáo án" thì AI hỏi lại cần file Word hay slide; "kế hoạch bài dạy", "KHBD" đi thẳng vào loại việc này. Giáo án cũ được đọc trước khi hỏi, nội dung chuyên môn của thầy cô được giữ nguyên; file phân phối chương trình chỉ được đọc, không sửa.
- Tài liệu `docs/vi/soan-giao-an.md` và mục "Xuất giáo án thất bại" trong Xử lý lỗi.

### Không thay đổi
- Lõi PPT Master v6.3.2 của Hugo He giữ nguyên. Soạn giáo án không tạo dự án PPTX và không dùng bước xác nhận của dự án gốc. Dùng lại thư viện `python-docx` và tầng dựng Word của bản 6.3.2-vi.5.

### Rủi ro
- `trich-sgk` với SGK chuyển ra toàn dòng thường (không có tiêu đề `#`) và có mục lục: cắt bài **cuối cùng** của sách sẽ lấy cả phần từ mục lục tới hết sách (chỉ có cảnh báo lớn hơn 200 KB). Các bài khác và sách có tiêu đề `#` không bị. Sẽ sửa ở bản sau.
- Khung mã AI mới chỉ có môn Hoá học; khung hệ chuyên có một mã, thiên về hữu cơ và phổ, nên có thể không hợp một số bài vô cơ. Môn khác dùng được nhưng ô mã AI để trống, hồ sơ có thể bị tổ chuyên môn hỏi lại.
- Công cụ kiểm cấu trúc và mã, không kiểm chất lượng sư phạm. Chưa có khung ký duyệt và quốc hiệu.
- Chủ repo chưa mở file Word để nghiệm thu bằng mắt. Bằng chứng hiện có: chạy thật trên một giáo án Bài 5 thật (giữ đủ 5 hoạt động, 90 phút), một giáo án tự soạn và một giáo án Ngữ văn, kiểm tra cấu trúc file bằng test.
- Giáo án có bảng lồng nhau hoặc công thức dạng ảnh có thể mất định dạng khi chuyển sang Markdown; AI phải ghi chỗ không đọc được vào "Cần thầy cô soát".

## 6.3.2-vi.5 — 2026-09-13

Soạn đề kiểm tra KHTN bằng tiếng Anh: chuyển đề tiếng Việt có sẵn hoặc soạn đề mới, dùng thuật ngữ khoa học đúng môn thay vì dịch từng chữ, xuất file Word đúng thể thức đề thi.

### Thêm
- `tools/vi/de_thi.py`: đọc `de.md` rồi dựng ba file Word `de-en.docx` (đề tiếng Anh), `de-song-ngu.docx` (song ngữ Anh – Việt) và `dap-an.docx` (đáp án, thang điểm, ma trận đặc tả, mục "Cần thầy cô soát"). `--phan de,dap-an` bỏ bản song ngữ; `--plan-only` chỉ kiểm cú pháp. Kết quả trả về dạng JSON cho AI đọc.
- Cấu trúc đề theo định dạng hiện hành: Phần I trắc nghiệm nhiều lựa chọn (0,25 điểm/câu), Phần II đúng/sai (1 điểm/câu), Phần III trả lời ngắn (0,25 điểm/câu); áp dụng cho KHTN THCS 6–9 và Vật lí, Hoá học, Sinh học THPT 10–12. Khổ A4, Times New Roman, đáp án ngắn tự xếp 4 cột, có số trang.
- Loại việc thứ 7 cho AI: `docs/vi/tro-ly/de-khtn-tieng-anh.md` (ngữ pháp `de.md` và đề mẫu) và `docs/vi/tro-ly/tieng-anh-khoa-hoc.md` (quy ước thuật ngữ, đơn vị, ký hiệu, cách gọi tên chất); `AGENTS.vi.md` mục 12 nêu thứ tự làm cho hai luồng.
- Thư viện `python-docx` (`tools/vi/requirements-vi.txt`) được cài cùng bộ công cụ ở mức khuyến nghị: cài hỏng thì chỉ cảnh báo, máy vẫn làm PPTX bình thường. `doctor.py` có thêm mục "Thư viện lớp Việt".
- Tài liệu `docs/vi/soan-de-tieng-anh.md` và mục "Xuất đề Word thất bại" trong Xử lý lỗi.

### Sửa
- `tools/vi/video.py` ghi JSON bằng UTF-8 khi console Windows dùng bảng mã cũ (commit sau tag 6.3.2-vi.4, nay mới vào bản phát hành).

### Không thay đổi
- Lõi PPT Master v6.3.2 của Hugo He giữ nguyên. Soạn đề không tạo dự án PPTX và không dùng bước xác nhận của dự án gốc.

### Rủi ro
- Chủ repo chưa mở các file Word mẫu để nghiệm thu bằng mắt (viền bảng, số trang). Bằng chứng hiện có là hai lần dựng thật (Vật lí 10, KHTN 8) và kiểm tra cấu trúc file bằng test.
- Đáp án Phần III chỉ nhận số (ví dụ `36`, `12,5`, `-0.25`); câu cần đáp án bằng chữ phải chuyển sang Phần I hoặc II.
- Chất lượng tiếng Anh phụ thuộc AI; công cụ không có từ điển hay bộ kiểm thuật ngữ. Thầy cô cần đọc lại đề, nhất là các mục trong "Cần thầy cô soát".
- Máy cài hỏng `python-docx` sẽ báo sẵn sàng kèm cảnh báo; lần soạn đề đầu tiên báo lỗi `docx` kèm lệnh cài. Chế độ `-Auto` của bộ cài sẽ thử cài lại thư viện này mỗi lần chạy.
- `video.py` vẫn có thể in hai dòng JSON trong trường hợp hiếm stdout bị lỗi khi đang ghi.

## 6.3.2-vi.4 — 2026-09-12

Làm video bài giảng: bài giảng đã có thành video MP4 có lời giảng tiếng Việt và phụ đề, chạy được cả khi máy không có PowerPoint.

### Thêm
- `tools/vi/video.py`: một lệnh để dựng video, tự chọn đường PowerPoint (giữ hiệu ứng chuyển cảnh) hoặc đường FFmpeg ghép ảnh slide (không cần PowerPoint). Kết quả trả về dạng JSON cho AI đọc.
- Phụ đề `.srt` dựng từ phụ đề từng slide: đường FFmpeg cộng dồn thời lượng tiếng, đường PowerPoint đọc mốc thời gian trong bản PPTX đã gắn tiếng. Thầy cô chọn để file rời hoặc in lên hình.
- `-Action tool -Name chromium` cài Chromium khi cần chụp ảnh slide, và chỉ khi thật sự cần chụp.
- Loại việc thứ 6 cho AI: `docs/vi/tro-ly/video-bai-giang.md` (4 câu hỏi: giọng đọc, tốc độ, phụ đề, độ phân giải); `AGENTS.vi.md` mục 11 nêu thứ tự làm và cách chuyển câu trả lời thành tham số.
- Tài liệu `docs/vi/lam-video.md` và mục "Dựng video thất bại" trong Xử lý lỗi, viết theo từng mã lỗi.

### Không thay đổi
- Lõi PPT Master v6.3.2 của Hugo He giữ nguyên. Tiếng đọc vẫn do `edge-tts` của dự án gốc tạo, giọng `vi-VN-HoaiMyNeural` và `vi-VN-NamMinhNeural`.

### Rủi ro
- Đường FFmpeg xuất video đúng bằng kích thước ảnh slide (1280×720 với khổ 16:9), không kéo giãn lên 1080. Cần 1080 thật thì chờ bản sau.
- Đường PowerPoint mở cửa sổ PowerPoint và chiếm máy vài phút. Bài dài khoảng 15 slide trở lên sẽ hiện cảnh báo phụ đề lệch chừng 1 giây, do PowerPoint tự thêm khoảng đệm mỗi slide; cần phụ đề chính xác thì dùng đường FFmpeg.
- Chủ repo chưa nghiệm thu trên một bài giảng thật của mình. Bằng chứng hiện có là một lần dựng thật trên dự án mẫu 3 slide, cả hai đường đều ra video xem được.
- Video 10 phút nặng khoảng 100–300 MB; ổ đĩa nên còn trống ít nhất 2 GB. Tiếng máy đọc có thể sai tên riêng nước ngoài và công thức, nên nghe lại trước khi giao cho học sinh.

## 6.3.2-vi.3 — 2026-09-12

AI tự cài đặt: thầy cô chỉ cần dán link repo vào Antigravity (hoặc mở thư mục đã tải), AI tự kiểm tra máy, cài những gì còn thiếu rồi báo khi sẵn sàng tạo slide.

### Thêm
- `tools/vi/pptmaster.ps1 -Action setup -Auto`: cài Python 3.12 cho riêng tài khoản (không cần quyền quản trị), tạo môi trường Python riêng `venv\`, cài thư viện, tạo `.env`, kiểm tra có xuất thử PPTX, trả kết quả JSON cho AI.
- `-Action tool -Name ffmpeg|pandoc`: chỉ cài FFmpeg hoặc Pandoc khi cần.
- `tools/vi/doctor.py --json`.
- Hướng dẫn cài cho AI `docs/vi/cai-dat-bang-ai.md`; `AGENTS.vi.md` mục 9 cho AI tự kiểm tra môi trường trước lệnh Python đầu tiên của repo trong mỗi cuộc trò chuyện.
- Tài liệu: mục "Để AI tự cài" trong Bắt đầu nhanh, mục "Máy trường chặn cài đặt" kèm đoạn gửi bộ phận IT.

### Không thay đổi
- `CAI-DAT.bat`, `KIEM-TRA.bat`, `CAP-NHAT.bat` vẫn dùng như cũ (cả ba ưu tiên `venv` nếu có).
- Lõi PPT Master v6.3.2 của Hugo He giữ nguyên.

### Rủi ro
- Thư mục bộ công cụ ở đường dẫn dài (khoảng 150 ký tự) có thể làm cài thư viện lỗi vì giới hạn đường dẫn của Windows. Bộ cài cảnh báo khi đường dẫn dài hơn 80 ký tự; nên đặt bộ công cụ ở `D:\PPTmaster`.
- Bộ cài dùng Python 3.10 trở lên có sẵn trên máy, kể cả bản mới hơn 3.12 có thể chưa có gói build sẵn cho vài thư viện; khi đó lỗi hiện ở bước cài thư viện. Máy có Python 3.12 cài cho mọi người dùng nhưng không có trong PATH hay `py` có thể không được nhận ra.
- Bước AI tự cài Python (winget hoặc bộ cài python.org) chưa được chạy thật trên một máy chưa có Python. Nếu bước này lỗi, cài Python theo [Cài đặt trên Windows](docs/vi/cai-dat-windows.md) rồi chạy lại.

## 6.3.2-vi.2 — 2026-09-11

Thêm trợ lý hỏi đáp cho thầy cô: AI hỏi một lượt ngắn trước khi tạo slide.

### Thêm
- Bộ hướng dẫn cho AI trong `docs/vi/tro-ly/`: quy trình hỏi chung và 5 loại việc (bài giảng, báo cáo – tổng kết, hoạt động Đoàn – sự kiện, poster Zalo – Facebook, tập huấn/workshop).
- Hồ sơ đơn vị lưu một lần ở `projects/_ho-so-don-vi.md` (không đưa lên GitHub); câu trả lời của thầy cô được ghi thành brief trong thư mục nguồn của dự án.
- "tạo nhanh" chỉ hỏi 2–3 câu thật cần thiết; "không cần hỏi lại" thì không hỏi câu nào.
- Bước xác nhận có thể làm ngay trong khung chat, không cần mở trang web.
- `AGENTS.vi.md` mục 10 trỏ AI tới bộ hướng dẫn; tài liệu người dùng giải thích lượt hỏi.

### Không thay đổi
- Lõi PPT Master v6.3.2 của Hugo He giữ nguyên; bước xác nhận của dự án gốc vẫn áp dụng.

## 6.3.2-vi.1 — 2026-09-11

Chuyển sang nền PPT Master **v6.3.2** của Hugo He và đóng gói lại cho người dùng Việt Nam.

### Thêm
- Ghi công dự án gốc trong `NOTICE` và `README.md`.
- Bộ cài một lần bấm cho Windows: `CAI-DAT.bat`, `KIEM-TRA.bat`, `CAP-NHAT.bat`; `tools/vi/setup.sh` cho macOS/Linux.
- Kiểm tra môi trường `tools/vi/doctor.py`, có xuất thử một file PPTX tiếng Việt.
- Quy tắc tiếng Việt cho AI editor: `AGENTS.vi.md`, tự nạp trong Claude Code, Cursor, Antigravity.
- Tài liệu tiếng Việt trong `docs/vi/`.

### Thay đổi so với bản cũ (v2.x)
- Toàn bộ lõi cập nhật lên v6.3.2: PPTX chỉnh sửa trực tiếp, hiệu ứng động, thuyết minh, làm đẹp PPTX có sẵn.
- Khổ Zalo/Facebook dùng tên key của dự án gốc (`moments`, `xiaohongshu`, `wechat`); bảng quy đổi nằm trong `AGENTS.vi.md`.

### Gỡ bỏ
- Thư mục `examples/`, `viewer.html`, `index.html` cũ. Bộ ví dụ xem tại https://github.com/hugohe3/ppt-master-examples.
- Trạng thái bản cũ vẫn giữ ở tag `v2-vi-legacy`.

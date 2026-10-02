# AGENTS.vi.md — Quy tắc bổ sung cho bản Việt

File này bổ sung ngữ cảnh Việt Nam cho [AGENTS.md](AGENTS.md). Nó không thay thế quy tắc nào của dự án gốc.

Tên sản phẩm với người dùng là **2Anh Studio** (trước đây là PPT Master bản Việt): khi giới thiệu bộ công cụ thì gọi tên này. Người dùng nhắc "PPT Master" là nói cùng bộ công cụ này. Lõi `skills/ppt-master/` vẫn là PPT Master của Hugo He và giữ nguyên tên, ghi công.

## 1. Thứ tự ưu tiên

- `skills/ppt-master/SKILL.md` và `AGENTS.md` luôn được ưu tiên khi có mâu thuẫn với file này.
- Không bao giờ sửa, bỏ qua hay tìm cách "sửa chữa" `skills/ppt-master/scripts/attribution_guard.py`. Nếu kiểm tra toàn vẹn thất bại, dừng lại và hướng dẫn người dùng tải lại bản đầy đủ.
- `tools/vi/` và `docs/vi/` là lớp Việt hoá của bản phân phối này; `tools/vi/tests/` là test riêng của lớp đó.

## 2. Ngôn ngữ

- Giữ quy tắc ngôn ngữ trong `SKILL.md`: trả lời theo ngôn ngữ người dùng đang dùng.
- Khi người dùng viết tiếng Việt và không yêu cầu ngôn ngữ khác, đặt ngôn ngữ nội dung của dự án (`primary_language`) là `vi`.

## 3. Câu lệnh tiếng Việt kích hoạt skill `ppt-master`

"tạo PPT", "làm slide", "làm bài giảng", "tạo bài thuyết trình", "làm poster", "làm báo cáo", "thêm thuyết minh", "làm đẹp slide", "làm video bài giảng", "lồng tiếng", "xuất video", "soạn đề", "làm đề kiểm tra", "đề tiếng Anh", "soạn giáo án", "kế hoạch bài dạy", "KHBD", "thí nghiệm ảo", "mô phỏng thí nghiệm", "video giải thích", "video viết tay", "video whiteboard", "video hoạt hình chữ", "video kể chuyện", "video dọc", "video cắt dán", "video vox", "kiểu vox", "công văn", "tờ trình", "soạn quyết định", "ra quyết định", "thông báo", "giấy mời", "biên bản", "văn bản hành chính", "Nghị định 30", "ND30", "đúng thể thức".

Các cụm "tạo nhanh", "làm nhanh", "không cần hỏi lại" là yêu cầu Quick tường minh (với bài tạo mới thông thường là hồ sơ `workflows/profiles/quick-generate.md` của upstream). Việc chọn hồ sơ và các bước thực hiện vẫn theo đúng `SKILL.md`.

## 4. Chạy lệnh trên Windows

- Có `venv\Scripts\python.exe` ở thư mục gốc repo thì dùng nó cho mọi lệnh `python3 …` hoặc `python …` của repo, ví dụ `venv\Scripts\python.exe skills/ppt-master/scripts/project_manager.py init <tên_dự_án>`.
- Nếu lệnh `python3 ...` báo không tìm thấy, trả mã 49 hoặc mở Microsoft Store, chạy lại đúng lệnh đó với `python`.
- Không dùng `cp`, `mkdir -p`, `/tmp` hay heredoc của bash trong PowerShell. Dùng lệnh tương đương (`Copy-Item`, `New-Item -ItemType Directory -Force`, `$env:TEMP`) hoặc Python.
- Khi ghi file có chữ tiếng Việt từ PowerShell 5.1, không dùng `Set-Content` hay `Out-File` mặc định. Dùng Python hoặc `[IO.File]::WriteAllText(path, text, (New-Object Text.UTF8Encoding $false))`.

## 5. Khổ canvas theo cách gọi của người Việt

<!-- format-map:start -->
| Người dùng nói | Key canvas |
|---|---|
| Slide 16:9, trình chiếu | `ppt169` |
| Slide 4:3, máy chiếu cũ | `ppt43` |
| Bài đăng Facebook/TikTok dọc 3:4 | `xiaohongshu` |
| Ảnh vuông Zalo/Facebook/Instagram | `moments` |
| Story, Reels, TikTok 9:16 | `story` |
| Ảnh bìa bài viết Zalo OA (2.35:1) | `wechat` |
<!-- format-map:end -->

## 6. Font

Với chữ tiếng Việt, chỉ dùng font có sẵn trên Windows hiển thị đủ dấu: Segoe UI, Arial, Calibri, Times New Roman (văn bản hành chính). Không dùng PingFang SC hay Microsoft YaHei cho chữ tiếng Việt.

## 7. Giọng thuyết minh (edge-tts)

- Giọng nữ: `vi-VN-HoaiMyNeural`
- Giọng nam: `vi-VN-NamMinhNeural`

## 8. Kết quả

Sau khi xuất, cho người dùng biết đường dẫn file PPTX trong thư mục dự án dưới `projects/`.

## 9. Môi trường: tự kiểm tra, tự cài và xử lý lỗi

- Mỗi cuộc trò chuyện, trước lệnh Python đầu tiên của repo (ví dụ `project_manager.py init`, `source_to_md.py`): chạy `tools/vi/doctor.py --no-smoke --json` (bằng Python của `venv` nếu có). Kết quả có `"ready": true` thì làm tiếp; chưa sẵn sàng, hoặc không chạy được Python, thì làm theo [docs/vi/cai-dat-bang-ai.md](docs/vi/cai-dat-bang-ai.md) rồi mới chạy lệnh đó.
- Yêu cầu thuộc mục 10: chạy kiểm tra trên (chỉ đọc, vài giây) trước khi gửi tin nhắn hỏi thầy cô. Chưa sẵn sàng thì thêm đúng một dòng ở cuối tin nhắn hỏi (ngay trước dòng chốt cách xác nhận, nếu có): "Máy chưa cài xong bộ công cụ; sau khi thầy cô trả lời, em sẽ cài trước (khoảng 5–10 phút) rồi làm bài." Không chạy được lệnh kiểm tra (công cụ chạy lệnh bị tắt hoặc bị từ chối) thì không kết luận máy chưa cài, mà dùng dòng này thay thế: "Em chưa kiểm tra được máy; sau khi thầy cô trả lời, em sẽ chạy kiểm tra `tools/vi/doctor.py` và cài nếu cần (khoảng 5–10 phút) rồi làm bài." Thầy cô trả lời xong thì cài ngay theo [docs/vi/cai-dat-bang-ai.md](docs/vi/cai-dat-bang-ai.md), rồi mới làm tiếp.
- Lệnh Python nào của repo báo không tìm thấy Python (kể cả sau khi chạy lại với `python` theo mục 4) hoặc báo `ModuleNotFoundError`: dừng, làm theo [docs/vi/cai-dat-bang-ai.md](docs/vi/cai-dat-bang-ai.md); không tự cài Python hay thư viện theo cách khác.
- Người dùng nhờ cài đặt, kiểm tra máy, hoặc dán link repo để cài: làm theo [docs/vi/cai-dat-bang-ai.md](docs/vi/cai-dat-bang-ai.md).
- Cần FFmpeg (thuyết minh, video) hoặc Pandoc (tài liệu định dạng cũ như `.doc`, `.odt`, `.rtf`) mà máy chưa có: làm theo mục "Công cụ tuỳ chọn" của file đó.
- Người dùng gặp lỗi môi trường: đề nghị chạy `KIEM-TRA.bat` (Windows) hoặc `python tools/vi/doctor.py`, rồi đối chiếu với [docs/vi/xu-ly-loi.md](docs/vi/xu-ly-loi.md).

## 10. Hỗ trợ thầy cô trước khi làm bài

Khi người dùng viết tiếng Việt và yêu cầu thuộc một trong 11 loại việc dưới đây, đọc [docs/vi/tro-ly/quy-trinh-hoi.md](docs/vi/tro-ly/quy-trinh-hoi.md) trước, rồi đọc file của loại việc đó. Hỏi thầy cô một lượt và chờ trả lời trước khi khởi tạo dự án. Riêng Video giải thích chỉ hỏi khi câu lệnh thiếu chủ đề hoặc nội dung, dùng được cho mọi ngành và không chờ duyệt kịch bản (mục 15).

| Loại việc | File hướng dẫn |
|---|---|
| Bài giảng | [docs/vi/tro-ly/bai-giang.md](docs/vi/tro-ly/bai-giang.md) |
| Báo cáo – tổng kết | [docs/vi/tro-ly/bao-cao-tong-ket.md](docs/vi/tro-ly/bao-cao-tong-ket.md) |
| Hoạt động Đoàn – sự kiện | [docs/vi/tro-ly/hoat-dong-doan.md](docs/vi/tro-ly/hoat-dong-doan.md) |
| Poster/ấn phẩm Zalo – Facebook | [docs/vi/tro-ly/poster-mang-xa-hoi.md](docs/vi/tro-ly/poster-mang-xa-hoi.md) |
| Tập huấn/workshop | [docs/vi/tro-ly/tap-huan-workshop.md](docs/vi/tro-ly/tap-huan-workshop.md) |
| Video bài giảng | [docs/vi/tro-ly/video-bai-giang.md](docs/vi/tro-ly/video-bai-giang.md) |
| Soạn đề KHTN tiếng Anh | [docs/vi/tro-ly/de-khtn-tieng-anh.md](docs/vi/tro-ly/de-khtn-tieng-anh.md) |
| Soạn giáo án tích hợp năng lực số và AI | [docs/vi/tro-ly/giao-an.md](docs/vi/tro-ly/giao-an.md) |
| Thí nghiệm ảo | [docs/vi/tro-ly/thi-nghiem-ao.md](docs/vi/tro-ly/thi-nghiem-ao.md) |
| Video giải thích dựng bằng mã | [docs/vi/tro-ly/video-giai-thich.md](docs/vi/tro-ly/video-giai-thich.md) |
| Soạn văn bản hành chính (Nghị định 30) | [docs/vi/tro-ly/van-ban-hanh-chinh.md](docs/vi/tro-ly/van-ban-hanh-chinh.md) |

- `SKILL.md` vẫn được ưu tiên. Lượt hỏi này chỉ tạo thêm tài liệu nguồn; bước xác nhận của upstream vẫn bắt buộc, trừ khi người dùng yêu cầu tạo nhanh (xem mục 3) hoặc thuộc loại việc "Soạn đề KHTN tiếng Anh" (mục 12), "Soạn giáo án tích hợp năng lực số và năng lực AI" (mục 13), "Thí nghiệm ảo" (mục 14), "Video giải thích" (mục 15) hoặc "Soạn văn bản hành chính (Nghị định 30)" (mục 16) — năm loại việc đó không có bước xác nhận của upstream, xem mục 12, mục 13, mục 14, mục 15 và mục 16. Khi tạo nhanh, kể cả với "không cần hỏi lại", vẫn đọc `docs/vi/tro-ly/quy-trinh-hoi.md` và làm theo mục "Tạo nhanh" của file đó: có thể không hỏi câu nào, nhưng vẫn ghi brief.
- Hiệu ứng: làm theo mức trong brief và [docs/vi/tro-ly/hieu-ung-lop-hoc.md](docs/vi/tro-ly/hieu-ung-lop-hoc.md). Bài giảng, báo cáo, hoạt động Đoàn, tập huấn: sau khi xuất PPTX, chạy `tools\vi\kiem_hieu_ung.py <file.pptx> --muc <mức>`, sửa tối đa một lần rồi báo kết quả cho thầy cô.
- Bài mới dạng PPTX (Bài giảng, Báo cáo – tổng kết, Hoạt động Đoàn – sự kiện, Poster/ấn phẩm Zalo – Facebook, Tập huấn/workshop) không làm toàn chữ: chọn nguồn ảnh cho từng trang theo mục "Ảnh minh hoạ" của `docs/vi/tro-ly/quy-trinh-hoi.md`, kể cả khi tạo nhanh.
- Câu lệnh khớp hai loại việc: từ chỉ dạng đầu ra thắng "thông báo", "quyết định" ("Làm poster Zalo thông báo họp phụ huynh" là Poster); tên loại văn bản đứng ngay sau động từ soạn thảo thắng các từ chủ đề ("Soạn công văn cử giáo viên đi tập huấn" là văn bản hành chính). Chi tiết ở mục "Khi nào áp dụng" của `docs/vi/tro-ly/quy-trinh-hoi.md`.
- Yêu cầu không thuộc 11 loại (bối cảnh trường học hay Đoàn một mình không đủ để xếp loại), hoặc người dùng không viết tiếng Việt: làm theo `SKILL.md` như bình thường, không tìm hồ sơ đơn vị và không dùng bộ câu hỏi Việt.

## 11. Làm video bài giảng

Câu chỉ có "làm video" hoặc "xuất video" (không nói rõ từ slide hay video giải thích): hỏi đúng một câu "Thầy cô muốn làm video từ bài giảng slide đã có, hay dựng video giải thích mới từ nội dung chữ?". Trả lời slide thì làm theo mục này; trả lời video mới thì làm theo mục 15.

Khi người dùng yêu cầu làm video từ một bài giảng đã có, đọc [docs/vi/tro-ly/video-bai-giang.md](docs/vi/tro-ly/video-bai-giang.md), hỏi một lượt theo file đó, rồi làm đúng thứ tự sau. Như mục 4: có `venv\Scripts\python.exe` ở thư mục gốc repo thì dùng nó cho mọi lệnh Python dưới đây, không có thì dùng `python`.

1. Chưa có `notes/*.md`: viết ghi chú lời giảng cho từng slide theo quy trình của upstream.
2. Chưa có `audio/*.mp3`: chạy `skills/ppt-master/scripts/notes_to_audio.py <đường_dẫn_dự_án> --voice vi-VN-HoaiMyNeural` (hoặc `vi-VN-NamMinhNeural`). Tốc độ đọc: chậm → thêm `--rate -10%`; vừa → không thêm cờ nào; nhanh → thêm `--rate +15%`.
3. Chưa có `exports/*_narrated.pptx`, hoặc dự án có `animations.json`: xuất bản PPTX đã gắn tiếng bằng `skills/ppt-master/scripts/svg_to_pptx.py <đường_dẫn_dự_án> --recorded-narration audio`; dự án tạo nhanh (không có `spec_lock.md`) thì thêm `--quick-generate --with-notes`. Dự án có `animations.json` mà thầy cô giữ hiệu ứng: trước đó tạo `animations_video.json` theo mục "Video" của [docs/vi/tro-ly/hieu-ung-lop-hoc.md](docs/vi/tro-ly/hieu-ung-lop-hoc.md) và thêm `--animation-config animations_video.json`; thầy cô bỏ hiệu ứng thì thêm `--no-animations`. Bỏ bước này thì đường PowerPoint không chạy được, AI buộc phải ghép bằng FFmpeg và phải tải Chromium. Chi tiết ở [docs/audio-narration.md](docs/audio-narration.md).
4. Kiểm hiệu ứng trước khi dựng: `venv\Scripts\python.exe tools\vi\kiem_hieu_ung.py <đường_dẫn_dự_án>\exports\<file>_narrated.pptx --video`. `error` khác `null` thì sửa và kiểm lại đúng một lần theo mục "Kiểm sau khi xuất" của file hướng dẫn hiệu ứng; vẫn không đạt thì dừng, không dựng video, báo thầy cô.
5. Dựng video: `venv\Scripts\python.exe tools\vi\video.py <đường_dẫn_dự_án>` kèm các cờ chọn theo đúng câu trả lời của thầy cô.

| Thầy cô trả lời | Cờ thêm vào |
|---|---|
| Phụ đề để thành file riêng | `--phu-de file` |
| Phụ đề in lên hình | `--phu-de hinh` |
| Không cần phụ đề | `--phu-de khong` |
| Độ phân giải 1080 | `--do-phan-giai 1080` |
| Độ phân giải 720 | `--do-phan-giai 720` |
| Muốn giữ hiệu ứng chuyển cảnh | `--cach powerpoint` |
| Không muốn mở PowerPoint | `--cach ffmpeg` |
| Không nêu cách dựng | `--cach auto` |

6. Đọc dòng JSON ở stdout. `ready` là `true` thì báo thầy cô đường dẫn video, thời lượng, dung lượng và nơi để phụ đề; `error` khác `null` thì làm theo `error.fix`, tối đa một lần, rồi báo thầy cô.

- `error.step` là `chromium`: hỏi thầy cô trước rồi chạy `powershell -NoProfile -ExecutionPolicy Bypass -File tools\vi\pptmaster.ps1 -Action tool -Name chromium`, vì bước này tải khoảng 150–300 MB.
- `error.step` là `audio`: quay lại bước 1 nếu dự án chưa có `notes/*.md`, quay lại bước 2 nếu đã có ghi chú.
- Cách dựng `powerpoint` sẽ mở **cửa sổ PowerPoint** và chiếm máy vài phút; báo trước cho thầy cô một dòng.
- Đường FFmpeg ghép từ ảnh chụp slide nên độ phân giải cao nhất bằng khổ slide, tức 1280×720 với `ppt169`; chọn 1080 ở đường này cũng không nét hơn.
- Không tự cài phần mềm nào khác, không tự chạy FFmpeg theo cách riêng.

## 12. Soạn đề KHTN bằng tiếng Anh

Khi người dùng cần đề kiểm tra KHTN bằng tiếng Anh, đọc [docs/vi/tro-ly/de-khtn-tieng-anh.md](docs/vi/tro-ly/de-khtn-tieng-anh.md) và [docs/vi/tro-ly/tieng-anh-khoa-hoc.md](docs/vi/tro-ly/tieng-anh-khoa-hoc.md) rồi làm đúng thứ tự dưới. Như mục 4: có `venv\Scripts\python.exe` ở thư mục gốc repo thì dùng nó cho mọi lệnh Python dưới đây.

1. Luồng A (đã có đề tiếng Việt): đọc đề thầy cô đưa bằng `python skills/ppt-master/scripts/source_to_md.py <file> -o <thư_mục_tạm>` trước khi hỏi gì. Thầy cô đưa **ảnh** thì nói rõ không đọc được ảnh, xin bản PDF hoặc Word. Luồng B (đề mới hoàn toàn) không có gì để đọc, bỏ qua bước này.
2. Sau bước 1 (luồng A) hoặc ngay từ đầu (luồng B), hỏi một lượt theo file hướng dẫn: luồng A lấy câu 3, 4 và 5 (chủ đề, số câu mỗi phần, tỉ lệ mức độ) trực tiếp từ đề vừa đọc, chỉ hỏi phần đề không trả lời được; luồng B hỏi đủ theo file đó.
3. Tạo `projects/_de-thi/<tên_đề>/`. Luồng B soạn ma trận đặc tả trước (chủ đề × mức độ × số câu) theo câu trả lời của thầy cô, viết câu hỏi trực tiếp bằng tiếng Anh, ghi bản tiếng Việt của từng câu vào `vi:` để thầy cô soát. Viết `de.md` theo đúng ngữ pháp trong file hướng dẫn.
4. Chạy `python tools\vi\de_thi.py projects\_de-thi\<tên_đề>`; thêm `--phan de,dap-an` khi thầy cô không cần bản song ngữ; thêm `--plan-only` khi chỉ muốn kiểm cú pháp.
5. Đọc dòng JSON ở stdout. `ready` là `true` thì báo thầy cô đường dẫn các file thực sự sinh ra (hai file khi chạy `--phan de,dap-an`, ba file với các trường hợp còn lại), số câu mỗi phần, tổng điểm, đọc nguyên văn các dòng `warnings`, và báo cho thầy cô các mục trong "Cần thầy cô soát" của file đáp án.

| `error.step` | Xử lý |
|---|---|
| `input` | Chưa có `de.md`, viết file rồi chạy lại. |
| `parse` | Sửa đúng dòng `error.message` nêu rồi chạy lại. |
| `docx` | Có `venv\Scripts\python.exe` ở thư mục gốc repo thì chạy `venv\Scripts\python.exe -m pip install -r tools/vi/requirements-vi.txt`; không thì chạy `python -m pip install -r tools/vi/requirements-vi.txt` (thư viện `python-docx`). Chạy lại lệnh xuất, tối đa một lần. |
| `write` | Xin thầy cô đóng file Word đang mở rồi chạy lại. |
| `internal` | Lỗi ngoài dự kiến; dán nguyên `error.message` để báo cho người bảo trì, không tự đoán cách sửa. |

Điều cấm: không tự sửa số liệu hay đáp án của đề gốc; không chạy `project_manager.py init`; không tạo SVG; không chạm `skills/`; không commit gì trong `projects/`.

## 13. Soạn giáo án tích hợp năng lực số và năng lực AI

Câu lệnh có chữ "giáo án" thì hỏi đúng một câu trước: "Thầy cô cần file Word kế hoạch bài dạy (giáo án 5512), hay slide trình chiếu cho bài này?". Trả lời Word thì theo mục này; trả lời slide thì theo mục 10. Câu lệnh có "kế hoạch bài dạy", "KHBD", "giáo án Word" hoặc "giáo án 5512" là rõ ràng: đi thẳng vào mục này, không hỏi câu trên.

Đọc [docs/vi/tro-ly/giao-an.md](docs/vi/tro-ly/giao-an.md) và [docs/vi/tro-ly/nang-luc-so-va-ai.md](docs/vi/tro-ly/nang-luc-so-va-ai.md) rồi làm đúng thứ tự dưới. Như mục 4: có `venv\Scripts\python.exe` ở thư mục gốc repo thì dùng nó cho mọi lệnh Python dưới đây, không có thì dùng `python`.

1. Luồng A (nâng cấp giáo án có sẵn): đọc giáo án cũ bằng `python skills/ppt-master/scripts/source_to_md.py <file> -o <thư_mục_tạm>` trước khi hỏi gì. Thầy cô đưa **ảnh** thì nói rõ không đọc được, xin PDF hoặc Word. Luồng B (soạn mới) không có gì để đọc, bỏ qua bước này.
2. Sau bước 1 (luồng A) hoặc ngay từ đầu (luồng B), hỏi một lượt theo file hướng dẫn, chờ trả lời.
3. (tuỳ chọn) Có file kế hoạch dạy học hoặc phân phối chương trình thì đọc để lấy tuần, tiết thứ, yêu cầu cần đạt và mã năng lực số đã khai. **Không sửa** file đó.
4. (tuỳ chọn) Cần nội dung SGK thì chuyển quyển SGK sang Markdown một lần, đặt ở `projects\_giao-an\_sgk\`, rồi cắt: `python tools\vi\giao_an.py trich-sgk projects\_giao-an\_sgk\<file>.md --bai "Bài <số>" --ra projects\_giao-an\<tên_bài>\sgk-trich.md` (ví dụ `--bai "Bài 5"`, không truyền cả tên bài; dùng `--ra` để lần cắt sau không ghi đè lần trước). Không nạp cả quyển.
5. Tạo `projects/_giao-an/<tên_bài>/` và viết `giao-an.md`.
6. `python tools\vi\giao_an.py xuat projects\_giao-an\<tên_bài>`; thêm `--plan-only` khi chỉ muốn kiểm.
7. Đọc dòng JSON. `ready` là `true` thì báo thầy cô đường dẫn hai file, số hoạt động, tổng thời lượng, các mã đã dùng, và đọc nguyên văn `warnings` cùng nội dung `can-soat.md`.

| `error.step` | Xử lý |
|---|---|
| `input` | Chưa có `giao-an.md`, viết file rồi chạy lại. |
| `parse` | Sửa đúng dòng `error.message` nêu rồi chạy lại. |
| `framework` | Sửa mã theo `error.fix`, **không tự đặt mã mới**. |
| `docx` | Có `venv\Scripts\python.exe` ở thư mục gốc repo thì chạy `venv\Scripts\python.exe -m pip install -r tools/vi/requirements-vi.txt`; không thì chạy `python -m pip install -r tools/vi/requirements-vi.txt`, rồi chạy lại, tối đa một lần. |
| `write` | Xin thầy cô đóng file Word đang mở rồi chạy lại. |
| `internal` | Lỗi ngoài dự kiến; dán nguyên `error.message` để báo cho người bảo trì, không tự đoán cách sửa. |

Với `trich-sgk`: `parse` là không tìm thấy bài (sửa `--bai` theo `error.fix`), `write` là thư mục của `--ra` không ghi được.

Điều cấm: không sửa nội dung chuyên môn của thầy cô; không sửa file phân phối chương trình; không tự đặt mã; không in ghi chú nội bộ vào giáo án; không commit gì trong `projects/`; không chạy `project_manager.py init`; không tạo SVG; không chạm `skills/`.

## 14. Làm thí nghiệm ảo

Khi người dùng cần một thí nghiệm ảo hoặc mô phỏng tương tác cho Toán, Vật lí, Hoá học, đọc [docs/vi/tro-ly/thi-nghiem-ao.md](docs/vi/tro-ly/thi-nghiem-ao.md) và [docs/vi/tro-ly/mo-hinh-thi-nghiem.md](docs/vi/tro-ly/mo-hinh-thi-nghiem.md) rồi làm đúng thứ tự dưới. Như mục 4: có `venv\Scripts\python.exe` ở thư mục gốc repo thì dùng nó cho mọi lệnh Python dưới đây, không có thì dùng `python`.

1. Hỏi một lượt theo file hướng dẫn, chờ trả lời. Chọn mẫu gần nhất trong danh mục; chỉ viết mô hình mới khi không mẫu nào dùng được, và nói trước với thầy cô rằng mô hình mới cần thầy cô soát công thức.
2. Tạo `projects/_thi-nghiem/<tên_thí_nghiệm>/` và viết `thi-nghiem.md` theo đúng ngữ pháp trong file hướng dẫn. Mô hình mới thì đặt `mau: moi` và viết thêm `mo-hinh.json`, `mo-hinh.js` theo khuôn.
3. Chạy `python tools\vi\thi_nghiem.py projects\_thi-nghiem\<tên_thí_nghiệm>`; thêm `--plan-only` khi chỉ muốn kiểm; thêm `--phan html` khi thầy cô không cần phiếu học tập.
4. Đọc dòng JSON ở stdout. `ready` là `true` thì báo thầy cô đường dẫn các file, mẫu đã dùng, tham số thay đổi được, số lần đo, kết quả `kiem_so` (đạt bao nhiêu trên bao nhiêu dòng, hoặc chưa chạy vì máy không có Node), đọc nguyên văn `warnings` và nội dung `can-soat.md`. Dặn thầy cô: mở `thi-nghiem.html` bằng trình duyệt là chạy, không cần mạng; muốn học sinh dùng điện thoại thì đưa file lên web.
5. Thầy cô làm slide cho cùng bài: thêm trang nối sang thí nghiệm theo mục "Nối vào bài giảng" của file hướng dẫn.

| `error.step` | Xử lý |
|---|---|
| `input` | Chưa có thư mục hoặc `thi-nghiem.md`, viết file rồi chạy lại. |
| `parse` | Sửa đúng dòng `error.message` nêu rồi chạy lại. Khoảng tham số vượt khoảng của mẫu thì thu hẹp khoảng, không đổi mẫu. |
| `model` | Mã mẫu không có, hoặc mô hình mới sai khuôn: sửa theo `error.message` và khuôn trong file hướng dẫn mô hình. |
| `check` | Bảng số kiểm trượt: sửa hàm `tinh` của mô hình mới cho khớp bảng. Chỉ sửa bảng khi chính bảng sai, và khi đó nói rõ với thầy cô dòng nào đã sửa. |
| `docx` | Có `venv\Scripts\python.exe` ở thư mục gốc repo thì chạy `venv\Scripts\python.exe -m pip install -r tools/vi/requirements-vi.txt`; không thì chạy `python -m pip install -r tools/vi/requirements-vi.txt`, rồi chạy lại, tối đa một lần. |
| `write` | Xin thầy cô đóng file Word hoặc tab trình duyệt đang mở file cũ rồi chạy lại. |
| `internal` | Lỗi ngoài dự kiến; dán nguyên `error.message` để báo cho người bảo trì, không tự đoán cách sửa. |

Điều cấm: không viết file HTML bằng tay; không bỏ bảng số kiểm, công thức hay điều kiện áp dụng để qua được công cụ; không chèn thư viện, font hay địa chỉ web từ Internet; không sửa file trong `tools/vi/thi_nghiem_parts/`; không chạy `project_manager.py init`; không tạo SVG; không chạm `skills/`; không commit gì trong `projects/`.

## 15. Làm video giải thích

Khi người dùng cần một video giải thích từ một chủ đề hay nội dung chữ (video giải thích, video vox, kiểu vox, video viết tay, video whiteboard, video hoạt hình chữ, video kể chuyện, video dọc, video cắt dán), làm video kiểu Vox: dùng cho mọi ngành, không theo khuôn bài giảng. Đọc [docs/vi/tro-ly/video-giai-thich.md](docs/vi/tro-ly/video-giai-thich.md) và [docs/vi/tro-ly/nhip-vox.md](docs/vi/tro-ly/nhip-vox.md) rồi làm đúng thứ tự dưới. Câu chỉ có "làm video" hoặc "xuất video" thì hỏi câu phân loại ở đầu mục 11 trước. Như mục 4: có `venv\Scripts\python.exe` ở thư mục gốc repo thì dùng nó cho mọi lệnh Python dưới đây, không có thì dùng `python`.

1. Chỉ hỏi khi câu lệnh thiếu chủ đề hoặc thiếu nội dung mà AI không tự viết đúng được (một tin nhắn, tối đa hai câu). Điều không nói thì dùng mặc định của file hướng dẫn: `thoi-luong: 60`, khổ ngang, giọng Thu Giang (VieNeu) tốc độ vừa, ảnh kiểu cắt dán cổ điển, mỗi cảnh một nền AI, phụ đề `karaoke`, có tiếng hiệu ứng, không nhạc nền. AI không dừng chờ duyệt kịch bản; người dùng xin xem kịch bản trước thì gửi kịch bản và dừng tới khi họ đồng ý.
2. Tạo `projects/_video/<tên_video>/` và viết `video.md` với `phong-cach: vox` và `thoi-luong`. Mạch: móc → vấn đề → 2–4 ý, mỗi ý một hình ví von → lật → chốt; không cảnh tiêu đề riêng. Lời liền mạch: câu 10–20 từ nối ý với nhau, không băm thành câu cụt. Quỹ từ theo `thoi-luong` và giọng (60 giây ≈ 230 từ với giọng Thu Giang, ≈ 150 từ với giọng edge-tts; 6–8 cảnh). Mỗi cảnh ghi `nen:` tả nền cắt dán của cảnh, và mở bằng nhãn tiêu đề cùng cụm hình chính ở `@dau` (cảnh mở bằng nền trống có cảnh báo "hiện muộn"). Không bịa số liệu: chỉ dùng số người dùng đưa hoặc có nguồn gọi tên được, ghi ở `nguon:` của cảnh. Người dùng đưa file giọng thu sẵn thì đặt vào `giong/canh-N.mp3`.
3. `python tools\vi\video_ma.py projects\_video\<tên_video> --plan-only`: đọc `thoi_luong_uoc` và cảnh báo `thoi-luong` trong `warnings`; lệch thì sửa `video.md` rồi chạy lại bước này. Bước này chưa cần ảnh: nhịp `anh` chưa có ảnh chỉ là cảnh báo.
4. Ảnh: `python tools\vi\anh_vox.py projects\_video\<tên_video>` (video không có nhịp `anh` thì bỏ bước này). Nền tảng có công cụ vẽ ảnh (Antigravity, Codex) thì chạy trước với `--chi-ke-hoach`, vẽ từng mục `"nguon": "ve"` của `anh/ai/ke-hoach.json` (dán nguyên văn `prompt`) và lưu đúng `anh/ai/goc/<ma>.png`, rồi chạy lại với `--cong-cu "<nền tảng>" --mo-hinh "<mô hình đã vẽ>"` (không biết mô hình thì bỏ hai cờ). Nền tảng khác, như Claude Code, để lệnh tự gọi API tạo ảnh theo `ANH_AI_URL`, `ANH_AI_KEY`, `ANH_AI_MO_HINH` (mặc định 9router `http://localhost:20128/v1`, mô hình `ag/gemini-3.1-flash-image`). Ảnh thật `anh: tim: <từ khoá tiếng Anh>` do lệnh tự tải bằng `image_search.py`.
5. `python tools\vi\video_ma.py projects\_video\<tên_video> --xem-truoc`: mở `xem-truoc/canh-N-giua.png` và `xem-truoc/canh-N.png` của từng cảnh và tự kiểm theo danh sách của file hướng dẫn. Hình phải khớp lời đọc; chữ không tràn; vật không chồng nhau; ảnh AI không có chữ, không sai ý. Lỗi nào thì sửa `video.md`, chạy lại từ bước 4 (chỉ ảnh có mô tả đổi mới vẽ lại), xem lại.
6. Báo một dòng rằng dựng mất khoảng 1,5 lần thời lượng video trên máy 6 lõi (chưa kể vẽ ảnh và tạo giọng), rồi chạy `python tools\vi\video_ma.py projects\_video\<tên_video>`. Đọc dòng JSON ở stdout. `ready` là `true` thì gửi đường dẫn `video.mp4`, thời lượng, nội dung `video.md` dạng dễ đọc, và đọc nguyên văn `warnings`. Video không hiện dòng nguồn nào: mô hình AI, nguồn ảnh thật, số liệu và nhạc nằm trong `nguon.txt` cạnh video; có ảnh thật hay nhạc CC BY thì nhắc người dùng dán nội dung file đó vào phần mô tả khi đăng. `error` khác `null` thì xử lý theo `error.step` ở bảng dưới.

Nhạc nền chỉ khi người dùng xin: tải bằng `python tools\vi\tim_nhac.py "<từ khoá tiếng Anh>" -o projects\_video\<tên_video>\nhac` (chỉ bản CC0 hoặc CC BY trên Openverse, dài từ 60 giây; nguồn tự ghi vào `nhac/nguon.json`), ghi `nhac-nen: <tên trong files>`, và gửi tên bài, tác giả, giấy phép kèm video để người dùng nghe thử. Nhạc người dùng gửi: chép vào `nhac/` và ghi `nguon-nhac:` theo lời họ. `tim_nhac.py` lỗi `mang` thì kiểm mạng rồi chạy lại, tối đa một lần; `input` hoặc `write` thì làm theo `error.fix`. Người dùng thấy ồn thì ghi `am-thanh: khong` hoặc bỏ dòng `nhac-nen` rồi dựng lại.

`video_ma.py`:

| `error.step` | Xử lý |
|---|---|
| `input` | Chưa có thư mục hoặc `video.md`, hoặc sai tham số lệnh: viết file rồi chạy lại. |
| `parse` | Sửa đúng dòng `error.message` nêu (cụm không có trong lời, nhịp sai thứ tự, ô sai với bố cục, chữ quá giới hạn, khoá không dùng với Vox) rồi chạy lại. |
| `canh` | Sửa đúng cảnh `error.message` nêu theo `error.fix`: nhịp chưa có ảnh đã xử lý hay ảnh đã cũ so với `video.md` (chạy lại `anh_vox.py`), cảnh chưa có nền AI hay nền đã cũ (chạy lại `anh_vox.py`; máy không có nguồn vẽ thì ghi `nen-canh: khong`), chữ của nhịp tràn ô, hai vật đè lên nhau quá nhiều. "Cảnh 0: nhạc nền: …" là lỗi file nhạc (thiếu, sai định dạng, hỏng hoặc chưa có nguồn): tải lại bằng `tim_nhac.py` hoặc thêm `nguon-nhac:`. |
| `giong` | Giọng Thu Giang lỗi: kiểm VieNeu chạy được (biến môi trường `VIENEU_PYTHON` trỏ tới python của VieNeu) hoặc ghi `giong: nu`. Giọng edge-tts lỗi, thường do mất mạng: kiểm mạng rồi chạy lại, tối đa một lần. Hoặc đặt sẵn file giọng người dùng đưa đúng tên `error.message` nêu (`giong/canh-N.mp3`). |
| `chromium` | Hỏi người dùng trước rồi chạy `powershell -NoProfile -ExecutionPolicy Bypass -File tools\vi\pptmaster.ps1 -Action tool -Name chromium`, vì bước này tải khoảng 150–300 MB. |
| `ffmpeg` | Cài FFmpeg theo mục "Công cụ tuỳ chọn" của [docs/vi/cai-dat-bang-ai.md](docs/vi/cai-dat-bang-ai.md) rồi chạy lại. |
| `dung` | Chụp khung hỏng (`error.message` nêu cảnh) hoặc ghép hỏng (`error.message` là thông báo của FFmpeg): báo nguyên `error.message`, không tự sửa. |
| `write` | Xin người dùng đóng `video.md` hoặc `video.mp4` đang mở, kiểm ổ đĩa còn chỗ, rồi chạy lại. |
| `internal` | Lỗi ngoài dự kiến; dán nguyên `error.message` để báo cho người bảo trì, không tự đoán cách sửa. |

`anh_vox.py` in một dòng JSON (`ready`, `files`, `so_anh`, `da_ve`, `dung_lai`, `ke_hoach`, `warnings`, `error`); đọc nguyên văn `warnings` (ảnh chuyển sang `khung` vì tách nền không sạch, ảnh do nền tảng vẽ chưa rõ mô hình: chạy lại với `--mo-hinh` nếu biết). `error.step`:

| `error.step` | Xử lý |
|---|---|
| `input` | Chưa có thư mục hoặc `video.md`, video không phải `phong-cach: vox`, thiếu file ảnh trong `anh/`, hoặc số ảnh cần vẽ quá giới hạn 30: làm theo `error.fix` (bớt nhịp `anh: ve:` hoặc thêm `--toi-da N`). |
| `parse` | Sửa đúng dòng `error.message` nêu trong `video.md` rồi chạy lại. |
| `cau-hinh` | Khoá thiếu hoặc bị từ chối (401), khoá có ký tự lạ, hoặc file cấu hình hỏng hay sai dạng: nhờ người dùng tự đặt `ANH_AI_KEY` theo `error.fix` (`setx ANH_AI_KEY "<khoá>"` rồi mở lại cửa sổ lệnh). Chưa được thì thay ảnh AI bằng `chu`, `the`, `dau`, `so` hoặc ảnh thật `tim:` và báo người dùng. |
| `mang` | Không gọi được nguồn vẽ (9router chưa chạy, sai `ANH_AI_URL`) hoặc không tải được ảnh thật: kiểm rồi chạy lại, tối đa một lần; ảnh thật thì đổi từ khoá `tim:`. |
| `nha-cung-cap` | Nguồn vẽ báo lỗi (hết hạn mức, từ chối câu lệnh, mô hình không có), trả dữ liệu không phải ảnh, hoặc ảnh thật chưa có nguồn: đọc nguyên văn lỗi; câu lệnh bị từ chối thì tả lại `ve:`; hết hạn mức thì báo người dùng (có thể đổi `ANH_AI_MO_HINH`). |
| `tach-nen` | Chưa có FFmpeg (cài theo [docs/vi/cai-dat-bang-ai.md](docs/vi/cai-dat-bang-ai.md)), hoặc một ảnh hỏng không tách nền được: xoá ảnh đó trong `anh/ai/goc/` để vẽ lại, hoặc thêm `khung` cho nhịp đó. |
| `write` | Đóng file đang mở, kiểm ổ đĩa còn chỗ, rồi chạy lại. |
| `internal` | Lỗi ngoài dự kiến; dán nguyên `error.message` để báo cho người bảo trì, không tự đoán cách sửa. |

- Giọng mặc định của Vox là Thu Giang (VieNeu), đọc ngay trên máy, không cần mạng; máy không có VieNeu thì công cụ tự dùng giọng nữ edge-tts (cần mạng) và báo trong `warnings`. Dựng không có mạng mà không có VieNeu thì mọi cảnh phải có file giọng sẵn trong `giong/`.
- Dựng thật chụp 30 khung/giây bằng nhiều tiến trình Chromium song song nên máy chạy nặng trong lúc dựng.
- Kịch bản cũ có dòng `loai:` (kiểu viết tay, cắt dán theo loại cảnh) vẫn dựng được bằng `video_ma.py`; sửa chúng theo [docs/vi/tham-khao/video-viet-tay.md](docs/vi/tham-khao/video-viet-tay.md) và [docs/vi/tham-khao/canh-video.md](docs/vi/tham-khao/canh-video.md). Người dùng nói rõ muốn kiểu viết tay cũ cho video mới thì cũng theo hai file đó.

Điều cấm:

- Không bịa số liệu; không tự sửa số liệu hay nội dung chuyên môn người dùng đưa, chỉ viết lại thành lời kể ngắn.
- Không viết HTML hay ảnh cảnh bằng tay; không sửa file trong `tools/vi/video_ma_parts/`.
- Không tự viết hay sửa `anh/ai/nguon.json`, `anh/ai/vox.json` (chỉ `anh_vox.py` ghi); không tự cắt, tách nền hay đặt ảnh vào `anh/ai/xu-ly/`.
- Khoá API (`ANH_AI_KEY`) không ghi vào file nào trong repo hay `projects/`, không in ra, không xin người dùng dán vào khung chat.
- Không chạy `project_manager.py init`; không tạo SVG; không chạm `skills/` (chỉ được chạy `image_search.py`, việc `anh_vox.py` tự làm); không commit gì trong `projects/`.
- Không tự cài phần mềm nào khác, không tự chạy FFmpeg theo cách riêng.
- Không dùng ảnh hay nhạc không rõ nguồn, không tự viết dòng nguồn cho ảnh, nhạc tải về.

Được phép: dùng công cụ tạo ảnh của chính nền tảng để vẽ ảnh trong `anh/ai/goc/` theo `ke-hoach.json`. Đây là ngoại lệ duy nhất của điều cấm "không viết ảnh cảnh bằng tay"; mọi điều cấm khác, kể cả không chạm `skills/`, giữ nguyên.

## 16. Soạn văn bản hành chính theo Nghị định 30

Khi người dùng cần công văn, tờ trình, quyết định, thông báo, giấy mời, biên bản hay văn bản hành chính khác ra file Word đúng thể thức Nghị định 30/2020/NĐ-CP, đọc [docs/vi/tro-ly/van-ban-hanh-chinh.md](docs/vi/tro-ly/van-ban-hanh-chinh.md) rồi làm đúng thứ tự dưới. Bộ sinh và bộ kiểm là mã ND30 nhúng ở `tools/vi/nd30/` (© 2026 Nguyễn Minh Phát, MIT). Như mục 4: có `venv\Scripts\python.exe` ở thư mục gốc repo thì dùng nó cho mọi lệnh Python dưới đây, không có thì dùng `python`.

Câu lệnh chỉ có "báo cáo" hoặc "kế hoạch" thì hỏi đúng một câu trước: "Thầy cô cần văn bản Word đúng thể thức Nghị định 30, hay slide trình chiếu?". Trả lời Word thì theo mục này; trả lời slide thì theo mục 10. Câu lệnh khớp hai loại việc: tên loại văn bản đứng ngay sau động từ soạn thảo thắng các từ chủ đề ("soạn công văn cử đi tập huấn" theo mục này); từ chỉ dạng đầu ra thắng "thông báo", "quyết định" ("poster thông báo" theo loại Poster). Văn bản Đảng và văn bản Đoàn không hỗ trợ: nói rõ với thầy cô, không dựng bằng thể thức Nghị định 30.

1. Thầy cô gửi tài liệu Word hoặc PDF thì đọc bằng `python skills/ppt-master/scripts/source_to_md.py <file> -o <thư_mục_tạm>` trước; ảnh chụp thì nói rõ không đọc được, xin PDF hoặc Word.
2. Sau bước 1, hỏi một lượt tối đa 7 câu theo file hướng dẫn (cơ quan chủ quản, địa danh, ký hiệu viết tắt lấy từ hồ sơ đơn vị; chưa có thì hỏi trong câu 1), chờ trả lời.
3. Chọn loại văn bản theo `tools/vi/nd30/references/danh-muc-loai-vb.md`; văn bản quy phạm của HĐND, UBND đọc thêm `tools/vi/nd30/references/the-thuc-qppl-*.md`.
4. Tạo `projects/_van-ban/<tên_văn_bản>/` và viết `noi-dung.json` sau khi đọc ví dụ đúng loại trong `tools/vi/nd30/examples/` (chỉ lấy khuôn, không chép tên đơn vị: từ 1/7/2025 chính quyền địa phương còn hai cấp, không còn huyện, quận, thị xã, thị trấn) và schema `tools/vi/nd30/schemas/nd30-input.schema.json`. Mọi thông tin thầy cô chưa nêu ghi `[CẦN BỔ SUNG: …]`.
5. Chạy `python tools\vi\van_ban.py "projects\_van-ban\<tên_văn_bản>"` (giữ ngoặc kép vì tên thư mục có khoảng trắng); thêm `--nhap` khi thầy cô chủ động muốn bản nháp.
6. Đọc dòng JSON. `ready` là `true` thì báo thầy cô đường dẫn `van-ban.docx` và `kiem-tra.md`, loại văn bản, số mục đạt và cảnh báo; `ban_nhap` là `true` thì nói rõ đây là bản nháp và đọc nguyên văn từng ô cần bổ sung trong `warnings`. Cảnh báo B7 (dấu, chữ ký số) lần nào cũng có, B3 có khi số văn bản để trống cho văn thư: đều bình thường, nhắc thầy cô soát tay. Đọc dòng "Thầy cô đối chiếu" để thầy cô soát số, ngày, người ký, cơ quan, căn cứ; dòng "Nghi còn chỗ trống" thì hỏi lại thầy cô chỗ đó. Luôn nhắc văn bản chưa đóng dấu, chưa ký.

| `error.step` | Xử lý |
|---|---|
| `input` | Thiếu thư mục hoặc `noi-dung.json`, file không phải UTF-8, hoặc sai tham số: viết hoặc lưu lại file rồi chạy lại. |
| `json` | Sửa đúng dòng, cột hoặc trường `error.message` nêu, theo schema và ví dụ đúng loại, rồi chạy lại. Lỗi `profile` thì làm theo `error.fix`. |
| `the-thuc` | Lỗi thể thức nặng, không có `van-ban.docx`: đọc các mục ✗ trong `kiem-tra.md`, sửa `noi-dung.json`, chạy lại tối đa hai lần; vẫn lỗi thì báo nguyên `error.message`. |
| `docx` | Có `venv\Scripts\python.exe` ở thư mục gốc repo thì chạy `venv\Scripts\python.exe -m pip install -r tools/vi/requirements-vi.txt`; không thì chạy `python -m pip install -r tools/vi/requirements-vi.txt`, rồi chạy lại, tối đa một lần. |
| `write` | Xin thầy cô đóng file Word đang mở rồi chạy lại. |
| `internal` | Lỗi ngoài dự kiến; dán nguyên `error.message` để báo cho người bảo trì, không tự đoán cách sửa. |

Điều cấm: không tự điền số, ký hiệu, ngày ban hành, người ký, căn cứ pháp lý, số tiền hay số liệu thầy cô chưa nêu; không giao bản nháp như thành phẩm; không đổi profile để qua bộ kiểm; không viết file Word bằng cách khác; không sửa file trong `tools/vi/nd30/`; không chạy `project_manager.py init`; không tạo SVG; không chạm `skills/`; không commit gì trong `projects/`.

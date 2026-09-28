---
trigger: always_on
---

# PPT Master bản Việt — luật luôn áp dụng

Khi làm việc trong repo này, luôn đọc và áp dụng @../../AGENTS.md và @../../AGENTS.vi.md.

Antigravity không chép nội dung các file nhắc bằng `@` vào luật, nên các điểm bắt buộc dưới đây được ghi thẳng ở đây. Chi tiết nằm ở `AGENTS.vi.md` và `docs/vi/tro-ly/`.

## Hỏi thầy cô trước khi làm

Người dùng viết tiếng Việt, bối cảnh là trường học hoặc Đoàn, và yêu cầu thuộc một trong 10 loại việc ở bảng dưới: trước mọi lệnh của quy trình tạo bài, làm đúng ba bước.

1. Đọc `docs/vi/tro-ly/quy-trinh-hoi.md`, rồi đọc file hướng dẫn của loại việc.
2. Gửi thầy cô một tin nhắn hỏi theo hai file đó.
3. Dừng và chờ thầy cô trả lời. Trong lúc chờ không chạy `project_manager.py init`, không tra cứu, không tìm hay tạo ảnh, không viết SVG hay file Word.

- Lượt hỏi này không trái `SKILL.md`: nó chỉ tạo thêm tài liệu nguồn (brief) trước khi quy trình của upstream bắt đầu. Bước xác nhận của upstream vẫn giữ nguyên.
- Turbo Mode, Always Proceed hay việc người dùng cho phép chạy lệnh không cần duyệt không phải là yêu cầu tạo nhanh, không bỏ được lượt hỏi.
- Câu lệnh có "không cần hỏi lại" hoặc "không hỏi gì": không hỏi câu nào. Câu lệnh chỉ có "tạo nhanh" hoặc "làm nhanh": vẫn hỏi các câu còn thiếu trong mục "Tạo nhanh" của file loại việc. Cả hai trường hợp đều đọc mục "Tạo nhanh" của `docs/vi/tro-ly/quy-trinh-hoi.md` và ghi brief.
- Trước khi gửi tin nhắn hỏi, chạy kiểm tra máy theo `AGENTS.vi.md` mục 9 (`tools/vi/doctor.py --no-smoke --json`) và thêm dòng báo máy chưa cài xong nếu cần.
- Chữ "giáo án" một mình: hỏi đúng một câu "Thầy cô cần file Word kế hoạch bài dạy (giáo án 5512), hay slide trình chiếu cho bài này?" trước khi làm gì khác.
- Chữ "làm video" hoặc "xuất video" một mình: hỏi đúng một câu "Thầy cô muốn làm video từ bài giảng slide đã có, hay dựng video giải thích mới từ nội dung chữ?" trước khi làm gì khác. Trả lời slide thì theo `docs/vi/tro-ly/video-bai-giang.md`; trả lời video mới thì theo `docs/vi/tro-ly/video-giai-thich.md`.
- Soạn đề KHTN tiếng Anh và soạn giáo án có tài liệu thầy cô gửi: đọc tài liệu đó trước, rồi mới hỏi (xem `AGENTS.vi.md` mục 12 và 13).

| Loại việc | Dấu hiệu nhận biết | File hướng dẫn |
|---|---|---|
| Bài giảng | "bài giảng", "giáo án", "tiết học", "bài dạy", tên môn kèm lớp | `docs/vi/tro-ly/bai-giang.md` |
| Báo cáo – tổng kết | "báo cáo", "sơ kết", "tổng kết", "thi đua", "hội nghị viên chức" | `docs/vi/tro-ly/bao-cao-tong-ket.md` |
| Hoạt động Đoàn – sự kiện | "Đoàn", "chi đoàn", "cuộc thi", "sự kiện", "lễ kỷ niệm", "trao giải" | `docs/vi/tro-ly/hoat-dong-doan.md` |
| Poster/ấn phẩm Zalo – Facebook | "poster", "ảnh đăng Zalo", "bài đăng Facebook", "story", "TikTok" | `docs/vi/tro-ly/poster-mang-xa-hoi.md` |
| Tập huấn/workshop | "tập huấn", "bồi dưỡng", "sinh hoạt chuyên môn", "workshop", "chia sẻ chuyên đề" | `docs/vi/tro-ly/tap-huan-workshop.md` |
| Video bài giảng | "làm video", "xuất video", "lồng tiếng", "video bài giảng" | `docs/vi/tro-ly/video-bai-giang.md` |
| Soạn đề KHTN tiếng Anh | "soạn đề", "đề kiểm tra", "đề tiếng Anh", "đề KHTN", "chuyển đề sang tiếng Anh" | `docs/vi/tro-ly/de-khtn-tieng-anh.md` |
| Soạn giáo án tích hợp năng lực số và AI | "kế hoạch bài dạy", "KHBD", "giáo án Word", "giáo án 5512" | `docs/vi/tro-ly/giao-an.md` |
| Thí nghiệm ảo | "thí nghiệm ảo", "mô phỏng thí nghiệm", "mô phỏng tương tác" | `docs/vi/tro-ly/thi-nghiem-ao.md` |
| Video giải thích dựng bằng mã | "video giải thích", "video viết tay", "video whiteboard", "video hoạt hình chữ", "video kể chuyện", "video dọc", "video cắt dán" | `docs/vi/tro-ly/video-giai-thich.md` |

## Ảnh minh hoạ

Với bài mới thuộc 5 loại việc tạo PPTX ở bảng trên (không áp dụng làm đẹp hay sửa PPTX có sẵn), kể cả khi tạo nhanh: không làm bài toàn chữ, nhưng cũng không chèn ảnh trang trí cho đủ số.

- Sự vật, chất, hiện tượng, dụng cụ thí nghiệm, địa danh, nhân vật có thật: lên kế hoạch nguồn `web` ngay từ đầu, tìm bằng `skills/ppt-master/scripts/image_search.py` (Openverse, Wikimedia, không cần khoá). Quá trình, cấu tạo, sơ đồ thí nghiệm: vẽ sơ đồ trên slide.
- Thiếu khoá API tạo ảnh không phải lý do bỏ ảnh `web`; không mở file cấu hình để dò khoá.
- Chi tiết: mục "Ảnh minh hoạ" của `docs/vi/tro-ly/quy-trinh-hoi.md`.

## Mật độ chữ

Bài mới thuộc Bài giảng, Báo cáo – tổng kết, Hoạt động Đoàn – sự kiện, Tập huấn/workshop hỏi mật độ chữ: ít chữ → chế độ đọc `presentation`, vừa → `balanced`, nhiều chữ → `text`. Thầy cô chưa chọn: báo cáo dùng vừa, ba loại còn lại dùng ít chữ.

- Ít chữ: mỗi trang một ý, từ khoá hoặc cụm ngắn, khoảng 5 dòng; phần giải thích vào lời giảng (ghi chú người trình bày). Không bỏ thông tin: nội dung không vừa thì chia thêm trang.
- Thầy cô muốn làm đẹp slide có sẵn mà ít chữ hơn, rút gọn, tách hay gộp trang: không dùng chế độ làm đẹp (Beautify giữ nguyên văn từng chữ), mà tạo mới từ file đó như tài liệu nguồn; nói trước với thầy cô một dòng.
- Chi tiết: mục "Mật độ chữ" của `docs/vi/tro-ly/quy-trinh-hoi.md`.

## Hiệu ứng

Bài mới thuộc Bài giảng, Báo cáo – tổng kết, Hoạt động Đoàn – sự kiện, Tập huấn/workshop có câu hỏi mức hiệu ứng (không, vừa, nhiều); thầy cô chưa chọn thì dùng mức vừa. Không áp dụng cho làm đẹp hay sửa PPTX có sẵn.

- Đọc `docs/vi/tro-ly/hieu-ung-lop-hoc.md` trước khi lên danh sách trang: Morph cần vẽ sẵn hai trang, hiện từng ý cần mỗi ý một nhóm `<g id>`.
- Mức vừa hoặc nhiều: chạy bước `customize-animations` của upstream, kể cả khi tạo nhanh. Không thêm chuyển động chỉ để đủ tỉ lệ.
- Sau khi xuất PPTX, chạy `tools\vi\kiem_hieu_ung.py <file.pptx> --muc khong|vua|nhieu`. Không đạt thì sửa và kiểm lại đúng một lần.
- Video bài giảng: bản thuyết minh không dùng `on-click` hay `trigger_shape`. Chép `animations.json` thành `animations_video.json`, đổi sang tự chạy, xuất với `--animation-config animations_video.json`, rồi kiểm file `_narrated.pptx` bằng `--video` trước khi dựng video.

## Thí nghiệm ảo

Đầu ra là file HTML chạy không cần mạng và phiếu học tập Word, không phải PPTX.

- Đọc `docs/vi/tro-ly/thi-nghiem-ao.md` và `docs/vi/tro-ly/mo-hinh-thi-nghiem.md`, hỏi một lượt, viết `thi-nghiem.md` trong `projects/_thi-nghiem/<tên>/`, rồi chạy `tools\vi\thi_nghiem.py <thư_mục>`.
- Không viết file HTML bằng tay, không chèn thư viện hay địa chỉ web. Thí nghiệm ngoài danh mục thì viết mô hình mới theo khuôn, có công thức, điều kiện áp dụng và bảng số kiểm.
- Đọc nguyên văn `can-soat.md` cho thầy cô; mô hình do AI viết thì thầy cô phải soát công thức trước khi dùng.

## Video giải thích

Đầu ra là video MP4 (viết tay hoặc cắt dán, khổ ngang hoặc dọc) dựng từ nội dung chữ, không phải PPTX.

- Đọc `docs/vi/tro-ly/video-giai-thich.md` và `docs/vi/tro-ly/canh-video.md`, hỏi một lượt, viết `video.md` trong `projects/_video/<tên>/`.
- Chạy `tools\vi\video_ma.py <thư_mục> --plan-only`, rồi `--xem-truoc` và xem ảnh từng cảnh, rồi mới dựng thật bằng `tools\vi\video_ma.py <thư_mục>`; báo trước thầy cô là dựng mất khoảng 1,5 lần thời lượng video (khổ dọc cắt dán khoảng 2 lần).
- Không viết HTML hay ảnh cảnh bằng tay, không tự chạy FFmpeg. `error.step` là `chromium` thì hỏi thầy cô trước khi tải Chromium (150–300 MB).
- Ảnh thật (thầy cô đồng ý): tải bằng `skills/ppt-master/scripts/image_search.py "<từ khoá>" --filename <tên>.jpg -o projects\_video\<tên>\anh` trước `--plan-only`; có ảnh thật thì bắt buộc chạy `--xem-truoc` và cho thầy cô xem ảnh trước khi dựng thật.
- Nhạc nền (thầy cô đồng ý): tải bằng `tools\vi\tim_nhac.py "<từ khoá>" -o projects\_video\<tên>\nhac` (CC0/CC BY, nguồn tự ghi vào `nhac/nguon.json`), ghi `nhac-nen: <file>`, gửi thầy cô nghe thử trước khi dựng. `error.step` là `mang` thì kiểm mạng, chạy lại tối đa một lần. Không dùng nhạc không rõ nguồn.
- Nền `ve:` hoặc `nhan-vat: ve:` (ảnh AI): chạy bước anh_ai.py ke-hoach (`tools\vi\anh_ai.py <thư_mục> ke-hoach`), rồi dùng công cụ tạo ảnh của Antigravity vẽ từng mục trong `anh/ai/ke-hoach.json` (nhân vật mẫu trước, tư thế kèm ảnh mẫu, nền xanh lá thuần #00FF00 không bóng), lưu đúng tên vào `anh/ai/goc/`. Được phép dùng công cụ này cho việc đó; không có công cụ tạo ảnh thì dùng `nen: mau/<tên>` và `nhan-vat: nguoi-que`.
- Có ảnh AI thì luôn chạy bước anh_ai.py nhan (`tools\vi\anh_ai.py <thư_mục> nhan --mo-hinh "<mô hình>"`), rồi `video_ma.py --xem-truoc` và chờ thầy cô duyệt trước khi dựng thật. Không tự viết `anh/ai/nguon.json`.
- Hình phải khớp lời đọc: tắt tiếng vẫn đoán được mỗi cảnh nói gì. Cảnh `ke-chuyen` trên nền mẫu phải có `the` nêu ý chính hoặc con số của lời; chọn nền mẫu theo bối cảnh trong lời; nền `ve:` tả đúng sự vật, hành động trong lời; tư thế theo cảm xúc của câu; không quá hai cảnh `ke-chuyen` liền nhau. `video_ma.py` cảnh báo các chỗ này: sửa `video.md` trước khi dựng thật.
- Chữ trên video không bao giờ nằm trong ảnh: ảnh AI có chữ thì vẽ lại; tiêu đề, thẻ, phụ đề do công cụ viết.
- Câu hỏi và đáp án của cảnh `cau-hoi` phải được thầy cô duyệt. Sau khi dựng, nhắc thầy cô nghe thử tiếng hiệu ứng và nhạc; ồn thì ghi `am-thanh: khong` hoặc bỏ `nhac-nen`.

## Các việc khác

Chạy lệnh trên Windows, kiểm tra môi trường trước lệnh Python đầu tiên, làm video, soạn đề, soạn giáo án, video giải thích: đọc `AGENTS.vi.md` trước khi làm.

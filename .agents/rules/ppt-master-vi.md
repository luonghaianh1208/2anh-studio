---
trigger: always_on
---

# 2Anh Studio — luật luôn áp dụng

Khi làm việc trong repo này, luôn đọc và áp dụng @../../AGENTS.md và @../../AGENTS.vi.md.

Antigravity không chép file nhắc bằng `@`, nên điểm bắt buộc ghi thẳng dưới đây; chi tiết ở `AGENTS.vi.md`, `docs/vi/tro-ly/`.

## Hỏi thầy cô trước khi làm

Người dùng viết tiếng Việt, bối cảnh trường học hoặc Đoàn, yêu cầu thuộc một trong 11 loại việc ở bảng dưới (văn bản hành chính: cả cơ quan ngoài trường như UBND xã, phòng ban): trước mọi lệnh tạo bài, làm đúng ba bước.

1. Đọc `docs/vi/tro-ly/quy-trinh-hoi.md`, rồi file hướng dẫn của loại việc.
2. Gửi thầy cô một tin nhắn hỏi theo hai file đó.
3. Dừng và chờ thầy cô trả lời. Lúc chờ không chạy `project_manager.py init`, không tra cứu, không tìm hay tạo ảnh, không viết SVG hay file Word.

- Lượt hỏi không trái `SKILL.md`: chỉ thêm tài liệu nguồn (brief); bước xác nhận của upstream giữ nguyên.
- Turbo Mode, Always Proceed hay quyền chạy lệnh không cần duyệt không phải yêu cầu tạo nhanh, không bỏ được lượt hỏi.
- Có "không cần hỏi lại" hoặc "không hỏi gì": không hỏi câu nào. Chỉ "tạo nhanh", "làm nhanh": vẫn hỏi các câu còn thiếu trong mục "Tạo nhanh" của file loại việc. Cả hai đọc mục "Tạo nhanh" của `docs/vi/tro-ly/quy-trinh-hoi.md` và ghi brief.
- Trước khi hỏi, kiểm tra máy theo `AGENTS.vi.md` mục 9 (`tools/vi/doctor.py --no-smoke --json`), báo máy chưa cài xong nếu cần.
- Chữ "giáo án" một mình: hỏi đúng một câu "Thầy cô cần file Word kế hoạch bài dạy (giáo án 5512), hay slide trình chiếu cho bài này?" trước khi làm gì khác.
- Chữ "làm video" hoặc "xuất video" một mình: hỏi đúng một câu "Thầy cô muốn làm video từ bài giảng slide đã có, hay dựng video giải thích mới từ nội dung chữ?" trước khi làm gì khác. Slide thì theo `docs/vi/tro-ly/video-bai-giang.md`; video mới thì theo `docs/vi/tro-ly/video-giai-thich.md`.
- Chữ "báo cáo" hoặc "kế hoạch" một mình: hỏi đúng một câu "Thầy cô cần văn bản Word đúng thể thức Nghị định 30, hay slide trình chiếu?" trước khi làm gì khác. Word thì theo `docs/vi/tro-ly/van-ban-hanh-chinh.md`.
- Khớp hai dòng: từ chỉ dạng đầu ra thắng "thông báo", "quyết định" ("poster", "ảnh đăng", "slide", "trình chiếu", "video"); tên loại văn bản đứng ngay sau động từ soạn thảo thắng các từ chủ đề ("soạn công văn cử đi tập huấn" là văn bản hành chính).
- Soạn đề KHTN tiếng Anh, giáo án, văn bản hành chính có tài liệu gửi kèm: đọc trước rồi mới hỏi (`AGENTS.vi.md` mục 12, 13, 16).

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
| Soạn văn bản hành chính (Nghị định 30) | "công văn", "tờ trình", "quyết định", "thông báo", "giấy mời", "biên bản", "văn bản hành chính", "Nghị định 30", "ND30", "đúng thể thức" | `docs/vi/tro-ly/van-ban-hanh-chinh.md` |

## Ảnh minh hoạ

Bài mới thuộc 5 loại việc tạo PPTX ở bảng trên (không áp dụng làm đẹp hay sửa PPTX có sẵn), kể cả tạo nhanh: không làm bài toàn chữ, nhưng không chèn ảnh trang trí cho đủ số.

- Sự vật, hiện tượng, dụng cụ, địa danh, nhân vật có thật: nguồn `web` từ đầu, tìm bằng `skills/ppt-master/scripts/image_search.py` (không cần khoá). Quá trình, cấu tạo: vẽ sơ đồ trên slide.
- Thiếu khoá API tạo ảnh không phải lý do bỏ ảnh `web`; không mở file cấu hình dò khoá.
- Chi tiết: mục "Ảnh minh hoạ" của `docs/vi/tro-ly/quy-trinh-hoi.md`.

## Mật độ chữ

Bài mới thuộc Bài giảng, Báo cáo – tổng kết, Hoạt động Đoàn – sự kiện, Tập huấn/workshop hỏi mật độ chữ: ít chữ → chế độ đọc `presentation`, vừa → `balanced`, nhiều chữ → `text`. Chưa chọn: báo cáo dùng vừa, ba loại còn lại dùng ít chữ.

- Ít chữ: mỗi trang một ý, cụm ngắn, khoảng 5 dòng; giải thích vào lời giảng (ghi chú người trình bày). Không bỏ thông tin: không vừa thì chia trang.
- Làm đẹp slide có sẵn mà muốn ít chữ hơn, rút gọn, tách hay gộp trang: không dùng chế độ làm đẹp (Beautify giữ nguyên văn), mà tạo mới từ file đó như tài liệu nguồn; báo trước một dòng.
- Chi tiết: mục "Mật độ chữ" của `docs/vi/tro-ly/quy-trinh-hoi.md`.

## Hiệu ứng

Bài mới thuộc bốn loại ở mục Mật độ chữ hỏi mức hiệu ứng (không, vừa, nhiều); chưa chọn thì dùng vừa. Không áp dụng cho làm đẹp hay sửa PPTX có sẵn.

- Đọc `docs/vi/tro-ly/hieu-ung-lop-hoc.md` trước khi lên danh sách trang (Morph cần hai trang vẽ sẵn, hiện từng ý cần mỗi ý một `<g id>`).
- Mức vừa, nhiều: chạy `customize-animations` của upstream, kể cả tạo nhanh; không thêm chuyển động cho đủ tỉ lệ.
- Sau khi xuất PPTX, chạy `tools\vi\kiem_hieu_ung.py <file.pptx> --muc khong|vua|nhieu`. Không đạt thì sửa và kiểm lại đúng một lần.
- Video bài giảng: không dùng `on-click` hay `trigger_shape`. Chép `animations.json` thành `animations_video.json`, đổi sang tự chạy, xuất với `--animation-config animations_video.json`, kiểm `_narrated.pptx` bằng `--video` trước khi dựng.

## Thí nghiệm ảo

Đầu ra là HTML chạy không cần mạng và phiếu học tập Word, không phải PPTX.

- Đọc `docs/vi/tro-ly/thi-nghiem-ao.md` và `docs/vi/tro-ly/mo-hinh-thi-nghiem.md`, hỏi một lượt, viết `thi-nghiem.md` trong `projects/_thi-nghiem/<tên>/`, rồi chạy `tools\vi\thi_nghiem.py <thư_mục>`.
- Không viết file HTML bằng tay, không chèn thư viện hay địa chỉ web. Ngoài danh mục thì viết mô hình mới theo khuôn (công thức, điều kiện áp dụng, bảng số kiểm).
- Đọc nguyên văn `can-soat.md`; mô hình do AI viết thì thầy cô soát công thức trước khi dùng.

## Video giải thích

Đầu ra là video MP4 dựng từ nội dung chữ, không phải PPTX.

- Đọc `docs/vi/tro-ly/video-giai-thich.md` và `docs/vi/tro-ly/canh-video.md`, hỏi một lượt, viết `video.md` trong `projects/_video/<tên>/`.
- Chạy `tools\vi\video_ma.py <thư_mục> --plan-only`, rồi `--xem-truoc` xem ảnh từng cảnh, rồi mới dựng thật; báo trước dựng mất khoảng 1,5 lần thời lượng (dọc cắt dán khoảng 2 lần).
- Không viết HTML hay ảnh cảnh bằng tay, không tự chạy FFmpeg. `error.step` là `chromium` thì hỏi trước khi tải Chromium (150–300 MB).
- Ảnh thật (thầy cô đồng ý): tải bằng `skills/ppt-master/scripts/image_search.py "<từ khoá>" --filename <tên>.jpg -o projects\_video\<tên>\anh` trước `--plan-only`; rồi bắt buộc `--xem-truoc`, cho thầy cô xem ảnh trước khi dựng thật.
- Nhạc nền (thầy cô đồng ý): tải bằng `tools\vi\tim_nhac.py "<từ khoá>" -o projects\_video\<tên>\nhac` (CC0/CC BY, nguồn tự ghi vào `nhac/nguon.json`), ghi `nhac-nen: <file>`, gửi thầy cô nghe thử trước khi dựng. `error.step` là `mang` thì kiểm mạng, chạy lại tối đa một lần. Không dùng nhạc không rõ nguồn.
- Nền `ve:` hoặc `nhan-vat: ve:` (ảnh AI): chạy bước anh_ai.py ke-hoach (`tools\vi\anh_ai.py <thư_mục> ke-hoach`), rồi dùng công cụ tạo ảnh của Antigravity (được phép) vẽ từng mục trong `anh/ai/ke-hoach.json` (nhân vật mẫu trước, tư thế kèm ảnh mẫu, nền #00FF00 thuần không bóng), lưu đúng tên vào `anh/ai/goc/`; không có công cụ thì dùng `nen: mau/<tên>`, `nhan-vat: nguoi-que`.
- Có ảnh AI thì luôn chạy bước anh_ai.py nhan (`tools\vi\anh_ai.py <thư_mục> nhan --mo-hinh "<mô hình>"`), rồi `video_ma.py --xem-truoc` và chờ thầy cô duyệt trước khi dựng thật. Không tự viết `anh/ai/nguon.json`.
- Hình phải khớp lời đọc: tắt tiếng vẫn đoán được mỗi cảnh nói gì. `ke-chuyen` trên nền mẫu có `the` nêu ý chính hoặc con số; nền theo bối cảnh; nền `ve:` tả đúng sự vật, hành động; tư thế theo cảm xúc; không quá hai `ke-chuyen` liền nhau. `video_ma.py` cảnh báo thì sửa `video.md` trước khi dựng thật.
- Chữ trên video không bao giờ nằm trong ảnh: ảnh AI có chữ thì vẽ lại; tiêu đề, thẻ, phụ đề do công cụ viết.
- Câu hỏi, đáp án cảnh `cau-hoi` phải được thầy cô duyệt. Dựng xong, nhắc nghe thử tiếng hiệu ứng và nhạc; ồn thì ghi `am-thanh: khong` hoặc bỏ `nhac-nen`.

## Văn bản hành chính

Đầu ra là file Word đúng thể thức Nghị định 30 (`van-ban.docx`) và `kiem-tra.md`, không phải PPTX.

- Đọc `docs/vi/tro-ly/van-ban-hanh-chinh.md`, hỏi một lượt 7 câu, viết `noi-dung.json` trong `projects/_van-ban/<tên>/` theo ví dụ đúng loại ở `tools/vi/nd30/examples/`, rồi chạy `tools\vi\van_ban.py "projects\_van-ban\<tên>"`.
- Không bịa: số, ký hiệu, ngày, người ký, căn cứ, số tiền, số liệu chưa nêu thì ghi `[CẦN BỔ SUNG: …]`. Còn ô thì `ban_nhap` là `true`: báo rõ là bản nháp, đọc từng ô và dòng "Thầy cô đối chiếu" trong `warnings`.
- Không sửa file trong `tools/vi/nd30/`, không viết file Word cách khác, không đổi profile để qua bộ kiểm. Văn bản Đảng, Đoàn không hỗ trợ.

## Các việc khác

Lệnh trên Windows, kiểm tra môi trường, video, đề, giáo án, văn bản: đọc `AGENTS.vi.md` trước.

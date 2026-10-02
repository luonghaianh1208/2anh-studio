---
trigger: always_on
---

# 2Anh Studio — luật luôn áp dụng

Khi làm việc trong repo này, luôn đọc và áp dụng @../../AGENTS.md và @../../AGENTS.vi.md.

Antigravity không chép file nhắc bằng `@`, nên điểm bắt buộc ghi thẳng dưới đây; chi tiết ở `AGENTS.vi.md`, `docs/vi/tro-ly/`.

## Hỏi thầy cô trước khi làm

Người dùng viết tiếng Việt, yêu cầu thuộc một trong 11 loại việc ở bảng dưới (trường học, Đoàn; văn bản hành chính cả UBND xã, phòng ban; video giải thích mọi ngành): trước mọi lệnh tạo bài, làm đúng ba bước.

1. Đọc `docs/vi/tro-ly/quy-trinh-hoi.md`, rồi file hướng dẫn của loại việc.
2. Gửi thầy cô một tin nhắn hỏi theo hai file đó.
3. Dừng và chờ thầy cô trả lời. Lúc chờ không chạy `project_manager.py init`, không tra cứu, không tìm hay tạo ảnh, không viết SVG hay file Word.

- Lượt hỏi không trái `SKILL.md`: chỉ thêm brief; bước xác nhận của upstream giữ nguyên.
- Video giải thích là ngoại lệ: có chủ đề thì không hỏi, không chờ (mục Video giải thích).
- Turbo Mode, Always Proceed hay quyền chạy lệnh không phải yêu cầu tạo nhanh, không bỏ được lượt hỏi.
- "không cần hỏi lại", "không hỏi gì": không hỏi câu nào. Chỉ "tạo nhanh", "làm nhanh": vẫn hỏi các câu còn thiếu. Cả hai theo mục "Tạo nhanh" của `quy-trinh-hoi.md` và ghi brief.
- Trước khi hỏi, chạy `tools/vi/doctor.py --no-smoke --json` (`AGENTS.vi.md` mục 9), báo máy chưa cài xong nếu cần.
- Một chữ mơ hồ đứng một mình: hỏi đúng một câu trước khi làm gì khác.
  - "giáo án": "Thầy cô cần file Word kế hoạch bài dạy (giáo án 5512), hay slide trình chiếu cho bài này?"
  - "làm video", "xuất video": "Thầy cô muốn làm video từ bài giảng slide đã có, hay dựng video giải thích mới từ nội dung chữ?" (slide: `video-bai-giang.md`; mới: `video-giai-thich.md`).
  - "báo cáo", "kế hoạch": "Thầy cô cần văn bản Word đúng thể thức Nghị định 30, hay slide trình chiếu?"
- Khớp hai dòng: từ chỉ dạng đầu ra thắng "thông báo", "quyết định" ("poster", "slide", "video"); tên loại văn bản đứng ngay sau động từ soạn thảo thắng các từ chủ đề ("soạn công văn cử đi tập huấn" là văn bản hành chính).
- Đề tiếng Anh, giáo án, văn bản hành chính có tài liệu gửi kèm: đọc trước rồi mới hỏi (`AGENTS.vi.md` mục 12, 13, 16).

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
| Video giải thích dựng bằng mã | "video giải thích", "video vox", "kiểu vox", "video viết tay", "video whiteboard", "video hoạt hình chữ", "video kể chuyện", "video dọc", "video cắt dán" | `docs/vi/tro-ly/video-giai-thich.md` |
| Soạn văn bản hành chính (Nghị định 30) | "công văn", "tờ trình", "quyết định", "thông báo", "giấy mời", "biên bản", "văn bản hành chính", "Nghị định 30", "ND30", "đúng thể thức" | `docs/vi/tro-ly/van-ban-hanh-chinh.md` |

## Ảnh minh hoạ

Bài mới thuộc 5 loại việc tạo PPTX ở bảng trên, kể cả tạo nhanh (không áp dụng làm đẹp, sửa PPTX có sẵn): không làm bài toàn chữ, nhưng không chèn ảnh trang trí cho đủ số. Sự vật, địa danh, nhân vật có thật: nguồn `web`, tìm bằng `skills/ppt-master/scripts/image_search.py` (không cần khoá); quá trình, cấu tạo: vẽ sơ đồ. Thiếu khoá tạo ảnh không phải lý do bỏ ảnh `web`.

## Mật độ chữ

Bài giảng, Báo cáo – tổng kết, Hoạt động Đoàn – sự kiện, Tập huấn/workshop hỏi mật độ chữ: ít chữ → `presentation`, vừa → `balanced`, nhiều chữ → `text`; chưa chọn thì báo cáo vừa, ba loại kia ít chữ. Ít chữ: mỗi trang một ý, khoảng 5 dòng, giải thích vào lời giảng; không vừa thì chia trang, không bỏ thông tin. Muốn làm đẹp slide có sẵn mà ít chữ hơn, tách hay gộp trang: không dùng Beautify, tạo mới từ file đó như tài liệu nguồn.

## Hiệu ứng

Bốn loại ở mục Mật độ chữ hỏi mức hiệu ứng (không, vừa, nhiều; chưa chọn thì vừa). Không áp dụng cho làm đẹp hay sửa PPTX có sẵn.

- Đọc `docs/vi/tro-ly/hieu-ung-lop-hoc.md` trước khi lên danh sách trang. Mức vừa, nhiều: chạy `customize-animations`, kể cả tạo nhanh.
- Xuất xong, chạy `tools\vi\kiem_hieu_ung.py <file.pptx> --muc khong|vua|nhieu`; không đạt thì sửa, kiểm lại đúng một lần.
- Video bài giảng: không dùng `on-click`, `trigger_shape`; xuất với `animations_video.json` (tự chạy) và kiểm `_narrated.pptx` bằng `--video` trước khi dựng.

## Thí nghiệm ảo

HTML chạy không cần mạng và phiếu Word, không phải PPTX. Đọc `docs/vi/tro-ly/thi-nghiem-ao.md`, hỏi một lượt, viết `thi-nghiem.md` trong `projects/_thi-nghiem/<tên>/`, chạy `tools\vi\thi_nghiem.py <thư_mục>`. Không viết file HTML bằng tay, không chèn thư viện hay địa chỉ web. Đọc nguyên văn `can-soat.md`; mô hình mới thì thầy cô soát công thức.

## Video giải thích

Video MP4 kiểu Vox, không phải PPTX; cho mọi ngành, không theo khuôn bài giảng. Đọc `docs/vi/tro-ly/video-giai-thich.md` và `nhip-vox.md`. Chỉ hỏi khi thiếu chủ đề hay nội dung; không dừng chờ duyệt, trừ khi được xin xem kịch bản trước.

- Quỹ từ theo `thoi-luong` (60 giây ≈ 230 từ). Không bịa số liệu: số nào cũng có `nguon`.
- Hình phải khớp lời đọc: cảnh mở bằng nhãn, cụm hình ở `@dau`; chữ trên hình ≤ 6 từ, ảnh AI không có chữ.
- `video_ma.py --plan-only` (sửa thời lượng, chưa cần ảnh) → `anh_vox.py` (ảnh tự vẽ: thêm `--cong-cu`, `--mo-hinh`) → `--xem-truoc` tự xem, tự sửa → dựng thật. Không viết HTML, ảnh cảnh bằng tay. Khoá ảnh chỉ qua `ANH_AI_KEY`, không ghi vào repo.
- Nhạc nền chỉ khi được xin: `tim_nhac.py`, ghi `nhac-nen`, nhắc nghe thử (`mang`: chạy lại một lần).

## Văn bản hành chính

File Word đúng Nghị định 30 và `kiem-tra.md`, không phải PPTX.

- Đọc `docs/vi/tro-ly/van-ban-hanh-chinh.md`, hỏi một lượt 7 câu, viết `noi-dung.json` trong `projects/_van-ban/<tên>/` theo khuôn `tools/vi/nd30/examples/` (không chép tên đơn vị: từ 1/7/2025 không còn cấp huyện), chạy `tools\vi\van_ban.py "projects\_van-ban\<tên>"`.
- Không bịa: số, ký hiệu, ngày, người ký, căn cứ, số tiền, số liệu chưa nêu thì ghi `[CẦN BỔ SUNG: …]`; còn ô thì báo rõ là bản nháp, đọc từng ô và dòng "Thầy cô đối chiếu".
- Không sửa `tools/vi/nd30/`, không viết file Word cách khác, không đổi profile để qua bộ kiểm. Văn bản Đảng, Đoàn không hỗ trợ.

## Các việc khác

Lệnh trên Windows, môi trường, video, đề, giáo án, văn bản: đọc `AGENTS.vi.md` trước.

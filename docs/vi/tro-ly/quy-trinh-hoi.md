# Quy trình hỏi thầy cô trước khi làm bài

File dành cho AI. Nó bổ sung ngữ cảnh cho quy trình tạo PPTX trong `skills/ppt-master/SKILL.md` và không thay thế bước nào của quy trình đó.

## Khi nào áp dụng

Áp dụng khi cả ba điều kiện đều đúng:

1. Người dùng viết tiếng Việt.
2. Yêu cầu thuộc một trong 10 loại việc dưới đây: câu lệnh có dấu hiệu trong bảng hoặc nói rõ loại việc.
3. Bối cảnh là trường học hoặc Đoàn (ví dụ lớp, môn học, tổ chuyên môn, học sinh, phụ huynh, giáo viên, đoàn viên).

| Loại việc | Dấu hiệu nhận biết | File hướng dẫn |
|---|---|---|
| Bài giảng | "bài giảng", "giáo án", "tiết học", "bài dạy", tên môn kèm lớp | [bai-giang.md](bai-giang.md) |
| Báo cáo – tổng kết | "báo cáo", "sơ kết", "tổng kết", "thi đua", "hội nghị viên chức" | [bao-cao-tong-ket.md](bao-cao-tong-ket.md) |
| Hoạt động Đoàn – sự kiện | "Đoàn", "chi đoàn", "cuộc thi", "sự kiện", "lễ kỷ niệm", "trao giải" | [hoat-dong-doan.md](hoat-dong-doan.md) |
| Poster/ấn phẩm Zalo – Facebook | "poster", "ảnh đăng Zalo", "bài đăng Facebook", "story", "TikTok" | [poster-mang-xa-hoi.md](poster-mang-xa-hoi.md) |
| Tập huấn/workshop | "tập huấn", "bồi dưỡng", "sinh hoạt chuyên môn", "workshop", "chia sẻ chuyên đề" | [tap-huan-workshop.md](tap-huan-workshop.md) |
| Video bài giảng | "làm video", "xuất video", "lồng tiếng", "video bài giảng" | [video-bai-giang.md](video-bai-giang.md) |
| Soạn đề KHTN tiếng Anh | "soạn đề", "đề kiểm tra", "đề tiếng Anh", "đề KHTN", "chuyển đề sang tiếng Anh" | [de-khtn-tieng-anh.md](de-khtn-tieng-anh.md) |
| Soạn giáo án tích hợp năng lực số và AI | "kế hoạch bài dạy", "KHBD", "giáo án Word", "giáo án 5512" | [giao-an.md](giao-an.md) |
| Thí nghiệm ảo | "thí nghiệm ảo", "mô phỏng thí nghiệm", "mô phỏng tương tác" | [thi-nghiem-ao.md](thi-nghiem-ao.md) |
| Video giải thích dựng bằng mã | "video giải thích", "video viết tay", "video whiteboard", "video hoạt hình chữ" | [video-giai-thich.md](video-giai-thich.md) |

- Chữ "làm video" hoặc "xuất video" một mình là ca mơ hồ thứ hai: nó có thể là video từ bài giảng slide, cũng có thể là video giải thích mới. Hỏi đúng một câu trước khi làm gì khác: "Thầy cô muốn làm video từ bài giảng slide đã có, hay dựng video giải thích mới từ nội dung chữ?" Trả lời slide thì dùng video-bai-giang.md; trả lời video mới thì dùng video-giai-thich.md. Câu lệnh có "video bài giảng" hoặc "lồng tiếng" là dòng Video bài giảng; có một cụm của dòng Video giải thích là loại việc đó, không hỏi câu này.
- Chữ "giáo án" một mình là ca mơ hồ đã biết: nó có thể là file Word kế hoạch bài dạy, cũng có thể là slide. Hỏi đúng một câu trước khi làm gì khác: "Thầy cô cần file Word kế hoạch bài dạy (giáo án 5512), hay slide trình chiếu cho bài này?" Trả lời Word thì dùng giao-an.md; trả lời slide thì dùng bai-giang.md. Câu lệnh có "kế hoạch bài dạy", "KHBD", "giáo án Word" hoặc "giáo án 5512" là rõ ràng: dùng giao-an.md và không hỏi câu này, dù cụm đó chứa chữ "bài dạy" hay "giáo án" của dòng Bài giảng.
- Chỉ xếp vào một loại khi câu lệnh có dấu hiệu trong bảng hoặc nói rõ loại việc. Bối cảnh trường học hay Đoàn một mình không đủ để xếp loại (ví dụ giới thiệu trường, giới thiệu một phòng chức năng): coi là yêu cầu không thuộc loại nào. Chữ "Đoàn" hay "chi đoàn" chỉ là dấu hiệu khi đi kèm một hoạt động (chương trình, cuộc thi, sự kiện, lễ kỷ niệm, trao giải).
- Loại việc "Soạn đề KHTN tiếng Anh" không tạo PPTX; nó ghi brief như các loại khác nhưng không đi vào quy trình của upstream. Các bước dành riêng cho PPTX ở trên (dòng chốt cách xác nhận cuối tin nhắn hỏi, đặt tên brief theo dự án PPTX rồi import vào dự án, `project_manager.py import-sources`, bước xác nhận của upstream, `quick-generate.md`) không áp dụng cho loại việc này; làm theo docs/vi/tro-ly/de-khtn-tieng-anh.md.
- Loại việc "Soạn giáo án tích hợp năng lực số và AI" không tạo PPTX; nó ghi brief như các loại khác nhưng không đi vào quy trình của upstream. Các bước chỉ dành cho PPTX (dòng chốt cách xác nhận cuối tin nhắn hỏi, `import-sources`, bước xác nhận của upstream, `quick-generate.md`) không áp dụng; làm theo mục "Ghi vào brief" của docs/vi/tro-ly/giao-an.md.
- Loại việc "Thí nghiệm ảo" không tạo PPTX; nó ghi brief như các loại khác nhưng không đi vào quy trình của upstream. Các bước chỉ dành cho PPTX (dòng chốt cách xác nhận cuối tin nhắn hỏi, `import-sources`, bước xác nhận của upstream, `quick-generate.md`) và mục "Ảnh minh hoạ" không áp dụng; làm theo mục "Ghi vào brief" của docs/vi/tro-ly/thi-nghiem-ao.md.
- Loại việc "Video giải thích dựng bằng mã" không tạo PPTX; nó ghi brief như các loại khác nhưng không đi vào quy trình của upstream. `import-sources`, bước xác nhận của upstream, `quick-generate.md` và mục "Ảnh minh hoạ" không áp dụng; dòng chốt cách xác nhận vẫn giữ nhưng luôn ở dạng khung chat, để thầy cô duyệt danh sách cảnh trước khi dựng. Làm theo mục "Ghi vào brief" của docs/vi/tro-ly/video-giai-thich.md.
- Yêu cầu không thuộc loại nào, hoặc có từ khoá nhưng không phải bối cảnh trường học hay Đoàn (ví dụ báo cáo doanh thu của công ty, giới thiệu sản phẩm): không dùng phần nào của file này (không tìm hay nhắc tới hồ sơ đơn vị, không viết brief, không dùng dạng câu hỏi kèm "Gợi ý:" hay dòng chốt cách xác nhận), làm theo `SKILL.md` như bình thường.
- Có dấu hiệu nhưng không rõ thuộc loại nào, hoặc thuộc hai loại: hỏi đúng một câu hỏi chọn loại việc (không phải chọn quy trình của upstream), kèm gợi ý loại gần nhất.
- Người dùng viết tiếng Anh hoặc ngôn ngữ khác: không dùng bộ câu hỏi này.

## Thứ tự ưu tiên

- `skills/ppt-master/SKILL.md` và `AGENTS.md` luôn được ưu tiên khi có mâu thuẫn với file này.
- Lượt hỏi ở đây diễn ra trước quy trình của upstream và chỉ tạo thêm tài liệu nguồn. Bước xác nhận của upstream vẫn bắt buộc, trừ khi người dùng yêu cầu tạo nhanh.
- Không sửa, bỏ qua hay tìm cách "sửa chữa" `skills/ppt-master/scripts/attribution_guard.py`.

## Hồ sơ đơn vị

- Hồ sơ lưu ở `projects/_ho-so-don-vi.md`, theo mẫu [mau-ho-so-don-vi.md](mau-ho-so-don-vi.md). Thư mục `projects/` không được đưa lên GitHub.
- Chưa có hồ sơ, hoặc hồ sơ thiếu mục: hỏi các mục còn thiếu trong cùng tin nhắn với câu hỏi của loại việc.
- Khi hỏi hồ sơ, không gợi ý sẵn tên đơn vị, họ tên người trình bày hay logo: để trống cho thầy cô điền. Không lấy các tên này từ README, NOTICE, bộ nhớ của AI hay dự án khác. Chỉ gợi ý cấp học khi suy ra được từ câu lệnh (ví dụ lớp 10 → THPT) và gợi ý một màu chủ đạo. Trả lời "đồng ý" không điền được mục chưa có gợi ý; mục nào thầy cô chưa cho biết thì để trống, không tự điền.
- Không hỏi riêng mục "Cách xác nhận"; ghi mục này theo câu trả lời của thầy cô cho dòng chốt cách xác nhận (xem mục "Cách hỏi").
- Đã có hồ sơ: mở đầu lượt hỏi bằng dòng "Hồ sơ hiện tại: <Đơn vị> — <Người trình bày>. Dùng tiếp?". Luôn có dòng này, vì nhiều thầy cô có thể dùng chung một máy.
- Thầy cô muốn đổi thông tin (ví dụ "đổi màu", "đổi trường"): sửa hồ sơ, ghi ngày hôm nay vào mục "Cập nhật", báo lại một dòng tóm tắt.
- Không bao giờ import file hồ sơ vào dự án. Chỉ chép các mục cần dùng sang brief.
- Đường dẫn logo không tồn tại: báo cho thầy cô, xin đường dẫn khác hoặc làm tiếp không dùng logo.

## Cách hỏi

- Xưng "em"; gọi "thầy cô" (hoặc "thầy/cô") khi chưa biết.
- Gửi một tin nhắn duy nhất, rồi dừng và chờ thầy cô trả lời. Trong lúc chờ không khởi tạo dự án, không tra cứu, không soạn slide.
- Hỏi tối đa 7 câu bắt buộc của loại việc. Phần hồ sơ đơn vị ở lần đầu không tính vào 7 câu này.
- Đánh số từng câu bằng số thường ở đầu dòng, ví dụ "1. Nội dung câu hỏi" (không in đậm số thứ tự). Giữ nguyên từ khoá trong câu hỏi bắt buộc của file loại việc (ví dụ "kỳ báo cáo", "đối tượng tham dự"), không diễn đạt lại bằng từ khác. Mỗi câu kèm gợi ý cụ thể để thầy cô chỉ cần trả lời "đồng ý" hoặc sửa. Quy tắc gợi ý này dành cho các câu hỏi đánh số của loại việc, không áp dụng cho phần hồ sơ đơn vị.
- Chỉ hỏi thông tin mà chỉ thầy cô biết. Không hỏi kiến thức của bài học hay dữ kiện AI tự tra cứu được.
- Câu hỏi tuỳ chọn chỉ thêm khi yêu cầu có liên quan. Câu hỏi tuỳ chọn có thể thay cho câu hỏi bắt buộc mà câu lệnh đã trả lời đủ; tổng số câu vẫn không quá 7.
- Kết thúc tin nhắn bằng dòng chốt cách xác nhận, theo mục "Cách xác nhận" trong hồ sơ (chưa có thì mặc định khung chat):
  - Khung chat: "Ở bước xác nhận, em sẽ tóm tắt trong khung chat để thầy cô duyệt, không mở trang web. Thầy cô đồng ý nhé?"
  - Trang web: "Ở bước xác nhận, em sẽ mở trang web xác nhận để thầy cô duyệt. Thầy cô đồng ý nhé?"
- Thầy cô đồng ý xác nhận trong khung chat ngay trong lần chạy này là chỉ dẫn hợp lệ để dùng nhánh khung chat của `skills/ppt-master/references/confirm-surface.md` (mục 1).
- Dòng chốt cách xác nhận không áp quy tắc "trả lời thiếu → dùng gợi ý". Mục "Cách xác nhận" trong hồ sơ chỉ chọn câu chữ của dòng chốt, không phải chỉ dẫn cho lần chạy này. Thầy cô không trả lời dòng chốt: trước khi mở trang web ở bước xác nhận, hỏi lại đúng một câu trong khung chat về cách xác nhận.
- Ở bước xác nhận, nếu thầy cô nói "AI tự quyết" hoặc giao hẳn cho AI: dùng nhánh ủy quyền trong mục 1 của `skills/ppt-master/references/confirm-surface.md` (AI chốt đề xuất và đưa một bản tóm tắt cuối).
- Thầy cô muốn dùng trang web xác nhận: dùng nhánh trang web mặc định của upstream; brief vẫn được dùng để điền sẵn đề xuất.
- Thầy cô trả lời thiếu câu hỏi đánh số: dùng gợi ý và ghi kèm "(AI đề xuất, chưa duyệt)" trong brief. Chỉ hỏi lại câu bắt buộc không thể đoán (ví dụ tên bài, loại báo cáo), và hỏi lại tối đa một lần.

## Ảnh minh hoạ

Mục này làm rõ, bằng ví dụ ở trường học, các quy tắc ảnh sẵn có của upstream (`skills/ppt-master/references/plan-core.md` mục 5); upstream vẫn là nơi quyết định.

Áp dụng khi tạo bài mới cho 5 loại việc tạo PPTX: Bài giảng, Báo cáo – tổng kết, Hoạt động Đoàn – sự kiện, Poster/ấn phẩm Zalo – Facebook, Tập huấn/workshop; cả khi tạo nhanh. Không áp dụng cho làm đẹp slide có sẵn (Beautify), sửa PPTX có sẵn, tạo template, dựng lại từ ảnh chụp slide, Soạn đề KHTN tiếng Anh, Soạn giáo án, Thí nghiệm ảo, Video bài giảng và Video giải thích.

- Thầy cô không dặn "không dùng ảnh" thì không làm bài toàn chữ; biểu đồ và bảng số liệu cũng tính. Không chèn ảnh trang trí chỉ để trang nào cũng có ảnh.
- Khi lên danh sách trang, chọn nguồn ảnh cho từng trang:
  - Sự vật, chất, hiện tượng, dụng cụ và thiết bị thí nghiệm, địa danh, nhân vật, sự kiện lịch sử có thật mà học sinh hay người nghe cần nhận ra: nguồn `web`, tìm bằng `skills/ppt-master/scripts/image_search.py` (Openverse, Wikimedia, không cần khoá API), từ khoá tiếng Anh cụ thể 1–4 từ. Ảnh thầy cô gửi thì dùng ảnh đó trước.
  - Hoạt động, sự kiện riêng của trường hay chi đoàn: dùng ảnh thầy cô gửi; không có thì dùng ảnh minh hoạ AI hoặc sơ đồ, không lấy ảnh trên mạng thay cho ảnh thật của đơn vị.
  - Cảnh minh hoạ không có thật, nhân vật hoạt hình, ảnh nền cách điệu: nguồn `ai` bằng `skills/ppt-master/scripts/image_gen.py`, đường `auto`.
  - Quá trình, cấu tạo, chu trình, sơ đồ thí nghiệm, so sánh: sơ đồ vẽ trực tiếp trên slide.
- Không mở file cấu hình hay dò xem máy có khoá API: thiếu khoá tạo ảnh không phải lý do bỏ ảnh `web`. Việc tạo ảnh AI thất bại thì xử lý đúng như upstream (thay bằng sơ đồ hoặc ảnh không phải AI đã chuẩn bị, không thêm nguồn mới); vì vậy các trang cần ảnh thật phải được lên kế hoạch nguồn `web` ngay từ đầu.
- Poster một ảnh: ảnh đó có ảnh thật, ảnh minh hoạ hoặc sơ đồ, không chỉ có chữ trên nền màu.
- Ảnh cần ghi nguồn thì ghi dòng nguồn nhỏ trên slide theo trường `attribution_text` trong `image_sources.json`.
- Ghi vào brief, mục "AI đề xuất": nguồn ảnh dự kiến, kèm "(AI đề xuất, chưa duyệt)" khi thầy cô chưa nêu.
- Khi báo kết quả, nêu số trang có ảnh hoặc sơ đồ, và nhắc thầy cô soát ảnh tìm trên mạng trước khi dùng.

## Mật độ chữ

Mục này quy đổi lựa chọn của thầy cô về lượng chữ trên slide sang chế độ đọc của upstream (`skills/ppt-master/references/plan-core.md` mục 2, khoá `delivery_purpose`); upstream vẫn là nơi quyết định cách dựng.

Áp dụng khi tạo bài mới cho Bài giảng, Báo cáo – tổng kết, Hoạt động Đoàn – sự kiện, Tập huấn/workshop; cả khi tạo nhanh. Poster vốn ít chữ nên không hỏi.

| Thầy cô chọn | Chế độ đọc | Trên slide | Phần giải thích |
|---|---|---|---|
| ít chữ | `presentation` | mỗi trang một ý chính; từ khoá hoặc cụm ngắn, số lớn, ảnh hoặc sơ đồ; định hướng tối đa khoảng 5 dòng, không đoạn văn nào dài quá 2 dòng | vào lời giảng (ghi chú người trình bày), bật ghi chú |
| vừa | `balanced` | một ý chính kèm giải thích ngắn hoặc danh sách cần thiết; định hướng tối đa khoảng 7 dòng | phần chính trên slide, phần thêm vào lời giảng |
| nhiều chữ | `text` | câu đầy đủ, đoạn văn ngắn, bảng; dùng khi slide là tài liệu để đọc hoặc gửi đi | trên slide |

- Thầy cô chưa chọn: Bài giảng, Tập huấn/workshop, Hoạt động Đoàn – sự kiện dùng ít chữ; Báo cáo – tổng kết dùng vừa. Ghi vào brief kèm "(AI đề xuất, chưa duyệt)".
- Số dòng là định hướng để soát bài, không phải hạn mức cứng của upstream.
- Ít chữ là chuyển chữ đi chỗ khác, không bỏ thông tin: phần giải thích vào lời giảng; nội dung không vừa một trang thì chia thêm trang; quá trình, so sánh, số liệu thì vẽ sơ đồ hoặc biểu đồ thay cho câu chữ. Quy tắc của upstream vẫn giữ nguyên: không bỏ thông tin chỉ để vừa bố cục.
- Ở bước xác nhận của upstream, điền chế độ đọc đúng theo bảng; tạo nhanh thì áp chế độ đó khi tự quyết.
- Làm đẹp slide có sẵn (Beautify) giữ nguyên văn từng chữ và từng trang. Thầy cô muốn làm đẹp mà ít chữ hơn, rút gọn, tách hay gộp trang: không dùng Beautify, mà tạo mới từ file đó (file PPTX cũ làm tài liệu nguồn) theo loại việc phù hợp và mật độ chữ thầy cô chọn. Nói trước với thầy cô một dòng rằng bài sẽ được dựng lại, không chỉ đổi giao diện.

## Ghi brief và đưa vào dự án

1. Tạo hoặc cập nhật `projects/_ho-so-don-vi.md`.
2. Viết `projects/_brief-<tên_dự_án>.md` theo mẫu [mau-brief.md](mau-brief.md); `<tên_dự_án>` là tên sẽ dùng khi khởi tạo dự án.
   - Mục "Thầy cô yêu cầu": ghi đúng lời thầy cô, mỗi ý một dòng. Điều thầy cô không muốn có (điều cấm) thì ghi nguyên văn lời thầy cô.
   - Mục "AI đề xuất (thầy cô đã đồng ý)": mỗi dòng một gợi ý, ghi kèm "(thầy cô đồng ý)" khi thầy cô đã chấp nhận gợi ý đó, hoặc "(AI đề xuất, chưa duyệt)" khi thầy cô chưa nêu hoặc không trả lời (kể cả khi tạo nhanh).
   - Mục "Cấu trúc gợi ý" là điểm khởi đầu, không phải bố cục cuối, trừ khi thầy cô yêu cầu giữ nguyên.
3. Làm theo `SKILL.md`. Sau khi khởi tạo dự án, import brief bằng một lệnh riêng, không thêm `--copy`, để file được chuyển vào `sources/` của dự án:

   ```
   python skills/ppt-master/scripts/project_manager.py import-sources <đường_dẫn_dự_án> projects/_brief-<tên_dự_án>.md
   ```

4. Nếu có logo, import bằng một lệnh riêng khác. Chỉ thêm `--copy` khi file logo nằm trong thư mục `projects/`:

   ```
   python skills/ppt-master/scripts/project_manager.py import-sources <đường_dẫn_dự_án> <đường_dẫn_logo>
   ```

5. Ở bước xác nhận của upstream, dùng brief để điền sẵn đề xuất. Nếu thầy cô đã đồng ý xác nhận trong khung chat, trình bày và chờ duyệt trong khung chat.

## Tạo nhanh

- Áp dụng khi câu lệnh có "tạo nhanh", "làm nhanh", "không cần hỏi lại" hoặc "không hỏi gì".
- Không hỏi hồ sơ đơn vị. Nếu đã có `projects/_ho-so-don-vi.md` thì dùng; nếu chưa có thì ghi "(chưa có hồ sơ đơn vị)" dưới mục Đơn vị của brief.
- Câu lệnh có "không cần hỏi lại" hoặc "không hỏi gì" (kể cả khi có thêm "tạo nhanh"): không hỏi câu nào, kể cả khi còn thiếu thông tin, rồi viết brief và chạy chế độ tạo nhanh. Tin nhắn gửi thầy cô trong lượt này vẫn xưng "em", gọi "thầy cô".
- Câu lệnh chỉ có "tạo nhanh" hoặc "làm nhanh": hỏi đủ các câu còn thiếu trong mục "Tạo nhanh" của file loại việc, đánh số như mục "Cách hỏi", trong một tin nhắn. Nếu câu lệnh đã có đủ các thông tin đó thì không hỏi; không tự bỏ bớt câu vì nghĩ có thể đoán mặc định. Các câu này là điều kiện của lớp Việt, được hỏi trước khi chế độ tạo nhanh của upstream bắt đầu; chúng không phải điểm dừng trong lượt chạy tạo nhanh.
- Viết brief như mục trên; mọi mục thầy cô chưa nêu trong câu lệnh hoặc câu trả lời ghi kèm "(AI đề xuất, chưa duyệt)". Loại việc có dòng "Mức hiệu ứng" mà thầy cô chưa chọn thì ghi "Mức hiệu ứng: vừa (AI đề xuất, chưa duyệt)" và vẫn làm hiệu ứng theo `hieu-ung-lop-hoc.md`. Loại việc có dòng "Mật độ chữ" mà thầy cô chưa chọn thì ghi mức mặc định theo mục "Mật độ chữ" kèm "(AI đề xuất, chưa duyệt)" và áp chế độ đọc tương ứng.
- Chạy chế độ tạo nhanh của upstream theo `skills/ppt-master/workflows/profiles/quick-generate.md`, không có bước xác nhận.

## Đổi ý giữa chừng

- Thầy cô đổi thông tin trước bước xác nhận: cập nhật brief. Nếu brief đã được import, cập nhật file brief trong `sources/` của dự án.
- Đã qua bước xác nhận: nêu rõ thay đổi để thầy cô duyệt lại ở bước xác nhận của upstream; không tự áp dụng thay đổi khi thầy cô chưa duyệt.

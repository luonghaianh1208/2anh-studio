# Làm video giải thích

Video giải thích là một video ngắn kiểu **Vox**: nền giấy cắt dán nhiều lớp, ảnh cắt rời có viền giấy xé, thẻ số liệu, con dấu và chữ lớn hiện ra đúng lúc giọng đọc tiếng Việt nói tới, máy quay đẩy chậm và nghiêng nhẹ cho có chiều sâu, phụ đề tô màu từng từ. Dùng được cho mọi chủ đề: chuyện công sở, sức khoẻ, tiền bạc, công nghệ, pháp luật, bài học, sản phẩm. Khác "Làm video bài giảng" (dựng từ file slide có sẵn), video giải thích dựng thẳng từ **một chủ đề hay một đoạn nội dung**, không cần làm slide trước.

| File | Dùng để |
|---|---|
| `video.mp4` | Video Full HD: 1920×1080 khi khổ ngang (YouTube, Zalo, chiếu màn hình), 1080×1920 khi khổ dọc (TikTok, Reels, Shorts). Máy yếu có thể nhờ AI dựng bản 720 (1280×720 hoặc 720×1280) cho nhanh hơn |
| `video.md` | Kịch bản: lời đọc từng cảnh và những gì hiện ra trên hình; sửa file này rồi dựng lại là video đổi theo |
| `phu-de.srt` | Phụ đề để riêng, chỉ có khi chọn không in phụ đề lên hình |
| `anh\` | Ảnh AI vẽ (trong `anh\ai\`) và ảnh chụp thật, kèm nguồn |
| `nhac\` | Nhạc nền (nếu có) và file `nguon.json` ghi tên bài, tác giả, giấy phép |

## Cách yêu cầu

Nhắn cho AI một câu có chủ đề, ví dụ:

```
Tạo video vox 60 giây về giao tiếp với đồng nghiệp
```

```
Làm video giải thích kiểu vox vì sao lãi kép quan trọng, khổ dọc để đăng TikTok
```

```
Video giải thích 2 phút về quy trình xin nghỉ phép ở công ty, dùng nội dung này: (dán nội dung)
```

Có chủ đề là đủ: AI không hỏi thêm mà tự viết kịch bản, tự tạo ảnh, tự xem trước từng cảnh và sửa chỗ chưa ổn, dựng xong mới gửi video kèm kịch bản. AI chỉ hỏi khi thiếu chủ đề, hoặc khi nội dung là thứ chỉ bạn biết (quy trình nội bộ, số liệu riêng). Muốn duyệt kịch bản trước khi dựng thì nói "cho xem kịch bản trước".

Không nói gì thêm thì video dài 60 giây, khổ ngang, giọng nữ tốc độ vừa, phụ đề in lên hình, có tiếng hiệu ứng; nhạc nền chỉ thêm khi bạn xin. Muốn khác thì nói luôn trong câu lệnh: "dài 2 phút", "khổ dọc", "giọng nam", "có nhạc nền nhẹ", "ảnh kiểu tranh minh hoạ".

Nói "làm video" mà không rõ loại, AI sẽ hỏi lại: làm video từ bài giảng slide đã có, hay dựng video giải thích mới.

## Kịch bản kiểu Vox

AI viết lời theo mạch của các video giải thích trên mạng: mở bằng một tình huống hay câu hỏi gây tò mò, nêu vấn đề, giải thích vài ý (mỗi ý một hình ví von dễ nhớ), lật lại điều người xem vẫn nghĩ, rồi chốt bằng một việc làm được ngay. Không có màn tiêu đề, không "Hôm nay chúng ta…".

- **Đúng thời lượng:** AI đếm số từ của lời theo thời lượng yêu cầu (60 giây khoảng 130 từ), công cụ ước lại và báo khi lệch; AI sửa trước khi dựng.
- **Không bịa số liệu:** chỉ dùng con số bạn đưa hoặc con số có nguồn gọi tên được, và nguồn hiện nhỏ ở góc dưới cảnh đó. Không có nguồn thì AI nói bằng lời, không đưa số.
- **Hình khớp lời:** mỗi câu có ít nhất một thứ hiện ra đúng lúc câu đó được đọc; tắt tiếng đi vẫn đoán được video nói gì.

## Ảnh trong video

- **Ảnh AI vẽ:** đồ vật, cảnh, người minh hoạ được AI vẽ theo từng câu lời, rồi bộ công cụ tự cắt nền, thêm viền giấy xé và bóng. Ảnh AI không bao giờ có chữ: mọi chữ trên video do bộ công cụ viết nên luôn đúng dấu tiếng Việt. Cuối video ghi "Hình minh hoạ tạo bằng AI".
- **Ảnh chụp thật:** người, địa danh, sự kiện, sản phẩm có thật thì AI tải ảnh giấy phép mở (Openverse, Wikimedia), không vẽ giả; tác giả và giấy phép hiện cạnh ảnh.
- **Ảnh của bạn:** gửi file cho AI và cho biết ai chụp.

Ảnh AI lấy từ đâu:

- Trên **Antigravity** hoặc **Codex**: AI tự vẽ bằng công cụ vẽ ảnh của nền tảng, không cần cài gì thêm.
- Trên **Claude Code** (và nền tảng không tự vẽ được): bộ công cụ gọi một dịch vụ tạo ảnh qua **9router** chạy trên máy (mặc định ở cổng 20128, mô hình `ag/gemini-3.1-flash-image`, khoảng 15 giây một ảnh). Cần một lần cài đặt:
  1. Cài 9router theo hướng dẫn của người cung cấp, mở ở cổng 20128 (`http://localhost:20128`), đăng nhập tài khoản có mô hình vẽ ảnh. Bộ công cụ không tự cài 9router.
  2. Tạo khoá API trong trang quản trị 9router.
  3. Mở cửa sổ lệnh (PowerShell hoặc Command Prompt), chạy `setx ANH_AI_KEY "<khoá vừa tạo>"`, rồi đóng và mở lại cửa sổ lệnh cùng ứng dụng AI.

  Khoá chỉ nằm trên máy bạn, không ghi vào kịch bản hay thư mục dự án; đừng dán khoá vào khung chat. Dùng dịch vụ khác kiểu OpenAI thì đặt thêm `ANH_AI_URL` và `ANH_AI_MO_HINH`. Chưa có khoá thì AI vẫn làm được video bằng ảnh chụp thật, thẻ, chữ và con dấu, nhưng kém sinh động hơn.

Mỗi lần dựng vẽ tối đa 20 ảnh mới; ảnh đã vẽ được giữ lại, sửa một câu thì chỉ ảnh của câu đó vẽ lại.

## Máy cần gì

- **Chromium** (trình duyệt dùng để vẽ cảnh): tải một lần, khoảng 150–300 MB. AI hỏi trước khi tải.
- **FFmpeg** để tách nền ảnh và ghép video: AI cài theo hướng dẫn nếu máy chưa có.
- **Mạng** khi dùng giọng máy (giọng nữ HoaiMy hoặc giọng nam NamMinh), khi vẽ ảnh AI, tải ảnh thật hay tìm nhạc nền. Muốn dùng giọng của chính mình: thu từng cảnh thành `giong\canh-1.mp3`, `giong\canh-2.mp3`… trong thư mục video.

## Thời gian dựng

Trước khi dựng thật, AI dựng thử mỗi cảnh hai ảnh (giữa và cuối cảnh, thư mục `xem-truoc`) và tự xem: hình có khớp lời, chữ có tràn, vật có chồng nhau, ảnh AI có chữ lạ hay sai ý không. Chỗ nào chưa ổn thì AI sửa kịch bản rồi xem lại.

Dựng thật mất khoảng 1,5 lần thời lượng video trên máy 6 lõi: video 60 giây khoảng 90 giây, video 5 phút khoảng 7–8 phút; máy ít lõi chậm hơn. Cộng thêm thời gian vẽ ảnh AI (vẽ 3 ảnh cùng lúc) và tạo giọng. Trong lúc dựng máy chạy nặng hơn bình thường.

## Hiệu ứng

- **Vật đập xuống, dán, trượt vào:** ảnh cắt rời bay vào rồi đập xuống có nảy và bóng đổ, ảnh khung rơi xoay rồi được băng dính dán lên, thẻ trượt vào, con dấu đóng mạnh làm khung hình rung nhẹ, chữ hiện từng từ.
- **Số chạy:** con số cần nhớ chạy từ 0 lên giá trị thật, kèm nguồn.
- **Chiều sâu:** nền giấy, mảng giấy xé và các vật nằm trên ba lớp; máy quay đẩy vào chậm và nghiêng nhẹ nên các lớp trượt lệch nhau.
- **Chuyển cảnh:** xé giấy và lia nhanh xen nhau; muốn một kiểu hoặc không chuyển thì nhờ AI đổi.
- **Bảng màu:** giấy kem (mặc định), giấy báo cũ, nền tối ban đêm, hoặc màu tươi.
- **Phụ đề karaoke:** in lên hình, một dòng một lúc, tô vàng dần từng từ theo giọng đọc, có khung nền tối cho dễ đọc. Vẫn chọn được phụ đề cả câu một màu, phụ đề file riêng hoặc không có phụ đề.
- **Tiếng hiệu ứng:** tiếng đập, tiếng dán, tiếng chuyển cảnh, do bộ công cụ tự tạo (không dùng file âm thanh của ai), luôn nhỏ hơn giọng đọc nhiều.
- **Nhạc nền:** chỉ có khi bạn xin. AI tìm nhạc trên kho Openverse, chỉ lấy bản giấy phép mở CC0 hoặc CC BY; tên bài, tác giả và giấy phép hiện ở góc dưới trong 4 giây cuối video. AI gửi tên bài kèm video để bạn nghe thử; không ưng thì nhờ đổi bài. Có nhạc riêng thì gửi file kèm nguồn.
- **Tên loạt:** video thuộc một loạt thì góc trên hiện tên loạt và số cảnh.

Chữ trên hình và phụ đề dùng font Be Vietnam Pro (giấy phép mở SIL OFL), đi kèm bộ công cụ, đủ mọi chữ có dấu, không cần cài font. Mọi hiệu ứng đều tắt được: nhờ AI tắt tiếng hiệu ứng, bỏ nhạc nền, dùng một kiểu chuyển cảnh, hoặc đổi phụ đề.

## Sửa video

Nhắn AI chỗ muốn đổi ("cảnh 3 đổi ảnh khác", "rút còn 45 giây", "bỏ con dấu ở cảnh cuối"). AI sửa `video.md`, vẽ lại đúng những ảnh đã đổi, rồi dựng lại. Chỉ cảnh bị sửa lời mới phải tạo giọng lại nên dựng lại nhanh hơn. File giọng bạn thu sẵn không bao giờ bị ghi đè.

## Kịch bản cũ vẫn dựng được

Video làm từ các bản trước vẫn dựng lại được không cần sửa: kiểu viết tay (chữ Itim viết dần trên nền giấy, bàn tay cầm bút, máy quay phóng vào phần đang nói, lau bảng khi sang cảnh), kiểu cắt dán theo loại cảnh, cảnh kể chuyện có người que hoặc nhân vật AI đứng trên nền mẫu, thẻ thông tin, biểu đồ, câu hỏi nhanh và thí nghiệm ảo. Video mới đều làm kiểu Vox; muốn đúng kiểu viết tay cũ thì nói rõ với AI.

## Những điều cần biết

- Không chèn video tư liệu, không làm video do AI sinh hình chuyển động; ảnh AI chỉ là ảnh tĩnh.
- Ảnh AI có thể sai ý hoặc có chữ lạ: AI xem trước từng cảnh và vẽ lại, nhưng bạn vẫn nên xem kỹ video trước khi đăng.
- Nguồn vẽ ảnh phụ thuộc tài khoản của bạn: hết hạn mức hay tài khoản bị khoá thì AI làm video bằng ảnh thật, thẻ, chữ, con dấu; đổi mô hình chỉ cần đổi `ANH_AI_MO_HINH`.
- Nhạc nền chỉ dùng bản giấy phép mở hoặc nhạc bạn gửi kèm nguồn; không dùng nhạc tải từ YouTube hay nhạc không rõ nguồn.
- Video dùng giọng thu sẵn thì chỗ vật hiện ra và phụ đề karaoke khớp giọng theo ước lượng, có thể lệch vài phần mười giây.
- Kịch bản và video nằm trong `projects\` trên máy bạn, không được đưa lên GitHub.
- Gặp lỗi khi dựng: xem mục **Dựng video giải thích thất bại** và **Tạo ảnh cho video Vox thất bại** trong [Xử lý lỗi](xu-ly-loi.md).

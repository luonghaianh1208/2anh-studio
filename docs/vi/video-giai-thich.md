# Làm video giải thích

Video giải thích là một video ngắn kiểu viết tay hoặc kiểu giấy cắt dán, khổ ngang để chiếu lớp hoặc khổ dọc để đăng TikTok, Reels: tiêu đề, khái niệm, công thức, các ý, sơ đồ, đồ thị, biểu đồ và cả thí nghiệm ảo được viết dần ra trên nền giấy, khớp với giọng đọc tiếng Việt, có phụ đề. Video có hình minh hoạ vẽ dần từng nét, có thể có ảnh chụp thật; một bàn tay cầm bút đi theo nét đang vẽ, lau bảng hoặc lật trang khi sang cảnh mới, và máy quay phóng vào phần đang nói rồi thu về toàn cảnh. Ý chính được tô màu đúng lúc giọng đọc nói tới, và video có thể dừng lại hỏi học sinh một câu hỏi nhanh. Khác "Làm video bài giảng" (dựng từ file slide có sẵn), video giải thích dựng thẳng từ **nội dung bài**, không cần làm slide trước.

| File | Dùng để |
|---|---|
| `video.mp4` | Video Full HD: 1920×1080 khi khổ ngang (chiếu trên lớp, đưa lên YouTube, Zalo), 1080×1920 khi khổ dọc (TikTok, Reels, Story). Máy yếu có thể nhờ AI dựng bản 720 (1280×720 hoặc 720×1280) cho nhanh hơn |
| `phu-de.srt` | Phụ đề để riêng, chỉ có khi thầy cô chọn không in phụ đề lên hình |
| `video.md` | Kịch bản từng cảnh; sửa file này rồi dựng lại là video đổi theo |
| `nhac\` | Nhạc nền (nếu có) và file `nguon.json` ghi tên bài, tác giả, giấy phép |
| `anh\` | Ảnh chụp thật (nếu có) kèm nguồn; thư mục `anh\ai\` chứa ảnh do AI vẽ (nếu có) kèm nguồn |

## Cách yêu cầu

Nhắn cho AI, ví dụ: `Làm video giải thích bài Con lắc đơn bằng kiểu viết tay`, rồi dán nội dung hoặc dàn ý bài. AI hỏi một lượt ngắn (bài nào, học sinh cần hiểu gì và có muốn câu hỏi nhanh không, dài bao lâu, khổ ngang hay dọc, có thuộc một loạt bài không, giọng nam hay nữ và có giọng thu sẵn không, phong cách viết tay hay cắt dán, có nhân vật dẫn chuyện không, có cảnh thí nghiệm ảo hay ảnh chụp thật không, phụ đề in lên hình hay để riêng, có muốn tiếng hiệu ứng và nhạc nền không), chia bài thành các cảnh để thầy cô duyệt, rồi dựng video trong `projects\_video\<tên_video>\`.

Nói "làm video" mà không rõ loại, AI sẽ hỏi lại: làm video từ bài giảng slide đã có, hay dựng video giải thích mới.

Ví dụ khác: `Làm video dọc kiểu cắt dán giải thích vì sao in thêm tiền gây lạm phát, có người que dẫn chuyện`.

## Khổ, phong cách và nhân vật

- **Khổ ngang hoặc dọc:** khổ ngang 16:9 để chiếu lớp; khổ dọc 9:16 để đăng TikTok, Reels, Story. Ở khổ dọc, hình và chữ xếp trên dưới thay vì hai cột, phụ đề ngắn hơn (khoảng 22 ký tự một dòng) và có khung nền tối cho dễ đọc; AI viết lời thành câu ngắn cho vừa.
- **Viết tay hoặc cắt dán:** viết tay là chữ và hình được bút viết dần trên nền giấy, hợp bài giảng trên lớp. Cắt dán là kiểu tạp chí Vox: nền giấy, mảnh giấy xé, tiêu đề dán trên băng dính màu, hình dạng nhãn dán viền trắng, chữ trượt vào, chuyển cảnh bằng mép giấy xé; phụ đề có khung nền tối. Font chữ cắt dán là Be Vietnam Pro (giấy phép mở SIL OFL), thiết kế cho tiếng Việt.
- **Cảnh kể chuyện:** một cảnh "nói bằng hình": tranh nền kín khung, một nhân vật dẫn chuyện đứng ở một tư thế, và một câu tiêu đề lớn là kết luận của cảnh; lời giảng chỉ hiện ở phụ đề. Hợp với cảnh mở đầu, cảnh đặt vấn đề hay kể một tình huống, xen với các cảnh có chữ và hình.
- **Nền của cảnh kể chuyện:** 8 nền mẫu vẽ sẵn trong bộ công cụ (lớp học, phòng thí nghiệm, bầu trời, vũ trụ, thành phố, đồng quê, giấy cắt dán, vòng tròn màu), không cần mạng, không vướng giấy phép; hoặc một ảnh chụp thật; hoặc tranh do AI vẽ theo mô tả (xem dưới). Nhiều cảnh có thể dùng chung một nền.
- **Nhân vật dẫn chuyện:** không có (mặc định); người que vẽ sẵn, đổi được màu áo, biết nhún thở, chớp mắt, vẫy tay; hoặc nhân vật do AI vẽ theo một câu mô tả của thầy cô. Nhân vật có 10 tư thế (đứng, chào, chỉ tay, giải thích, suy nghĩ, ngạc nhiên, vò đầu, dừng lại, ăn mừng, buồn); AI chọn tư thế khớp lời từng cảnh. Nhân vật cũng có thể đứng cạnh chữ ở cảnh tiêu đề, khái niệm hay các ý.
- **Tên loạt:** video thuộc một loạt bài thì góc trái trên hiện tên loạt, góc phải trên hiện số cảnh (ví dụ "03/08").
- **Thẻ thông tin và dòng tài liệu:** một con số đáng nhớ hiện thành thẻ thông tin ba tầng (ví dụ "Siêu lạm phát · 1923 · Cộng hoà Weimar"); dòng tài liệu nhỏ ở góc dưới ghi nguồn nội dung (ví dụ sách giáo khoa).

## Hình do AI vẽ

Nền tranh và nhân vật do AI vẽ chỉ làm được khi thầy cô dùng AI có công cụ vẽ ảnh: **Antigravity** (Nano Banana Pro) hoặc **ChatGPT Codex** (GPT Image). AI vẽ nhân vật mẫu trước rồi vẽ các tư thế theo mẫu đó để nhân vật giống nhau qua các cảnh; bộ công cụ tự tách nền, cắt đúng khổ và ghi nguồn. Ảnh AI không bao giờ có chữ: mọi chữ trên video do bộ công cụ viết nên luôn đúng dấu tiếng Việt. Video có ảnh AI luôn ghi "Hình minh hoạ tạo bằng AI" ở cuối, và AI gửi thầy cô xem từng cảnh trước khi dựng thật. Trên **Claude Code** (không có công cụ vẽ ảnh), AI dùng nền mẫu và người que; muốn nhân vật AI thì mở bài trên Antigravity hoặc Codex.

## Máy cần gì

- **Chromium** (trình duyệt dùng để vẽ cảnh): tải một lần, khoảng 150–300 MB. AI hỏi thầy cô trước khi tải.
- **FFmpeg** để ghép video: AI cài theo hướng dẫn nếu máy chưa có.
- **Mạng** khi dùng giọng máy (giọng nữ HoaiMy hoặc giọng nam NamMinh) và khi AI tìm nhạc nền; bản thân bước dựng không tự lên mạng tìm nhạc hay ảnh. Không có mạng, hoặc muốn dùng giọng của chính mình: thu từng cảnh thành file `giong\canh-1.mp3`, `giong\canh-2.mp3`… đặt trong thư mục video; cảnh có file thu sẵn thì không cần mạng.

## Thời gian dựng

Trước khi dựng thật, AI dựng thử mỗi cảnh một ảnh (thư mục `xem-truoc`) để soát chữ có tràn khung không. Video có ảnh chụp thật hoặc ảnh AI vẽ thì AI gửi thầy cô xem các cảnh đó trước (lệnh `--xem-truoc`) và chỉ dựng khi thầy cô đồng ý.

Dựng thật mất khoảng bằng thời lượng video trên máy 6 lõi: video 5 phút mất khoảng 5 phút; máy 2–3 lõi mất khoảng 7–8 phút. Video kiểu cắt dán chậm hơn: khoảng 1,5 lần thời lượng ngay trên máy 6 lõi (video 5 phút khoảng 7–8 phút). Cộng thêm thời gian tạo giọng. Máy càng nhiều lõi thì càng nhanh vì công cụ chụp khung bằng nhiều trình duyệt chạy song song. Trong lúc đó máy chạy nặng hơn bình thường.

## Hình và ảnh

- **Hình vẽ nét** lấy từ bộ biểu tượng có sẵn trong bộ công cụ, không cần mạng. AI tự chọn hình theo nội dung bài.
- **Ảnh chụp thật** do AI tải từ kho ảnh mở (Openverse, Wikimedia), không cần khoá. Mỗi ảnh luôn có dòng ghi tác giả và giấy phép cạnh ảnh, không đè lên chữ. Thầy cô muốn dùng ảnh tự chụp thì gửi file cho AI và cho biết ai chụp; ảnh điện thoại chụp dọc vẫn hiện đúng chiều.
- Muốn video bớt chuyển động: nhờ AI tắt bàn tay, tắt máy quay hoặc tắt lau bảng; mỗi thứ tắt riêng được.
- Chữ trên hình và phụ đề dùng font Itim (kiểu viết tay) hoặc Be Vietnam Pro (kiểu cắt dán), đều theo giấy phép mở SIL OFL 1.1 và đi kèm bộ công cụ, đủ mọi chữ có dấu, máy nào cũng hiện giống nhau; không cần cài font.

## Hiệu ứng giúp học sinh nhớ bài

AI tự chọn các hiệu ứng dưới đây theo nội dung bài; thầy cô chỉ cần nói khi muốn thêm, bớt hay tắt.

- **Nhấn ý chính:** từ khoá được tô vàng như bút dạ quang, khoanh tròn đỏ hoặc gạch chân đúng lúc giọng đọc nói tới, và nảy nhẹ một nhịp. Mỗi cảnh chỉ nhấn 1–2 ý quan trọng nhất.
- **Số chạy:** con số cần nhớ chạy từ 0 lên giá trị thật (ví dụ 0 → 2,01 giây), viết kiểu Việt với dấu phẩy thập phân.
- **Biểu đồ động:** biểu đồ cột, đường hoặc tròn mọc dần theo lời, số trên cột chạy lên cùng lúc.
- **Sơ đồ tư duy và dòng thời gian:** các nhánh, các mốc được vẽ dần theo lời; hợp với cảnh tóm tắt cuối bài và bài lịch sử.
- **Công thức từng phần:** công thức hiện từng bước (công thức gốc, thay số, kết quả) theo từng câu giảng.
- **Câu hỏi nhanh:** video hiện câu hỏi 2–4 lựa chọn, đếm ngược vài giây (mặc định 5 giây) cho học sinh tự nghĩ, rồi khoanh đáp án đúng và đọc lời giải. Thầy cô duyệt câu hỏi và đáp án trước khi dựng; công cụ chỉ kiểm đáp án có nằm trong các lựa chọn.
- **Chuyển cảnh:** ngoài lau bảng còn có lật trang, trượt, phóng xuyên và mở màn; AI có thể cho các kiểu này xoay vòng để video đỡ lặp.
- **Tiêu đề nảy chữ:** tiêu đề cảnh mở đầu nảy vào từng chữ cái.
- **Phụ đề karaoke:** phụ đề in lên hình tô vàng dần từng từ theo giọng đọc, giúp học sinh theo kịp từ ngữ khoa học. Thầy cô vẫn chọn được phụ đề kiểu cũ (cả câu một màu), phụ đề file riêng hoặc không có phụ đề.
- **Tiếng hiệu ứng:** tiếng bút viết, tiếng "ting" khi một ý hiện ra, tiếng chuyển cảnh, tích tắc khi đếm ngược, tiếng chuông khi hiện đáp án. Các tiếng này do bộ công cụ tự tạo (không dùng file âm thanh của ai), luôn nhỏ hơn giọng đọc nhiều.
- **Nhạc nền:** nhạc nhẹ tự nhỏ đi khi có giọng đọc, to lên một chút ở chỗ đếm ngược. AI tìm nhạc trên kho Openverse, chỉ lấy bản giấy phép mở CC0 hoặc CC BY, và gửi thầy cô nghe thử trước khi dựng; tên bài, tác giả và giấy phép luôn hiện ở góc dưới trong 4 giây cuối video. Thầy cô có nhạc riêng thì gửi file kèm nguồn (ai sáng tác, giấy phép).

Mọi hiệu ứng đều tắt được: nhờ AI tắt tiếng hiệu ứng, bỏ nhạc nền, tắt chữ nảy, dùng một kiểu chuyển cảnh, hoặc đổi phụ đề. Tiếng hiệu ứng tự tạo có thể nghe hơi "máy"; thầy cô nghe thử video đầu tiên rồi quyết giữ hay tắt.

## Sửa một cảnh

Mở `video.md`, sửa chữ hoặc lời của cảnh đó (hoặc nhờ AI sửa), rồi nhờ AI dựng lại. Chỉ cảnh bị sửa lời mới phải tạo giọng lại; các cảnh khác dùng lại giọng cũ nên dựng lại nhanh hơn. File giọng thầy cô thu sẵn không bao giờ bị ghi đè, kể cả khi thầy cô chép nó đè lên giọng máy cũ mà file `giong\canh-N.json` vẫn còn (xoá file `.json` đó cũng không sao).

## Những điều cần biết

- Có hai phong cách (viết tay, cắt dán) và hai khổ (ngang 16:9, dọc 9:16). Không chèn video tư liệu, không làm video do AI sinh hình chuyển động; ảnh AI chỉ là tranh tĩnh.
- Kịch bản làm từ các bản trước dựng lại được không cần sửa; video viết tay khổ ngang giữ bố cục cũ, nay nét hơn ở Full HD.
- Nhạc nền chỉ dùng bản giấy phép mở hoặc nhạc thầy cô gửi kèm nguồn; không dùng nhạc tải từ YouTube hay nhạc không rõ nguồn. Nhạc CC BY bắt buộc ghi tác giả, và video luôn ghi.
- Video dùng giọng thu sẵn thì chỗ nhấn ý và phụ đề karaoke khớp giọng theo ước lượng, có thể lệch vài phần mười giây; AI sẽ báo cảnh nào ước lượng.
- Ảnh tải về có thể sai nội dung: thầy cô xem kỹ ảnh AI gửi trước khi đồng ý dựng.
- Cảnh thí nghiệm ảo dùng 8 mô hình đã kiểm bằng số của phần [Làm thí nghiệm ảo](thi-nghiem-ao.md); số hiện trên hình luôn khớp công thức.
- AI không tự sửa số liệu, công thức hay lời giảng của thầy cô; khi chữ quá dài cho khung, AI chỉ rút gọn chữ trên hình hoặc tách cảnh.
- Kịch bản và video nằm trong `projects\` trên máy thầy cô, không được đưa lên GitHub.
- Gặp lỗi khi dựng: xem mục **Dựng video giải thích thất bại** trong [Xử lý lỗi](xu-ly-loi.md).

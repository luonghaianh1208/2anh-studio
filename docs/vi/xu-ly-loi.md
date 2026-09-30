# Xử lý lỗi

Gặp lỗi, hãy chạy `KIEM-TRA.bat` trước, rồi đối chiếu dòng ❌ [LỖI] (hoặc ⚠️ [CẢNH BÁO]) với các mục bên dưới.

## Gõ python mà mở Microsoft Store

Lệnh `python` đang bị lối tắt của Microsoft Store chiếm chỗ, chưa phải Python thật.

- Vào **Settings → Apps → Advanced app settings → App execution aliases**, tắt `python.exe` và `python3.exe`.
- Hoặc cài Python từ https://www.python.org/downloads/, nhớ tick **"Add python.exe to PATH"**.
- Sau khi sửa, đóng cửa sổ dòng lệnh đang mở rồi mở lại (hoặc bấm lại `CAI-DAT.bat`).

## Đã cài Python nhưng bộ cài báo không tìm thấy

`CAI-DAT.bat` báo **"Đã cài Python ... nhưng bản này chưa có trong PATH"**, hoặc gõ `python` báo không tìm thấy dù máy đã cài Python. Nguyên nhân thường gặp: lúc cài chưa tick **"Add python.exe to PATH"** (bộ cài của python.org mặc định không tick ô này). Cài lại bằng winget không giúp được vì Python đã có sẵn trên máy.

1. Mở **Settings → Apps → Installed apps** (Windows 10: **Apps & features**), tìm **Python 3.x** rồi chọn **Modify**. Cách khác: chạy lại bộ cài đã tải từ python.org và chọn **Modify**.
2. Bấm **Next** tới trang **Advanced Options**, tick **"Add Python to environment variables"**, rồi bấm **Install**.
3. Đóng cửa sổ dòng lệnh đang mở, mở lại rồi bấm lại `CAI-DAT.bat`.

## PowerShell bị chặn trên máy trường hoặc công ty

Bấm `CAI-DAT.bat` hoặc `KIEM-TRA.bat` mà thấy thông báo tiếng Anh có cụm **"running scripts is disabled on this system"** hoặc nhắc tới **execution policy**, rồi dừng: máy do nhà trường hoặc công ty quản lý đang chặn chạy script PowerShell. Chính sách này mạnh hơn tuỳ chọn mà các file `.bat` dùng nên bộ cài không tự vượt qua được.

- Nhờ quản trị máy (bộ phận IT) cho phép chạy script PowerShell.
- Hoặc tự chạy từng lệnh trong cửa sổ dòng lệnh mở tại thư mục bộ công cụ:
  ```
  python -m pip install -r requirements.txt
  python tools\vi\doctor.py
  ```
  Nếu chưa có file `.env`, tạo bằng lệnh `copy .env.example .env`.

## Máy trường chặn cài đặt

Dấu hiệu: AI báo không tải được bộ công cụ hoặc Python, không chạy được bộ cài Python, không cài được thư viện vì mạng, hoặc PowerShell bị chặn chạy script. Máy do nhà trường quản lý có thể chặn các việc này; AI không tìm cách vượt qua.

Gửi bộ phận IT đoạn sau:

> Nhờ anh/chị hỗ trợ để tôi dùng bộ công cụ 2Anh Studio (trước đây là PPT Master bản Việt) trên máy này:
> 1. Cho tài khoản Windows của tôi truy cập: python.org, pypi.org, files.pythonhosted.org, github.com, codeload.github.com; thêm cdn.winget.microsoft.com, objects.githubusercontent.com (khi cần FFmpeg/Pandoc).
> 2. Cho phép cài Python 3.12 cho riêng tài khoản của tôi (không cần quyền quản trị).
> 3. Cho phép chạy PowerShell với tuỳ chọn `-ExecutionPolicy Bypass` cho từng lệnh.

Nếu chỉ bị chặn chạy script PowerShell mà máy đã có Python, xem mục **PowerShell bị chặn trên máy trường hoặc công ty** ở trên.

## Cài thư viện thất bại

Vài nguyên nhân thường gặp:

- **Mạng trường học/công ty có proxy chặn:** thử đổi sang mạng khác (ví dụ 4G), hoặc chạy:
  ```
  python -m pip install --proxy http://<máy chủ>:<cổng> -r requirements.txt
  ```
- **Thiếu quyền ghi:**
  ```
  python -m pip install --user -r requirements.txt
  ```
- **Python quá mới, chưa có bản build cho vài gói:** cài thêm Python 3.12 và dùng bản đó.
- **Phần mềm diệt virus chặn quá trình cài:** tạm tắt diệt virus trong lúc cài, bật lại sau khi xong.

## KIEM-TRA báo thiếu thư viện

- Thư mục bộ công cụ có thư mục `venv` (bộ công cụ do AI cài): nhờ AI chạy lại lệnh cài, hoặc chạy lệnh sau trong cửa sổ dòng lệnh mở tại thư mục bộ công cụ:
  ```
  venv\Scripts\python.exe -m pip install -r requirements.txt
  ```
- Bấm lại `CAI-DAT.bat` để cài lại thư viện.
- Nếu máy có nhiều bản Python, lệnh `python` trong PATH có thể không phải bản đã cài thư viện. Kiểm tra bằng:
  ```
  python -c "import sys; print(sys.executable)"
  ```
  và đảm bảo đây là bản bạn đã dùng để cài thư viện.

## Lỗi "Tính toàn vẹn skill"

Bộ công cụ bị sửa đổi hoặc thiếu file bản quyền (`LICENSE`, `SKILL.md`, `SPONSORS*.md`).

- Tải lại bản đầy đủ từ repo.
- Không tự chỉnh sửa các file trên.

## Xuất thử PPTX thất bại

- Chạy lại `KIEM-TRA.bat` để xem lỗi có lặp lại không.
- Kiểm tra xem phần mềm diệt virus có đang quét thư mục Temp của Windows không — việc quét có thể làm chậm hoặc chặn quá trình xuất file.
- Nếu thông báo có `FileNotFoundError` kèm một đường dẫn rất dài, xem mục **Đường dẫn quá dài** ngay bên dưới.
- Nếu vẫn lỗi, khi hỏi hỗ trợ hãy chụp toàn bộ màn hình kết quả `KIEM-TRA.bat` để gửi kèm.

## Dựng video giải thích thất bại

Xem dòng kết quả AI đọc được, phần `error`:

- `input`: chưa có thư mục video hoặc file `video.md`. Nhờ AI viết file theo docs/vi/tro-ly/video-giai-thich.md rồi chạy lại.
- `parse`: `error.message` nêu đúng số **Dòng** trong `video.md` cần sửa, ví dụ thiếu `loai:` hay `loi:`, cảnh đánh số không liên tiếp, hoặc có địa chỉ web.
- `canh`: nội dung một cảnh không vừa khung. `error.message` nêu số cảnh: chữ dài quá giới hạn, **chữ tràn khung** khi dựng thử, mã thí nghiệm không có trong danh mục, hoặc mốc thời gian của thí nghiệm dài hơn lời đọc. AI rút gọn chữ hoặc tách thành hai cảnh; lời giảng và số liệu của thầy cô giữ nguyên. Lỗi `canh` về hình và ảnh:
  - **tên biểu tượng không có**: tên biểu tượng phải là tiếng Anh; lỗi chỉ tới bảng tra biểu tượng và gợi ý tối đa 5 tên (tên tiếng Việt được đối chiếu với bảng tra). AI chọn một tên trong đó hoặc tra bảng.
  - **ảnh nặng quá 8 MB**: AI dùng bản thu nhỏ mà lệnh tải ảnh để sẵn trong `anh\.review\`.
  - **ảnh chưa có nguồn**: ảnh thầy cô tự chụp cần ghi ai chụp; ảnh tải về thì AI tải lại để có bản ghi nguồn.
  - **`anh\image_sources.json` sai cấu trúc** hoặc không phải JSON: AI sửa file theo dạng nêu trong thông báo.
  - **thiếu file ảnh** hoặc sai định dạng: chỉ nhận `.jpg`, `.jpeg`, `.png`, `.webp` đặt trong thư mục `anh\` của video.
  - **nhạc nền** (thông báo bắt đầu bằng "Cảnh 0: nhạc nền"): thiếu file trong thư mục `nhac\`, file không phải `.mp3`, `.m4a`, `.wav`, `.ogg`, file hỏng, hoặc nhạc **chưa có nguồn**. Nhạc AI tải bằng `tim_nhac.py` có nguồn sẵn trong `nhac\nguon.json`; nhạc thầy cô gửi thì cho AI biết tên bài, người sáng tác và giấy phép để ghi `nguon-nhac:`.
  - **dấu nhấn** sai (lỗi `parse` nêu **Dòng**): cụm `==…==`, `((…))`, `__…__` chưa đóng, lồng nhau hoặc quá 3 cụm một dòng; `{{…}}` không phải số (số trong kịch bản dùng dấu chấm thập phân).
- `giong`: không tạo được giọng đọc. Giọng máy **cần mạng**: kiểm tra mạng rồi nhờ AI chạy lại. Không có mạng thì thu giọng từng cảnh thành `giong\canh-1.mp3`, `giong\canh-2.mp3`… trong thư mục video; cảnh có file sẵn không cần mạng. Cảnh câu hỏi nhanh cần thêm giọng lời giải `giong\canh-N-giai.mp3`; `error.message` nêu đúng file đang thiếu.
- `chromium`: máy chưa có Chromium để vẽ cảnh. Cho AI chạy `powershell -NoProfile -ExecutionPolicy Bypass -File tools\vi\pptmaster.ps1 -Action tool -Name chromium` (tải 150–300 MB, một lần). Bước cài `playwright` báo `FileNotFoundError` hay lỗi đường dẫn thì xem mục **Đường dẫn quá dài**.
- `ffmpeg`: máy chưa có FFmpeg. Cho AI chạy lệnh trên với `-Name ffmpeg`.
- `dung`: chụp khung hoặc ghép video hỏng giữa chừng. Hỏng lúc chụp khung thì `error.message` nêu cảnh (hoặc dải cảnh) đang chụp; hỏng lúc ghép thì `error.message` là thông báo lỗi của FFmpeg. Dán nguyên dòng `error.message` gửi người bảo trì.
- `write`: **`video.mp4` đang mở** trong trình phát video — đóng lại rồi chạy lại; hoặc ổ đĩa hết dung lượng (khung hình tạm được ghi ra đĩa trong lúc dựng).
- `internal`: lỗi ngoài dự kiến. Dán nguyên dòng `error.message` gửi người bảo trì.

Các dòng `warnings` không chặn video, chỉ gợi ý: cảnh dài quá 40 giây, video dài quá 8 phút, lời hoặc lời giải một cảnh quá 700 ký tự, hoặc "mốc câu … ước lượng", "mốc từng từ ước lượng" khi dùng giọng thu sẵn hay khi chữ không khớp được với giọng máy (chữ, chỗ nhấn ý và phụ đề karaoke có thể lệch tiếng vài trăm mili giây).

Video có tiếng hiệu ứng hay nhạc nền nghe ồn: nhờ AI ghi `am-thanh: khong` (tắt tiếng hiệu ứng) hoặc bỏ dòng `nhac-nen` (bỏ nhạc) rồi dựng lại.

## Tìm nhạc nền thất bại

Lệnh `tools\vi\tim_nhac.py` tìm và tải nhạc nền giấy phép mở (CC0, CC BY) trên Openverse cho video giải thích. Xem dòng kết quả AI đọc được, phần `error`:

- `mang`: không kết nối được Openverse, hết thời gian chờ, hoặc Openverse trả dữ liệu lạ. Kiểm tra mạng rồi nhờ AI chạy lại; Openverse bận thì thử lại sau vài phút. Máy trường chặn trang ngoài thì thầy cô tự gửi một file nhạc có giấy phép rõ ràng.
- `input`: sai tham số lệnh; từ khoá không có chữ cái hay chữ số; không có bản CC0/CC BY dạng mp3 dài từ 60 giây cho từ khoá đó (nhờ AI thử từ khoá tiếng Anh khác, ngắn hơn, ví dụ "calm piano"); hoặc `nhac\nguon.json` đang có sai cấu trúc (sửa lại hoặc xoá file đó rồi chạy lại).
- `write`: không ghi được thư mục `nhac\` hay file nhạc: kiểm ổ đĩa còn chỗ, đóng file đang mở rồi chạy lại.

Lệnh không bao giờ ghi đè file nhạc đã có; bản tải về không phải mp3 hoặc quá 40 MB thì bị bỏ qua và có một dòng `warnings`.

## Tạo thí nghiệm ảo thất bại

Xem dòng kết quả AI đọc được, phần `error`:

- `input`: chưa có thư mục thí nghiệm hoặc file `thi-nghiem.md`. Nhờ AI viết file theo docs/vi/tro-ly/thi-nghiem-ao.md rồi chạy lại.
- `parse`: `error.message` nêu đúng số **Dòng** trong `thi-nghiem.md` cần sửa. Hay gặp nhất: khoảng tham số vượt khoảng của mẫu (ví dụ góc lệch con lắc trên 15°), vì ngoài khoảng đó công thức không còn đúng.
- `model`: mã mẫu không có trong danh mục, hoặc mô hình AI tự viết thiếu công thức, điều kiện áp dụng hay bảng số kiểm. AI sửa theo khuôn; không bỏ các phần đó.
- `check`: mô hình AI tự viết cho kết quả lệch bảng số kiểm. AI sửa mô hình; nếu AI sửa bảng số kiểm thì phải nói rõ với thầy cô dòng nào đã sửa.
- `docx`: máy chưa có thư viện `python-docx`. Có `venv\Scripts\python.exe` ở thư mục gốc repo thì chạy `venv\Scripts\python.exe -m pip install -r tools/vi/requirements-vi.txt`; không thì chạy `python -m pip install -r tools/vi/requirements-vi.txt`, hoặc bấm đúp `CAI-DAT.bat`.
- `write`: phiếu học tập đang mở trong Word, hoặc ổ đĩa hết dung lượng, hoặc đường dẫn quá 200 ký tự (xem mục **Đường dẫn quá dài**).
- `internal`: lỗi ngoài dự kiến. Dán nguyên dòng `error.message` gửi người bảo trì.

Cảnh báo "chưa chạy kiểm số vì không có Node" không phải lỗi: trang HTML tự kiểm mỗi lần mở. Trang hiện **dải đỏ** "Mô hình không qua tự kiểm" thì không dùng để dạy; nhờ AI tạo lại.

## Kiểm hiệu ứng không đạt

Sau khi xuất slide, AI chạy `tools\vi\kiem_hieu_ung.py` để so hiệu ứng với mức thầy cô chọn (không, vừa, nhiều). Xem dòng kết quả AI đọc được, phần `error`:

- `muc`: bài có ít hiệu ứng hơn mức đã chọn (ví dụ mức vừa cần ít nhất 30% trang nội dung có hiệu ứng), hoặc mức "không" mà vẫn còn hiệu ứng. AI tự sửa một lần; vẫn không đạt thì thầy cô có thể chọn mức thấp hơn hoặc nhờ AI thêm hiệu ứng ở những trang cụ thể.
- `video`: bài dùng làm video còn hiệu ứng **bấm mới hiện** hoặc ô bấm hiện đáp án. Video không có ai bấm nên hình sẽ đứng; AI đổi các hiệu ứng đó sang tự chạy trong bản riêng cho video (`animations_video.json`) rồi xuất lại. Bản trình chiếu trên lớp vẫn giữ hiệu ứng bấm.
- Bước xuất bản thuyết minh báo "cannot be used with on-click object animations": cùng nguyên nhân với `video`, AI làm như trên.
- `parse`: file PPTX hỏng hoặc không phải file PPTX. Nhờ AI xuất lại bài.
- `input`: lệnh thiếu mức hoặc sai đường dẫn file. Nhờ AI chạy lại đúng lệnh.
- `internal`: lỗi ngoài dự kiến. Dán nguyên dòng `error.message` gửi người bảo trì.

Các dòng `warnings` không chặn bài, chỉ gợi ý: trang có quá nhiều bước bấm, câu trắc nghiệm chưa có cách hiện đáp án, hiệu ứng dài quá 2 giây.

## Xuất giáo án thất bại

Xem dòng kết quả AI đọc được, phần `error`:

- `input`: chưa có file `giao-an.md` trong thư mục giáo án. Nhờ AI viết file `giao-an.md` theo docs/vi/tro-ly/giao-an.md rồi chạy lại lệnh xuất.
- `parse`: `error.message` nêu đúng số **Dòng** trong `giao-an.md` cần sửa. Mở file, sửa đúng dòng đó rồi chạy lại.
- `framework`: một **mã năng lực** số hoặc AI trong `giao-an.md` không đúng bảng mã. Sửa mã theo `error.fix`; AI không tự đặt mã mới.
- `docx`: máy chưa có thư viện `python-docx`. Có `venv\Scripts\python.exe` ở thư mục gốc repo thì chạy `venv\Scripts\python.exe -m pip install -r tools/vi/requirements-vi.txt`; không thì chạy `python -m pip install -r tools/vi/requirements-vi.txt`, hoặc bấm đúp `CAI-DAT.bat`.
- `write`: một file Word trong kết quả **đang mở trong Word** — đóng file đó rồi chạy lại; hoặc ổ đĩa hết dung lượng; hoặc đường dẫn dự án quá 200 ký tự, xem mục **Đường dẫn quá dài**.
- `internal`: lỗi ngoài dự kiến. Dán nguyên dòng `error.message` gửi người bảo trì.

## Xuất đề Word thất bại

Xem dòng kết quả AI đọc được, phần `error`:

- `input`: chưa có file `de.md` trong thư mục đề. Nhờ AI viết file `de.md` rồi chạy lại lệnh xuất.
- `parse`: `error.message` nêu đúng số **Dòng** trong `de.md` cần sửa. Mở file, sửa đúng dòng đó rồi chạy lại.
- `docx`: máy chưa có thư viện `python-docx`. Có `venv\Scripts\python.exe` ở thư mục gốc repo thì chạy `venv\Scripts\python.exe -m pip install -r tools/vi/requirements-vi.txt`; không thì chạy `python -m pip install -r tools/vi/requirements-vi.txt`, hoặc bấm đúp `CAI-DAT.bat`.
- `write`: một file Word trong kết quả **đang mở trong Word** — đóng file đó rồi chạy lại; hoặc ổ đĩa hết dung lượng; hoặc đường dẫn dự án quá 200 ký tự, xem mục **Đường dẫn quá dài**.
- `internal`: lỗi ngoài dự kiến. Dán nguyên dòng `error.message` gửi người bảo trì.

## Dựng video thất bại

Xem dòng kết quả AI đọc được, phần `error`:

- `chromium`: máy chưa có Chromium để chụp ảnh slide. Cho AI chạy `powershell -NoProfile -ExecutionPolicy Bypass -File tools\vi\pptmaster.ps1 -Action tool -Name chromium` (tải 150–300 MB).
- `ffmpeg`: máy chưa có FFmpeg. Cho AI chạy lệnh trên với `-Name ffmpeg`.
- `audio`: bài giảng chưa có lời giảng hoặc chưa có tiếng đọc. Đọc `error.message`: thiếu ghi chú thì nhờ AI viết lời giảng trước, rồi mới tạo tiếng đọc.
- `powerpoint`: PowerPoint không xuất được video. Thử lại bằng cách ghép ảnh: `venv\Scripts\python.exe tools\vi\video.py <đường_dẫn_dự_án> --cach ffmpeg`.
- `render`, không chụp được ảnh slide (thường thiếu Chromium hoặc một slide bị lỗi): cho AI cài Chromium như mục `chromium` ở trên, hoặc mở bài giảng xem slide nào lỗi rồi sửa.
- `render`, hết dung lượng ổ đĩa hoặc đường dẫn quá dài: dọn ổ đĩa, hoặc chuyển bộ công cụ sang `D:\PPTmaster` rồi làm lại.
- `project`: đường dẫn dự án không đúng, thư mục không phải dự án PPT Master, dự án chưa có slide nào, hoặc đường dẫn quá dài (trên 200 ký tự) — kiểm lại tên dự án trong `projects\`, và chuyển bộ công cụ sang `D:\PPTmaster` nếu `error.message` nói về độ dài đường dẫn.
- `narrated_pptx`: chưa có bản PPTX đã gắn tiếng, nên đường PowerPoint không chạy được — nhờ AI xuất lại bản PPTX có thuyết minh, hoặc dựng bằng cách ghép ảnh với `--cach ffmpeg`.

Khi hỏi hỗ trợ, dán nguyên dòng `error.message` — dòng đó nêu đúng nguyên nhân, còn tên `error.step` chỉ nói bước nào dừng.

## Đường dẫn quá dài

Dấu hiệu: `KIEM-TRA.bat` hoặc lúc xuất bài báo lỗi có chữ `FileNotFoundError`, kèm một đường dẫn rất dài (thường chứa `.pptx-build-`). Windows mặc định chỉ cho phép đường dẫn dài khoảng 260 ký tự, trong khi quá trình xuất PPTX tạo thêm nhiều thư mục con bên trong thư mục dự án.

- Dời cả thư mục bộ công cụ sang đường dẫn ngắn, ví dụ `D:\PPTmaster`.
- Tránh giải nén ZIP thành thư mục lồng nhau như `PPTmaster-main\PPTmaster-main`, và tránh đặt trong thư mục OneDrive nhiều cấp.
- Hoặc nhờ quản trị máy bật **Long Paths** của Windows (cần quyền quản trị).

## Cập nhật thất bại

- Thông báo **"not a Git checkout"**: thư mục này là bản tải bằng ZIP, không tự cập nhật được. Tải bản mới rồi chép thư mục `projects\` và file `.env` của bạn sang.
- Thông báo **"Tracked local changes"**: bạn đã sửa file thuộc bộ công cụ. Chạy `git status` để xem file nào đã đổi, chuyển các file cá nhân của bạn vào thư mục `projects\`, rồi khôi phục file bộ công cụ bằng:
  ```
  git restore <tên file>
  ```
  **Cảnh báo:** lệnh này sẽ xoá mọi thay đổi bạn đã làm trong file đó.
- Thiếu Git: cài Git (bấm `CAI-DAT.bat`, bộ cài sẽ đề nghị cài Git).

## Chữ tiếng Việt lỗi dấu trong PowerPoint

Thường do máy không có sẵn font đang dùng. Nhắn cho AI, ví dụ "đổi toàn bộ font sang Segoe UI" (hoặc Arial, Times New Roman), rồi xuất lại file.

## Hỏi hỗ trợ

Tạo issue tại https://github.com/luonghaianh1208/2anh-studio/issues, kèm theo kết quả chạy `KIEM-TRA.bat`. **Xoá mọi API key** trong nội dung trước khi gửi.

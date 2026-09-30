# Cài đặt trên Windows

> **Cách nhanh: nhờ AI cài.** Dùng Antigravity thì chỉ cần mở một thư mục trống và dán câu lệnh mẫu trong [Bắt đầu nhanh](bat-dau-nhanh.md#để-ai-tự-cài); AI tự tải bộ công cụ, tự cài Python và thư viện. Các bước bấm đúp dưới đây dành cho ai muốn tự cài.

## Cần chuẩn bị

- Windows 10 hoặc Windows 11.
- Khoảng 2 GB dung lượng trống.
- Kết nối Internet cho lần cài đầu tiên (để tải Python và thư viện).
- Một AI editor để mở thư mục và trò chuyện với AI: [Claude Code](https://docs.anthropic.com/en/docs/claude-code), [Cursor](https://www.cursor.com/) hoặc [Antigravity](https://antigravity.google/).

## Bước 1: Cài Python

Có hai cách:

**Cách 1 — để bộ cài tự làm:** Bấm đúp `CAI-DAT.bat`. Nếu máy chưa có Python, bộ cài sẽ đề nghị cài Python 3.12 qua winget. Trả lời `Y`. Sau khi cài xong, **đóng cửa sổ này** rồi bấm lại `CAI-DAT.bat` để PATH mới có hiệu lực.

**Cách 2 — cài tay:** Tải tại https://www.python.org/downloads/. Khi cài, nhớ **tick "Add python.exe to PATH"**.

Nếu gõ `python` mà Windows mở Microsoft Store thay vì chạy Python: lệnh `python` đang bị lối tắt của Store chiếm chỗ. Vào **Settings → Apps → Advanced app settings → App execution aliases** rồi tắt `python.exe` và `python3.exe`.

Nếu `CAI-DAT.bat` báo đã cài Python nhưng chưa có trong PATH (thường do lúc cài chưa tick ô "Add python.exe to PATH"), xem mục **Đã cài Python nhưng bộ cài báo không tìm thấy** trong [Xử lý lỗi](xu-ly-loi.md).

## Bước 2: Tải bộ công cụ

Chọn một trong hai cách:

- **ZIP:** bấm **Code → Download ZIP** trên trang repo rồi giải nén. Cách này không tự cập nhật được sau này.
- **Git:**
  ```
  git clone https://github.com/luonghaianh1208/2anh-studio.git
  ```

Nên đặt thư mục ở đường dẫn ngắn, ví dụ `D:\PPTmaster`, và tránh đặt trong thư mục đang đồng bộ OneDrive.

## Bước 3: Chạy CAI-DAT.bat

Bấm đúp `CAI-DAT.bat`. Nếu Windows SmartScreen chặn, bấm **More info → Run anyway**.

Bộ cài chạy 4 bước:

1. Kiểm tra Python.
2. Cài thư viện Python.
3. Tạo file cấu hình `.env`.
4. Hỏi Y/N cho từng công cụ tuỳ chọn: Git, Pandoc, FFmpeg.

Sau đó bộ cài tự chạy kiểm tra môi trường.

## Bước 4: Đọc kết quả kiểm tra

Mỗi dòng kết quả bắt đầu bằng một trong ba ký hiệu, kèm nhãn chữ trong ngoặc vuông:

| Ký hiệu | Ý nghĩa |
|---|---|
| ✅ [ĐẠT] | Mục này đạt |
| ⚠️ [CẢNH BÁO] | Mục khuyến nghị hoặc tuỳ chọn chưa có — vẫn dùng được |
| ❌ [LỖI] | Mục bắt buộc bị lỗi — xem dòng `→` ngay bên dưới để biết cách sửa, và xem [Xử lý lỗi](xu-ly-loi.md) |

Trên một số máy Windows 10, biểu tượng có thể hiện thành ô vuông; khi đó hãy đọc nhãn chữ trong ngoặc vuông.

Bốn mục bắt buộc là: **Python**, **Thư viện Python**, **Tính toàn vẹn skill**, **Xuất thử PPTX**.

## Tiếp theo

Cài xong, sang bước [Bắt đầu nhanh](bat-dau-nhanh.md).

<!-- nha-van:exempt — tài liệu kỹ thuật hướng dẫn agent, chứa mẫu rỗng minh hoạ, không phải văn bản gửi-đi thật -->
# Hiển thị Markdown fallback — khi môi trường KHÔNG hỗ trợ tải file .docx

Một số môi trường trò chuyện (chat thuần, preview trong tin nhắn, môi trường sandbox chưa cho
xuất file) chỉ hỗ trợ hiển thị văn bản/Markdown trực tiếp, chưa cho tải file Word ngay. Trường
hợp đó, dựng khối đầu văn bản (Quốc hiệu/tên cơ quan + Nơi nhận/chữ ký) bằng bảng Markdown
2 cột dưới đây để người đọc thấy đúng bố cục — sau đó khi có khả năng xuất file, dùng
`scripts/generate_docx.py` để ra bản `.docx` thật (bảng Markdown chỉ để XEM TRƯỚC, không thay
thế được validate).

## Khối đầu văn bản (header)

```markdown
| UBND HUYỆN ...<br>**UBND XÃ ...** | **CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM**<br>*Độc lập - Tự do - Hạnh phúc* |
|:---:|:---:|
| Số: .../TTr-UBND | *..., ngày ... tháng ... năm 2026* |
```

Render ra:

| UBND HUYỆN ...<br>**UBND XÃ ...** | **CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM**<br>*Độc lập - Tự do - Hạnh phúc* |
|:---:|:---:|
| Số: .../TTr-UBND | *..., ngày ... tháng ... năm 2026* |

## Khối cuối văn bản (nơi nhận + chữ ký)

```markdown
| Nơi nhận: | |
|---|:---:|
| - Như trên; | **CHỦ TỊCH** |
| - Lưu: VT. | |
| | |
| | [CẦN BỔ SUNG: họ tên] |
```

Render ra:

| Nơi nhận: | |
|---|:---:|
| - Như trên; | **CHỦ TỊCH** |
| - Lưu: VT. | |
| | |
| | [CẦN BỔ SUNG: họ tên] |

## Lưu ý

- Đây là bản XEM TRƯỚC nhanh trong chat, KHÔNG phải bản bàn giao cuối. `validate_docx.py` không
  kiểm được Markdown — chỉ kiểm `.docx` thật.
- Khi môi trường cho phép chạy code (sandbox có Python), luôn ưu tiên xuất `.docx` thật qua
  `scripts/generate_docx.py` rồi mới coi là hoàn thành Pha 3.

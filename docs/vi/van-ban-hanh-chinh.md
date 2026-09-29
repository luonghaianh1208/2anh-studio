# Soạn văn bản hành chính theo Nghị định 30

Nhờ AI soạn công văn, tờ trình, quyết định, thông báo, giấy mời, biên bản… ra file Word đúng thể thức Nghị định 30/2020/NĐ-CP: khổ A4, lề, font Times New Roman, quốc hiệu, tên cơ quan, số và ký hiệu, trích yếu, nơi nhận. Bộ sinh và bộ kiểm thể thức là ND30 của tác giả Nguyễn Minh Phát (giấy phép MIT), nhúng trong `tools/vi/nd30`.

## Làm được gì

- Các loại văn bản hành chính của Nghị định 30 và biểu mẫu nội bộ (phiếu). Văn bản quy phạm của HĐND, UBND cũng làm được theo thể thức riêng.
- AI hỏi thầy cô tối đa 7 câu (loại văn bản, gửi ai, nội dung và số liệu, người ký, số và ký hiệu, ngày ban hành, căn cứ), rồi dựng file Word và cho chạy bộ kiểm thể thức.
- **Không hỗ trợ** văn bản của Đảng và văn bản của Đoàn Thanh niên: hai loại này có thể thức riêng.

## Cách nhắn cho AI

```
Soạn công văn cử cô Trần Thị B, giáo viên Toán, đi tập huấn ứng dụng AI ngày 15/10 tại Phòng GD&ĐT
```

```
Làm tờ trình xin kinh phí mua 2 máy chiếu cho tổ Toán, đúng thể thức Nghị định 30
```

Nói chỉ "báo cáo" hoặc "kế hoạch" thì AI hỏi lại: thầy cô cần văn bản Word đúng thể thức Nghị định 30, hay **slide** trình chiếu. Tên cơ quan chủ quản, địa danh và ký hiệu viết tắt của trường được lưu trong hồ sơ đơn vị sau lần đầu, không phải nhắc lại.

## AI không tự bịa

Số văn bản, ngày ban hành, người ký, căn cứ pháp lý, số tiền và số liệu thầy cô chưa cho biết thì AI để ô **`[CẦN BỔ SUNG: …]`** trong văn bản, không tự điền. Còn ô nào thì file là **bản nháp**: AI báo rõ từng ô cần điền. Thầy cô nhắn thông tin còn thiếu để AI điền rồi xuất lại, hoặc sửa thẳng trong Word.

Số văn bản để trống là đúng quy trình: văn thư điền khi vào sổ. Ngày chưa chốt thì AI để trống ngày, ghi tháng và năm.

## File nhận được

AI lưu tại `projects\_van-ban\<tên văn bản>\`:

| File | Nội dung |
|---|---|
| `noi-dung.json` | Nội dung văn bản; sửa file này rồi nhờ AI xuất lại |
| `van-ban.docx` | Văn bản Word đúng thể thức, mở bằng Word sửa tiếp được |
| `kiem-tra.md` | Kết quả bộ kiểm thể thức từng mục (✓ đạt, ⚠ cần soát, ✗ lỗi) và danh sách ô cần bổ sung |

Có lỗi thể thức nặng thì AI không giao file Word mà sửa rồi xuất lại. Mục "Dấu / chữ ký số" lần nào cũng là ⚠ vì máy không kiểm được: thầy cô soát tay.

## Trước khi ban hành

1. Điền đủ mọi ô `[CẦN BỔ SUNG: …]`, đọc lại nội dung.
2. Trình ký, rồi đóng dấu hoặc ký số theo quy trình văn thư của đơn vị. Văn thư vào sổ và điền số.

File AI giao **chưa đóng dấu, chưa ký**; AI không đánh số văn bản và không xuất PDF.

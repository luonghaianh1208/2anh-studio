# Gói chạy thử: ảnh AI của video giải thích trên Antigravity (vi.12)

File dành cho chủ repo. Spec `docs/vi/phat-trien/2026-09-27-video-ma-vi12-design.md` (mục 6 và mục 8) đặt điều kiện phát hành: luồng ảnh AI (`anh_ai.py` → công cụ vẽ của nền tảng → `anh_ai.py nhan` → `video_ma.py --xem-truoc`) phải chạy thật một lần trên Antigravity. Kết quả lần chạy này quyết định vi.12 có phát hành phần nhân vật AI (`nhan-vat: ve:`) hay chỉ phát hành người que và nền mẫu.

Lần chạy kiểm hai điều:

- AI của Antigravity tự đi đúng luồng chỉ nhờ luật trong repo (`AGENTS.vi.md` §15, `.agents/rules/ppt-master-vi.md`, `docs/vi/tro-ly/video-giai-thich.md` mục "Hình do AI vẽ"), không cần câu khởi động riêng.
- Ảnh Nano Banana Pro qua được bước nhận: nhân vật giống nhau ở ba tư thế, tách nền sạch, không có chữ.

## 1. Chuẩn bị

- Mở thư mục repo (nhánh `feat/vi-video-vi12`) trong Antigravity. Máy đã cài đủ bộ công cụ: `KIEM-TRA.bat` báo sẵn sàng, có Chromium và FFmpeg.
- Không cần tạo thư mục hay file nào trước: câu lệnh ở mục 3 đưa sẵn kịch bản, AI tự tạo `projects/_video/thu-anh-ai/`.
- Chọn mô hình tác tử có công cụ tạo ảnh (Nano Banana Pro). Không bật chế độ tự chạy lệnh mà không hỏi, để chủ repo thấy từng lệnh.

## 2. Kịch bản thử

Ba cảnh, phong cách cắt dán, khổ ngang. Nhân vật AI xuất hiện ở ba tư thế (`chao`, `giai-thich`, `an-mung`); hai cảnh kể chuyện có nền `ve:` khác nhau. Mô tả nhân vật cố ý có kính và màu áo, váy rõ ràng để dễ so ba tư thế, và không có màu xanh lá (nền tách là #00FF00).

```
---
tieu-de: Vì sao lá cây có màu xanh
mon: Khoa học tự nhiên
lop: 7
phong-cach: cat-dan
nhan-vat: ve: cô bé học sinh tóc đen buộc đuôi ngựa, áo sơ mi trắng, váy xanh tím than, đeo kính tròn, dáng tươi vui
---

## Cảnh 1
loai: ke-chuyen
tieu-de: Lá cây xanh vì sao?
nen: ve: khu vườn trường buổi sáng, hàng cây xanh hai bên lối đi, bầu trời trong
tu-the: chao
loi: Chào các em! Các em có bao giờ tự hỏi, vì sao lá cây lại có màu xanh?

## Cảnh 2
loai: khai-niem
thuat-ngu: Diệp lục
dinh-nghia: Sắc tố trong lục lạp của lá, hấp thụ ánh sáng đỏ và xanh tím, phản xạ ánh sáng ==xanh lục==.
tu-the: giai-thich
loi: Trong lá có một sắc tố tên là diệp lục. Diệp lục hấp thụ ánh sáng đỏ và xanh tím, nhưng phản xạ ánh sáng xanh lục.

## Cảnh 3
loai: ke-chuyen
tieu-de: Mắt ta thấy màu xanh
nen: ve: phòng thí nghiệm sinh học sáng sủa, kính hiển vi trên bàn, chậu cây nhỏ cạnh cửa sổ
tu-the: an-mung
loi: Ánh sáng xanh lục phản xạ vào mắt ta, nên ta thấy lá cây màu xanh.
```

Kịch bản này đã qua `video_ma.py --plan-only` về cú pháp (lỗi duy nhất là thiếu ảnh AI, đúng như chờ đợi). `anh_ai.py ke-hoach` của nó ra 6 mục, theo đúng thứ tự:

| File trong `anh/ai/goc/` | Loại | Kích thước | Ảnh tham chiếu | Cảnh |
|---|---|---|---|---|
| `nhan-vat-mau.png` | nhân vật mẫu | 1024x1536 | — | 1, 2, 3 |
| `tu-the-chao.png` | tư thế | 1024x1536 | `goc/nhan-vat-mau.png` | 1 |
| `tu-the-giai-thich.png` | tư thế | 1024x1536 | `goc/nhan-vat-mau.png` | 2 |
| `tu-the-an-mung.png` | tư thế | 1024x1536 | `goc/nhan-vat-mau.png` | 3 |
| `nen-1.png` | nền | 1920x1080 | — | 1 |
| `nen-3.png` | nền | 1920x1080 | — | 3 |

## 3. Câu lệnh dán vào Antigravity

Dán nguyên văn khối dưới vào khung chat của Antigravity, một lần, không thêm gì:

```
Làm video giải thích kiểu cắt dán, có nhân vật do AI vẽ, cho bài "Vì sao lá cây có màu xanh" (Khoa học tự nhiên 7). Em dùng đúng kịch bản dưới đây, lưu thành projects/_video/thu-anh-ai/video.md; kịch bản, nhân vật và nền đã được duyệt, không cần hỏi lại. Dùng công cụ tạo ảnh của em (Nano Banana Pro) để vẽ ảnh nhân vật và ảnh nền theo đúng các bước trong hướng dẫn của repo. Làm tới bước xem trước (--xem-truoc) thì dừng, chưa dựng video thật: gửi tôi ảnh xem trước từng cảnh, nguyên văn dòng JSON của mỗi lệnh anh_ai.py và video_ma.py đã chạy, và cho biết em đã vẽ lại ảnh nào, vì sao.

---
tieu-de: Vì sao lá cây có màu xanh
mon: Khoa học tự nhiên
lop: 7
phong-cach: cat-dan
nhan-vat: ve: cô bé học sinh tóc đen buộc đuôi ngựa, áo sơ mi trắng, váy xanh tím than, đeo kính tròn, dáng tươi vui
---

## Cảnh 1
loai: ke-chuyen
tieu-de: Lá cây xanh vì sao?
nen: ve: khu vườn trường buổi sáng, hàng cây xanh hai bên lối đi, bầu trời trong
tu-the: chao
loi: Chào các em! Các em có bao giờ tự hỏi, vì sao lá cây lại có màu xanh?

## Cảnh 2
loai: khai-niem
thuat-ngu: Diệp lục
dinh-nghia: Sắc tố trong lục lạp của lá, hấp thụ ánh sáng đỏ và xanh tím, phản xạ ánh sáng ==xanh lục==.
tu-the: giai-thich
loi: Trong lá có một sắc tố tên là diệp lục. Diệp lục hấp thụ ánh sáng đỏ và xanh tím, nhưng phản xạ ánh sáng xanh lục.

## Cảnh 3
loai: ke-chuyen
tieu-de: Mắt ta thấy màu xanh
nen: ve: phòng thí nghiệm sinh học sáng sủa, kính hiển vi trên bàn, chậu cây nhỏ cạnh cửa sổ
tu-the: an-mung
loi: Ánh sáng xanh lục phản xạ vào mắt ta, nên ta thấy lá cây màu xanh.
```

Câu lệnh cố ý không nhắc tên `anh_ai.py`, `ke-hoach.json` hay nền xanh #00FF00: AI phải tự tìm các bước đó trong luật của repo. Đó là một phần của phép thử.

Trình tự đúng mà AI phải tự làm (để chủ repo đối chiếu, không dán vào chat):

1. Chạy `tools/vi/doctor.py --no-smoke --json` (AGENTS.vi.md §9), rồi ghi `video.md`.
2. `python tools\vi\anh_ai.py projects\_video\thu-anh-ai ke-hoach` (dùng `venv\Scripts\python.exe` nếu có).
3. Đọc `anh/ai/ke-hoach.json`, dán nguyên văn `prompt` của từng mục vào công cụ vẽ: `nhan-vat-mau.png` trước; mỗi `tu-the-*.png` kèm `goc/nhan-vat-mau.png` làm ảnh tham chiếu; rồi `nen-1.png`, `nen-3.png`. Lưu đúng tên vào `anh/ai/goc/`, không tự cắt hay sửa ảnh.
4. `python tools\vi\anh_ai.py projects\_video\thu-anh-ai nhan --cong-cu "Antigravity" --mo-hinh "Nano Banana Pro"`. Lỗi `tach-nen` hay `thieu` thì vẽ lại đúng ảnh bị nêu rồi chạy lại `nhan`.
5. `python tools\vi\video_ma.py projects\_video\thu-anh-ai --plan-only`, rồi `--xem-truoc`; mở `xem-truoc/canh-1.png` … `canh-3.png` và gửi lên chat.

## 4. Những gì chụp lại gửi về

Gửi một thư mục nén hoặc các file sau (đường dẫn tính từ `projects/_video/thu-anh-ai/`):

| Gửi | Để kiểm |
|---|---|
| `xem-truoc/canh-1.png`, `canh-2.png`, `canh-3.png` | nhân vật trong khung, nền, chữ Việt, viền xanh |
| Toàn bộ `anh/ai/goc/` (ảnh gốc AI vẽ, kể cả bản vẽ lại nếu còn) | chữ lạ trong ảnh, nền xanh có thuần không, bóng đổ |
| `anh/ai/nhan-vat-mau.png`, `anh/ai/tu-the-*.png`, `anh/ai/nen-1.jpg`, `anh/ai/nen-3.jpg` | kết quả tách nền và cắt khổ |
| `anh/ai/ke-hoach.json`, `anh/ai/nguon.json` | câu lệnh AI đã dán, mô hình và công cụ được ghi |
| Nguyên văn các dòng JSON của `anh_ai.py ke-hoach`, `anh_ai.py nhan` (mọi lần chạy, kể cả lần lỗi), `video_ma.py --plan-only`, `video_ma.py --xem-truoc` | `error.step`, `warnings` (ảnh nhỏ hơn Full HD…) |
| Ảnh chụp màn hình khung chat Antigravity từ câu lệnh tới lúc dừng | AI có tự tìm đúng luồng không, có hỏi lại không cần thiết, có tự sửa ảnh hay tự viết `nguon.json` không |
| Một dòng ghi: số lần vẽ lại từng ảnh và lý do | độ ổn định của công cụ vẽ |

## 5. Tiêu chí đạt

Đạt khi đủ cả sáu điều:

1. **Nhân vật đồng nhất ở 3 tư thế.** Đặt `tu-the-chao.png`, `tu-the-giai-thich.png`, `tu-the-an-mung.png` cạnh nhau: cùng khuôn mặt, kiểu tóc buộc đuôi ngựa, kính tròn, áo trắng, váy xanh tím than, cùng tỉ lệ đầu và thân. Một học sinh nhìn ba ảnh phải nói ngay là cùng một người. Dáng khớp tên tư thế (vẫy tay, xoè tay giảng, hai tay giơ cao).
2. **Tách nền sạch, không viền xanh.** `anh_ai.py nhan` ra `ready: true` (tối đa một lần vẽ lại mỗi ảnh nhân vật vì `tach-nen`). Trên `xem-truoc`, phóng to mép tóc, tay, váy: không có viền hay vệt xanh lá, không có mảng nền xanh sót lại, không có bóng đổ thành vệt mờ dưới chân.
3. **Không có chữ trong ảnh.** Mọi ảnh trong `anh/ai/goc/` và `anh/ai/` không có chữ, số, logo, chữ ký, kể cả chữ nhỏ trên bảng, sách, biển. Chữ duy nhất trên `xem-truoc` là chữ công cụ viết (nhãn tiêu đề, định nghĩa, phụ đề), đúng dấu tiếng Việt.
4. **Nền dùng được.** `nen-1.jpg`, `nen-3.jpg` đúng 1920x1080 (hoặc có cảnh báo "nhỏ hơn Full HD" nêu rõ), đúng mô tả, vùng giữa đủ dịu để nhãn tiêu đề và nhân vật đọc được.
5. **Nguồn được ghi.** `anh/ai/nguon.json` có đủ 6 mục, mô hình "Nano Banana Pro"; AI không tự viết file này.
6. **AI đi đúng luồng không cần nhắc.** Không chạy `video_ma.py` dựng thật trước khi gửi xem trước; không tự cắt, tách nền hay sửa ảnh bằng cách khác; không đặt ảnh thẳng vào `anh/ai/`.

Quyết định sau lần chạy:

- **Đạt cả sáu:** phát hành vi.12 kèm nhân vật AI như tài liệu hiện tại.
- **Trượt 1 (nhân vật không đồng nhất) sau hai lần vẽ lại:** phát hành vi.12 với người que và nền mẫu; giữ `nen: ve:` (nền AI không cần đồng nhất); ghi `nhan-vat: ve:` là "thử nghiệm" trong `video-giai-thich.md`, hoặc tạm ẩn khỏi bộ câu hỏi, và mở việc cải thiện câu lệnh tư thế.
- **Trượt 2 hay 3:** ghi lại màu nền đo được và ảnh lỗi, sửa câu lệnh hoặc ngưỡng tách nền trong `tools/vi/anh_ai_parts/` rồi chạy lại gói này.
- **Trượt 6:** sửa luật trong `.agents/rules/ppt-master-vi.md` và `AGENTS.vi.md` §15 cho rõ hơn, rồi chạy lại gói này trong một cuộc trò chuyện mới.

## 6. Dọn sau khi chạy

Thư mục `projects/_video/thu-anh-ai/` không commit (`projects/` bị bỏ qua trong `.gitignore`). Giữ lại tới khi có quyết định phát hành, rồi xoá.

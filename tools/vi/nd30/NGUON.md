# Nguồn gốc: mã ND30

- **Repo gốc:** https://github.com/kanazawahere/nd30
- **Commit:** `b683ff9a3d74221802d073dcd10bd2aa3823087d`
- **Ngày lấy:** 2026-09-29
- **Giấy phép:** MIT License, © 2026 Nguyễn Minh Phát (ATP / Agent Do Agency) — xem `LICENSE` trong thư mục này.

Toàn bộ file dưới đây lấy bằng `git -c core.autocrlf=false archive` ở commit trên (dòng kết thúc LF như trong repo gốc), không sửa nội dung: SHA-256 của từng file trùng SHA-256 của blob tương ứng (`git show <commit>:<đường dẫn>`). `.gitattributes` gốc của repo có dòng `tools/vi/nd30/** -text` để git không đổi CRLF/LF khi checkout, giữ đúng SHA-256.

## Bỏ không nhúng

| Đường dẫn ở repo gốc | Lý do bỏ |
|---|---|
| `SPARK-INSTRUCTIONS.md` | Nhắc công cụ riêng của tác giả (`/biensoan`, `/atp-deliver`), không dùng trong bản Việt |
| `pack-for-spark.sh` | Script đóng gói riêng cho hạ tầng Spark của tác giả |
| `README.en.md`, `README.ja.md`, `README.zh.md` | Chỉ giữ `README.md`; các bản dịch khác không cần |
| `_linh-moi-2026-08-27.md` | Ghi chú nội bộ của tác giả cho commit, không phải tài liệu vận hành |
| `assets/samples/` (và `assets/` nói chung) | Ví dụ minh hoạ ngoài luồng, không được `scripts/` tham chiếu |
| `tests/` | Test gốc của ND30 cần `pytest`; theo ràng buộc dự án, không nhúng test gốc |
| `.gitignore` (gốc và trong `scripts/`, `tests/`) | File cấu hình git của repo gốc, không cần trong bản nhúng |
| `scripts/__pycache__/`, `tests/__pycache__/` | File biên dịch tạm, không phải mã nguồn |

## Bảng SHA-256

| đường dẫn tương đối | sha256 |
|---|---|
| LICENSE | 8c618bd499a693bbbf905a4dc4c276db6a09a9abb190e05a2e2b2b978fb6cc3a |
| PHAN-LUONG.md | a0aa2e994c44c5a0fdd360e19701a1d7638727bb65133c5ab80f5cf92fe125b7 |
| README.md | dd842f49c0805addbe2f674e8eae84d64d501557c46d728ce8a52ba540d8ee89 |
| SKILL.md | b7c5abd5e7efd9ad6889f3b35acd1c201f1d949e60335c6992b2c905539ccc42 |
| examples/bien_ban.json | 5e24297eb01bff5dc210f8d6a68b6cd4be0b864587c063a447bd6350cb961977 |
| examples/cong_van.json | 97dac5c34dea0796016c9084b06814ec1a1b6ccfe5077d357056b9bc3d967864 |
| examples/giay_moi.json | eacd416b7aaaf634b528b3337cb7aec393b8b2aee099ec7f63abd123abe21675 |
| examples/input-sample.json | bac9e87eb5028707e2aa24df55914ebefb431d3b61fe5306a567a43541a32c39 |
| examples/nghi_quyet_hdnd.json | 9ac4f196a0a22f5ae6388d6c31d8041eec65474aaa6f3daefed3c8278b117ac2 |
| examples/nghi_quyet_hdnd_kem_quy_dinh.json | 10b2800f9c35f4b22def6fdc3fcd9849c9b76560d39d3a4b37fc08ae1e5d5bb8 |
| examples/quyet_dinh.json | 90ec0a4a189192ba802f91f873a0668830ab393bc2812a0d99c95218aaf255b7 |
| examples/quyet_dinh_ubnd_qppl.json | 563b1cf0f8ee68356d3e7b83cfedd84d874836fbc193cbd72b9a0c3ca64c5e01 |
| examples/thong_bao.json | 656febdf2e43fef261884d5d84935857dcbbec246202bd939559ab143ad798ac |
| llms.txt | f13ca06f54b9ecdf9142e9f7b79d2df926fce258f1f6e92680662a3b9fe3399a |
| references/danh-muc-loai-vb.md | f178efa8ea3ade3249e90e6e66061d2beb36633262d542c587cd5733f9f57ee8 |
| references/document-profiles.md | 8bcc641d9180e6d6e78ebe7b0a1ce6d3c49b8de03c75b91f8173f7fae84a49d0 |
| references/editorial-quality-vi.md | 58e39cf9f452869ab549f166204f9b569194a974351f5b755123334832dcc5ac |
| references/hien-thi-markdown-fallback.md | 4c02e49806cc3277fd1d1a786dfb9e666f8703fe1cdba4c43e2be338189c8798 |
| references/interview-questions.md | ac31cefa8a0991cb33d6dff539a97af8dc15eb08dd38b3a0eda821b6311188fe |
| references/the-thuc-nd30.md | 04be2490fe2eec0b42932b6b43f67d6f4ece8e1299d0887063bd78f2b8d714b1 |
| references/the-thuc-qppl-nq-hdnd.md | 9c71926338881f0a25a49ee228edf2705257da3cd35b8478c8c8e72e2296dd4f |
| references/the-thuc-qppl-qd-ubnd.md | bab1e9841da9931b1dbc6924eeadecc8bb656edf4d072d5fed4682603e2096c0 |
| references/validation-checklist.md | 2a0b123b250703dec18adf74fe5a56ef2ddea89b7ab858fd371e0964d693128d |
| schemas/nd30-input.schema.json | 02a0b15ffaf953180235ac1b918241fae7ce39043467b213e930bb2800e72a21 |
| scripts/_common.py | baecd402e84f9dd992d5a3aa7b610cb2871b54f440d1eec8283db995bc972c16 |
| scripts/build_docx.py | 71098e49bfc14182529ba9b52c264275c017b868c9a22f9297539230faaf171b |
| scripts/fill_template.py | d382ddb252ab3a1892d1408e7d19dc8859dc645a1918fe855b7a6cbda72abe86 |
| scripts/find_placeholders.py | f06fe4f59186e9693347271c35e97a28e1bef9a4f81bc3b0f058d2dafcd423ee |
| scripts/generate_docx.py | 197236b53b969e23a86f9d47d7781b6965f40507d4a7645fd1f53dffda04aed9 |
| scripts/inspect_docx.py | a26bea9a7b58f4cdc568be60cb0e757e5e403277f12abecfb483108b0aff5800 |
| scripts/learn_template.py | 6123dacfd3e1c821fc1b77409057ee145570cd1682d03ba26992a3f1873a2bb2 |
| scripts/normalize_template.py | fb62f513da3b897c7690b51f8c93357c3048e5cdaa98c33bc60b3b17a2ed3c4d |
| scripts/render_docx.py | 2630742c481602097ececc4b0b88a2daea4ab874f067f89e17787bafc62a6564 |
| scripts/rules/loai-vb.yaml | a6802542421fe2543a02f6be89cfe92f178e0692c5fe5188a462e1e63cf3ef28 |
| scripts/rules/the-thuc.yaml | 9d287c3c74a09652b152d68c011b542490e3f201a794eeb453d0054547849bc1 |
| scripts/rules/typo-fixes.yaml | 94b3f2e31f7c4fe702342e5670fddcc0b0b3964156bcd51d636f9c7e91f88e7f |
| scripts/rules_loader.py | 2a538e51be70f853bef053c98cfe60b754baa83d52e183d1c60205ac9fdd18f7 |
| scripts/validate_docx.py | b5fb9bc5054a540c1dee1709a2cde2615dfe78a105f0b40d36c29310e0fc9976 |
| templates/_build_templates.py | ab6d91750f172a8cbfe1f4457c574ebb9df02ed4ad3cca95490d742555acc977 |
| templates/bao-cao.docx | 6db15d729ed2d901620023b9da71412076966219eed9e892fb06189c387bfefb |
| templates/cong-van.docx | 5816ead12bd2cfd889163cf8cd209e2f1c478b26affc799f3f24a7bea1e44863 |
| templates/ke-hoach.docx | 42f5938b07c7cb60d1e704ee2256b77c0da106380b84e725be507b5a3ce0f680 |
| templates/quyet-dinh.docx | 9a7880f979dc69a1df02fd776a3106c7d64f595aca9b3d9a4a0d052e99f6af4a |
| templates/to-trinh.docx | 500d0fefa1f3f74c7bb11418cada8d9d559dce10c81907539c1ab845b9c5ae39 |

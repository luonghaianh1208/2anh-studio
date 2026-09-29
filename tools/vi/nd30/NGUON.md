# Nguồn gốc: mã ND30

- **Repo gốc:** https://github.com/kanazawahere/nd30
- **Commit:** `b683ff9a3d74221802d073dcd10bd2aa3823087d`
- **Ngày lấy:** 2026-09-29
- **Giấy phép:** MIT License, © 2026 Nguyễn Minh Phát (ATP / Agent Do Agency) — xem `LICENSE` trong thư mục này.

Toàn bộ file dưới đây được chép byte-cho-byte từ commit trên, không sửa nội dung. `.gitattributes` gốc của repo có dòng `tools/vi/nd30/** -text` để git không đổi CRLF/LF khi checkout, giữ đúng SHA-256.

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
| LICENSE | 6a5c9ab7051cb9eb64710a95178227e0d5004a1a73f75dd58d6afbbb07fe6fbf |
| PHAN-LUONG.md | 8b2840a01fcc4a57f93c3473ab5b74f30b45464b32f5d33385b7f4c6ca9fb469 |
| README.md | b1086e860742b4b41cf48ba1d17a41f5a1fafc1c32d85e6dac38a019dc91811a |
| SKILL.md | 9bc074abd9f791351fe708fcb8aaaeba01f62a05c24af746f14049790c78e7df |
| examples/bien_ban.json | 36fd2fb8121411bcb3e0db85f4cab1621551f4a8f1533ca8f419bcf95e14d1ba |
| examples/cong_van.json | 18b5501f2cb50593d9d31e88366fb3155023acfae78d0272f9e0c7d587bf2325 |
| examples/giay_moi.json | 0efca864a0d59c0de76a80f1d922b78ac42cf3db1759273e4b29b73f270371df |
| examples/input-sample.json | f9557458d916692eeaf2c2e728d4b120ca26e070d8699c7ef6c0389fd3d2a7fb |
| examples/nghi_quyet_hdnd.json | 10c562d615d545930c98ef53f9015e3ff4341139826e04eb556179a9ecffe874 |
| examples/nghi_quyet_hdnd_kem_quy_dinh.json | 5aa13bdae417293b5ce2fcc57311a098a9e122b16378f2044fa4915c865f0ed6 |
| examples/quyet_dinh.json | 2269cebbbb8ccfb348e46aed9114a273dd04f3185af44e43625e8c6712b39632 |
| examples/quyet_dinh_ubnd_qppl.json | 1e930c8102411391220b2a104ab3faed72add79000a05524a866e81b61dbc20b |
| examples/thong_bao.json | 3bd8834eee660a10090f32c17ad10db50243ee3aa9770b119287199da19d1382 |
| llms.txt | cdfcfa971a4026144500d1b139be11712e7bb8966cc9bfd42705e47bef68e19d |
| references/danh-muc-loai-vb.md | 036b4f1c0736061f12afee89b12b0adc6a77433f5599b8fb04a90c0a52741019 |
| references/document-profiles.md | 5ac8dbb56f2682c5fb90763afbe6ebf380142803e9763ad446ce9c5da3fe78ee |
| references/editorial-quality-vi.md | f8dae3e232c86aee6be6da618519eb5b6571a4f9e55d0f011e6f6adf7f01d6bd |
| references/hien-thi-markdown-fallback.md | 0081c94cbaa0c6b3a32fc94fbd0ddc3078006d6d023be49dddadafefa89302c2 |
| references/interview-questions.md | c8f1dcc1e4fa8f0679bd018579f6e73ca3c4b4c1690885e1b2103e2884f9e7b5 |
| references/the-thuc-nd30.md | bd969ebf78b52b37f412a7aabb8863d4529aede92c78ca3f6f0788d0a23bd73f |
| references/the-thuc-qppl-nq-hdnd.md | 154819b7acbb216856939695c22c2dce4f63f35e6346be13e37e8a0ecc453a21 |
| references/the-thuc-qppl-qd-ubnd.md | f5f293f67920692840303b9dc008aa2f12d4a23ca433d5c32667ecae0cee4418 |
| references/validation-checklist.md | c32cc8cf8046c9d76564ddba002e77b99eb1bdb2a75c3ece20c83436aec412b2 |
| schemas/nd30-input.schema.json | 403101e9922a7e3a52dac8ff49605d049c276c75888d25a545ee42dd47478266 |
| scripts/_common.py | 64f7c3dcab3ce47c2e8dc647af96de55a1f75c858cad9920cf02ab9b083d4402 |
| scripts/build_docx.py | 06b7a6e2cd43fcd43498304caef33bee41fb9c16e74ded6e9268dbc8b24ffc69 |
| scripts/fill_template.py | 56c106eed7b87a734c96ca36ed779248d8e297c9ea67423c8c8d2d8b84d2d94e |
| scripts/find_placeholders.py | 9f5f5be4db0e980719b4ef40c1356368f3edc1f7b737428e77718278cf79ca8e |
| scripts/generate_docx.py | aec7d49817559511a0420b5e2de2ce14b53f504f7127f5ee62bddea0454e3693 |
| scripts/inspect_docx.py | 9bd97bee28990050c3c4fa873e5332539693728c7d8ae014426f3390db64d0c3 |
| scripts/learn_template.py | c5b95cf63d6a09c915bee22a303cdd1802ce997995e94dc62a9648754f8dc636 |
| scripts/normalize_template.py | 551c30c95dc8244209ffec2601d85935d55c4826102adb39e4033e39fb03470a |
| scripts/render_docx.py | 190f8d272b73f59fdf0ba691bf6f1fea176e1698fd497312cd736e22b30c9293 |
| scripts/rules/loai-vb.yaml | 1f34ef8c507465120d382566d83a0f297f266e34babbbf9ff815c1f56665bc7d |
| scripts/rules/the-thuc.yaml | 6b0e3945431e0b6788ed03bf317740087cb9af5c9204bd567801aaaf87b50964 |
| scripts/rules/typo-fixes.yaml | fa40e282e616e1b6e6c702e1ed546bfbe3a40a03192bd2926195a65b85e9b421 |
| scripts/rules_loader.py | 105ca893ef5f96d05368e63dc11d13a0d9b24fff25b56a38a387032678ae3eee |
| scripts/validate_docx.py | 5641b0bfb850dc02b2bcd614864c4649d7cfedaa55935c321cf3463debd359ce |
| templates/_build_templates.py | c3c50d1f65d653e344d81d6d0452233d48a59cbd229be2b0f6974bc33dff9d29 |
| templates/bao-cao.docx | 6db15d729ed2d901620023b9da71412076966219eed9e892fb06189c387bfefb |
| templates/cong-van.docx | 5816ead12bd2cfd889163cf8cd209e2f1c478b26affc799f3f24a7bea1e44863 |
| templates/ke-hoach.docx | 42f5938b07c7cb60d1e704ee2256b77c0da106380b84e725be507b5a3ce0f680 |
| templates/quyet-dinh.docx | 9a7880f979dc69a1df02fd776a3106c7d64f595aca9b3d9a4a0d052e99f6af4a |
| templates/to-trinh.docx | 500d0fefa1f3f74c7bb11418cada8d9d559dce10c81907539c1ab845b9c5ae39 |

"""Danh mục giọng VieNeu (không import gì, để parse.py và giong.py cùng dùng mà không vòng import)."""

# Mỗi giọng: (tên trong VieNeu, giới "nu"/"nam", vùng, chất giọng) — chất giọng để AI chọn giọng hợp nội dung
# (docs/vi/tro-ly/chon-giong.md). Máy không có VieNeu thì lùi về giọng edge-tts cùng giới (`giong_du_phong`).
VIENEU = {
    "thu-giang": ("Thu Giang", "nu", "Bắc", "MC dẫn chương trình"),
    "ngoc-huyen": ("Ngọc Huyền", "nu", "Bắc", "tự nhiên"),
    "truc-ly": ("Trúc Ly", "nu", "Bắc", "tự nhiên"),
    "doan-trang": ("Đoan Trang", "nu", "Bắc", "tự nhiên"),
    "ngoc-linh": ("Ngọc Linh", "nu", "Bắc", "kể chuyện"),
    "mai-anh": ("Mai Anh", "nu", "Bắc", "tin tức"),
    "quynh-anh": ("Quỳnh Anh", "nu", "Bắc", "đọc truyện"),
    "ngoc-tran": ("Ngọc Trân", "nu", "Trung", "tự nhiên"),
    "thuc-doan": ("Thục Đoan", "nu", "Nam", "kể chuyện"),
    "thuy-dung": ("Thùy Dung", "nu", "Nam", "tin tức"),
    "my-duyen": ("Mỹ Duyên", "nu", "Nam", "đọc truyện"),
    "kim-thanh": ("Kim Thanh", "nu", "Nam", "đọc truyện"),
    "pham-tuyen": ("Phạm Tuyên", "nam", "Bắc", "tự nhiên"),
    "xuan-vinh": ("Xuân Vĩnh", "nam", "Bắc", "tự nhiên"),
    "manh-dung": ("Mạnh Dũng", "nam", "Bắc", "tự nhiên"),
    "minh-quan": ("Minh Quân", "nam", "Bắc", "tự nhiên"),
    "minh-duc": ("Minh Đức", "nam", "Bắc", "tin tức"),
    "thanh-binh": ("Thanh Bình", "nam", "Bắc", "kể chuyện"),
    "anh-khoi": ("Anh Khôi", "nam", "Bắc", "kể chuyện"),
    "quang-son": ("Quang Sơn", "nam", "Trung", "tự nhiên"),
    "thai-son": ("Thái Sơn", "nam", "Nam", "kể chuyện"),
    "minh-triet": ("Minh Triết", "nam", "Nam", "tin tức"),
    "duc-tri": ("Đức Trí", "nam", "Nam", "đọc truyện"),
    "adam": ("Adam", "nam", "Nam", "tự nhiên"),
}

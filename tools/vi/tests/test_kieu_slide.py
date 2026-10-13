"""Danh mục kiểu slide (docs/vi/tro-ly/kieu-slide.md) và bộ hoạ tiết SVG (tools/vi/hoa_tiet/): tên trong tài liệu khớp
file thật, hoạ tiết chỉ dùng hình cơ bản mà bộ xuất của upstream đổi được thành hình PowerPoint gốc."""
import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
DOC = REPO / "docs" / "vi" / "tro-ly" / "kieu-slide.md"
HT = REPO / "tools" / "vi" / "hoa_tiet"
SVG = "{http://www.w3.org/2000/svg}"
HINH = {"polygon", "polyline", "path", "circle", "rect", "line"}
KIEU = ("Học đường sáng", "Bút dạ – sổ tay", "Cắt dán giấy", "Sách tranh tiểu học", "Ruy băng hành chính",
        "Lễ hội Đoàn", "Học thuật – hội thảo", "Kính mờ CLB")
LOAI_VIEC = ("bai-giang.md", "bao-cao-tong-ket.md", "hoat-dong-doan.md", "poster-mang-xa-hoi.md", "tap-huan-workshop.md")


def doc():
    return DOC.read_text(encoding="utf-8")


def muc(text, tieu_de):
    a = text.index(tieu_de)
    m = re.search(r"^#{2,3} ", text[a + len(tieu_de):], re.M)
    return text[a:a + len(tieu_de) + (m.start() if m else len(text))]


class KieuSlideTest(unittest.TestCase):
    def test_eight_named_styles_each_with_three_palettes_and_fit_rules(self):
        t = doc()
        for ten in KIEU:
            with self.subTest(kieu=ten):
                than = muc(t, f"### {ten}")
                for nhan in ("- Nhìn:", "- Hợp với:", "- Không hợp với:", "- Bảng màu", "- Chữ:", "- Hoạ tiết:", "- Upstream:"):
                    self.assertIn(nhan, than)
                bang = [l for l in than.splitlines() if re.match(r"^  - \S.*: `#", l)]
                self.assertEqual(len(bang), 3, bang)
                for l in bang:
                    for mau in re.findall(r"`(#[^`]*)`", l):
                        self.assertRegex(mau, r"^#[0-9A-F]{6}$")

    def test_upstream_style_and_layout_names_exist(self):
        t = doc()
        styles = REPO / "skills" / "ppt-master" / "templates" / "styles"
        layouts = REPO / "skills" / "ppt-master" / "templates" / "layouts"
        for dong in (l for l in t.splitlines() if l.startswith("- Upstream:")):
            for ten in re.findall(r"style `([^`]+)`", dong):
                self.assertTrue((styles / ten).is_dir(), ten)
            for ten in re.findall(r"layout `([^`]+)`", dong) + re.findall(r"hoặc `([a-z_0-9]+)`", dong):
                self.assertTrue((layouts / ten).is_dir() or (styles / ten).is_dir(), ten)

    def test_every_task_guide_points_to_the_catalogue(self):
        for ten in LOAI_VIEC:
            with self.subTest(file=ten):
                than = (REPO / "docs" / "vi" / "tro-ly" / ten).read_text(encoding="utf-8")
                self.assertIn("kieu-slide.md", muc(than, "## Phong cách gợi ý"))
        qt = (REPO / "docs" / "vi" / "tro-ly" / "quy-trinh-hoi.md").read_text(encoding="utf-8")
        self.assertIn("kieu-slide.md", muc(qt, "## Kiểu nhìn"))
        self.assertIn("Kiểu nhìn:", (REPO / "docs" / "vi" / "tro-ly" / "mau-brief.md").read_text(encoding="utf-8"))

    def test_lesson_guide_has_the_5512_page_roles(self):
        than = muc((REPO / "docs" / "vi" / "tro-ly" / "bai-giang.md").read_text(encoding="utf-8"), "## Cấu trúc gợi ý")
        for vai in ("Bìa", "Mục tiêu", "Mở đầu", "Hình thành kiến thức mới", "Luyện tập", "Vận dụng", "Tổng kết", "Dặn dò",
                    "Ghi chú người nói"):
            with self.subTest(vai=vai):
                self.assertIn(vai, than)


class HoaTietTest(unittest.TestCase):
    def bang(self):
        than = muc(doc(), "## Hoạ tiết")
        return {m.group(1): m.group(2) for m in re.finditer(r"^\| `([a-z-]+)` \| [^|]+ \| (có|không) \|$", than, re.M)}

    def test_table_and_files_match(self):
        self.assertEqual(set(self.bang()), {p.stem for p in HT.glob("*.svg")})
        self.assertEqual(len(self.bang()), 12)

    def test_each_motif_is_one_symbol_of_plain_shapes_with_hex_colours(self):
        keo = self.bang()
        for p in sorted(HT.glob("*.svg")):
            with self.subTest(file=p.name):
                goc = ET.parse(p).getroot()
                syms = goc.findall(f"{SVG}defs/{SVG}symbol")
                self.assertEqual(len(syms), 1)
                sym = syms[0]
                self.assertEqual(sym.get("id"), f"ht-{p.stem}")
                self.assertEqual(sym.get("viewBox"), goc.get("viewBox"))
                self.assertEqual(sym.get("preserveAspectRatio") == "none", keo[p.stem] == "có")
                for el in sym:
                    self.assertIn(el.tag.replace(SVG, ""), HINH)
                    for thuoc_tinh in ("fill", "stroke"):
                        v = el.get(thuoc_tinh)
                        if v is not None:
                            self.assertRegex(v, r"^(none|#[0-9A-F]{6})$")
                    tf = el.get("transform")
                    if tf is not None:
                        self.assertRegex(tf, r"^rotate\(")
                    self.assertIsNone(el.get("style"))
                    self.assertIsNone(el.get("class"))


if __name__ == "__main__":
    unittest.main()

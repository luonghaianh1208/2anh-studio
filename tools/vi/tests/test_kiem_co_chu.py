"""kiem_co_chu.py: cỡ chữ slide trình chiếu tối thiểu 24pt (1px SVG = 0,75pt), dòng nguồn và số trang từ 18pt."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

VI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(VI))

import kiem_co_chu  # noqa: E402

DAU = '<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="Segoe UI" font-size="{goc}">'


def trang(than, w=1280, h=720, goc=32):
    return DAU.format(w=w, h=h, goc=goc) + than + "</svg>"


class KiemCoChuTest(unittest.TestCase):
    def chay(self, *cac_trang, **kw):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp) / "svg_output"
            d.mkdir()
            for i, t in enumerate(cac_trang, 1):
                (d / f"{i:02d}_t.svg").write_text(t, encoding="utf-8")
            return kiem_co_chu.chay(Path(tmp), kw.get("toi_thieu", 24.0), kw.get("noi_dung", 28.0))

    def test_px_to_pt_follows_the_exporter(self):
        self.assertEqual(kiem_co_chu.PT_MOI_PX, 9525 / 12700)

    def test_small_text_is_an_error_and_names_the_px_needed(self):
        kq = self.chay(trang('<text x="10" y="40" font-size="24">Chữ nhỏ quá</text>'))
        self.assertEqual(len(kq["loi"]), 1)
        self.assertEqual((kq["loi"][0]["pt"], kq["loi"][0]["px_can"]), (18.0, 32))

    def test_inherited_size_from_groups_and_tspans_counts(self):
        kq = self.chay(trang('<g font-size="40"><text x="10" y="40">Đủ to</text>'
                             '<text x="10" y="90">Dòng một<tspan x="10" dy="40" font-size="20">dòng hai nhỏ</tspan></text></g>'))
        self.assertEqual([x["chu"] for x in kq["loi"]], ["Dòng một dòng hai nhỏ"])
        self.assertEqual(kq["loi"][0]["pt"], 15.0)

    def test_source_lines_and_page_numbers_may_be_smaller(self):
        kq = self.chay(trang('<text x="10" y="700" font-size="24">Nguồn: Wikimedia Commons, CC BY-SA 4.0</text>'
                             '<text x="1200" y="700" font-size="24">7 / 12</text>'
                             '<text x="10" y="650" font-size="20">Nguồn: quá nhỏ</text>'))
        self.assertEqual([x["chu"] for x in kq["loi"]], ["Nguồn: quá nhỏ"])
        self.assertEqual(kq["loi"][0]["toi_thieu"], 18.0)

    def test_long_body_lines_under_28pt_are_a_warning(self):
        dai = "Một dòng nội dung đủ dài để được tính là thân bài trên slide"
        kq = self.chay(trang(f'<text x="10" y="40" font-size="32">{dai}</text>'))
        self.assertEqual(kq["loi"], [])
        self.assertEqual(kq["canh_bao"][0]["px_can"], 37)

    def test_text_inside_defs_and_non_projection_canvases_are_skipped(self):
        kq = self.chay(trang('<defs><symbol id="s"><text font-size="10">x</text></symbol></defs>'),
                       trang('<text font-size="12">poster</text>', w=1242, h=1660))
        self.assertEqual((kq["loi"], kq["bo_qua"]), ([], ["02_t.svg"]))

    def test_cli_prints_one_json_line_and_exits_non_zero_on_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "svg_output").mkdir()
            (Path(tmp) / "svg_output" / "01.svg").write_text(trang('<text font-size="20">nhỏ</text>'), encoding="utf-8")
            r = subprocess.run([sys.executable, str(VI / "kiem_co_chu.py"), tmp], capture_output=True, text=True,
                               encoding="utf-8")
            self.assertEqual(r.returncode, 1)
            d = json.loads(r.stdout.strip().splitlines()[-1])
            self.assertFalse(d["ready"])
            self.assertIsNone(d["error"])
            r2 = subprocess.run([sys.executable, str(VI / "kiem_co_chu.py"), str(Path(tmp) / "khong-co")],
                                capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(json.loads(r2.stdout)["error"]["step"], "input")


if __name__ == "__main__":
    unittest.main()

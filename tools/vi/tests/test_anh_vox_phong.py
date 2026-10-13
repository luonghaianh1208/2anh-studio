"""Prompt ảnh của video Vox: khối phong cách chi tiết cho `phong-anh: cat-dan` (chung, nền, vật) và nhân vật chính cố
định (`nhan-vat-chinh` + `@nhan-vat` trong mô tả `ve:`)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from anh_vox_parts import ke_hoach  # noqa: E402
from video_ma_parts import parse  # noqa: E402

DAU = "---\ntieu-de: T\nphong-cach: vox\n{them}---\n\n"
CANH = ("## Cảnh 1\nbo-cuc: hai-ben\nloi: Cốc cà phê và chiếc bánh.\nnen: bàn gỗ quán cà phê\n"
        "nhip: Cốc cà phê | anh: ve: {mo_ta} | trai\n"
        "nhip: chiếc bánh | anh: ve: bánh sừng bò | phai | khung\n")


def video(mo_ta="cốc cà phê sứ trắng", them=""):
    return parse.parse(DAU.format(them=them) + CANH.format(mo_ta=mo_ta))


def muc(v):
    ds = ke_hoach.lap(v)
    return {m.kieu: m for m in ds}


class CatDanPromptTest(unittest.TestCase):
    def test_cut_out_prompt_carries_palette_technique_and_green_screen_but_no_paper_sheet(self):
        m = muc(video())["cat"]
        for chu in ("cốc cà phê sứ trắng", "halftone", "engraving", "#1F3A5F", "#D9472B", "#E3A72F", "#2A7F7A",
                    "#00FF00", "white paper border", "No text"):
            with self.subTest(chu=chu):
                self.assertIn(chu, m.prompt)
        # Giấy kem chỉ thuộc nền: để ở prompt vật thì mô hình vẽ cả tờ giấy sau vật, tách nền ra cả tờ giấy.
        self.assertNotIn("newsprint", m.prompt)

    def test_background_prompt_keeps_a_calm_cream_centre_and_no_people(self):
        m = muc(video())["nen"]
        for chu in ("bàn gỗ quán cà phê", "cream newsprint", "left two thirds", "graph paper", "no people", "#1F3A5F"):
            with self.subTest(chu=chu):
                self.assertIn(chu, m.prompt)
        self.assertNotIn("#00FF00", m.prompt)

    def test_framed_picture_prompt_fills_the_frame(self):
        m = muc(video())["khung"]
        self.assertIn("bánh sừng bò", m.prompt)
        self.assertIn("edge to edge", m.prompt)
        self.assertNotIn("#00FF00", m.prompt)

    def test_other_image_styles_keep_their_old_prompts(self):
        # Đổi phong cách cat-dan không được làm cũ ảnh đã vẽ của `chup-that`, `minh-hoa`.
        m = muc(video(them="phong-anh: chup-that\n"))["cat"]
        cu = ", ".join(["cốc cà phê sứ trắng", ke_hoach.DUOI_PHONG["chup-that"], ke_hoach.DUOI_CAT, ke_hoach.DUOI_CHUNG])
        self.assertEqual(m.prompt, cu)


class NhanVatChinhTest(unittest.TestCase):
    MO_TA = "cô gái văn phòng 25 tuổi, tóc đen buộc đuôi ngựa, áo sơ mi vàng mù tạt, quần xanh than"

    def test_marker_is_replaced_by_the_main_character_in_every_prompt_that_uses_it(self):
        v = video(mo_ta="@nhan-vat cầm cốc cà phê", them=f"nhan-vat-chinh: {self.MO_TA}\n")
        self.assertEqual(v.meta["nhan-vat-chinh"], self.MO_TA)
        m = muc(v)["cat"]
        self.assertIn(self.MO_TA, m.prompt)
        self.assertNotIn("@nhan-vat", m.prompt)
        self.assertIn("same main character", m.prompt)
        # Ảnh không gọi nhân vật thì không chèn mô tả nhân vật.
        self.assertNotIn(self.MO_TA, muc(v)["khung"].prompt)
        self.assertNotIn(self.MO_TA, muc(v)["nen"].prompt)

    def test_marker_without_a_main_character_is_a_parse_error_on_that_beat(self):
        with self.assertRaises(parse.ParseError) as c:
            video(mo_ta="@nhan-vat cầm cốc cà phê")
        self.assertIn("nhan-vat-chinh", str(c.exception))
        self.assertEqual(c.exception.line_no, 10)

    def test_main_character_is_vox_only_and_bounded(self):
        with self.assertRaises(parse.ParseError) as c:
            parse.parse("---\ntieu-de: T\nmon: Lí\nlop: 10\nnhan-vat-chinh: cô gái\n---\n\n## Cảnh 1\nloai: mo-dau\n"
                        "tieu-de: A\nloi: Một.\n")
        self.assertIn("phong-cach: vox", str(c.exception))
        with self.assertRaises(parse.ParseError) as c:
            video(them="nhan-vat-chinh: " + "a" * 301 + "\n")
        self.assertIn("300", str(c.exception))



class BanVeTest(unittest.TestCase):
    def test_blueprint_style_prompts_and_default_palette(self):
        v = video(them="phong-anh: ban-ve\n")
        self.assertEqual(v.meta["bang-mau"], "ban-ve")
        m = muc(v)
        for kieu in ("cat", "nen", "khung"):
            with self.subTest(kieu=kieu):
                self.assertIn("blueprint", m[kieu].prompt)
                self.assertIn("#123A5C", m[kieu].prompt)
                self.assertNotIn("halftone", m[kieu].prompt)
        self.assertIn("#00FF00", m["cat"].prompt)
        self.assertIn("card of blueprint paper", m["cat"].prompt)
        self.assertIn("no people", m["nen"].prompt)

    def test_an_explicit_palette_wins(self):
        self.assertEqual(video(them="phong-anh: ban-ve\nbang-mau: dem\n").meta["bang-mau"], "dem")
        self.assertEqual(video().meta["bang-mau"], "kem")


if __name__ == "__main__":
    unittest.main()

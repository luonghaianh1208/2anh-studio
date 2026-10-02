"""Xử lý ảnh Vox: tách nền xanh, viền xé, khung xé, cắt phủ, in chấm. Cần FFmpeg cho tách nền."""
import shutil, sys, tempfile, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402
from anh_vox_parts import ke_hoach, xu_ly  # noqa: E402

CO_FFMPEG = shutil.which("ffmpeg") is not None


def vat_tren_nen(mau_nen=(0, 255, 0), w=200, h=200) -> Image.Image:
    im = Image.new("RGB", (w, h), mau_nen)
    for x in range(60, 140):
        for y in range(50, 160):
            im.putpixel((x, y), (180, 70, 40))
    return im


class CatPhuTest(unittest.TestCase):
    def test_cover_crop_keeps_the_ratio(self):
        im = xu_ly.cat_phu(Image.new("RGB", (1024, 1024)), 1.5)
        self.assertAlmostEqual(im.width / im.height, 1.5, places=2)
        im = xu_ly.cat_phu(Image.new("RGB", (1536, 1024)), 1 / 1.5)
        self.assertAlmostEqual(im.width / im.height, 1 / 1.5, places=2)


@unittest.skipUnless(CO_FFMPEG, "cần FFmpeg")
class TachNenTest(unittest.TestCase):
    def test_pure_green_is_removed(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "g.png"
            vat_tren_nen().save(p)
            im = xu_ly.tach_nen(p)
        self.assertEqual(im.mode, "RGBA")
        self.assertEqual(im.getpixel((5, 5))[3], 0)
        self.assertEqual(im.getpixel((100, 100))[3], 255)
        self.assertTrue(xu_ly.alpha_sach(im))

    def test_yellow_object_keeps_its_colour(self):
        im = Image.new("RGB", (200, 200), (0, 255, 0))
        im.paste((250, 210, 60), (60, 50, 140, 160))
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "g.png"
            im.save(p)
            ra = xu_ly.tach_nen(p)
        self.assertEqual(ra.getpixel((100, 100)), (250, 210, 60, 255))

    def test_opaque_green_tinted_colours_are_kept(self):
        im = Image.new("RGB", (240, 200), (0, 255, 0))
        im.paste((120, 140, 60), (30, 40, 110, 160))     # ô liu
        im.paste((200, 230, 210), (130, 40, 210, 160))   # bạc hà
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "g.png"
            im.save(p)
            ra = xu_ly.tach_nen(p)
        for xy, mau in (((70, 100), (120, 140, 60)), ((170, 100), (200, 230, 210))):
            px = ra.getpixel(xy)
            self.assertEqual(px[3], 255)
            for k in range(3):
                self.assertLessEqual(abs(px[k] - mau[k]), 3, (xy, px, mau))

    def test_not_green_background_is_not_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "g.png"
            vat_tren_nen((240, 240, 240)).save(p)
            im = xu_ly.tach_nen(p)
        self.assertFalse(xu_ly.alpha_sach(im))


class VienXeTest(unittest.TestCase):
    def setUp(self):
        self.vat = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
        for x in range(60, 140):
            for y in range(50, 160):
                self.vat.putpixel((x, y), (180, 70, 40, 255))

    def test_rim_is_paper_coloured_around_the_object_and_deterministic(self):
        a = xu_ly.vien_xe(self.vat, 101)
        b = xu_ly.vien_xe(self.vat, 101)
        self.assertEqual(a.tobytes(), b.tobytes())
        self.assertNotEqual(a.tobytes(), xu_ly.vien_xe(self.vat, 102).tobytes())
        # Có lề trong suốt để bóng đổ không bị cắt, viền giấy sáng ngay ngoài vật.
        self.assertGreater(a.width, self.vat.width)
        lech = (a.width - self.vat.width) // 2
        r, g, bl, al = a.getpixel((lech + 55, lech + 100))
        self.assertGreater(min(r, g, bl), 200)
        self.assertEqual(al, 255)

    def test_frame_has_torn_edges(self):
        k = xu_ly.khung_xe(Image.new("RGB", (300, 200), (90, 120, 160)), 7)
        self.assertEqual(k.mode, "RGBA")
        canh = [k.getpixel((x, 2))[3] for x in range(20, k.width - 20, 3)]
        self.assertIn(0, canh)
        self.assertIn(255, [k.getpixel((x, k.height // 2))[3] for x in range(20, k.width - 20, 3)])


class InTest(unittest.TestCase):
    def test_duotone_uses_two_colours(self):
        im = xu_ly.duotone(Image.linear_gradient("L").convert("RGB"), (30, 40, 90), (240, 220, 180))
        self.assertEqual(im.getpixel((0, 0))[:3], (30, 40, 90))
        self.assertEqual(im.getpixel((0, 255))[:3], (240, 220, 180))

    def test_halftone_makes_dots(self):
        im = xu_ly.halftone(Image.new("RGB", (64, 64), (128, 128, 128)), buoc=8)
        mau = {im.getpixel((x, y))[:3] for x in range(64) for y in range(64)}
        self.assertLessEqual(len(mau), 6)

    def test_print_effects_keep_alpha(self):
        vat = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        vat.paste((180, 70, 40, 255), (16, 16, 48, 48))
        for im in (xu_ly.duotone(vat, (30, 40, 90), (240, 220, 180)), xu_ly.halftone(vat, buoc=8)):
            self.assertEqual(im.mode, "RGBA")
            self.assertEqual(im.getpixel((2, 2))[3], 0)
            self.assertEqual(im.getpixel((32, 32))[3], 255)


def _muc(kieu, nguon="ve", tuy_chon=(), kich_thuoc="1024x1024", canh=1, chi_so=0):
    return ke_hoach.Muc("abc123", canh, chi_so, kieu, nguon, "p", kich_thuoc, tuple(tuy_chon))


@unittest.skipUnless(CO_FFMPEG, "cần FFmpeg")
class XuLyMucTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.thu_muc = Path(self._tmp.name)
        (self.thu_muc / "anh" / "ai" / "goc").mkdir(parents=True)

    def tearDown(self):
        self._tmp.cleanup()

    def _dat_goc(self, m, im):
        im.save(ke_hoach.file_goc(self.thu_muc, m))

    def test_cutout_is_saved_under_the_planned_name(self):
        m = _muc("cat")
        self._dat_goc(m, vat_tren_nen(w=400, h=400))
        canh_bao = xu_ly.xu_ly_muc(self.thu_muc, m)
        self.assertEqual(canh_bao, [])
        self.assertEqual(m.kieu, "cat")
        with Image.open(ke_hoach.file_xu_ly(self.thu_muc, m)) as ra:
            self.assertEqual(ra.mode, "RGBA")
            # Nằm trên viền giấy, quanh có phần trong suốt; vật cam vẫn ở giữa.
            self.assertGreater(ra.getchannel("A").histogram()[0], ra.width * ra.height * 0.02)
            self.assertEqual(ra.getpixel((ra.width // 2, ra.height // 2)), (180, 70, 40, 255))

    def test_unclean_cutout_falls_back_to_a_frame_with_a_warning(self):
        m = _muc("cat", canh=3, chi_so=2)
        self._dat_goc(m, vat_tren_nen((240, 240, 240), w=300, h=300))
        canh_bao = xu_ly.xu_ly_muc(self.thu_muc, m)
        self.assertEqual(m.kieu, "khung")
        self.assertEqual(len(canh_bao), 1)
        self.assertIn("Cảnh 3, nhịp 3", canh_bao[0])   # nhịp đếm từ 1 cho thầy cô đọc
        self.assertTrue(ke_hoach.file_xu_ly(self.thu_muc, m).name.endswith("-khung.png"))
        with Image.open(ke_hoach.file_xu_ly(self.thu_muc, m)) as ra:
            self.assertGreater(ra.width / ra.height, 1.3)

    def test_dark_green_with_shadow_leaves_no_green_fringe(self):
        im = Image.new("RGB", (400, 400), (20, 150, 50))
        for x in range(150, 290):          # bóng đổ xanh đậm dưới vật
            for y in range(250, 275):
                im.putpixel((x, y), (10, 90, 25))
        for x in range(130, 270):
            for y in range(100, 260):
                im.putpixel((x, y), (180, 70, 40))
        m = _muc("cat")
        self._dat_goc(m, im)
        xu_ly.xu_ly_muc(self.thu_muc, m)
        with Image.open(ke_hoach.file_xu_ly(self.thu_muc, m)) as ra:
            a = np.asarray(ra.convert("RGBA")).astype(int)
        xanh = int(((a[..., 3] > 128) & (a[..., 1] > np.maximum(a[..., 0], a[..., 2]) + 30)).sum())
        self.assertEqual(xanh, 0, f"{xanh} điểm xanh còn sót")

    @staticmethod
    def _mat_na_lo_xanh():
        # Mặt nạ giấy trắng gần kín khung, hai lỗ mắt kín màu xanh nền: vật > 90 % diện tích nên tách nền không sạch.
        im = Image.new("RGB", (400, 400), (0, 255, 0))
        d = ImageDraw.Draw(im)
        d.rectangle((4, 4, 395, 395), fill=(238, 236, 228))
        d.ellipse((110, 150, 170, 200), fill=(0, 255, 0))
        d.ellipse((230, 150, 290, 200), fill=(0, 255, 0))
        return im

    @staticmethod
    def _diem_xanh(p) -> int:
        with Image.open(p) as ra:
            a = np.asarray(ra.convert("RGBA")).astype(int)
        return int(((a[..., 3] > 0) & (a[..., 1] > np.maximum(a[..., 0], a[..., 2]) + 40)).sum())

    def test_green_screen_fallback_frame_has_no_green_even_in_enclosed_holes(self):
        m = _muc("cat")
        self._dat_goc(m, self._mat_na_lo_xanh())
        self.assertFalse(xu_ly.alpha_sach(xu_ly.tach_nen(ke_hoach.file_goc(self.thu_muc, m))))
        canh_bao = xu_ly.xu_ly_muc(self.thu_muc, m)
        self.assertEqual(m.kieu, "khung")
        self.assertEqual(len(canh_bao), 1)
        self.assertEqual(self._diem_xanh(ke_hoach.file_xu_ly(self.thu_muc, m)), 0)

    def test_frame_drawn_as_frame_from_the_start_keeps_its_colours(self):
        m = _muc("khung")
        self._dat_goc(m, self._mat_na_lo_xanh())
        xu_ly.xu_ly_muc(self.thu_muc, m)
        self.assertGreater(self._diem_xanh(ke_hoach.file_xu_ly(self.thu_muc, m)), 1000)

    def test_frame_ratio_follows_the_format_and_effects_add_suffixes(self):
        m = _muc("khung", nguon="ve", tuy_chon=("duotone", "halftone"), kich_thuoc="1024x1536")
        self._dat_goc(m, Image.new("RGB", (1024, 1024), (120, 90, 60)))
        xu_ly.xu_ly_muc(self.thu_muc, m, kho="doc", bang_mau="dem")
        p = ke_hoach.file_xu_ly(self.thu_muc, m)
        self.assertTrue(p.name.endswith("-khung-duotone-halftone.png"))
        with Image.open(p) as ra:
            self.assertLess(ra.width / ra.height, 0.8)
            self.assertLessEqual(max(ra.size), 1400)

    def test_full_frame_is_cover_cropped_without_border(self):
        m = _muc("phu", kich_thuoc="1536x1024")
        self._dat_goc(m, Image.new("RGB", (1024, 1024), (120, 90, 60)))
        xu_ly.xu_ly_muc(self.thu_muc, m)
        with Image.open(ke_hoach.file_xu_ly(self.thu_muc, m)) as ra:
            self.assertAlmostEqual(ra.width / ra.height, 16 / 9, places=2)
            self.assertEqual(ra.convert("RGBA").getpixel((0, 0))[3], 255)

    def test_missing_source_file_is_an_input_error(self):
        with self.assertRaises(xu_ly.XuLyError) as c:
            xu_ly.xu_ly_muc(self.thu_muc, _muc("khung"))
        self.assertEqual(c.exception.step, "input")


if __name__ == "__main__":
    unittest.main()

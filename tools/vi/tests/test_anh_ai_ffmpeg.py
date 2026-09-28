"""`anh_ai.py nhan` với FFmpeg thật, ảnh tổng hợp bằng lavfi (không tải gì): nền cắt phủ đúng khổ, ảnh nhỏ không phóng
to mà cảnh báo, nhân vật tách nền xanh trong suốt và cắt sát, nền xanh loang có dải tối ở góc là lỗi `tach-nen`,
nhận `.jpg` khi kế hoạch ghi `.png`, nguon.json đọc được bởi `anh.doc`."""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS_VI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_VI))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import anh_ai  # noqa: E402
from anh_ai_parts import xu_ly  # noqa: E402
from test_anh_ai import VIDEO_MD, viet_video_md  # noqa: E402
from video_ma_parts import anh  # noqa: E402

CO_FFMPEG = shutil.which("ffmpeg") is not None and shutil.which("ffprobe") is not None
TRON = "lt(hypot(X-512\\,Y-760)\\,300)"  # hình tròn bán kính 300 giữa ảnh 1024x1536


def ve(ra: Path, nguon: str) -> Path:
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "lavfi", "-i", nguon,
                    "-frames:v", "1", str(ra)], check=True, capture_output=True, timeout=120)
    return ra


def nhan_vat(ra: Path, nen=(0, 255, 0), them: str = "") -> Path:
    """Hình tròn đỏ trên nền màu `nen` (mặc định #00FF00), 1024x1536; `them`: bộ lọc nối thêm (nhiễu, dải tối...)."""
    r, g, b = nen
    loc = (f"color=c=0x{r:02X}{g:02X}{b:02X}:s=1024x1536,format=gbrp,"
           f"geq=r='if({TRON},230,{r})':g='if({TRON},20,{g})':b='if({TRON},30,{b})'{them}")
    return ve(ra, loc)


def kich_thuoc(p: Path) -> tuple:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=width,height", "-of", "csv=s=x:p=0", str(p)],
                         capture_output=True, text=True, timeout=60).stdout.strip()
    return tuple(int(x) for x in out.split("x"))


def alpha_tho(p: Path) -> tuple:
    w, h = kich_thuoc(p)
    raw = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(p), "-vf", "alphaextract",
                          "-f", "rawvideo", "-pix_fmt", "gray", "pipe:1"], capture_output=True, timeout=60).stdout
    return raw, w, h


@unittest.skipUnless(CO_FFMPEG, "cần FFmpeg")
class NhanFfmpegTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.thu_muc = viet_video_md(Path(cls.tmp.name) / "bai", VIDEO_MD)
        anh_ai.chay_ke_hoach(cls.thu_muc, [])
        cls.goc = cls.thu_muc / "anh" / "ai" / "goc"
        cls.goc.mkdir(parents=True, exist_ok=True)
        for ten in ("nhan-vat-mau", "tu-the-dung", "tu-the-chao", "tu-the-giai-thich"):
            nhan_vat(cls.goc / f"{ten}.png")
        # Nền cảnh 1: AI trả ảnh vuông 1024x1024, lưu JPEG dù kế hoạch ghi nen-1.png.
        ve(cls.goc / "nen-1.jpg", "color=c=0x3366AA:s=1024x1024,drawbox=x=100:y=100:w=300:h=300:color=0xFFCC00:t=fill")
        ve(cls.goc / "nen-3.png", "color=c=0x88AA44:s=2400x1350,drawbox=x=0:y=600:w=2400:h=150:color=0x552211:t=fill")
        cls.warnings = []
        cls.kq = anh_ai.chay_nhan(cls.thu_muc, cls.warnings, cong_cu="Antigravity", mo_hinh="Nano Banana")
        cls.ai = cls.thu_muc / "anh" / "ai"

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_nen_lon_ra_dung_full_hd(self):
        self.assertEqual(kich_thuoc(self.ai / "nen-3.jpg"), (1920, 1080))

    def test_nen_vuong_nho_phu_16_9_co_canh_bao(self):
        w, h = kich_thuoc(self.ai / "nen-1.jpg")
        self.assertEqual((w, h), (1024, 576))
        self.assertIn("Ảnh nền cảnh 1 nhỏ hơn Full HD (1024x1024).", self.warnings)
        self.assertFalse(any("cảnh 3" in w for w in self.warnings))

    def test_nhan_jpg_khi_ke_hoach_ghi_png(self):
        self.assertIn("anh/ai/nen-1.jpg", self.kq["files"])
        self.assertTrue((self.goc / "nen-1.jpg").is_file())  # ảnh gốc giữ nguyên

    def test_nhan_vat_trong_suot_va_cat_sat(self):
        for ten in ("nhan-vat-mau.png", "tu-the-chao.png"):
            p = self.ai / ten
            self.assertTrue(anh.co_alpha(p.read_bytes(), ".png"), ten)
            raw, w, h = alpha_tho(p)
            self.assertLessEqual(abs(w - 600), 4, (w, h))
            self.assertLessEqual(abs(h - 600), 4, (w, h))
            do = xu_ly.do_alpha(raw, w, h)
            self.assertEqual(do["goc"], [0, 0, 0, 0])  # góc hộp cắt ngoài hình tròn: trong suốt hẳn
            # Giữa hình tròn đục hẳn.
            self.assertEqual(raw[(h // 2) * w + w // 2], 255)

    def test_nguon_doc_duoc_boi_anh_doc(self):
        nguon = json.loads((self.ai / "nguon.json").read_text(encoding="utf-8"))
        self.assertEqual(len(nguon), 6)
        info = anh.doc(self.thu_muc, "ai/nen-1.jpg", None)
        self.assertEqual(info["nguon"], "Hình minh hoạ tạo bằng AI (Nano Banana)")
        self.assertTrue(anh.doc(self.thu_muc, "ai/tu-the-giai-thich.png", None)["alpha"])


@unittest.skipUnless(CO_FFMPEG, "cần FFmpeg")
class TachNenFfmpegTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.d = Path(self.tmp.name)

    def test_nen_xanh_loang_van_tach(self):
        goc = nhan_vat(self.d / "loang.png", (0x33, 0xCC, 0x55), ",noise=alls=30:allf=u")
        xu_ly.xu_ly_nhan_vat(goc, self.d / "ra.png", "goc/loang.png", subprocess.run)
        self.assertTrue(anh.co_alpha((self.d / "ra.png").read_bytes(), ".png"))

    def test_nen_loang_co_dai_toi_o_goc_la_loi_tach_nen(self):
        goc = nhan_vat(self.d / "tu-the-chao.png", (0x33, 0xCC, 0x55),
                       ",noise=alls=30:allf=u,drawbox=x=0:y=0:w=1024:h=90:color=0x202020:t=fill")
        with self.assertRaises(xu_ly.XuLyError) as caught:
            xu_ly.xu_ly_nhan_vat(goc, self.d / "ra.png", "goc/tu-the-chao.png", subprocess.run)
        self.assertEqual(caught.exception.step, "tach-nen")
        self.assertIn("goc/tu-the-chao.png", caught.exception.message)
        self.assertIn("góc trái trên", caught.exception.message)
        self.assertFalse((self.d / "ra.png").exists())

    def test_anh_da_trong_suot_giu_nguyen_alpha(self):
        # GPT Image có thể trả PNG trong suốt sẵn: không tách xanh (sẽ xoá mất phần áo xanh lá), giữ alpha gốc.
        tron = "lt(hypot(X-512\\,Y-760)\\,300)"
        goc = ve(self.d / "trong-suot.png",
                 "color=c=black@0.0:s=1024x1536,format=rgba,"
                 f"geq=r='if({tron},30,0)':g='if({tron},200,0)':b='if({tron},60,0)':a='if({tron},255,0)'")
        ra = self.d / "ra.png"
        xu_ly.xu_ly_nhan_vat(goc, ra, "goc/trong-suot.png", subprocess.run)
        raw, w, h = alpha_tho(ra)
        self.assertLessEqual(abs(w - 600), 4, (w, h))
        self.assertEqual(xu_ly.do_alpha(raw, w, h)["goc"], [0, 0, 0, 0])
        self.assertEqual(raw[(h // 2) * w + w // 2], 255)  # hình xanh lá vẫn đục

    def test_nen_xanh_khong_thuan_noi_ro_mau_do_duoc(self):
        goc = nhan_vat(self.d / "tu-the-buon.png", (0x4C, 0xAF, 0x50))
        with self.assertRaises(xu_ly.XuLyError) as caught:
            xu_ly.xu_ly_nhan_vat(goc, self.d / "ra.png", "goc/tu-the-buon.png", subprocess.run)
        self.assertEqual(caught.exception.step, "tach-nen")
        self.assertIn("nền không phải xanh thuần #00FF00 (đo được #4CAF50)", caught.exception.message)
        self.assertIn("#00FF00", caught.exception.fix)

    def test_nhan_vat_lon_thu_ve_1536_duoi_8_mb(self):
        tron = "lt(hypot(X-1024\\,Y-1536)\\,900)"
        goc = ve(self.d / "lon.png", "color=c=0x00FF00:s=2048x3072,format=gbrp,"
                                     f"geq=r='if({tron},230,0)':g='if({tron},20,255)':b='if({tron},30,0)',"
                                     "noise=c0s=40:c2s=40:allf=u")
        ra = self.d / "ra.png"
        xu_ly.xu_ly_nhan_vat(goc, ra, "goc/lon.png", subprocess.run)
        w, h = kich_thuoc(ra)
        self.assertEqual(max(w, h), 1536)
        self.assertLessEqual(ra.stat().st_size, xu_ly.TOI_DA)
        self.assertTrue(anh.co_alpha(ra.read_bytes(), ".png"))

    def test_anh_hong_la_loi_ffmpeg(self):
        hong = self.d / "hong.png"
        hong.write_bytes(b"khong phai anh")
        with self.assertRaises(xu_ly.XuLyError) as caught:
            xu_ly.xu_ly_nen(hong, self.d / "nen-1.jpg", "ngang", "goc/hong.png", subprocess.run)
        self.assertEqual(caught.exception.step, "ffmpeg")
        self.assertIn("goc/hong.png", caught.exception.message)


if __name__ == "__main__":
    unittest.main()

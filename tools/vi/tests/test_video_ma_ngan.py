"""Phong cách video ngắn mạng xã hội (`phong-cach: ngan`): khung của cat-dan với da neon tối. Kiểm khoá đầu và mặc
định (khổ dọc, chuyển trượt, ẩn tay), giới hạn chữ dùng đúng bảng cat-dan, trang nạp ngan.css và nền neon, và trên
Chromium: mọi loại cảnh ở đúng giới hạn khổ dọc nằm gọn, nền neon dựng lặp lại ra cùng ảnh.

Phần Chromium tự bỏ qua nếu máy thiếu."""

import re
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS_VI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_VI))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import video_ma  # noqa: E402
from do_gioi_han import LOAI_CO_COT, meta, ngoai_vung  # noqa: E402
from test_video_ma_cat_dan import trang_cua  # noqa: E402
from test_video_ma_kho_doc import canh_toi_da, thu_muc_bai, video_md  # noqa: E402
from video_ma_parts import chup, karaoke, kho, kiem, lich, parse, phong  # noqa: E402

CO_CHROMIUM = video_ma.co_chromium()
TOI_THIEU = "---\ntieu-de: Tin nhanh\nmon: Tin học\nlop: 10\nphong-cach: ngan\n---\n\n## Cảnh 1\nloai: tieu-de\nchu: Chào\nloi: Xin chào.\n"


class KhoaDauNganTest(unittest.TestCase):
    def test_ngan_mac_dinh_kho_doc_truot_an_tay(self):
        video = parse.parse(TOI_THIEU)
        self.assertEqual(video.meta["phong-cach"], "ngan")
        self.assertEqual(video.meta["kho"], "doc")
        self.assertEqual(lich.mac_dinh(video.meta, "chuyen-canh"), "truot")
        self.assertEqual(lich.mac_dinh(video.meta, "ban-tay"), "khong")

    def test_ngan_ghi_kho_ngang_thi_giu(self):
        video = parse.parse(TOI_THIEU.replace("phong-cach: ngan\n", "phong-cach: ngan\nkho: ngang\n"))
        self.assertEqual(video.meta["kho"], "ngang")

    def test_phong_cach_khac_khong_doi_mac_dinh(self):
        video = parse.parse(TOI_THIEU.replace("phong-cach: ngan", "phong-cach: cat-dan"))
        self.assertEqual(video.meta["kho"], "ngang")

    def test_gioi_han_ngan_bang_cat_dan(self):
        for ten_kho in ("ngang", "doc"):
            for co_the in (False, True):
                self.assertEqual(kiem.bang_gioi_han(ten_kho, "ngan", co_the), kiem.bang_gioi_han(ten_kho, "cat-dan", co_the))

    def test_chu_de_va_phu_de(self):
        cd = phong.chu_de("ngan") if hasattr(phong, "chu_de") else phong.CHU_DE["ngan"]
        self.assertEqual(cd["ten"], "ngan")
        self.assertEqual(cd["font"], phong.TEN_CAT_DAN)
        self.assertEqual(len(cd["mauNhan"]), 4)
        kieu = karaoke.kieu_phu_de("ngan", "doc")
        self.assertEqual((kieu["font"], kieu["khung"], kieu["vien"]), (karaoke.FONT_PHUDU, False, True))
        self.assertTrue(phong.FONT_PHUDU.is_file())

    def test_phu_de_ngan_moi_luc_mot_dong_vang_vien_den(self):
        from video_ma_parts import lich

        loi = "Người ta đồn lực hút bí ẩn nuốt chửng tàu bè ngoài khơi xa."
        tu = [{"t": round(k * 0.35, 3), "d": 0.3, "chu": w} for k, w in enumerate(loi.split())]
        cl = lich.CanhLich(so=1, bat_dau=0.0, thoi_luong=6.0, so_khung=180, giay_giong=5.0, cau=[loi], moc_cau=[0.0],
                           moc_cau_giong=[0.0], uoc_luong=False, moc_tu=tu)
        ass = karaoke.tao_ass([cl], rong=720, cao=1280, chu_de="ngan", kho_ten="doc")
        self.assertIn("Style: Vien,Phudu ExtraBold,58,&H0000D7FF", ass)
        chu = [d for d in ass.splitlines() if d.startswith("Dialogue:")]
        self.assertGreater(len(chu), 1)
        # Không có hai dòng hiện cùng lúc: mỗi sự kiện bắt đầu khi sự kiện trước kết thúc.
        moc = [d.split(",")[1:3] for d in chu]
        for (_a, het), (dau, _b) in zip(moc, moc[1:]):
            self.assertLessEqual(het, dau)
        self.assertTrue(all("\\an2" in d and "\\p1" not in d for d in chu))


class TrangNganTest(unittest.TestCase):
    def test_trang_ngan_nap_cat_dan_va_ngan_css_khong_dia_chi_web(self):
        html = trang_cua("chu: Tin nóng\n", phong_cach="ngan")
        self.assertIn("#khung.ngan", html)
        self.assertIn(".nen-giay", html)
        self.assertIn("nenNeon", html)
        self.assertEqual(html.count("font-family:'BeVietnamPro'"), 2)
        self.assertIsNone(re.search(r"https://|url\((?!data:|#)", html))

    def test_cat_dan_khong_nap_ngan_css(self):
        self.assertNotIn("#khung.ngan", trang_cua("chu: Giấy\n", phong_cach="cat-dan"))


@unittest.skipUnless(CO_CHROMIUM, "máy không có Chromium hoặc playwright")
class NganChromiumTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.cm = chup.trinh_duyet()
        cls.browser = cls.cm.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.cm.__exit__(None, None, None)
        cls.tmp.cleanup()

    def test_moi_loai_canh_kho_doc_o_gioi_han_nam_gon(self):
        L, H = kiem.bang_gioi_han("doc", "ngan")
        ds = canh_toi_da(L, H) + [c for c in canh_toi_da(L, H, cot=True) if c[0] in LOAI_CO_COT]
        thu_muc = thu_muc_bai(Path(self.tmp.name) / "doc", video_md(ds, meta("doc", "ngan")))
        video = parse.parse((thu_muc / "video.md").read_text(encoding="utf-8"))
        self.assertEqual(kiem.kiem(video, thu_muc), [])
        page = chup.trang_moi(self.browser, kho.Kho("doc", 720))
        try:
            for canh, html in zip(video.canh, video_ma._trang_tam(video, thu_muc, video_ma._mo_hinh(video, thu_muc))):
                with self.subTest(so=canh.so, loai=canh.loai):
                    tran, ra = ngoai_vung(page, html, "doc")
                    self.assertEqual(tran, [])
                    self.assertEqual(ra, [])
        finally:
            page.close()

    def test_nen_neon_toi_va_nhan_mau_canh(self):
        page = chup.trang_moi(self.browser, kho.Kho("doc", 720))
        try:
            chup.mo_trang(page, trang_cua("tieu-de: Ba ý\ny: Một\ny: Hai\n", "y-tung-y", phong_cach="ngan", so=2, ten_kho="doc"))
            page.evaluate("() => window.datThoiDiem(window.THI_VIDEO.thoiDiemCuoi())")
            kq = page.evaluate("""() => ({
              lop: document.querySelector('#khung').className,
              neon: !!document.querySelector('.nen-giay svg.neon'),
              mauNhan: getComputedStyle(document.querySelector('#khung')).getPropertyValue('--mau-nhan').trim(),
              chu: getComputedStyle(document.querySelector('.chu[data-id="tieu-de"]')).color })""")
            self.assertIn("ngan", kq["lop"])
            self.assertTrue(kq["neon"])
            self.assertEqual(kq["mauNhan"], "#f472b6")  # cảnh 2
            self.assertEqual(kq["chu"], "rgb(11, 16, 32)")  # chữ tối trên dải neon
        finally:
            page.close()

    def test_hai_lan_dung_cung_canh_cho_cung_anh(self):
        html = trang_cua("tieu-de: Ba ý\ny: Một\ny: ==Hai==\n", "y-tung-y", phong_cach="ngan", so=3, ten_kho="doc")
        anh = []
        for _ in range(2):
            page = chup.trang_moi(self.browser, kho.Kho("doc", 720))
            try:
                chup.mo_trang(page, html)
                khung = []
                for t in (0.35, 1.3, 4.0):
                    page.evaluate("(t) => window.datThoiDiem(t)", t)
                    khung.append(page.screenshot(type="png"))
                anh.append(khung)
            finally:
                page.close()
        self.assertEqual(anh[0], anh[1])


if __name__ == "__main__":
    unittest.main()

"""Phong cách cắt dán (`phong-cach: cat-dan`): bảng giới hạn chữ riêng (font Be Vietnam Pro rộng hơn Itim), trang
nhúng font và lớp da, và trên Chromium: mọi loại cảnh × hai khổ ở đúng giới hạn nằm gọn trong khung và trên vạch phụ đề;
font Be Vietnam Pro nạp đủ chữ Việt; dựng hai lần ra cùng ảnh.

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
from test_video_ma_kho_doc import canh_toi_da, chuoi, thu_muc_bai, video_md  # noqa: E402
from video_ma_parts import chup, kho, kiem, lich, parse, trang  # noqa: E402

CO_CHROMIUM = video_ma.co_chromium()


def video_cua(ds: list, ten_kho: str = "ngang", phong_cach: str = "cat-dan") -> parse.Video:
    return parse.parse(video_md(ds, meta(ten_kho, phong_cach)))


class GioiHanCatDanTest(unittest.TestCase):
    def test_bang_cat_dan_cung_khoa_va_khong_lon_hon_viet_tay(self):
        for ten_kho in ("ngang", "doc"):
            L, H = kiem.bang_gioi_han(ten_kho, "viet-tay")
            Lc, Hc = kiem.bang_gioi_han(ten_kho, "cat-dan")
            self.assertEqual(set(Lc), set(L))
            self.assertEqual(set(Hc), set(H))
            for k in L:
                self.assertLessEqual(Lc[k], L[k], (ten_kho, k))
            for k in H:
                for a, b in zip(Hc[k], H[k]):
                    if b is not None:
                        self.assertLessEqual(a, b, (ten_kho, k))

    def test_viet_tay_khong_ha(self):
        self.assertEqual(kiem.bang_gioi_han("ngang", "viet-tay"), (kiem.LIMITS, kiem.LIMITS_HAI_PHAN))
        self.assertEqual(kiem.bang_gioi_han("doc", "viet-tay"), (kiem.LIMITS_DOC, kiem.LIMITS_HAI_PHAN_DOC))
        self.assertEqual(kiem.LIMITS[("tieu-de", "chu")], 90)
        self.assertEqual(kiem.LIMITS[("y-tung-y", "y")], 60)

    def test_vuot_gioi_han_cat_dan_la_loi_neu_dung_dong(self):
        n = kiem.LIMITS_CAT_DAN[("y-tung-y", "y")] + 1
        self.assertLessEqual(n, kiem.LIMITS[("y-tung-y", "y")])
        ds = [("y-tung-y", f"tieu-de: Ý\ny: {chuoi(n)}\n")]
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(kiem.CanhError) as cm:
                kiem.kiem(video_cua(ds), Path(tmp))
            self.assertIn("phong cách cắt dán", str(cm.exception))
            self.assertIn("dòng 12", str(cm.exception))
            self.assertEqual(kiem.kiem(video_cua(ds, phong_cach="viet-tay"), Path(tmp)), [])
            n = kiem.LIMITS_CAT_DAN_DOC[("y-tung-y", "y")] + 1
            with self.assertRaises(kiem.CanhError) as cm:
                kiem.kiem(video_cua([("y-tung-y", f"tieu-de: Ý\ny: {chuoi(n)}\n")], "doc"), Path(tmp))
            self.assertIn("giới hạn khổ dọc, phong cách cắt dán", str(cm.exception))


def trang_cua(noi: str, loai: str = "tieu-de", phong_cach: str = "cat-dan", so: int = 1, ten_kho: str = "ngang") -> str:
    video = parse.parse(video_md([(loai, noi)], meta(ten_kho, phong_cach)))
    canh = video.canh[0]
    canh.so = so
    giong = lich.GiongInfo(mp3=None, giay=4.0, moc_cau=[], uoc_luong=True, nguon="may")
    plan, _ = lich.dung_lich([canh], [giong])
    tai_nguyen = {"meta": video.meta, "hinh": {"phanTu": [{"the": "circle", "thuocTinh": {"cx": "12", "cy": "12", "r": "9"}},
                                                          {"the": "path", "thuocTinh": {"d": "M12 6v6l4 2"}}],
                                               "viewBox": "0 0 24 24"}} if "hinh:" in noi else {"meta": video.meta}
    return trang.dung_trang(lich.du_lieu_canh(canh, plan[0], tai_nguyen=tai_nguyen))


class TrangCatDanTest(unittest.TestCase):
    def test_trang_cat_dan_nhung_font_va_lop_da_khong_dia_chi_web(self):
        html = trang_cua("chu: Con lắc đơn\n")
        self.assertEqual(html.count("font-family:'BeVietnamPro'"), 2)
        self.assertIn(".nen-giay", html)
        self.assertIn("THI_CAT_DAN", html)
        self.assertIsNone(re.search(r"https://|url\((?!data:|#)", html))

    def test_trang_viet_tay_khong_co_font_hay_lop_da_cat_dan(self):
        html = trang_cua("chu: Con lắc đơn\n", phong_cach="viet-tay")
        self.assertNotIn("BeVietnamPro", html)
        self.assertNotIn(".nen-giay", html)
        self.assertEqual(html.count("@font-face"), 1)


@unittest.skipUnless(CO_CHROMIUM, "máy không có Chromium hoặc playwright")
class CatDanChromiumTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.cm = chup.trinh_duyet()
        cls.browser = cls.cm.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.cm.__exit__(None, None, None)
        cls.tmp.cleanup()

    def test_moi_loai_canh_hai_kho_o_gioi_han_cat_dan_nam_gon(self):
        for ten_kho in ("ngang", "doc"):
            L, H = kiem.bang_gioi_han(ten_kho, "cat-dan")
            ds = canh_toi_da(L, H) + [c for c in canh_toi_da(L, H, cot=True) if c[0] in LOAI_CO_COT]
            self.assertEqual({loai for loai, _ in ds}, set(parse.SCENE_TYPES))
            thu_muc = thu_muc_bai(Path(self.tmp.name) / ten_kho, video_md(ds, meta(ten_kho, "cat-dan")))
            video = parse.parse((thu_muc / "video.md").read_text(encoding="utf-8"))
            self.assertEqual(kiem.kiem(video, thu_muc), [])
            page = chup.trang_moi(self.browser, kho.Kho(ten_kho, 720))
            try:
                for canh, html in zip(video.canh, video_ma._trang_tam(video, thu_muc, video_ma._mo_hinh(video, thu_muc))):
                    with self.subTest(kho=ten_kho, so=canh.so, loai=canh.loai):
                        self.assertIn("BeVietnamPro", html)
                        tran, ra = ngoai_vung(page, html, ten_kho)
                        self.assertEqual(tran, [])
                        self.assertEqual(ra, [])
            finally:
                page.close()

    def test_be_vietnam_pro_nap_du_chu_viet(self):
        page = chup.trang_moi(self.browser, kho.Kho("ngang", 720))
        try:
            chup.mo_trang(page, trang_cua("chu: Nghiễm nhiên\nphu: Vật lí 11\n"))
            self.assertTrue(page.evaluate("() => document.fonts.check('800 20px BeVietnamPro', 'Nghiễm')"))
            self.assertTrue(page.evaluate("() => document.fonts.check('400 20px BeVietnamPro', 'Nghiễm')"))
            page.evaluate("() => window.datThoiDiem(window.THI_VIDEO.thoiDiemCuoi())")
            chu = page.evaluate("() => getComputedStyle(document.querySelector('.chu[data-id=chu]')).fontFamily")
            self.assertIn("BeVietnamPro", chu)
        finally:
            page.close()

    def test_nhan_tieu_de_bang_dinh_mau_cua_canh_va_sticker(self):
        page = chup.trang_moi(self.browser, kho.Kho("ngang", 720))
        try:
            html = trang_cua("tieu-de: Lạm phát\ny: Một\ny: Hai\nhinh: clock\n", "y-tung-y", so=3)
            chup.mo_trang(page, html)
            page.evaluate("() => window.datThoiDiem(window.THI_VIDEO.thoiDiemCuoi())")
            kq = page.evaluate("""() => {
              const nhan = document.querySelector('.chu[data-id="tieu-de"]');
              const cs = getComputedStyle(nhan);
              const dai = document.querySelectorAll('g.bang-dinh polygon');
              return { weight: cs.fontWeight, upper: cs.textTransform, mau: cs.color, dai: dai.length,
                       nen: getComputedStyle(dai[0]).fill, giay: !!document.querySelector('.nen-giay svg'),
                       dan: document.querySelector('g.hinh-dan').getAttribute('transform') };
            }""")
            self.assertEqual((kq["weight"], kq["upper"], kq["mau"]), ("800", "uppercase", "rgb(255, 255, 255)"))
            self.assertEqual(kq["dai"], 1)
            self.assertEqual(kq["nen"], "rgb(200, 69, 47)")  # cảnh 3: #c8452f
            self.assertTrue(kq["giay"])
            self.assertIn("rotate(", kq["dan"])
            self.assertIn("scale(1)", kq["dan"])
        finally:
            page.close()

    def test_hai_lan_dung_cung_canh_cho_cung_anh(self):
        html = trang_cua("tieu-de: Ba ý\ny: Một\ny: ==Hai==\nhinh: clock\n", "y-tung-y", so=2)
        anh = []
        for _ in range(2):
            page = chup.trang_moi(self.browser, kho.Kho("ngang", 720))
            try:
                chup.mo_trang(page, html)
                khung = []
                for t in (0.35, 0.5, 1.3, 4.0):
                    page.evaluate("(t) => window.datThoiDiem(t)", t)
                    khung.append(page.screenshot(type="png"))
                anh.append(khung)
            finally:
                page.close()
        self.assertEqual(anh[0], anh[1])
        self.assertNotEqual(anh[0][0], anh[0][-1])


if __name__ == "__main__":
    unittest.main()

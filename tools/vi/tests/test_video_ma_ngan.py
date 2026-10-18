"""Video ngắn "nhịp hình" (`phong-cach: ngan`, ngan.py + runtime/ngan.js): khoá đầu, dàn nhân vật ghép từ bộ phận,
vật mới, phụ đề trong trang (từ khoá, ngắt dòng), trang HTML, tiếng hiệu ứng, và trên Chromium: không tràn chữ,
phụ đề hiện, nhân vật đổi tư thế, dựng lặp lại ra cùng ảnh. Phần Chromium tự bỏ qua nếu máy thiếu."""

import sys
import unittest
from pathlib import Path

TOOLS_VI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_VI))

import video_ma  # noqa: E402
from video_ma_parts import am_thanh, chup, kho, lich, ngan, parse, trang  # noqa: E402

CO_CHROMIUM = video_ma.co_chromium()

MAU = """---
tieu-de: Từ chối khéo
phong-cach: ngan
{dau}
---

## Cảnh 1
tieu-de: Bị nhờ vả
chuong: 1 · VÍ DỤ
loi: Bạn có hay bị bạn bè / ==nhờ vả== liên tục / mà **không dám** từ chối? Bảy trên mười bạn / sẽ ((thông cảm)).
nhip: @dau | nguoi: an dung
nhip: bạn bè | nguoi: linh chi-tay
nhip: không dám | nguoi: an vo-dau
nhip: Bảy trên mười | luoi-cham: 7/10 | bạn sẽ thông cảm
nhip: thông cảm | nguoi: linh an-mung
"""
VAI = "vai: an = hoc-sinh-nam; linh = hoc-sinh-nu, ao so-mi hong"


def video(dau=VAI, them=""):
    return parse.parse(MAU.format(dau=dau) + them)


def du_canh(v, k=0, giay=6.0):
    canh = v.canh[k]
    giong = lich.GiongInfo(mp3=None, giay=giay, moc_cau=[], uoc_luong=True, nguon="may")
    plan, _ = lich.dung_lich([canh], [giong])
    return lich.du_lieu_canh(canh, plan[0], tai_nguyen={"meta": v.meta})


class KhoaDauTest(unittest.TestCase):
    def test_mac_dinh(self):
        v = video()
        self.assertEqual((v.meta["kho"], v.meta["giao-dien"]), ("doc", "phang-sang"))
        self.assertEqual(v.canh[0].loai, "vox")
        self.assertEqual([n.vat for n in v.canh[0].nhip], ["nguoi", "nguoi", "nguoi", "luoi-cham", "nguoi"])

    def test_chi_tieu_de_bat_buoc(self):
        self.assertNotIn("mon", video().meta)

    def test_kho_ngang_bi_tu_choi(self):
        with self.assertRaises(parse.ParseError):
            video(VAI + "\nkho: ngang")

    def test_giao_dien_va_vai_chi_cho_ngan(self):
        for dong in ("giao-dien: toi-du-lieu", "vai: a = hoc-sinh-nam"):
            with self.subTest(dong=dong), self.assertRaises(parse.ParseError):
                parse.parse(f"---\ntieu-de: A\nmon: B\nlop: 1\n{dong}\n---\n\n## Cảnh 1\nloai: tieu-de\nchu: A\nloi: B.\n")

    def test_giao_dien_toi(self):
        self.assertEqual(video(VAI + "\ngiao-dien: toi-du-lieu").meta["giao-dien"], "toi-du-lieu")

    def test_goi_y_ngat_khong_doc(self):
        c = video().canh[0]
        self.assertNotIn(" / ", c.loi)
        self.assertIn(" / ", c.truong["loi-phu-de"][0])


class VaiTest(unittest.TestCase):
    def test_vai_lam_san_va_ghep(self):
        d = ngan.doc_dan_vai("a = co-giao; b = nam, toc troc, ao vest xam, duoi quan den, mu ke-pi, phu phu-hieu kinh")
        self.assertEqual(d["a"]["ao"]["kieu"], "ao-dai")
        self.assertEqual((d["b"]["toc"], d["b"]["ao"]["kieu"], d["b"]["mu"]), ("troc", "vest", "ke-pi"))
        self.assertEqual(d["b"]["ao"]["mau"], ngan.MAU["xam"])
        self.assertEqual(d["b"]["phu"], ["phu-hieu", "kinh"])

    def test_vai_nu_mac_dinh_toc_dai_va_ma_mau(self):
        d = ngan.doc_dan_vai("x = nu, ao the-thao #12AB34")
        self.assertEqual((d["x"]["toc"], d["x"]["ao"]["mau"]), ("dai", "#12AB34"))

    def test_bo_phan_sai_va_ten_sai(self):
        for gia_tri in ("a = nam, ao ao-giap", "A = nam", "a = nam; a = nu", "a = nam, mau-ao do"):
            with self.subTest(gia_tri=gia_tri), self.assertRaises(ngan.VaiError):
                ngan.doc_dan_vai(gia_tri)

    def test_vai_chua_khai_bao(self):
        with self.assertRaises(parse.ParseError):
            video(VAI, "\n## Cảnh 2\nloi: Chào bạn.\nnhip: @dau | nguoi: bac-si-la dung\n")

    def test_tu_the_sai(self):
        with self.assertRaises(parse.ParseError):
            video(VAI, "\n## Cảnh 2\nloi: Chào bạn.\nnhip: @dau | nguoi: an nhay-mua\n")

    def test_vai_lam_san_goi_thang(self):
        v = video(VAI, "\n## Cảnh 2\nloi: Chào bạn.\nnhip: @dau | nguoi: bac-si chao\n")
        self.assertEqual(v.canh[1].nhip[0].noi_dung, "bac-si chao")


class VatMoiTest(unittest.TestCase):
    def canh(self, nhip, loi="Chào các bạn nhé."):
        return video(VAI, f"\n## Cảnh 2\nloi: {loi}\nnhip: @dau | {nhip}\n").canh[1]

    def test_vat_hop_le(self):
        for nhip, vat in (("bieu-tuong: bulb | Ý tưởng", "bieu-tuong"), ("truoc-sau: 80,4% -> 71,8% | trước | sau", "truoc-sau"),
                          ("tin-nhan: ban: Đi chơi không?; minh: Ok luôn | dien-thoai", "tin-nhan"),
                          ("thong-bao: Zalo | Lớp 10A | Mai nghỉ học | tren", "thong-bao"),
                          ("trich-dan: \"Học, học nữa\" | Lênin", "trich-dan"), ("nhom: an dung; linh chao", "nhom"),
                          ("so: {{30}} mét", "so")):
            with self.subTest(vat=vat):
                n = self.canh(nhip).nhip[0]
                self.assertEqual(n.vat, vat)
        n = self.canh("thong-bao: Zalo | Lớp 10A | Mai nghỉ học | tren").nhip[0]
        self.assertEqual((n.o, n.noi_dung), ("tren", "Zalo | Lớp 10A | Mai nghỉ học"))
        self.assertEqual(self.canh("tin-nhan: ban: A; minh: B | dien-thoai").nhip[0].tuy_chon, ("dien-thoai",))

    def test_vat_sai(self):
        for nhip in ("luoi-cham: 12/10 | x", "luoi-cham: 5/300 | x", "thong-bao: Ứng dụng quá dài mười bảy | a | b",
                     "tin-nhan: ho: chào", "bieu-tuong: khong-co-bieu-tuong-nay", "nhom: an dung",
                     "anh: ve: một con mèo", "the: A | B | C | dien-thoai"):
            with self.subTest(nhip=nhip), self.assertRaises(parse.ParseError):
                self.canh(nhip)


class PhuDeTest(unittest.TestCase):
    def dong(self, loi):
        return [" ".join(w["chu"] for w in d) for d in ngan.chia_dong(ngan.tach_tu(loi))]

    def test_tu_khoa_theo_dau_nhan(self):
        ws = ngan.tach_tu("Có ==lực hút== và ((sóng)) cao {{30.5}} mét, **nguyên nhân** __bão__?")
        kieu = {w["chu"]: w["kieu"] for w in ws}
        self.assertEqual((kieu["lực"], kieu["sóng"], kieu["30,5"], kieu["nguyên"], kieu["bão?"]),
                         ("to", "khoanh", "so", "nhan", "gach"))
        self.assertEqual(kieu["Có"], None)

    def test_khong_ngat_giua_cum_nhan_va_tu_ghep(self):
        for loi, cum in (("Người ta đồn có ((lực hút)) ma quái rất đáng sợ.", "lực hút"),
                         ("Nhưng khoa học chỉ ra bão lớn và sóng dữ mới là nguyên nhân.", "sóng dữ")):
            with self.subTest(loi=loi):
                dong = self.dong(loi)
                self.assertTrue(any(cum in d for d in dong), dong)
                self.assertTrue(all(len(d) <= ngan.PHU_DE_DONG for d in dong), dong)

    def test_goi_y_ngat_duoc_ton_trong(self):
        self.assertEqual(self.dong("Hãy nói rõ / lý do của mình."), ["Hãy nói rõ", "lý do của mình."])

    def test_moc_thoi_gian_va_dong(self):
        du = du_canh(video())
        pd = du["phuDe"]
        self.assertGreater(len(pd), 2)
        self.assertEqual([d["tu"] for d in pd], sorted(d["tu"] for d in pd))
        for a, b in zip(pd, pd[1:]):
            self.assertLessEqual(a["den"], b["tu"] + 1e-6)
        self.assertTrue(any(w["kieu"] == "to" for d in pd for w in d["chu"]))


class TrangTest(unittest.TestCase):
    def test_du_lieu_va_trang(self):
        du = du_canh(video())
        self.assertEqual((du["loai"], du["giaoDien"], du["tieuDe"], du["chuong"]), ("ngan", "phang-sang", "Bị nhờ vả", "1 · VÍ DỤ"))
        self.assertEqual(set(du["vai"]), {"an", "linh"})
        self.assertEqual(du["vai"]["linh"]["ao"]["mau"], ngan.MAU["hong"])
        html = trang.dung_trang(du)
        for chuoi in ("THI_NHAN_VAT_PHANG", "THI_NGAN", "font-family:'Baloo'", "font-family:'Lobster'", "font-family:'Phudu'",
                      'class="phang-sang"'):
            self.assertIn(chuoi, html)
        self.assertNotRegex(html, r"https?://(?!www\.w3\.org)")


class AmThanhTest(unittest.TestCase):
    def test_loai_moi_co_cong_thuc(self):
        for loai in ("vut", "pop", "bup", "dem", "ding"):
            self.assertIn(loai, am_thanh.LOAI)
            self.assertIn(loai, am_thanh.CONG_THUC)
            self.assertIn(loai, am_thanh.DINH_MAU)


@unittest.skipUnless(CO_CHROMIUM, "cần Chromium")
class NganChromiumTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cm = chup.trinh_duyet()
        cls.browser = cls.cm.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.cm.__exit__(None, None, None)

    def mo(self, du):
        page = chup.trang_moi(self.browser, kho.Kho("doc", 720))
        chup.mo_trang(page, trang.dung_trang(du))
        return page

    def test_khong_tran_phu_de_hien_va_doi_tu_the(self):
        for gd in ("phang-sang", "toi-du-lieu"):
            with self.subTest(giao_dien=gd):
                du = du_canh(video(VAI + f"\ngiao-dien: {gd}"))
                page = self.mo(du)
                try:
                    self.assertEqual(page.evaluate("() => window.THI_VIDEO.kiemTran()"), [])
                    t = du["phuDe"][1]["tu"] + 0.05
                    kq = page.evaluate("""(t) => { window.datThoiDiem(t);
                      var d = [...document.querySelectorAll('.dong-pd')].filter(e => e.style.display === 'block');
                      var r = d.length ? d[0].getBoundingClientRect() : null;
                      return {so: d.length, giua: r ? (r.left + r.right) / 2 : -1,
                              svg: document.querySelector('.lop-nv').innerHTML.length,
                              lop: document.querySelector('#khung').className}; }""", t)
                    self.assertEqual(kq["so"], 1)
                    self.assertAlmostEqual(kq["giua"], 360, delta=2)
                    self.assertIn(gd, kq["lop"])
                    self.assertGreater(kq["svg"], 500)
                    su = page.evaluate("() => window.THI_VIDEO.suKien().map(e => e.loai)")
                    self.assertIn("bup", su)     # nhân vật đổi tư thế
                    self.assertIn("dem", su)     # lưới chấm
                    # Nhân vật `an`: tư thế lúc đầu khác lúc vò đầu.
                    hinh = page.evaluate("""(ts) => ts.map(t => { window.datThoiDiem(t);
                        return document.querySelector('.lop-nv g').innerHTML; })""",
                                         [1.5, du["nhip"][2]["batDau"] + 1.5])
                    self.assertNotEqual(hinh[0], hinh[1])
                finally:
                    page.close()

    def test_dung_lap_lai_cung_anh(self):
        du = du_canh(video())
        anh = []
        for _ in range(2):
            page = self.mo(du)
            try:
                page.evaluate("(t) => window.datThoiDiem(t)", du["nhip"][3]["batDau"] + 0.7)
                anh.append(page.screenshot(type="png"))
            finally:
                page.close()
        self.assertEqual(anh[0], anh[1])


if __name__ == "__main__":
    unittest.main()

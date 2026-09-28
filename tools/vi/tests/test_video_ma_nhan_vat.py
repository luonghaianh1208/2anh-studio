"""Người que (`nhan-vat: nguoi-que`, trường `tu-the`) trên Chromium: nhân vật ở cột phụ của `tieu-de`, `khai-niem`,
`y-tung-y` nằm gọn trong ô, không đè dòng chữ nào (giao hộp bằng 0), quay mặt về phía nội dung; chữ ở đúng giới hạn
vẫn không tràn (2 khổ × 2 phong cách, có và không có thẻ); mười tư thế đều dựng được.

Phần Chromium tự bỏ qua nếu máy thiếu."""

import sys
import tempfile
import unittest
from pathlib import Path

TOOLS_VI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_VI))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import video_ma  # noqa: E402
from do_gioi_han import meta, ngoai_vung, them_the  # noqa: E402
from test_video_ma_kho_doc import canh_toi_da, thu_muc_bai, video_md  # noqa: E402
from video_ma_parts import chup, kho, kiem, parse  # noqa: E402

CO_CHROMIUM = video_ma.co_chromium()
LOAI = ("tieu-de", "khai-niem", "y-tung-y")

# Hộp nhân vật và các dòng chữ (Range) của lớp bảng, toạ độ khung: [nhãn, trái, trên, phải, dưới].
HOP = """() => {
  const k = document.getElementById('khung').getBoundingClientRect();
  const kq = [];
  const them = (ten, r) => { if (r.width > 0 && r.height > 0) { kq.push([ten, r.left - k.left, r.top - k.top, r.right - k.left, r.bottom - k.top]); } };
  document.querySelectorAll('#bang .chu').forEach((el) => {
    const r = document.createRange(); r.selectNodeContents(el);
    [...r.getClientRects()].forEach((c) => them('chu:' + el.dataset.id, c));
  });
  const nv = document.querySelector('#bang svg.ve g.nhan-vat');
  if (nv) { them('nhan-vat', nv.getBoundingClientRect()); }
  return kq;
}"""


def giao(a, b) -> bool:
    return a[1] < b[3] and b[1] < a[3] and a[2] < b[4] and b[2] < a[4]


def nhan_vat(ds: list, ten: str = "giai-thich") -> list:
    """Cảnh có cột phụ (canh_toi_da(cot=True)) của ba loại nhận `tu-the`, thay hình bằng nhân vật."""
    return [(loai, noi.replace("hinh: clock\n", f"tu-the: {ten}\n")) for loai, noi in ds if loai in LOAI]


@unittest.skipUnless(CO_CHROMIUM, "máy không có Chromium hoặc playwright")
class NhanVatChromiumTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.cm = chup.trinh_duyet()
        cls.browser = cls.cm.__enter__()
        cls.dem = 0

    @classmethod
    def tearDownClass(cls):
        cls.cm.__exit__(None, None, None)
        cls.tmp.cleanup()

    def trang(self, ds: list, ten_kho: str, phong_cach: str) -> list:
        type(self).dem += 1
        thu_muc = thu_muc_bai(Path(self.tmp.name) / f"b{self.dem}",
                              video_md(ds, meta(ten_kho, phong_cach) + "nhan-vat: nguoi-que\nmau-ao: xanh-duong\n"))
        video = parse.parse((thu_muc / "video.md").read_text(encoding="utf-8"))
        self.assertEqual(kiem.kiem(video, thu_muc), [])
        return list(zip(video.canh, video_ma._trang_tam(video, thu_muc, video_ma._mo_hinh(video, thu_muc))))

    def kiem_nhan_vat(self, page, html: str, canh, ten_kho: str):
        tran, ra = ngoai_vung(page, html, ten_kho)
        self.assertEqual(tran, [])
        self.assertEqual(ra, [])
        hop = page.evaluate(HOP)
        nv = [h for h in hop if h[0] == "nhan-vat"]
        self.assertEqual(len(nv), 1)
        nv = nv[0]
        o = kho.o(ten_kho, "cot-phu")
        if "the" in canh.truong and ten_kho == "doc":
            dich = kho.o("doc", "the")["h"] + 20
            o = {**o, "y": o["y"] + dich, "h": o["h"] - dich}
        self.assertGreaterEqual(nv[1], o["x"] - 1, nv)
        self.assertGreaterEqual(nv[2], o["y"] - 1, nv)
        self.assertLessEqual(nv[3], o["x"] + o["w"] + 1, nv)
        self.assertLessEqual(nv[4], o["y"] + o["h"] + 1, nv)
        for h in hop:
            if h[0] != "nhan-vat":
                self.assertFalse(giao(nv, h), (nv, h))
        return nv

    def test_cot_phu_chu_toi_da_hai_kho_hai_phong_cach_co_va_khong_the(self):
        for ten_kho in ("ngang", "doc"):
            for phong_cach in ("viet-tay", "cat-dan"):
                for co_the in (False, True):
                    L, H = kiem.bang_gioi_han(ten_kho, phong_cach, co_the)
                    ds = nhan_vat(canh_toi_da(L, H, cot=True))
                    if co_the:
                        ds = them_the(ds)
                    page = chup.trang_moi(self.browser, kho.Kho(ten_kho, 720))
                    try:
                        for canh, html in self.trang(ds, ten_kho, phong_cach):
                            with self.subTest(kho=ten_kho, phong_cach=phong_cach, co_the=co_the, loai=canh.loai):
                                self.kiem_nhan_vat(page, html, canh, ten_kho)
                                lat = page.evaluate("() => document.querySelector('g.nhan-vat > g').getAttribute('transform')")
                                self.assertEqual("scale(-" in lat, ten_kho == "ngang", lat)
                                if phong_cach == "cat-dan":
                                    self.assertEqual(page.evaluate("() => document.querySelector('g.nhan-vat').getAttribute('filter')"),
                                                     "url(#bong-dan)")
                    finally:
                        page.close()

    def test_muoi_tu_the_khai_niem_hai_kho(self):
        for ten_kho, phong_cach in (("ngang", "viet-tay"), ("doc", "cat-dan")):
            ds = [("khai-niem", f"thuat-ngu: Lạm phát\ndinh-nghia: Mức giá chung tăng liên tục.\ntu-the: {ten}\n")
                  for ten in parse.TU_THE]
            page = chup.trang_moi(self.browser, kho.Kho(ten_kho, 720))
            try:
                for canh, html in self.trang(ds, ten_kho, phong_cach):
                    with self.subTest(kho=ten_kho, tu_the=canh.truong["tu-the"][0]):
                        self.kiem_nhan_vat(page, html, canh, ten_kho)
                        # Lúc bật vào (0,45 s, phóng lớn nhất) nhân vật vẫn không đè chữ.
                        page.evaluate("() => window.datThoiDiem(0.45)")
                        hop = page.evaluate(HOP)
                        nv = [h for h in hop if h[0] == "nhan-vat"][0]
                        for h in hop:
                            if h[0] != "nhan-vat":
                                self.assertFalse(giao(nv, h), (nv, h))
            finally:
                page.close()

    def test_khong_tu_the_khong_co_nhan_vat(self):
        page = chup.trang_moi(self.browser, kho.Kho("ngang", 720))
        try:
            (_, html), = self.trang([("khai-niem", "thuat-ngu: A\ndinh-nghia: B\n")], "ngang", "viet-tay")
            self.assertEqual(chup.kiem_tran(page, html), [])
            self.assertEqual(page.evaluate("() => document.querySelectorAll('g.nhan-vat').length"), 0)
        finally:
            page.close()


if __name__ == "__main__":
    unittest.main()

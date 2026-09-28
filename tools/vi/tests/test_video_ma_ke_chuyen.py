"""Cảnh kể chuyện (`ke-chuyen`) trên Chromium: nền mẫu `lop-hoc` + người que ở 2 khổ × 2 phong cách, tiêu đề ở đúng
giới hạn, có và không có thẻ/dòng tài liệu: không tràn, nhân vật trong ô `nhan-vat-<vi-tri>` và không đè chữ; nền phủ
kín khung (bốn góc không trong suốt, đầu và cuối cảnh, cả ảnh vuông); nhân vật ảnh giả (PNG trong suốt tạo bằng FFmpeg)
hiện đúng ô; tiêu đề viet-tay đọc được trên `lop-hoc` và `bau-troi` (viền tối quanh chữ vàng).

Phần Chromium/FFmpeg tự bỏ qua nếu máy thiếu."""

import base64
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

import video_ma  # noqa: E402
from do_gioi_han import meta, ngoai_vung  # noqa: E402
from test_video_ma_kho_doc import chuoi, thu_muc_bai, video_md  # noqa: E402
from video_ma_parts import chup, kho, kiem, parse  # noqa: E402

CO_CHROMIUM = video_ma.co_chromium()
CO_FFMPEG = shutil.which("ffmpeg") is not None

# Hộp nhân vật và các dòng chữ (Range) của lớp bảng, toạ độ khung: [nhãn, trái, trên, phải, dưới].
HOP = """() => {
  const k = document.getElementById('khung').getBoundingClientRect();
  const kq = [];
  const them = (ten, r) => { if (r.width > 0 && r.height > 0) { kq.push([ten, r.left - k.left, r.top - k.top, r.right - k.left, r.bottom - k.top]); } };
  document.querySelectorAll('#bang .chu').forEach((el) => {
    const r = document.createRange(); r.selectNodeContents(el);
    [...r.getClientRects()].forEach((c) => them('chu:' + el.dataset.id, c));
  });
  const nv = document.querySelector('#bang .nhan-vat');
  if (nv) { them('nhan-vat', nv.getBoundingClientRect()); }
  return kq;
}"""

# Alpha của bốn điểm ảnh góc của một ảnh PNG (data URL).
GOC = """async (u) => {
  const i = new Image(); await new Promise((ok, loi) => { i.onload = ok; i.onerror = loi; i.src = u; });
  const c = document.createElement('canvas'); c.width = i.naturalWidth; c.height = i.naturalHeight;
  const g = c.getContext('2d'); g.drawImage(i, 0, 0);
  const w = c.width - 1, h = c.height - 1;
  return [[0, 0], [w, 0], [0, h], [w, h]].map(([x, y]) => g.getImageData(x, y, 1, 1).data[3]);
}"""

# So hai ảnh cùng vùng tiêu đề (có và không có tiêu đề): điểm ảnh đổi là chữ và viền; độ chói tương đối (WCAG) của
# phần sáng (chữ), phần tối (viền) và nền trung bình ở chỗ đó.
TUONG_PHAN = """async ([a, b]) => {
  const tai = (u) => new Promise((ok, loi) => { const i = new Image(); i.onload = () => ok(i); i.onerror = loi; i.src = u; });
  const [ia, ib] = await Promise.all([tai(a), tai(b)]);
  const w = ia.naturalWidth, h = ia.naturalHeight;
  const doc = (i) => { const c = document.createElement('canvas'); c.width = w; c.height = h;
    const g = c.getContext('2d'); g.drawImage(i, 0, 0); return g.getImageData(0, 0, w, h).data; };
  const da = doc(ia), db = doc(ib);
  const lin = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
  const L = (d, k) => 0.2126 * lin(d[k]) + 0.7152 * lin(d[k + 1]) + 0.0722 * lin(d[k + 2]);
  let n = 0, toi = 0, sang = 0, lToi = 0, lSang = 0, lNen = 0, m = 0;
  for (let k = 0; k < da.length; k += 4) {
    lNen += L(db, k); m++;
    if (Math.abs(da[k] - db[k]) + Math.abs(da[k + 1] - db[k + 1]) + Math.abs(da[k + 2] - db[k + 2]) < 60) { continue; }
    n++;
    const l = L(da, k);
    if (l < 0.05) { toi++; lToi += l; } else if (l > 0.45) { sang++; lSang += l; }
  }
  return {n: n, toi: toi, sang: sang, lToi: toi ? lToi / toi : null, lSang: sang ? lSang / sang : null, lNen: lNen / m};
}"""


def ti_so(a: float, b: float) -> float:
    return (max(a, b) + 0.05) / (min(a, b) + 0.05)


def ke(so: int, nen: str, them: str = "") -> tuple:
    return ("ke-chuyen", f"tieu-de: {chuoi(20)}\nnen: {nen}\n{them}")


def png_trong_suot(path: Path, rong: int = 300, cao: int = 600) -> None:
    """PNG RGBA: nền trong suốt, một hình chữ nhật đục ở giữa (nhân vật giả)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "lavfi", "-i",
                    f"color=c=black@0.0:s={rong}x{cao},format=rgba,drawbox=x=60:y=40:w=180:h=540:color=red@1:t=fill",
                    "-frames:v", "1", str(path)], check=True, timeout=60)


def nguon_ai(thu_muc: Path, *cac_file: str) -> None:
    ds = [{"file": f, "cong_cu": "thử", "mo_hinh": "Mô hình thử", "prompt": "x", "ngay": "2026-09-28"} for f in cac_file]
    (thu_muc / "anh" / "ai" / "nguon.json").write_text(json.dumps(ds, ensure_ascii=False), encoding="utf-8")


def data_url(anh: bytes) -> str:
    return "data:image/png;base64," + base64.b64encode(anh).decode("ascii")


@unittest.skipUnless(CO_CHROMIUM, "máy không có Chromium hoặc playwright")
class KeChuyenChromiumTest(unittest.TestCase):
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

    def trang(self, ds: list, ten_kho: str, phong_cach: str, meta_them: str = "nhan-vat: nguoi-que\n", chuan_bi=None) -> list:
        type(self).dem += 1
        thu_muc = thu_muc_bai(Path(self.tmp.name) / f"k{self.dem}", video_md(ds, meta(ten_kho, phong_cach) + meta_them))
        if chuan_bi:
            chuan_bi(thu_muc)
        video = parse.parse((thu_muc / "video.md").read_text(encoding="utf-8"))
        self.assertEqual(kiem.kiem(video, thu_muc), [])
        return list(zip(video.canh, video_ma._trang_tam(video, thu_muc, {})))

    def o_nhan_vat(self, canh, ten_kho: str) -> dict:
        vi_tri = canh.truong.get("vi-tri", ["phai" if canh.so % 2 == 0 else "trai"])[0]
        o = kho.o(ten_kho, f"nhan-vat-{vi_tri}")
        if "tai-lieu" in canh.truong:
            tl = kho.o(ten_kho, "tai-lieu")
            if o["x"] < tl["x"] + tl["w"] and tl["x"] < o["x"] + o["w"]:
                o["h"] = tl["y"] - 6 - o["y"]
        return o

    def kiem_canh(self, page, html: str, canh, ten_kho: str) -> list:
        tran, ra = ngoai_vung(page, html, ten_kho)
        self.assertEqual(tran, [])
        self.assertEqual(ra, [])
        hop = page.evaluate(HOP)
        nv = [h for h in hop if h[0] == "nhan-vat"]
        self.assertEqual(len(nv), 1)
        nv = nv[0]
        o = self.o_nhan_vat(canh, ten_kho)
        self.assertGreaterEqual(nv[1], o["x"] - 1, nv)
        self.assertGreaterEqual(nv[2], o["y"] - 1, nv)
        self.assertLessEqual(nv[3], o["x"] + o["w"] + 1, nv)
        self.assertLessEqual(nv[4], o["y"] + o["h"] + 1, nv)
        for h in hop:
            if h[0] != "nhan-vat":
                self.assertFalse(h[1] < nv[3] and nv[1] < h[3] and h[2] < nv[4] and nv[2] < h[4], (nv, h))
        return nv

    def test_lop_hoc_nguoi_que_hai_kho_hai_phong_cach_khong_tran(self):
        the = f"the: {chuoi(24)} | {chuoi(16)} | {chuoi(60)}\ntai-lieu: {chuoi(90)}\n"
        for ten_kho in ("ngang", "doc"):
            n = kiem.bang_gioi_han(ten_kho)[0][("ke-chuyen", "tieu-de")]
            tieu_de = f"tieu-de: {chuoi(n)}\n"
            ds = [("ke-chuyen", f"{tieu_de}nen: mau/lop-hoc\ntu-the: chi-tay\n"),
                  ("ke-chuyen", f"{tieu_de}nen: nhu-canh 1\ntu-the: an-mung\n"),
                  ("ke-chuyen", f"{tieu_de}nen: mau/lop-hoc\nvi-tri: giua\n"),
                  ("ke-chuyen", f"{tieu_de}nen: mau/lop-hoc\ntu-the: giai-thich\n{the}"),
                  ("ke-chuyen", f"{tieu_de}nen: mau/lop-hoc\ntu-the: suy-nghi\n{the}"),
                  ("ke-chuyen", f"{tieu_de}nen: mau/lop-hoc\nvi-tri: giua\n{the}")]
            for phong_cach in ("viet-tay", "cat-dan"):
                page = chup.trang_moi(self.browser, kho.Kho(ten_kho, 720))
                try:
                    for canh, html in self.trang(ds, ten_kho, phong_cach):
                        with self.subTest(kho=ten_kho, phong_cach=phong_cach, so=canh.so):
                            self.kiem_canh(page, html, canh, ten_kho)
                            # Tiêu đề: viet-tay chữ hoa vàng; cat-dan có dải băng dính.
                            if phong_cach == "cat-dan":
                                self.assertGreater(page.evaluate("() => document.querySelectorAll('g.bang-dinh polygon').length"), 0)
                            else:
                                mau = page.evaluate("() => getComputedStyle(document.querySelector('[data-id=\"tieu-de\"]')).color")
                                self.assertEqual(mau, "rgb(255, 216, 77)")
                            # Nền là SVG nền mẫu, lớp đầu tiên của lớp bảng.
                            self.assertTrue(page.evaluate(
                                "() => document.querySelector('#bang').firstElementChild.matches('.nen-canh')"
                                " && !!document.querySelector('.nen-canh > svg.nen-mau')"))
                finally:
                    page.close()

    def goc_trong_suot(self, page, t: float) -> list:
        page.evaluate("(t) => window.datThoiDiem(t)", t)
        return page.evaluate(GOC, data_url(page.screenshot(omit_background=True)))

    def test_nen_phu_kin_bon_goc(self):
        def anh_vuong(thu_muc: Path):
            subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "lavfi", "-i",
                            "color=c=0x3366aa:s=1024x1024", "-frames:v", "1", str(thu_muc / "anh" / "vuong.png")],
                           check=True, timeout=60)
            (thu_muc / "anh" / "image_sources.json").write_text(
                json.dumps({"items": [{"filename": "vuong.png", "author": "Thử", "license": "CC0"}]}), encoding="utf-8")

        if not CO_FFMPEG:
            self.skipTest("máy không có FFmpeg")
        ds = [ke(1, "mau/lop-hoc"), ke(2, "vuong.png"), ke(3, "mau/bau-troi")]
        for ten_kho in ("ngang", "doc"):
            for phong_cach in ("viet-tay", "cat-dan"):
                page = chup.trang_moi(self.browser, kho.Kho(ten_kho, 720))
                try:
                    for canh, html in self.trang(ds, ten_kho, phong_cach, "", anh_vuong):
                        with self.subTest(kho=ten_kho, phong_cach=phong_cach, so=canh.so):
                            self.assertEqual(chup.kiem_tran(page, html), [])
                            chup.mo_trang(page, html)
                            page.add_style_tag(content="html, body, #khung, #khung.cat-dan { background: transparent !important; }"
                                                       " .nen-giay { display: none !important; }")
                            gh = page.evaluate("() => window.DU_CANH.thoiLuong")
                            for t in (0, gh / 2, gh - 0.2):
                                self.assertEqual(self.goc_trong_suot(page, t), [255, 255, 255, 255], t)
                            # Nền phóng 1,00 → 1,06 quanh tâm khung.
                            page.evaluate("(t) => window.datThoiDiem(t)", gh)
                            self.assertEqual(page.evaluate("() => getComputedStyle(document.querySelector('.nen-canh')).transform"),
                                             "matrix(1.06, 0, 0, 1.06, 0, 0)")
                finally:
                    page.close()

    @unittest.skipUnless(CO_FFMPEG, "máy không có FFmpeg")
    def test_nhan_vat_anh_gia_hien_dung_o(self):
        def ai(thu_muc: Path):
            for ten in ("tu-the-chao.png", "tu-the-dung.png"):
                png_trong_suot(thu_muc / "anh" / "ai" / ten)
            nguon_ai(thu_muc, "tu-the-chao.png", "tu-the-dung.png")

        ds = [ke(1, "mau/dong-que", "tu-the: chao\n"), ke(2, "mau/thanh-pho"),
              ke(3, "mau/vu-tru", f"vi-tri: giua\nthe: A | 1 | B\ntai-lieu: {chuoi(90)}\n"),
              ("khai-niem", "thuat-ngu: Lạm phát\ndinh-nghia: Mức giá chung tăng liên tục.\ntu-the: chao\n")]
        for ten_kho, phong_cach in (("ngang", "viet-tay"), ("doc", "cat-dan")):
            page = chup.trang_moi(self.browser, kho.Kho(ten_kho, 720))
            try:
                for canh, html in self.trang(ds, ten_kho, phong_cach, "nhan-vat: ve: cô giáo trẻ\n", ai):
                    with self.subTest(kho=ten_kho, so=canh.so):
                        if canh.loai == "ke-chuyen":
                            nv = self.kiem_canh(page, html, canh, ten_kho)
                            o = self.o_nhan_vat(canh, ten_kho)
                            # Ảnh 1:2 vừa ô, chân ở đáy ô lùi 10, giữa ô.
                            self.assertAlmostEqual((nv[3] - nv[1]) / (nv[4] - nv[2]), 0.5, delta=0.01)
                            self.assertAlmostEqual(nv[4], o["y"] + o["h"] - 10, delta=1)
                            self.assertAlmostEqual((nv[1] + nv[3]) / 2, o["x"] + o["w"] / 2, delta=1)
                        else:
                            self.assertEqual(ngoai_vung(page, html, ten_kho), ([], []))
                        self.assertTrue(page.evaluate(
                            "() => { const i = document.querySelector('.nhan-vat-anh img'); return i.complete && i.naturalWidth === 300; }"))
                        self.assertEqual(page.evaluate("() => document.querySelectorAll('g.nhan-vat').length"), 0)
            finally:
                page.close()

    def test_tieu_de_viet_tay_doc_duoc_tren_lop_hoc_va_bau_troi(self):
        ds = [ke(1, "mau/lop-hoc", "vi-tri: giua\n"), ke(2, "mau/bau-troi", "vi-tri: giua\n")]
        for ten_kho in ("ngang", "doc"):
            page = chup.trang_moi(self.browser, kho.Kho(ten_kho, 720))
            try:
                for canh, html in self.trang(ds, ten_kho, "viet-tay"):
                    with self.subTest(kho=ten_kho, nen=canh.truong["nen"][0]):
                        chup.mo_trang(page, html)
                        page.evaluate("() => window.datThoiDiem(window.DU_CANH.thoiLuong - 0.2)")
                        r = page.evaluate("() => { const g = document.createRange();"
                                          " g.selectNodeContents(document.querySelector('[data-id=\"tieu-de\"]'));"
                                          " const b = g.getBoundingClientRect(); return [b.left, b.top, b.width, b.height]; }")
                        clip = {"x": max(0, r[0] - 6), "y": max(0, r[1] - 6), "width": r[2] + 12, "height": r[3] + 12}
                        co = page.screenshot(clip=clip)
                        page.add_style_tag(content="[data-id='tieu-de'] { visibility: hidden !important; }")
                        khong = page.screenshot(clip=clip)
                        kq = page.evaluate(TUONG_PHAN, [data_url(co), data_url(khong)])
                        self.assertGreater(kq["n"], 500, kq)
                        # Viền tối và chữ sáng đều hiện rõ; viền tách chữ khỏi mọi nền.
                        self.assertGreater(kq["toi"] / kq["n"], 0.2, kq)
                        self.assertGreater(kq["sang"] / kq["n"], 0.2, kq)
                        self.assertGreater(ti_so(kq["lSang"], kq["lToi"]), 7, kq)
                        self.assertGreater(max(ti_so(kq["lSang"], kq["lNen"]), ti_so(kq["lToi"], kq["lNen"])), 3, kq)
            finally:
                page.close()


if __name__ == "__main__":
    unittest.main()

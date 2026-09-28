"""Kho 8 nền mẫu (runtime/nen-mau.js): trang cảnh nạp nen-mau.js; trên Chromium, mỗi nền × 2 khổ dựng ra ảnh
(PNG kiểu `xem-truoc` trong thư mục tạm) và vùng ô `noi-dung` có độ lệch chuẩn độ sáng ≤ 40 (thang 0–255),
để chữ và nhân vật đặt lên vẫn đọc được.

Phần Chromium tự bỏ qua nếu máy thiếu."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS_VI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_VI))

import video_ma  # noqa: E402
from video_ma_parts import chup, kho, trang  # noqa: E402

RUNTIME = TOOLS_VI / "video_ma_parts" / "runtime"
TEN = ("giay", "bau-troi", "vu-tru", "lop-hoc", "phong-thi-nghiem", "thanh-pho", "dong-que", "vong-tron")
CO_CHROMIUM = video_ma.co_chromium()
LECH_TOI_DA = 40


def trang_nen(ten: str, ten_kho: str, hat: int = 3) -> str:
    """Trang chỉ có một nền mẫu, đúng khổ, dựng bằng chính các file runtime."""
    rong, cao, day = kho.CAC_KHO[ten_kho]
    k = {"ten": ten_kho, "rong": rong, "cao": cao, "day": day}
    js = "".join(f"<script>\n{(RUNTIME / f).read_text(encoding='utf-8-sig')}\n</script>\n" for f in ("cat-dan.js", "nen-mau.js"))
    return ("<!doctype html><html><head><meta charset=\"utf-8\"><style>html,body{margin:0;background:#000}"
            "svg{display:block}</style></head><body>"
            f"<script>window.THI_O_BO_CUC = {trang.json_nhung(kho.O)};</script>\n{js}"
            f"<script>document.body.innerHTML = THI_NEN_MAU.ve({json.dumps(ten)}, {json.dumps(k)}, {hat});</script>"
            "</body></html>")


# Vẽ SVG vào canvas đúng khổ rồi tính độ lệch chuẩn độ sáng (Rec. 601) trên hộp o = {x, y, w, h}.
DO_LECH = """async (o) => {
  const svg = document.querySelector('svg');
  const w = +svg.getAttribute('width'), h = +svg.getAttribute('height');
  const url = URL.createObjectURL(new Blob([new XMLSerializer().serializeToString(svg)], {type: 'image/svg+xml'}));
  const img = new Image();
  await new Promise((ok, loi) => { img.onload = ok; img.onerror = loi; img.src = url; });
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  const g = c.getContext('2d'); g.drawImage(img, 0, 0);
  const d = g.getImageData(o.x, o.y, o.w, o.h).data;
  let n = 0, s = 0, s2 = 0;
  for (let i = 0; i < d.length; i += 4) {
    const l = 0.299 * d[i] + 0.587 * d[i + 1] + 0.114 * d[i + 2];
    n++; s += l; s2 += l * l;
  }
  const tb = s / n;
  return {tb: tb, lech: Math.sqrt(Math.max(0, s2 / n - tb * tb))};
}"""


class NapTrangTest(unittest.TestCase):
    def test_trang_canh_nap_nen_mau(self):
        du = {"loai": "tieu-de", "kho": {"ten": "ngang", "rong": 1280, "cao": 720, "day": 620}}
        html = trang.dung_trang(du)
        self.assertTrue("root.THI_NEN_MAU =" in html, "trang không nạp nen-mau.js")
        # Nạp sau cat-dan.js (giay dùng lại nenGiay).
        self.assertLess(html.index("root.THI_CAT_DAN ="), html.index("root.THI_NEN_MAU ="))


@unittest.skipUnless(CO_CHROMIUM, "máy không có Chromium hoặc playwright")
class NenMauChromiumTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.cm = chup.trinh_duyet()
        cls.browser = cls.cm.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.cm.__exit__(None, None, None)
        cls.tmp.cleanup()

    def test_vung_giua_do_tuong_phan_thap(self):
        thu_muc = Path(self.tmp.name) / "xem-truoc"
        thu_muc.mkdir()
        for ten_kho in ("ngang", "doc"):
            rong, cao, _ = kho.CAC_KHO[ten_kho]
            page = self.browser.new_page(viewport={"width": rong, "height": cao})
            try:
                for ten in TEN:
                    with self.subTest(nen=ten, kho=ten_kho):
                        page.set_content(trang_nen(ten, ten_kho))
                        anh = thu_muc / f"{ten}-{ten_kho}.png"
                        page.screenshot(path=str(anh))
                        self.assertGreater(anh.stat().st_size, 5000)
                        kq = page.evaluate(DO_LECH, kho.o(ten_kho, "noi-dung"))
                        self.assertLessEqual(kq["lech"], LECH_TOI_DA, kq)
            finally:
                page.close()


if __name__ == "__main__":
    unittest.main()

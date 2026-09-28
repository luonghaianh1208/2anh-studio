"""Thẻ thông tin (`the`), dòng tài liệu (`tai-lieu`), công thức không ngắt và khung loạt (`loat`) trên Chromium:
thẻ ở đúng giới hạn nằm gọn trong ô và không đè chữ, hình, ảnh (2 khổ × 2 phong cách); công thức "M x V = P x Y" khổ
dọc một dòng; phần công thức quá rộng là lỗi `canh`; khung loạt đứng yên khi máy quay chạy; nguồn ảnh xếp trên dòng
tài liệu.

Phần Chromium tự bỏ qua nếu máy thiếu."""

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS_VI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_VI))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import video_ma  # noqa: E402
from do_gioi_han import LOAI_CO_THE, meta, ngoai_vung, them_the  # noqa: E402
from test_video_ma_kho_doc import canh_toi_da, chuoi, thu_muc_bai, video_md  # noqa: E402
from video_ma_parts import chup, kho, kiem, parse  # noqa: E402

CO_CHROMIUM = video_ma.co_chromium()
NGUON_ANH = "Hình vẽ minh hoạ · PPT Master bản Việt · CC0 1.0"
# Thẻ ở đúng giới hạn (nhãn 24, giá trị 16, chú thích 60), chữ nhiều dấu.
THE_TOI_DA = f"the: {chuoi(24)} | {chuoi(16)} | {chuoi(60)}\n"
NOI_DUNG = {
    "tieu-de": "chu: Vì sao in thêm tiền lại gây lạm phát\nphu: Kinh tế học nhập môn\n",
    "khai-niem": "thuat-ngu: Lạm phát\ndinh-nghia: Mức giá chung của nền kinh tế tăng liên tục trong một thời gian.\n",
    "cong-thuc": "bieu-thuc: M x V = P x Y\ngiai-thich: M là lượng tiền\ngiai-thich: V là vòng quay của tiền\n",
    "y-tung-y": "tieu-de: Ba nguyên nhân lạm phát\ny: Cầu kéo\ny: Chi phí đẩy\ny: In thêm tiền\n",
}

# Hộp (toạ độ khung, Z = 1) của các phần tử sau kiemTran(): chữ theo từng dòng (Range của từng nút chữ, không tính hộp
# của phần tử bọc như `.trong`), hình SVG, ảnh, giấy thẻ và các dòng của khối tài liệu. [nhãn, trái, trên, phải, dưới].
HOP = """() => {
  const k = document.getElementById('khung').getBoundingClientRect();
  const kq = [];
  const them = (ten, r) => { if (r.width > 0 && r.height > 0) { kq.push([ten, r.left - k.left, r.top - k.top, r.right - k.left, r.bottom - k.top]); } };
  document.querySelectorAll('#bang .chu').forEach((el) => {
    const id = el.dataset.id;
    if (id === 'the-nen') { them(id, el.getBoundingClientRect()); return; }
    const w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    for (let n = w.nextNode(); n; n = w.nextNode()) {
      if (!n.textContent.trim()) { continue; }
      const r = document.createRange(); r.selectNodeContents(n);
      [...r.getClientRects()].forEach((c) => them(id, c));
    }
  });
  document.querySelectorAll('#bang svg.ve g.hinh, #bang svg.ve g.hinh-dan').forEach((el) => them('hinh', el.getBoundingClientRect()));
  document.querySelectorAll('#bang .anh .cua-anh').forEach((el) => them('anh', el.getBoundingClientRect()));
  document.querySelectorAll('#bang .dong-nguon .dong').forEach((el, i) => them('dong-' + i, el.getBoundingClientRect()));
  return kq;
}"""


def giao(a, b, le: float = 0.5) -> bool:
    return a[1] < b[3] - le and b[1] < a[3] - le and a[2] < b[4] - le and b[2] < a[4] - le


def chay(thu_muc: Path, *them: str) -> dict:
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
        video_ma.main([str(thu_muc), *them])
    return json.loads(out.getvalue().strip().splitlines()[-1])


@unittest.skipUnless(CO_CHROMIUM, "máy không có Chromium hoặc playwright")
class TheChromiumTest(unittest.TestCase):
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

    def trang(self, ds: list, ten_kho: str, phong_cach: str, meta_them: str = "", kiem_truoc: bool = True) -> list:
        type(self).dem += 1
        thu_muc = thu_muc_bai(Path(self.tmp.name) / f"b{self.dem}", video_md(ds, meta(ten_kho, phong_cach) + meta_them))
        video = parse.parse((thu_muc / "video.md").read_text(encoding="utf-8"))
        if kiem_truoc:
            self.assertEqual(kiem.kiem(video, thu_muc), [])
        return list(zip(video.canh, video_ma._trang_tam(video, thu_muc, video_ma._mo_hinh(video, thu_muc))))

    def test_the_o_gioi_han_nam_gon_khong_de_noi_dung_hai_kho_hai_phong_cach(self):
        for ten_kho in ("ngang", "doc"):
            k = kho.Kho(ten_kho, 720)
            o_the = kho.o(ten_kho, "the")
            for phong_cach in ("viet-tay", "cat-dan"):
                ds = [(loai, noi + THE_TOI_DA + cot) for loai, noi in NOI_DUNG.items()
                      for cot in ("", "hinh: clock\n", f"anh: con-lac.png\nnguon: {NGUON_ANH}\n")]
                page = chup.trang_moi(self.browser, k)
                try:
                    for canh, html in self.trang(ds, ten_kho, phong_cach):
                        with self.subTest(kho=ten_kho, phong_cach=phong_cach, so=canh.so, loai=canh.loai):
                            self.assertEqual(chup.kiem_tran(page, html), [])
                            hop = page.evaluate(HOP)
                            the = [h for h in hop if h[0].startswith("the-")]
                            self.assertEqual({h[0] for h in the} - {"the-nen"},
                                             {"the-nhan", "the-gia-tri", "the-chu-thich"})
                            khac = [h for h in hop if not h[0].startswith("the-")]
                            self.assertTrue(khac)
                            for h in the:
                                self.assertGreaterEqual(h[1], -1, h)
                                self.assertLessEqual(h[3], k.rong + 1, h)
                                self.assertLessEqual(h[4], k.day + 1, h)
                                # Chữ thẻ trong ô thẻ (khổ dọc cảnh bìa: đỉnh ô bìa).
                                if canh.loai != "tieu-de" or ten_kho == "ngang":
                                    self.assertGreaterEqual(h[2], o_the["y"] - 1, h)
                                    self.assertLessEqual(h[4], o_the["y"] + o_the["h"] + 5, h)
                                for g in khac:
                                    self.assertFalse(giao(h, g), (h, g))
                            # Giá trị một dòng (khối không ngắt).
                            gt = [h for h in the if h[0] == "the-gia-tri"]
                            self.assertEqual(len({round(h[2]) for h in gt}), 1, gt)
                finally:
                    page.close()

    def test_may_quay_cong_thuc_co_tai_lieu_giu_tron_khung_bieu_thuc(self):
        # Cảnh công thức có dòng tài liệu nhưng không thẻ, không tiêu đề: ở mọi t, khung biểu thức (kể cả nửa nét vẽ)
        # nằm trọn trong khung hình, không bị máy quay cắt mép.
        do = """() => {
          const d = window.THI_CANH['cong-thuc'].muc(window.DU_CANH).filter((m) => m.id === 'khung')[0].d;
          const p = [...document.querySelectorAll('#bang svg.ve path')].filter((el) => el.getAttribute('d') === d)[0];
          const k = document.getElementById('khung').getBoundingClientRect();
          const r = p.getBoundingClientRect();
          const nua = parseFloat(getComputedStyle(p).strokeWidth) / 2 * (r.width / p.getBBox().width);
          return [r.left - k.left - nua, r.top - k.top - nua, r.right - k.left + nua, r.bottom - k.top + nua];
        }"""
        ds = [("cong-thuc", "bieu-thuc: M × V = P × Y\ngiai-thich: M là lượng tiền, V là vòng quay\n"
                            f"tai-lieu: {chuoi(60)}\n"),
              ("cong-thuc", f"bieu-thuc: v = s / t\ngiai-thich: {chuoi(30)}\ngiai-thich: {chuoi(30)}\n"
                            f"tai-lieu: {chuoi(90)}\n")]
        for ten_kho in ("ngang", "doc"):
            k = kho.Kho(ten_kho, 720)
            for phong_cach in ("viet-tay", "cat-dan"):
                page = chup.trang_moi(self.browser, k)
                try:
                    for canh, html in self.trang(ds, ten_kho, phong_cach):
                        chup.mo_trang(page, html)
                        gh = page.evaluate("() => window.DU_CANH.thoiLuong")
                        n = int(gh / 0.1)
                        for i in range(n + 1):
                            t = round(gh * i / n, 3)
                            page.evaluate("(t) => window.datThoiDiem(t)", t)
                            h = page.evaluate(do)
                            with self.subTest(kho=ten_kho, phong_cach=phong_cach, so=canh.so, t=t):
                                self.assertGreaterEqual(h[0], 0, h)
                                self.assertGreaterEqual(h[1], 0, h)
                                self.assertLessEqual(h[2], k.rong, h)
                                self.assertLessEqual(h[3], k.cao, h)
                finally:
                    page.close()

    def test_may_quay_giu_tieu_de_the_tai_lieu_trong_khung_va_duoi_khung_loat(self):
        # Máy quay bật (mặc định), có khung loạt: ở mọi t của cảnh, tiêu đề (cả dải băng dính cat-dan), thẻ và dòng
        # tài liệu nằm trọn trong khung và không đè khung loạt, sau khi mục đó đã trượt/hiện xong (cat-dan trượt vào từ
        # mép trái là hiệu ứng vào cảnh, không phải máy quay).
        do = """(t) => {
          const xong = {};
          window.THI_CANH[window.DU_CANH.loai].muc(window.DU_CANH).forEach((m) => { xong[m.id] = m.batDau + m.thoiLuong; });
          const da = (id) => t >= (xong[id] === undefined ? 0 : xong[id]) + 0.05;
          const k = document.getElementById('khung').getBoundingClientRect();
          const hop = (r) => [r.left - k.left, r.top - k.top, r.right - k.left, r.bottom - k.top];
          const kq = [];
          document.querySelectorAll('#bang .chu').forEach((el) => {
            const id = el.dataset.id;
            if ((id !== 'tieu-de' && !id.startsWith('the-')) || !da(id)) { return; }
            if (id === 'the-nen') { kq.push([id].concat(hop(el.getBoundingClientRect()))); return; }
            const r = document.createRange(); r.selectNodeContents(el);
            [...r.getClientRects()].filter((c) => c.width > 0).forEach((c) => kq.push([id].concat(hop(c))));
          });
          document.querySelectorAll('#bang g.bang-dinh polygon, #bang .dong-nguon .dong').forEach((el) => {
            const ten = el.tagName === 'polygon' ? 'bang-dinh' : 'tai-lieu';
            if (da(ten === 'bang-dinh' ? 'tieu-de' : 'tai-lieu')) { kq.push([ten].concat(hop(el.getBoundingClientRect()))); }
          });
          const loat = [...document.querySelectorAll('#khung-loat span')].map((el) => ['loat'].concat(hop(el.getBoundingClientRect())));
          return [kq, loat];
        }"""
        the_tl = THE_TOI_DA + f"tai-lieu: {chuoi(60)}\n"
        ds = [("y-tung-y", NOI_DUNG["y-tung-y"] + the_tl), ("khai-niem", NOI_DUNG["khai-niem"] + the_tl),
              ("y-tung-y", NOI_DUNG["y-tung-y"] + "hinh: clock\n" + the_tl)]
        for ten_kho in ("ngang", "doc"):
            k = kho.Kho(ten_kho, 720)
            for phong_cach in ("viet-tay", "cat-dan"):
                page = chup.trang_moi(self.browser, k)
                try:
                    for canh, html in self.trang(ds, ten_kho, phong_cach, "loat: Kinh tế học nhập môn\n"):
                        chup.mo_trang(page, html)
                        gh = page.evaluate("() => window.DU_CANH.thoiLuong")
                        n = int(gh / 0.2)
                        for i in range(n + 1):
                            t = round(gh * i / n, 3)
                            page.evaluate("(t) => window.datThoiDiem(t)", t)
                            hop, loat = page.evaluate(do, t)
                            with self.subTest(kho=ten_kho, phong_cach=phong_cach, so=canh.so, t=t):
                                if t >= gh - 0.5:
                                    self.assertTrue(any(h[0] == "the-gia-tri" for h in hop), hop)
                                    self.assertTrue(any(h[0] == "tai-lieu" for h in hop), hop)
                                self.assertEqual(len(loat), 2)
                                for h in hop:
                                    self.assertGreaterEqual(h[1], -1, h)
                                    self.assertGreaterEqual(h[2], -1, h)
                                    self.assertLessEqual(h[3], k.rong + 1, h)
                                    self.assertLessEqual(h[4], k.cao + 1, h)
                                    for g in loat:
                                        self.assertFalse(giao(h, g), (h, g))
                finally:
                    page.close()

    def test_cong_thuc_M_x_V_kho_doc_mot_dong(self):
        for phong_cach in ("viet-tay", "cat-dan"):
            for cot in ("", "hinh: clock\n"):
                ds = [("cong-thuc", "bieu-thuc: M x V = P x Y\n" + cot), ("cong-thuc", "bieu-thuc: M x V | = P x Y\n" + cot)]
                page = chup.trang_moi(self.browser, kho.Kho("doc", 720))
                try:
                    for canh, html in self.trang(ds, "doc", phong_cach):
                        with self.subTest(phong_cach=phong_cach, cot=cot, so=canh.so):
                            self.assertEqual(chup.kiem_tran(page, html), [])
                            dong = [h for h in page.evaluate(HOP) if h[0] == "bieu-thuc"]
                            self.assertEqual(len({round(h[2]) for h in dong}), 1, dong)
                            self.assertEqual(page.evaluate(
                                "() => [...document.querySelectorAll('[data-id=bieu-thuc] span.phan')].map((s) => s.style.whiteSpace)"),
                                ["nowrap", "nowrap"])
                finally:
                    page.close()

    def test_phan_cong_thuc_rong_thu_chu_roi_bao_loi(self):
        lien = "Nghiêngnghiễmnhiên" * 4
        page = chup.trang_moi(self.browser, kho.Kho("doc", 720))
        try:
            # Đoạn liền vừa rộng hơn ô một chút: thu chữ, không ngắt, không lỗi.
            (_, html), = self.trang([("cong-thuc", f"bieu-thuc: a = {lien[:24]}\n")], "doc", "cat-dan")
            self.assertEqual(chup.kiem_tran(page, html), [])
            co = page.evaluate("() => parseFloat(document.querySelector('[data-id=bieu-thuc]').style.fontSize)")
            self.assertLess(co, 40)
            self.assertGreaterEqual(co, 28 - 1e-6)
            # Chữ dài có khoảng trắng, không toán tử (kiểu vi.11): về cỡ gốc và xuống dòng ở khoảng trắng như vi.11.
            (_, html), = self.trang([("cong-thuc", "bieu-thuc: " + chuoi(60) + "\n")], "doc", "cat-dan")
            self.assertEqual(chup.kiem_tran(page, html), [])
            self.assertEqual(page.evaluate("() => [document.querySelector('[data-id=bieu-thuc]').style.fontSize,"
                                           " document.querySelector('[data-id=bieu-thuc] span.phan').style.whiteSpace]"),
                             ["40px", "normal"])
            # Đoạn liền quá dài (kiem đã chặn; ở đây dựng thẳng): kiemTran báo đúng đoạn.
            (_, html), = self.trang([("cong-thuc", f"bieu-thuc: a = {lien[:40]}\n")], "doc", "cat-dan", kiem_truoc=False)
            self.assertIn("phan:" + lien[:40], chup.kiem_tran(page, html))
        finally:
            page.close()

    def test_cong_thuc_90_ky_tu_kieu_vi11_co_toan_tu_dung_sach(self):
        bt = "P = A / t = F · s / t = F · v = 1500 N · 12,5 m/s = 18750 W ≈ 18,75 kW (công suất kéo)"
        self.assertLessEqual(len(bt), 90)
        page = chup.trang_moi(self.browser, kho.Kho("ngang", 720))
        try:
            for cot in ("", "hinh: clock\n"):
                with self.subTest(cot=cot):
                    (_, html), = self.trang([("cong-thuc", f"bieu-thuc: {bt}\n{cot}giai-thich: A là công\n")],
                                            "ngang", "viet-tay")
                    self.assertEqual(chup.kiem_tran(page, html), [])
                    kieu = page.evaluate(
                        "() => [...document.querySelectorAll('[data-id=bieu-thuc] span.phan')].map((s) => s.style.whiteSpace)")
                    self.assertEqual(kieu, ["nowrap"] * 7)
        finally:
            page.close()

    def test_so_hang_lien_o_gioi_han_cung_chu_dai_kho_doc_khong_qua_kiem_roi_tran(self):
        # Hồi quy: số hạng liền đúng kiem.DOAN_LIEN (chỉ vừa khi thu tới 70 %) đi cùng một đoạn chữ dài phải xuống dòng
        # kiểu vi.11, khổ dọc không cột phụ. Qua kiem thì phải dựng sạch; không bao giờ qua kiem rồi tràn ở Chromium.
        for phong_cach in ("viet-tay", "cat-dan"):
            n = kiem.DOAN_LIEN[("doc", phong_cach)]
            bt = f"a = {('Nghiêngnghiễmnhiên' * 3)[:n]} = {chuoi(45)}"
            self.assertLessEqual(len(bt), kiem.bang_gioi_han("doc", phong_cach)[0][("cong-thuc", "bieu-thuc")])
            page = chup.trang_moi(self.browser, kho.Kho("doc", 720))
            try:
                with self.subTest(phong_cach=phong_cach):
                    (_, html), = self.trang([("cong-thuc", f"bieu-thuc: {bt}\n")], "doc", phong_cach)
                    tran, ra = ngoai_vung(page, html, "doc")
                    self.assertEqual(tran, [])
                    self.assertEqual(ra, [])
            finally:
                page.close()

    def test_noi_dung_o_gioi_han_co_the_va_tai_lieu_nam_gon(self):
        # Nội dung ở giới hạn áp dụng (bảng có thẻ), thẻ ở giới hạn, dòng tài liệu 90 ký tự: bốn loại × hai khổ × hai
        # phong cách, có và không có cột phụ.
        for ten_kho in ("ngang", "doc"):
            for phong_cach in ("viet-tay", "cat-dan"):
                L, H = kiem.bang_gioi_han(ten_kho, phong_cach, True)
                ds = them_the(canh_toi_da(L, H) + canh_toi_da(L, H, cot=True))
                self.assertEqual({loai for loai, _ in ds}, set(LOAI_CO_THE))
                page = chup.trang_moi(self.browser, kho.Kho(ten_kho, 720))
                try:
                    for canh, html in self.trang(ds, ten_kho, phong_cach):
                        with self.subTest(kho=ten_kho, phong_cach=phong_cach, so=canh.so, loai=canh.loai):
                            tran, ra = ngoai_vung(page, html, ten_kho)
                            self.assertEqual(tran, [])
                            self.assertEqual(ra, [])
                finally:
                    page.close()

    def test_loat_dung_yen_khi_may_quay_chay(self):
        ds = [("y-tung-y", NOI_DUNG["y-tung-y"])] * 8
        for phong_cach in ("viet-tay", "cat-dan"):
            canh, html = self.trang(ds, "ngang", phong_cach, "loat: Kinh tế học nhập môn\n")[2]
            page = chup.trang_moi(self.browser, kho.Kho("ngang", 720))
            try:
                chup.mo_trang(page, html)
                vi_tri = []
                bang = []
                cuoi = page.evaluate("() => window.THI_VIDEO.thoiDiemCuoi()")
                for t in (0.0, 5.0, cuoi):
                    page.evaluate("(t) => window.datThoiDiem(t)", t)
                    vi_tri.append(page.evaluate("""() => { const s = document.querySelector('#khung-loat .so');
                        const r = s.getBoundingClientRect(); return [s.textContent, r.left, r.top, r.right, r.bottom]; }"""))
                    bang.append(page.evaluate("() => document.getElementById('bang').style.transform"))
                self.assertEqual(vi_tri[0][0], "03/08")
                self.assertEqual(vi_tri[0], vi_tri[1])
                self.assertEqual(vi_tri[0], vi_tri[2])
                self.assertTrue(any(b not in ("", "none") for b in bang), bang)  # máy quay có chạy
                ten = page.evaluate("() => { const e = document.querySelector('#khung-loat .ten'); const r = e.getBoundingClientRect();"
                                    " return [getComputedStyle(e).textTransform, getComputedStyle(e).fontSize, r.left, r.bottom]; }")
                self.assertEqual(ten[:2], ["uppercase", "12px"])
                self.assertLess(ten[2], vi_tri[0][1])
                # Tiêu đề chừa dải khung loạt.
                td = page.evaluate("() => document.querySelector('.chu[data-id=\"tieu-de\"]').getBoundingClientRect().top")
                self.assertGreaterEqual(td, 40)
                self.assertLessEqual(max(ten[3], vi_tri[0][4]), 40)
            finally:
                page.close()

    def test_khong_loat_khong_co_khung_loat(self):
        (_, html), = self.trang([("y-tung-y", NOI_DUNG["y-tung-y"])], "ngang", "cat-dan")
        page = chup.trang_moi(self.browser, kho.Kho("ngang", 720))
        try:
            chup.mo_trang(page, html)
            page.evaluate("() => window.datThoiDiem(2)")
            self.assertEqual(page.evaluate("() => document.querySelectorAll('#khung-loat').length"), 0)
        finally:
            page.close()

    def test_nguon_anh_xep_tren_dong_tai_lieu(self):
        for ten_kho in ("ngang", "doc"):
            for phong_cach in ("viet-tay", "cat-dan"):
                ds = [("khai-niem", NOI_DUNG["khai-niem"] + f"anh: con-lac.png\nnguon: {NGUON_ANH}\n"
                       f"tai-lieu: Giáo trình Kinh tế vĩ mô · TS. Hà Thúc Huân · NXB Giáo dục {chuoi(20)}\n"),
                      ("y-tung-y", NOI_DUNG["y-tung-y"] + "tai-lieu: Sách giáo khoa Kinh tế và Pháp luật 10\n")]
                page = chup.trang_moi(self.browser, kho.Kho(ten_kho, 720))
                try:
                    for canh, html in self.trang(ds, ten_kho, phong_cach):
                        with self.subTest(kho=ten_kho, phong_cach=phong_cach, so=canh.so):
                            self.assertEqual(chup.kiem_tran(page, html), [])
                            hop = page.evaluate(HOP)
                            dong = [h for h in hop if h[0].startswith("dong-")]
                            chu = page.evaluate("() => [...document.querySelectorAll('.dong-nguon .dong')].map((d) => d.textContent)")
                            k = kho.Kho(ten_kho, 720)
                            if canh.so == 1:
                                self.assertEqual(chu[0], NGUON_ANH)
                                self.assertTrue(chu[1].startswith("Nguồn: Giáo trình"))
                                self.assertLessEqual(dong[0][4], dong[1][2] + 0.5)  # nguồn ảnh ở trên, không chồng
                                self.assertEqual(page.evaluate("() => getComputedStyle(document.querySelector('.anh .nguon')).display"), "none")
                            else:
                                self.assertEqual(chu, ["Nguồn: Sách giáo khoa Kinh tế và Pháp luật 10"])
                            for d in dong:
                                self.assertLessEqual(d[4], k.day + 0.5)
                                self.assertLessEqual(d[3], k.rong + 0.5)
                                for g in hop:
                                    if not g[0].startswith("dong-"):
                                        self.assertFalse(giao(d, g), (d, g))
                finally:
                    page.close()


@unittest.skipUnless(CO_CHROMIUM, "máy không có Chromium hoặc playwright")
class TheXemTruocTest(unittest.TestCase):
    def test_so_hang_lien_qua_dai_la_loi_canh_truoc_khi_dung(self):
        # Số hạng liền 30 ký tự không có toán tử ở khổ dọc cắt dán (tối đa 28): lỗi `canh` ngay ở bước kiểm.
        with tempfile.TemporaryDirectory() as tmp:
            phan = ("Nghiêngnghiễmnhiên" * 2)[:30]
            thu_muc = thu_muc_bai(Path(tmp), video_md([("tieu-de", "chu: A\n"), ("cong-thuc", f"bieu-thuc: {phan}\n")],
                                                      meta("doc", "cat-dan")))
            data = chay(thu_muc, "--plan-only")
            self.assertFalse(data["ready"])
            self.assertEqual(data["error"]["step"], "canh")
            self.assertTrue(data["error"]["message"].startswith(f'Cảnh 2: phần công thức "{phan}" quá dài cho khổ này'),
                            data["error"]["message"])
            self.assertIn("` | `", data["error"]["fix"])


if __name__ == "__main__":
    unittest.main()

"""Test dựng trang và chụp khung. Phần Chromium tự bỏ qua nếu máy thiếu Chromium hoặc playwright."""

import contextlib
import importlib.util
import io
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

TOOLS_VI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_VI))

from video_ma_parts import chup, lich, parse, phong, trang  # noqa: E402

META = "tieu-de: T\nmon: Toán\nlop: 8\n"


def co_chromium() -> bool:
    root = os.environ.get("LOCALAPPDATA")
    if not root or importlib.util.find_spec("playwright") is None:
        return False
    base = Path(root) / "ms-playwright"
    return base.is_dir() and (any(base.glob("chromium-*")) or any(base.glob("chromium_headless_shell-*")))


NEED_CHROMIUM = "máy không có Chromium hoặc playwright"

_CUM_TU = "Nhờ ướt nhẫm quyết định "


def vi_text(n: int) -> str:
    """Chuỗi tiếng Việt có dấu, đủ khoảng trắng, đúng `n` ký tự (không phải một từ dài liền)."""
    s = (_CUM_TU * (n // len(_CUM_TU) + 2))[:n]
    return s[:-1] + "x" if s.endswith(" ") else s


# Biểu thức ở giới hạn 90 ký tự: mỗi phần là một khối không ngắt dòng (spec Q14), nên chuỗi dài chia bốn phần bằng
# ` | ` (4 × 21 ký tự + 3 khoảng trắng ngăn = 87); một phần dài 90 ký tự là lỗi "phần công thức quá dài".
BIEU_THUC_TOI_DA = " | ".join(vi_text(21) for _ in range(4))


def du_cua(noi_dung: str, giay: float = 6.0, loi: str = "Xin chào các em. Hôm nay học bài mới. Cảm ơn các em."):
    text = f"---\n{META}---\n\n## Cảnh 1\n{noi_dung}loi: {loi}\n"
    canh = parse.parse(text).canh[0]
    giong = lich.GiongInfo(mp3=None, giay=giay, moc_cau=[0.0, 2.0, 4.0], uoc_luong=False, nguon="may")
    plan, _ = lich.dung_lich([canh], [giong])
    return lich.du_lieu_canh(canh, plan[0]), plan[0]


class PageBuildTest(unittest.TestCase):
    def test_page_is_self_contained(self):
        du, _ = du_cua("loai: tieu-de\nchu: Xin chào\n")
        html = trang.dung_trang(du)
        self.assertNotIn("http://", html.replace("http://www.w3.org/2000/svg", ""))
        self.assertNotIn("https://", html)
        self.assertIn("Itim", html)
        self.assertIn("THI_CANH['tieu-de']", html)
        self.assertNotIn("THI_CANH['y-tung-y']", html)
        self.assertIn("khoiDong", html)

    def test_trang_khong_chua_ma_chay_duoc(self):
        du, _ = du_cua('loai: tieu-de\nchu: a < b </script><img src=x onerror=alert(1)> & "c"\n')
        html = trang.dung_trang(du)
        self.assertEqual(html.count("</script>"), html.count("<script>"))
        self.assertNotIn("<img src=x", html)
        self.assertIn("\\u003c/script>", html)

    def test_experiment_page_embeds_khung_and_model(self):
        from thi_nghiem_parts import thu_vien

        model = thu_vien.load("li-con-lac-don", Path("."))
        text = f"---\n{META}---\n\n## Cảnh 1\nloai: thi-nghiem\nmau: li-con-lac-don\nloi: Ok.\n"
        canh = parse.parse(text).canh[0]
        giong = lich.GiongInfo(mp3=None, giay=4.0, moc_cau=[0.0], uoc_luong=False, nguon="may")
        plan, _ = lich.dung_lich([canh], [giong])
        html = trang.dung_trang(lich.du_lieu_canh(canh, plan[0], model), model)
        self.assertIn("THI_NGHIEM_KHUNG", html)
        self.assertIn("THI_NGHIEM_MO_HINH", html)
        self.assertLess(html.index("THI_NGHIEM_KHUNG = "), html.index("THI_NGHIEM_MO_HINH = "))


@unittest.skipUnless(co_chromium(), NEED_CHROMIUM)
class ChromiumTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cm = chup.trinh_duyet()
        cls.browser = cls.cm.__enter__()
        cls.page = chup.trang_moi(cls.browser)

    @classmethod
    def tearDownClass(cls):
        cls.cm.__exit__(None, None, None)

    def test_normal_scene_does_not_overflow_and_ink_grows(self):
        du, cl = du_cua("loai: y-tung-y\ntieu-de: Ba bước\ny: Một\ny: Hai\ny: Ba\n")
        html = trang.dung_trang(du)
        self.assertEqual(chup.kiem_tran(self.page, html), [])
        with tempfile.TemporaryDirectory() as tmp:
            n = chup.chup_canh(self.page, html, 6, lich.FPS, Path(tmp), 0)
            self.assertEqual(n, 6)
            frames = sorted(Path(tmp).glob("f*.jpg"))
            self.assertEqual([f.name for f in frames], [f"f{i:06d}.jpg" for i in range(6)])
            first = frames[0].read_bytes()
            self.assertEqual(first[:3], b"\xff\xd8\xff")  # khung tạm là JPEG (chup.DUOI_KHUNG)
            final = Path(tmp) / "cuoi.png"
            chup.chup_cuoi(self.page, html, final)
            self.assertGreater(final.stat().st_size, frames[0].stat().st_size)

    def test_itim_renders_every_vietnamese_letter_without_a_fallback_glyph(self):
        html = f"<!doctype html><html><head><style>{phong.font_css()}</style></head><body></body></html>"
        self.page.set_content(html)
        chars = list(phong.CHU_VIET)
        text = "".join(chars)
        loaded = self.page.evaluate(
            "(text) => document.fonts.load(\"40px 'Itim'\", text).then((faces) => faces.length)", text,
        )
        self.assertGreaterEqual(loaded, 1)
        diffs = self.page.evaluate(
            """(chars) => {
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                return chars.map((c) => {
                    ctx.font = "40px 'Itim', monospace";
                    const w1 = ctx.measureText(c).width;
                    ctx.font = "40px 'Itim', serif";
                    const w2 = ctx.measureText(c).width;
                    return Math.abs(w1 - w2);
                });
            }""",
            chars,
        )
        for d, c in zip(diffs, chars):
            self.assertLess(d, 0.01, c)

    def test_first_frame_of_a_freshly_opened_page_already_has_itim_loaded(self):
        du, _ = du_cua("loai: tieu-de\nchu: " + phong.CHU_VIET[:20] + "\n")
        html = trang.dung_trang(du)
        page = chup.trang_moi(self.browser)
        try:
            chup.mo_trang(page, html)
            chars = list(phong.CHU_VIET)
            diffs = page.evaluate(
                """(chars) => {
                    const canvas = document.createElement('canvas');
                    const ctx = canvas.getContext('2d');
                    return chars.map((c) => {
                        ctx.font = "40px 'Itim', monospace";
                        const w1 = ctx.measureText(c).width;
                        ctx.font = "40px 'Itim', serif";
                        const w2 = ctx.measureText(c).width;
                        return Math.abs(w1 - w2);
                    });
                }""",
                chars,
            )
            for d, c in zip(diffs, chars):
                self.assertLess(d, 0.01, c)
        finally:
            page.close()

    def test_scene_page_computed_font_family_starts_with_itim(self):
        du, _ = du_cua("loai: tieu-de\nchu: Xin chào\n")
        html = trang.dung_trang(du)
        chup.mo_trang(self.page, html)
        font_family = self.page.evaluate("() => getComputedStyle(document.querySelector('.chu')).fontFamily")
        self.assertTrue(font_family.startswith("Itim"), font_family)

    def test_overflowing_text_is_reported_by_item_id(self):
        du, _ = du_cua("loai: tieu-de\nchu: " + "A" * 80 + "\n")
        self.assertIn("chu", chup.kiem_tran(self.page, trang.dung_trang(du)))

    def khoang_gach(self, html: str, id_chu: str, y_gach: float) -> float:
        chup.mo_trang(self.page, html)
        self.page.evaluate("window.datThoiDiem(1e6)")
        day = self.page.evaluate(f"document.querySelector('[data-id=\"{id_chu}\"] .trong').getBoundingClientRect().bottom")
        return y_gach - day

    def test_underline_sits_right_under_a_one_line_heading(self):
        for noi_dung, id_chu, y_gach in (("loai: y-tung-y\ntieu-de: Ba bước\ny: Một\n", "tieu-de", 160),
                                         ("loai: khai-niem\nthuat-ngu: Chu kì\ndinh-nghia: Thời gian.\n", "thuat-ngu", 335),
                                         ("loai: tieu-de\nchu: Con lắc đơn\nphu: Vật lí 11\n", "chu", 400)):
            du, _ = du_cua(noi_dung)
            self.assertLess(abs(self.khoang_gach(trang.dung_trang(du), id_chu, y_gach)), 30, id_chu)

    def test_two_line_term_and_heading_fit_their_boxes(self):
        du, _ = du_cua("loai: khai-niem\nthuat-ngu: Chu kì dao động điều hoà của con lắc đơn khi góc lệch nhỏ\n"
                       "dinh-nghia: Thời gian.\n")
        self.assertEqual(chup.kiem_tran(self.page, trang.dung_trang(du)), [])
        du, _ = du_cua("loai: y-tung-y\ntieu-de: Chu kì của con lắc đơn phụ thuộc vào những yếu tố nào và "
                       "không phụ thuộc vào yếu tố nào\ny: Một\n")
        self.assertEqual(chup.kiem_tran(self.page, trang.dung_trang(du)), [])

    def test_list_scenes_fit_their_boxes_at_the_new_limits(self):
        diem = "\n".join(f"diem: {k}, {k * k % 7}" for k in range(12))
        casos = {
            "y-tung-y": "loai: y-tung-y\ntieu-de: Sáu ý\n" + "".join(f"y: {vi_text(60)}\n" for _ in range(6)),
            "cong-thuc": ("loai: cong-thuc\nbieu-thuc: " + BIEU_THUC_TOI_DA + "\n"
                          + "".join(f"giai-thich: {vi_text(60)}\n" for _ in range(4))),
            "quy-trinh": "loai: quy-trinh\ntieu-de: Năm bước\n" + "".join(f"buoc: {vi_text(50)}\n" for _ in range(5)),
            "so-sanh": ("loai: so-sanh\ntieu-de: So sánh\n" + f"trai: {vi_text(24)}\nphai: {vi_text(24)}\n"
                        + "".join(f"y-trai: {vi_text(60)}\n" for _ in range(4))
                        + "".join(f"y-phai: {vi_text(60)}\n" for _ in range(4))),
            "do-thi": (f"loai: do-thi\ntieu-de: Đồ thị\ntruc-ngang: {vi_text(40)}\ntruc-doc: {vi_text(40)}\n"
                       + diem + "\n"),
            "khai-niem": f"loai: khai-niem\nthuat-ngu: {vi_text(60)}\ndinh-nghia: {vi_text(220)}\n",
            "tieu-de": f"loai: tieu-de\nchu: {vi_text(90)}\nphu: {vi_text(90)}\n",
        }
        for loai, noi_dung in casos.items():
            with self.subTest(loai=loai):
                du, _ = du_cua(noi_dung)
                html = trang.dung_trang(du)
                self.assertEqual(chup.kiem_tran(self.page, html), [])

    def test_hostile_text_renders_as_text(self):
        du, _ = du_cua('loai: tieu-de\nchu: a < b </script><img src=x onerror=alert(1)> & "c"\n')
        html = trang.dung_trang(du)
        chup.mo_trang(self.page, html)
        self.page.evaluate("window.datThoiDiem(1e6)")
        self.assertEqual(self.page.evaluate("document.querySelectorAll('#khung img').length"), 0)
        texto = self.page.evaluate("document.querySelector('[data-id=chu]').textContent")
        self.assertIn("a < b </script><img src=x onerror=alert(1)> & \"c\"", re.sub(r"\s+", " ", texto))

    def test_frames_are_repeatable(self):
        du, _ = du_cua("loai: khai-niem\nthuat-ngu: Chu kì\ndinh-nghia: Thời gian một dao động.\n")
        html = trang.dung_trang(du)
        with tempfile.TemporaryDirectory() as tmp:
            chup.chup_canh(self.page, html, 4, lich.FPS, Path(tmp), 0)
            chup.chup_canh(self.page, html, 4, lich.FPS, Path(tmp), 10)
            for i in range(4):
                self.assertEqual((Path(tmp) / f"f{i:06d}.jpg").read_bytes(), (Path(tmp) / f"f{10 + i:06d}.jpg").read_bytes())

    def test_experiment_scene_draws_the_model(self):
        from thi_nghiem_parts import thu_vien

        model = thu_vien.load("li-con-lac-don", Path("."))
        text = (f"---\n{META}---\n\n## Cảnh 1\nloai: thi-nghiem\nmau: li-con-lac-don\ntham-so: 0 chieu-dai 0.4\n"
                "tham-so: 5 chieu-dai 1.6\ndo: chu-ki\nloi: Ok.\n")
        canh = parse.parse(text).canh[0]
        giong = lich.GiongInfo(mp3=None, giay=6.0, moc_cau=[0.0], uoc_luong=False, nguon="may")
        plan, _ = lich.dung_lich([canh], [giong])
        html = trang.dung_trang(lich.du_lieu_canh(canh, plan[0], model), model)
        self.assertEqual(chup.kiem_tran(self.page, html), [])
        self.page.evaluate("window.datThoiDiem(3)")
        dong = self.page.evaluate("document.querySelector('[data-id=do-0]').textContent")
        self.assertRegex(dong, r"Chu kì T = \d,\d{3} s")
        self.page.evaluate("window.datThoiDiem(1e6)")
        cuoi = self.page.evaluate("document.querySelector('[data-id=do-0]').textContent")
        self.assertIn("2,539", cuoi)

    def test_experiment_canvas_writes_vietnamese_in_itim(self):
        # "Số dao động: 3" vẽ trên canvas của mô hình cũng phải là Itim, không phải Segoe UI.
        from thi_nghiem_parts import thu_vien

        for mau, ts in (("li-con-lac-don", "chieu-dai 0.4"), ("li-nem-xien", None)):
            with self.subTest(mau=mau):
                model = thu_vien.load(mau, Path("."))
                them = f"tham-so: 0 {ts}\n" if ts else ""
                text = f"---\n{META}---\n\n## Cảnh 1\nloai: thi-nghiem\nmau: {mau}\n{them}loi: Ok.\n"
                canh = parse.parse(text).canh[0]
                giong = lich.GiongInfo(mp3=None, giay=4.0, moc_cau=[0.0], uoc_luong=False, nguon="may")
                plan, _ = lich.dung_lich([canh], [giong])
                chup.mo_trang(self.page, trang.dung_trang(lich.du_lieu_canh(canh, plan[0], model), model))
                self.page.evaluate("window.datThoiDiem(3)")
                phong = self.page.evaluate("document.getElementById('ban-ve').getContext('2d').font")
                self.assertIn("Itim", phong)
                self.assertNotIn("Segoe", phong)

    def test_preview_shows_the_scene_at_its_final_parameter_value(self):
        from thi_nghiem_parts import thu_vien

        model = thu_vien.load("li-con-lac-don", Path("."))
        text = (f"---\n{META}---\n\n## Cảnh 1\nloai: thi-nghiem\nmau: li-con-lac-don\ntham-so: 0 chieu-dai 0.4\n"
                "tham-so: 5 chieu-dai 1.6\ndo: chu-ki\nloi: Ok.\n")
        canh = parse.parse(text).canh[0]
        giong = lich.GiongInfo(mp3=None, giay=6.0, moc_cau=[0.0], uoc_luong=False, nguon="may")
        plan, _ = lich.dung_lich([canh], [giong])
        html = trang.dung_trang(lich.du_lieu_canh(canh, plan[0], model), model)
        chup.mo_trang(self.page, html)
        self.page.evaluate("window.datThoiDiem(window.THI_VIDEO.thoiDiemCuoi())")
        ts0 = self.page.evaluate("document.querySelector('[data-id=ts-0]').textContent")
        self.assertIn("1,60 m", ts0)


def png(rong: int, cao: int) -> bytes:
    """PNG sọc ngang tự dựng bằng thư viện chuẩn (để thấy ảnh chuyển động)."""
    import struct
    import zlib

    hang = [b"\x00" + (bytes((200, 90, 60)) if (y // 40) % 2 else bytes((60, 120, 200))) * rong for y in range(cao)]
    def khoi(loai, du):
        return struct.pack(">I", len(du)) + loai + du + struct.pack(">I", zlib.crc32(loai + du) & 0xFFFFFFFF)
    return (b"\x89PNG\r\n\x1a\n" + khoi(b"IHDR", struct.pack(">IIBBBBB", rong, cao, 8, 2, 0, 0, 0))
            + khoi(b"IDAT", zlib.compress(b"".join(hang), 9)) + khoi(b"IEND", b""))


def anh_gia(rong: int, cao: int) -> dict:
    import base64
    return {"dataUrl": "data:image/png;base64," + base64.b64encode(png(rong, cao)).decode("ascii"),
            "nguon": "Ảnh: Tác giả thử · CC BY 4.0 · Wikimedia", "rong": rong, "cao": cao}


def du_hinh(noi_dung: str, tai_nguyen: dict, so: int = 1, giay: float = 6.0,
            loi: str = "Xin chào các em. Hôm nay học bài mới. Cảm ơn các em."):
    truoc = "".join(f"## Cảnh {k}\nloai: tieu-de\nchu: Mở đầu\nloi: Chào.\n\n" for k in range(1, so))
    text = f"---\n{META}---\n\n{truoc}## Cảnh {so}\n{noi_dung}loi: {loi}\n"
    canh = parse.parse(text).canh[so - 1]
    giong = lich.GiongInfo(mp3=None, giay=giay, moc_cau=[0.0, 2.0, 4.0], uoc_luong=False, nguon="may")
    plan, _ = lich.dung_lich([canh], [giong])
    return lich.du_lieu_canh(canh, plan[0], None, {**tai_nguyen, "meta": {}})


@unittest.skipUnless(co_chromium(), NEED_CHROMIUM)
class PictureMotionChromiumTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from video_ma_parts import hinh
        cls.hinh = hinh.doc("flask")
        cls.cm = chup.trinh_duyet()
        cls.browser = cls.cm.__enter__()
        cls.page = chup.trang_moi(cls.browser)

    @classmethod
    def tearDownClass(cls):
        cls.cm.__exit__(None, None, None)

    def muc(self, id_muc: str) -> dict:
        return self.page.evaluate(
            "(id) => THI_CANH[DU_CANH.loai].muc(DU_CANH).filter((m) => m.id === id)[0]", id_muc)

    def test_picture_column_scenes_fit_at_the_text_limits(self):
        casos = {
            "khai-niem": f"loai: khai-niem\nthuat-ngu: {vi_text(60)}\ndinh-nghia: {vi_text(220)}\n",
            "y-tung-y": f"loai: y-tung-y\ntieu-de: {vi_text(90)}\n" + "".join(f"y: {vi_text(60)}\n" for _ in range(6)),
            "cong-thuc": ("loai: cong-thuc\nbieu-thuc: " + BIEU_THUC_TOI_DA + "\n"
                          + "".join(f"giai-thich: {vi_text(60)}\n" for _ in range(4))),
            "tieu-de": f"loai: tieu-de\nchu: {vi_text(90)}\nphu: {vi_text(90)}\n",
        }
        for loai, noi_dung in casos.items():
            for kieu, tai in (("hinh", {"hinh": self.hinh}), ("anh", {"anh": anh_gia(600, 1200)})):
                with self.subTest(loai=loai, kieu=kieu):
                    du = du_hinh(noi_dung + ("hinh: flask\n" if kieu == "hinh" else "anh: a.png\n"), tai)
                    self.assertEqual(chup.kiem_tran(self.page, trang.dung_trang(du)), [])

    def test_minh_hoa_three_pictures_with_long_labels_fit(self):
        nhan = vi_text(30)
        noi_dung = "loai: minh-hoa\ntieu-de: " + vi_text(90) + "\n" + "".join(f"hinh: flask | {nhan}\n" for _ in range(3))
        du = du_hinh(noi_dung, {"hinhs": [{**self.hinh, "nhan": nhan} for _ in range(3)]})
        self.assertEqual(chup.kiem_tran(self.page, trang.dung_trang(du)), [])

    def test_photo_scene_keeps_the_photo_ratio_inside_its_area(self):
        for rong, cao in ((600, 1200), (2000, 800)):
            with self.subTest(rong=rong, cao=cao):
                du = du_hinh(f"loai: anh\nanh: a.png\nchu-thich: {vi_text(90)}\nnguon: Tôi\n", {"anh": anh_gia(rong, cao)})
                html = trang.dung_trang(du)
                self.assertEqual(chup.kiem_tran(self.page, html), [])
                m = self.muc("anh")
                self.page.evaluate("(t) => window.datThoiDiem(t)", m["batDau"])
                r = self.page.evaluate("""() => { const i = document.querySelector('.anh img');
                    const b = i.getBoundingClientRect();
                    return {x: b.left, y: b.top, w: b.width, h: b.height, nw: i.naturalWidth, nh: i.naturalHeight}; }""")
                self.assertEqual((r["nw"], r["nh"]), (rong, cao))
                self.assertGreaterEqual(r["x"], 80 - 0.5)
                self.assertGreaterEqual(r["y"], 70 - 0.5)
                self.assertLessEqual(r["x"] + r["w"], 1200 + 0.5)
                self.assertLessEqual(r["y"] + r["h"], 560 + 0.5)
                self.assertAlmostEqual(r["w"] / r["h"], rong / cao, delta=0.01 * rong / cao)
                nguon = self.page.evaluate("document.querySelector('.anh .nguon').textContent")
                self.assertIn("Tác giả thử", nguon)
                # Ken Burns: so hai thời điểm sau khi ảnh đã hiện hẳn, chỉ chụp ô ảnh (không tính máy quay, tay, chú thích).
                du["co"].update(mayQuay=False, banTay=False)
                chup.mo_trang(self.page, trang.dung_trang(du))
                o_anh = self.page.locator(".anh .cua-anh")
                bien_doi = "getComputedStyle(document.querySelector('.anh img')).transform"
                self.page.evaluate("(t) => window.datThoiDiem(t)", m["batDau"] + 0.5)
                self.assertEqual(self.page.evaluate("getComputedStyle(document.querySelector('.anh')).opacity"), "1")
                dau, bd_dau = o_anh.screenshot(type="png"), self.page.evaluate(bien_doi)
                self.page.evaluate("(t) => window.datThoiDiem(t)", du["thoiLuong"] - 0.2)
                cuoi, bd_cuoi = o_anh.screenshot(type="png"), self.page.evaluate(bien_doi)
                self.assertNotEqual(bd_dau, bd_cuoi, "ảnh phải phóng/lướt (Ken Burns)")
                self.assertNotEqual(dau, cuoi, "ảnh phải chuyển động (Ken Burns)")

    def test_source_line_of_a_column_photo_sits_under_the_frame_on_one_line(self):
        # Ô cột hẹp (ảnh dọc rộng ~240 px): dòng nguồn trong góc ảnh bị ngắt hai dòng và đè lên ảnh.
        for nguon, mot_dong in (("Ảnh: PPT Master bản Việt · CC0 1.0 · Tự vẽ", True),
                                ("Ảnh: Nguyễn Thị Thử Nghiệm · CC BY-SA 4.0 · Wikimedia Commons", False)):
            for rong, cao in ((200, 320), (480, 300)):
                with self.subTest(nguon=nguon, rong=rong, cao=cao):
                    du = du_hinh("loai: y-tung-y\ntieu-de: Quả nặng\n" + "".join(f"y: {vi_text(60)}\n" for _ in range(6))
                                 + "anh: a.png\n", {"anh": {**anh_gia(rong, cao), "nguon": nguon}})
                    du["co"].update(mayQuay=False, banTay=False)
                    chup.mo_trang(self.page, trang.dung_trang(du))
                    self.page.evaluate("window.datThoiDiem(window.THI_VIDEO.thoiDiemCuoi())")
                    r = self.page.evaluate("""() => {
                        const hop = (s) => { const b = document.querySelector(s).getBoundingClientRect();
                            return {l: b.left, t: b.top, r: b.right, b: b.bottom, h: b.height}; };
                        const n = document.querySelector('.anh .nguon');
                        return {anh: hop('.anh .cua-anh'), nguon: hop('.anh .nguon'),
                                dong: parseFloat(getComputedStyle(n).lineHeight)}; }""")
                    self.assertGreaterEqual(r["nguon"]["t"], r["anh"]["b"], "dòng nguồn không được đè lên ảnh")
                    self.assertGreaterEqual(r["nguon"]["l"], 860, "không lấn sang cột chữ")
                    self.assertLessEqual(r["nguon"]["r"], 1280)
                    self.assertLessEqual(r["nguon"]["b"], 620 + 0.5, "trên vùng phụ đề")
                    if mot_dong:
                        self.assertLess(r["nguon"]["h"], 1.6 * r["dong"], "tín dụng ngắn phải nằm một dòng")

    def test_photo_source_never_covers_text_and_stays_above_the_subtitles(self):
        # Mọi bố cục có ảnh × ảnh dọc, vuông, ngang × dòng nguồn dài nhất thường gặp × chữ dài tối đa.
        nguon = "Ảnh: Nguyễn Thị Thử Nghiệm · CC BY-SA 4.0 · Wikimedia Commons"
        self.assertEqual(len(nguon), 61)
        bo_cuc = {
            "anh": f"loai: anh\nchu-thich: {vi_text(90)}\n",
            "khai-niem": f"loai: khai-niem\nthuat-ngu: {vi_text(60)}\ndinh-nghia: {vi_text(220)}\n",
            "y-tung-y": f"loai: y-tung-y\ntieu-de: {vi_text(90)}\n" + "".join(f"y: {vi_text(60)}\n" for _ in range(6)),
            "cong-thuc": ("loai: cong-thuc\nbieu-thuc: " + BIEU_THUC_TOI_DA + "\n"
                          + "".join(f"giai-thich: {vi_text(60)}\n" for _ in range(4))),
            "tieu-de": f"loai: tieu-de\nchu: {vi_text(90)}\nphu: {vi_text(90)}\n",
        }
        for loai, noi_dung in bo_cuc.items():
            for rong, cao in ((600, 1200), (1000, 1000), (2000, 800)):
                with self.subTest(loai=loai, rong=rong, cao=cao):
                    du = du_hinh(noi_dung + "anh: a.png\n", {"anh": {**anh_gia(rong, cao), "nguon": nguon}})
                    du["co"].update(mayQuay=False, banTay=False)
                    html = trang.dung_trang(du)
                    self.assertEqual(chup.kiem_tran(self.page, html), [])
                    chup.mo_trang(self.page, html)
                    self.page.evaluate("window.datThoiDiem(window.THI_VIDEO.thoiDiemCuoi())")
                    r = self.page.evaluate("""() => {
                        const hop = (e) => { const b = e.getBoundingClientRect();
                            return {l: b.left, t: b.top, r: b.right, b: b.bottom}; };
                        return {nguon: hop(document.querySelector('.anh .nguon')),
                                chu: Array.from(document.querySelectorAll('.chu')).map((e) => ({id: e.dataset.id, ...hop(e)}))}; }""")
                    n = r["nguon"]
                    self.assertGreaterEqual(n["l"], 0)
                    self.assertGreaterEqual(n["t"], 0)
                    self.assertLessEqual(n["r"], 1280)
                    self.assertLessEqual(n["b"], 620, "dòng nguồn phải nằm trên vùng phụ đề")
                    for c in r["chu"]:
                        giao = n["l"] < c["r"] and c["l"] < n["r"] and n["t"] < c["b"] and c["t"] < n["b"]
                        self.assertFalse(giao, f"dòng nguồn đè lên ô chữ `{c['id']}`: {n} / {c}")

    def test_rotated_phone_photo_gets_a_frame_of_its_displayed_shape(self):
        # JPEG 400×300 điểm ảnh kèm Exif Orientation = 6: Chromium hiện ảnh dọc 300×400, khung phải dọc theo.
        import base64
        import struct

        from video_ma_parts import anh

        self.page.set_content("<!doctype html><html><body></body></html>")
        url = self.page.evaluate("""() => { const c = document.createElement('canvas'); c.width = 400; c.height = 300;
            const g = c.getContext('2d'); g.fillStyle = '#c85a3c'; g.fillRect(0, 0, 400, 300);
            g.fillStyle = '#3c78c8'; g.fillRect(0, 0, 400, 100); return c.toDataURL('image/jpeg', 0.9); }""")
        goc = base64.b64decode(url.split(",", 1)[1])
        tiff = (b"II" + struct.pack("<HI", 42, 8) + struct.pack("<H", 1)
                + struct.pack("<HHIHH", 0x0112, 3, 1, 6, 0) + struct.pack("<I", 0))
        exif = b"\xff\xe1" + struct.pack(">H", len(tiff) + 8) + b"Exif\x00\x00" + tiff
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "anh").mkdir()
            (Path(tmp) / "anh" / "x.jpg").write_bytes(goc[:2] + exif + goc[2:])
            info = anh.doc(Path(tmp), "x.jpg", "Ảnh tự chụp")
        self.assertEqual((info["rong"], info["cao"]), (300, 400))
        du = du_hinh(f"loai: anh\nanh: x.jpg\nchu-thich: {vi_text(40)}\nnguon: Tôi\n", {"anh": info})
        du["co"].update(mayQuay=False, banTay=False)
        chup.mo_trang(self.page, trang.dung_trang(du))
        self.page.evaluate("window.datThoiDiem(window.THI_VIDEO.thoiDiemCuoi())")
        r = self.page.evaluate("""() => { const i = document.querySelector('.anh img');
            const b = document.querySelector('.anh').getBoundingClientRect();
            return {nw: i.naturalWidth, nh: i.naturalHeight, w: b.width, h: b.height}; }""")
        self.assertEqual((r["nw"], r["nh"]), (300, 400), "Chromium hiện ảnh theo thẻ Orientation")
        self.assertAlmostEqual(r["w"] / r["h"], r["nw"] / r["nh"], delta=0.01)

    def test_kiem_tran_reports_a_source_line_below_the_subtitle_line(self):
        du = du_hinh("loai: y-tung-y\ntieu-de: T\ny: Một\nanh: a.png\n",
                     {"anh": {**anh_gia(600, 1200), "nguon": "Ảnh: " + vi_text(400)}})
        self.assertIn("nguon", chup.kiem_tran(self.page, trang.dung_trang(du)))

    def test_icon_is_drawn_stroke_by_stroke(self):
        du = du_hinh("loai: y-tung-y\ntieu-de: Dụng cụ\nhinh: flask\ny: Bình tam giác\n", {"hinh": self.hinh})
        chup.mo_trang(self.page, trang.dung_trang(du))
        m = self.muc("hinh")
        self.assertGreaterEqual(m["thoiLuong"], 1.2)
        trang_thai = """() => Array.from(document.querySelectorAll('g.hinh > *')).map((e) => {
            const cs = getComputedStyle(e);
            return {o: parseFloat(cs.opacity), d: parseFloat(cs.strokeDashoffset)}; })"""
        self.assertGreaterEqual(len(self.hinh["phanTu"]), 3)
        self.page.evaluate("(t) => window.datThoiDiem(t)", m["batDau"] + 0.5 * m["thoiLuong"])
        giua = self.page.evaluate(trang_thai)
        xong = [e for e in giua if e["o"] == 1 and abs(e["d"]) < 1e-6]
        chua = [e for e in giua if e["o"] == 0 or abs(e["d"] - 1) < 1e-6]
        dang = [e for e in giua if e not in xong and e not in chua]
        self.assertGreaterEqual(len(xong), 1, giua)
        self.assertGreaterEqual(len(chua), 1, giua)
        self.assertLessEqual(len(dang), 1, giua)
        self.page.evaluate("(t) => window.datThoiDiem(t)", du["thoiLuong"] - 0.2)
        cuoi = self.page.evaluate(trang_thai)
        self.assertTrue(all(e["o"] == 1 and abs(e["d"]) < 1e-6 for e in cuoi), cuoi)

    def test_pen_hand_sits_on_the_pen_tip_while_writing(self):
        noi_dung = "loai: y-tung-y\ntieu-de: Ba bước\ny: Nhờ ướt nhẫm quyết định mọi thứ\ny: Hai bước nhỏ\n"
        ngoi_chu = """(id) => {
            const tay = document.getElementById('ban-tay');
            const s = document.querySelector('[data-id="' + id + '"] .ngoi').getBoundingClientRect();
            const n = document.getElementById('ngoi-but').getBoundingClientRect();
            return {hien: getComputedStyle(tay).display !== 'none',
                    d: Math.hypot((n.left + n.width / 2) - s.left, (n.top + n.height / 2) - (s.top + 0.8 * s.height))};
        }"""
        for tai, cac_muc in (({}, ("tieu-de", "y-0", "y-1")), ({"hinh": self.hinh}, ("tieu-de", "y-1"))):
            du = du_hinh(noi_dung + ("hinh: flask\n" if tai else ""), tai)
            chup.mo_trang(self.page, trang.dung_trang(du))
            for id_muc in cac_muc:
                with self.subTest(hinh=bool(tai), muc=id_muc):
                    m = self.muc(id_muc)
                    self.page.evaluate("(t) => window.datThoiDiem(t)", m["batDau"] + 0.5 * m["thoiLuong"])
                    kq = self.page.evaluate(ngoi_chu, id_muc)
                    self.assertTrue(kq["hien"])
                    self.assertLess(kq["d"], 40)
            self.page.evaluate("(t) => window.datThoiDiem(t)", du["thoiLuong"] - 1 / 30)
            self.assertEqual(self.page.evaluate("getComputedStyle(document.getElementById('ban-tay')).display"), "none")
        m = self.muc("hinh")
        self.page.evaluate("(t) => window.datThoiDiem(t)", m["batDau"] + 0.5 * m["thoiLuong"])
        trong = self.page.evaluate("""() => {
            const g = document.querySelector('g.hinh').getBoundingClientRect();
            const n = document.getElementById('ngoi-but').getBoundingClientRect();
            const x = n.left + n.width / 2, y = n.top + n.height / 2;
            return x >= g.left - 10 && x <= g.right + 10 && y >= g.top - 10 && y <= g.bottom + 10; }""")
        self.assertTrue(trong, "giữa lúc vẽ hình, ngòi bút phải nằm trên hình")

    def test_board_wipe_uncovers_the_previous_scene(self):
        import base64
        du = du_hinh("loai: khai-niem\nthuat-ngu: Chu kì\ndinh-nghia: Thời gian.\n", {}, so=2)
        self.assertTrue(du["co"]["lauBang"])
        du["nenTruoc"] = "data:image/png;base64," + base64.b64encode(png(1280, 720)).decode("ascii")
        chup.mo_trang(self.page, trang.dung_trang(du))
        thay = """() => { const n = document.getElementById('nen-truoc');
            if (!n || getComputedStyle(n).display === 'none') { return 0; }
            const m = /inset\\(0(?:px)? 0(?:px)? 0(?:px)? ([\\d.]+)px\\)/.exec(n.style.clipPath);
            return 1280 - (m ? Number(m[1]) : 0); }"""
        self.page.evaluate("window.datThoiDiem(0.05)")
        self.assertGreater(self.page.evaluate(thay), 1000)
        self.assertEqual(self.page.evaluate("document.getElementById('ban-tay').getAttribute('data-kieu')"), "gie")
        self.page.evaluate("window.datThoiDiem(0.6)")
        self.assertEqual(self.page.evaluate(thay), 0)

    def test_camera_zooms_during_the_scene_and_is_home_on_the_last_frame(self):
        du = du_hinh("loai: minh-hoa\ntieu-de: Dụng cụ\nhinh: flask | Bình\nhinh: flask | Bình\nhinh: flask | Bình\n",
                     {"hinhs": [{**self.hinh, "nhan": "Bình"} for _ in range(3)]})
        html = trang.dung_trang(du)
        chup.mo_trang(self.page, html)
        m = self.muc("hinh-1")
        tf = "getComputedStyle(document.getElementById('bang')).transform"
        self.page.evaluate("(t) => window.datThoiDiem(t)", m["batDau"] + 0.8 * m["thoiLuong"])
        giua = self.page.evaluate(tf)
        self.assertNotEqual(giua, "none")
        self.assertGreater(float(giua[len("matrix("):].split(",")[0]), 1.05)
        self.page.evaluate("(t) => window.datThoiDiem(t)", du["thoiLuong"] - 1 / 30)
        self.assertIn(self.page.evaluate(tf), ("none", "matrix(1, 0, 0, 1, 0, 0)"))
        t = m["batDau"] + 0.5 * m["thoiLuong"]
        self.page.evaluate("(t) => window.datThoiDiem(t)", t)
        mot = self.page.screenshot(type="png")
        self.page.evaluate("(t) => window.datThoiDiem(t)", 0.1)
        self.page.evaluate("(t) => window.datThoiDiem(t)", t)
        self.assertEqual(mot, self.page.screenshot(type="png"), "cùng t phải cho cùng khung")

    def test_icon_attributes_with_namespace_or_event_keys_are_skipped(self):
        hinh_la = {"ten": "la", "viewBox": "0 0 24 24", "phanTu": [
            {"the": "path", "thuocTinh": {"d": "M2 2l20 20", "{urn:x-thu}nhan": "a", "onload": "window.BI_CHAY = 1"}},
            {"the": "circle", "thuocTinh": {"cx": "12", "cy": "12", "r": "5", "ONCLICK": "window.BI_CHAY = 2"}},
        ]}
        du = du_hinh("loai: y-tung-y\ntieu-de: T\ny: Một\nhinh: flask\n", {"hinh": hinh_la})
        chup.mo_trang(self.page, trang.dung_trang(du))
        self.page.evaluate("window.datThoiDiem(1e6)")
        kq = self.page.evaluate("""() => Array.from(document.querySelectorAll('g.hinh > *'))
            .map((e) => Array.from(e.attributes).map((a) => a.name))""")
        self.assertEqual(len(kq), 2)
        for ten in kq:
            self.assertFalse([a for a in ten if a.lower().startswith("on") or "{" in a or "nhan" in a], ten)
        self.assertIsNone(self.page.evaluate("window.BI_CHAY"))

    def test_kiem_tran_still_catches_overflow_with_a_picture(self):
        du = du_hinh("loai: y-tung-y\ntieu-de: T\ny: " + "A" * 60 + "\nhinh: flask\n", {"hinh": self.hinh})
        self.assertIn("y-0", chup.kiem_tran(self.page, trang.dung_trang(du)))


@unittest.skipUnless(co_chromium(), NEED_CHROMIUM)
class NhanChromiumTest(unittest.TestCase):
    """Cụm nhấn, số chạy, tiêu đề nảy chữ trong Chromium thật."""

    @classmethod
    def setUpClass(cls):
        from video_ma_parts import hinh
        cls.hinh = hinh.doc("flask")
        cls.cm = chup.trinh_duyet()
        cls.browser = cls.cm.__enter__()
        cls.page = chup.trang_moi(cls.browser)

    @classmethod
    def tearDownClass(cls):
        cls.cm.__exit__(None, None, None)

    def muc(self, id_muc: str) -> dict:
        return self.page.evaluate(
            "(id) => THI_CANH[DU_CANH.loai].muc(DU_CANH).filter((m) => m.id === id)[0]", id_muc)

    def dat(self, t: float) -> None:
        self.page.evaluate("(t) => window.datThoiDiem(t)", t)

    TRANG_THAI = """() => {
        const to = document.querySelector('.cum.to');
        const net = [...document.querySelectorAll('path.nhan-net')];
        return {to: to.style.backgroundSize,
                net: net.map((p) => [getComputedStyle(p).opacity, Number(p.style.strokeDashoffset)])};
    }"""

    def test_emphasis_appears_when_the_narrator_says_it_not_before(self):
        noi_dung = ("loai: khai-niem\nthuat-ngu: Chu kì\n"
                    "dinh-nghia: Thời gian để ==vật== thực hiện ((một dao động)) __toàn phần__.\n")
        du, _ = du_cua(noi_dung, giay=10.0)
        chup.mo_trang(self.page, trang.dung_trang(du))
        m = self.muc("dinh-nghia")
        noi = m["batDau"] + m["thoiLuong"] + 1.0
        self.assertLess(noi + 0.6, du["thoiLuong"] - 0.2)
        du["tu"] = [{"t": noi + 0.01 * i, "d": 0.01, "chu": w, "khoa": w.lower()}
                    for i, w in enumerate(("Vật", "một", "dao", "động", "toàn", "phần."))]
        chup.mo_trang(self.page, trang.dung_trang(du))
        self.dat(noi - 0.05)
        truoc = self.page.evaluate(self.TRANG_THAI)
        self.assertEqual(truoc["to"], "0% 100%")
        self.assertEqual([o for o, _ in truoc["net"]], ["0", "0"])
        self.dat(noi + 0.25)
        giua = self.page.evaluate(self.TRANG_THAI)
        self.assertNotIn(giua["to"], ("0% 100%", "100% 100%"))
        # So trạng thái DOM (không so ảnh chụp: nét SVG khi máy quay phóng có thể lệch vài điểm ảnh giữa hai lần vẽ,
        # kể cả trước thay đổi này). Bỏ bàn tay đang ẩn.
        bang = """() => [...document.getElementById('bang').children]
            .filter((e) => e.id !== 'ban-tay').map((e) => e.outerHTML).join('')
            + document.getElementById('bang').style.transform"""
        mot = self.page.evaluate(bang)
        self.dat(0.1)
        self.dat(noi + 0.25)
        self.assertEqual(mot, self.page.evaluate(bang), "cùng t phải cho cùng khung")
        self.dat(noi + 0.6)
        sau = self.page.evaluate(self.TRANG_THAI)
        self.assertEqual(sau["to"], "100% 100%")
        self.assertEqual(sau["net"], [["1", 0], ["1", 0]])

    def test_emphasis_missing_from_the_narration_fires_after_it_is_written(self):
        # Cụm ở cuối dòng: viết xong cụm gần như cùng lúc viết xong mục; nổ 0,3 s sau đó.
        du, _ = du_cua("loai: khai-niem\nthuat-ngu: Chu kì\ndinh-nghia: Nhớ ==chu kỳ==\n", giay=10.0,
                       loi="Chu kì là thời gian. Hết bài.")
        du["tu"] = [{"t": 1.0, "d": 0.2, "chu": "Chu", "khoa": "chu"}, {"t": 1.2, "d": 0.2, "chu": "kì", "khoa": "kì"}]
        chup.mo_trang(self.page, trang.dung_trang(du))
        m = self.muc("dinh-nghia")
        xong = m["batDau"] + m["thoiLuong"]
        self.dat(xong + 0.2)
        self.assertEqual(self.page.evaluate(self.TRANG_THAI)["to"], "0% 100%")
        self.dat(xong + 0.8)
        self.assertEqual(self.page.evaluate(self.TRANG_THAI)["to"], "100% 100%")

    def test_longest_emphasis_at_the_text_limits_does_not_overflow(self):
        from video_ma_parts import kiem

        def cum(dau, n, cuoi):
            return dau + vi_text(n) + cuoi
        casos = {
            "y-tung-y": "loai: y-tung-y\ntieu-de: " + cum("((", 90, "))") + "\n"
                        + "".join(f"y: {cum(d, 60, c)}\n" for d, c in (("==", "=="), ("((", "))"), ("__", "__")) * 2),
            "khai-niem": ("loai: khai-niem\nthuat-ngu: " + cum("((", 60, "))") + "\ndinh-nghia: "
                          + cum("==", 70, "== ") + cum("((", 70, ")) ") + cum("__", 78, "__") + "\n"),
            "tieu-de": "loai: tieu-de\nchu: " + cum("((", 90, "))") + "\nphu: " + cum("__", 90, "__") + "\n",
            "so-sanh": ("loai: so-sanh\ntieu-de: S\ntrai: " + cum("((", 24, "))") + "\nphai: " + cum("==", 24, "==") + "\n"
                        + "".join(f"y-trai: {cum('((', 60, '))')}\n" for _ in range(4))
                        + "".join(f"y-phai: {cum('__', 60, '__')}\n" for _ in range(4))),
            "cot-hinh": "loai: y-tung-y\ntieu-de: " + cum("((", 90, "))") + "\nhinh: flask\n"
                        + "".join(f"y: {cum('((', 60, '))')}\n" for _ in range(6)),
            "khai-niem-cot": ("loai: khai-niem\nthuat-ngu: " + cum("((", 60, "))") + "\nhinh: flask\ndinh-nghia: "
                              + cum("((", 70, ")) ") + cum("((", 70, ")) ") + cum("((", 78, "))") + "\n"),
            "cong-thuc-cot": ("loai: cong-thuc\nbieu-thuc: y = ((a+b))__c\nhinh: flask\n"
                              + "".join(f"giai-thich: {cum('((', 60, '))')}\n" for _ in range(4))),
            "dinh-nghia-khoanh":"loai: khai-niem\nthuat-ngu: A\ndinh-nghia: " + cum("((", 200, "))") + "\n",
        }
        for loai, noi_dung in casos.items():
            with self.subTest(loai=loai):
                text = f"---\n{META}---\n\n## Cảnh 1\n{noi_dung}loi: Xin chào.\n"
                if "hinh: flask" not in noi_dung:
                    kiem.kiem(parse.parse(text), Path("."))
                du = du_hinh(noi_dung, {"hinh": self.hinh} if "hinh: flask" in noi_dung else {})
                self.assertEqual(chup.kiem_tran(self.page, trang.dung_trang(du)), [])
                bien = self.page.evaluate("""() => [...document.querySelectorAll('path.nhan-net')].map((p) => {
                    const b = p.getBBox(); return [b.x, b.y, b.x + b.width, b.y + b.height]; })""")
                for x1, y1, x2, y2 in bien:
                    self.assertGreaterEqual(min(x1, y1), 0)
                    self.assertLessEqual(x2, 1280)
                    self.assertLessEqual(y2, 620)

    # Mỗi vòng elip (mỗi đoạn `M` của path) và hộp các chữ không thuộc cụm khoanh nào, toạ độ khung ở Z = 1.
    VONG_VA_CHU = """(id) => {
        const k = document.getElementById('khung').getBoundingClientRect();
        const vong = [...document.querySelectorAll('path.nhan-net.khoanh')].flatMap((p) =>
            p.getAttribute('d').split('M').filter((s) => s.trim()).map((s) => {
                const so = s.match(/-?\\d+(\\.\\d+)?/g).map(Number);
                const xs = so.filter((_, i) => i % 2 === 0), ys = so.filter((_, i) => i % 2 === 1);
                return [Math.min(...xs), Math.min(...ys), Math.max(...xs), Math.max(...ys)]; }));
        const el = document.querySelector('[data-id="' + id + '"]');
        const di = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
        const rg = document.createRange(); const chu = []; let n;
        while ((n = di.nextNode())) {
            if (n.parentElement.closest('.cum.khoanh')) { continue; }
            for (let i = 0; i < n.data.length; i++) {
                if (/\\s/.test(n.data[i])) { continue; }
                rg.setStart(n, i); rg.setEnd(n, i + 1);
                const r = rg.getBoundingClientRect();
                chu.push([n.data[i], r.left - k.left, r.top - k.top, r.right - k.left, r.bottom - k.top]);
            }
        }
        return {vong, chu}; }"""

    def test_circle_clears_neighbouring_letters_and_the_lines_above_and_below(self):
        casos = {
            "dinh-nghia": ("loai: khai-niem\nthuat-ngu: Chu kì\ndinh-nghia: Thời gian để vật thực hiện một dao động "
                           "toàn phần, đo bằng giây, rồi thêm chữ cho dài ra hai dòng để ((một dao động)) nằm giữa "
                           "hai dòng chữ khác và ((cụm này khá dài nên sẽ phải xuống dòng ở giữa cụm khoanh)) nhé.\n"),
            "y-0": "loai: y-tung-y\ntieu-de: A\ny: Thời gian để vật thực hiện ((một dao động)) toàn phần\n",
        }
        for chu_dong in (True, False):
            for id_muc, noi_dung in casos.items():
                with self.subTest(muc=id_muc, chu_dong=chu_dong):
                    du, _ = du_cua(noi_dung, giay=10.0)
                    du["co"]["chuDong"] = chu_dong
                    chup.mo_trang(self.page, trang.dung_trang(du))
                    self.assertEqual(self.page.evaluate("THI_VIDEO.kiemTran()"), [])
                    kq = self.page.evaluate(self.VONG_VA_CHU, id_muc)
                    self.assertGreaterEqual(len(kq["vong"]), 2 if id_muc == "dinh-nghia" else 1)
                    if id_muc == "dinh-nghia":
                        self.assertGreaterEqual(len(kq["vong"]), 3, "cụm hai dòng phải có một vòng mỗi dòng")
                    for x1, y1, x2, y2 in kq["vong"]:
                        for c, a1, b1, a2, b2 in kq["chu"]:
                            cham = a1 < x2 - 0.5 and a2 > x1 + 0.5 and b1 < y2 - 0.5 and b2 > y1 + 0.5
                            self.assertFalse(cham, f"vòng {[x1, y1, x2, y2]} chạm chữ '{c}' {[a1, b1, a2, b2]}")

    def test_bouncing_emphasis_keeps_a_gap_to_its_neighbours(self):
        noi_dung = "loai: y-tung-y\ntieu-de: A\ny: Thời gian để ==vật== thực hiện ((một dao động)) toàn phần\n"
        du, _ = du_cua(noi_dung, giay=10.0)
        chup.mo_trang(self.page, trang.dung_trang(du))
        m = self.muc("y-0")
        noi = m["batDau"] + m["thoiLuong"] + 1.0
        du["tu"] = [{"t": noi + 0.01 * i, "d": 0.01, "chu": w, "khoa": w.lower()}
                    for i, w in enumerate(("vật", "một", "dao", "động"))]
        chup.mo_trang(self.page, trang.dung_trang(du))
        self.dat(noi + 0.225)
        kq = self.page.evaluate("""() => [...document.querySelectorAll('[data-id=y-0] .cum')].map((sp) => {
            const r = sp.getBoundingClientRect();
            const rg = document.createRange();
            const ke = (n, i) => { rg.setStart(n, i); rg.setEnd(n, i + 1); return rg.getBoundingClientRect(); };
            const truoc = sp.previousSibling, sau = sp.nextSibling;
            const a = ke(truoc, truoc.data.trimEnd().length - 1), b = ke(sau, sau.data.length - sau.data.trimStart().length);
            return {tf: sp.style.transform, trai: r.left - a.right, phai: b.left - r.right}; })""")
        self.assertEqual(len(kq), 2)
        for c in kq:
            self.assertTrue(c["tf"].startswith("scale(1.") and c["tf"] != "scale(1)", c)
            self.assertGreaterEqual(c["trai"], 1, c)
            self.assertGreaterEqual(c["phai"], 1, c)

    def test_kiem_tran_reports_an_ellipse_below_the_subtitle_line(self):
        du, _ = du_cua("loai: y-tung-y\ntieu-de: A\ny: Một ((hai)) ba\n")
        chup.mo_trang(self.page, trang.dung_trang(du))
        self.page.evaluate("document.querySelector('[data-id=\"y-0\"]').style.top = '586px'")
        loi = self.page.evaluate("THI_VIDEO.kiemTran()")
        self.assertIn("nhan-y-0-0", loi)

    def test_kiem_tran_still_catches_overflow_with_emphasis(self):
        du, _ = du_cua("loai: tieu-de\nchu: ((" + "A" * 80 + "))\n")
        self.assertIn("chu", chup.kiem_tran(self.page, trang.dung_trang(du)))

    def test_bouncing_title_shows_every_letter_at_the_end(self):
        chu = "Con lắc ==đơn== và {{12}} dao động"
        for tai in ({}, {"hinh": self.hinh}):
            with self.subTest(hinh=bool(tai)):
                du = du_hinh(f"loai: tieu-de\nchu: {chu}\n" + ("hinh: flask\n" if tai else ""), tai, giay=1.0)
                self.assertTrue(du["co"]["chuDong"])
                chup.mo_trang(self.page, trang.dung_trang(du))
                m = self.muc("chu")
                self.assertIs(m["tay"], False)
                self.dat(m["batDau"] + 0.3 * m["thoiLuong"])
                mo = self.page.evaluate("[...document.querySelectorAll('[data-id=chu] .nay')].map((s) => getComputedStyle(s).opacity)")
                self.assertTrue(any(float(o) < 1 for o in mo), "giữa lúc nảy phải còn chữ chưa hiện hẳn")
                self.dat(du["thoiLuong"] - 1 / 30)
                cuoi = self.page.evaluate("""() => {
                    const el = document.querySelector('[data-id=chu]');
                    return {chu: el.textContent.replace(/\\s+/g, ' ').trim(),
                            mo: [...el.querySelectorAll('.nay')].map((s) => getComputedStyle(s).opacity),
                            tay: getComputedStyle(document.getElementById('ban-tay')).display}; }""")
                self.assertEqual(cuoi["chu"], "Con lắc đơn và 12 dao động")
                self.assertTrue(all(o == "1" for o in cuoi["mo"]))
        du = du_hinh("loai: tieu-de\nchu: Con lắc\n", {})
        du["co"]["chuDong"] = False
        chup.mo_trang(self.page, trang.dung_trang(du))
        self.assertEqual(self.page.evaluate("document.querySelectorAll('.nay').length"), 0)

    def test_running_number_ends_on_its_value_and_keeps_its_width(self):
        du, _ = du_cua("loai: y-tung-y\ntieu-de: Số\ny: Được {{1500}} lần và {{2.5}} m\n")
        chup.mo_trang(self.page, trang.dung_trang(du))
        m = self.muc("y-0")
        do = """() => [...document.querySelectorAll('[data-id=y-0] .so')].map((s) => {
            const c = s.querySelector('.so-chay'); return [c ? c.textContent : s.textContent, s.offsetWidth]; })"""
        self.dat(du["thoiLuong"] - 1 / 30)
        cuoi = self.page.evaluate(do)
        self.assertEqual([c for c, _ in cuoi], ["1500", "2,5"])
        self.assertIn("Được 1500 lần và 2,5 m", self.page.evaluate("document.querySelector('[data-id=y-0]').textContent"))
        self.dat(m["batDau"] + m["thoiLuong"] * ("Được ".__len__() + 1) / len("Được 1500 lần và 2,5 m") + 0.2)
        giua = self.page.evaluate(do)
        self.assertNotEqual(giua[0][0], "1500")
        self.assertAlmostEqual(giua[0][1], cuoi[0][1], delta=0.5)


SO_GIOI_HAN = ["12.5", "-40", "0", "100000", "1", "-7.25", "3000", "99999.99"]


def bieu_do_toi_da(kieu: str) -> str:
    so = [s.lstrip("-") if kieu == "tron" and s != "0" else ("0.5" if kieu == "tron" else s) for s in SO_GIOI_HAN]
    them = ("" if kieu == "tron"
            else f"don-vi: {vi_text(12)}\ntruc-ngang: {vi_text(40)}\ntruc-doc: {vi_text(40)}\n")
    return (f"loai: bieu-do\ntieu-de: {vi_text(90)}\nkieu: {kieu}\n{them}"
            + "".join(f"du-lieu: {vi_text(16)} | {s}\n" for s in so))


CANH_MOI_TOI_DA = {
    "cot": bieu_do_toi_da("cot"),
    "duong": bieu_do_toi_da("duong"),
    "tron": bieu_do_toi_da("tron"),
    "so-do": f"loai: so-do\ntrung-tam: {vi_text(30)}\n" + "".join(f"nhanh: {vi_text(40)}\n" for _ in range(6)),
    "so-do-hinh": f"loai: so-do\ntrung-tam: {vi_text(30)}\nhinh: flask\n" + "".join(f"nhanh: {vi_text(40)}\n" for _ in range(6)),
    "dong-thoi-gian": f"loai: dong-thoi-gian\ntieu-de: {vi_text(90)}\n" + "".join(
        f"moc: {vi_text(12)} | {vi_text(60)}\n" for _ in range(6)),
    "dong-thoi-gian-4": f"loai: dong-thoi-gian\ntieu-de: {vi_text(90)}\n" + "".join(
        f"moc: {vi_text(12)} | {vi_text(60)}\n" for _ in range(4)),
    "cong-thuc": ("loai: cong-thuc\nbieu-thuc: " + " | ".join(vi_text(21) for _ in range(4)) + "\n"
                  + "".join(f"giai-thich: {vi_text(60)}\n" for _ in range(4))),
    "cong-thuc-hinh": ("loai: cong-thuc\nbieu-thuc: " + " | ".join(vi_text(21) for _ in range(4)) + "\nhinh: flask\n"
                       + "".join(f"giai-thich: {vi_text(60)}\n" for _ in range(4))),
}

# Hộp chữ thật (theo từng dòng) của mọi ô chữ và hộp mọi nét SVG (trừ bàn tay), toạ độ khung ở Z = 1.
HOP_CANH = """() => {
    const k = document.getElementById('khung').getBoundingClientRect();
    const chu = [...document.querySelectorAll('#bang .chu')].map((el) => {
        const r = document.createRange(); r.selectNodeContents(el);
        const b = r.getBoundingClientRect();
        return {id: el.dataset.id, l: b.left - k.left, t: b.top - k.top, r: b.right - k.left, b: b.bottom - k.top, w: b.width};
    }).filter((h) => h.w > 0);
    const net = [...document.querySelectorAll('#bang svg.ve path')].filter((p) => p.getAttribute('d') !== 'M0 0').map((p) => {
        const b = p.getBBox(); return {l: b.x, t: b.y, r: b.x + b.width, b: b.y + b.height}; });
    return {chu, net}; }"""


@unittest.skipUnless(co_chromium(), NEED_CHROMIUM)
class ChartMapTimelineChromiumTest(unittest.TestCase):
    """Biểu đồ, sơ đồ tư duy, dòng thời gian, công thức từng phần ở giới hạn tối đa (Chromium thật)."""

    @classmethod
    def setUpClass(cls):
        from video_ma_parts import hinh
        cls.hinh = hinh.doc("flask")
        cls.cm = chup.trinh_duyet()
        cls.browser = cls.cm.__enter__()
        cls.page = chup.trang_moi(cls.browser)

    @classmethod
    def tearDownClass(cls):
        cls.cm.__exit__(None, None, None)

    def du(self, noi_dung: str, giay: float = 12.0) -> dict:
        from video_ma_parts import kiem

        text = f"---\n{META}---\n\n## Cảnh 1\n{noi_dung}loi: Một. Hai. Ba.\n"
        kiem.kiem(parse.parse(text), Path("."))
        return du_hinh(noi_dung, {"hinh": self.hinh} if "hinh: flask" in noi_dung else {}, giay=giay,
                       loi="Một. Hai. Ba.")

    def cuoi(self, du: dict) -> dict:
        chup.mo_trang(self.page, trang.dung_trang(du))
        self.page.evaluate("window.datThoiDiem(window.THI_VIDEO.thoiDiemCuoi())")
        return self.page.evaluate(HOP_CANH)

    def test_every_new_scene_at_its_limits_fits_above_the_subtitles(self):
        for ten, noi_dung in CANH_MOI_TOI_DA.items():
            with self.subTest(canh=ten):
                du = self.du(noi_dung)
                self.assertEqual(chup.kiem_tran(self.page, trang.dung_trang(du)), [])
                hop = self.cuoi(du)
                for h in hop["chu"] + hop["net"]:
                    self.assertGreaterEqual(min(h["l"], h["t"]), -1, h)
                    self.assertLessEqual(h["r"], 1281, h)
                    self.assertLessEqual(h["b"], 620, h)

    def test_text_boxes_never_overlap_in_charts_maps_and_timelines(self):
        for ten in ("cot", "duong", "tron", "so-do", "so-do-hinh", "dong-thoi-gian", "dong-thoi-gian-4"):
            with self.subTest(canh=ten):
                chu = self.cuoi(self.du(CANH_MOI_TOI_DA[ten]))["chu"]
                for i, a in enumerate(chu):
                    for b in chu[i + 1:]:
                        giao = a["l"] < b["r"] - 0.5 and b["l"] < a["r"] - 0.5 and a["t"] < b["b"] - 0.5 and b["t"] < a["b"] - 0.5
                        self.assertFalse(giao, f"`{a['id']}` chồng `{b['id']}`: {a} / {b}")

    def test_bar_values_run_to_their_exact_value_without_overlapping_for_huge_ranges(self):
        for du_lieu in (SO_GIOI_HAN, ["1", "100000"], ["-99999.99", "0", "0.001", "99999.99"]):
            with self.subTest(du_lieu=du_lieu):
                noi_dung = ("loai: bieu-do\ntieu-de: T\nkieu: cot\n"
                            + "".join(f"du-lieu: {vi_text(16)} | {s}\n" for s in du_lieu))
                chu = self.cuoi(self.du(noi_dung))["chu"]
                so = sorted((c for c in chu if c["id"].startswith("so-")), key=lambda c: int(c["id"][3:]))
                text = self.page.evaluate("() => [...document.querySelectorAll('[data-id^=so-]')].map((e) => e.textContent)")
                self.assertEqual([t.replace("−", "-") for t in text], [s.replace(".", ",") for s in du_lieu])
                for a, b in zip(so, so[1:]):
                    self.assertLessEqual(a["r"], b["l"], f"nhãn giá trị chồng nhau: {a} / {b}")

    def test_bar_grows_from_the_axis_and_negative_bar_grows_down(self):
        du = self.du("loai: bieu-do\ntieu-de: T\nkieu: cot\ndu-lieu: A | 30\ndu-lieu: B | -20\n")
        chup.mo_trang(self.page, trang.dung_trang(du))
        cao = """() => [...document.querySelectorAll('path.to-mau')].map((p) => {
            const b = p.getBBox(); return [b.y, b.height]; })"""
        for k in (0, 1):
            m = self.page.evaluate(f"THI_CANH['bieu-do'].muc(DU_CANH).filter((m) => m.id === 'cot-{k}')[0]")
            self.page.evaluate("(t) => window.datThoiDiem(t)", m["batDau"] - 0.01)
            self.assertLess(self.page.evaluate(cao)[k][1], 0.5)
            self.page.evaluate("(t) => window.datThoiDiem(t)", m["batDau"] + 0.1 * m["thoiLuong"])
            giua = self.page.evaluate(cao)[k]
            self.page.evaluate("(t) => window.datThoiDiem(t)", du["thoiLuong"] - 0.2)
            cuoi = self.page.evaluate(cao)[k]
            self.assertTrue(0.5 < giua[1] < cuoi[1], (giua, cuoi))
            if k == 0:
                self.assertAlmostEqual(giua[0] + giua[1], cuoi[0] + cuoi[1], delta=0.5)  # đáy cố định ở trục
            else:
                self.assertAlmostEqual(giua[0], cuoi[0], delta=0.5)  # đỉnh cố định ở trục, cột âm mọc xuống

    def test_formula_parts_appear_one_after_another(self):
        du = self.du("loai: cong-thuc\nbieu-thuc: T = 2π√(l/g) | ≈ {{2.01}} s\n", giay=12.0)
        chup.mo_trang(self.page, trang.dung_trang(du))
        m = self.page.evaluate("THI_CANH['cong-thuc'].muc(DU_CANH).filter((m) => m.id === 'bieu-thuc')[0]")
        p0, p1 = m["phan"]
        self.assertGreater(p1["batDau"], p0["batDau"] + p0["thoiLuong"] + 0.5)
        hien = """() => { const el = document.querySelector('[data-id="bieu-thuc"]').cloneNode(true);
            el.querySelectorAll('.an, .so-cuoi').forEach((s) => s.remove()); return el.textContent.trim(); }"""
        self.page.evaluate("(t) => window.datThoiDiem(t)", (p0["batDau"] + p0["thoiLuong"] + p1["batDau"]) / 2)
        self.assertEqual(self.page.evaluate(hien), "T = 2π√(l/g)")
        self.page.evaluate("(t) => window.datThoiDiem(t)", du["thoiLuong"] - 0.2)
        self.assertEqual(self.page.evaluate(hien), "T = 2π√(l/g) ≈ 2,01 s")


def cau_hoi_toi_da(n: int, dai_lc: int = 60) -> str:
    return (f"loai: cau-hoi\ncau-hoi: {vi_text(160)}\n" + "".join(f"lua-chon: {vi_text(dai_lc)}\n" for _ in range(n))
            + f"dap-an: {'ABCD'[n - 1]}\ngiai-thich: {vi_text(180)}\nloi-giai: Đáp án. Vì vậy.\n")


CAU_HOI_TOI_DA = {"4": cau_hoi_toi_da(4), "3": cau_hoi_toi_da(3), "2": cau_hoi_toi_da(2), "4-34": cau_hoi_toi_da(4, 34),
                  "ngan": "loai: cau-hoi\ncau-hoi: Chu kì?\nlua-chon: Tăng\nlua-chon: Giảm\ndap-an: A\ncho: 3\n"
                          "giai-thich: Vì l tăng.\nloi-giai: Đáp án A.\n"}
# Hộp của đồng hồ, viền đúng và dấu ✓ (toạ độ khung ở Z = 1).
HOP_CAU_HOI = """() => ['#dong-ho', 'path.dung-vien', '#dau-dung'].map((s) => {
    const b = document.querySelector(s).getBBox(); return {id: s, l: b.x, t: b.y, r: b.x + b.width, b: b.y + b.height}; })"""


@unittest.skipUnless(co_chromium(), NEED_CHROMIUM)
class QuizChromiumTest(unittest.TestCase):
    """Cảnh câu hỏi nhanh ở giới hạn tối đa (Chromium thật)."""

    @classmethod
    def setUpClass(cls):
        cls.cm = chup.trinh_duyet()
        cls.browser = cls.cm.__enter__()
        cls.page = chup.trang_moi(cls.browser)

    @classmethod
    def tearDownClass(cls):
        cls.cm.__exit__(None, None, None)

    def du(self, noi_dung: str, giay: float = 9.0, giay_giai: float = 6.0) -> dict:
        from video_ma_parts import kiem

        text = f"---\n{META}---\n\n## Cảnh 1\n{noi_dung}loi: Một. Hai. Ba. Bốn. Năm.\n"
        video = parse.parse(text)
        self.assertEqual(kiem.kiem(video, Path(".")), [])
        giai = lich.GiongInfo(mp3=None, giay=giay_giai, moc_cau=[0.0, 2.0], uoc_luong=False, nguon="may")
        giong = lich.GiongInfo(mp3=None, giay=giay, moc_cau=[0.0, 1.5, 3.0, 4.5, 6.0], uoc_luong=False, nguon="may", giai=giai)
        plan, _ = lich.dung_lich(video.canh, [giong])
        return lich.du_lieu_canh(video.canh[0], plan[0], None, {"meta": {}})

    def dat(self, t: float) -> None:
        self.page.evaluate("(t) => window.datThoiDiem(t)", t)

    def test_every_quiz_at_its_limits_fits_above_the_subtitles(self):
        for ten, noi_dung in CAU_HOI_TOI_DA.items():
            with self.subTest(canh=ten):
                du = self.du(noi_dung)
                self.assertEqual(chup.kiem_tran(self.page, trang.dung_trang(du)), [])
                q = du["cauHoi"]
                for t in (q["batDauDem"] + q["cho"] / 2, du["thoiLuong"] - 0.2):
                    self.page.evaluate("() => { document.getElementById('bang').style.transform = 'none'; }")
                    self.dat(t)
                    self.page.evaluate("() => { document.getElementById('bang').style.transform = 'none'; }")
                    hop = self.page.evaluate(HOP_CANH)
                    for h in hop["chu"] + hop["net"] + self.page.evaluate(HOP_CAU_HOI):
                        self.assertGreaterEqual(min(h["l"], h["t"]), -1, h)
                        self.assertLessEqual(h["r"], 1281, h)
                        self.assertLessEqual(h["b"], 620, h)
                chu = self.page.evaluate(HOP_CANH)["chu"]
                for i, a in enumerate(chu):
                    for b in chu[i + 1:]:
                        giao = a["l"] < b["r"] - 0.5 and b["l"] < a["r"] - 0.5 and a["t"] < b["b"] - 0.5 and b["t"] < a["b"] - 0.5
                        self.assertFalse(giao, f"`{a['id']}` chồng `{b['id']}`: {a} / {b}")

    def test_tick_and_green_border_appear_only_when_the_answer_is_revealed(self):
        du = self.du(CAU_HOI_TOI_DA["4"])
        chup.mo_trang(self.page, trang.dung_trang(du))
        q = du["cauHoi"]
        do = """() => [document.getElementById('dau-dung'), document.querySelector('path.dung-vien'), document.getElementById('dong-ho')]
            .map((e) => Number(getComputedStyle(e).opacity))"""
        mo = "() => [...document.querySelectorAll('[data-id^=lc-]')].map((e) => Number(getComputedStyle(e).opacity))"
        self.dat(q["batDauGiai"] - 1 / 30)
        self.assertEqual(self.page.evaluate(do)[:2], [0, 0], "trước lúc giải không có ✓ và viền xanh")
        self.assertEqual(self.page.evaluate(mo), [1, 1, 1, 1])
        self.dat(q["batDauDem"] + 1.5)
        self.assertEqual(self.page.evaluate(do), [0, 0, 1])
        so = self.page.evaluate("() => document.querySelector('#dong-ho .so').textContent")
        self.assertEqual(so, str(q["cho"] - 1))
        self.assertEqual(self.page.evaluate("() => document.getElementById('ban-tay').style.display"), "none")
        self.dat(du["thoiLuong"] - 0.2)
        self.assertEqual(self.page.evaluate(do), [1, 1, 0], "sau lúc giải có ✓, viền xanh; đồng hồ đã tắt")
        self.assertEqual(self.page.evaluate(mo), [0.35, 0.35, 0.35, 1])
        giai = self.page.evaluate("() => document.querySelector('[data-id=giai-thich]').textContent")
        self.assertIn(vi_text(180)[:20], giai)

    def test_frames_are_repeatable_during_the_countdown(self):
        du = self.du(CAU_HOI_TOI_DA["3"])
        html = trang.dung_trang(du)
        t = du["cauHoi"]["batDauDem"] + 1.37
        anh = []
        for _ in range(2):
            chup.mo_trang(self.page, html)
            self.dat(t)
            anh.append(self.page.screenshot(type="png"))
        self.assertEqual(anh[0], anh[1])


def hai_canh(chuyen_canh: str):
    """Cảnh 1 (tiêu đề, có mực) và cảnh 2 với khoá đầu `chuyen-canh`."""
    text = (f"---\n{META}chuyen-canh: {chuyen_canh}\n---\n\n"
            "## Cảnh 1\nloai: tieu-de\nchu: Chu kì của con lắc đơn dao động nhỏ\nphu: Vật lí 11 · bài mở đầu\nloi: Chào.\n\n"
            "## Cảnh 2\nloai: khai-niem\nthuat-ngu: Chu kì\ndinh-nghia: Thời gian vật thực hiện một dao động toàn phần.\n"
            "loi: Một.\n")
    video = parse.parse(text)
    cac_giong = [lich.GiongInfo(mp3=None, giay=g, moc_cau=[0.0], uoc_luong=False, nguon="may") for g in (0.9, 1.2)]
    plan, _ = lich.dung_lich(video.canh, cac_giong)
    return [lich.du_lieu_canh(c, cl, None, {"meta": video.meta}) for c, cl in zip(video.canh, plan)], plan


# So khung `b` với nền cũ `a` trong vùng giữa (x 128–1152, y 72–648): tỉ lệ điểm ảnh khớp (lệch mỗi kênh ≤ 24),
# và tỉ lệ điểm mực của nền cũ (khác màu giấy #fbfaf5 quá 48) còn thấy trong `b` gần đúng chỗ (có điểm khớp trong
# ô 5×5 quanh nó của `b`; chuyển động dưới 2 px ở khung đầu không tính là mất nền).
SO_KHOP = """([a, b]) => Promise.all([a, b].map((src) => new Promise((ok, loi) => {
        const i = new Image(); i.onload = () => ok(i); i.onerror = loi; i.src = src; })))
    .then((imgs) => {
        const px = imgs.map((i) => { const c = document.createElement('canvas'); c.width = 1280; c.height = 720;
            const g = c.getContext('2d'); g.drawImage(i, 0, 0); return g.getImageData(128, 72, 1024, 576).data; });
        const W = 1024, H = 576, giay = [0xfb, 0xfa, 0xf5];
        const lech = (k, j) => Math.max(Math.abs(px[0][j] - px[1][k]), Math.abs(px[0][j + 1] - px[1][k + 1]),
                                        Math.abs(px[0][j + 2] - px[1][k + 2]));
        const laMuc = (j) => [0, 1, 2].some((c) => Math.abs(px[0][j + c] - giay[c]) > 48);
        let tong = 0, khop = 0, muc = 0, mucKhop = 0;
        for (let y = 0; y < H; y++) {
            for (let x = 0; x < W; x++) {
                const k = 4 * (y * W + x);
                tong++; if (lech(k, k) <= 24) { khop++; }
                if (!laMuc(k)) { continue; }
                muc++;
                let thay = false;
                for (let dy = -2; dy <= 2 && !thay; dy++) {
                    for (let dx = -2; dx <= 2 && !thay; dx++) {
                        const xx = x + dx, yy = y + dy, j = 4 * (yy * W + xx);
                        if (xx >= 0 && yy >= 0 && xx < W && yy < H && lech(j, k) <= 24) { thay = true; }
                    }
                }
                if (thay) { mucKhop++; }
            }
        }
        return {khop: khop / tong, muc: muc, mucKhop: mucKhop / Math.max(1, muc)}; })"""


@unittest.skipUnless(co_chromium(), NEED_CHROMIUM)
class TransitionChromiumTest(unittest.TestCase):
    """Năm kiểu chuyển cảnh trên khung cuối thật của cảnh trước."""

    @classmethod
    def setUpClass(cls):
        import base64

        cls.cm = chup.trinh_duyet()
        cls.browser = cls.cm.__enter__()
        cls.page = chup.trang_moi(cls.browser)
        cac_du, plan = hai_canh("lau-bang")
        chup.mo_trang(cls.page, trang.dung_trang(cac_du[0]))
        cls.page.evaluate("(t) => window.datThoiDiem(t)", (plan[0].so_khung - 1) / lich.FPS)
        cls.nen = "data:image/png;base64," + base64.b64encode(cls.page.screenshot(type="png")).decode("ascii")

    @classmethod
    def tearDownClass(cls):
        cls.cm.__exit__(None, None, None)

    def khung(self, du: dict, t: float) -> str:
        import base64

        self.page.evaluate("(t) => window.datThoiDiem(t)", t)
        return "data:image/png;base64," + base64.b64encode(self.page.screenshot(type="png")).decode("ascii")

    def so(self, khung: str) -> dict:
        return self.page.evaluate(SO_KHOP, [self.nen, khung])

    def test_every_kind_starts_on_the_previous_frame_and_ends_without_it(self):
        for kieu in ("lau-bang", "lat-trang", "truot", "phong", "mo-man"):
            with self.subTest(kieu=kieu):
                du = hai_canh(kieu)[0][1]
                self.assertEqual(du["co"]["chuyen"], kieu)
                du["nenTruoc"] = self.nen
                chup.mo_trang(self.page, trang.dung_trang(du))
                dau = self.so(self.khung(du, 1 / 30))
                self.assertGreater(dau["muc"], 2000, "nền cũ phải có mực")
                self.assertGreaterEqual(dau["khop"], 0.9, dau)
                self.assertGreaterEqual(dau["mucKhop"], 0.9, dau)
                sau = self.so(self.khung(du, 0.55))
                self.assertLess(sau["mucKhop"], 0.1, sau)
                an = self.page.evaluate("""() => Array.from(document.querySelectorAll('#nen-truoc, #nen-truoc-2'))
                    .every((n) => getComputedStyle(n).display === 'none')""")
                self.assertTrue(an)
                loe = self.page.evaluate("() => { const l = document.getElementById('loe-chuyen'); "
                                         "return l ? Number(getComputedStyle(l).opacity) : 0; }")
                self.assertEqual(loe, 0)

    def test_only_the_board_wipe_has_the_eraser_hand(self):
        for kieu in ("lau-bang", "lat-trang", "truot", "phong", "mo-man"):
            with self.subTest(kieu=kieu):
                du = hai_canh(kieu)[0][1]
                du["nenTruoc"] = self.nen
                chup.mo_trang(self.page, trang.dung_trang(du))
                self.page.evaluate("window.datThoiDiem(0.25)")
                tay = self.page.evaluate("""() => { const t = document.getElementById('ban-tay');
                    return {hien: getComputedStyle(t).display !== 'none', kieu: t.getAttribute('data-kieu')}; }""")
                if kieu == "lau-bang":
                    self.assertEqual(tay, {"hien": True, "kieu": "gie"})
                else:
                    self.assertFalse(tay["hien"], tay)

    def test_no_transition_for_khong_or_scene_one_even_with_a_background(self):
        cac_du, _ = hai_canh("khong")
        for du in (cac_du[1], hai_canh("truot")[0][0]):
            with self.subTest(so=du["so"]):
                self.assertIsNone(du["co"]["chuyen"])
                du["nenTruoc"] = self.nen
                chup.mo_trang(self.page, trang.dung_trang(du))
                self.assertIsNone(self.page.evaluate("document.getElementById('nen-truoc')"))
                self.assertLess(self.so(self.khung(du, 1 / 30))["mucKhop"], 0.1)


class TransitionBookkeepingTest(unittest.TestCase):
    """Mọi kiểu chuyển cảnh nhận khung cuối cảnh trước; không chuyển cảnh thì không."""

    def nen_luc_dung(self, chuyen_canh: str) -> list:
        text = (f"---\n{META}chuyen-canh: {chuyen_canh}\n---\n\n" + "".join(
            f"## Cảnh {k}\nloai: tieu-de\nchu: C{k}\nloi: Chào.\n\n" for k in (1, 2, 3)))
        video = parse.parse(text)
        plan, _ = lich.dung_lich(video.canh, [lich.GiongInfo(None, 0.9, [0.0], False, "may")] * 3)
        cac_du = [lich.du_lieu_canh(c, cl, None, {"meta": video.meta}) for c, cl in zip(video.canh, plan)]
        so_khung = [cl.so_khung for cl in plan]
        thay = []

        def dung_trang_gia(du, model=None):
            thay.append(du.get("nenTruoc") is not None)
            return "<html></html>"

        viec = {"cac_du": cac_du, "models_js": {}, "dau": 0, "cuoi": 3,
                "khung_dau": [0, so_khung[0], so_khung[0] + so_khung[1]], "so_khung": so_khung, "fps": lich.FPS}
        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch.object(chup, "trinh_duyet", CaptureBookkeepingTest.trinh_duyet_gia), \
                mock.patch.object(chup, "chup_canh", CaptureBookkeepingTest.chup_canh_gia), \
                mock.patch.object(trang, "dung_trang", dung_trang_gia), \
                contextlib.redirect_stderr(io.StringIO()):
            chup.chup_dai({**viec, "thu_muc_anh": tmp})
        return thay

    def test_every_kind_gets_the_previous_frame(self):
        for kieu in ("lau-bang", "lat-trang", "truot", "phong", "mo-man", "luan-phien"):
            with self.subTest(kieu=kieu):
                self.assertEqual(self.nen_luc_dung(kieu), [False, True, True])

    def test_khong_gets_no_background(self):
        self.assertEqual(self.nen_luc_dung("khong"), [False, False, False])


class ChiaDaiTest(unittest.TestCase):
    def kiem_phu(self, so_khung, so_tt, dai):
        self.assertTrue(dai)
        self.assertLessEqual(len(dai), min(so_tt, len(so_khung)))
        self.assertEqual(dai[0][0], 0)
        self.assertEqual(dai[-1][1], len(so_khung))
        for (a, b), (c, _) in zip(dai, dai[1:]):
            self.assertEqual(b, c)
        for a, b in dai:
            self.assertLess(a, b)
        self.assertEqual(sum(sum(so_khung[a:b]) for a, b in dai), sum(so_khung))

    def test_equal_scenes_split_into_four_neighbouring_ranges(self):
        self.assertEqual(chup.chia_dai([30] * 8, 4), [(0, 2), (2, 4), (4, 6), (6, 8)])

    def test_a_long_first_scene_gets_a_range_of_its_own(self):
        dai = chup.chia_dai([300, 30, 30, 30], 4)
        self.assertEqual(dai[0], (0, 1))
        self.kiem_phu([300, 30, 30, 30], 4, dai)

    def test_a_long_last_scene_is_not_lumped_with_the_short_ones(self):
        self.assertEqual(chup.chia_dai([1, 1, 1, 1000], 4)[-1], (3, 4))

    def test_one_scene_or_one_process_is_one_range(self):
        self.assertEqual(chup.chia_dai([90], 4), [(0, 1)])
        self.assertEqual(chup.chia_dai([90, 75, 30, 120], 1), [(0, 4)])

    def test_ranges_always_cover_every_scene_once(self):
        for so_khung in ([75, 84, 90], [30] * 7, [900, 75, 75, 75, 75, 900], [75, 1200], [5, 7, 11, 13, 17, 19, 23]):
            for so_tt in (1, 2, 3, 4):
                with self.subTest(so_khung=so_khung, so_tt=so_tt):
                    self.kiem_phu(so_khung, so_tt, chup.chia_dai(so_khung, so_tt))

    def test_process_count_is_half_the_cores_between_one_and_four(self):
        for loi, mong in ((None, 1), (1, 1), (2, 1), (3, 1), (6, 3), (8, 4), (32, 4)):
            with self.subTest(cpu=loi), mock.patch.object(chup.os, "cpu_count", return_value=loi):
                self.assertEqual(chup.so_tien_trinh(), mong)


def ba_canh_ngan():
    """Ba cảnh 2,5 / 2,8 / 3,0 giây, lau bảng ở cảnh 2 và 3."""
    text = (f"---\n{META}---\n\n"
            "## Cảnh 1\nloai: tieu-de\nchu: Chu kì của con lắc đơn dao động nhỏ\nphu: Vật lí 11 · bài mở đầu\nloi: Chào.\n\n"
            "## Cảnh 2\nloai: khai-niem\nthuat-ngu: Chu kì\ndinh-nghia: Thời gian vật thực hiện một dao động toàn phần.\nloi: Một.\n\n"
            "## Cảnh 3\nloai: y-tung-y\ntieu-de: Phụ thuộc vào\ny: Chiều dài dây\ny: Gia tốc trọng trường\nloi: Hai.\n")
    cac_canh = parse.parse(text).canh
    cac_giong = [lich.GiongInfo(mp3=None, giay=g, moc_cau=[0.0], uoc_luong=False, nguon="may") for g in (0.9, 1.2, 1.4)]
    plan, _ = lich.dung_lich(cac_canh, cac_giong)
    return [lich.du_lieu_canh(c, cl, None, {"meta": {}}) for c, cl in zip(cac_canh, plan)], [cl.so_khung for cl in plan]


_SO_SANH = """([a, b]) => Promise.all([a, b].map((src) => new Promise((ok, loi) => {
        const i = new Image(); i.onload = () => ok(i); i.onerror = loi; i.src = src; })))
    .then((imgs) => {
        const px = imgs.map((i) => { const c = document.createElement('canvas'); c.width = 1280; c.height = 720;
            const g = c.getContext('2d'); g.drawImage(i, 0, 0); return g.getImageData(X, 0, 1280 - X, 720).data; });
        let lon = 0;
        for (let k = 0; k < px[0].length; k++) { lon = Math.max(lon, Math.abs(px[0][k] - px[1][k])); }
        return lon; })"""
SO_SANH_NUA_PHAI = _SO_SANH.replace("X", "640")
SO_SANH_CA_KHUNG = _SO_SANH.replace("X", "0")
# Tỉ lệ điểm ảnh nửa phải có một kênh lệch quá 16 mức: khung tạm là JPEG nên nền cảnh trước (khung JPEG đọc lại rồi
# mã hoá lần nữa) chỉ gần đúng từng điểm ảnh.
LECH_NUA_PHAI = _SO_SANH.replace("X", "640").replace(
    """let lon = 0;
        for (let k = 0; k < px[0].length; k++) { lon = Math.max(lon, Math.abs(px[0][k] - px[1][k])); }
        return lon; })""",
    """let lech = 0;
        for (let k = 0; k < px[0].length; k += 4) {
            if ([0, 1, 2].some((c) => Math.abs(px[0][k + c] - px[1][k + c]) > 16)) { lech++; } }
        return lech / (px[0].length / 4); })""")


@unittest.skipUnless(co_chromium(), NEED_CHROMIUM)
class ParallelCaptureChromiumTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cac_du, cls.so_khung = ba_canh_ngan()
        cls.tmp = tempfile.TemporaryDirectory()
        cls.hai = Path(cls.tmp.name) / "hai"
        cls.mot = Path(cls.tmp.name) / "mot"
        chup.chup_song_song(cls.cac_du, {}, cls.so_khung, lich.FPS, cls.hai, 2)
        chup.chup_song_song(cls.cac_du, {}, cls.so_khung, lich.FPS, cls.mot, 1)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_scenes_are_short_and_split_across_both_processes(self):
        self.assertEqual(self.so_khung, [75, 84, 90])
        self.assertEqual(chup.chia_dai(self.so_khung, 2), [(0, 2), (2, 3)])
        self.assertTrue(self.cac_du[1]["co"]["lauBang"] and self.cac_du[2]["co"]["lauBang"])
        self.assertIsNone(self.cac_du[1]["nenTruoc"], "không được sửa dữ liệu của người gọi")

    def test_every_frame_is_written_once_with_no_gap(self):
        for thu_muc in (self.hai, self.mot):
            with self.subTest(thu_muc=thu_muc.name):
                ten = sorted(p.name for p in thu_muc.iterdir())
                self.assertEqual(ten, [f"f{i:06d}.jpg" for i in range(sum(self.so_khung))])

    def test_one_process_and_two_processes_give_the_same_frames(self):
        # Ngoại lệ duy nhất: các khung lau bảng của cảnh mở đầu dải thứ hai. Nền ở đó là khung cuối cảnh trước dựng
        # lại trực tiếp, còn Chromium vẽ lại nét gạch chân hơi khác (vài mức xám) khi trang đã được chụp liên tục.
        dau_dai_2 = self.so_khung[0] + self.so_khung[1]
        lau = range(dau_dai_2, dau_dai_2 + int(lich.LAU_BANG * lich.FPS) + 1)
        khac = []
        for i in range(sum(self.so_khung)):
            if (self.hai / f"f{i:06d}.jpg").read_bytes() != (self.mot / f"f{i:06d}.jpg").read_bytes():
                khac.append(i)
        self.assertTrue(set(khac) <= set(lau), khac)
        import base64

        def url(thu_muc, i):
            return "data:image/jpeg;base64," + base64.b64encode((thu_muc / f"f{i:06d}.jpg").read_bytes()).decode("ascii")

        with chup.trinh_duyet() as browser:
            page = chup.trang_moi(browser)
            page.set_content("<!doctype html><html><body></body></html>")
            for i in khac:
                a, b = url(self.hai, i), url(self.mot, i)
                self.assertLessEqual(page.evaluate(SO_SANH_CA_KHUNG, [a, b]), 8, i)

    def test_wiped_scene_starts_on_the_last_frame_of_the_previous_scene(self):
        import base64

        def url(i):
            return "data:image/jpeg;base64," + base64.b64encode((self.hai / f"f{i:06d}.jpg").read_bytes()).decode("ascii")

        dau = [0, self.so_khung[0], self.so_khung[0] + self.so_khung[1]]
        with chup.trinh_duyet() as browser:
            page = chup.trang_moi(browser)
            page.set_content("<!doctype html><html><body></body></html>")
            # Cảnh 2 lấy nền từ khung đã ghi trong cùng tiến trình; cảnh 3 (tiến trình thứ hai) tự dựng lại khung cuối cảnh 2.
            # Bảng trống thật: khung đầu cảnh 1 (chưa có nét nào trong một giây dẫn đầu, không lau bảng).
            bang_trong = url(0)
            for k in (1, 2):
                with self.subTest(canh=k + 1):
                    cuoi_truoc = dau[k] - 1
                    self.assertGreater(page.evaluate(SO_SANH_NUA_PHAI, [url(cuoi_truoc), bang_trong]), 64,
                                       "nửa phải khung cuối cảnh trước phải có mực, không phải bảng trống")
                    self.assertLessEqual(page.evaluate(LECH_NUA_PHAI, [url(cuoi_truoc), url(dau[k] + 1)]), 0.005)
                    self.assertGreater(page.evaluate(SO_SANH_NUA_PHAI, [url(cuoi_truoc), url(dau[k] + self.so_khung[k] - 1)]), 64,
                                       "khung cuối cảnh mới phải khác nền cảnh trước")

    def test_a_failing_range_is_a_dung_error_naming_its_scenes(self):
        cac_du = [dict(du) for du in self.cac_du[:2]]
        cac_du[1]["loai"] = "khong-co-loai-nay"
        with tempfile.TemporaryDirectory() as tmp, self.assertRaises(chup.MediaError) as caught:
            chup.chup_song_song(cac_du, {}, self.so_khung[:2], lich.FPS, Path(tmp), 2)
        self.assertEqual(caught.exception.step, "dung")
        self.assertIn("cảnh 2", caught.exception.message)


def _khong_mo_duoc_chromium(cong_viec):
    """Thay `_chup_dai_con` trong tiến trình con: Chromium không mở được (MediaError `chromium`)."""
    @contextlib.contextmanager
    def hong():
        raise chup.MediaError("chromium", "Không mở được Chromium: thử", chup.FIX_CHROMIUM)
        yield

    with mock.patch.object(chup, "trinh_duyet", hong):
        return chup._chup_dai_con(cong_viec)


class _PoolGia:
    """ProcessPoolExecutor giả, không tạo tiến trình. `hong`: dải đầu hỏng ngay, các dải sau còn chờ và tự xong
    sau 3 giây nếu không bị huỷ. Không `hong`: mọi dải xong ngay."""

    def __init__(self, hong, max_workers=None):
        self.hong = hong
        self.viec = []
        self.dong = None

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.shutdown(wait=True)
        return False

    def submit(self, fn, cong_viec):
        import threading
        from concurrent.futures import Future

        tl = Future()
        self.viec.append((cong_viec, tl))
        if not self.hong:
            tl.set_result(0)
        elif len(self.viec) == 1:
            tl.set_exception(RuntimeError("hỏng"))
        else:
            threading.Timer(3.0, lambda: tl.cancelled() or tl.done() or tl.set_result(0)).start()
        return tl

    def shutdown(self, wait=True, cancel_futures=False):
        self.dong = (wait, cancel_futures)


class ParallelBookkeepingTest(unittest.TestCase):
    """Không cần Chromium: thay ProcessPoolExecutor bằng bản giả để xem việc gửi đi và cách dừng."""

    def chay(self, hong):
        cac_du, so_khung = ba_canh_ngan()
        pool = _PoolGia(hong)
        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch.object(chup, "ProcessPoolExecutor", lambda max_workers: pool):
            try:
                chup.chup_song_song(cac_du, {}, so_khung, lich.FPS, Path(tmp), 3)
            except chup.MediaError as exc:
                return pool, exc, cac_du, so_khung
        return pool, None, cac_du, so_khung

    def test_first_failure_cancels_the_ranges_still_waiting(self):
        import time

        dau = time.monotonic()
        pool, loi, _, _ = self.chay(hong=True)
        self.assertLess(time.monotonic() - dau, 2.0, "không chờ các dải còn lại chạy xong")
        self.assertEqual(len(pool.viec), 3)
        self.assertTrue(all(tl.cancelled() for _v, tl in pool.viec[1:]))
        self.assertIsNotNone(loi)
        self.assertEqual(loi.step, "dung")
        self.assertIn("cảnh 1", loi.message)
        self.assertEqual(pool.dong[0], True, "vẫn chờ các tiến trình đang chạy trước khi dọn")

    def test_each_worker_gets_only_its_scenes_and_the_one_before(self):
        pool, loi, cac_du, so_khung = self.chay(hong=False)
        self.assertIsNone(loi)
        khung_dau = [0, so_khung[0], so_khung[0] + so_khung[1]]
        for (a, b), (v, _tl) in zip(chup.chia_dai(so_khung, 3), pool.viec):
            with self.subTest(dai=(a, b)):
                lo = max(a - 1, 0)
                self.assertEqual([du["so"] for du in v["cac_du"]], [du["so"] for du in cac_du[lo:b]])
                self.assertEqual((v["dau"], v["cuoi"]), (a - lo, b - lo))
                self.assertEqual(v["khung_dau"], khung_dau[lo:b], "số thứ tự khung giữ nguyên")
                self.assertEqual(v["so_khung"], so_khung[lo:b])


def _chup_canh_day_dia(page, html, so_khung, fps, thu_muc, so_dau, ghi_log=None):
    raise OSError(28, "No space left on device")


def _dia_day(cong_viec):
    """Thay `_chup_dai_con` trong tiến trình con: chạy `chup_dai` thật, trình duyệt giả, ổ đĩa đầy khi ghi khung."""
    with mock.patch.object(chup, "trinh_duyet", CaptureBookkeepingTest.trinh_duyet_gia), \
            mock.patch.object(chup, "chup_canh", _chup_canh_day_dia), \
            mock.patch.object(trang, "dung_trang", lambda du, model=None: "<html></html>"):
        return chup._chup_dai_con(cong_viec)


class CaptureBookkeepingTest(unittest.TestCase):
    """Không cần Chromium: thay trình duyệt và bước chụp bằng bản giả ghi PNG nhỏ."""

    @staticmethod
    @contextlib.contextmanager
    def trinh_duyet_gia():
        yield mock.MagicMock()

    @staticmethod
    def chup_canh_gia(page, html, so_khung, fps, thu_muc, so_dau, ghi_log=None):
        thu_muc.mkdir(parents=True, exist_ok=True)
        for i in range(so_khung):
            (thu_muc / f"f{so_dau + i:06d}.jpg").write_bytes(png(4, 4))
        return so_dau + so_khung

    def test_background_of_a_finished_scene_is_released(self):
        cac_du, so_khung = ba_canh_ngan()
        khung_dau = [0, so_khung[0], so_khung[0] + so_khung[1]]
        da_dung = []

        def dung_trang_gia(du, model=None):
            da_dung.append(du)
            return "<html></html>"

        viec = {"cac_du": cac_du, "models_js": {}, "dau": 0, "cuoi": 3, "khung_dau": khung_dau,
                "so_khung": so_khung, "fps": lich.FPS}
        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch.object(chup, "trinh_duyet", self.trinh_duyet_gia), \
                mock.patch.object(chup, "chup_canh", self.chup_canh_gia), \
                mock.patch.object(trang, "dung_trang", dung_trang_gia), \
                contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(chup.chup_dai({**viec, "thu_muc_anh": tmp}), sum(so_khung))
        self.assertEqual(len(da_dung), 3)
        self.assertEqual([du["so"] for du in da_dung], [1, 2, 3])
        self.assertTrue(all(du.get("nenTruoc") is None for du in da_dung),
                        "nền data: của cảnh đã chụp xong phải được bỏ, không giữ trong bộ nhớ")

    def test_disk_error_while_writing_frames_is_a_write_error(self):
        cac_du, so_khung = ba_canh_ngan()
        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch.object(chup, "trinh_duyet", self.trinh_duyet_gia), \
                mock.patch.object(chup, "chup_canh", _chup_canh_day_dia), \
                mock.patch.object(trang, "dung_trang", lambda du, model=None: "<html></html>"), \
                contextlib.redirect_stderr(io.StringIO()), \
                self.assertRaises(chup.MediaError) as caught:
            chup.chup_song_song(cac_du, {}, so_khung, lich.FPS, Path(tmp), 1)
        self.assertEqual(caught.exception.step, "write")
        self.assertIn("ổ đĩa", caught.exception.fix)
        self.assertIn("No space left", caught.exception.message)

    def test_missing_scene_file_is_still_a_dung_error(self):
        # Đọc file mã cảnh (OSError) không phải lỗi ghi khung: vẫn là `dung`.
        cac_du, so_khung = ba_canh_ngan()
        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch.object(chup, "trinh_duyet", self.trinh_duyet_gia), \
                mock.patch.object(trang, "dung_trang", side_effect=FileNotFoundError(2, "no such file")), \
                contextlib.redirect_stderr(io.StringIO()), \
                self.assertRaises(chup.MediaError) as caught:
            chup.chup_song_song(cac_du, {}, so_khung, lich.FPS, Path(tmp), 1)
        self.assertEqual(caught.exception.step, "dung")

    def test_chromium_failure_in_a_child_process_is_a_chromium_error(self):
        cac_du, so_khung = ba_canh_ngan()
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(chup, "_chup_dai_con", _khong_mo_duoc_chromium), \
                self.assertRaises(chup.MediaError) as caught:
            chup.chup_song_song(cac_du, {}, so_khung, lich.FPS, Path(tmp), 2)
        self.assertEqual(caught.exception.step, "chromium")
        self.assertIn("pptmaster.ps1", caught.exception.fix)
        self.assertIn("Không mở được Chromium", caught.exception.message)

    def test_disk_error_in_a_child_process_is_a_write_error(self):
        cac_du, so_khung = ba_canh_ngan()
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(chup, "_chup_dai_con", _dia_day), \
                self.assertRaises(chup.MediaError) as caught:
            chup.chup_song_song(cac_du, {}, so_khung, lich.FPS, Path(tmp), 2)
        self.assertEqual(caught.exception.step, "write")
        self.assertIn("ổ đĩa", caught.exception.fix)


class ChromiumMissingTest(unittest.TestCase):
    def test_missing_playwright_is_a_chromium_error(self):
        import builtins
        real_import = builtins.__import__

        def no_pw(name, *args, **kwargs):
            if name.startswith("playwright"):
                raise ImportError("no playwright")
            return real_import(name, *args, **kwargs)

        builtins.__import__ = no_pw
        try:
            with self.assertRaises(chup.MediaError) as caught:
                with chup.trinh_duyet():
                    pass
        finally:
            builtins.__import__ = real_import
        self.assertEqual(caught.exception.step, "chromium")
        self.assertIn("pptmaster.ps1", caught.exception.fix)


if __name__ == "__main__":
    unittest.main()

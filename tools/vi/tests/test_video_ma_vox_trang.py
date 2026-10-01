"""Trang cảnh Vox trong Chromium (runtime/vox.js, vox.css): khung tất định, vật hiện đúng nhịp, đo tràn, khổ xuất,
chuyển lia trên ảnh cảnh trước, sự kiện âm thanh."""
import base64
import io
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tests.test_video_ma_chup import NEED_CHROMIUM, co_chromium  # noqa: E402
from video_ma_parts import chup, lich, parse, trang, vox  # noqa: E402
from video_ma_parts.kho import Kho  # noqa: E402


def png(rong: int, cao: int, mau=(200, 80, 40, 255)) -> str:
    from PIL import Image, ImageDraw
    im = Image.new("RGBA", (rong, cao), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([8, 8, rong - 8, cao - 8], radius=30, fill=(250, 246, 236, 255))
    d.ellipse([24, 24, rong - 24, cao - 24], fill=mau)
    buf = io.BytesIO()
    im.save(buf, "PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def anh(kieu: str, rong=400, cao=300, nguon=None) -> dict:
    return {"dataUrl": png(rong, cao), "rong": rong, "cao": cao, "kieu": kieu, "nguon": nguon, "moHinh": None}


LOI = "Một hai ba bốn năm sáu bảy tám chín mười."
CHU40 = "Tiền nhiều lên nhưng hàng hoá vẫn vậy nhé"[:40]
NHAN30 = "Siêu lạm phát ở nước Đức xưa!"[:30]
DAU16 = "KHÔNG ĐƯỢC ĐÂU!!"[:16]
THE = "Lạm phát năm một chín hai | 1.000.000.000 % | Giá bánh mì tăng gấp tỉ lần chỉ trong vòng một năm ở Đức"
THE = " | ".join([THE.split(" | ")[0][:24], THE.split(" | ")[1][:16], THE.split(" | ")[2][:60]])


def du_vox(nhip: list, bo_cuc: str, kho: str = "ngang", anh_tn=None, so: int = 1, thoi_luong_loi: str = LOI):
    md = (f"---\ntieu-de: T\nphong-cach: vox\nkho: {kho}\n---\n\n## Cảnh 1\nbo-cuc: {bo_cuc}\n"
          f"loi: {thoi_luong_loi}\n" + "".join(f"nhip: {n}\n" for n in nhip))
    v = parse.parse(md)
    c = v.canh[0]
    moc = [{"t": lich.DAN_DAU + i * 0.5, "d": 0.5, "chu": w, "khoa": lich.khoa_so_khop(w)} for i, w in enumerate(c.loi.split())]
    plan, _ = lich.dung_lich([c], [lich.GiongInfo(None, 8.0, [0.0], False, "may", moc_tu=moc)])
    du = vox.du_lieu_canh(c, plan[0], {"anh": anh_tn or {}}, v.meta)
    du["so"] = du["hat"] = so  # cảnh sau (chuyển cảnh) mà không phải dựng cả video
    return du


# Cảnh mẫu của mọi bố cục, chữ dài đúng giới hạn.
def cac_canh_mau(kho: str) -> list:
    tren, duoi = ("trai", "phai") if kho == "ngang" else ("tren", "duoi")
    return [
        ("mot", [f"@dau | anh: ve: cốc | giua", f"hai | nhan: {NHAN30} | tren", f"ba | chu: {CHU40} | duoi"],
         {0: anh("cat")}),
        ("hai-ben", [f"@dau | anh: ve: cốc | {tren}", f"hai | the: {THE} | {duoi}", "ba | dau: VS | giua",
                     f"bốn | mui-ten: {tren} -> {duoi}"], {0: anh("khung", 300, 400, "Ảnh: Wikimedia Commons (CC0)")}),
        ("dan-hang", [f"@dau | the: {THE} | 1", f"hai | chu: {CHU40} | 2", f"ba | nhan: {NHAN30} | 3",
                      "bốn | so: {{1250.5}} triệu đồng mỗi | 4"], {}),
        ("chong", ["@dau | anh: ve: cốc", f"hai | chu: {CHU40}", f"ba | the: {THE}", f"bốn | nhan: {NHAN30}",
                   f"năm | dau: {DAU16}"], {0: anh("cat")}),
        ("toan-canh", ["@dau | anh: ve: phố | nen", f"hai | chu: {CHU40} | giua", f"ba | dau: {DAU16} | duoi"],
         {0: anh("phu", 800, 500, "Ảnh: Basile Morin (PD)")}),
    ]


@unittest.skipUnless(co_chromium(), NEED_CHROMIUM)
class VoxTrangTest(unittest.TestCase):
    def test_same_time_same_bytes(self):
        du = du_vox(["@dau | anh: ve: cốc | giua", "hai | chu: Hai | duoi"], "mot", anh_tn={0: anh("cat")})
        with chup.trang_chup(Kho("ngang", 720)) as page:
            chup.mo_trang(page, trang.dung_trang(du))
            page.evaluate("() => window.datThoiDiem(2.0)")
            a = chup._anh_khung(page)
            page.evaluate("() => window.datThoiDiem(3.1)")
            page.evaluate("() => window.datThoiDiem(2.0)")
            b = chup._anh_khung(page)
        self.assertEqual(a, b)

    def test_frame_does_not_depend_on_render_history(self):
        # Khung là hàm thuần của t: trang mới nhảy thẳng tới t và trang đã vẽ các khung trước đó phải ra cùng byte.
        # Hỏng khi lớp giữ tỉ lệ raster cũ (will-change: transform), hay khi lớp đổi tỉ lệ liên tục (chữ, ảnh, bộ lọc
        # vẽ qua bộ đệm dựng từ tỉ lệ của khung trước). Khung cuối cảnh là ảnh nền chuyển cảnh của cảnh sau, dựng lại
        # bằng cách nhảy thẳng trong tiến trình khác, nên cũng phải đúng từng byte.
        canh = [
            du_vox(["@dau | anh: ve: cốc | giua", "hai | nhan: Hai | tren", "ba | chu: Ba chữ | duoi"], "mot",
                   anh_tn={0: anh("cat")}),
            du_vox(["@dau | anh: ve: phố | nen", f"hai | chu: {CHU40} | giua", f"ba | dau: {DAU16} | duoi"], "toan-canh",
                   anh_tn={0: anh("phu", 800, 500)}),
        ]
        for du in canh:
            html = trang.dung_trang(du)
            fps = lich.FPS
            n_cuoi = round((du["thoiLuong"] - 1 / fps) * fps)
            with self.subTest(bo_cuc=du["boCuc"]):
                with chup.trang_chup(Kho("ngang", 720)) as page:
                    chup.mo_trang(page, html)
                    page.evaluate("() => window.datThoiDiem(3.2)")
                    thang_32 = chup._anh_khung(page)
                    page.evaluate("(t) => window.datThoiDiem(t)", n_cuoi / fps)
                    thang_cuoi = chup._anh_khung(page)
                with chup.trang_chup(Kho("ngang", 720)) as page:
                    chup.mo_trang(page, html)
                    for t in (0.0, 1.0, 2.0, 3.0, 3.2):
                        page.evaluate("(t) => window.datThoiDiem(t)", t)
                        noi_32 = chup._anh_khung(page)
                self.assertEqual(thang_32, noi_32, "0, 1, 2, 3 rồi 3,2")
                with chup.trang_chup(Kho("ngang", 720)) as page:
                    chup.mo_trang(page, html)
                    for i in range(n_cuoi + 1):
                        page.evaluate("(t) => window.datThoiDiem(t)", i / fps)
                        noi_cuoi = chup._anh_khung(page)
                self.assertEqual(thang_cuoi, noi_cuoi, "mọi khung từ 0 tới khung cuối")

    def test_object_hidden_before_its_beat_and_visible_after(self):
        du = du_vox(["@dau | nhan: Mở đầu | tren", "ba | chu: Hai dòng chữ | giua"], "mot")
        bd = du["nhip"][1]["batDau"]
        self.assertGreater(bd, 1.5)
        with chup.trinh_duyet() as b:
            page = chup.trang_moi(b, Kho("ngang", 720))
            chup.mo_trang(page, trang.dung_trang(du))
            sel = "document.querySelector('[data-id=nhip-1]')"
            page.evaluate("(t) => window.datThoiDiem(t)", bd - 0.1)
            self.assertEqual(page.evaluate(f"() => getComputedStyle({sel}).visibility"), "hidden")
            page.evaluate("(t) => window.datThoiDiem(t)", bd + 1.0)
            self.assertEqual(page.evaluate(f"() => getComputedStyle({sel}).visibility"), "visible")
            r = page.evaluate(f"() => {{ const r = {sel}.querySelector('.noi').getBoundingClientRect(); "
                              "return [r.left, r.top, r.right, r.bottom]; }")
        o = vox_o("ngang", "vox-mot-giua")
        tol = 0.05 * o["w"]  # camera đã đẩy vào nhẹ và xoay ±4°
        self.assertGreater(r[0], o["x"] - tol)
        self.assertGreater(r[1], o["y"] - tol)
        self.assertLess(r[2], o["x"] + o["w"] + tol)
        self.assertLess(r[3], o["y"] + o["h"] + tol)

    def test_no_overflow_for_the_example_scenes(self):
        with chup.trinh_duyet() as b:
            for kho in ("ngang", "doc"):
                page = chup.trang_moi(b, Kho(kho, 720))
                for bo_cuc, nhip, tn in cac_canh_mau(kho):
                    with self.subTest(kho=kho, bo_cuc=bo_cuc):
                        du = du_vox(nhip, bo_cuc, kho, tn)
                        self.assertEqual(chup.kiem_tran(page, trang.dung_trang(du)), [])
                page.close()

    def test_overflowing_text_is_reported(self):
        du = du_vox(["@dau | chu: " + "W" * 40 + " | 1"], "dan-hang", "doc")
        with chup.trinh_duyet() as b:
            page = chup.trang_moi(b, Kho("doc", 720))
            self.assertIn("nhip-0", chup.kiem_tran(page, trang.dung_trang(du)))

    def test_overlapping_images_are_reported(self):
        # Ảnh rộng 2:1 ở `giua` đè lên ảnh ở `trai` hơn 30 % ảnh nhỏ: hai ảnh chồng thật, phải báo.
        du = du_vox(["@dau | anh: ve: cốc | trai", "hai | anh: ve: bánh | giua"], "hai-ben",
                    anh_tn={0: anh("cat", 400, 300), 1: anh("cat", 600, 300)})
        with chup.trinh_duyet() as b:
            page = chup.trang_moi(b, Kho("ngang", 720))
            self.assertIn("chong:nhip-0,nhip-1", chup.kiem_tran(page, trang.dung_trang(du)))

    def test_stamp_between_two_cutouts_is_not_an_overlap(self):
        # Mẫu của hướng dẫn: hai ảnh cắt nền 1,5:1 hai bên, con dấu "IM LẶNG" ở `giua`. Dấu, nhãn được phép đè ảnh.
        for vat in ("dau: IM LẶNG", "nhan: Im lặng"):
            du = du_vox(["@dau | anh: ve: cốc | trai", "hai | anh: ve: bánh | phai", f"ba | {vat} | giua"], "hai-ben",
                        anh_tn={0: anh("cat", 600, 400), 1: anh("cat", 600, 400)})
            with self.subTest(vat=vat), chup.trinh_duyet() as b:
                page = chup.trang_moi(b, Kho("ngang", 720))
                tran = chup.kiem_tran(page, trang.dung_trang(du))
                self.assertFalse([m for m in tran if m.startswith("chong:")], tran)

    def test_text_items_overlapping_each_other_are_still_reported(self):
        du = du_vox([f"@dau | chu: {CHU40} | trai", f"hai | dau: {DAU16} | giua"], "hai-ben")
        with chup.trinh_duyet() as b:
            page = chup.trang_moi(b, Kho("ngang", 720))
            self.assertIn("chong:nhip-0,nhip-1", chup.kiem_tran(page, trang.dung_trang(du)))

    def test_full_hd_frame_size(self):
        from PIL import Image
        for ten, kich in (("ngang", (1920, 1080)), ("doc", (1080, 1920))):
            du = du_vox(["@dau | chu: Xin chào | giua"], "mot", ten)
            with chup.trang_chup(Kho(ten, 1080)) as page:
                chup.mo_trang(page, trang.dung_trang(du))
                page.evaluate("() => window.datThoiDiem(1.5)")
                with Image.open(io.BytesIO(chup._anh_khung(page))) as im:
                    self.assertEqual(im.size, kich)

    def test_lia_transition_uses_previous_frame(self):
        from PIL import Image
        du = du_vox(["@dau | chu: Cảnh hai | giua"], "mot", so=2)
        du["co"]["chuyen"] = "lia"
        buf = io.BytesIO()
        Image.new("RGB", (1280, 720), (255, 0, 0)).save(buf, "PNG")
        du["nenTruoc"] = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")

        def do_cot(im):
            rgb = im.convert("RGB")
            return sum(1 for y in range(0, 720, 8)
                       for (r, g, b_) in [rgb.getpixel((640, y))] if r > 200 and g < 60 and b_ < 60)
        with chup.trang_chup(Kho("ngang", 720)) as page:
            chup.mo_trang(page, trang.dung_trang(du))
            page.evaluate("() => window.datThoiDiem(0.1)")
            dau = Image.open(io.BytesIO(chup._anh_khung(page)))
            page.evaluate("() => window.datThoiDiem(0.4)")
            sau = Image.open(io.BytesIO(chup._anh_khung(page)))
        self.assertGreater(do_cot(dau), 0)
        self.assertEqual(do_cot(sau), 0)

    def test_torn_paper_transition_reveals_the_new_scene_from_the_left(self):
        from PIL import Image
        du = du_vox(["@dau | chu: Cảnh hai | giua"], "mot", so=2)
        du["co"]["chuyen"] = "xe-giay"
        buf = io.BytesIO()
        Image.new("RGB", (1280, 720), (255, 0, 0)).save(buf, "PNG")
        du["nenTruoc"] = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")

        def do(im, x):
            r, g, b_ = im.convert("RGB").getpixel((x, 360))
            return r > 200 and g < 60 and b_ < 60
        with chup.trang_chup(Kho("ngang", 720)) as page:
            chup.mo_trang(page, trang.dung_trang(du))
            page.evaluate("() => window.datThoiDiem(0.12)")
            giua = Image.open(io.BytesIO(chup._anh_khung(page)))
            page.evaluate("() => window.datThoiDiem(0.4)")
            sau = Image.open(io.BytesIO(chup._anh_khung(page)))
        self.assertFalse(do(giua, 60), "mép trái đã xé lộ cảnh mới")
        self.assertTrue(do(giua, 1220), "mép phải còn cảnh trước")
        self.assertFalse(do(sau, 1220))

    def test_sound_events(self):
        du = du_vox(["@dau | anh: ve: cốc | giua", "hai | nhan: Hai | tren", "ba | dau: XONG | duoi"], "mot", so=2,
                    anh_tn={0: anh("cat")})
        du["co"]["chuyen"] = "xe-giay"
        with chup.trinh_duyet() as b:
            page = chup.trang_moi(b, Kho("ngang", 720))
            chup.mo_trang(page, trang.dung_trang(du))
            sk = chup.doc_su_kien(page)
        self.assertEqual([e for e in sk if e["loai"] == "chuyen"], [{"t": 0, "loai": "chuyen", "dai": 0.35}])
        khac = [e for e in sk if e["loai"] != "chuyen"]
        self.assertEqual(len(khac), 3)
        self.assertEqual([e["loai"] for e in khac], ["nhan", "ting", "nhan"])
        self.assertAlmostEqual(khac[0]["t"], du["nhip"][0]["batDau"] + 0.45)

    def test_vox_page_after_an_old_style_page_in_the_same_tab(self):
        # page.set_content giữ window: THI_VIDEO của khung-video.js (đã `san`) không được làm trang Vox dựng sai.
        from PIL import Image
        from tests.test_video_ma_chup import du_cua
        cu, _ = du_cua("loai: tieu-de\nchu: Xin chào\n")
        du = du_vox(["@dau | chu: Xin chào | giua"], "mot")
        with chup.trang_chup(Kho("ngang", 720)) as page:
            chup.mo_trang(page, trang.dung_trang(cu))
            chup.mo_trang(page, trang.dung_trang(du))
            self.assertTrue(page.evaluate("() => !!document.querySelector('.vox .vat-chu')"))
            page.evaluate("() => window.datThoiDiem(3.0)")
            lo, hi = Image.open(io.BytesIO(chup._anh_khung(page))).convert("L").getextrema()
        self.assertGreater(hi - lo, 100)

    def test_page_is_self_contained_and_skips_the_old_runtime(self):
        html = trang.dung_trang(du_vox(["@dau | chu: A | giua"], "mot"))
        self.assertNotIn("https://", html)
        self.assertNotIn("http://", html.replace("http://www.w3.org/2000/svg", ""))
        self.assertIn("THI_VOX", html)
        self.assertNotIn("THI_CANH", html)
        self.assertNotIn("'Itim', sans-serif", html)  # viet-tay.css không nạp


def vox_o(kho: str, ten: str) -> dict:
    from video_ma_parts import kho as kho_py
    return kho_py.o(kho, ten)


if __name__ == "__main__":
    unittest.main()

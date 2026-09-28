"""Kế hoạch ảnh AI (`anh_ai.py ke-hoach`): thứ tự mục, câu cấm chữ, tham chiếu tư thế, ổn định, lỗi parse."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS_VI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_VI))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import anh_ai  # noqa: E402
from anh_ai_parts import cau_lenh, xu_ly  # noqa: E402
from test_video_ma_anh import jpeg, png  # noqa: E402
from video_ma_parts import anh, parse  # noqa: E402

VIDEO_MD = """---
tieu-de: Vì sao giá tăng
mon: KTPL
lop: 11
nhan-vat: ve: cô giáo trẻ, áo dài xanh
---

## Cảnh 1
loai: ke-chuyen
tieu-de: Mở đầu câu chuyện
nen: ve: cánh đồng lúa chín buổi sáng
tu-the: chao
loi: Xin chào các em.

## Cảnh 2
loai: ke-chuyen
tieu-de: Nhắc lại khung cảnh
nen: nhu-canh 1
tu-the: giai-thich
loi: Chúng ta cùng xem lại.

## Cảnh 3
loai: ke-chuyen
tieu-de: Chuyển sang thành phố
nen: ve: khu chợ đông người buổi sáng
loi: Bây giờ ta sang cảnh khác.
"""


def viet_video_md(thu_muc: Path, text: str = VIDEO_MD) -> Path:
    thu_muc.mkdir(parents=True, exist_ok=True)
    (thu_muc / "video.md").write_text(text, encoding="utf-8")
    return thu_muc


class LapKeHoachTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.thu_muc = viet_video_md(Path(self.tmp.name) / "bai")

    def test_sau_muc_dung_thu_tu(self):
        warnings: list = []
        kq = anh_ai.chay_ke_hoach(self.thu_muc, warnings)
        self.assertEqual(kq["so_anh"], 6)
        ke_hoach = json.loads((self.thu_muc / "anh" / "ai" / "ke-hoach.json").read_text(encoding="utf-8"))
        muc = ke_hoach["muc"]
        self.assertEqual(len(muc), 6)
        self.assertEqual(
            [(m["loai"], m["file"]) for m in muc],
            [
                ("nhan-vat-mau", "nhan-vat-mau.png"),
                ("tu-the", "tu-the-dung.png"),
                ("tu-the", "tu-the-chao.png"),
                ("tu-the", "tu-the-giai-thich.png"),
                ("nen", "nen-1.png"),
                ("nen", "nen-3.png"),
            ],
        )
        # Cảnh 2 dùng lại nền của Cảnh 1 (`nhu-canh 1`): cùng mục nền-1, không tạo mục riêng.
        nen1 = next(m for m in muc if m["file"] == "nen-1.png")
        self.assertEqual(nen1["canh"], [1, 2])
        nen3 = next(m for m in muc if m["file"] == "nen-3.png")
        self.assertEqual(nen3["canh"], [3])

    def test_moi_prompt_chua_cau_cam(self):
        warnings: list = []
        anh_ai.chay_ke_hoach(self.thu_muc, warnings)
        ke_hoach = json.loads((self.thu_muc / "anh" / "ai" / "ke-hoach.json").read_text(encoding="utf-8"))
        for muc in ke_hoach["muc"]:
            self.assertIn(cau_lenh.CAM, muc["prompt"], muc)

    def test_muc_tu_the_co_tham_chieu(self):
        warnings: list = []
        anh_ai.chay_ke_hoach(self.thu_muc, warnings)
        ke_hoach = json.loads((self.thu_muc / "anh" / "ai" / "ke-hoach.json").read_text(encoding="utf-8"))
        for muc in ke_hoach["muc"]:
            if muc["loai"] == "tu-the":
                self.assertEqual(muc["tham_chieu"], "goc/nhan-vat-mau.png")
            else:
                self.assertIsNone(muc["tham_chieu"])

    def test_muc_tu_the_co_cau_phong_cach_va_mo_ta(self):
        # R9: câu lệnh tư thế cũng phải có câu phong cách và mô tả nhân vật (nguyên văn), không chỉ tư thế + câu cấm.
        warnings: list = []
        anh_ai.chay_ke_hoach(self.thu_muc, warnings)
        ke_hoach = json.loads((self.thu_muc / "anh" / "ai" / "ke-hoach.json").read_text(encoding="utf-8"))
        mo_ta = "cô giáo trẻ, áo dài xanh"
        for muc in ke_hoach["muc"]:
            if muc["loai"] != "tu-the":
                continue
            self.assertIn(cau_lenh.PHONG_CACH_ANH[ke_hoach["phong_cach"]], muc["prompt"], muc)
            self.assertIn(mo_ta, muc["prompt"], muc)
            self.assertIn("pure green (#00FF00) background", muc["prompt"], muc)
            self.assertIn(cau_lenh.CAM, muc["prompt"], muc)

    def test_chay_hai_lan_ra_cung_byte(self):
        warnings: list = []
        anh_ai.chay_ke_hoach(self.thu_muc, warnings)
        a = (self.thu_muc / "anh" / "ai" / "ke-hoach.json").read_bytes()
        warnings2: list = []
        anh_ai.chay_ke_hoach(self.thu_muc, warnings2)
        b = (self.thu_muc / "anh" / "ai" / "ke-hoach.json").read_bytes()
        self.assertEqual(a, b)

    def test_khong_co_anh_ve_thi_bao_khong_dung_anh_ai(self):
        thu_muc = viet_video_md(Path(self.tmp.name) / "khong-ai", "---\ntieu-de: Bài không AI\nmon: KTPL\nlop: 11\n---\n\n"
                                 "## Cảnh 1\nloai: khai-niem\nthuat-ngu: Lạm phát\ndinh-nghia: Mức giá chung tăng.\n"
                                 "loi: Xin chào các em.\n")
        warnings: list = []
        kq = anh_ai.chay_ke_hoach(thu_muc, warnings)
        self.assertEqual(kq["so_anh"], 0)
        self.assertIn(anh_ai.KHONG_AI, warnings)

    def test_video_md_loi_bao_step_parse(self):
        thu_muc = viet_video_md(Path(self.tmp.name) / "loi", "---\ntieu-de: Thiếu môn\nlop: 11\n---\n\n## Cảnh 1\n")
        with self.assertRaises(parse.ParseError):
            anh_ai.chay_ke_hoach(thu_muc, [])


class CliTest(unittest.TestCase):
    def test_video_md_loi_in_error_step_parse(self):
        with tempfile.TemporaryDirectory() as tmp:
            thu_muc = viet_video_md(Path(tmp) / "loi", "---\ntieu-de: Thiếu môn\nlop: 11\n---\n\n## Cảnh 1\n")
            proc = subprocess.run([sys.executable, str(TOOLS_VI / "anh_ai.py"), str(thu_muc), "ke-hoach"],
                                  capture_output=True, text=True, encoding="utf-8", timeout=60)
            out = json.loads(proc.stdout)
            self.assertFalse(out["ready"])
            self.assertEqual(out["error"]["step"], "parse")


def _alpha(rong: int, cao: int, hop=None, gia_tri: int = 255, nen: int = 0) -> bytearray:
    """Kênh alpha thô (một byte một điểm): nền `nen`, hình chữ nhật `hop` = (x, y, w, h) đặc `gia_tri`."""
    raw = bytearray([nen]) * (rong * cao)
    if hop:
        x, y, w, h = hop
        for yy in range(y, y + h):
            raw[yy * rong + x:yy * rong + x + w] = bytes([gia_tri]) * w
    return raw


class DoAlphaTest(unittest.TestCase):
    """xu_ly.do_alpha / kiem_alpha: góc 8×8 trong suốt, phần đục 5–70 %, hộp cắt sát."""

    def test_hinh_sach_qua_va_hop_sat(self):
        do = xu_ly.do_alpha(bytes(_alpha(100, 200, (20, 30, 50, 100))), 100, 200)
        self.assertEqual(do["hop"], (20, 30, 50, 100))
        self.assertAlmostEqual(do["duc"], 0.25)
        self.assertEqual(do["goc"], [0, 0, 0, 0])
        self.assertIsNone(xu_ly.kiem_alpha(do))

    def test_goc_con_duc_la_loi(self):
        raw = _alpha(100, 200, (20, 30, 50, 100))
        for yy in range(8):
            raw[yy * 100 + 92:yy * 100 + 100] = b"\xff" * 8  # góc phải trên đục
        ly_do = xu_ly.kiem_alpha(xu_ly.do_alpha(bytes(raw), 100, 200))
        self.assertIn("góc phải trên", ly_do)

    def test_phan_duc_ngoai_5_70_phan_tram(self):
        it = xu_ly.do_alpha(bytes(_alpha(100, 200, (40, 40, 10, 10))), 100, 200)  # 0,5 %
        self.assertIn("quá ít", xu_ly.kiem_alpha(it))
        nhieu = xu_ly.do_alpha(bytes(_alpha(100, 200, (8, 8, 84, 184))), 100, 200)  # ~77 %
        self.assertIn("quá nhiều", xu_ly.kiem_alpha(nhieu))

    def test_mo_nhat_khong_mo_rong_hop(self):
        raw = _alpha(100, 200, (20, 30, 50, 100))
        raw[199 * 100 + 50] = 10  # nhiễu rất mờ ở đáy ảnh không tính vào hộp cắt
        self.assertEqual(xu_ly.do_alpha(bytes(raw), 100, 200)["hop"], (20, 30, 50, 100))


class LyDoTachNenTest(unittest.TestCase):
    def test_mau_goc_va_ly_do_theo_mau(self):
        w, h = 16, 16
        rgba = bytearray(bytes([0x4C, 0xAF, 0x50, 255]) * (w * h))
        for y in range(8):  # góc phải dưới tối
            for x in range(8, 16):
                rgba[((8 + y) * w + x) * 4:((8 + y) * w + x) * 4 + 3] = b"   "
        mau = xu_ly.mau_goc(bytes(rgba), w, h)
        self.assertEqual(mau, [(0x4C, 0xAF, 0x50)] * 3 + [(0x20, 0x20, 0x20)])
        ly_do = xu_ly.kiem_alpha({"goc": [255, 0, 0, 255], "duc": 0.3, "hop": (0, 0, 1, 1)}, mau)
        self.assertIn("góc trái trên còn đục: nền không phải xanh thuần #00FF00 (đo được #4CAF50)", ly_do)
        self.assertIn("góc phải dưới còn đục: còn bóng hoặc viền ở góc (đo được #202020)", ly_do)
        self.assertNotIn("phải trên", ly_do)

    def test_co_nho_canh_dai_1536_khong_phong_to(self):
        self.assertEqual(xu_ly.co_nho(2000, 3000), (1024, 1536))
        self.assertEqual(xu_ly.co_nho(3000, 1000), (1536, 512))
        self.assertEqual(xu_ly.co_nho(500, 600), (500, 600))
        self.assertEqual(xu_ly.co_nho(500, 600, 0.5), (250, 300))


class LenhNenTest(unittest.TestCase):
    def test_anh_lon_phu_va_cat_giua_dung_full_hd(self):
        loc, ra, thieu = xu_ly.loc_nen(2400, 1350, 1920, 1080)
        self.assertEqual(ra, (1920, 1080))
        self.assertFalse(thieu)
        self.assertIn("scale=1920:1080:force_original_aspect_ratio=increase", loc)
        self.assertIn("crop=1920:1080", loc)

    def test_anh_vuong_nho_khong_phong_to(self):
        loc, ra, thieu = xu_ly.loc_nen(1024, 1024, 1920, 1080)
        self.assertEqual(ra, (1024, 576))
        self.assertTrue(thieu)
        self.assertNotIn("scale", loc)
        loc, ra, thieu = xu_ly.loc_nen(1024, 1024, 1080, 1920)
        self.assertEqual(ra, (576, 1024))
        self.assertTrue(thieu)


class RunGia:
    """Lệnh giả thay subprocess.run: ffprobe trả kích thước, alphaextract trả kênh alpha, lệnh ghi ảnh tạo file nhỏ."""

    def __init__(self, kich_thuoc: dict, alpha=None):
        self.kich_thuoc = kich_thuoc  # tên file gốc -> (rộng, cao)
        self.alpha = alpha or {}      # tên file gốc -> bytes alpha
        self.hong: set = set()        # tên file gốc mà FFmpeg "không đọc được"
        self.lenh = []

    def __call__(self, cmd, **kw):
        self.lenh.append(cmd)
        vao = Path(cmd[cmd.index("-i") + 1]) if "-i" in cmd else Path(cmd[-1])
        if cmd[0] == "ffprobe":
            w, h = self.kich_thuoc[vao.name]
            return subprocess.CompletedProcess(cmd, 0, f"{w}x{h}\n", "")
        if "rawvideo" in cmd and "rgba" in cmd:  # ảnh gốc RGBA: nền xanh đục (chưa trong suốt)
            if vao.name in self.hong:
                return subprocess.CompletedProcess(cmd, 1, b"", b"Invalid data found")
            w, h = self.kich_thuoc[vao.name]
            return subprocess.CompletedProcess(cmd, 0, bytes([0, 255, 0, 255]) * (w * h), b"")
        if "rawvideo" in cmd:
            return subprocess.CompletedProcess(cmd, 0, self.alpha[vao.name], b"")
        if vao.name in self.hong:
            return subprocess.CompletedProcess(cmd, 1, "", "Invalid data found")
        ra = Path(cmd[-1])
        if ra.suffix == ".png":
            png(ra, 4, 4, kieu=6)
        else:
            jpeg(ra, 1920, 1080)
        return subprocess.CompletedProcess(cmd, 0, "", "")


def _co_ffmpeg(ten):
    return "C:/ffmpeg/" + ten


class NhanTest(unittest.TestCase):
    """chay_nhan với lệnh giả: tìm file gốc, lỗi thiếu gộp một lần, tên đầu ra, nguon.json đọc được bởi anh.doc."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.thu_muc = viet_video_md(Path(self.tmp.name) / "bai")
        anh_ai.chay_ke_hoach(self.thu_muc, [])
        self.goc = self.thu_muc / "anh" / "ai" / "goc"
        self.goc.mkdir(parents=True, exist_ok=True)
        self.ke_hoach = json.loads((self.thu_muc / "anh" / "ai" / "ke-hoach.json").read_text(encoding="utf-8"))

    def dat_du(self, bo=()):
        kich, alpha = {}, {}
        for muc in self.ke_hoach["muc"]:
            if muc["file"] in bo:
                continue
            ten = muc["file"]
            if muc["loai"] == "nen":
                ten = ten[:-4] + ".jpg"  # AI lưu JPEG dù kế hoạch ghi .png
                kich[ten] = (2400, 1350)
            else:
                kich[ten] = (100, 200)
                alpha[ten] = bytes(_alpha(100, 200, (20, 30, 50, 100)))
            (self.goc / ten).write_bytes(b"x")
        return RunGia(kich, alpha)

    def test_thieu_hai_file_mot_loi_liet_ke_ca_hai(self):
        run = self.dat_du(bo=("tu-the-chao.png", "nen-3.png"))
        with self.assertRaises(xu_ly.XuLyError) as caught:
            anh_ai.chay_nhan(self.thu_muc, [], run=run, which=_co_ffmpeg)
        self.assertEqual(caught.exception.step, "thieu")
        self.assertIn("goc/tu-the-chao.png", caught.exception.message)
        self.assertIn("goc/nen-3.png", caught.exception.message)
        self.assertIn("2 ảnh", caught.exception.message)
        self.assertEqual(run.lenh, [])

    def test_tim_goc_nhan_duoi_khac(self):
        (self.goc / "nen-1.webp").write_bytes(b"x")
        self.assertEqual(xu_ly.tim_goc(self.goc, "nen-1.png"), self.goc / "nen-1.webp")
        (self.goc / "nen-1.png").write_bytes(b"x")
        self.assertEqual(xu_ly.tim_goc(self.goc, "nen-1.png"), self.goc / "nen-1.png")
        self.assertIsNone(xu_ly.tim_goc(self.goc, "nen-9.png"))

    def test_khong_co_ffmpeg(self):
        run = self.dat_du()
        with self.assertRaises(xu_ly.XuLyError) as caught:
            anh_ai.chay_nhan(self.thu_muc, [], run=run, which=lambda ten: None)
        self.assertEqual(caught.exception.step, "ffmpeg")
        self.assertIn("docs/vi/cai-dat-bang-ai.md", caught.exception.fix)

    def test_du_file_ghi_dau_ra_va_nguon_doc_duoc(self):
        run = self.dat_du()
        warnings: list = []
        kq = anh_ai.chay_nhan(self.thu_muc, warnings, cong_cu="Antigravity", mo_hinh="Nano Banana", run=run,
                              which=_co_ffmpeg, hom_nay="2026-09-28")
        ai = self.thu_muc / "anh" / "ai"
        mong = ["nhan-vat-mau.png", "tu-the-dung.png", "tu-the-chao.png", "tu-the-giai-thich.png", "nen-1.jpg", "nen-3.jpg"]
        self.assertEqual(kq["files"], [f"anh/ai/{f}" for f in mong] + ["anh/ai/nguon.json"])
        self.assertEqual(kq["so_anh"], 6)
        for f in mong:
            self.assertTrue((ai / f).is_file(), f)
        self.assertEqual(sorted(p.name for p in ai.iterdir() if ".tam" in p.name), [])
        nguon = json.loads((ai / "nguon.json").read_text(encoding="utf-8"))
        self.assertEqual([m["file"] for m in nguon], mong)
        muc = nguon[mong.index("nen-1.jpg")]
        self.assertEqual((muc["cong_cu"], muc["mo_hinh"], muc["ngay"]), ("Antigravity", "Nano Banana", "2026-09-28"))
        self.assertIn(cau_lenh.CAM, muc["prompt"])
        # Đọc lại được bởi bộ dựng (Task 10).
        self.assertEqual(anh.doc(self.thu_muc, "ai/nen-1.jpg", None)["moHinh"], "Nano Banana")
        self.assertTrue(anh.doc(self.thu_muc, "ai/tu-the-chao.png", None)["alpha"])
        # Nhân vật: lệnh cắt dùng đúng bộ lọc tách nền và hộp alpha.
        cat = [c for c in run.lenh if c[0] == "ffmpeg" and "rawvideo" not in c and str(c[-1]).endswith(".png")][0]
        self.assertIn(xu_ly.LOC_TACH + ",crop=50:100:20:30", cat[cat.index("-vf") + 1])

    def test_mac_dinh_cong_cu_mo_hinh_va_giu_ban_ghi_cu(self):
        ai = self.thu_muc / "anh" / "ai"
        (ai / "nguon.json").write_text(json.dumps([{"file": "khac.png", "mo_hinh": "Cũ"},
                                                   {"file": "nen-1.jpg", "mo_hinh": "Cũ"}]), encoding="utf-8")
        anh_ai.chay_nhan(self.thu_muc, [], run=self.dat_du(), which=_co_ffmpeg)
        nguon = json.loads((ai / "nguon.json").read_text(encoding="utf-8"))
        self.assertEqual(nguon[0], {"file": "khac.png", "mo_hinh": "Cũ"})
        moi = [m for m in nguon if m["file"] == "nen-1.jpg"]
        self.assertEqual(len(moi), 1)
        self.assertEqual((moi[0]["cong_cu"], moi[0]["mo_hinh"]), ("công cụ vẽ của nền tảng", "AI"))
        self.assertRegex(moi[0]["ngay"], r"^\d{4}-\d{2}-\d{2}$")

    def test_tach_nen_hong_la_loi_tach_nen_neu_file(self):
        run = self.dat_du()
        run.alpha["tu-the-chao.png"] = bytes(_alpha(100, 200, (0, 0, 100, 200)))  # không tách được gì
        with self.assertRaises(xu_ly.XuLyError) as caught:
            anh_ai.chay_nhan(self.thu_muc, [], run=run, which=_co_ffmpeg)
        self.assertEqual(caught.exception.step, "tach-nen")
        self.assertIn("goc/tu-the-chao.png", caught.exception.message)
        self.assertIn("#00FF00", caught.exception.fix)

    def test_loi_mot_muc_van_ghi_nguon_muc_xong_va_xoa_dau_ra_cu(self):
        ai = self.thu_muc / "anh" / "ai"
        anh_ai.chay_nhan(self.thu_muc, [], mo_hinh="Cũ", run=self.dat_du(), which=_co_ffmpeg)
        self.assertTrue((ai / "tu-the-chao.png").is_file())
        run = self.dat_du()
        run.alpha["tu-the-chao.png"] = bytes(_alpha(100, 200, (0, 0, 100, 200)))
        with self.assertRaises(xu_ly.XuLyError) as caught:
            anh_ai.chay_nhan(self.thu_muc, [], mo_hinh="Mới", run=run, which=_co_ffmpeg)
        self.assertEqual(caught.exception.step, "tach-nen")
        self.assertFalse((ai / "tu-the-chao.png").exists())  # không dùng nhầm ảnh cũ
        nguon = {m["file"]: m["mo_hinh"] for m in json.loads((ai / "nguon.json").read_text(encoding="utf-8"))}
        self.assertNotIn("tu-the-chao.png", nguon)
        self.assertEqual(nguon["nen-3.jpg"], "Mới")  # mục sau mục lỗi vẫn được nhận và ghi nguồn
        self.assertEqual(nguon["tu-the-dung.png"], "Mới")

    def test_loi_ffmpeg_dung_lai_nhung_ghi_nguon_da_xong(self):
        ai = self.thu_muc / "anh" / "ai"
        anh_ai.chay_nhan(self.thu_muc, [], mo_hinh="Cũ", run=self.dat_du(), which=_co_ffmpeg)
        run = self.dat_du()
        run.hong.add("nen-1.jpg")
        with self.assertRaises(xu_ly.XuLyError) as caught:
            anh_ai.chay_nhan(self.thu_muc, [], mo_hinh="Mới", run=run, which=_co_ffmpeg)
        self.assertEqual(caught.exception.step, "ffmpeg")
        self.assertFalse((ai / "nen-1.jpg").exists())
        nguon = {m["file"]: m["mo_hinh"] for m in json.loads((ai / "nguon.json").read_text(encoding="utf-8"))}
        self.assertNotIn("nen-1.jpg", nguon)
        self.assertEqual(nguon["tu-the-giai-thich.png"], "Mới")  # xong trước mục lỗi
        self.assertEqual(nguon["nen-3.jpg"], "Cũ")  # chưa tới lượt: giữ bản ghi và file cũ
        self.assertTrue((ai / "nen-3.jpg").is_file())

    def test_nguon_cu_hong_thi_cat_va_canh_bao(self):
        ai = self.thu_muc / "anh" / "ai"
        for cu in ("{hỏng", '{"items": []}'):
            with self.subTest(cu=cu):
                (ai / "nguon.json").write_text(cu, encoding="utf-8")
                warnings: list = []
                anh_ai.chay_nhan(self.thu_muc, warnings, run=self.dat_du(), which=_co_ffmpeg)
                self.assertTrue(any("nguon.hong.json" in w for w in warnings), warnings)
                self.assertEqual((ai / "nguon.hong.json").read_text(encoding="utf-8"), cu)
                self.assertEqual(len(json.loads((ai / "nguon.json").read_text(encoding="utf-8"))), 6)

    def test_ke_hoach_muc_sai_la_loi_input(self):
        duong_dan = self.thu_muc / "anh" / "ai" / "ke-hoach.json"
        for sua in ({"file": None}, {"loai": "khac"}, {"canh": []}, {"prompt": 3}, {"file": "../x.png"}):
            with self.subTest(sua=sua):
                ke = json.loads(json.dumps(self.ke_hoach))
                nen = next(m for m in ke["muc"] if m["loai"] == "nen")
                nen.update(sua)
                duong_dan.write_text(json.dumps(ke), encoding="utf-8")
                with self.assertRaises(xu_ly.XuLyError) as caught:
                    anh_ai.chay_nhan(self.thu_muc, [], run=self.dat_du(), which=_co_ffmpeg)
                self.assertEqual(caught.exception.step, "input")
                self.assertIn("ke-hoach", caught.exception.fix)
        ke = json.loads(json.dumps(self.ke_hoach))
        del ke["muc"][0]["prompt"]
        duong_dan.write_text(json.dumps(ke), encoding="utf-8")
        with self.assertRaises(xu_ly.XuLyError) as caught:
            anh_ai.chay_nhan(self.thu_muc, [], run=self.dat_du(), which=_co_ffmpeg)
        self.assertIn("mục thứ 1", caught.exception.message)

    def test_chua_co_ke_hoach(self):
        (self.thu_muc / "anh" / "ai" / "ke-hoach.json").unlink()
        with self.assertRaises(xu_ly.XuLyError) as caught:
            anh_ai.chay_nhan(self.thu_muc, [], run=RunGia({}), which=_co_ffmpeg)
        self.assertEqual(caught.exception.step, "input")
        self.assertIn("ke-hoach", caught.exception.fix)


class CliNhanTest(unittest.TestCase):
    def test_nhan_thieu_file_in_error_thieu(self):
        with tempfile.TemporaryDirectory() as tmp:
            thu_muc = viet_video_md(Path(tmp) / "bai")
            anh_ai.chay_ke_hoach(thu_muc, [])
            proc = subprocess.run([sys.executable, str(TOOLS_VI / "anh_ai.py"), str(thu_muc), "nhan",
                                   "--cong-cu", "Codex", "--mo-hinh", "GPT Image 1"],
                                  capture_output=True, text=True, encoding="utf-8", timeout=60)
            out = json.loads(proc.stdout)
            self.assertFalse(out["ready"])
            self.assertEqual(out["error"]["step"], "thieu")
            self.assertEqual(set(out), {"ready", "files", "so_anh", "ke_hoach", "warnings", "error"})


if __name__ == "__main__":
    unittest.main()

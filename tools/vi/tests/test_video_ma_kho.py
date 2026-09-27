"""Test đối tượng khổ (kho.py): kích thước, dữ liệu cho trang, chụp Full HD và khổ dọc.

Phần Chromium/FFmpeg tự bỏ qua nếu máy thiếu. Ảnh tham chiếu vi.11 ở tests/data/tham-chieu-vi11/ được chụp
bằng mã vi.11 chưa sửa (khung cuối mỗi cảnh, `--xem-truoc`, 1280×720)."""

import contextlib
import io
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

import so_anh  # noqa: E402
import video_ma  # noqa: E402
from video_ma_parts import chup, ghep, kho, lich, parse, trang  # noqa: E402
from video_parts import media  # noqa: E402

META = "tieu-de: T\nmon: Toán\nlop: 8\n"
FIXTURES = TOOLS_VI / "fixtures"
THAM_CHIEU = Path(__file__).resolve().parent / "data" / "tham-chieu-vi11"
CO_CHROMIUM = video_ma.co_chromium()
CO_CA_HAI = CO_CHROMIUM and video_ma.co_ffmpeg()


class KhoTest(unittest.TestCase):
    def test_kich_thuoc_theo_kho_va_do_phan_giai(self):
        for ten, dpg, css, xuat, ti_le in (
            ("ngang", 1080, (1280, 720), (1920, 1080), 1.5),
            ("doc", 1080, (720, 1280), (1080, 1920), 1.5),
            ("ngang", 720, (1280, 720), (1280, 720), 1.0),
            ("doc", 720, (720, 1280), (720, 1280), 1.0),
        ):
            with self.subTest(ten=ten, dpg=dpg):
                k = kho.Kho(ten, dpg)
                self.assertEqual((k.rong, k.cao), css)
                self.assertEqual((k.rong_xuat, k.cao_xuat), xuat)
                self.assertEqual(k.ti_le, ti_le)

    def test_day_va_tam(self):
        ngang, doc = kho.Kho("ngang", 1080), kho.Kho("doc", 1080)
        self.assertEqual(ngang.day, 620)
        self.assertEqual(ngang.tam, (640, 310))
        self.assertEqual(doc.day, 1080)
        self.assertEqual(doc.tam, (360, 540))

    def test_bat_bien_va_gia_tri_la(self):
        k = kho.Kho("ngang", 1080)
        with self.assertRaises(Exception):
            k.rong = 5  # type: ignore[misc]
        with self.assertRaises(ValueError):
            kho.Kho("vuong", 1080)
        with self.assertRaises(ValueError):
            kho.Kho("ngang", 480)

    def test_tu_meta(self):
        self.assertEqual(kho.tu_meta({}), kho.Kho("ngang", 1080))
        self.assertEqual(kho.tu_meta({"kho": "doc", "do-phan-giai": "720"}), kho.Kho("doc", 720))
        video = parse.parse(f"---\n{META}kho: doc\n---\n\n## Cảnh 1\nloai: tieu-de\nchu: A\nloi: Xin chào.\n")
        self.assertEqual(kho.tu_meta(video.meta), kho.Kho("doc", 1080))

    def test_du_lieu_cho_trang(self):
        self.assertEqual(kho.Kho("ngang", 720).du_lieu(),
                         {"ten": "ngang", "rong": 1280, "cao": 720, "day": 620, "tamX": 640, "tamY": 310})
        self.assertEqual(kho.Kho("doc", 1080).du_lieu(),
                         {"ten": "doc", "rong": 720, "cao": 1280, "day": 1080, "tamX": 360, "tamY": 540})


def du_mot_canh(meta_them: str = "", noi_dung: str = "loai: tieu-de\nchu: Xin chào\n"):
    video = parse.parse(f"---\n{META}{meta_them}---\n\n## Cảnh 1\n{noi_dung}loi: Xin chào các em.\n")
    giong = lich.GiongInfo(mp3=None, giay=2.0, moc_cau=[0.0], uoc_luong=False, nguon="may")
    plan, _ = lich.dung_lich(video.canh, [giong])
    return lich.du_lieu_canh(video.canh[0], plan[0], None, {"meta": video.meta}), plan


class DuLieuTrangTest(unittest.TestCase):
    def test_du_lieu_canh_mang_kho(self):
        du, _ = du_mot_canh("kho: doc\n")
        self.assertEqual(du["kho"], kho.Kho("doc", 1080).du_lieu())
        du, _ = du_mot_canh()
        self.assertEqual(du["kho"]["ten"], "ngang")

    def test_trang_nap_kho_dau_tien_va_dat_bien_css(self):
        du, _ = du_mot_canh("kho: doc\n")
        html = trang.dung_trang(du)
        self.assertIn("--rong: 720px", html)
        self.assertIn("--cao: 1280px", html)
        self.assertLess(html.index("root.THI_KHO ="), html.index("root.THI_VIDEO ="))
        self.assertLess(html.index("THI_KHO.dat("), html.index("THI_VIDEO.khoiDong("))

    def test_css_khong_con_kich_thuoc_cung(self):
        css = (TOOLS_VI / "video_ma_parts" / "runtime" / "viet-tay.css").read_text(encoding="utf-8")
        self.assertNotIn("1280px", css)
        self.assertNotIn("720px", css)
        # Dòng nguồn nhạc nền đặt theo vạch phụ đề của khổ (biến --day do trang đặt), không theo số cứng 108px.
        self.assertNotIn("108px", css)
        self.assertIn("var(--day)", css)

    def test_trang_dat_bien_day(self):
        du, _ = du_mot_canh("kho: doc\n")
        self.assertIn("--day: 1080px", trang.dung_trang(du))
        du, _ = du_mot_canh()
        self.assertIn("--day: 620px", trang.dung_trang(du))


RUNTIME = TOOLS_VI / "video_ma_parts" / "runtime"
# Số nguyên ≥ 200 còn được phép trong runtime/canh/*.js: (file, số) -> lý do. Mọi toạ độ khác lấy từ ô bố cục.
SO_LON_DUOC_PHEP = {
    ("bieu-do.js", 200): "ngưỡng bề rộng một cột (px) để chọn cỡ nhãn, không phải vị trí",
    ("bieu-do.js", 360): "số độ của một vòng tròn khi chia lát",
    ("bieu-do.js", 220): "ô tên trục đứng hẹp hơn ô biểu đồ 220 (khoảng lùi tính từ ô)",
    ("bieu-do.js", 340): "ô tên trục ngang hẹp hơn ô biểu đồ 340 (khoảng lùi tính từ ô)",
    ("do-thi.js", 1000): "làm tròn nhãn số tới 3 chữ số thập phân",
    ("so-do.js", 215): "góc (độ) của nhánh theo số nhánh",
    ("so-do.js", 220): "góc (độ) của nhánh theo số nhánh",
    ("so-do.js", 240): "góc (độ) của nhánh theo số nhánh",
    ("so-do.js", 372): "cung (độ) của nét elip tâm, vẽ chồng mép 12°",
    ("so-do.js", 330): "bề rộng ô nhánh (kích thước; vị trí tính từ ô so-do)",
    ("khai-niem.js", 460): "độ dài nét gạch dưới thuật ngữ khi có cột phụ (kích thước)",
    ("khai-niem.js", 600): "độ dài nét gạch dưới thuật ngữ (kích thước)",
    ("tieu-de.js", 600): "độ dài nét gạch dưới tiêu đề, đặt giữa ô bia (kích thước)",
    ("tieu-de.js", 300): "khổ dọc: chiều cao ô tiêu đề dưới hình (kích thước)",
    ("cong-thuc.js", 300): "khổ dọc: chiều cao khung biểu thức (kích thước)",
    ("cau-hoi.js", 230): "khổ dọc: chiều cao ô câu hỏi (kích thước)",
    ("so-do.js", 210): "góc (độ) của nhánh khổ dọc",
}


def so_nguyen_lon(ma: str) -> list:
    """Các số nguyên ≥ 200 trong mã JS, bỏ chú thích và chuỗi (số thập phân như 0.575 không tính)."""
    import re
    ma = re.sub(r"/\*.*?\*/", " ", ma, flags=re.S)
    ma = re.sub(r"'(?:\\.|[^'\\\n])*'|\"(?:\\.|[^\"\\\n])*\"", "''", ma)
    ma = re.sub(r"//[^\n]*", " ", ma)
    return [int(m) for m in re.findall(r"(?<![\w.])\d+(?![\w.])", ma) if int(m) >= 200]


class OBoCucTest(unittest.TestCase):
    def test_bang_o_python_la_file_json_chung(self):
        bang = json.loads((RUNTIME / "o-bo-cuc.json").read_text(encoding="utf-8"))
        self.assertEqual(kho.O, bang)
        self.assertEqual(kho.o("ngang", "cot-phu"), {"x": 900, "y": 200, "w": 320, "h": 380})
        self.assertEqual(kho.o("ngang", "anh-lon"), {"x": 80, "y": 70, "w": 1120, "h": 490})
        with self.assertRaises(ValueError) as bat:
            kho.o("ngang", "cot-phai-khong-co")
        self.assertIn("cot-phai-khong-co", str(bat.exception))
        o = kho.o("ngang", "cot-phu")
        o["x"] = 0
        self.assertEqual(kho.o("ngang", "cot-phu")["x"], 900)

    def test_kho_doc_co_bang_rieng_va_kho_la_la_loi(self):
        self.assertEqual(set(kho.O), {"ngang", "doc"})
        self.assertEqual(set(kho.O["doc"]), set(kho.O["ngang"]))
        self.assertEqual(kho.o("doc", "cot-phu"), {"x": 160, "y": 640, "w": 400, "h": 380})
        for ten in kho.O["doc"]:
            self.assertEqual(kho.o("doc", ten), kho.O["doc"][ten])
        with self.assertRaises(ValueError) as bat:
            kho.o("vuong", "tieu-de")
        self.assertIn("vuong", str(bat.exception))

    def test_trang_nhung_bang_o_truoc_kho_js(self):
        du, _ = du_mot_canh()
        html = trang.dung_trang(du)
        dau = html.index("window.THI_O_BO_CUC = ") + len("window.THI_O_BO_CUC = ")
        self.assertEqual(json.loads(html[dau:html.index(";\n", dau)]), kho.O)
        self.assertLess(dau, html.index("root.THI_KHO ="))
        # kho.js không giữ bản sao của bảng: một nguồn duy nhất là o-bo-cuc.json.
        self.assertNotIn("1120", (RUNTIME / "kho.js").read_text(encoding="utf-8"))

    def test_canh_khong_con_toa_do_cung(self):
        con = {}
        for f in sorted((RUNTIME / "canh").glob("*.js")):
            for so in so_nguyen_lon(f.read_text(encoding="utf-8")):
                if (f.name, so) not in SO_LON_DUOC_PHEP:
                    con.setdefault(f.name, []).append(so)
        self.assertEqual(con, {}, "số nguyên ≥ 200 dùng làm toạ độ: lấy từ V.o(tên ô)")

    def test_ngoai_le_con_dung_va_co_ly_do(self):
        for (ten, so), ly_do in SO_LON_DUOC_PHEP.items():
            with self.subTest(file=ten, so=so):
                self.assertTrue(ly_do.strip())
                self.assertIn(so, so_nguyen_lon((RUNTIME / "canh" / ten).read_text(encoding="utf-8")))

    def test_bo_loc_so(self):
        self.assertEqual(so_nguyen_lon("a(640, 0.575, 1e3) // 900\n'2000' /* 300 */ x.y2000 250"), [640, 250])


class GhepKhoTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.thu_muc = Path(tmp.name) / "bai"
        (self.thu_muc / ".khung" / "anh").mkdir(parents=True)
        _, self.plan = du_mot_canh()
        self.giong = [lich.GiongInfo(mp3=self.thu_muc / "g1.mp3", giay=2.0, moc_cau=[], uoc_luong=False, nguon="may")]

    def ghep(self, k, kich_thuoc: str):
        calls = []

        def run(cmd, **kw):
            calls.append(cmd)
            if cmd[0] == "ffprobe":
                return subprocess.CompletedProcess(cmd, 0, kich_thuoc + "\n", "")
            if cmd[-1].endswith("video.mp4"):
                (Path(kw["cwd"]) / cmd[-1]).write_bytes(b"mp4")
            return subprocess.CompletedProcess(cmd, 0, "", "")
        ghep.ghep_video(self.thu_muc, self.plan, self.giong, "karaoke", run=run, kho=k)
        return calls

    def test_karaoke_theo_diem_css_va_khong_co_gian(self):
        calls = self.ghep(kho.Kho("doc", 1080), "1080x1920")
        ass = (self.thu_muc / ".khung" / "phu-de.ass").read_text(encoding="utf-8")
        self.assertIn("PlayResX: 720", ass)
        self.assertIn("PlayResY: 1280", ass)
        video = calls[-1]
        self.assertFalse(any("scale" in str(x) for x in video), video)

    def test_kiem_kich_thuoc_khung_dau(self):
        calls = self.ghep(kho.Kho("ngang", 1080), "1920x1080")
        probe = [c for c in calls if c[0] == "ffprobe"]
        self.assertEqual(len(probe), 1)
        self.assertTrue(str(probe[0][-1]).replace("\\", "/").endswith(".khung/anh/f000000.jpg"), probe[0])

    def test_khung_sai_kich_thuoc_la_loi_dung(self):
        with self.assertRaises(media.MediaError) as bat:
            self.ghep(kho.Kho("ngang", 1080), "1280x720")
        self.assertEqual(bat.exception.step, "dung")
        self.assertIn("1920", str(bat.exception))


def chay_xem_truoc(thu_muc: Path) -> dict:
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
        video_ma.main([str(thu_muc), "--xem-truoc"])
    return json.loads(out.getvalue().strip().splitlines()[-1])


def chen_meta(md: Path, dong: str) -> None:
    text = md.read_text(encoding="utf-8")
    dau = text.index("---", 3)
    md.write_text(text[:dau] + dong + text[dau:], encoding="utf-8")


@unittest.skipUnless(CO_CHROMIUM, "máy không có Chromium hoặc playwright")
class ChupKhoTest(unittest.TestCase):
    # video_ma tự mở Playwright riêng, nên trình duyệt của test chỉ mở sau khi dựng xong (không lồng hai vòng).
    def test_720_giong_anh_tham_chieu_vi11(self):
        with tempfile.TemporaryDirectory() as tmp:
            cap = []
            for ten in ("video-mau", "video-hinh"):
                thu_muc = Path(tmp) / ten
                shutil.copytree(FIXTURES / ten, thu_muc)
                chen_meta(thu_muc / "video.md", "do-phan-giai: 720\n")
                data = chay_xem_truoc(thu_muc)
                self.assertTrue(data["ready"], data)
                cap += [(ten, Path(f).stem, thu_muc / f) for f in data["files"]]
            self.assertEqual(len(cap), len(list(THAM_CHIEU.glob("*.png"))))
            with chup.trinh_duyet() as browser:
                page = chup.trang_moi(browser)
                for ten, so, moi in cap:
                    with self.subTest(fixture=ten, canh=so):
                        self.assertEqual(so_anh.kich_thuoc_png(moi), (1280, 720))
                        self.assertLessEqual(so_anh.ti_le_lech(page, moi, THAM_CHIEU / f"{ten}-{so}.png"), 0.005)

    def test_1080_xem_truoc_ra_full_hd(self):
        with tempfile.TemporaryDirectory() as tmp:
            thu_muc = Path(tmp) / "bai"
            thu_muc.mkdir()
            (thu_muc / "video.md").write_text(f"---\n{META}---\n\n## Cảnh 1\nloai: tieu-de\nchu: Con lắc đơn\nloi: Xin chào.\n",
                                              encoding="utf-8")
            data = chay_xem_truoc(thu_muc)
            self.assertTrue(data["ready"], data)
            self.assertEqual(so_anh.kich_thuoc_png(thu_muc / data["files"][0]), (1920, 1080))

    def test_kho_doc_chup_1080x1920(self):
        du, _ = du_mot_canh("kho: doc\n", "loai: tieu-de\nchu: Con lắc\n")
        with chup.trinh_duyet() as browser, tempfile.TemporaryDirectory() as tmp:
            page = chup.trang_moi(browser, kho.Kho("doc", 1080))
            png = Path(tmp) / "doc.png"
            chup.chup_cuoi(page, trang.dung_trang(du), png)
            self.assertEqual(so_anh.kich_thuoc_png(png), (1080, 1920))
            self.assertEqual(page.evaluate("() => [window.THI_VIDEO.kho.rong, window.THI_VIDEO.kho.cao]"), [720, 1280])


@unittest.skipUnless(CO_CA_HAI, "máy thiếu Chromium/playwright hoặc FFmpeg/ffprobe")
class VideoDocTest(unittest.TestCase):
    def test_video_doc_1080x1920_30fps(self):
        k = kho.Kho("doc", 1080)
        du, plan = du_mot_canh("kho: doc\nphu-de: karaoke\n", "loai: tieu-de\nchu: Con lắc\n")
        with tempfile.TemporaryDirectory() as tmp:
            thu_muc = Path(tmp) / "bai doc"
            anh = thu_muc / ".khung" / "anh"
            anh.mkdir(parents=True)
            mp3 = thu_muc / "giong" / "canh-1.mp3"
            mp3.parent.mkdir()
            subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "lavfi", "-i",
                            "sine=frequency=440:duration=2", "-q:a", "9", str(mp3)], check=True, timeout=60)
            chup.chup_song_song([du], {}, [plan[0].so_khung], lich.FPS, anh, 1, kho=k)
            giong = [lich.GiongInfo(mp3=mp3, giay=2.0, moc_cau=[], uoc_luong=False, nguon="co-san")]
            ghep.ghep_video(thu_muc, plan, giong, "karaoke", kho=k)
            out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                  "stream=width,height,r_frame_rate", "-of", "json", str(thu_muc / "video.mp4")],
                                 capture_output=True, text=True, check=True, timeout=60).stdout
            s = json.loads(out)["streams"][0]
            self.assertEqual((s["width"], s["height"], s["r_frame_rate"]), (1080, 1920, "30/1"))


if __name__ == "__main__":
    unittest.main()

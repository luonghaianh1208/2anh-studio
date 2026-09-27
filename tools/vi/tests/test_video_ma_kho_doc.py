"""Khổ dọc 9:16: mọi loại cảnh ở đúng giới hạn khổ dọc (kiem.LIMITS_DOC) nằm gọn trong 720×1280 và trên vạch
phụ đề (y 1080). Chuỗi thử có nhiều dấu: "Nghiêng nghiễm nhiên " lặp, cắt đúng độ dài.

Phần Chromium/FFmpeg tự bỏ qua nếu máy thiếu."""

import contextlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

TOOLS_VI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_VI))

import video_ma  # noqa: E402
from video_ma_parts import chup, hinh, kho, kiem, lich, parse  # noqa: E402

CO_CHROMIUM = video_ma.co_chromium()
CO_CA_HAI = CO_CHROMIUM and video_ma.co_ffmpeg()
ANH_MAU = TOOLS_VI / "fixtures" / "video-hinh" / "anh" / "con-lac.png"
CUM = "Nghiêng nghiễm nhiên "
META_DOC = "tieu-de: Khổ dọc\nmon: Vật lí\nlop: 11\nkho: doc\n"


def chuoi(n: int) -> str:
    """Chuỗi thử đúng `n` ký tự; ký tự cuối là khoảng trắng thì thay bằng chữ để parse không cắt mất."""
    s = (CUM * (n // len(CUM) + 1))[:n]
    return s[:-1] + "n" if s.endswith(" ") else s


def canh_toi_da(gioi_han: dict | None = None, hai_phan: dict | None = None, cot: bool = False) -> list:
    """Các cảnh (loại, nội dung markdown) với mọi trường chữ ở đúng giới hạn và số dòng lặp tối đa.
    `cot`: thêm hình vào các loại có cột phụ (và sơ đồ có hình ở tâm)."""
    L = dict(kiem.LIMITS_DOC if gioi_han is None else gioi_han)
    H = dict(kiem.LIMITS_HAI_PHAN_DOC if hai_phan is None else hai_phan)

    def t(loai, truong):
        return chuoi(L[(loai, truong)])

    hinh_cot = "hinh: clock\n" if cot else ""
    moc_nhan, moc_ta = H[("dong-thoi-gian", "moc")]
    nhan_du_lieu, so_du_lieu = H[("bieu-do", "du-lieu")]
    so_du_lieu = so_du_lieu or parse.SO_DAI
    ds = [
        ("tieu-de", f"chu: {t('tieu-de', 'chu')}\nphu: {t('tieu-de', 'phu')}\n{hinh_cot}"),
        ("khai-niem", f"thuat-ngu: {t('khai-niem', 'thuat-ngu')}\ndinh-nghia: {t('khai-niem', 'dinh-nghia')}\n{hinh_cot}"),
        ("cong-thuc", f"bieu-thuc: {t('cong-thuc', 'bieu-thuc')}\n"
                      + "".join(f"giai-thich: {t('cong-thuc', 'giai-thich')}\n" for _ in range(4)) + hinh_cot),
        ("y-tung-y", f"tieu-de: {t('y-tung-y', 'tieu-de')}\n" + "".join(f"y: {t('y-tung-y', 'y')}\n" for _ in range(6)) + hinh_cot),
        ("quy-trinh", f"tieu-de: {t('quy-trinh', 'tieu-de')}\n" + "".join(f"buoc: {t('quy-trinh', 'buoc')}\n" for _ in range(5))),
        ("so-sanh", f"tieu-de: {t('so-sanh', 'tieu-de')}\ntrai: {t('so-sanh', 'trai')}\nphai: {t('so-sanh', 'phai')}\n"
                    + "".join(f"y-trai: {t('so-sanh', 'y-trai')}\n" for _ in range(4))
                    + "".join(f"y-phai: {t('so-sanh', 'y-phai')}\n" for _ in range(4))),
        ("do-thi", f"tieu-de: {t('do-thi', 'tieu-de')}\ntruc-ngang: {t('do-thi', 'truc-ngang')}\n"
                   f"truc-doc: {t('do-thi', 'truc-doc')}\n" + "".join(f"diem: {k}, {k * k % 7}\n" for k in range(12))),
        ("thi-nghiem", "mau: li-con-lac-don\ntham-so: 0 chieu-dai 0.4\ntham-so: 4 g 24.8\ntham-so: 6 goc-lech 15\n"
                       "do: chu-ki, thoi-gian-10-dao-dong\n"),
        ("minh-hoa", f"tieu-de: {t('minh-hoa', 'tieu-de')}\n"
                     + "".join(f"hinh: {ten} | {chuoi(hinh.NHAN_TOI_DA)}\n" for ten in ("stopwatch", "ruler-measure", "weight"))),
        ("anh", f"anh: con-lac.png\nchu-thich: {t('anh', 'chu-thich')}\nnguon: Hình vẽ minh hoạ · PPT Master bản Việt · CC0 1.0\n"),
    ]
    for kieu in ("cot", "duong", "tron"):
        truc = "" if kieu == "tron" else (f"don-vi: {t('bieu-do', 'don-vi')}\ntruc-ngang: {t('bieu-do', 'truc-ngang')}\n"
                                          f"truc-doc: {t('bieu-do', 'truc-doc')}\n")
        # Số dài nhất được phép: số dương (tròn) hoặc âm (cột, đường), có phần thập phân.
        so = ("98765432109"[:so_du_lieu - 2] + ".5") if kieu == "tron" else ("-" + "8765432109"[:so_du_lieu - 3] + ".5")
        ds.append(("bieu-do", f"tieu-de: {t('bieu-do', 'tieu-de')}\nkieu: {kieu}\n{truc}"
                              + "".join(f"du-lieu: {chuoi(nhan_du_lieu)} | {so if k % 2 else '12'}\n" for k in range(8))))
    ds += [
        ("so-do", f"trung-tam: {t('so-do', 'trung-tam')}\n" + "".join(f"nhanh: {t('so-do', 'nhanh')}\n" for _ in range(6))
                  + hinh_cot),
        ("dong-thoi-gian", f"tieu-de: {t('dong-thoi-gian', 'tieu-de')}\n"
                           + "".join(f"moc: {chuoi(moc_nhan)} | {chuoi(moc_ta)}\n" for _ in range(6))),
        ("dong-thoi-gian", f"tieu-de: {t('dong-thoi-gian', 'tieu-de')}\n"
                           + "".join(f"moc: {chuoi(moc_nhan)} | {chuoi(moc_ta)}\n" for _ in range(3))),
        ("cau-hoi", f"cau-hoi: {t('cau-hoi', 'cau-hoi')}\n" + "".join(f"lua-chon: {t('cau-hoi', 'lua-chon')}\n" for _ in range(4))
                    + f"dap-an: C\ngiai-thich: {t('cau-hoi', 'giai-thich')}\nloi-giai: Vì vậy.\n"),
        ("cau-hoi", f"cau-hoi: {t('cau-hoi', 'cau-hoi')}\n" + "".join(f"lua-chon: {t('cau-hoi', 'lua-chon')}\n" for _ in range(3))
                    + f"dap-an: C\ngiai-thich: {t('cau-hoi', 'giai-thich')}\nloi-giai: Vì vậy.\n"),
    ]
    return ds


def video_md(ds: list, meta: str = META_DOC) -> str:
    return f"---\n{meta}---\n\n" + "".join(f"## Cảnh {k}\nloai: {loai}\n{noi}loi: Xin chào các em.\n\n"
                                           for k, (loai, noi) in enumerate(ds, 1))


def thu_muc_bai(goc: Path, text: str) -> Path:
    thu_muc = goc / "bai"
    (thu_muc / "anh").mkdir(parents=True)
    shutil.copyfile(ANH_MAU, thu_muc / "anh" / "con-lac.png")
    (thu_muc / "video.md").write_text(text, encoding="utf-8")
    return thu_muc


# Mọi phần tử vẽ trong lớp bảng (trừ bàn tay) và dòng nguồn nhạc: [nhãn, trái, trên, phải, dưới] theo điểm CSS,
# đo sau kiemTran() (trạng thái cuối, máy quay Z = 1). Nét SVG đo bằng getBoundingClientRect (không tính độ dày nét).
DO_HOP = """() => {
  const kq = [];
  const them = (ten, r) => { if (r.width > 0 || r.height > 0) { kq.push([ten, r.left, r.top, r.right, r.bottom]); } };
  const bang = document.getElementById('bang');
  bang.querySelectorAll('.chu').forEach((el) => them('chu:' + el.getAttribute('data-id'), el.getBoundingClientRect()));
  bang.querySelectorAll('svg.ve > *').forEach((el, i) => {
    if (getComputedStyle(el).opacity === '0' || el.style.opacity === '0') { return; }
    them('svg:' + (el.getAttribute('class') || el.tagName) + ':' + i, el.getBoundingClientRect());
  });
  bang.querySelectorAll('.anh, .anh .nguon, canvas').forEach((el) => them('khoi:' + el.className + (el.id || ''), el.getBoundingClientRect()));
  const nn = document.getElementById('nhac-nguon');
  if (nn) { them('nhac-nguon', nn.getBoundingClientRect()); }
  return kq;
}"""


def ngoai_vung(page, html: str) -> tuple:
    """(kiemTran(), phần tử ra ngoài 720×1280 hoặc có đáy > 1080; cho phép lệch 1 px)."""
    tran = chup.kiem_tran(page, html)
    k = kho.Kho("doc", 1080)
    ra = [h for h in page.evaluate(DO_HOP)
          if h[1] < -1 or h[2] < -1 or h[3] > k.rong + 1 or h[4] > k.day + 1]
    return tran, ra


@unittest.skipUnless(CO_CHROMIUM, "máy không có Chromium hoặc playwright")
class KhoDocGioiHanTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.cm = chup.trinh_duyet()
        cls.browser = cls.cm.__enter__()
        cls.page = chup.trang_moi(cls.browser, kho.Kho("doc", 720))

    @classmethod
    def tearDownClass(cls):
        cls.cm.__exit__(None, None, None)
        cls.tmp.cleanup()

    def dung(self, ds: list, ten: str, nhac: dict | None = None) -> list:
        thu_muc = thu_muc_bai(Path(self.tmp.name) / ten, video_md(ds))
        video = parse.parse((thu_muc / "video.md").read_text(encoding="utf-8"))
        self.assertEqual(kiem.kiem(video, thu_muc), [])
        return list(zip(video.canh, video_ma._trang_tam(video, thu_muc, video_ma._mo_hinh(video, thu_muc), nhac)))

    def test_moi_loai_canh_o_gioi_han_doc_nam_gon_trong_khung(self):
        ds = canh_toi_da()
        self.assertEqual({loai for loai, _ in ds}, set(parse.SCENE_TYPES))
        for canh, html in self.dung(ds, "toi-da"):
            with self.subTest(so=canh.so, loai=canh.loai):
                tran, ra = ngoai_vung(self.page, html)
                self.assertEqual(tran, [])
                self.assertEqual(ra, [])

    def test_cot_phu_o_gioi_han_doc(self):
        # Có hình ở cột phụ (khối dưới nội dung), số dòng lặp vừa ô nội dung hẹp (tới y 620).
        ds = [(loai, noi) for loai, noi in canh_toi_da(cot=True)
              if loai in ("tieu-de", "khai-niem", "cong-thuc", "y-tung-y", "so-do")]
        for canh, html in self.dung(ds, "cot"):
            with self.subTest(so=canh.so, loai=canh.loai):
                tran, ra = ngoai_vung(self.page, html)
                self.assertEqual(tran, [])
                self.assertEqual(ra, [])

    def test_nguon_nhac_nen_tren_vach_phu_de(self):
        ds = [("tieu-de", "chu: Con lắc đơn\n")]
        nguon = "Nhạc: Buổi sáng êm đềm · Nghệ sĩ Nguyễn Văn Nghiêng · CC BY 4.0 · openverse.org"
        (_, html), = self.dung(ds, "nhac", {"nguon": nguon})
        tran, ra = ngoai_vung(self.page, html)
        self.assertEqual((tran, ra), ([], []))
        self.page.evaluate("() => window.datThoiDiem(1e6)")
        r = self.page.evaluate("() => { const r = document.getElementById('nhac-nguon').getBoundingClientRect();"
                               " return [r.top, r.bottom, getComputedStyle(document.getElementById('nhac-nguon')).display]; }")
        self.assertEqual(r[2], "block")
        self.assertLessEqual(r[1], 1080)
        self.assertGreater(r[1], 1080 - 20)


def chay(thu_muc: Path, *them: str) -> dict:
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
        video_ma.main([str(thu_muc), *them])
    return json.loads(out.getvalue().strip().splitlines()[-1])


@unittest.skipUnless(CO_CHROMIUM, "máy không có Chromium hoặc playwright")
class KhoDocXemTruocTest(unittest.TestCase):
    def test_xem_truoc_kho_doc_ra_anh_1080x1920(self):
        import so_anh
        with tempfile.TemporaryDirectory() as tmp:
            ds = [("tieu-de", "chu: Con lắc đơn\nphu: Vật lí 11\n"),
                  ("so-sanh", "tieu-de: Hai loại\ntrai: A\nphai: B\ny-trai: Một\ny-phai: Hai\n")]
            thu_muc = thu_muc_bai(Path(tmp), video_md(ds))
            data = chay(thu_muc, "--xem-truoc")
            self.assertTrue(data["ready"], data)
            self.assertEqual(len(data["files"]), 2)
            for f in data["files"]:
                self.assertEqual(so_anh.kich_thuoc_png(thu_muc / f), (1080, 1920))

    def test_xem_truoc_kho_doc_vuot_gioi_han_doc_la_loi_canh(self):
        with tempfile.TemporaryDirectory() as tmp:
            n = kiem.LIMITS_DOC[("tieu-de", "chu")] + 1
            thu_muc = thu_muc_bai(Path(tmp), video_md([("tieu-de", f"chu: {chuoi(n)}\n")]))
            data = chay(thu_muc, "--xem-truoc")
            self.assertFalse(data["ready"])
            self.assertEqual(data["error"]["step"], "canh")
            self.assertIn("giới hạn khổ dọc", data["error"]["message"])


@unittest.skipUnless(CO_CA_HAI, "máy thiếu Chromium/playwright hoặc FFmpeg/ffprobe")
class KhoDocDungThatTest(unittest.TestCase):
    def test_dung_that_kho_doc_giong_gia(self):
        with tempfile.TemporaryDirectory() as tmp:
            ds = [("tieu-de", "chu: Con lắc đơn\n"),
                  ("y-tung-y", "tieu-de: Hai ý\ny: Một\ny: Hai\nhinh: clock\n")]
            thu_muc = thu_muc_bai(Path(tmp), video_md(ds, META_DOC + "do-phan-giai: 720\n"))
            for so in (1, 2):
                mp3 = thu_muc / "giong" / f"canh-{so}.mp3"
                mp3.parent.mkdir(exist_ok=True)
                subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "lavfi", "-i",
                                "sine=frequency=440:duration=1.5", "-q:a", "9", str(mp3)], check=True, timeout=60)
            with mock.patch.object(chup, "so_tien_trinh", return_value=1):
                data = chay(thu_muc)
            self.assertTrue(data["ready"], data)
            out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                  "stream=width,height", "-of", "json", str(thu_muc / "video.mp4")],
                                 capture_output=True, text=True, check=True, timeout=60).stdout
            s = json.loads(out)["streams"][0]
            self.assertEqual((s["width"], s["height"]), (720, 1280))
            self.assertAlmostEqual(data["thoi_luong_giay"], sum(lich.thoi_luong_canh(1.5) for _ in ds), delta=0.3)


if __name__ == "__main__":
    unittest.main()

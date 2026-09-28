"""Nhạc nền: khoá `nhac-nen`/`nguon-nhac`, đọc file trong nhac/ (chặn đường dẫn, nguồn, tên có dấu), lệnh trộn có
hạ nhạc khi có giọng, dòng nguồn nhạc 4 s cuối video. Phần FFmpeg/Chromium thật tự bỏ qua nếu máy thiếu."""

import contextlib
import importlib.util
import io
import json
import math
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import unicodedata
import unittest
import wave
from pathlib import Path
from unittest import mock

TOOLS_VI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_VI))

import video_ma  # noqa: E402
from video_ma_parts import chup, ghep, kiem, lich, nhac, parse, trang  # noqa: E402

META = "tieu-de: T\nmon: Toán\nlop: 8\n"
CO_FFMPEG = shutil.which("ffmpeg") is not None and shutil.which("ffprobe") is not None


def co_chromium() -> bool:
    root = os.environ.get("LOCALAPPDATA")
    if not root or importlib.util.find_spec("playwright") is None:
        return False
    base = Path(root) / "ms-playwright"
    return base.is_dir() and (any(base.glob("chromium-*")) or any(base.glob("chromium_headless_shell-*")))


def video_md(dong_meta="", canh2=True):
    text = f"---\n{META}{dong_meta}---\n\n## Cảnh 1\nloai: tieu-de\nchu: A\nloi: Chào.\n"
    if canh2:
        text += "\n## Cảnh 2\nloai: y-tung-y\ntieu-de: B\ny: một\nloi: Một.\n"
    return text


def probe_gia(giay="12.5", ma=0):
    calls = []

    def run(cmd, **kw):
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, ma, giay, "loi" if ma else "")
    run.calls = calls
    return run


class KhoaDauTest(unittest.TestCase):
    def test_nhac_nen_va_nguon_nhac_la_khoa_tu_do_co_so_dong(self):
        v = parse.parse(video_md("nhac-nen: nhạc êm.mp3\nnguon-nhac: Bản A · B · CC0\n"))
        self.assertEqual(v.meta["nhac-nen"], "nhạc êm.mp3")
        self.assertEqual(v.meta["nguon-nhac"], "Bản A · B · CC0")
        self.assertEqual(v.dong_meta["nhac-nen"], 5)
        self.assertEqual(v.dong_meta["nguon-nhac"], 6)

    def test_khong_co_nhac_nen_thi_khong_co_khoa(self):
        v = parse.parse(video_md())
        self.assertNotIn("nhac-nen", v.meta)
        self.assertNotIn("nguon-nhac", v.meta)

    def test_nguon_nhac_khong_kem_nhac_nen_la_loi_dong(self):
        with self.assertRaises(parse.ParseError) as cm:
            parse.parse(video_md("nguon-nhac: Bản A\n"))
        self.assertEqual(cm.exception.line_no, 5)

    def test_nguon_nhac_chua_dia_chi_web_la_loi(self):
        with self.assertRaises(parse.ParseError) as cm:
            parse.parse(video_md("nhac-nen: a.mp3\nnguon-nhac: https://x.example/a\n"))
        self.assertEqual(cm.exception.line_no, 6)


class DocTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.du_an = Path(tmp.name) / "bai"
        self.nhac = self.du_an / "nhac"
        self.nhac.mkdir(parents=True)
        (self.nhac / "em.mp3").write_bytes(b"ID3")

    def nguon_json(self, items):
        (self.nhac / "nguon.json").write_text(json.dumps({"items": items}, ensure_ascii=False), encoding="utf-8")

    def test_doc_nguon_tu_nguon_json_bo_dia_chi_web(self):
        self.nguon_json([{"filename": "em.mp3", "title": "Êm", "creator": "An (https://an.example)", "license": "CC BY 4.0",
                          "license_url": "https://creativecommons.org/licenses/by/4.0/", "source_url": "https://x"}])
        run = probe_gia("61.2")
        kq = nhac.doc(self.du_an, "em.mp3", None, run=run)
        self.assertEqual(kq["duong_dan"], (self.nhac / "em.mp3").resolve())
        self.assertEqual(kq["nguon"], "Nhạc: Êm · An · CC BY 4.0")
        self.assertAlmostEqual(kq["giay"], 61.2)
        self.assertEqual(run.calls[0][0], "ffprobe")

    def test_nguon_tay_uu_tien_va_them_chu_nhac(self):
        self.nguon_json([{"filename": "em.mp3", "title": "Khác", "creator": "X", "license": "CC0 1.0"}])
        self.assertEqual(nhac.doc(self.du_an, "em.mp3", "Êm · An · CC0", run=probe_gia())["nguon"], "Nhạc: Êm · An · CC0")
        self.assertEqual(nhac.doc(self.du_an, "em.mp3", "Nhạc: Êm", run=probe_gia())["nguon"], "Nhạc: Êm")

    def test_nguon_tay_nfd_da_co_chu_nhac_khong_them_lan_nua(self):
        v = parse.parse(unicodedata.normalize("NFD", video_md("nhac-nen: em.mp3\nnguon-nhac: Nhạc: Êm · An\n")))
        kq = nhac.doc(self.du_an, v.meta["nhac-nen"], v.meta["nguon-nhac"], run=probe_gia())
        self.assertEqual(kq["nguon"], unicodedata.normalize("NFC", "Nhạc: Êm · An"))

    def test_chan_duong_dan_ra_ngoai_nhac(self):
        (self.du_an / "ngoai.mp3").write_bytes(b"ID3")
        for ten in ("../ngoai.mp3", "con/em.mp3", "con\\em.mp3", "C:em.mp3", str((self.du_an / "ngoai.mp3").resolve()), ""):
            with self.subTest(ten=ten):
                with self.assertRaises(nhac.NhacError) as cm:
                    nhac.doc(self.du_an, ten, "Nguồn", run=probe_gia())
                self.assertIn("nhac/", str(cm.exception))

    def test_sai_dinh_dang_va_thieu_file(self):
        (self.nhac / "a.flac").write_bytes(b"x")
        with self.assertRaises(nhac.NhacError) as cm:
            nhac.doc(self.du_an, "a.flac", "N", run=probe_gia())
        self.assertIn("a.flac", str(cm.exception))
        for duoi in (".mp3", ".m4a", ".wav", ".ogg", ".MP3"):
            (self.nhac / f"b{duoi}").write_bytes(b"x")
            self.assertTrue(nhac.doc(self.du_an, f"b{duoi}", "N", run=probe_gia())["nguon"])
        with self.assertRaises(nhac.NhacError) as cm:
            nhac.doc(self.du_an, "khong-co.mp3", "N", run=probe_gia())
        self.assertIn("khong-co.mp3", str(cm.exception))

    def test_thieu_nguon_bao_ten_file(self):
        with self.assertRaises(nhac.NhacError) as cm:
            nhac.doc(self.du_an, "em.mp3", None, run=probe_gia())
        self.assertIn("em.mp3", str(cm.exception))
        self.assertIn("nguon-nhac", str(cm.exception))
        self.nguon_json([{"filename": "khac.mp3", "title": "K", "creator": "K", "license": "CC0"}])
        with self.assertRaises(nhac.NhacError):
            nhac.doc(self.du_an, "em.mp3", None, run=probe_gia())
        self.nguon_json([{"filename": "em.mp3", "title": "https://chi-co-dia-chi.example"}])
        with self.assertRaises(nhac.NhacError):
            nhac.doc(self.du_an, "em.mp3", None, run=probe_gia())

    def test_nguon_json_hong_la_loi(self):
        (self.nhac / "nguon.json").write_text("{hong", encoding="utf-8")
        with self.assertRaises(nhac.NhacError) as cm:
            nhac.doc(self.du_an, "em.mp3", None, run=probe_gia())
        self.assertIn("nguon.json", str(cm.exception))
        (self.nhac / "nguon.json").write_text(json.dumps({"items": ["em.mp3"]}), encoding="utf-8")
        with self.assertRaises(nhac.NhacError):
            nhac.doc(self.du_an, "em.mp3", None, run=probe_gia())

    def test_file_hong_ffprobe_khong_doc_duoc(self):
        for run in (probe_gia("", ma=1), probe_gia("N/A"), probe_gia("0")):
            with self.assertRaises(nhac.NhacError) as cm:
                nhac.doc(self.du_an, "em.mp3", "N", run=run)
            self.assertIn("em.mp3", str(cm.exception))

    def test_may_chua_co_ffprobe_thi_chua_do_thoi_luong(self):
        def run(cmd, **kw):
            raise FileNotFoundError("ffprobe")
        self.assertIsNone(nhac.doc(self.du_an, "em.mp3", "N", run=run)["giay"])

    def test_ten_co_dau_nfd_tren_dia_nfc_trong_kich_ban(self):
        ten = "nhạc nền.mp3"
        (self.nhac / unicodedata.normalize("NFD", ten)).write_bytes(b"ID3")
        self.nguon_json([{"filename": unicodedata.normalize("NFD", ten), "title": "Nền", "creator": "C", "license": "CC0 1.0"}])
        kq = nhac.doc(self.du_an, unicodedata.normalize("NFC", ten), None, run=probe_gia())
        self.assertTrue(kq["duong_dan"].is_file())
        self.assertEqual(kq["nguon"], "Nhạc: Nền · C · CC0 1.0")


class KiemTest(unittest.TestCase):
    def kiem(self, dong_meta, nguon=None):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        du_an = Path(tmp.name)
        (du_an / "nhac").mkdir()
        (du_an / "nhac" / "em.mp3").write_bytes(b"ID3")
        if nguon is not None:
            (du_an / "nhac" / "nguon.json").write_text(json.dumps({"items": nguon}), encoding="utf-8")
        with mock.patch.object(nhac, "thoi_luong", return_value=40.0):
            return kiem.kiem(parse.parse(video_md(dong_meta)), du_an)

    def test_thieu_nguon_la_loi_canh_0_neu_dong_khoa_dau(self):
        with self.assertRaises(kiem.CanhError) as cm:
            self.kiem("nhac-nen: em.mp3\n")
        self.assertEqual(cm.exception.so, 0)
        self.assertIn("em.mp3", cm.exception.message)
        self.assertIn("dòng 5", cm.exception.message)

    def test_duong_dan_thoat_la_loi_canh(self):
        with self.assertRaises(kiem.CanhError) as cm:
            self.kiem("nhac-nen: ../em.mp3\nnguon-nhac: A\n")
        self.assertIn("dòng 5", cm.exception.message)

    def test_du_nguon_thi_qua(self):
        self.assertEqual(self.kiem("nhac-nen: em.mp3\nnguon-nhac: A · B · CC0\n"), [])
        self.assertEqual(self.kiem("nhac-nen: em.mp3\n", [{"filename": "em.mp3", "title": "A", "creator": "B",
                                                          "license": "CC0"}]), [])


class LenhNhacTest(unittest.TestCase):
    def lenh(self):
        return ghep.lenh_nhac(Path("am.txt"), Path("nhac/em.mp3"), Path("am-nhac.wav"), 12.0)

    def test_nhac_lap_cat_dung_tong_thoi_luong(self):
        cmd = self.lenh()
        i = cmd.index("nhac/em.mp3") if "nhac/em.mp3" in cmd else cmd.index(str(Path("nhac/em.mp3")))
        self.assertEqual(cmd[i - 3:i - 1], ["-stream_loop", "-1"])
        self.assertEqual(cmd[cmd.index("-t") + 1], "12.000")
        loc = cmd[cmd.index("-filter_complex") + 1]
        self.assertIn("atrim=duration=12.000", loc)
        self.assertIn(["-f", "concat", "-safe", "0", "-i", "am.txt"], [cmd[k:k + 6] for k in range(len(cmd))])

    def test_vao_ra_1_5_giay_nen_tru_24_db_ha_khi_co_giong_tron_khong_chuan_hoa(self):
        loc = self.lenh()[self.lenh().index("-filter_complex") + 1]
        self.assertIn("afade=t=in:d=1.500", loc)
        self.assertIn("afade=t=out:st=10.500:d=1.500", loc)
        self.assertIn("volume=-24dB", loc)
        self.assertIn("sidechaincompress=threshold=0.02:ratio=8:attack=20:release=400", loc)
        self.assertIn("amix=inputs=2:duration=first:normalize=0", loc)

    def test_video_ngan_hon_3_giay_thi_vao_ra_vua_video(self):
        cmd = ghep.lenh_nhac(Path("am.txt"), Path("em.mp3"), Path("ra.wav"), 2.5)
        loc = cmd[cmd.index("-filter_complex") + 1]
        self.assertIn("afade=t=in:d=1.250", loc)
        self.assertIn("afade=t=out:st=1.250:d=1.250", loc)


def canh_lich(so, bat_dau, thoi_luong, giay):
    return lich.CanhLich(so=so, bat_dau=bat_dau, thoi_luong=thoi_luong, so_khung=round(thoi_luong * lich.FPS), giay_giong=giay,
                         cau=["Chào."], moc_cau=[lich.DAN_DAU], moc_cau_giong=[0.0], uoc_luong=False)


PLAN = [canh_lich(1, 0.0, 6.0, 4.0), canh_lich(2, 6.0, 3.0, 1.5)]


class GhepTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.thu_muc = Path(tmp.name) / "bai"
        (self.thu_muc / ".khung" / "anh").mkdir(parents=True)
        self.giong = [lich.GiongInfo(mp3=self.thu_muc / f"g{cl.so}.mp3", giay=cl.giay_giong, moc_cau=[], uoc_luong=False,
                                     nguon="may") for cl in PLAN]

    def ghep(self, nhac_):
        calls = []

        def run(cmd, **kw):
            calls.append(cmd)
            if cmd[-1].endswith("video.mp4"):
                (Path(kw["cwd"]) / cmd[-1]).write_bytes(b"mp4")
            return subprocess.CompletedProcess(cmd, 0, "", "")
        ghep.ghep_video(self.thu_muc, PLAN, self.giong, "khong", run=run, nhac=nhac_)
        return calls

    def test_khong_nhac_thi_nhu_cu(self):
        calls = self.ghep(None)
        self.assertEqual(len(calls), 3)
        self.assertEqual(calls[2], ghep.lenh_video(self.thu_muc / ".khung" / "am.txt", self.thu_muc / ".khung" / "video.mp4",
                                                   lich.FPS, None))

    def test_co_nhac_thi_tron_sau_khi_noi_tieng_va_video_dung_tieng_da_tron(self):
        em = self.thu_muc / "nhac" / "em.mp3"
        calls = self.ghep({"duong_dan": em, "nguon": "Nhạc: A", "giay": 5.0})
        lam = self.thu_muc / ".khung"
        self.assertEqual(len(calls), 4)
        self.assertEqual(calls[2], ghep.lenh_nhac(lam / "am.txt", em, lam / "am-nhac.wav", 9.0))
        video = calls[3]
        self.assertEqual(video[video.index("-framerate") + 4:video.index("-framerate") + 6], ["-i", str(lam / "am-nhac.wav")])
        self.assertNotIn("concat", video)


class DungTest(unittest.TestCase):
    """video_ma: nhạc đọc lại từ nhac/, đưa sang ghep; dòng nguồn gắn vào dữ liệu cảnh cuối (4 s cuối)."""

    def test_nhac_va_dong_nguon_cua_canh_cuoi(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        thu_muc = Path(tmp.name) / "bai"
        (thu_muc / "nhac").mkdir(parents=True)
        (thu_muc / "nhac" / "em.mp3").write_bytes(b"ID3")
        (thu_muc / "video.md").write_text(video_md("nhac-nen: em.mp3\nnguon-nhac: Êm · An · CC0\n"), encoding="utf-8")
        giong = lich.GiongInfo(mp3=thu_muc / "x.mp3", giay=3.0, moc_cau=[0.0], uoc_luong=False, nguon="may")
        seen = {}

        def chup_gia(cac_du, *a, **kw):
            seen["du"] = cac_du
            return None

        def ghep_gia(thu_muc_, cac_lich, cac_giong, phu_de, **kw):
            seen["ghep_kw"] = kw
            seen["lich"] = cac_lich
            return ["video.mp4"]

        with contextlib.ExitStack() as st:
            for p in (mock.patch.object(video_ma, "co_ffmpeg", return_value=True),
                      mock.patch.object(video_ma, "co_chromium", return_value=True),
                      mock.patch.object(video_ma.chup, "trinh_duyet", side_effect=lambda: contextlib.nullcontext(object())),
                      mock.patch.object(video_ma.chup, "trang_moi", return_value=object()),
                      mock.patch.object(video_ma.chup, "kiem_tran", return_value=[]),
                      mock.patch.object(video_ma.giong, "lay_giong", return_value=giong),
                      mock.patch.object(video_ma.chup, "chup_song_song", side_effect=chup_gia),
                      mock.patch.object(video_ma.ghep, "ghep_video", side_effect=ghep_gia),
                      mock.patch.object(nhac, "thoi_luong", return_value=30.0)):
                st.enter_context(p)
            out = io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                code = video_ma.main([str(thu_muc)])
        data = json.loads(out.getvalue().strip())
        self.assertEqual(code, 0, data)
        self.assertEqual(seen["ghep_kw"]["nhac"]["duong_dan"], (thu_muc / "nhac" / "em.mp3").resolve())
        self.assertNotIn("dongNguon", seen["du"][0])
        gh = seen["lich"][-1].thoi_luong
        self.assertEqual(seen["du"][-1]["dongNguon"], [{"chu": "Nhạc: Êm · An · CC0", "tu": round(gh - 4.0, 3)}])

    def dung(self, dong_meta, kiem_tran=()):
        """Chạy video_ma.main (dựng) với FFmpeg/Chromium/giọng giả; trả (mã, JSON, số lần đo nhạc bằng ffprobe)."""
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        thu_muc = Path(tmp.name) / "bai"
        (thu_muc / "nhac").mkdir(parents=True)
        (thu_muc / "nhac" / "em.mp3").write_bytes(b"ID3")
        (thu_muc / "video.md").write_text(video_md(dong_meta), encoding="utf-8")
        giong = lich.GiongInfo(mp3=thu_muc / "x.mp3", giay=3.0, moc_cau=[0.0], uoc_luong=False, nguon="may")
        do = mock.Mock(return_value=30.0)
        with contextlib.ExitStack() as st:
            for p in (mock.patch.object(video_ma, "co_ffmpeg", return_value=True),
                      mock.patch.object(video_ma, "co_chromium", return_value=True),
                      mock.patch.object(video_ma.chup, "trinh_duyet", side_effect=lambda: contextlib.nullcontext(object())),
                      mock.patch.object(video_ma.chup, "trang_moi", return_value=object()),
                      mock.patch.object(video_ma.chup, "kiem_tran", return_value=list(kiem_tran)),
                      mock.patch.object(video_ma.giong, "lay_giong", return_value=giong),
                      mock.patch.object(video_ma.chup, "chup_song_song", return_value=None),
                      mock.patch.object(video_ma.ghep, "ghep_video", return_value=["video.mp4"]),
                      mock.patch.object(nhac, "thoi_luong", do)):
                st.enter_context(p)
            out = io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                code = video_ma.main([str(thu_muc)])
        return code, json.loads(out.getvalue().strip()), do.call_count

    def test_mot_lan_dung_chi_do_nhac_mot_lan(self):
        code, data, lan = self.dung("nhac-nen: em.mp3\nnguon-nhac: Êm · An · CC0\n")
        self.assertEqual(code, 0, data)
        self.assertEqual(lan, 1)

    def test_loi_nhac_nen_co_cach_sua_rieng(self):
        code, data, _ = self.dung("nhac-nen: em.mp3\n")
        self.assertEqual(code, 1)
        self.assertEqual(data["error"]["step"], "canh")
        self.assertEqual(data["error"]["fix"], video_ma.FIX_NHAC)
        self.assertNotIn("nội dung cảnh", data["error"]["fix"])
        self.assertIn("nguon-nhac", data["error"]["fix"])

    def test_dong_nguon_nhac_tran_khung_co_cach_sua_rieng(self):
        code, data, _ = self.dung("nhac-nen: em.mp3\nnguon-nhac: Êm · An · CC0\n", kiem_tran=["nhac-nguon"])
        self.assertEqual(code, 1)
        self.assertEqual(data["error"]["step"], "canh")
        self.assertIn("nguồn nhạc", data["error"]["message"])
        self.assertEqual(data["error"]["fix"], video_ma.FIX_NGUON_NHAC)

    def test_dong_nguon_cuoi_de_chu_canh_cuoi_co_cach_sua_rieng(self):
        code, data, _ = self.dung("nhac-nen: em.mp3\nnguon-nhac: Êm · An · CC0\n", kiem_tran=["nhac-nguon-de"])
        self.assertEqual(code, 1)
        self.assertEqual(data["error"]["step"], "canh")
        self.assertIn("đè", data["error"]["message"])
        self.assertEqual(data["error"]["fix"], video_ma.FIX_NGUON_DE)

    def test_tran_khung_noi_dung_canh_van_bao_nhu_cu(self):
        code, data, _ = self.dung("nhac-nen: em.mp3\nnguon-nhac: Êm · An · CC0\n", kiem_tran=["tieu-de", "nhac-nguon"])
        self.assertEqual(code, 1)
        self.assertIn("`tieu-de`", data["error"]["message"])
        self.assertEqual(data["error"]["fix"], video_ma.FIX_CANH)

    def test_canh_cuoi_ngan_hon_4_giay_thi_hien_ca_canh(self):
        du = {"so": 1, "thoiLuong": 2.5}
        lich.gan_dong_nguon(du, ["Nhạc: A"])
        self.assertEqual(du["dongNguon"], [{"chu": "Nhạc: A", "tu": 0.0}])


def doc_wav(path: Path) -> tuple:
    with wave.open(str(path)) as w:
        assert (w.getnchannels(), w.getsampwidth()) == (1, 2)
        return struct.unpack("<%dh" % w.getnframes(), w.readframes(w.getnframes())), w.getframerate()


def rms_db(mau) -> float:
    if not mau:
        return -120.0
    r = math.sqrt(sum(x * x for x in mau) / len(mau))
    return 20 * math.log10(r / 32768) if r else -120.0


@unittest.skipUnless(CO_FFMPEG, "máy không có FFmpeg")
class FfmpegThatTest(unittest.TestCase):
    """Giọng sine 440 Hz ngắt quãng + nhạc sine 2000 Hz dài 5 s; video 12 s (hai cảnh 6 s)."""

    NHAC_HZ = 2000

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        tmp = Path(cls.tmp.name)
        wavs = []
        for so in (1, 2):
            g = tmp / f"g{so}.wav"
            # Giọng 2 s đỉnh −6 dBFS; trong cảnh bắt đầu ở DAN_DAU = 1 s -> có giọng ở 1–3 s và 7–9 s của video.
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i",
                            "aevalsrc='0.5*sin(2*PI*440*t)':s=44100:d=2", "-ac", "1", "-c:a", "pcm_s16le", str(g)], check=True)
            w = tmp / f"am-{so}.wav"
            subprocess.run(ghep.lenh_am_canh(g, w, 6.0), check=True)
            wavs.append(w)
        cls.danh_sach = tmp / "am.txt"
        cls.danh_sach.write_text(ghep.media.build_audio_concat_text(wavs), encoding="utf-8")
        cls.nhac = tmp / "nhac.mp3"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i",
                        f"aevalsrc='0.5*sin(2*PI*{cls.NHAC_HZ}*t)':s=44100:d=5", "-ac", "2", str(cls.nhac)], check=True)
        cls.ra = tmp / "am-nhac.wav"
        subprocess.run(ghep.lenh_nhac(cls.danh_sach, cls.nhac, cls.ra, 12.0), check=True)
        cls.loc = tmp / "loc.wav"
        # Lọc thông dải hẹp quanh tần số nhạc (ba tầng) để đo riêng mức nhạc.
        bp = f"bandpass=f={cls.NHAC_HZ}:width_type=q:w=4"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(cls.ra), "-af", ",".join([bp] * 3),
                        "-c:a", "pcm_s16le", str(cls.loc)], check=True)
        cls.mau, cls.tan = doc_wav(cls.ra)
        cls.nhac_bang, _ = doc_wav(cls.loc)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def doan(self, mau, a, b):
        return mau[int(a * self.tan):int(b * self.tan)]

    def test_thoi_luong_dung_12_giay(self):
        self.assertEqual(len(self.mau), round(12.0 * self.tan))
        self.assertEqual(self.tan, 44100)

    def test_nhac_ha_it_nhat_6_db_khi_co_giong(self):
        co_giong = [rms_db(self.doan(self.nhac_bang, a, b)) for a, b in ((1.6, 2.9), (7.3, 8.9))]
        khong_giong = [rms_db(self.doan(self.nhac_bang, a, b)) for a, b in ((4.0, 6.8), (9.8, 10.4))]
        self.__class__.do = (co_giong, khong_giong)
        for cg in co_giong:
            for kg in khong_giong:
                self.assertLessEqual(cg, kg - 6, (co_giong, khong_giong))

    def test_nhac_5_giay_lap_du_video_12_giay(self):
        # Không giọng: mỗi nửa giây từ 3,6 s tới 6,9 s và 9,6 s tới 10,4 s (lượt lặp thứ ba) đều có nhạc ở mức nền.
        for a in [x / 10 for x in range(36, 69, 5)] + [9.6, 10.0]:
            with self.subTest(giay=a):
                self.assertGreater(rms_db(self.doan(self.nhac_bang, a, a + 0.4)), -40)
        self.assertGreater(rms_db(self.doan(self.nhac_bang, 11.0, 11.4)), -60, "đang ra dần, vẫn còn nhạc")

    def test_nhac_nen_quanh_tru_24_db_va_giong_giu_nguyen(self):
        # Nhạc gốc sine đỉnh 0,5 (RMS −9 dBFS) -> nền −24 dB: RMS khoảng −33 dBFS khi không có giọng.
        self.assertAlmostEqual(rms_db(self.doan(self.nhac_bang, 4.0, 6.8)), -33.0, delta=2.0)
        self.assertAlmostEqual(rms_db(self.doan(self.mau, 1.6, 2.9)), 20 * math.log10(0.5 / math.sqrt(2)), delta=1.0)

    def test_khong_co_doan_im_lang_tuyet_doi(self):
        cua = self.tan // 20
        self.assertEqual([i for i in range(0, len(self.mau) - cua, cua) if not any(self.mau[i:i + cua])], [])


@unittest.skipUnless(co_chromium(), "máy không có Chromium hoặc playwright")
class TrangChromiumTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ctx = chup.trinh_duyet()
        cls.browser = cls.ctx.__enter__()
        cls.page = chup.trang_moi(cls.browser)

    @classmethod
    def tearDownClass(cls):
        cls.ctx.__exit__(None, None, None)

    def du(self, nguon):
        v = parse.parse(video_md(canh2=False))
        cl = canh_lich(1, 0.0, 8.0, 5.0)
        du = lich.du_lieu_canh(v.canh[0], cl, None, {"meta": v.meta})
        lich.gan_dong_nguon(du, [nguon])
        return du

    def the(self, t):
        self.page.evaluate("(t) => window.datThoiDiem(t)", t)
        return self.page.evaluate("""() => { const e = document.getElementById('nhac-nguon');
            if (!e) return null; const r = e.getBoundingClientRect(); const s = getComputedStyle(e);
            return {hien: s.display !== 'none' && Number(s.opacity) > 0, chu: e.textContent, trai: r.left, day: r.bottom,
                    tren: r.top, phai: r.right, co: s.fontSize}; }""")

    def test_dong_nguon_nhac_hien_4_giay_cuoi_goc_duoi_trai_tren_phu_de(self):
        html = trang.dung_trang(self.du("Nhạc: Êm dịu · Nguyễn Văn An · CC BY 4.0"))
        self.assertEqual(chup.kiem_tran(self.page, html), [])
        chup.mo_trang(self.page, html)
        self.assertFalse(self.the(3.9)["hien"])
        o = self.the(4.6)
        self.assertTrue(o["hien"])
        self.assertEqual(o["chu"], "Nhạc: Êm dịu · Nguyễn Văn An · CC BY 4.0")
        self.assertEqual(o["co"], "14px")
        self.assertLess(o["trai"], 60)
        self.assertLessEqual(o["day"], 620)
        self.assertGreater(o["tren"], 540)
        self.assertTrue(self.the(7.8)["hien"])

    def test_dong_nguon_dai_van_trong_khung(self):
        html = trang.dung_trang(self.du("Nhạc: " + "Bản nhạc có tên rất dài " * 12))
        self.assertEqual(chup.kiem_tran(self.page, html), [])

    def test_khong_co_nhac_thi_khong_co_dong_nguon(self):
        v = parse.parse(video_md(canh2=False))
        html = trang.dung_trang(lich.du_lieu_canh(v.canh[0], canh_lich(1, 0.0, 8.0, 5.0), None, {"meta": v.meta}))
        chup.mo_trang(self.page, html)
        self.assertIsNone(self.the(7.0))


if __name__ == "__main__":
    unittest.main()

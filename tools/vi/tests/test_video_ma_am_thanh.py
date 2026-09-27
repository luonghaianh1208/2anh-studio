"""Hiệu ứng âm thanh: khoá `am-thanh`, mẫu tạo bằng FFmpeg, lệnh trộn theo sự kiện của trang, ghép vào tiếng cảnh.
Phần FFmpeg/Chromium thật tự bỏ qua nếu máy thiếu."""

import contextlib
import importlib.util
import io
import json
import math
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
import wave
from pathlib import Path
from unittest import mock

TOOLS_VI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_VI))

import video_ma  # noqa: E402
from video_ma_parts import am_thanh, chup, ghep, lich, parse, trang  # noqa: E402

META = "tieu-de: T\nmon: Toán\nlop: 8\n"
CO_FFMPEG = shutil.which("ffmpeg") is not None


def co_chromium() -> bool:
    root = os.environ.get("LOCALAPPDATA")
    if not root or importlib.util.find_spec("playwright") is None:
        return False
    base = Path(root) / "ms-playwright"
    return base.is_dir() and (any(base.glob("chromium-*")) or any(base.glob("chromium_headless_shell-*")))


def doc_wav(path: Path) -> tuple:
    with wave.open(str(path)) as w:
        assert (w.getnchannels(), w.getsampwidth()) == (1, 2), (w.getnchannels(), w.getsampwidth())
        return struct.unpack("<%dh" % w.getnframes(), w.readframes(w.getnframes())), w.getframerate()


def dbfs(mau) -> float:
    dinh = max((abs(x) for x in mau), default=0)
    return 20 * math.log10(dinh / 32768) if dinh else -120.0


class KhoaDauTest(unittest.TestCase):
    def doc(self, dong=""):
        return parse.parse(f"---\n{META}{dong}---\n\n## Cảnh 1\nloai: tieu-de\nchu: A\nloi: Chào.\n")

    def test_am_thanh_mac_dinh_co_va_nhan_khong(self):
        self.assertEqual(self.doc().meta["am-thanh"], "co")
        self.assertEqual(self.doc("am-thanh: khong\n").meta["am-thanh"], "khong")

    def test_am_thanh_gia_tri_la_bao_loi_kem_so_dong(self):
        with self.assertRaises(parse.ParseError) as cm:
            self.doc("am-thanh: to\n")
        self.assertEqual(cm.exception.line_no, 5)


SU_KIEN = [
    {"t": 0.0, "loai": "chuyen", "dai": 0},
    {"t": 1.25, "loai": "but", "dai": 0.8},
    {"t": 1.25, "loai": "ting", "dai": 0},
    {"t": 2.0, "loai": "ting", "dai": 0},
    {"t": 3.5, "loai": "tictac", "dai": 0},
    {"t": 4.5, "loai": "dung", "dai": 0},
    {"t": 4.6, "loai": "nhan", "dai": 0},
]
MAU = {loai: Path(f"am/{loai}.wav") for loai in am_thanh.LOAI}


class LenhTronTest(unittest.TestCase):
    def lenh(self, su_kien=SU_KIEN, dinh=-3.0):
        return am_thanh.lenh_tron(Path("am-1-giong.wav"), su_kien, MAU, Path("am-1.wav"), 6.0, dinh_giong_db=dinh)

    def test_giong_la_dau_vao_dau_tien_moi_mau_dung_mot_lan(self):
        cmd = self.lenh()
        vao = [cmd[i + 1] for i, x in enumerate(cmd) if x == "-i"]
        self.assertEqual(vao[0], "am-1-giong.wav")
        self.assertEqual(vao[1:], [str(MAU[l]) for l in am_thanh.LOAI if any(e["loai"] == l for e in SU_KIEN)])
        chi_ting = self.lenh([{"t": 1.0, "loai": "ting", "dai": 0}])
        self.assertEqual([chi_ting[i + 1] for i, x in enumerate(chi_ting) if x == "-i"], ["am-1-giong.wav", str(MAU["ting"])])

    def test_moi_su_kien_tre_dung_thoi_diem(self):
        loc = self.lenh()[self.lenh().index("-filter_complex") + 1]
        self.assertEqual(loc.count("adelay="), len(SU_KIEN))
        for ms, lan in ((0, 1), (1250, 2), (2000, 1), (3500, 1), (4500, 1), (4600, 1)):
            self.assertEqual(loc.count(f"adelay={ms}:all=1"), lan, ms)
        self.assertIn("asplit=2", loc, "hai tiếng ting dùng chung một đầu vào")

    def test_but_lap_va_cat_theo_dai(self):
        loc = self.lenh()[self.lenh().index("-filter_complex") + 1]
        self.assertIn("aloop=loop=-1:size=", loc)
        self.assertIn("atrim=duration=0.800", loc)

    def test_muc_hieu_ung_duoi_dinh_giong_20_db_va_co_bo_gioi_han(self):
        loc = self.lenh(dinh=-3.0)[self.lenh().index("-filter_complex") + 1]
        muc = -3.0 - am_thanh.DUOI_GIONG_DB - am_thanh.DINH_BUS_DB
        self.assertIn(f"volume={muc:.2f}dB", loc)
        self.assertIn("alimiter=", loc)
        self.assertIn("level=0", loc)

    def muc(self, dinh):
        loc = self.lenh(dinh=dinh)[self.lenh().index("-filter_complex") + 1]
        return float(re.search(r"volume=(-?\d+\.\d+)dB", loc).group(1)) + am_thanh.DINH_BUS_DB

    def test_giong_rat_nho_hieu_ung_van_duoi_giong_it_nhat_12_db(self):
        for dinh in (-45.0, -40.0, -30.0):
            with self.subTest(dinh=dinh):
                self.assertLessEqual(self.muc(dinh), dinh - 12.0)

    def test_canh_im_lang_dung_muc_san_an_toan(self):
        muc = self.muc(-120.0)
        self.assertAlmostEqual(muc, am_thanh.MUC_THAP_NHAT, delta=0.01)  # lệnh ghi volume 2 chữ số thập phân
        self.assertLessEqual(muc, -70.0)

    def test_giu_dung_thoi_luong_canh_va_tron_khong_chuan_hoa(self):
        cmd = self.lenh()
        loc = cmd[cmd.index("-filter_complex") + 1]
        self.assertIn("amix=inputs=2:duration=first:normalize=0", loc)
        self.assertEqual(cmd[cmd.index("-t") + 1], "6.000")
        self.assertEqual(cmd[-1], "am-1.wav")
        self.assertIn("pcm_s16le", cmd)


def canh_lich(so, bat_dau, thoi_luong, giay):
    return lich.CanhLich(so=so, bat_dau=bat_dau, thoi_luong=thoi_luong, so_khung=round(thoi_luong * lich.FPS), giay_giong=giay,
                         cau=["Chào."], moc_cau=[lich.DAN_DAU], moc_cau_giong=[0.0], uoc_luong=False)


PLAN = [canh_lich(1, 0.0, 6.0, 4.0), canh_lich(2, 6.0, 3.0, 1.5)]


class GhepTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.thu_muc = Path(self.tmp.name) / "bai"
        (self.thu_muc / ".khung" / "anh").mkdir(parents=True)
        self.giong = []
        for cl in PLAN:
            mp3 = self.thu_muc / "giong" / f"canh-{cl.so}.mp3"
            mp3.parent.mkdir(exist_ok=True)
            mp3.write_bytes(b"ID3")
            self.giong.append(lich.GiongInfo(mp3=mp3, giay=cl.giay_giong, moc_cau=[], uoc_luong=False, nguon="may"))

    def run_gia(self, calls):
        def run(cmd, **kwargs):
            calls.append(cmd)
            if cmd[-1].endswith("video.mp4"):
                (Path(kwargs["cwd"]) / cmd[-1]).write_bytes(b"mp4")
            return subprocess.CompletedProcess(cmd, 0, "", "")
        return run

    def ghep(self, su_kien):
        calls = []
        mau = {loai: self.thu_muc / ".khung" / "am" / f"{loai}.wav" for loai in am_thanh.LOAI}
        with mock.patch.object(am_thanh, "tao_mau", return_value=mau) as tao, \
                mock.patch.object(am_thanh, "dinh_db", return_value=-4.0) as dinh:
            ghep.ghep_video(self.thu_muc, PLAN, self.giong, "khong", run=self.run_gia(calls), su_kien=su_kien)
        return calls, tao, dinh

    def test_khong_co_su_kien_thi_tieng_nhu_cu(self):
        calls, tao, dinh = self.ghep(None)
        self.assertEqual(len(calls), 3)
        self.assertEqual(calls[0], ghep.lenh_am_canh(self.giong[0].mp3, self.thu_muc / ".khung" / "am-1.wav", 6.0))
        self.assertEqual(calls[1], ghep.lenh_am_canh(self.giong[1].mp3, self.thu_muc / ".khung" / "am-2.wav", 3.0))
        tao.assert_not_called()
        dinh.assert_not_called()

    def test_co_su_kien_thi_tron_hieu_ung_vao_tieng_canh(self):
        calls, tao, dinh = self.ghep([SU_KIEN, []])
        lam = self.thu_muc / ".khung"
        self.assertEqual(len(calls), 4)
        self.assertEqual(calls[0], ghep.lenh_am_canh(self.giong[0].mp3, lam / "am-1-giong.wav", 6.0))
        self.assertEqual(calls[1], am_thanh.lenh_tron(lam / "am-1-giong.wav", SU_KIEN, tao.return_value, lam / "am-1.wav", 6.0,
                                                      dinh_giong_db=-4.0))
        # Cảnh không có sự kiện: tiếng như cũ, không trộn.
        self.assertEqual(calls[2], ghep.lenh_am_canh(self.giong[1].mp3, lam / "am-2.wav", 3.0))
        tao.assert_called_once_with(lam / "am", run=mock.ANY)
        dinh.assert_called_once_with(lam / "am-1-giong.wav")
        danh_sach = (lam / "am.txt").read_text(encoding="utf-8")
        self.assertIn("am-1.wav", danh_sach)
        self.assertNotIn("giong.wav", danh_sach)


class FakeBrowser:
    def __enter__(self):
        return object()

    def __exit__(self, *a):
        return False


class DungTest(unittest.TestCase):
    """video_ma: sự kiện lấy từ lượt chụp (chup_song_song) đưa sang ghep; `am-thanh: khong` thì không."""

    def dung(self, dong_meta):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        thu_muc = Path(tmp.name) / "bai"
        thu_muc.mkdir()
        (thu_muc / "video.md").write_text(
            f"---\n{META}{dong_meta}---\n\n## Cảnh 1\nloai: tieu-de\nchu: A\nloi: Chào.\n\n"
            "## Cảnh 2\nloai: y-tung-y\ntieu-de: B\ny: một\nloi: Một.\n", encoding="utf-8")
        giong = lich.GiongInfo(mp3=thu_muc / "x.mp3", giay=3.0, moc_cau=[0.0], uoc_luong=False, nguon="may")
        seen = {}

        def chup_gia(cac_du, models_js, so_khung, fps, thu_muc_anh, so_tt, **kw):
            seen["chup_kw"] = kw
            return {2: [{"t": 0.0, "loai": "chuyen", "dai": 0}]} if kw.get("thu_muc_su_kien") else None

        def ghep_gia(thu_muc, cac_lich, cac_giong, phu_de, **kw):
            seen["ghep_kw"] = kw
            return ["video.mp4"]

        with contextlib.ExitStack() as st:
            for p in (mock.patch.object(video_ma, "co_ffmpeg", return_value=True),
                      mock.patch.object(video_ma, "co_chromium", return_value=True),
                      mock.patch.object(video_ma.chup, "trinh_duyet", side_effect=lambda: FakeBrowser()),
                      mock.patch.object(video_ma.chup, "trang_moi", return_value=object()),
                      mock.patch.object(video_ma.chup, "kiem_tran", return_value=[]),
                      mock.patch.object(video_ma.giong, "lay_giong", return_value=giong),
                      mock.patch.object(video_ma.chup, "chup_song_song", side_effect=chup_gia),
                      mock.patch.object(video_ma.ghep, "ghep_video", side_effect=ghep_gia)):
                st.enter_context(p)
            out = io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                code = video_ma.main([str(thu_muc)])
        data = json.loads(out.getvalue().strip())
        self.assertEqual(code, 0, data)
        return seen, thu_muc

    def test_am_thanh_co_lay_su_kien_tu_luot_chup(self):
        seen, thu_muc = self.dung("")
        self.assertEqual(Path(seen["chup_kw"]["thu_muc_su_kien"]), thu_muc / ".khung" / "su-kien")
        self.assertEqual(seen["ghep_kw"]["su_kien"], [[], [{"t": 0.0, "loai": "chuyen", "dai": 0}]])

    def test_am_thanh_khong_thi_khong_doc_su_kien_va_khong_tron(self):
        seen, _ = self.dung("am-thanh: khong\n")
        self.assertIsNone(seen["chup_kw"].get("thu_muc_su_kien"))
        self.assertIsNone(seen["ghep_kw"].get("su_kien"))


def giong_sine(path: Path, dau: float, dai: float, tong: float) -> None:
    """Giọng giả: sine 440 Hz đỉnh −6 dBFS từ giây `dau`, dài `dai`, cả file `tong` giây."""
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i",
                    f"aevalsrc='0.5*sin(2*PI*440*t)*between(t,{dau},{dau + dai})':s=44100:d={tong}",
                    "-ac", "1", "-c:a", "pcm_s16le", str(path)], check=True)


@unittest.skipUnless(CO_FFMPEG, "máy không có FFmpeg")
class FfmpegThatTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.mau = am_thanh.tao_mau(Path(cls.tmp.name) / "am")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_mau_du_loai_mono_44100_dinh_dung_muc_va_xac_dinh(self):
        self.assertEqual(sorted(self.mau), sorted(am_thanh.LOAI))
        lan2 = am_thanh.tao_mau(Path(self.tmp.name) / "am-2")
        for loai, path in self.mau.items():
            with self.subTest(loai=loai):
                self.assertEqual(path, Path(self.tmp.name) / "am" / f"{loai}.wav")
                mau, tan = doc_wav(path)
                self.assertEqual(tan, 44100)
                self.assertAlmostEqual(len(mau) / tan, am_thanh.DAI_MAU[loai], delta=0.01)
                self.assertAlmostEqual(dbfs(mau), 20 * math.log10(am_thanh.DINH_MAU[loai]), delta=0.2)
                self.assertEqual(path.read_bytes(), lan2[loai].read_bytes(), "mẫu phải xác định")

    def test_mau_da_co_thi_dung_lai(self):
        path = self.mau["ting"]
        truoc = path.stat().st_mtime_ns
        calls = []
        am_thanh.tao_mau(path.parent, run=lambda *a, **k: calls.append(a))
        self.assertEqual(calls, [])
        self.assertEqual(path.stat().st_mtime_ns, truoc)

    def test_tron_that_hieu_ung_thap_hon_giong_12_db_khong_im_lang_thoi_luong_giu_nguyen(self):
        tmp = Path(self.tmp.name)
        giong = tmp / "g.wav"
        giong_sine(giong, 0.0, 1.0, 1.0)
        wav_giong = tmp / "am-1-giong.wav"
        subprocess.run(ghep.lenh_am_canh(giong, wav_giong, 6.0), check=True)
        # Chồng mọi loại cùng lúc (bút + ting + nhấn + tích tắc) và một ting sát cuối cảnh.
        su_kien = [{"t": 0.0, "loai": "chuyen", "dai": 0}, {"t": 2.4, "loai": "but", "dai": 2.0},
                   {"t": 2.6, "loai": "ting", "dai": 0}, {"t": 2.6, "loai": "nhan", "dai": 0}, {"t": 2.6, "loai": "tictac", "dai": 0},
                   {"t": 3.0, "loai": "tictac", "dai": 0}, {"t": 4.5, "loai": "dung", "dai": 0}, {"t": 5.85, "loai": "ting", "dai": 0}]
        ra = tmp / "am-1.wav"
        dinh = am_thanh.dinh_db(wav_giong)
        self.assertAlmostEqual(dinh, -6.0, delta=0.3)
        subprocess.run(am_thanh.lenh_tron(wav_giong, su_kien, self.mau, ra, 6.0, dinh_giong_db=dinh), check=True)
        mau, tan = doc_wav(ra)
        self.assertEqual(len(mau), round(6.0 * tan), "thời lượng tiếng cảnh không đổi")
        giong_vung = mau[int(1.1 * tan):int(1.9 * tan)]
        hieu_ung = mau[int(2.2 * tan):]
        self.assertAlmostEqual(dbfs(giong_vung), -6.0, delta=0.5, msg="giọng giữ nguyên")
        self.assertLessEqual(dbfs(hieu_ung), dbfs(giong_vung) - 12, "hiệu ứng thấp hơn giọng ít nhất 12 dB")
        self.assertGreater(dbfs(hieu_ung), -45, "hiệu ứng phải nghe được")
        self.assertGreater(dbfs(mau[: int(0.6 * tan)]), -45, "tiếng chuyển cảnh ở đầu cảnh")
        cua = tan // 20
        self.assertEqual([i for i in range(0, len(mau) - cua, cua) if not any(mau[i:i + cua])], [], "không im lặng tuyệt đối")

    def test_dinh_db_doc_dinh_file_wav(self):
        tmp = Path(self.tmp.name)
        g = tmp / "dinh.wav"
        giong_sine(g, 0.0, 0.5, 0.5)
        self.assertAlmostEqual(am_thanh.dinh_db(g), 20 * math.log10(0.5), delta=0.1)


@unittest.skipUnless(co_chromium(), "máy không có Chromium hoặc playwright")
class TrangChromiumTest(unittest.TestCase):
    def test_trang_tra_su_kien_va_chup_song_song_doc_duoc_theo_canh(self):
        text = (f"---\n{META}chuyen-canh: truot\n---\n\n"
                "## Cảnh 1\nloai: tieu-de\nchu: Con lắc ==đơn==\nloi: Chào các em.\n\n"
                "## Cảnh 2\nloai: y-tung-y\ntieu-de: Hai ý\ny: ==Chu kì== tăng\ny: Dây dài\nloi: Chu kì tăng. Dây dài.\n")
        cac_canh = parse.parse(text).canh
        cac_giong = [lich.GiongInfo(mp3=None, giay=g, moc_cau=[0.0], uoc_luong=True, nguon="may") for g in (1.0, 1.5)]
        plan, _ = lich.dung_lich(cac_canh, cac_giong)
        meta = parse.parse(text).meta
        cac_du = [lich.du_lieu_canh(c, cl, None, {"meta": meta}) for c, cl in zip(cac_canh, plan)]
        so_khung = [cl.so_khung for cl in plan]
        with tempfile.TemporaryDirectory() as tmp:
            anh, su = Path(tmp) / "anh", Path(tmp) / "su-kien"
            ket = chup.chup_song_song(cac_du, {}, so_khung, lich.FPS, anh, 1, thu_muc_su_kien=su)
            self.assertEqual(sorted(p.name for p in anh.iterdir()), [f"f{i:06d}.jpg" for i in range(sum(so_khung))])
            with chup.trinh_duyet() as browser:
                page = chup.trang_moi(browser)
                truc_tiep = {}
                for du in cac_du:
                    chup.mo_trang(page, trang.dung_trang(du))
                    truc_tiep[du["so"]] = chup.doc_su_kien(page)
        self.assertEqual(ket, truc_tiep)
        self.assertEqual(sorted(ket), [1, 2])
        for so, ds in ket.items():
            gh = plan[so - 1].thoi_luong
            self.assertTrue(ds, so)
            self.assertEqual(ds, sorted(ds, key=lambda e: e["t"]))
            for e in ds:
                self.assertTrue(0 <= e["t"] <= gh - 0.1 + 1e-9, e)
            self.assertLessEqual(sum(e["dai"] for e in ds if e["loai"] == "but"), 0.4 * gh + 1e-9)
        loai_2 = {e["loai"] for e in ket[2]}
        self.assertTrue({"chuyen", "but", "ting", "nhan"} <= loai_2, loai_2)
        self.assertNotIn("chuyen", {e["loai"] for e in ket[1]})


if __name__ == "__main__":
    unittest.main()


class DocSuKienTest(unittest.TestCase):
    def test_file_su_kien_thieu_hoac_hong_thi_canh_khong_co_hieu_ung(self):
        import tempfile
        from video_ma_parts import chup
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "canh-1.json").write_text('[{"t": 1.0, "loai": "ting", "dai": 0.2}]', encoding="utf-8")
            (Path(tmp) / "canh-2.json").write_text("{hong", encoding="utf-8")
            kq = chup._doc_cac_su_kien([{"so": 1}, {"so": 2}, {"so": 3}], tmp)
        self.assertEqual(len(kq[1]), 1)
        self.assertEqual(kq[2], [])
        self.assertEqual(kq[3], [])

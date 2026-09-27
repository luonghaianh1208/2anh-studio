"""Tích hợp: fixture `video-hieu-ung` (mọi loại cảnh mới, cụm nhấn, số động, luân phiên chuyển cảnh, hiệu ứng âm thanh,
nhạc nền WAV sine tự tạo) dựng không cần mạng. Giọng là sine 440 Hz do test tạo; nhạc là sine 150 Hz.
Phần dựng thật tự bỏ qua nếu máy thiếu Chromium/playwright hoặc FFmpeg/ffprobe."""

import contextlib
import io
import json
import math
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
from video_ma_parts import chup, lich, parse  # noqa: E402

FIXTURE = TOOLS_VI / "fixtures" / "video-hieu-ung"
CO = video_ma.co_chromium() and video_ma.co_ffmpeg()
NEED = "máy thiếu Chromium/playwright hoặc FFmpeg/ffprobe"
# Giọng giả: cảnh 1–6 dài 2,5 s; cảnh 7 (câu hỏi) hỏi 3 s, lời giải 2 s.
GIAY = 2.5
GIAY_HOI, GIAY_GIAI = 3.0, 2.0
GIONG_HZ, NHAC_HZ = 440, 150


def chay(argv) -> tuple:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = video_ma.main([str(a) for a in argv])
    lines = [l for l in out.getvalue().splitlines() if l.strip()]
    assert len(lines) == 1, lines
    return code, json.loads(lines[0]), err.getvalue()


def tao_tieng(path: Path, giay: float) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "lavfi", "-i",
                    f"sine=frequency={GIONG_HZ}:duration={giay}", "-q:a", "9", str(path)], check=True, timeout=60)


def doc_wav(path: Path) -> tuple:
    with wave.open(str(path)) as w:
        assert (w.getnchannels(), w.getsampwidth()) == (1, 2)
        return struct.unpack("<%dh" % w.getnframes(), w.readframes(w.getnframes())), w.getframerate()


def rms_db(mau) -> float:
    if not mau:
        return -120.0
    r = math.sqrt(sum(x * x for x in mau) / len(mau))
    return 20 * math.log10(r / 32768) if r else -120.0


def tieng(video: Path, ra: Path, loc: str = "") -> tuple:
    """Tiếng của video (mono 44,1 kHz, PCM 16 bit), qua bộ lọc `loc` nếu có."""
    cmd = ["ffmpeg", "-y", "-v", "error", "-i", str(video), "-vn", "-ac", "1", "-ar", "44100"]
    if loc:
        cmd += ["-af", loc]
    subprocess.run(cmd + ["-c:a", "pcm_s16le", str(ra)], check=True, timeout=120)
    return doc_wav(ra)


class FixturePlanTest(unittest.TestCase):
    def test_plan_only_passes_and_uses_every_new_feature(self):
        code, data, _ = chay([FIXTURE, "--plan-only"])
        self.assertEqual(code, 0, data)
        self.assertTrue(data["ready"], data)
        self.assertEqual((data["so_canh"], data["warnings"]), (7, []))
        video = parse.parse((FIXTURE / "video.md").read_text(encoding="utf-8"))
        self.assertTrue({"bieu-do", "so-do", "dong-thoi-gian", "cau-hoi", "cong-thuc"} <= {c.loai for c in video.canh})
        self.assertEqual((video.meta["chuyen-canh"], video.meta["am-thanh"], video.meta["chu-dong"], video.meta["phu-de"]),
                         ("luan-phien", "co", "co", "karaoke"))
        self.assertEqual(video.meta["nhac-nen"], "nen.wav")
        self.assertIn("nguon-nhac", video.meta)
        chu = (FIXTURE / "video.md").read_text(encoding="utf-8")
        for dau in ("==", "((", "__", "{{"):
            self.assertIn(dau, chu)
        cong_thuc = next(c for c in video.canh if c.loai == "cong-thuc")
        self.assertIn(" | ", cong_thuc.truong["bieu-thuc"][0])
        # Luân phiên cho đủ năm kiểu chuyển cảnh; cảnh 7 ghi đè bằng `chuyen:`.
        kieu = [lich.kieu_chuyen(c, video.meta) for c in video.canh]
        self.assertEqual(kieu, [None, "lau-bang", "lat-trang", "truot", "phong", "mo-man", "lat-trang"])

    def test_music_is_a_tiny_committed_wav(self):
        nhac = FIXTURE / "nhac" / "nen.wav"
        self.assertLess(nhac.stat().st_size, 20_000)
        with wave.open(str(nhac)) as w:
            self.assertAlmostEqual(w.getnframes() / w.getframerate(), 2.0, places=2)


@unittest.skipUnless(CO, NEED)
class FixtureBuildTest(unittest.TestCase):
    """Dựng thật hai lần (có và không có hiệu ứng âm thanh), mỗi lần 2 tiến trình Chromium."""

    @classmethod
    def dung(cls, ten: str, am_thanh: str) -> tuple:
        thu_muc = Path(cls.tmp.name) / ten
        shutil.copytree(FIXTURE, thu_muc)
        md = thu_muc / "video.md"
        md.write_text(md.read_text(encoding="utf-8").replace("am-thanh: co", f"am-thanh: {am_thanh}"), encoding="utf-8")
        for so in range(1, 7):
            tao_tieng(thu_muc / "giong" / f"canh-{so}.mp3", GIAY)
        tao_tieng(thu_muc / "giong" / "canh-7.mp3", GIAY_HOI)
        tao_tieng(thu_muc / "giong" / "canh-7-giai.mp3", GIAY_GIAI)
        with mock.patch.object(chup, "so_tien_trinh", return_value=2):
            code, data, log = chay([thu_muc])
        return thu_muc, code, data, log

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.co = cls.dung("có hiệu ứng", "co")
        cls.khong = cls.dung("khong hieu ung", "khong")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def setUp(self):
        for _, code, data, _ in (self.co, self.khong):
            self.assertEqual(code, 0, data)

    def test_playable_video_with_expected_duration(self):
        thu_muc, _, data, log = self.co
        self.assertTrue(data["ready"], data)
        self.assertEqual((data["so_canh"], data["giong"]), (7, "co-san"))
        self.assertIn("bằng 2 tiến trình Chromium", log)
        info = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json",
                                          str(thu_muc / "video.mp4")], capture_output=True, text=True, encoding="utf-8",
                                         check=True, timeout=60).stdout)
        kinds = {s["codec_type"]: s for s in info["streams"]}
        self.assertEqual((kinds["video"]["width"], kinds["video"]["height"]), (1920, 1080))  # do-phan-giai mặc định 1080
        self.assertEqual(kinds["video"]["r_frame_rate"], "30/1")
        self.assertIn("audio", kinds)
        cau_hoi = parse.parse((thu_muc / "video.md").read_text(encoding="utf-8")).canh[6]
        expect = 6 * lich.thoi_luong_canh(GIAY) + lich.thoi_luong_cau_hoi(GIAY_HOI, int(cau_hoi.truong["cho"][0]), GIAY_GIAI)
        self.assertAlmostEqual(float(info["format"]["duration"]), expect, delta=0.25)
        self.assertAlmostEqual(data["thoi_luong_giay"], expect, delta=0.05)
        self.assertFalse((thu_muc / ".khung").exists())

    def test_sound_effects_are_audible(self):
        # Hiệu ứng (bút ~3 kHz, ting 1318/2636 Hz, tích tắc 1900 Hz...) nằm trên dải giọng và nhạc: lọc thông cao 1,2 kHz
        # thì bản có hiệu ứng phải mạnh hơn hẳn bản `am-thanh: khong` (cùng giọng, cùng nhạc, cùng nhiễu nền).
        loc = ",".join(["highpass=f=1200"] * 3)
        co, _ = tieng(self.co[0] / "video.mp4", Path(self.tmp.name) / "co-cao.wav", loc)
        khong, _ = tieng(self.khong[0] / "video.mp4", Path(self.tmp.name) / "khong-cao.wav", loc)
        self.__class__.cao = (rms_db(co), rms_db(khong))
        self.assertGreaterEqual(rms_db(co), rms_db(khong) + 10, self.cao)

    def test_music_is_present_and_ducked_under_the_voice(self):
        loc = ",".join([f"bandpass=f={NHAC_HZ}:width_type=q:w=4"] * 3)
        mau, tan = tieng(self.co[0] / "video.mp4", Path(self.tmp.name) / "nhac.wav", loc)

        def muc(a, b):
            return rms_db(mau[int(a * tan):int(b * tan)])

        dau_7 = 6 * lich.thoi_luong_canh(GIAY)
        dem = dau_7 + lich.DAN_DAU + GIAY_HOI  # đếm ngược: không có giọng
        khong_giong = muc(dem + 0.6, dem + 2.8)
        dau_2 = lich.thoi_luong_canh(GIAY)
        co_giong = muc(dau_2 + lich.DAN_DAU + 0.5, dau_2 + lich.DAN_DAU + GIAY - 0.2)
        self.__class__.nhac = (co_giong, khong_giong)
        self.assertGreater(khong_giong, -45, self.nhac)
        self.assertLessEqual(co_giong, khong_giong - 6, self.nhac)

    def test_no_digital_silence(self):
        mau, tan = tieng(self.co[0] / "video.mp4", Path(self.tmp.name) / "tat-ca.wav")
        cua = tan // 20
        self.assertEqual([i / tan for i in range(0, len(mau) - cua, cua) if not any(mau[i:i + cua])], [])


if __name__ == "__main__":
    unittest.main()

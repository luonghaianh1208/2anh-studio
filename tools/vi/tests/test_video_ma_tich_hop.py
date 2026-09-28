"""Tích hợp: dựng video 3 cảnh thật (hình, ảnh, thí nghiệm) với tiếng giả, 2 tiến trình chụp; fixture kể chuyện khổ dọc
cắt dán (vi.12); video viết tay ngang có nền "AI" giả qua `anh_ai.py`. Không gọi mạng. Tự bỏ qua nếu máy thiếu
Chromium/playwright hoặc FFmpeg/ffprobe."""

import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

TOOLS_VI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_VI))

import anh_ai  # noqa: E402
import video_ma  # noqa: E402
from video_ma_parts import chup, lich, parse  # noqa: E402

CO = video_ma.co_chromium() and video_ma.co_ffmpeg()
NEED = "máy thiếu Chromium/playwright hoặc FFmpeg/ffprobe"
ANH_MAU = TOOLS_VI / "fixtures" / "video-hinh" / "anh" / "con-lac.png"
KE_CHUYEN = TOOLS_VI / "fixtures" / "video-ke-chuyen"

VIDEO_MD = """---
tieu-de: Con lắc đơn
mon: Vật lí
lop: 11
phu-de: {phu_de}
---

## Cảnh 1
loai: y-tung-y
tieu-de: Chu kì phụ thuộc vào gì
y: Chiều dài dây l
y: Gia tốc trọng trường g
hinh: ruler-measure
loi: Thứ nhất, chu kì phụ thuộc chiều dài dây. Thứ hai, chu kì phụ thuộc gia tốc trọng trường.

## Cảnh 2
loai: anh
anh: con-lac.png
chu-thich: Con lắc lệch khỏi vị trí cân bằng
nguon: Hình vẽ minh hoạ · CC0 1.0
loi: Đây là con lắc đang dao động.

## Cảnh 3
loai: thi-nghiem
mau: li-con-lac-don
tham-so: 0 chieu-dai 0.4
tham-so: 3 chieu-dai 1.6
do: chu-ki
loi: Hãy quan sát chu kì.
"""


GIAY = (3.0, 2.5, 4.0)


def tao_tieng(path: Path, giay: float) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "lavfi", "-i", f"sine=frequency=440:duration={giay}",
                    "-q:a", "9", str(path)], check=True, timeout=60)


def thong_so(video: Path) -> dict:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(video)],
                         capture_output=True, text=True, encoding="utf-8", check=True, timeout=60).stdout
    return json.loads(out)


@unittest.skipUnless(CO, NEED)
class EndToEndTest(unittest.TestCase):
    def dung(self, ten: str, phu_de: str):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        thu_muc = Path(tmp.name) / ten
        thu_muc.mkdir()
        (thu_muc / "video.md").write_text(VIDEO_MD.format(phu_de=phu_de), encoding="utf-8")
        (thu_muc / "anh").mkdir()
        shutil.copyfile(ANH_MAU, thu_muc / "anh" / "con-lac.png")
        for so, giay in enumerate(GIAY, 1):
            tao_tieng(thu_muc / "giong" / f"canh-{so}.mp3", giay)
        out, err = io.StringIO(), io.StringIO()
        # Hai tiến trình Chromium dù máy có bao nhiêu lõi: mỗi dải tự dựng lại nền lau bảng của cảnh đầu dải.
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), \
                mock.patch.object(chup, "so_tien_trinh", return_value=2):
            code = video_ma.main([str(thu_muc)])
        lines = [l for l in out.getvalue().splitlines() if l.strip()]
        self.assertEqual(len(lines), 1, lines)
        self.nhat_ky = err.getvalue()
        return thu_muc, code, json.loads(lines[0])

    def test_builds_a_playable_video_in_a_hard_folder_name(self):
        thu_muc, code, data = self.dung("Bài 5 – Sulfur dioxide (thử) 'a' 50%", "hinh")
        self.assertEqual(code, 0, data)
        self.assertTrue(data["ready"], data)
        self.assertEqual(data["giong"], "co-san")
        self.assertTrue(any("ước lượng" in w for w in data["warnings"]))
        video = thu_muc / "video.mp4"
        self.assertTrue(video.is_file())
        info = thong_so(video)
        kinds = {s["codec_type"]: s for s in info["streams"]}
        self.assertEqual((kinds["video"]["width"], kinds["video"]["height"]), (1920, 1080))  # do-phan-giai mặc định 1080
        self.assertEqual(kinds["video"]["r_frame_rate"], "30/1")
        self.assertIn("audio", kinds)
        self.assertEqual(data["so_canh"], 3)
        self.assertIn("bằng 2 tiến trình Chromium", self.nhat_ky)
        expect = sum(lich.thoi_luong_canh(g) for g in GIAY)
        self.assertAlmostEqual(float(info["format"]["duration"]), expect, delta=0.25)
        self.assertAlmostEqual(data["thoi_luong_giay"], expect, delta=0.01)
        self.assertFalse((thu_muc / ".khung").exists())
        self.assertEqual((thu_muc / "giong" / "canh-1.mp3").is_file(), True)

    def test_subtitle_file_mode_writes_srt_next_to_the_video(self):
        thu_muc, code, data = self.dung("phu de rieng", "file")
        self.assertEqual(code, 0, data)
        self.assertIn("phu-de.srt", data["files"])
        text = (thu_muc / "phu-de.srt").read_text(encoding="utf-8")
        self.assertIn("Thứ nhất, chu kì phụ thuộc chiều dài dây.", text)

    def test_rerun_after_editing_one_scene_reuses_supplied_voice(self):
        thu_muc, code, _ = self.dung("chay-lai", "khong")
        self.assertEqual(code, 0)
        before = (thu_muc / "giong" / "canh-1.mp3").read_bytes()
        md = thu_muc / "video.md"
        md.write_text(md.read_text(encoding="utf-8").replace("Hãy quan sát chu kì.", "Hãy quan sát kĩ chu kì."), encoding="utf-8")
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(video_ma.main([str(thu_muc)]), 0)
        self.assertEqual((thu_muc / "giong" / "canh-1.mp3").read_bytes(), before)


def chay_video_ma(thu_muc: Path) -> tuple:
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()),             mock.patch.object(chup, "so_tien_trinh", return_value=2):
        code = video_ma.main([str(thu_muc)])
    lines = [l for l in out.getvalue().splitlines() if l.strip()]
    return code, json.loads(lines[-1])


def luong_video(info: dict) -> dict:
    return {s["codec_type"]: s for s in info["streams"]}


@unittest.skipUnless(CO, NEED)
class Vi12EndToEndTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.goc = Path(tmp.name)

    def test_fixture_ke_chuyen_doc_cat_dan_full_hd(self):
        # Fixture: cat-dan, khổ dọc, loạt, người que, 3 cảnh ke-chuyen (mau/…, nhu-canh), khai-niem có thẻ và tài
        # liệu, cong-thuc. Giọng giả: mỗi cảnh một file (coi như giọng thầy cô, không mạng).
        thu_muc = self.goc / "ke chuyen"
        shutil.copytree(KE_CHUYEN, thu_muc)
        video = parse.parse((thu_muc / "video.md").read_text(encoding="utf-8"))
        self.assertEqual((video.meta["kho"], video.meta["phong-cach"], video.meta["nhan-vat"]), ("doc", "cat-dan", "nguoi-que"))
        loai = [c.loai for c in video.canh]
        self.assertEqual(loai.count("ke-chuyen"), 3)
        self.assertIn("nhu", [c.nen["kieu"] for c in video.canh if c.nen])
        giay = (2.0, 3.0, 2.2, 3.5, 2.0)
        self.assertEqual(len(giay), len(video.canh))
        for so, g in enumerate(giay, 1):
            tao_tieng(thu_muc / "giong" / f"canh-{so}.mp3", g)
        code, data = chay_video_ma(thu_muc)
        self.assertEqual(code, 0, data)
        self.assertEqual((data["phong_cach"], data["so_canh"], data["giong"]), ("cat-dan", 5, "co-san"))
        info = thong_so(thu_muc / "video.mp4")
        kinds = luong_video(info)
        self.assertEqual((kinds["video"]["width"], kinds["video"]["height"]), (1080, 1920))
        self.assertEqual(kinds["video"]["r_frame_rate"], "30/1")
        self.assertIn("audio", kinds)
        # Thời lượng khớp lịch ±1 khung: số khung video bằng tổng số khung của lịch.
        so_khung = sum(round(lich.thoi_luong_canh(g) * lich.FPS) for g in giay)
        self.assertLessEqual(abs(int(kinds["video"]["nb_frames"]) - so_khung), 1)
        self.assertAlmostEqual(data["thoi_luong_giay"], so_khung / lich.FPS, delta=1 / lich.FPS)
        self.assertLessEqual(abs(float(info["format"]["duration"]) - so_khung / lich.FPS), 0.1)

    def test_viet_tay_ngang_nen_ai_gia_qua_anh_ai(self):
        # Nền "AI" giả: lavfi → anh/ai/goc/nen-2.png → anh_ai.py nhan → video viết tay ngang Full HD có dòng "tạo bằng AI".
        thu_muc = self.goc / "nen-ai"
        thu_muc.mkdir()
        (thu_muc / "video.md").write_text(VIDEO_AI, encoding="utf-8")
        w: list = []
        ke_hoach = anh_ai.chay_ke_hoach(thu_muc, w)
        self.assertEqual(ke_hoach["so_anh"], 1)
        goc = thu_muc / "anh" / "ai" / "goc"
        goc.mkdir(parents=True)
        subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "lavfi", "-i",
                        "color=c=0x6699CC:s=1920x1080,drawbox=x=0:y=700:w=1920:h=380:color=0x88BB66:t=fill",
                        "-frames:v", "1", str(goc / "nen-2.png")], check=True, timeout=60)
        kq = anh_ai.chay_nhan(thu_muc, w, cong_cu="Thử", mo_hinh="Mô hình giả")
        self.assertIn("anh/ai/nen-2.jpg", kq["files"])
        for so, g in enumerate((2.0, 2.5), 1):
            tao_tieng(thu_muc / "giong" / f"canh-{so}.mp3", g)
        code, data = chay_video_ma(thu_muc)
        self.assertEqual(code, 0, data)
        self.assertEqual(data["phong_cach"], "viet-tay")
        kinds = luong_video(thong_so(thu_muc / "video.mp4"))
        self.assertEqual((kinds["video"]["width"], kinds["video"]["height"]), (1920, 1080))
        self.assertIn("audio", kinds)
        # Trang cảnh cuối mang dòng ghi công ảnh AI (hiện 4 giây cuối video).
        video = parse.parse((thu_muc / "video.md").read_text(encoding="utf-8"))
        html = video_ma._trang_tam(video, thu_muc, {})
        self.assertIn("Hình minh hoạ tạo bằng AI (Mô hình giả)", html[-1])
        self.assertNotIn("Hình minh hoạ tạo bằng AI (Mô hình giả)", html[0])


VIDEO_AI = """---
tieu-de: Con lắc đơn
mon: Vật lí
lop: 11
nhan-vat: nguoi-que
---

## Cảnh 1
loai: y-tung-y
tieu-de: Chu kì phụ thuộc vào gì
y: Chiều dài dây l
y: Gia tốc trọng trường g
loi: Thứ nhất, chiều dài dây. Thứ hai, gia tốc trọng trường.

## Cảnh 2
loai: ke-chuyen
tieu-de: Galileo và chiếc đèn chùm
nen: ve: nhà thờ cổ, đèn chùm treo cao, ánh nắng qua cửa sổ
tu-the: suy-nghi
loi: Vì sao chiếc đèn chùm đung đưa đều đặn như vậy?
"""


if __name__ == "__main__":
    unittest.main()

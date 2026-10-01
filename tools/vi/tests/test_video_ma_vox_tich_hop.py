"""Tích hợp Vox: xem trước (khung giữa + khung cuối mỗi cảnh), dựng thật ra video.mp4 đúng thời lượng, kiểm tràn
Vox (`chong:`, `nhip-k`) nêu lỗi đúng cảnh, ảnh chưa xử lý dừng trước khi chụp, kịch bản cũ (viet-tay) không đổi.
Ảnh xử lý sẵn tạo bằng Pillow, không gọi `anh_vox.py` / mạng. Giọng giả bằng FFmpeg `sine` (như test tích hợp
hiện có). Tự bỏ qua nếu máy thiếu Chromium/playwright hoặc FFmpeg/ffprobe."""

import contextlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS_VI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_VI))

import video_ma  # noqa: E402
from video_ma_parts import lich  # noqa: E402
from tests.test_video_ma_tich_hop import ANH_MAU, VIDEO_MD, chay_video_ma, tao_tieng, thong_so  # noqa: E402

CO = video_ma.co_chromium() and video_ma.co_ffmpeg()
NEED = "máy thiếu Chromium/playwright hoặc FFmpeg/ffprobe"

VIDEO_MD_VOX = """---
tieu-de: Lạm phát
phong-cach: vox
{thoi_luong}---

## Cảnh 1
bo-cuc: mot
loi: Tiền giấy in thêm nhiều sẽ gây ra lạm phát.
nhip: @dau | anh: ve: cốc sứ | giua
nhip: lạm phát | chu: Giá tăng | duoi

## Cảnh 2
bo-cuc: mot
loi: Ngân hàng trung ương kiểm soát điều đó.
nhip: @dau | anh: ve: ngân hàng | giua
nhip: kiểm soát | chu: Kiểm soát | duoi
"""


def _anh_xu_ly(thu_muc: Path, ten: str) -> None:
    from PIL import Image
    d = thu_muc / "anh" / "ai" / "xu-ly"
    d.mkdir(parents=True, exist_ok=True)
    Image.new("RGBA", (400, 300), (10, 20, 30, 255)).save(d / ten)


def du_an_vox(goc: Path, ten: str, thoi_luong: str = "") -> Path:
    """Dự án Vox 2 cảnh, mỗi cảnh một nhịp `anh` đã có ảnh xử lý sẵn trong `anh/ai/vox.json` (không gọi anh_vox.py)."""
    thu_muc = goc / ten
    thu_muc.mkdir()
    (thu_muc / "video.md").write_text(
        VIDEO_MD_VOX.format(thoi_luong=f"thoi-luong: {thoi_luong}\n" if thoi_luong else ""), encoding="utf-8")
    _anh_xu_ly(thu_muc, "canh1-anh.png")
    _anh_xu_ly(thu_muc, "canh2-anh.png")
    (thu_muc / "anh" / "ai" / "vox.json").write_text(json.dumps({
        "1-0": {"file": "ai/xu-ly/canh1-anh.png", "kieu": "cat", "ma": "c1", "mo_hinh": "mo-hinh-thu", "nguon": None},
        "2-0": {"file": "ai/xu-ly/canh2-anh.png", "kieu": "cat", "ma": "c2", "mo_hinh": "mo-hinh-thu", "nguon": None},
    }, ensure_ascii=False), encoding="utf-8")
    return thu_muc


def _chay(thu_muc: Path, *co: str) -> tuple:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = video_ma.main([str(thu_muc), *co])
    lines = [l for l in out.getvalue().splitlines() if l.strip()]
    return code, json.loads(lines[-1])


@unittest.skipUnless(CO, NEED)
class VoxTichHopTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.goc = Path(tmp.name)

    def test_preview_writes_middle_and_end_frames(self):
        thu_muc = du_an_vox(self.goc, "xem-truoc")
        code, data = _chay(thu_muc, "--xem-truoc")
        self.assertEqual(code, 0, data)
        self.assertTrue(data["ready"], data)
        self.assertEqual(data["files"], [
            "xem-truoc/canh-1-giua.png", "xem-truoc/canh-1.png",
            "xem-truoc/canh-2-giua.png", "xem-truoc/canh-2.png",
        ])
        for ten in data["files"]:
            self.assertTrue((thu_muc / ten).is_file(), ten)

    def test_full_render_produces_a_video_with_the_right_length(self):
        thu_muc = du_an_vox(self.goc, "dung-that", thoi_luong="15")
        giay = (5.9, 5.9)
        for so, g in enumerate(giay, 1):
            tao_tieng(thu_muc / "giong" / f"canh-{so}.mp3", g)
        code, data = chay_video_ma(thu_muc)
        self.assertEqual(code, 0, data)
        self.assertTrue(data["ready"], data)
        video = thu_muc / "video.mp4"
        self.assertTrue(video.is_file())
        info = thong_so(video)
        expect = sum(lich.thoi_luong_canh(g) for g in giay)
        self.assertAlmostEqual(float(info["format"]["duration"]), expect, delta=0.1)
        self.assertAlmostEqual(data["thoi_luong_giay"], expect, delta=0.1)
        self.assertFalse(any("mục tiêu `thoi-luong:" in w for w in data["warnings"]), data["warnings"])

    def test_missing_images_stop_before_capture(self):
        thu_muc = du_an_vox(self.goc, "thieu-anh")
        (thu_muc / "anh" / "ai" / "vox.json").unlink()
        code, data = _chay(thu_muc, "--xem-truoc")
        self.assertEqual(code, 1, data)
        self.assertFalse(data["ready"])
        self.assertEqual(data["error"]["step"], "canh")
        self.assertIn("anh_vox.py", data["error"]["fix"])

    def test_old_styles_render_unchanged(self):
        thu_muc = self.goc / "viet-tay"
        thu_muc.mkdir()
        (thu_muc / "video.md").write_text(VIDEO_MD.format(phu_de="hinh"), encoding="utf-8")
        (thu_muc / "anh").mkdir()
        shutil.copyfile(ANH_MAU, thu_muc / "anh" / "con-lac.png")
        code, data = _chay(thu_muc, "--plan-only")
        self.assertEqual(code, 0, data)
        self.assertEqual(data["so_canh"], 3)
        self.assertEqual(data["warnings"], [])
        self.assertAlmostEqual(data["thoi_luong_uoc"], 14.8, delta=0.05)


if __name__ == "__main__":
    unittest.main()

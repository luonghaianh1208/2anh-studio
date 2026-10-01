"""Tích hợp Vox: xem trước (khung giữa + khung cuối mỗi cảnh), dựng thật ra video.mp4 đúng thời lượng, kiểm tràn
Vox (`chong:`, `nhip-k`, `nguon-nhip-k`, `nguon`, `nhac-nguon`, mã lạ) nêu lỗi đúng cảnh, ảnh chưa xử lý dừng trước
khi chụp, kịch bản cũ (viet-tay) không đổi. Ảnh xử lý sẵn tạo bằng Pillow, không gọi `anh_vox.py` / mạng. Giọng giả
bằng FFmpeg `sine`/`anullsrc` (như test tích hợp hiện có). Các test cần Chromium/FFmpeg tự bỏ qua nếu máy thiếu."""

import contextlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

TOOLS_VI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_VI))

import video_ma  # noqa: E402
from video_ma_parts import kiem, lich  # noqa: E402
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

# Dòng nguồn cảnh không có khoảng trắng (một "từ" dài): không thể xuống dòng nên luôn tràn khung dù trong giới hạn
# 90 ký tự của `nguon` (vox.NGUON_DAI) — cách tin cậy để kích hoạt mã `nguon` của kiemTran() mà không cần sửa parse.
VIDEO_MD_VOX_NGUON = """---
tieu-de: T
phong-cach: vox
kho: doc
---

## Cảnh 1
bo-cuc: mot
nguon: {nguon}
loi: Xin chào các bạn.
nhip: @dau | chu: Xin chào | giua
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


class VoxKiemTranKhongChromiumTest(unittest.TestCase):
    """Đơn vị, không cần Chromium: `_kiem_tran_vox` ánh xạ đúng từng mã của `kiemTran()` sang CanhError."""

    def loi(self, tran: list) -> kiem.CanhError:
        canh = SimpleNamespace(so=3)
        with self.assertRaises(kiem.CanhError) as c:
            video_ma._kiem_tran_vox(canh, tran)
        self.assertEqual(c.exception.so, 3)
        return c.exception

    def test_overlap_pair(self):
        exc = self.loi(["chong:nhip-0,nhip-1"])
        self.assertIn("nhip-0", exc.message)
        self.assertIn("nhip-1", exc.message)
        self.assertIn("đè lên nhau", exc.message)

    def test_text_overflow_names_the_one_based_beat(self):
        exc = self.loi(["nhip-2"])
        self.assertIn("nhịp 3", exc.message)
        self.assertIn("tràn ô", exc.message)

    def test_image_source_overflow_names_the_one_based_beat(self):
        exc = self.loi(["nguon-nhip-4"])
        self.assertIn("nhịp 5", exc.message)
        self.assertIn("nguồn ảnh", exc.message)
        self.assertIn("Đổi ảnh", exc.fix)

    def test_scene_source_line_overflow(self):
        exc = self.loi(["nguon"])
        self.assertIn("nguon", exc.message)
        self.assertIn("90 ký tự", exc.fix)

    def test_end_credit_source_overflow_reuses_old_style_fix(self):
        exc = self.loi(["nhac-nguon"])
        self.assertEqual(exc.fix, video_ma.FIX_NGUON_NHAC)
        self.assertIn("nhạc nền", exc.message)

    def test_unknown_id_raises_a_generic_scene_error_instead_of_passing_silently(self):
        exc = self.loi(["mot-ma-la-chua-biet"])
        self.assertIn("mot-ma-la-chua-biet", exc.message)
        self.assertIn("tràn khung", exc.message)

    def test_first_id_in_the_list_wins(self):
        # `kiemTran()` trả nhiều mã cùng lúc; nêu đúng lỗi đầu tiên (thứ tự vox.js đẩy vào), không gộp hay bỏ sót.
        exc = self.loi(["nhip-0", "chong:nhip-1,nhip-2"])
        self.assertIn("nhịp 1", exc.message)


class VieTayPlanOnlyTest(unittest.TestCase):
    """Không cần Chromium/FFmpeg (`--plan-only` không chạm tới): kịch bản viet-tay cũ không đổi."""

    def test_old_styles_render_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            thu_muc = Path(tmp) / "viet-tay"
            thu_muc.mkdir()
            (thu_muc / "video.md").write_text(VIDEO_MD.format(phu_de="hinh"), encoding="utf-8")
            (thu_muc / "anh").mkdir()
            shutil.copyfile(ANH_MAU, thu_muc / "anh" / "con-lac.png")
            code, data = _chay(thu_muc, "--plan-only")
        self.assertEqual(code, 0, data)
        self.assertEqual(data["so_canh"], 3)
        self.assertEqual(data["warnings"], [])
        self.assertAlmostEqual(data["thoi_luong_uoc"], 14.8, delta=0.05)


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

    def test_scene_source_line_overflow_stops_with_a_canh_error(self):
        # Dòng `nguon` không khoảng trắng (một "từ" 85 ký tự, trong giới hạn 90 của vox.NGUON_DAI) không thể xuống
        # dòng nên luôn tràn khung dọc hẹp; `kiemTran()` phải trả mã `nguon` và video_ma phải dừng trước khi dựng.
        thu_muc = self.goc / "nguon-tran"
        thu_muc.mkdir()
        (thu_muc / "video.md").write_text(VIDEO_MD_VOX_NGUON.format(nguon="X" * 85), encoding="utf-8")
        code, data = _chay(thu_muc, "--xem-truoc")
        self.assertEqual(code, 1, data)
        self.assertFalse(data["ready"])
        self.assertEqual(data["error"]["step"], "canh")
        self.assertIn("nguon", data["error"]["message"])
        self.assertIn("90 ký tự", data["error"]["fix"])


if __name__ == "__main__":
    unittest.main()

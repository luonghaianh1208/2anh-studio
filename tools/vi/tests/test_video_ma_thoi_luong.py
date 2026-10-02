"""Ước tính và cảnh báo thời lượng so với `thoi-luong`."""
import json, subprocess, sys, tempfile, unittest
from pathlib import Path

TOOLS_VI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_VI))
from video_ma_parts import kiem, parse, thoi_luong  # noqa: E402


def video(so_canh: int, so_tu: int, them: str = "") -> parse.Video:
    loi = " ".join(["từ"] * (so_tu - 1)) + " cuối."
    canh = "".join(f"## Cảnh {k}\nbo-cuc: mot\nloi: {loi}\nnhip: @dau | chu: A\n\n" for k in range(1, so_canh + 1))
    return parse.parse(f"---\ntieu-de: T\nphong-cach: vox\nnen-canh: khong\ngiong: nu\n{them}---\n\n{canh}")


class UocTinhTest(unittest.TestCase):
    def test_word_count_ignores_markup(self):
        self.assertEqual(thoi_luong.dem_tu("Tiền ==nhiều== lên {{85}} lần, ((rất)) __nhanh__."), 7)

    def test_estimate_matches_the_measured_video(self):
        # Số đo spec mục 7: 9 cảnh, 288 từ → video 115 giây.
        v = video(9, 32)
        self.assertAlmostEqual(thoi_luong.uoc_tinh(v), 288 / 2.7 + 9 * thoi_luong.MOI_CANH_VOX, places=3)

    def test_speed_changes_the_estimate(self):
        nhanh = video(2, 54, "toc-do: nhanh\n")
        self.assertAlmostEqual(thoi_luong.uoc_tinh(nhanh), 108 / 3.1 + 2 * thoi_luong.MOI_CANH_VOX, places=3)


class CanhBaoTest(unittest.TestCase):
    def test_within_band_is_silent(self):
        self.assertIsNone(thoi_luong.canh_bao(60, 66.0, "vua", True))
        self.assertIsNone(thoi_luong.canh_bao(60, 46.0, "vua", True))

    def test_too_long_names_words_to_cut(self):
        w = thoi_luong.canh_bao(60, 115.0, "vua", True)
        self.assertIn("115", w)
        self.assertIn("60", w)
        self.assertIn("bớt khoảng 150 từ", w)   # (115-60)*2.7 = 148.5 → làm tròn chục: 150

    def test_too_short_names_words_to_add(self):
        w = thoi_luong.canh_bao(60, 40.0, "vua", False)
        self.assertIn("thêm khoảng 50 từ", w)   # 20*2.7 = 54 → 50

    def test_measured_vs_estimated_wording(self):
        self.assertIn("ước", thoi_luong.canh_bao(60, 115.0, "vua", True))
        self.assertIn("dài", thoi_luong.canh_bao(60, 115.0, "vua", False))


class KiemVoxTest(unittest.TestCase):
    def test_old_scene_type_checks_do_not_apply_to_vox(self):
        self.assertEqual(kiem.kiem(video(2, 10), Path(".")), [])


class CliTest(unittest.TestCase):
    def test_plan_only_reports_the_estimate(self):
        with tempfile.TemporaryDirectory() as tmp:
            loi = " ".join(["từ"] * 99) + " cuối."
            canh = "".join(f"## Cảnh {k}\nbo-cuc: mot\nloi: {loi}\nnhip: @dau | chu: A\n\n" for k in (1, 2, 3))
            (Path(tmp) / "video.md").write_text(f"---\ntieu-de: T\nphong-cach: vox\nnen-canh: khong\ngiong: nu\nthoi-luong: 60\n---\n\n{canh}",
                                                encoding="utf-8")
            r = subprocess.run([sys.executable, str(TOOLS_VI / "video_ma.py"), tmp, "--plan-only"],
                               capture_output=True, text=True, encoding="utf-8")
            out = json.loads(r.stdout.strip().splitlines()[-1])
        self.assertTrue(out["ready"])
        self.assertTrue(any("bớt khoảng" in w for w in out["warnings"]), out["warnings"])
        self.assertAlmostEqual(out["thoi_luong_uoc"], round(300 / 2.7 + 3 * thoi_luong.MOI_CANH_VOX, 1))


if __name__ == "__main__":
    unittest.main()

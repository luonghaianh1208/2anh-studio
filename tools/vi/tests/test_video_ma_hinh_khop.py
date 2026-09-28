"""Cảnh báo hình không khớp lời (vi.12): cảnh kể chuyện trên nền mẫu phải có thẻ, không quá hai cảnh kể chuyện
liền nhau, nhân vật không đứng một tư thế quá hai cảnh liền."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from video_ma_parts import kiem, parse  # noqa: E402

DAU = "---\ntieu-de: Quy tắc hai phút\nmon: Kỹ năng\nlop: 10\nnhan-vat: nguoi-que\n---\n\n"


def canh(so: int, loai: str, **truong) -> str:
    dong = [f"## Cảnh {so}", f"loai: {loai}"]
    dong += [f"{k.replace('_', '-')}: {v}" for k, v in truong.items()]
    dong.append("loi: Việc nhỏ để sau rồi cộng lại thành núi.")
    return "\n".join(dong) + "\n\n"


def canh_bao(*cac_canh: str) -> list:
    return kiem.canh_bao_hinh_khop_loi(parse.parse(DAU + "".join(cac_canh)))


class HinhKhopLoiTest(unittest.TestCase):
    def test_ke_chuyen_on_a_template_background_without_a_card_warns(self):
        ket = canh_bao(canh(1, "ke-chuyen", tieu_de="Cái bẫy để sau", nen="mau/lop-hoc"))
        self.assertEqual(len(ket), 1, ket)
        self.assertIn("Cảnh 1", ket[0])
        self.assertIn("`the`", ket[0])

    def test_a_card_or_an_ai_background_carries_the_content(self):
        self.assertEqual(canh_bao(
            canh(1, "ke-chuyen", tieu_de="Núi việc", nen="mau/lop-hoc", the="Việc dưới | 2 phút | làm ngay"),
            canh(2, "khai-niem", thuat_ngu="Quy tắc hai phút", dinh_nghia="Việc dưới hai phút thì làm ngay."),
            canh(3, "ke-chuyen", tieu_de="Bàn đầy giấy", nen="ve: bàn học chất chồng giấy tờ thành núi"),
        ), [])

    def test_reusing_a_template_background_is_still_a_template(self):
        ket = canh_bao(
            canh(1, "ke-chuyen", tieu_de="Núi việc", nen="mau/bau-troi", the="Việc | 2 phút | làm ngay"),
            canh(2, "ke-chuyen", tieu_de="Cái bẫy", nen="nhu-canh 1"),
        )
        self.assertEqual(len(ket), 1, ket)
        self.assertIn("Cảnh 2", ket[0])

    def test_a_third_story_scene_in_a_row_warns_once(self):
        the = "Ý | 1 | chú thích"
        ket = canh_bao(*(canh(k, "ke-chuyen", tieu_de=f"Cảnh {k}", nen="mau/vong-tron", the=the,
                              tu_the=("chao", "suy-nghi", "vo-dau", "an-mung")[k - 1]) for k in range(1, 5)))
        self.assertEqual(len(ket), 1, ket)
        self.assertIn("Cảnh 3", ket[0])
        self.assertIn("liền nhau", ket[0])

    def test_the_same_pose_three_scenes_in_a_row_warns(self):
        ket = canh_bao(
            canh(1, "tieu-de", chu="Quy tắc hai phút", tu_the="chao"),
            canh(2, "y-tung-y", tieu_de="Vì sao", y="Việc nhỏ dồn lại", tu_the="chao"),
            canh(3, "y-tung-y", tieu_de="Làm gì", y="Làm ngay", tu_the="chao"),
        )
        self.assertEqual(len(ket), 1, ket)
        self.assertIn("`chao`", ket[0])
        self.assertIn("Cảnh 3", ket[0])

    def test_a_video_without_story_scenes_or_character_has_no_warning(self):
        video = parse.parse("---\ntieu-de: Con lắc\nmon: Vật lí\nlop: 10\n---\n\n"
                            + canh(1, "tieu-de", chu="Con lắc đơn") + canh(2, "khai-niem", thuat_ngu="Chu kì",
                                                                         dinh_nghia="Thời gian một dao động."))
        self.assertEqual(kiem.canh_bao_hinh_khop_loi(video), [])


class HinhKhopLoiCliTest(unittest.TestCase):
    def test_plan_only_reports_the_warning_to_the_agent(self):
        import json
        import subprocess
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            thu_muc = Path(tmp) / "bai"
            thu_muc.mkdir()
            (thu_muc / "video.md").write_text(
                DAU + canh(1, "ke-chuyen", tieu_de="Cái bẫy để sau", nen="mau/lop-hoc"), encoding="utf-8")
            ra = subprocess.run([sys.executable, str(ROOT / "video_ma.py"), str(thu_muc), "--plan-only"],
                                capture_output=True, text=True, encoding="utf-8")
            ket = json.loads(ra.stdout.strip().splitlines()[-1])
        self.assertTrue(ket["ready"], ket)
        self.assertTrue(any("không có `the`" in w for w in ket["warnings"]), ket["warnings"])


if __name__ == "__main__":
    unittest.main()

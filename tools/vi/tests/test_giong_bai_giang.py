"""Test giọng lời giảng (giong_bai_giang.py): chia phụ đề, chọn VieNeu hay lùi về edge-tts. Không gọi giọng thật."""

import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

TOOLS_VI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_VI))

import giong_bai_giang as gbg  # noqa: E402


def tu(chuoi: str, buoc: float = 0.3) -> list:
    return [{"t": round(k * buoc, 3), "d": buoc, "chu": w} for k, w in enumerate(chuoi.split())]


class PhuDeTest(unittest.TestCase):
    def test_moi_cau_mot_dong_khi_ngan(self):
        cues = gbg.cac_dong_phu_de(tu("Xin chào các em. Hôm nay học bài mới."), 5.0)
        self.assertEqual([c.text for c in cues], ["Xin chào các em.", "Hôm nay học bài mới."])
        self.assertEqual(cues[-1].end, 5.0)
        self.assertEqual(cues[1].start, cues[0].end)

    def test_cau_dai_chia_deu_khong_co_tu_mo_coi(self):
        cau = "Kính chào quý thầy cô, quý phụ huynh và các em học sinh."
        cues = gbg.cac_dong_phu_de(tu(cau), 10.0)
        self.assertEqual(" ".join(c.text for c in cues), cau)
        self.assertTrue(all(len(c.text) <= gbg.DONG_TOI_DA for c in cues))
        self.assertGreater(min(len(c.text.split()) for c in cues), 2)


class ChonGiongTest(unittest.TestCase):
    def test_khong_co_vieneu_thi_goi_edge_cung_gioi(self):
        goi = []
        with mock.patch.object(gbg.giong, "co_vieneu", return_value=False), \
                mock.patch.object(gbg, "doc_edge", side_effect=lambda p, g: goi.append(g) or 0):
            self.assertEqual(gbg.main(["du-an", "--giong", "thanh-binh"]), 0)
        self.assertEqual(goi, ["thanh-binh"])
        chay = []
        gbg.doc_edge(Path("du-an"), "thanh-binh", run=lambda cmd: chay.append(cmd) or SimpleNamespace(returncode=0))
        self.assertIn("vi-VN-NamMinhNeural", chay[0])
        gbg.doc_edge(Path("du-an"), "mai-anh", run=lambda cmd: chay.append(cmd) or SimpleNamespace(returncode=0))
        self.assertIn("vi-VN-HoaiMyNeural", chay[1])

    def test_co_vieneu_thi_doc_vieneu(self):
        with mock.patch.object(gbg.giong, "co_vieneu", return_value=True), \
                mock.patch.object(gbg, "doc_vieneu", return_value=0) as doc:
            self.assertEqual(gbg.main(["du-an"]), 0)
        doc.assert_called_once_with(Path("du-an"), "thu-giang", "vua")


if __name__ == "__main__":
    unittest.main()

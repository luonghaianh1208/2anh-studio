"""Test cắt lặng của vieneu_doc.py (chạy bằng Python của VieNeu): giữ đuôi câu, làm nhỏ dần hai đầu.
Venv của repo không có numpy/soundfile thì bỏ qua."""

import sys
import unittest
from pathlib import Path

TOOLS_VI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_VI / "video_ma_parts"))

try:
    import numpy as np
    import vieneu_doc
except ImportError:  # venv của repo không có numpy/soundfile
    vieneu_doc = None


@unittest.skipIf(vieneu_doc is None, "cần numpy và soundfile (Python của VieNeu)")
class CatLangTest(unittest.TestCase):
    def test_giu_duoi_cau_va_lam_nho_dan(self):
        sr = vieneu_doc.SR
        lang = np.zeros(sr, dtype=np.float32)
        tieng = np.full(sr // 2, 0.5, dtype=np.float32)
        a = vieneu_doc.cat_lang(np.concatenate([lang, tieng, lang]))
        # Đuôi giữ DEM_SAU giây sau tiếng (âm cuối nhỏ dần không bị cụt), đầu giữ DEM.
        self.assertAlmostEqual(len(a) / sr, 0.5 + vieneu_doc.DEM + vieneu_doc.DEM_SAU, delta=0.002)
        self.assertGreaterEqual(vieneu_doc.DEM_SAU, 0.15)
        # Hai đầu bằng 0 (nhỏ dần), không có bước nhảy biên độ gây tiếng tách.
        self.assertEqual(float(a[0]), 0.0)
        self.assertEqual(float(a[-1]), 0.0)


if __name__ == "__main__":
    unittest.main()

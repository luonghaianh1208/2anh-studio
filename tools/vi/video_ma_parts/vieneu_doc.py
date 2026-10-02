"""Đọc lời bằng VieNeu. Chạy bằng Python của môi trường VieNeu (không phải venv của repo):

    <VIENEU_PYTHON> vieneu_doc.py viec.json

viec.json: {"giong": "Thu Giang", "nghi": 0.22, "viec": [{"cau": ["Câu một.", "Câu hai."], "ra": "duong-dan.wav"}]}
Mỗi câu đọc riêng, cắt lặng hai đầu, nối lại cách nhau `nghi` giây. stdout một dòng JSON:
{"ket_qua": [{"ra": ..., "giay": tổng giây, "moc": [giây bắt đầu từng câu], "dai": [giây từng câu]}], "sr": 48000}
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

SR = 48000
NGUONG = 0.012   # biên độ coi là lặng khi cắt hai đầu câu
DEM = 0.03       # giữ lại 30 ms trước và sau tiếng


def cat_lang(a: np.ndarray) -> np.ndarray:
    co = np.flatnonzero(np.abs(a) > NGUONG)
    if co.size == 0:
        return a
    dau = max(0, int(co[0] - DEM * SR))
    cuoi = min(len(a), int(co[-1] + DEM * SR))
    return a[dau:cuoi]


def main(path: str) -> int:
    viec = json.loads(Path(path).read_text(encoding="utf-8"))
    from vieneu import Vieneu

    tts = Vieneu()
    nghi = np.zeros(int(float(viec.get("nghi", 0.22)) * SR), dtype=np.float32)
    ket_qua = []
    for v in viec["viec"]:
        doan, moc, dai, t = [], [], [], 0.0
        for k, cau in enumerate(v["cau"]):
            a = cat_lang(np.asarray(tts.infer(cau, voice=viec["giong"]), dtype=np.float32).squeeze())
            if k:
                doan.append(nghi)
                t += len(nghi) / SR
            moc.append(round(t, 3))
            dai.append(round(len(a) / SR, 3))
            doan.append(a)
            t += len(a) / SR
        am = np.concatenate(doan) if doan else np.zeros(1, dtype=np.float32)
        Path(v["ra"]).parent.mkdir(parents=True, exist_ok=True)
        sf.write(v["ra"], am, SR)
        ket_qua.append({"ra": v["ra"], "giay": round(len(am) / SR, 3), "moc": moc, "dai": dai})
        print(f"đã đọc {Path(v['ra']).name} ({len(am) / SR:.1f} s)", file=sys.stderr, flush=True)
    sys.stdout.write(json.dumps({"ket_qua": ket_qua, "sr": SR}, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))

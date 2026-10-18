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
DEM = 0.12       # giữ lại 120 ms trước tiếng: phụ âm đầu nhỏ ("Ng", "Nh") dưới ngưỡng — cắt sát thì mất tiếng đầu
DEM_SAU = 0.18   # và 180 ms sau tiếng: âm cuối, thanh hỏi/ngã nhỏ dần dưới ngưỡng — cắt sát thì cụt tiếng cuối câu
MO = 0.012       # làm to dần / nhỏ dần hai đầu (giây), tránh tiếng tách ở chỗ cắt
# Độ ngẫu nhiên khi sinh giọng: mặc định của VieNeu v3 Turbo là 0,8, giọng dễ "trôi" âm sắc giữa câu; 0,6 đều hơn mà
# vẫn tự nhiên.
NHIET = 0.6


def cat_lang(a: np.ndarray) -> np.ndarray:
    co = np.flatnonzero(np.abs(a) > NGUONG)
    if co.size == 0:
        return a
    dau = max(0, int(co[0] - DEM * SR))
    cuoi = min(len(a), int(co[-1] + DEM_SAU * SR))
    a = a[dau:cuoi].copy()
    n = min(int(MO * SR), len(a) // 2)
    if n:
        ram = np.linspace(0.0, 1.0, n, dtype=a.dtype)
        a[:n] *= ram
        a[-n:] *= ram[::-1]
    return a


# VieNeu hay đọc sai TIẾNG ĐẦU của câu ("Người ta" → "Thế ta", "Thủ phạm" → "Hồ phạm"; đã kiểm bằng nhận dạng giọng):
# đọc kèm tiếng mồi "À, " rồi cắt bỏ mồi ở khoảng lặng của dấu phẩy. Không thấy khoảng lặng thì đọc lại không mồi.
MOI = "À, "
MOI_LANG = 0.06                  # khoảng lặng tối thiểu (giây) sau tiếng mồi
MOI_TRONG = (0.12, 1.2)          # khoảng lặng đó phải nằm trong đoạn này (giây từ đầu)


def bo_moi(a: np.ndarray) -> np.ndarray | None:
    """Cắt phần mồi: tìm khoảng lặng ≥ MOI_LANG đầu tiên sau khi đã có tiếng, trong MOI_TRONG; trả phần sau khoảng
    lặng (None nếu không thấy)."""
    khung = int(0.01 * SR)
    if len(a) < khung * 20:
        return None
    nang = np.sqrt(np.convolve(a.astype(np.float64) ** 2, np.ones(khung) / khung, mode="same"))
    lang = nang < NGUONG
    da_co_tieng, chuoi = False, 0
    for i in range(int(MOI_TRONG[0] * SR), min(len(a), int(MOI_TRONG[1] * SR)), khung):
        if not lang[i]:
            if da_co_tieng and chuoi * khung >= MOI_LANG * SR:
                return a[i - int(DEM * SR):]
            da_co_tieng, chuoi = True, 0
        elif da_co_tieng:
            chuoi += 1
    return None


def doc_cau(tts, cau: str, giong: str) -> np.ndarray:
    tho = np.asarray(tts.infer(MOI + cau, voice=giong, temperature=NHIET), dtype=np.float32).squeeze()
    sau = bo_moi(tho)
    if sau is None:
        sau = np.asarray(tts.infer(cau, voice=giong, temperature=NHIET), dtype=np.float32).squeeze()
    return cat_lang(sau)


def main(path: str) -> int:
    viec = json.loads(Path(path).read_text(encoding="utf-8"))
    from vieneu import Vieneu

    tts = Vieneu()
    nghi = np.zeros(int(float(viec.get("nghi", 0.22)) * SR), dtype=np.float32)
    ket_qua = []
    for v in viec["viec"]:
        doan, moc, dai, t = [], [], [], 0.0
        for k, cau in enumerate(v["cau"]):
            a = doc_cau(tts, cau, viec["giong"])
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

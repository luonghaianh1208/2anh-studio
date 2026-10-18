#!/usr/bin/env python3
"""Giọng đọc lời giảng của video bài giảng từ slide, ưu tiên VieNeu.

    python tools/vi/giong_bai_giang.py <project> [--giong thu-giang] [--toc-do vua]

Đọc `notes/` của dự án (đúng danh sách trang như `notes_to_audio.py`), ghi `audio/<trang>.mp3`, phụ đề
`audio/<trang>.srt` và `audio/manifest.json` cho `svg_to_pptx.py --recorded-narration` và `video.py`.
Máy có VieNeu: đọc mọi trang trong một tiến trình VieNeu. Máy không có VieNeu: gọi `notes_to_audio.py` với giọng
edge-tts cùng giới (dự phòng) và báo một dòng cảnh báo.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from video_ma_parts import giong  # noqa: E402
from video_parts import media, srt  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = REPO_ROOT / "skills" / "ppt-master" / "scripts"
EDGE_DU_PHONG = {"nu": "vi-VN-HoaiMyNeural", "nam": "vi-VN-NamMinhNeural"}
DONG_TOI_DA = 50   # ký tự tối đa của một dòng phụ đề


def _chia_deu(cac_tu: list, n: int) -> list:
    """Chia một câu thành `n` dòng liền nhau, mỗi dòng gần `tổng ký tự / n` (ngắt ở ranh giới từ gần mức nhất)."""
    if n <= 1:
        return [cac_tu]
    tong = sum(len(w["chu"]) + 1 for w in cac_tu)
    ra, dong, da = [], [], 0
    for w in cac_tu:
        if dong and len(ra) < n - 1 and da + (len(w["chu"]) + 1) / 2 > tong * (len(ra) + 1) / n:
            ra.append(dong)
            dong = []
        dong.append(w)
        da += len(w["chu"]) + 1
    return ra + [dong]


def cac_dong_phu_de(tu: list, giay: float) -> list:
    """Mốc từng từ → dòng phụ đề: mỗi câu một dòng; câu dài hơn DONG_TOI_DA ký tự chia thành vài dòng dài gần bằng
    nhau (không để sót một từ mồ côi ở dòng sau). Dòng cuối kéo tới hết tiếng."""
    cau, dang = [], []
    for w in tu:
        dang.append(w)
        if w["chu"][-1:] in ".?!":
            cau.append(dang)
            dang = []
    if dang:
        cau.append(dang)
    cues = []
    for c in cau:
        n = -(-len(" ".join(x["chu"] for x in c)) // DONG_TOI_DA)
        cues.extend(_chia_deu(c, n))
    ra = []
    for i, c in enumerate(cues):
        het = cues[i + 1][0]["t"] if i + 1 < len(cues) else giay
        ra.append(srt.Cue(index=i + 1, start=c[0]["t"], end=max(het, c[0]["t"] + 0.3),
                          text=" ".join(x["chu"] for x in c)))
    return ra


def _danh_sach(project: Path, audio: Path) -> list:
    sys.path.insert(0, str(SCRIPTS))
    import notes_to_audio  # noqa: PLC0415 — script gốc của ppt-master, chỉ dùng danh sách trang và cách lấy lời

    roster = notes_to_audio._expected_note_roster(project)
    if not roster:
        raise ValueError(f"không có lời giảng trong {project / 'notes'}")
    return notes_to_audio._prepare_audio_jobs(roster, audio, ".mp3")


def doc_vieneu(project: Path, giong_khoa: str, toc_do: str) -> int:
    audio = project / "audio"
    jobs = _danh_sach(project, audio)
    audio.mkdir(parents=True, exist_ok=True)
    (audio / "manifest.json").unlink(missing_ok=True)
    print(f"Đọc {len(jobs)} trang bằng giọng {giong.VIENEU_GIONG[giong_khoa]} (VieNeu)...", flush=True)
    viec = [(" ".join(j.text.split()), j.output_path) for j in jobs]
    ket = giong._vieneu_chay(viec, "vieneu:" + giong.VIENEU_GIONG[giong_khoa], toc_do)
    for job, kq in zip(jobs, ket):
        for cu in (".m4a", ".wav"):
            job.output_path.with_suffix(cu).unlink(missing_ok=True)
        giay = media.probe_duration(job.output_path)
        job.output_path.with_suffix(".srt").write_text(srt.render_srt(cac_dong_phu_de(kq["tu"], giay)), encoding="utf-8")
        print(f"[OK] {job.output_path}")
    manifest = {"schema": "ppt-master.narration.v1",
                "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
                "provider": "vieneu", "model": "VieNeu-TTS", "voice_ref": giong.VIENEU_GIONG[giong_khoa],
                "audio_format": "mp3", "subtitles": {"format": "srt", "timing": "word", "max_visible_chars": DONG_TOI_DA}}
    (audio / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[Done] {len(jobs)} trang: {audio}")
    return 0


def doc_edge(project: Path, giong_khoa: str, run=subprocess.run) -> int:
    voice = EDGE_DU_PHONG[giong.VIENEU[giong_khoa][1]]
    print(f"Cảnh báo: máy không có VieNeu nên không dùng được giọng {giong.VIENEU_GIONG[giong_khoa]}; "
          f"đọc bằng giọng edge-tts {voice} (dự phòng).", flush=True)
    return run([sys.executable, str(SCRIPTS / "notes_to_audio.py"), str(project), "--voice", voice]).returncode


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("project", type=Path)
    ap.add_argument("--giong", default="thu-giang", choices=sorted(giong.VIENEU))
    ap.add_argument("--toc-do", dest="toc_do", default="vua", choices=sorted(giong.VIENEU_TEMPO))
    args = ap.parse_args(argv)
    if not giong.co_vieneu():
        return doc_edge(args.project, args.giong)
    try:
        return doc_vieneu(args.project, args.giong, args.toc_do)
    except (ValueError, media.MediaError) as exc:
        print(f"error: {getattr(exc, 'message', exc)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

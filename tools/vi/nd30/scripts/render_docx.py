"""render_docx — render .docx ra PDF (và PNG) để SOI BẰNG MẮT.

nha-van:exempt — đây là mã nguồn, không phải văn bản gửi ra ngoài.

Vì sao cần: validate_docx.py chỉ đo được cái nằm trong XML. Những thứ chỉ mắt thấy được
— Quốc hiệu có nằm bên phải không, gạch chân có cân không, chữ có vỡ font không, có dòng
mồ côi không — bắt buộc phải render rồi xem ảnh.

Usage:
    python3 render_docx.py <file.docx>                 # → PDF cạnh file gốc
    python3 render_docx.py <file.docx> --png           # → PDF + PNG từng trang
    python3 render_docx.py <file.docx> --png --outdir /tmp/soi

Yêu cầu: `soffice` (LibreOffice) cho PDF; `pdftoppm` (poppler-utils) cho PNG.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def _need(cmd: str) -> str:
    path = shutil.which(cmd)
    if not path:
        raise RuntimeError(
            f"thiếu '{cmd}'. Cài: "
            + ("sudo apt install libreoffice-writer" if cmd == "soffice"
               else "sudo apt install poppler-utils")
        )
    return path


def to_pdf(docx_path: Path, outdir: Path) -> Path:
    _need("soffice")
    outdir.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["soffice", "--headless", "--convert-to", "pdf",
         "--outdir", str(outdir), str(docx_path)],
        check=True, capture_output=True,
    )
    pdf = outdir / (docx_path.stem + ".pdf")
    if not pdf.is_file():
        raise RuntimeError(f"soffice chạy xong nhưng không thấy {pdf}")
    return pdf


def to_png(pdf_path: Path, outdir: Path, dpi: int = 110) -> list[Path]:
    _need("pdftoppm")
    prefix = outdir / pdf_path.stem
    subprocess.run(["pdftoppm", "-png", "-r", str(dpi), str(pdf_path), str(prefix)],
                   check=True, capture_output=True)
    return sorted(outdir.glob(f"{pdf_path.stem}-*.png"))


def main() -> int:
    ap = argparse.ArgumentParser(description="Render .docx ra PDF/PNG để soi bằng mắt")
    ap.add_argument("filepath")
    ap.add_argument("--png", action="store_true", help="render tiếp ra PNG từng trang")
    ap.add_argument("--outdir", default=None, help="thư mục xuất (mặc định: cạnh file gốc)")
    ap.add_argument("--dpi", type=int, default=110)
    args = ap.parse_args()

    src = Path(args.filepath).resolve()
    if not src.is_file():
        print(f"ERROR: không thấy file: {src}", file=sys.stderr)
        return 1
    outdir = Path(args.outdir).resolve() if args.outdir else src.parent

    try:
        pdf = to_pdf(src, outdir)
        print(f"PDF: {pdf}")
        if args.png:
            pngs = to_png(pdf, outdir, args.dpi)
            if not pngs:
                print("WARN: không sinh được PNG nào", file=sys.stderr)
                return 1
            for p in pngs:
                print(f"PNG: {p}")
            print("\n→ Bước tiếp: MỞ ẢNH RA XEM (checklist mục B), đừng chỉ tin dòng log này.")
    except (RuntimeError, subprocess.CalledProcessError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

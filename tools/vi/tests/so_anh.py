"""Tiện ích test: đọc kích thước PNG và so điểm ảnh hai ảnh bằng Chromium (không Pillow)."""

from __future__ import annotations

import base64
import struct
from pathlib import Path

_PNG = b"\x89PNG\r\n\x1a\n"


def kich_thuoc_png(path: Path) -> tuple:
    """(rộng, cao) đọc từ khối IHDR."""
    dau = Path(path).read_bytes()[:24]
    if dau[:8] != _PNG or dau[12:16] != b"IHDR":
        raise ValueError(f"{path} không phải PNG")
    return struct.unpack(">II", dau[16:24])


def _data_url(path: Path) -> str:
    return "data:image/png;base64," + base64.b64encode(Path(path).read_bytes()).decode("ascii")


_SO = """async ([a, b, nguong]) => {
  const tai = (u) => new Promise((ok, loi) => { const i = new Image(); i.onload = () => ok(i); i.onerror = loi; i.src = u; });
  const [ia, ib] = await Promise.all([tai(a), tai(b)]);
  if (ia.naturalWidth !== ib.naturalWidth || ia.naturalHeight !== ib.naturalHeight) { return -1; }
  const w = ia.naturalWidth, h = ia.naturalHeight;
  const doc = (i) => { const c = document.createElement('canvas'); c.width = w; c.height = h;
    const g = c.getContext('2d'); g.drawImage(i, 0, 0); return g.getImageData(0, 0, w, h).data; };
  const da = doc(ia), db = doc(ib);
  let lech = 0;
  for (let k = 0; k < da.length; k += 4) {
    if (Math.abs(da[k] - db[k]) > nguong || Math.abs(da[k + 1] - db[k + 1]) > nguong || Math.abs(da[k + 2] - db[k + 2]) > nguong) { lech++; }
  }
  return lech / (w * h);
}"""


def ti_le_lech(page, a: Path, b: Path, nguong: int = 16) -> float:
    """Tỉ lệ điểm ảnh có một kênh màu lệch quá `nguong` mức; -1 nếu hai ảnh khác kích thước."""
    return float(page.evaluate(_SO, [_data_url(a), _data_url(b), nguong]))

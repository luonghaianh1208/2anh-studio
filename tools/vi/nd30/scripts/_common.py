"""Shared helpers for soan-thao-vbhc scripts."""
import sys, io, os, re, unicodedata
from pathlib import Path

# Force UTF-8 stdout for Vietnamese
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")


def slugify_vn(text: str) -> str:
    """Convert Vietnamese text to ASCII slug (no diacritics, lowercase, hyphens)."""
    text = text.replace("đ", "d").replace("Đ", "d")
    nfkd = unicodedata.normalize("NFKD", text)
    ascii_text = "".join(c for c in nfkd if not unicodedata.combining(c))
    ascii_text = ascii_text.lower()
    ascii_text = re.sub(r"[^a-z0-9]+", "-", ascii_text)
    return ascii_text.strip("-")


def next_folder_number(parent: Path) -> str:
    """Find next NNNN number based on existing <NNNN>-<...> folders in parent."""
    parent.mkdir(parents=True, exist_ok=True)
    nums = []
    for child in parent.iterdir():
        if not child.is_dir():
            continue
        m = re.match(r"^(\d{4})-", child.name)
        if m:
            nums.append(int(m.group(1)))
    return f"{(max(nums) + 1) if nums else 1:04d}"


def human_size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}TB"

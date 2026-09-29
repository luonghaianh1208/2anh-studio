"""Load bộ luật thể thức từ YAML kèm theo skill (scripts/rules/<name>.yaml).

Bản gốc (repo vbhc) có thêm tầng cache đồng bộ từ server KB — skill này CỐ Ý bỏ,
vì nguyên tắc thiết kế: chạy được bằng script thuần, không cần server nào.

PyYAML không có sẵn cũng không sao: trả None → caller dùng fallback hardcode trong Python.

API:
    load_rules(name) -> dict | None
    rules_source(name) -> "bundled" | "none"
    clear_cache()
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except ImportError:  # PyYAML chưa cài → fallback hardcode
    yaml = None

_RULES_DIR = Path(__file__).resolve().parent / "rules"

# name → (source_label, parsed_dict)
_loaded: dict[str, tuple[str, dict]] = {}


def load_rules(name: str) -> dict[str, Any] | None:
    """Đọc scripts/rules/<name>.yaml. Trả None nếu không có file hoặc không có PyYAML."""
    if name in _loaded:
        return _loaded[name][1]
    if yaml is None:
        return None
    stem = name.removesuffix(".yaml").removesuffix(".yml")
    for path in (_RULES_DIR / f"{stem}.yaml", _RULES_DIR / f"{stem}.yml"):
        if path.is_file():
            try:
                data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            except yaml.YAMLError:
                continue
            _loaded[name] = ("bundled", data)
            return data
    return None


def rules_source(name: str) -> str:
    if name not in _loaded:
        load_rules(name)
    return _loaded[name][0] if name in _loaded else "none"


def clear_cache():
    _loaded.clear()

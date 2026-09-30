#!/usr/bin/env python3
"""Kiểm tra môi trường 2Anh Studio.

Cách dùng:
    python tools/vi/doctor.py             # kiểm tra đầy đủ, có xuất thử 1 file PPTX
    python tools/vi/doctor.py --no-smoke  # bỏ bước xuất thử
    python tools/vi/doctor.py --json      # in kết quả dạng JSON cho AI đọc (dùng được với --no-smoke)

Mã thoát: 0 khi mọi mục bắt buộc đạt, 1 khi còn mục bắt buộc lỗi.
Chỉ dùng thư viện chuẩn Python.
"""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Iterable, Mapping, Optional, Sequence

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_DIR = REPO_ROOT / "skills" / "ppt-master"
SMOKE_SVG = Path(__file__).resolve().parent / "fixtures" / "smoke" / "01_smoke.svg"
SMOKE_TEXT = "Kiểm tra tiếng Việt"
SMOKE_NAME = "Xuất thử PPTX"
SMOKE_TIMEOUT = 300
FIX_DOC = "docs/vi/xu-ly-loi.md"
MIN_PYTHON = (3, 10)

REQUIRED = "required"
RECOMMENDED = "recommended"
OPTIONAL = "optional"
LEVEL_LABELS = {REQUIRED: "bắt buộc", RECOMMENDED: "khuyến nghị", OPTIONAL: "tuỳ chọn"}

API_KEY_RE = re.compile(r"^[A-Z0-9_]+_API_KEY$")
SLIDE_RE = re.compile(r"ppt/slides/slide\d+\.xml")


@dataclass
class CheckResult:
    name: str
    level: str
    ok: bool
    detail: str
    fix: str = ""


def parse_requirement_names(text: str) -> list[str]:
    """Lấy tên gói từ requirements.txt: bỏ comment, tuỳ chọn pip, phiên bản, marker, extras."""
    names = []
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or line.startswith("-"):
            continue
        name = re.split(r"[\[<>=!~;\s]", line, maxsplit=1)[0]
        if name:
            names.append(name)
    return names


def _run_quiet(run: Callable, cmd: list[str], timeout: int, env: Optional[Mapping[str, str]] = None):
    return run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout, env=env)


def check_python(version_info: Sequence[int] = sys.version_info) -> CheckResult:
    major, minor = version_info[0], version_info[1]
    detail = f"Phiên bản {major}.{minor}"
    if (major, minor) >= MIN_PYTHON:
        return CheckResult("Python", REQUIRED, True, detail)
    return CheckResult("Python", REQUIRED, False, detail + " (cần 3.10 trở lên)", "Cài Python 3.10+ rồi chạy lại CAI-DAT.bat")


def check_packages(
    requirements_path: Path,
    find_dist: Callable[[str], object] = importlib.metadata.distribution,
    name: str = "Thư viện Python",
    level: str = REQUIRED,
    fix: str = "Chạy CAI-DAT.bat để cài thư viện",
) -> CheckResult:
    try:
        packages = parse_requirement_names(requirements_path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeDecodeError):
        return CheckResult(name, level, False, f"Không đọc được {requirements_path.name}",
                           "Tải lại bản đầy đủ của bộ công cụ")
    missing = []
    for package in packages:
        try:
            find_dist(package)
        except importlib.metadata.PackageNotFoundError:
            missing.append(package)
    if missing:
        return CheckResult(name, level, False, "Thiếu: " + ", ".join(missing), fix)
    return CheckResult(name, level, True, f"Đủ {len(packages)} gói")


def check_integrity(run: Callable = subprocess.run, python: str = sys.executable) -> CheckResult:
    name = "Tính toàn vẹn skill"
    fix = "Tải lại bản đầy đủ; không sửa LICENSE, SKILL.md, SPONSORS*.md"
    guard = SKILL_DIR / "scripts" / "attribution_guard.py"
    try:
        proc = _run_quiet(run, [python, str(guard)], timeout=60)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return CheckResult(name, REQUIRED, False, f"Không chạy được kiểm tra: {exc}", fix)
    if proc.returncode == 0:
        return CheckResult(name, REQUIRED, True, "Hợp lệ")
    return CheckResult(name, REQUIRED, False, f"Kiểm tra thất bại (mã {proc.returncode})", fix)


def check_tool(command: str, label: str, level: str, purpose: str, which: Callable[[str], Optional[str]] = shutil.which) -> CheckResult:
    if which(command):
        return CheckResult(label, level, True, "Đã cài")
    return CheckResult(label, level, False, "Chưa cài", purpose)


def default_env_candidates(cwd: Path, home: Path) -> list[Path]:
    """Cùng thứ tự tìm .env với upstream (scripts/config.py)."""
    return [cwd / ".env", SKILL_DIR / ".env", REPO_ROOT / ".env", home / ".ppt-master" / ".env"]


def find_env_file(candidates: Iterable[Path]) -> Optional[Path]:
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def _strip_inline_env_comment(value: str) -> str:
    """Mirrors upstream skills/ppt-master/scripts/config.py:strip_inline_env_comment."""
    stripped = value.lstrip()
    if stripped.startswith(('"', "'")):
        quote = stripped[0]
        end = stripped.find(quote, 1)
        if end != -1:
            head = value[: len(value) - len(stripped) + end + 1]
            tail = value[len(head):]
            hash_pos = tail.find("#")
            if hash_pos == -1:
                return value
            return head + tail[:hash_pos]
        return value
    hash_pos = value.find("#")
    if hash_pos == -1:
        return value
    return value[:hash_pos]


def _strip_env_quotes(value: str) -> str:
    """Mirrors upstream skills/ppt-master/scripts/config.py:strip_env_quotes."""
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    return value


def read_env_file(path: Path) -> dict[str, str]:
    values = {}
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key.startswith("export "):
            key = key[len("export "):].strip()
        cleaned = _strip_inline_env_comment(value).strip()
        values[key] = _strip_env_quotes(cleaned)
    return values


def find_malformed_env_lines(path: Path) -> list[int]:
    """Số dòng (tính từ 1) mà upstream (scripts/config.py) sẽ báo lỗi: thiếu '=' hoặc thiếu tên biến."""
    malformed = []
    try:
        with path.open("r", encoding="utf-8", errors="replace") as f:
            for lineno, raw in enumerate(f, start=1):
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith("export "):
                    line = line[len("export "):].lstrip()
                if "=" not in line or not line.split("=", 1)[0].strip():
                    malformed.append(lineno)
    except OSError:
        return []
    return malformed


def env_file_has_bom(path: Path) -> bool:
    try:
        with path.open("rb") as f:
            return f.read(3) == b"\xef\xbb\xbf"
    except OSError:
        return False


def check_api_keys(
    environ: Mapping[str, str],
    env_values: Mapping[str, str],
    env_has_bom: bool = False,
    malformed_lines: Sequence[int] = (),
) -> CheckResult:
    name = "API key dịch vụ AI"
    if env_has_bom:
        return CheckResult(
            name, OPTIONAL, False,
            "File .env được lưu kèm BOM nên dòng đầu tiên sẽ bị bỏ qua",
            "Mở .env bằng Notepad → File → Save As → Encoding: UTF-8 (không chọn \"UTF-8 with BOM\"), rồi chạy lại KIEM-TRA.bat",
        )
    if malformed_lines:
        numbers = ", ".join(str(number) for number in malformed_lines)
        return CheckResult(
            name, OPTIONAL, False,
            f"Dòng {numbers} trong .env không đúng dạng KEY=VALUE",
            "Sửa các dòng đó thành dạng TÊN_BIẾN=giá_trị (xem docs/vi/lay-api-key.md), rồi chạy lại KIEM-TRA.bat",
        )
    merged = dict(env_values)
    merged.update(environ)
    count = sum(1 for key, value in merged.items() if API_KEY_RE.match(key) and value.strip())
    if count:
        return CheckResult(name, OPTIONAL, True, f"Đã cấu hình {count} key")
    return CheckResult(
        name, OPTIONAL, False,
        "Chưa có key (chỉ cần khi tạo ảnh AI hoặc dùng giọng đọc đám mây)",
        "Xem docs/vi/lay-api-key.md",
    )


def verify_pptx(pptx: Path, expected_text: str = SMOKE_TEXT) -> CheckResult:
    fix = f"Xem {FIX_DOC}"
    if not pptx.is_file():
        return CheckResult(SMOKE_NAME, REQUIRED, False, "Không tạo được file PPTX", fix)
    try:
        with zipfile.ZipFile(pptx) as archive:
            slides = [item for item in archive.namelist() if SLIDE_RE.fullmatch(item)]
            if len(slides) != 1:
                return CheckResult(SMOKE_NAME, REQUIRED, False, f"Số slide sai: {len(slides)}", fix)
            xml = archive.read(slides[0]).decode("utf-8", errors="replace")
    except zipfile.BadZipFile:
        return CheckResult(SMOKE_NAME, REQUIRED, False, "File PPTX bị hỏng", fix)
    except OSError:
        return CheckResult(SMOKE_NAME, REQUIRED, False, "Không đọc được file PPTX", fix)
    if expected_text not in xml:
        return CheckResult(SMOKE_NAME, REQUIRED, False, "Chữ tiếng Việt bị lỗi trong slide", fix)
    return CheckResult(SMOKE_NAME, REQUIRED, True, "Tạo được PPTX 1 slide, tiếng Việt hiển thị đúng")


def run_smoke(run: Callable = subprocess.run, python: str = sys.executable) -> CheckResult:
    fix = f"Xem {FIX_DOC}"
    scripts = SKILL_DIR / "scripts"
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    with tempfile.TemporaryDirectory(prefix="pptmaster-vi-smoke-", ignore_cleanup_errors=True) as tmp:
        project = Path(tmp)
        (project / "svg_output").mkdir()
        try:
            shutil.copyfile(SMOKE_SVG, project / "svg_output" / SMOKE_SVG.name)
        except OSError as exc:
            return CheckResult(
                SMOKE_NAME, REQUIRED, False,
                f"Không chép được file mẫu smoke test: {exc}",
                "Tải lại bản đầy đủ của bộ công cụ",
            )
        pptx = project / "smoke.pptx"
        steps = [
            [python, str(scripts / "finalize_svg.py"), str(project), "-q"],
            [python, str(scripts / "svg_to_pptx.py"), str(project), "-s", "final", "-o", str(pptx),
             "--no-notes", "--no-animations", "-q"],
        ]
        for cmd in steps:
            script = Path(cmd[1]).name
            try:
                proc = _run_quiet(run, cmd, timeout=SMOKE_TIMEOUT, env=env)
            except subprocess.TimeoutExpired:
                return CheckResult(SMOKE_NAME, REQUIRED, False, f"Quá thời gian khi chạy {script}", fix)
            except OSError as exc:
                return CheckResult(SMOKE_NAME, REQUIRED, False, f"Không chạy được {script}: {exc}", fix)
            if proc.returncode != 0:
                tail = (proc.stderr or proc.stdout or "").strip().splitlines()[-3:]
                return CheckResult(SMOKE_NAME, REQUIRED, False, f"{script} lỗi (mã {proc.returncode}): " + " | ".join(tail), fix)
        return verify_pptx(pptx)


def exit_code(results: Iterable[CheckResult]) -> int:
    return 1 if any(result.level == REQUIRED and not result.ok for result in results) else 0


def _icon(result: CheckResult) -> str:
    if result.ok:
        return "✅ [ĐẠT]"
    return "❌ [LỖI]" if result.level == REQUIRED else "⚠️ [CẢNH BÁO]"


def render(results: Sequence[CheckResult]) -> str:
    lines = ["Kiểm tra môi trường 2Anh Studio", ""]
    for result in results:
        lines.append(f"{_icon(result)} {result.name} ({LEVEL_LABELS[result.level]}): {result.detail}")
        if not result.ok and result.fix:
            lines.append(f"   → {result.fix}")
    lines.append("")
    if exit_code(results) == 0:
        lines.append("Kết quả: sẵn sàng sử dụng.")
    else:
        lines.append(f"Kết quả: còn lỗi bắt buộc. Xem hướng dẫn trong {FIX_DOC}")
    return "\n".join(lines)


def render_json(results: Sequence[CheckResult], python: str = sys.executable) -> str:
    payload = {
        "ready": exit_code(results) == 0,
        "python": python,
        "checks": [asdict(result) for result in results],
    }
    return json.dumps(payload, ensure_ascii=False)


def collect(no_smoke: bool) -> list[CheckResult]:
    python_result = check_python()
    results = [python_result]
    if not python_result.ok:
        return results
    packages = check_packages(SKILL_DIR / "requirements.txt")
    integrity = check_integrity()
    results += [packages, integrity]
    results.append(check_packages(
        REPO_ROOT / "tools" / "vi" / "requirements-vi.txt",
        name="Thư viện lớp Việt",
        level=RECOMMENDED,
        fix="Chạy: python -m pip install -r tools/vi/requirements-vi.txt (hoặc chạy lại CAI-DAT.bat)",
    ))
    if not no_smoke:
        if packages.ok and integrity.ok:
            results.append(run_smoke())
        else:
            results.append(CheckResult(SMOKE_NAME, REQUIRED, False, "Bỏ qua vì còn lỗi ở trên", "Sửa các lỗi phía trên trước"))
    results.append(check_tool("git", "Git", RECOMMENDED, "Cần để cập nhật bằng CAP-NHAT.bat"))
    results.append(check_tool("pandoc", "Pandoc", OPTIONAL, "Chỉ cần khi chuyển tài liệu định dạng cũ"))
    results.append(check_tool("ffmpeg", "FFmpeg", OPTIONAL, "Chỉ cần cho thuyết minh và video"))
    env_file = find_env_file(default_env_candidates(Path.cwd(), Path.home()))
    results.append(check_api_keys(
        os.environ,
        read_env_file(env_file) if env_file else {},
        env_has_bom=env_file_has_bom(env_file) if env_file else False,
        malformed_lines=find_malformed_env_lines(env_file) if env_file else (),
    ))
    return results


def _configure_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def main(argv: Optional[Sequence[str]] = None) -> int:
    _configure_utf8()
    parser = argparse.ArgumentParser(description="Kiểm tra môi trường 2Anh Studio")
    parser.add_argument("--no-smoke", action="store_true", help="Bỏ bước xuất thử PPTX")
    parser.add_argument("--json", action="store_true", help="In kết quả dạng JSON cho AI đọc")
    args = parser.parse_args(argv)
    results = collect(args.no_smoke)
    print(render_json(results) if args.json else render(results))
    return exit_code(results)


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Xuất văn bản hành chính đúng thể thức Nghị định 30 ra file Word.

Cách dùng:
    python tools/vi/van_ban.py <thư_mục> [--nhap]

Đọc <thư_mục>/noi-dung.json (schema tools/vi/nd30/schemas/nd30-input.schema.json),
dựng van-ban.docx bằng bộ mã ND30 đã nhúng, chạy bộ kiểm thể thức của ND30 rồi ghi
kiem-tra.md. stdout: đúng một dòng JSON. Mã thoát: 0 khi xuất xong, 1 khi lỗi.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import re
import sys
import tempfile
from pathlib import Path

ND30_SCRIPTS = Path(__file__).resolve().parent / "nd30" / "scripts"
SOURCE_NAME = "noi-dung.json"
DOCX_NAME = "van-ban.docx"
REPORT_NAME = "kiem-tra.md"
ERROR_STEPS = ("input", "json", "the-thuc", "docx", "write", "internal")
REMINDER = "Văn bản chưa đóng dấu, chưa ký; soát và điền đủ trước khi ban hành."
BLANK_RE = re.compile(r"\[CẦN BỔ SUNG[^\]]*\]?|\?\?\?")

PROFILES = {
    "administrative": "văn bản hành chính gửi ra ngoài: đủ 9 thành phần thể thức, khổ A4, lề, "
                      "font Times New Roman, chữ đen, không bullet tự động, không tô nền bảng, "
                      "bắt buộc Nơi nhận và Lưu",
    "bieu-mau-noi-bo": "biểu mẫu nội bộ (phiếu): như văn bản hành chính nhưng miễn Số và Nơi nhận",
    "minutes-administrative": "biên bản có thể thức hành chính: như văn bản hành chính",
    "academic": "tài liệu học thuật, không phải văn bản hành chính: chỉ kiểm A4, font, màu chữ",
    "general": "tài liệu nội bộ tự do: chỉ kiểm A4, lề, font, màu chữ và ô còn sót",
}
BODY_FIELDS = {
    "heading": {"text": str},
    "paragraph": {"text": str},
    "bullet": {"text": str},
    "table": {"headers": list, "rows": list},
    "can_cu": {"items": list},
    "centered": {"text": str},
    "italic_paragraph": {"text": str},
}
HEADER_REQUIRED = ("co_quan_chu_quan", "co_quan_ban_hanh", "ky_hieu", "trich_yeu", "dia_danh")
QUYEN_HAN = ("", "KT.", "TL.", "TUQ.", "TM.")

FIX_SOURCE = (
    f"Viết file {SOURCE_NAME} trong thư mục văn bản theo "
    "docs/vi/tro-ly/van-ban-hanh-chinh.md rồi chạy lại."
)
FIX_JSON = (
    f"Sửa đúng chỗ đó trong {SOURCE_NAME} theo tools/vi/nd30/schemas/nd30-input.schema.json "
    "(xem ví dụ đúng loại trong tools/vi/nd30/examples/) rồi chạy lại."
)
FIX_THE_THUC = (
    f"Đọc các mục ✗ trong {REPORT_NAME}, sửa {SOURCE_NAME} cho đúng thể thức rồi chạy lại."
)
FIX_WRITE = "Đóng file Word đang mở rồi chạy lại."
FIX_INTERNAL = "Gửi nguyên dòng error.message cho người bảo trì."
FIX_ARGS = "Chạy: python tools/vi/van_ban.py <thư_mục> [--nhap]"


class ArgumentError(Exception):
    """Tham số dòng lệnh sai; báo bằng JSON thay vì để argparse tự thoát."""


class JsonArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ArgumentError(message)


class SpecError(ValueError):
    """noi-dung.json sai schema; message nêu đúng trường."""


def log(text: str) -> None:
    print(text, file=sys.stderr, flush=True)


def emit(payload: dict) -> None:
    """In đúng một dòng JSON và không bao giờ ném lỗi."""
    text = json.dumps(payload, ensure_ascii=False) + "\n"
    try:
        try:
            sys.stdout.write(text)
        except UnicodeEncodeError:
            buffer = getattr(sys.stdout, "buffer", None)
            if buffer is not None:
                buffer.write(text.encode("utf-8", errors="replace"))
            else:
                sys.stdout.write(json.dumps(payload, ensure_ascii=True) + "\n")
        sys.stdout.flush()
    except OSError:
        pass


def configure_streams() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


def result(*, ready: bool, files=(), loai: str = "", profile: str = "", blanks: int = 0,
           draft: bool = False, counts: dict | None = None, warnings=(),
           error: dict | None = None) -> dict:
    return {
        "ready": ready,
        "files": [str(path) for path in files],
        "loai_van_ban": loai,
        "profile": profile,
        "so_o_can_bo_sung": blanks,
        "ban_nhap": draft,
        "kiem_tra": counts or {"dat": 0, "canh_bao": 0, "loi": 0},
        "warnings": list(warnings),
        "error": error,
    }


def failure(step: str, message: str, fix: str, **rest) -> dict:
    return result(ready=False, error={"step": step, "message": message, "fix": fix}, **rest)


# ---------------------------------------------------------------- schema

def _need(obj: dict, key: str, kind, path: str, required: bool = False) -> None:
    if key not in obj:
        if required:
            raise SpecError(f"Thiếu trường bắt buộc {path}")
        return
    kinds = kind if isinstance(kind, tuple) else (kind,)
    value = obj[key]
    if isinstance(value, bool) and bool not in kinds:
        raise SpecError(f"Trường {path} sai kiểu")
    if not isinstance(value, kinds):
        raise SpecError(f"Trường {path} sai kiểu")


def check_spec(spec) -> None:
    """Kiểm noi-dung.json theo schema ND30, nêu đúng tên trường đầu tiên sai."""
    if not isinstance(spec, dict):
        raise SpecError("Gốc của noi-dung.json phải là một đối tượng {...}")
    profile = spec.get("profile", "administrative")
    if profile not in PROFILES:
        raise SpecError(
            f"Trường profile nhận {profile!r}; chỉ nhận: " + ", ".join(PROFILES)
        )
    _need(spec, "header", dict, "header", required=True)
    header = spec["header"]
    for key in HEADER_REQUIRED:
        _need(header, key, str, f"header.{key}", required=True)
    for key in ("so_vb", "ten_loai_in_hoa"):
        _need(header, key, str, f"header.{key}")
    for key in ("ngay", "thang", "nam"):
        _need(header, key, (str, int), f"header.{key}")
    _need(header, "is_cong_van", bool, "header.is_cong_van")
    _need(spec, "kinh_gui", str, "kinh_gui")
    _need(spec, "ket_thuc", str, "ket_thuc")
    _need(spec, "body", list, "body")
    for index, item in enumerate(spec.get("body", [])):
        where = f"body[{index}]"
        if not isinstance(item, dict):
            raise SpecError(f"Trường {where} phải là một đối tượng {{...}}")
        kind = item.get("type", "paragraph")
        if kind not in BODY_FIELDS:
            raise SpecError(
                f"Trường {where}.type nhận {kind!r}; chỉ nhận: " + ", ".join(BODY_FIELDS)
            )
        for key, value_type in BODY_FIELDS[kind].items():
            _need(item, key, value_type, f"{where}.{key}", required=True)
        _need(item, "level", int, f"{where}.level")
    _need(spec, "signature", dict, "signature")
    signature = spec.get("signature") or {}
    _need(signature, "noi_nhan_items", list, "signature.noi_nhan_items")
    for key in ("phong_viet_tat", "chuc_vu", "nguoi_ky", "quyen_han", "chuc_vu_thay"):
        _need(signature, key, str, f"signature.{key}")
    if signature.get("quyen_han", "") not in QUYEN_HAN:
        raise SpecError(
            "Trường signature.quyen_han chỉ nhận: " + ", ".join(repr(v) for v in QUYEN_HAN)
        )


def document_kind(header: dict) -> str:
    if header.get("is_cong_van"):
        return "Công văn"
    name = str(header.get("ten_loai_in_hoa", "")).strip()
    if not name:
        return "Chưa rõ loại"
    lower = name.lower()
    return lower[0].upper() + lower[1:]


def _place(path: tuple) -> str:
    if not path:
        return "văn bản"
    head = path[0]
    if head == "header":
        return "phần đầu (" + ".".join(str(p) for p in path[1:]) + ")"
    if head == "body" and len(path) > 1:
        return f"nội dung, khối {path[1] + 1}"
    if head == "signature":
        return "phần ký"
    if head == "kinh_gui":
        return "dòng Kính gửi"
    return str(head)


def find_blanks(value, path: tuple = ()) -> list[tuple[str, str]]:
    """Mọi ô `[CẦN BỔ SUNG...]` và `???` trong JSON, theo thứ tự xuất hiện."""
    found: list[tuple[str, str]] = []
    if isinstance(value, str):
        for match in BLANK_RE.finditer(value):
            found.append((_place(path), match.group(0)))
    elif isinstance(value, dict):
        for key, child in value.items():
            if key != "profile":
                found.extend(find_blanks(child, path + (key,)))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(find_blanks(child, path + (index,)))
    return found


# ---------------------------------------------------------------- ND30

def load_nd30():
    """Import muộn bộ mã ND30; mọi thứ nó in khi nạp đều bị giữ lại, không ra stdout."""
    scripts = str(ND30_SCRIPTS)
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    with contextlib.redirect_stdout(io.StringIO()):
        import generate_docx
        import validate_docx
    return generate_docx, validate_docx


def run_validator(vd, path: Path, profile: str, allow_placeholder: bool) -> list:
    with contextlib.redirect_stdout(io.StringIO()):
        return list(vd.run_checks(path, profile, allow_placeholder))


def classify(vd, strict: list, lenient: list) -> list[tuple[str, str, str, bool]]:
    """Gắn cờ mục lỗi nặng chỉ vì ô cần bổ sung (hết lỗi khi cho phép placeholder)."""
    lenient_fail = {(label, i) for i, (st, label, _) in enumerate(lenient) if st == vd.FAIL}
    rows = []
    for i, (status, label, detail) in enumerate(strict):
        blank_only = status == vd.FAIL and (label, i) not in lenient_fail
        rows.append((status, label, detail, blank_only))
    return rows


def _cell(text: str) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ")


def build_report(*, kind: str, trich_yeu: str, profile: str, rows, blanks, verdict: str,
                 vd) -> str:
    marks = {vd.OK: "✓", vd.WARN: "⚠", vd.FAIL: "✗"}
    lines = [
        f"# Kiểm tra thể thức — {kind}",
        "",
        f"- Loại văn bản: {kind}",
    ]
    if trich_yeu:
        lines.append(f"- Trích yếu: {trich_yeu}")
    lines += [
        f"- Luật thể thức đã áp: Nghị định 30/2020/NĐ-CP, bộ kiểm `{profile}` "
        f"({PROFILES[profile]}).",
        f"- Kết quả: {verdict}",
        "",
        "## Từng mục kiểm",
        "",
        "| Kết quả | Mục | Chi tiết |",
        "|---|---|---|",
    ]
    for status, label, detail, blank_only in rows:
        mark = "⚠" if blank_only else marks.get(status, status)
        note = " (ô cần bổ sung)" if blank_only else ""
        lines.append(f"| {mark} | {_cell(label)} | {_cell(detail)}{note} |")
    lines += ["", "## Ô cần bổ sung", ""]
    if blanks:
        for number, (place, text) in enumerate(blanks, 1):
            lines.append(f"{number}. {place}: `{text}`")
    else:
        lines.append("Không còn ô nào.")
    lines += ["", REMINDER, ""]
    return "\n".join(lines)


def write_text_atomic(target: Path, text: str) -> None:
    fd, tmp = tempfile.mkstemp(prefix=".tmp-", suffix=target.suffix, dir=target.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        os.replace(tmp, target)
    except BaseException:
        with contextlib.suppress(OSError):
            os.remove(tmp)
        raise


# ---------------------------------------------------------------- run

def run(args) -> int:
    folder = args.folder.expanduser().resolve()
    if not folder.is_dir():
        emit(failure("input", f"Không có thư mục văn bản: {folder}", FIX_SOURCE))
        return 1
    source = folder / SOURCE_NAME
    if not source.is_file():
        emit(failure("input", f"Không có file {SOURCE_NAME} trong {folder}", FIX_SOURCE))
        return 1
    try:
        text = source.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError) as exc:
        emit(failure("input", f"Không đọc được {source}: {exc}",
                     f"Lưu lại {SOURCE_NAME} bằng bảng mã UTF-8 rồi chạy lại."))
        return 1

    try:
        spec = json.loads(text)
    except json.JSONDecodeError as exc:
        emit(failure("json", f"{SOURCE_NAME} sai cú pháp JSON ở dòng {exc.lineno}, "
                             f"cột {exc.colno}: {exc.msg}", FIX_JSON))
        return 1
    try:
        check_spec(spec)
    except SpecError as exc:
        emit(failure("json", f"{SOURCE_NAME}: {exc}", FIX_JSON))
        return 1

    profile = spec.get("profile", "administrative")
    header = spec["header"]
    kind = document_kind(header)
    blanks = find_blanks(spec)
    info = {"loai": kind, "profile": profile, "blanks": len(blanks)}

    try:
        gd, vd = load_nd30()
    except ImportError as exc:
        if getattr(exc, "name", None) in ("docx", "lxml"):
            emit(failure("docx", f"Chưa cài thư viện python-docx ({exc})",
                         f'Cài thư viện bằng: "{sys.executable}" -m pip install -r '
                         "tools/vi/requirements-vi.txt (hoặc chạy lại CAI-DAT.bat)", **info))
        else:
            emit(failure("internal", f"Lỗi khi nạp bộ mã ND30: {exc}", FIX_INTERNAL, **info))
        return 1

    target = folder / DOCX_NAME
    report_path = folder / REPORT_NAME
    fd, tmp_name = tempfile.mkstemp(prefix=".tmp-", suffix=".docx", dir=folder)
    os.close(fd)
    tmp = Path(tmp_name)
    try:
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                gd.generate(spec).save(str(tmp))
        except OSError as exc:
            emit(failure("write", f"Không ghi được file Word: {exc}", FIX_WRITE, **info))
            return 1
        except Exception as exc:  # noqa: BLE001
            emit(failure("internal", f"Lỗi khi dựng file Word: {exc}", FIX_INTERNAL, **info))
            return 1

        strict = run_validator(vd, tmp, profile, False)
        lenient = run_validator(vd, tmp, profile, True)
        rows = classify(vd, strict, lenient)
        real = [(label, detail) for st, label, detail, blank in rows if st == vd.FAIL and not blank]
        blank_fail = [(label, detail) for st, label, detail, blank in rows if blank]
        draft = bool(blanks or blank_fail)
        counts = {
            "dat": sum(1 for r in rows if r[0] == vd.OK),
            "canh_bao": sum(1 for r in rows if r[0] == vd.WARN or r[3]),
            "loi": len(real),
        }

        warnings: list[str] = []
        if draft:
            number = len(blanks) or len(blank_fail)
            if args.nhap:
                warnings.append(f"Bản nháp có chủ đích (--nhap): còn {number} ô cần bổ sung; "
                                "thầy cô điền đủ rồi chạy lại trước khi ban hành.")
            else:
                warnings.append(f"Bản nháp: còn {number} ô cần bổ sung; chưa phải thành phẩm, "
                                "điền đủ rồi chạy lại trước khi ban hành.")
            for place, value in blanks:
                warnings.append(f"Ô cần bổ sung ở {place}: {value}")
            if not blanks:
                for label, detail in blank_fail:
                    warnings.append(f"{label}: {detail}")
        for status, label, detail, _ in rows:
            if status == vd.WARN:
                warnings.append(f"{label}: {detail}")

        if real:
            verdict = "Có lỗi thể thức nặng — chưa xuất văn bản."
        elif draft:
            verdict = "Bản nháp — còn ô cần bổ sung."
        else:
            verdict = "Đạt các mục bộ kiểm tra được."
        report = build_report(kind=kind, trich_yeu=str(header.get("trich_yeu", "")),
                              profile=profile, rows=rows, blanks=blanks, verdict=verdict, vd=vd)

        try:
            if real:
                tmp.unlink()
                if target.exists():
                    target.unlink()
            else:
                os.replace(tmp, target)
            write_text_atomic(report_path, report)
        except PermissionError as exc:
            emit(failure("write", f"Không ghi được file: {exc}", FIX_WRITE, **info))
            return 1
        except OSError as exc:
            emit(failure("write", f"Không ghi được file: {exc}",
                         FIX_WRITE + " Kiểm tra ổ đĩa còn trống.", **info))
            return 1
    finally:
        with contextlib.suppress(OSError):
            if tmp.exists():
                tmp.unlink()

    if real:
        labels = "; ".join(f"{label} ({detail})" for label, detail in real)
        emit(failure("the-thuc", f"Bộ kiểm thể thức ND30 báo lỗi nặng: {labels}", FIX_THE_THUC,
                     files=[report_path], draft=draft, counts=counts, warnings=warnings, **info))
        return 1

    log(f"Đã xuất {target.name} và {report_path.name}.")
    emit(result(ready=True, files=[target, report_path], draft=draft, counts=counts,
                warnings=warnings, **info))
    return 0


def main(argv: list[str] | None = None) -> int:
    configure_streams()
    parser = JsonArgumentParser(description="Xuất văn bản hành chính theo Nghị định 30")
    parser.add_argument("folder", type=Path, help=f"Thư mục chứa {SOURCE_NAME}")
    parser.add_argument("--nhap", action="store_true",
                        help="Ghi rõ đây là bản nháp có chủ đích; vẫn chạy đủ kiểm tra")
    try:
        args = parser.parse_args(argv)
    except ArgumentError as exc:
        emit(failure("input", f"Tham số không hợp lệ: {exc}", FIX_ARGS))
        return 1
    try:
        return run(args)
    except Exception as exc:  # noqa: BLE001 - stdout không bao giờ được để trống
        emit(failure("internal", f"Lỗi ngoài dự kiến: {exc}", FIX_INTERNAL))
        return 1


if __name__ == "__main__":
    sys.exit(main())

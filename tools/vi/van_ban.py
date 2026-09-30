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
import unicodedata
from pathlib import Path

ND30_SCRIPTS = Path(__file__).resolve().parent / "nd30" / "scripts"
SOURCE_NAME = "noi-dung.json"
DOCX_NAME = "van-ban.docx"
REPORT_NAME = "kiem-tra.md"
ERROR_STEPS = ("input", "json", "the-thuc", "docx", "write", "internal")
REMINDER = "Văn bản chưa đóng dấu, chưa ký; soát và điền đủ trước khi ban hành."
BLANK_RE = re.compile(r"\[CẦN BỔ SUNG[^\]]*\]?|\?\?\?", re.IGNORECASE)
SUSPECT_RE = re.compile(r"…{2,}|\.{4,}|…\s*/\s*…|\bX{2}/X{2}\b|\[CAN BO SUNG[^\]]*\]?", re.IGNORECASE)
CHECK_VALUES_PREFIX = "Thầy cô đối chiếu"
# Từ 1/7/2025 chính quyền địa phương còn 2 cấp (tỉnh, xã/phường): không còn huyện, quận, thị xã, thị trấn.
OLD_UNIT_RE = re.compile(r"\b(?:huyện|quận|thị xã|thị trấn)\b", re.IGNORECASE)
OLD_UNIT_NOTE = ("Có tên đơn vị cấp huyện ({text}): từ 1/7/2025 chính quyền địa phương chỉ còn cấp tỉnh "
                 "và cấp xã, phường; kiểm tra lại danh xưng đơn vị hiện hành (kính gửi, nơi nhận, tên cơ quan).")
HEADER_BLANKS = (
    ("co_quan_ban_hanh", "tên cơ quan ban hành"),
    ("ky_hieu", "ký hiệu văn bản"),
    ("trich_yeu", "trích yếu"),
    ("dia_danh", "địa danh"),
)
SIGNATURE_BLANKS = (("nguoi_ky", "họ tên người ký"), ("chuc_vu", "chức vụ người ký"))
LOW_PROFILES = ("academic", "general")

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
FIX_PROFILE = (
    "Sửa trường profile: dùng profile administrative (hoặc bieu-mau-noi-bo, "
    "minutes-administrative nếu đúng loại văn bản); không đổi profile để qua bộ kiểm."
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
        for match in BLANK_RE.finditer(unicodedata.normalize("NFC", value)):
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


def _empty(value) -> bool:
    return str(value).strip() == ""


def field_blanks(spec: dict) -> list[tuple[str, str]]:
    """Trường trống mà bộ dựng vẫn in ra văn bản trông như đã xong: mỗi trường một ô.

    Thiếu tháng hoặc năm thì bộ dựng tự in tháng, năm hiện tại, nên cũng là ô trống.
    Người ký, chức vụ thiếu hẳn khoá thì bộ dựng tự chèn `[CẦN BỔ SUNG…]` (đếm từ file
    Word), nên ở đây chỉ bắt khi khoá có mà rỗng, hoặc không có khối ký.
    """
    header = spec["header"]
    found: list[tuple[str, str]] = []
    if _empty(header.get("thang", "")) or _empty(header.get("nam", "")):
        found.append(("phần đầu (ngày ban hành)",
                      "chưa có ngày ban hành (thiếu tháng hoặc năm; bộ dựng sẽ tự in tháng, "
                      "năm hiện tại)"))
    for key, name in HEADER_BLANKS:
        if _empty(header.get(key, "")):
            found.append((f"phần đầu ({key})", f"chưa có {name} (header.{key} trống)"))
    if header.get("is_cong_van") and _empty(spec.get("kinh_gui", "")):
        found.append(("dòng Kính gửi", "chưa có nơi kính gửi (kinh_gui trống)"))
    if not spec.get("body"):
        found.append(("nội dung", "chưa có nội dung (body trống)"))
    signature = spec.get("signature") or {}
    for key, name in SIGNATURE_BLANKS:
        if not signature or (key in signature and _empty(signature[key])):
            found.append(("phần ký", f"chưa có {name} (signature.{key} trống)"))
    return found


def profile_error(spec: dict) -> str | None:
    """Văn bản hành chính thật (công văn, có tên loại) không được hạ xuống bộ kiểm lỏng."""
    profile = spec.get("profile", "administrative")
    header = spec["header"]
    if profile in LOW_PROFILES and (header.get("is_cong_van")
                                    or not _empty(header.get("ten_loai_in_hoa", ""))):
        kind = document_kind(header)
        return (f"{SOURCE_NAME}: trường profile là {profile!r} nhưng văn bản là {kind}; "
                f"bộ kiểm {profile} bỏ qua gần hết thể thức Nghị định 30")
    return None


def collect_blanks(vd, path: Path, json_blanks: list[tuple[str, str]],
                   fields: list[tuple[str, str]]) -> tuple[list, list]:
    """Ô cần bổ sung và chỗ nghi là ô trống, đọc từ chính file Word vừa dựng.

    Bắt cả ô bộ dựng tự chèn (thiếu người ký) và ô chỉ bộ kiểm nhận ra (`<Tên đơn vị>`).
    Ô gộp của bảng lặp lại cùng một đoạn nên đếm theo đoạn, không theo ô. Chữ được
    chuẩn hoá NFC trước khi dò, để dạng tổ hợp dấu vẫn khớp.
    """
    pattern = re.compile(f"(?:{BLANK_RE.pattern})|(?:{vd.placeholder_re().pattern})",
                         re.IGNORECASE)
    unused = list(json_blanks)
    seen: dict = {}
    found: list[tuple[str, str]] = list(fields)
    suspects: list[str] = []
    old_units: list[str] = []
    doc = vd.Document(str(path))
    for _, paragraph in vd._iter_all_paragraphs(doc):
        element = paragraph._p
        if element in seen:
            continue
        seen[element] = True
        text_nfc = unicodedata.normalize("NFC", paragraph.text)
        for match in pattern.finditer(text_nfc):
            text = match.group(0)
            place = ""
            for index, (json_place, json_text) in enumerate(unused):
                if json_text.lower() == text.lower():
                    place = json_place
                    del unused[index]
                    break
            found.append((place, text))
        suspects.extend(match.group(0) for match in SUSPECT_RE.finditer(text_nfc))
        for match in OLD_UNIT_RE.finditer(text_nfc):
            if match.group(0).lower() not in (u.lower() for u in old_units):
                old_units.append(match.group(0))
    return found, suspects, old_units


def check_values(spec: dict) -> list[tuple[str, str]]:
    """Giá trị máy không kiểm được đúng sai, in nguyên văn để thầy cô đối chiếu."""
    header = spec["header"]
    signature = spec.get("signature") or {}

    def shown(value) -> str:
        return str(value).strip() or "(trống)"

    so = str(header.get("so_vb", "")).strip() or "(trống, văn thư điền)"
    ngay = " ".join(f"{word} {shown(header.get(key, ''))}"
                    for word, key in (("ngày", "ngay"), ("tháng", "thang"), ("năm", "nam")))
    signer = " / ".join(str(signature.get(key, "")).strip()
                        for key in ("quyen_han", "chuc_vu_thay", "chuc_vu", "nguoi_ky")
                        if str(signature.get(key, "")).strip()) or "(trống)"
    rows = [
        ("Số, ký hiệu", f"{so}/{shown(header.get('ky_hieu', ''))}"),
        ("Ngày ban hành", ngay),
        ("Người ký, chức vụ", signer),
        ("Cơ quan chủ quản", shown(header.get("co_quan_chu_quan", ""))),
        ("Cơ quan ban hành", shown(header.get("co_quan_ban_hanh", ""))),
        ("Địa danh", shown(header.get("dia_danh", ""))),
        ("Kính gửi", shown(spec.get("kinh_gui", ""))),
    ]
    for block in spec.get("body", []):
        if block.get("type") == "can_cu":
            rows.extend(("Căn cứ", shown(item)) for item in block.get("items", []))
    return rows


def run_validator(vd, path: Path, profile: str, allow_placeholder: bool) -> list:
    with contextlib.redirect_stdout(io.StringIO()):
        return list(vd.run_checks(path, profile, allow_placeholder))


def confirm_signer_title(vd, rows: list, path: Path, signature: dict) -> list:
    """Bỏ cảnh báo B6 khi chức vụ in hoa có thật trong văn bản.

    Mẫu B6 của ND30 chỉ biết chức vụ khối cơ quan (GIÁM ĐỐC, CHỦ TỊCH…), nên
    HIỆU TRƯỞNG, TỔ TRƯỞNG luôn bị cảnh báo giả. Chức vụ trống hoặc chưa in hoa
    thì giữ nguyên cảnh báo.
    """
    titles = [str(signature.get(key, "")).strip() for key in ("chuc_vu", "chuc_vu_thay")]
    titles = [t for t in titles if t and t == t.upper() and t != t.lower()]
    if not titles or not any(st == vd.WARN and label.startswith("B6.") for st, label, _ in rows):
        return rows
    doc = vd.Document(str(path))
    text = "\n".join(p.text for _, p in vd._iter_all_paragraphs(doc))
    found = next((t for t in titles if t in text), None)
    if found is None:
        return rows
    return [(vd.OK, label, f"Chức vụ người ký: {found}")
            if st == vd.WARN and label.startswith("B6.") else (st, label, detail)
            for st, label, detail in rows]


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
                 vd, values, suspects, old_units=()) -> str:
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
            lines.append(f"{number}. {place}: `{text}`" if place else f"{number}. `{text}`")
    else:
        lines.append("Không còn ô nào.")
    if suspects:
        lines += ["", "## Nghi còn chỗ trống", "",
                  "Không tính là ô cần bổ sung; còn thiếu thì ghi `[CẦN BỔ SUNG: …]` rồi chạy lại.",
                  ""]
        lines += [f"- `{text}`" for text in suspects]
    if old_units:
        lines += ["", "## Đơn vị hành chính", "", OLD_UNIT_NOTE.format(text=", ".join(old_units))]
    lines += ["", "## Thầy cô đối chiếu", "",
              "Máy không kiểm được các giá trị dưới đây đúng hay sai; thầy cô đối chiếu với "
              "thực tế trước khi trình ký.", ""]
    lines += [f"- {name}: {value}" for name, value in values]
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
    message = profile_error(spec)
    if message:
        emit(failure("json", message, FIX_PROFILE, loai=kind, profile=profile))
        return 1
    json_blanks = find_blanks(spec)
    fields = field_blanks(spec)
    info = {"loai": kind, "profile": profile, "blanks": len(json_blanks) + len(fields)}

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
    tmp: Path | None = None
    try:
        try:
            fd, tmp_name = tempfile.mkstemp(prefix=".tmp-", suffix=".docx", dir=folder)
            os.close(fd)
            tmp = Path(tmp_name)
        except OSError as exc:
            emit(failure("write", f"Không ghi được vào thư mục {folder}: {exc}",
                         FIX_WRITE + " Kiểm tra thư mục không chỉ đọc và ổ đĩa còn trống.",
                         **info))
            return 1
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                gd.generate(spec).save(str(tmp))
        except OSError as exc:
            emit(failure("write", f"Không ghi được file Word: {exc}", FIX_WRITE, **info))
            return 1
        except Exception as exc:  # noqa: BLE001
            emit(failure("internal", f"Lỗi khi dựng file Word: {exc}", FIX_INTERNAL, **info))
            return 1

        signature = spec.get("signature") or {}
        strict = confirm_signer_title(vd, run_validator(vd, tmp, profile, False), tmp, signature)
        lenient = confirm_signer_title(vd, run_validator(vd, tmp, profile, True), tmp, signature)
        rows = classify(vd, strict, lenient)
        real = [(label, detail) for st, label, detail, blank in rows if st == vd.FAIL and not blank]
        blank_fail = [(label, detail) for st, label, detail, blank in rows if blank]
        blanks, suspects, old_units = collect_blanks(vd, tmp, json_blanks, fields)
        values = check_values(spec)
        info["blanks"] = len(blanks)
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
                warnings.append(f"Ô cần bổ sung ở {place}: {value}" if place
                                else f"Ô cần bổ sung: {value}")
            if not blanks:
                for label, detail in blank_fail:
                    warnings.append(f"{label}: {detail}")
        for text in suspects:
            warnings.append(f"Nghi còn chỗ trống chưa đánh dấu: {text} — còn thiếu thì ghi "
                            "[CẦN BỔ SUNG: …] rồi chạy lại.")
        if old_units:
            warnings.append(OLD_UNIT_NOTE.format(text=", ".join(old_units)))
        for status, label, detail, _ in rows:
            if status == vd.WARN:
                warnings.append(f"{label}: {detail}")
        warnings.append(f"{CHECK_VALUES_PREFIX} (máy không kiểm được): "
                        + "; ".join(f"{name}: {value}" for name, value in values))

        if real:
            verdict = "Có lỗi thể thức nặng — chưa xuất văn bản."
        elif draft:
            verdict = "Bản nháp — còn ô cần bổ sung."
        else:
            verdict = "Đạt các mục bộ kiểm tra được."
        report = build_report(kind=kind, trich_yeu=str(header.get("trich_yeu", "")),
                              profile=profile, rows=rows, blanks=blanks, verdict=verdict, vd=vd,
                              values=values, suspects=suspects, old_units=old_units)

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
            if tmp is not None and tmp.exists():
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

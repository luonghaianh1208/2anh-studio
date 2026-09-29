#!/usr/bin/env python3
"""generate_docx — sinh file .docx đúng thể thức NĐ30 từ 1 file JSON/YAML mô tả nội dung.

nha-van:exempt — đây là mã nguồn, không phải văn bản gửi ra ngoài.

Vì sao script này tồn tại: AI agent (đặc biệt Gemini Spark chạy trong sandbox không có
filesystem của mình) dễ SINH RA cấu trúc JSON đúng, nhưng dễ SAI khi tự viết code
python-docx ad-hoc gọi trực tiếp build_docx.py (phải đọc + transcribe ~1200 dòng code
qua giao diện web rất chậm và dễ lỗi). Đường đi đúng: agent chỉ cần sinh 1 file JSON nhỏ,
rồi gọi:

    python3 scripts/generate_docx.py input.json

3 cách truyền input, chọn 1 (không cần tạo file tạm nếu sandbox không tiện):
    python3 scripts/generate_docx.py input.json                       # từ file, -o suy ra: input.docx
    python3 scripts/generate_docx.py input.json output.docx           # -o dạng vị trí, gõ ngắn hơn
    echo '{"header": {...}, ...}' | python3 scripts/generate_docx.py - -o output.docx   # stdin, -o bắt buộc
    python3 scripts/generate_docx.py --json-string '{"header": {...}}' -o output.docx   # chuỗi, -o bắt buộc

Output LUÔN là .docx: `-o` bỏ trống thì tự đặt tên theo input (`input.json` → `input.docx`);
truyền `-o` với đuôi khác `.docx` (vd `.doc`, `.pdf`, `.txt`) → script BÁO LỖI và dừng, không
bao giờ âm thầm xuất định dạng khác. Đây là chủ đích: nd30 chỉ có 1 định dạng bàn giao.

Script tự import build_docx.py (cùng thư mục) và dựng file — KHÔNG cần agent đọc/hiểu
nội dung bên trong build_docx.py.

Schema JSON (mọi field đều optional trừ ghi chú *bắt buộc*):
{
  "profile": "administrative",
  "header": {
    "co_quan_chu_quan": "UBND HUYỆN ...",      // *bắt buộc*
    "co_quan_ban_hanh": "UBND XÃ ...",          // *bắt buộc*
    "so_vb": "",                                 // để trống nếu chưa có số
    "ky_hieu": "TTr-UBND",                       // *bắt buộc*
    "trich_yeu": "Về việc ...",                  // *bắt buộc*
    "dia_danh": "...",                           // *bắt buộc*
    "ngay": "", "thang": "", "nam": "",
    "is_cong_van": false,
    "ten_loai_in_hoa": "TỜ TRÌNH"                 // bỏ trống nếu is_cong_van=true
  },
  "kinh_gui": "UBND huyện ...",
  "body": [
    {"type": "heading", "text": "1. Sự cần thiết"},
    {"type": "paragraph", "text": "..."},
    {"type": "bullet", "text": "...", "level": 1},
    {"type": "table", "headers": ["A","B"], "rows": [["1","2"]]},
    {"type": "can_cu", "items": ["Căn cứ Luật ...", "Căn cứ Nghị định ..."]}
  ],
  "ket_thuc": "./.",
  "signature": {
    "noi_nhan_items": ["Như trên"],
    "phong_viet_tat": "VT",
    "chuc_vu": "CHỦ TỊCH",
    "nguoi_ky": "[CẦN BỔ SUNG: họ tên]",
    "quyen_han": "", "chuc_vu_thay": ""
  }
}

Dùng `placeholder("mô tả")` bằng cách gõ thẳng chuỗi "[CẦN BỔ SUNG: mô tả]" trong JSON —
validate_docx.py sẽ tự bắt được các placeholder này.

Ví dụ JSON đầy đủ có sẵn ở `examples/input-sample.json`.

Zero third-party dependency cho input .json: parser dùng module `json` chuẩn của Python, KHÔNG
cần cài `pyyaml`. `pyyaml` chỉ cần khi input là `.yaml`/`.yml` — sandbox không cài được pyyaml
vẫn dùng được script này miễn truyền input dạng `.json`.

Xuất file + validate luôn trong 1 lệnh (khỏi gọi validate_docx.py riêng):

    python3 scripts/generate_docx.py input.json -o output.docx --validate --profile administrative
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_docx as bd  # noqa: E402

try:
    import yaml  # optional; chỉ cần nếu input là .yaml/.yml
except ImportError:
    yaml = None


def load_spec(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in (".yaml", ".yml"):
        if yaml is None:
            raise SystemExit("Cần cài pyyaml để đọc file .yaml (pip install pyyaml), "
                              "hoặc chuyển input sang .json.")
        return yaml.safe_load(text)
    return json.loads(text)


def build_body_item(doc, item: dict, profile: str) -> None:
    kind = item.get("type", "paragraph")
    if kind == "heading":
        bd.add_section_heading(doc, item["text"], level=item.get("level", 1))
    elif kind == "paragraph":
        bd.add_body_paragraph(doc, item["text"])
    elif kind == "bullet":
        bd.add_bullet(doc, item["text"], level=item.get("level", 1), profile=profile)
    elif kind == "table":
        bd.add_table(doc, item["headers"], item["rows"])
    elif kind == "can_cu":
        bd.add_can_cu(doc, item["items"])
    elif kind == "centered":
        bd.add_centered(doc, item["text"], bold=item.get("bold", False))
    elif kind == "italic_paragraph":
        # dùng cho dòng "Nghị quyết này đã được HĐND ... thông qua ngày..." của VBQPPL
        # (Phụ lục I NĐ 78/2025, Mục III.2.c) — chữ nghiêng, không thụt đầu dòng, không justify.
        bd.add_body_paragraph(doc, item["text"], italic=True,
                               indent_first_cm=0, align=bd.WD_ALIGN_PARAGRAPH.LEFT)
    else:
        raise ValueError(f"body item không hỗ trợ type={kind!r}: {item}")


def generate(spec: dict) -> "bd.Document":
    profile = spec.get("profile", "administrative")
    header = spec["header"]

    doc = bd.Document()
    bd.setup_page(doc)
    bd.add_header_section(
        doc,
        co_quan_chu_quan=header["co_quan_chu_quan"],
        co_quan_ban_hanh=header["co_quan_ban_hanh"],
    )
    bd.add_so_vb_and_date_section(
        doc,
        so_vb=header.get("so_vb", ""),
        ky_hieu=header.get("ky_hieu", ""),
        trich_yeu=header.get("trich_yeu", ""),
        dia_danh=header.get("dia_danh", ""),
        ngay=header.get("ngay", ""),
        thang=header.get("thang", ""),
        nam=header.get("nam", ""),
        is_cong_van=header.get("is_cong_van", False),
    )
    if not header.get("is_cong_van") and header.get("ten_loai_in_hoa"):
        bd.add_title_block(doc, ten_loai=header["ten_loai_in_hoa"],
                            trich_yeu=header.get("trich_yeu", ""))

    if spec.get("kinh_gui"):
        bd.add_kinh_gui(doc, spec["kinh_gui"])

    for item in spec.get("body", []):
        build_body_item(doc, item, profile)

    if spec.get("ket_thuc"):
        bd.add_ket_thuc(doc, spec["ket_thuc"])

    sig = spec.get("signature")
    if sig:
        bd.add_signature_noi_nhan(
            doc,
            noi_nhan_items=sig.get("noi_nhan_items", ["Như trên"]),
            chuc_vu=sig.get("chuc_vu", bd.placeholder("chức vụ người ký")),
            nguoi_ky=sig.get("nguoi_ky", bd.placeholder("họ tên người ký")),
            quyen_han=sig.get("quyen_han", ""),
            chuc_vu_thay=sig.get("chuc_vu_thay", ""),
            phong_viet_tat=sig.get("phong_viet_tat", ""),
        )

    return doc


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", type=str, nargs="?", default=None,
                    help="File .json/.yaml mô tả nội dung, hoặc '-' để đọc JSON từ stdin. "
                         "Bỏ qua nếu dùng --json-string.")
    ap.add_argument("output_pos", type=str, nargs="?", default=None,
                    help="Đường dẫn output truyền dạng vị trí (vd `generate_docx.py input.json output.docx`) — "
                         "tương đương -o/--output, chỉ để gõ ngắn hơn. -o vẫn được ưu tiên nếu cả 2 có mặt.")
    ap.add_argument("--json-string", type=str, default=None,
                    help="Truyền JSON trực tiếp dạng chuỗi, khỏi cần tạo file tạm "
                         "(vd: --json-string '{\"header\": {...}, ...}'). Ưu tiên hơn `input` nếu cả 2 có mặt.")
    ap.add_argument("-o", "--output", type=Path, default=None,
                    help="Đường dẫn file xuất ra — LUÔN LÀ .docx (tự thêm đuôi nếu thiếu, báo lỗi "
                         "nếu đuôi khác .docx). Bỏ trống → tự đặt tên theo input (vd input.json → input.docx; "
                         "bắt buộc truyền khi dùng stdin/--json-string vì không có tên input để suy ra).")
    ap.add_argument("--validate", action="store_true",
                    help="(GIỮ TƯƠNG THÍCH — validate giờ là MẶC ĐỊNH, cờ này thừa nhưng vẫn nhận.) "
                         "Chạy validate_docx.py trên file vừa tạo, in kết quả tóm tắt.")
    ap.add_argument("--no-validate", action="store_true",
                    help="TẮT validate mặc định (Pha 4). Chỉ dùng khi thật sự cần file thô chưa kiểm "
                         "— file bàn giao thì KHÔNG được tắt.")
    ap.add_argument("--validate-json", action="store_true",
                    help="Như --validate nhưng in JSON (machine-readable) thay vì báo cáo chữ — "
                         "cho agent tự đọc và tự quyết định sửa lỗi mà không cần parse text.")
    ap.add_argument("--profile", default="administrative",
                    help="Profile truyền cho validate_docx.py khi dùng --validate "
                         "(administrative | bieu-mau-noi-bo | minutes-administrative | academic | general)")
    ap.add_argument("--allow-placeholder", action="store_true",
                    help="Khi dùng --validate: coi placeholder [CẦN BỔ SUNG] là cảnh báo, không phải lỗi nặng "
                         "(dùng khi cố ý xuất bản nháp còn thiếu dữ liệu).")
    args = ap.parse_args()
    if args.output is None and args.output_pos is not None:
        args.output = Path(args.output_pos)

    if args.json_string is not None:
        spec = json.loads(args.json_string)
    elif args.input == "-":
        spec = json.loads(sys.stdin.read())
    elif args.input is not None:
        spec = load_spec(Path(args.input))
    else:
        ap.error("cần 1 trong 3: <input.json>, '-' (stdin), hoặc --json-string")

    output = args.output
    if output is None:
        if args.input in (None, "-"):
            ap.error("--output bắt buộc khi dùng stdin/--json-string (không có tên input để tự đặt tên .docx)")
        output = Path(args.input).with_suffix(".docx")
    elif output.suffix.lower() != ".docx":
        if output.suffix == "":
            output = output.with_suffix(".docx")  # thiếu đuôi -> tự thêm
        else:
            raise SystemExit(f"--output phải là file .docx, nhận '{output.suffix}'. "
                              f"Output của skill nd30 LUÔN là .docx (đúng thể thức, mở Word sửa được), "
                              f"không xuất định dạng khác.")
    args.output = output

    doc = generate(spec)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(args.output))
    print(f"✓ Đã xuất {args.output}")

    # Pha 4 (validate) MẶC ĐỊNH BẬT từ 2026-08-27 — trước đây là cờ opt-in nên luật "BẮT BUỘC,
    # đừng bỏ" trong SKILL.md chỉ là chữ (agent quên cờ = file không kiểm vẫn được giao).
    # Tắt phải CHỦ ĐỘNG --no-validate và chịu cảnh báo — không có đường quên-im-lặng.
    if args.no_validate and not args.validate_json:
        print("⚠️  BỎ QUA validate (--no-validate) — file CHƯA qua kiểm thể thức, KHÔNG bàn giao bản này.")
        return

    import validate_docx as vd  # cùng thư mục, import trực tiếp — không cần subprocess
    results = vd.run_checks(args.output, args.profile, args.allow_placeholder)
    if args.validate_json:
        payload = vd.results_to_json(args.output, args.profile, results)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        if payload["overall_status"] == "FAILED":
            raise SystemExit(2)
        if payload["counts"]["warn"]:
            raise SystemExit(1)
        return
    _, warn, fail = vd.report(args.output, args.profile, results)
    if fail:
        print("  ℹ️  Nếu lỗi nặng CHỈ là placeholder [CẦN BỔ SUNG] (đúng Luật #1 không-bịa) và bạn"
              " cần BẢN NHÁP cho người điền tiếp: chạy lại thêm --allow-placeholder"
              " (file vẫn chưa được bàn giao thành phẩm).")
        raise SystemExit(2)
    if warn:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

"""Sinh MẪU .docx rỗng (đúng thể thức NĐ30, nội dung để placeholder) cho các loại VB hay dùng.

nha-van:exempt — đây là mã nguồn, không phải văn bản gửi ra ngoài.

Chạy:
    python3 templates/_build_templates.py            # sinh đủ 5 mẫu vào templates/
    python3 templates/_build_templates.py --check    # sinh xong tự validate luôn

Mẫu CỐ Ý còn `[CẦN BỔ SUNG: ...]` — đó là chỗ phải phỏng vấn user mới điền được (Luật cứng #1).
Vì vậy validate mẫu phải dùng cờ `--allow-placeholder`.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

from build_docx import (  # noqa: E402
    add_body_paragraph, add_bullet, add_can_cu, add_centered, add_header_section,
    add_kinh_gui, add_ket_thuc, add_section_heading, add_signature_noi_nhan,
    add_so_vb_and_date_section, add_title_block, placeholder, setup_document,
)
from validate_docx import validate_doc  # noqa: E402

P = placeholder
CQ_CHU_QUAN = P("tên cơ quan chủ quản")
CQ_BAN_HANH = P("TÊN CƠ QUAN BAN HÀNH")
DIA_DANH = P("địa danh")
NGUOI_KY = P("họ tên người ký")
CHUC_VU = P("CHỨC VỤ NGƯỜI KÝ")
NOI_NHAN = ["- " + P("nơi nhận 1"), "- Lưu: VT, " + P("đơn vị soạn thảo") + "."]


def _skeleton(ky_hieu: str, ten_loai: str | None, *, is_cong_van: bool = False,
              trich_yeu: str = ""):
    """Khối đầu văn bản dùng chung: header 2 cột + Số/ngày + (tên loại + trích yếu)."""
    doc = setup_document(profile="administrative")
    add_header_section(doc, co_quan_chu_quan=CQ_CHU_QUAN, co_quan_ban_hanh=CQ_BAN_HANH)
    add_so_vb_and_date_section(
        doc, so_vb="", ky_hieu=ky_hieu, trich_yeu=trich_yeu, dia_danh=DIA_DANH,
        ngay="", thang="", nam="", is_cong_van=is_cong_van,
    )
    if ten_loai:
        add_title_block(doc, ten_loai=ten_loai, trich_yeu=trich_yeu)
    return doc


def _close(doc, *, quyen_han: str = ""):
    add_signature_noi_nhan(doc, noi_nhan_items=NOI_NHAN, chuc_vu=CHUC_VU,
                           nguoi_ky=NGUOI_KY, quyen_han=quyen_han)
    return doc


# ============================================================
# Từng loại văn bản
# ============================================================

def build_to_trinh(out: Path):
    doc = _skeleton("TTr-" + P("VIẾT TẮT CƠ QUAN"), "TỜ TRÌNH",
                    trich_yeu="Về việc " + P("nội dung trình"))
    add_kinh_gui(doc, P("cơ quan nhận tờ trình"))
    add_body_paragraph(doc, "Thực hiện " + P("văn bản chỉ đạo: số, ngày, cơ quan ban hành")
                       + ", " + P("cơ quan ban hành") + " báo cáo và kính trình như sau:")
    add_section_heading(doc, "1. Căn cứ và sự cần thiết")
    add_body_paragraph(doc, P("nêu căn cứ pháp lý và lý do phải trình"))
    add_section_heading(doc, "2. Nội dung trình")
    add_bullet(doc, P("nội dung đề nghị phê duyệt"))
    add_bullet(doc, "Kinh phí thực hiện: " + P("số tiền + nguồn kinh phí"))
    add_bullet(doc, "Thời gian thực hiện: " + P("mốc thời gian"))
    add_section_heading(doc, "3. Đề nghị")
    add_body_paragraph(doc, "Kính đề nghị " + P("cơ quan nhận tờ trình")
                       + " xem xét, phê duyệt " + P("nội dung đề nghị phê duyệt") + ".")
    add_ket_thuc(doc)
    _close(doc)
    doc.save(str(out))


def build_cong_van(out: Path):
    doc = _skeleton(P("VIẾT TẮT CƠ QUAN"), None, is_cong_van=True,
                    trich_yeu=P("trích yếu ngắn — nội dung công văn"))
    add_kinh_gui(doc, P("cơ quan nhận công văn"))
    add_body_paragraph(doc, P("nêu lý do / căn cứ gửi công văn: số, ngày, cơ quan ban hành"))
    add_body_paragraph(doc, P("nội dung đề nghị / trao đổi"))
    add_body_paragraph(doc, "Đề nghị " + P("cơ quan nhận công văn")
                       + " quan tâm, phối hợp thực hiện.")
    add_ket_thuc(doc)
    _close(doc)
    doc.save(str(out))


def build_quyet_dinh(out: Path):
    doc = _skeleton("QĐ-" + P("VIẾT TẮT CƠ QUAN"), "QUYẾT ĐỊNH",
                    trich_yeu="Về việc " + P("nội dung quyết định"))
    add_centered(doc, CHUC_VU, size_pt=13, bold=True)
    add_can_cu(doc, [
        "Căn cứ " + P("văn bản quy định thẩm quyền: tên, số, ngày"),
        "Căn cứ " + P("văn bản pháp lý liên quan: tên, số, ngày"),
        "Theo đề nghị của " + P("đơn vị đề nghị"),
    ])
    add_centered(doc, "QUYẾT ĐỊNH:", size_pt=13, bold=True)
    add_body_paragraph(doc, "Điều 1. " + P("nội dung quyết định chính"))
    add_body_paragraph(doc, "Điều 2. " + P("phân công tổ chức thực hiện"))
    add_body_paragraph(doc, "Điều 3. Quyết định này có hiệu lực kể từ ngày "
                       + P("ngày có hiệu lực") + ". "
                       + P("các tổ chức, cá nhân chịu trách nhiệm thi hành") + ".")
    add_ket_thuc(doc)
    _close(doc)
    doc.save(str(out))


def build_ke_hoach(out: Path):
    doc = _skeleton("KH-" + P("VIẾT TẮT CƠ QUAN"), "KẾ HOẠCH",
                    trich_yeu=P("tên kế hoạch") + " năm " + P("năm"))
    add_body_paragraph(doc, "Thực hiện " + P("văn bản chỉ đạo: số, ngày, cơ quan ban hành")
                       + ", " + P("cơ quan ban hành") + " xây dựng kế hoạch như sau:")
    add_section_heading(doc, "I. MỤC ĐÍCH, YÊU CẦU")
    add_bullet(doc, "Mục đích: " + P("mục đích"))
    add_bullet(doc, "Yêu cầu: " + P("yêu cầu"))
    add_section_heading(doc, "II. NỘI DUNG THỰC HIỆN")
    add_bullet(doc, P("nội dung công việc 1") + " — hoàn thành trước " + P("mốc thời gian"))
    add_bullet(doc, P("nội dung công việc 2") + " — hoàn thành trước " + P("mốc thời gian"))
    add_section_heading(doc, "III. KINH PHÍ")
    add_body_paragraph(doc, "Tổng kinh phí: " + P("số tiền") + ", nguồn " + P("nguồn kinh phí") + ".")
    add_section_heading(doc, "IV. TỔ CHỨC THỰC HIỆN")
    add_bullet(doc, P("đơn vị chủ trì") + ": " + P("nhiệm vụ"))
    add_bullet(doc, P("đơn vị phối hợp") + ": " + P("nhiệm vụ"))
    add_ket_thuc(doc)
    _close(doc)
    doc.save(str(out))


def build_bao_cao(out: Path):
    doc = _skeleton("BC-" + P("VIẾT TẮT CƠ QUAN"), "BÁO CÁO",
                    trich_yeu=P("nội dung báo cáo") + " " + P("kỳ báo cáo"))
    add_kinh_gui(doc, P("cơ quan nhận báo cáo"))
    add_body_paragraph(doc, "Thực hiện " + P("văn bản yêu cầu báo cáo: số, ngày, cơ quan ban hành")
                       + ", " + P("cơ quan ban hành") + " báo cáo như sau:")
    add_section_heading(doc, "I. KẾT QUẢ THỰC HIỆN")
    add_bullet(doc, P("kết quả 1 — kèm số liệu"))
    add_bullet(doc, P("kết quả 2 — kèm số liệu"))
    add_section_heading(doc, "II. TỒN TẠI, HẠN CHẾ VÀ NGUYÊN NHÂN")
    add_bullet(doc, P("tồn tại, hạn chế"))
    add_section_heading(doc, "III. NHIỆM VỤ THỜI GIAN TỚI")
    add_bullet(doc, P("nhiệm vụ tiếp theo"))
    add_section_heading(doc, "IV. ĐỀ XUẤT, KIẾN NGHỊ")
    add_body_paragraph(doc, P("đề xuất, kiến nghị"))
    add_ket_thuc(doc)
    _close(doc)
    doc.save(str(out))


BUILDERS = {
    "to-trinh.docx": build_to_trinh,
    "cong-van.docx": build_cong_van,
    "quyet-dinh.docx": build_quyet_dinh,
    "ke-hoach.docx": build_ke_hoach,
    "bao-cao.docx": build_bao_cao,
}


def build_all(outdir: Path) -> list[Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    made = []
    for name, fn in BUILDERS.items():
        path = outdir / name
        fn(path)
        made.append(path)
        print(f"đã sinh: {path}")
    return made


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default=str(Path(__file__).resolve().parent))
    ap.add_argument("--check", action="store_true", help="validate từng mẫu sau khi sinh")
    args = ap.parse_args()

    made = build_all(Path(args.outdir))
    if not args.check:
        return 0
    bad = []
    for path in made:
        print(f"\n----- validate {path.name} -----")
        if not validate_doc(path, profile="administrative", allow_placeholder=True):
            bad.append(path.name)
    if bad:
        print(f"\n✗ Mẫu chưa đạt: {bad}")
        return 2
    print("\n✓ Tất cả mẫu tự pass validate (mức allow-placeholder).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

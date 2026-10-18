# tools/vi/video_ma_parts/ngan.py
"""Video ngắn "nhịp hình" (`phong-cach: ngan`, thiết kế docs/vi/phat-trien/2026-10-19-video-ngan-nhip-hinh-thiet-ke.md).

Dùng ngữ pháp nhịp của Vox (`nhip: <cụm từ> | <vật>: <nội dung> | <ô> | <tuỳ chọn>`) với bố cục khổ dọc cố định,
hai giao diện (`phang-sang`, `toi-du-lieu`) và các vật riêng: người minh hoạ phẳng ghép từ bộ phận (`nguoi`, `nhom`),
biểu tượng lớn, lưới chấm, trước → sau, tin nhắn, thông báo, trích dẫn. Trang vẽ ở runtime/ngan.js."""

from __future__ import annotations

import re

GIAO_DIEN = ("phang-sang", "toi-du-lieu")
TIEU_DE_DAI = 40
CHUONG_DAI = 20
NHIP_TOI_DA = 8
O = ("giua", "tren", "duoi", "trai", "phai")
TU_THE = ("dung", "chao", "chi-tay", "giai-thich", "suy-nghi", "ngac-nhien", "vo-dau", "dung-lai", "an-mung", "buon")

# Vật của video ngắn: vật Vox dùng lại + vật mới (giới hạn ký tự ở _kiem).
VAT_VOX = ("chu", "so", "the", "nhan", "dau", "cot", "chu-trinh", "moc", "thap")
VAT_MOI = ("nguoi", "nhom", "bieu-tuong", "luoi-cham", "truoc-sau", "tin-nhan", "thong-bao", "trich-dan")
VAT = VAT_VOX + VAT_MOI
TUY_CHON = ("dien-thoai",)

# ---- Nhân vật ghép từ bộ phận (runtime/nhan-vat-phang.js vẽ đúng các tên này) ----
TOC = ("ngan", "re-ngoi", "dai", "duoi-ngua", "bui", "troc")
DA = ("sang", "vua", "ngam")
AO = ("so-mi", "so-mi-dai", "ao-thun", "hoodie", "blouse", "ao-dai", "ao-ba-ba", "vest", "tap-de", "dong-phuc", "the-thao")
DUOI = ("quan", "quan-short", "vay")
MU = ("mu-bao-ho", "ke-pi", "non-la", "mu-dau-bep", "luoi-trai", "bao-hiem")
PHU = ("kinh", "ca-vat", "khan-do", "ong-nghe", "phu-hieu", "cap-sach")
MAU = {"do": "#D64545", "cam": "#F28C28", "vang": "#F2C14E", "xanh-la": "#3FAE7A", "xanh-reu": "#3D5A2A",
       "xanh-duong": "#3F7FD9", "xanh-nhat": "#9CC9EE", "xanh-than": "#24345C", "tim": "#8E5BD0", "hong": "#F4A7B9",
       "nau": "#7A5236", "be": "#D8C3A0", "xam": "#8A8F98", "den": "#2A2A2A", "trang": "#FFFFFF"}
MAU_TOC = {"den": "#1E1A17", "nau": "#4A2E1F", "bac": "#D9D9D9", "vang": "#C9A04E"}
_HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")
_TEN_VAI = re.compile(r"^[a-z0-9][a-z0-9-]{0,19}$")


def _nv(gioi, toc, mau_toc, da, ao, mau_ao, duoi, mau_duoi, mu=None, phu=()):
    return {"gioi": gioi, "toc": toc, "mauToc": MAU_TOC.get(mau_toc, mau_toc), "da": da,
            "ao": {"kieu": ao, "mau": MAU.get(mau_ao, mau_ao)}, "duoi": {"kieu": duoi, "mau": MAU.get(mau_duoi, mau_duoi)},
            "mu": mu, "phu": list(phu)}


# 13 vai làm sẵn (đã duyệt 2026-10-19). AI gọi thẳng tên này, hoặc ghép vai mới ở khoá đầu `vai`.
VAI_SAN = {
    "hoc-sinh-nam": _nv("nam", "ngan", "den", "vua", "so-mi", "trang", "quan", "xanh-than", phu=("khan-do",)),
    "hoc-sinh-nu": _nv("nu", "duoi-ngua", "den", "sang", "so-mi", "trang", "vay", "xanh-than", phu=("khan-do",)),
    "thay-giao": _nv("nam", "re-ngoi", "den", "vua", "so-mi-dai", "#DCE8F7", "quan", "#3A3F47", phu=("ca-vat", "kinh")),
    "co-giao": _nv("nu", "dai", "den", "sang", "ao-dai", "#2F7FB8", "quan", "trang"),
    "bac-si": _nv("nam", "re-ngoi", "den", "vua", "blouse", "trang", "quan", "#5B7FA3", phu=("ong-nghe",)),
    "nha-khoa-hoc": _nv("nu", "bui", "nau", "sang", "blouse", "trang", "quan", "xanh-than", phu=("kinh",)),
    "ky-su": _nv("nam", "ngan", "den", "ngam", "ao-thun", "cam", "quan", "xanh-than", mu="mu-bao-ho"),
    "van-phong-nu": _nv("nu", "dai", "nau", "sang", "so-mi-dai", "hong", "vay", "den"),
    "ban-tre": _nv("nam", "re-ngoi", "den", "vua", "hoodie", "xanh-la", "quan", "#4D6FA8"),
    "ban-tre-nu": _nv("nu", "dai", "den", "vua", "hoodie", "vang", "quan", "#4D6FA8"),
    "phu-huynh-nu": _nv("nu", "bui", "den", "vua", "ao-thun", "#E07A9B", "quan", "#3A3F47"),
    "ong": _nv("nam", "ngan", "bac", "vua", "so-mi-dai", "#B9A27A", "quan", "#4A4A4A", phu=("kinh",)),
    "ba": _nv("nu", "bui", "bac", "vua", "ao-ba-ba", "tim", "quan", "den"),
}


class VaiError(ValueError):
    pass


def _mau(chu: str, bang: dict) -> str:
    if chu in bang:
        return bang[chu]
    if _HEX.match(chu):
        return chu.upper()
    raise VaiError(f"màu `{chu}` không có; dùng mã `#RRGGBB` hoặc một trong: {', '.join(bang)}")


def doc_mot_vai(mo_ta: str) -> dict:
    """`<vai làm sẵn>` hoặc danh sách bộ phận cách nhau bằng dấu phẩy (có thể mở đầu bằng vai làm sẵn rồi đổi vài
    bộ phận): `nam|nu`, `toc <kiểu> [màu]`, `da <sang|vua|ngam>`, `ao <kiểu> [màu]`, `duoi <kiểu> [màu]`,
    `mu <kiểu>`, `phu <phụ kiện> …`."""
    phan = [p.strip() for p in mo_ta.split(",") if p.strip()]
    if not phan:
        raise VaiError("vai chưa có mô tả")
    if phan[0] in VAI_SAN:
        v = {**VAI_SAN[phan[0]], "ao": dict(VAI_SAN[phan[0]]["ao"]), "duoi": dict(VAI_SAN[phan[0]]["duoi"]),
             "phu": list(VAI_SAN[phan[0]]["phu"])}
        phan = phan[1:]
    else:
        v = _nv("nam", "ngan", "den", "vua", "ao-thun", "xanh-duong", "quan", "xanh-than")
        v["toc"] = None
    for p in phan:
        tu = p.split()
        loai, du = tu[0], tu[1:]
        if loai in ("nam", "nu") and not du:
            v["gioi"] = loai
        elif loai == "toc" and 1 <= len(du) <= 2 and du[0] in TOC:
            v["toc"] = du[0]
            if len(du) == 2:
                v["mauToc"] = _mau(du[1], MAU_TOC)
        elif loai == "da" and len(du) == 1 and du[0] in DA:
            v["da"] = du[0]
        elif loai == "ao" and 1 <= len(du) <= 2 and du[0] in AO:
            v["ao"] = {"kieu": du[0], "mau": _mau(du[1], MAU) if len(du) == 2 else v["ao"]["mau"]}
        elif loai == "duoi" and 1 <= len(du) <= 2 and du[0] in DUOI:
            v["duoi"] = {"kieu": du[0], "mau": _mau(du[1], MAU) if len(du) == 2 else v["duoi"]["mau"]}
        elif loai == "mu" and len(du) == 1 and (du[0] in MU or du[0] == "khong"):
            v["mu"] = None if du[0] == "khong" else du[0]
        elif loai == "phu" and du and all(x in PHU for x in du):
            v["phu"] = list(dict.fromkeys(v["phu"] + du))
        else:
            raise VaiError(f"bộ phận `{p}` không hiểu. Dùng: nam|nu; toc <{'|'.join(TOC)}> [màu]; da <{'|'.join(DA)}>; "
                           f"ao <{'|'.join(AO)}> [màu]; duoi <{'|'.join(DUOI)}> [màu]; mu <{'|'.join(MU)}>; "
                           f"phu <{'|'.join(PHU)}>")
    if v["toc"] is None:
        v["toc"] = "dai" if v["gioi"] == "nu" else "ngan"
    return v


def doc_dan_vai(gia_tri: str) -> dict:
    """Khoá đầu `vai: <tên> = <mô tả>; <tên> = <mô tả>` → {tên: nhân vật}."""
    ra = {}
    for muc in (m.strip() for m in gia_tri.split(";")):
        if not muc:
            continue
        ten, dau, mo_ta = muc.partition("=")
        ten = ten.strip()
        if not dau or not _TEN_VAI.match(ten):
            raise VaiError(f"`{muc}` phải có dạng `<tên-vai> = <mô tả>`, tên viết thường không dấu, nối bằng `-`")
        if ten in ra:
            raise VaiError(f"vai `{ten}` khai báo hai lần")
        ra[ten] = doc_mot_vai(mo_ta.strip())
    return ra


def _loi(no: int, message: str):
    from .parse import ParseError  # tránh vòng import
    return ParseError(no, message)


def _nguoi(nd: str, no: int, dan_vai: dict) -> dict:
    tu = nd.split()
    if len(tu) != 2:
        raise _loi(no, "`nguoi` có dạng `<vai> <tư thế>`, ví dụ `nguoi: hoc-sinh-nam chi-tay`.")
    vai, tu_the = tu
    if vai not in dan_vai and vai not in VAI_SAN:
        raise _loi(no, f"Vai `{vai}` chưa khai báo ở khoá đầu `vai` và không phải vai làm sẵn ({', '.join(VAI_SAN)}).")
    if tu_the not in TU_THE:
        raise _loi(no, f"Tư thế `{tu_the}` không có; chọn một trong: {', '.join(TU_THE)}.")
    return {"vai": vai, "tuThe": tu_the}


def kiem_noi_dung(vat: str, nd: str, no: int, dan_vai: dict) -> None:
    """Kiểm nội dung các vật mới của video ngắn. Raise ParseError nêu đúng dòng."""
    du_lieu_vat(vat, nd, no, dan_vai)


def du_lieu_vat(vat: str, nd: str, no: int, dan_vai: dict) -> dict:
    """Nội dung vật mới → dữ liệu cho trang (đồng thời là bước kiểm)."""
    from . import hinh as _hinh
    from .vox import hien

    if not nd:
        raise _loi(no, f"Nhịp `{vat}` chưa có nội dung.")
    if vat == "nguoi":
        return _nguoi(nd, no, dan_vai)
    if vat == "nhom":
        muc = [m.strip() for m in nd.split(";")]
        if not 2 <= len(muc) <= 4:
            raise _loi(no, "`nhom` có 2 đến 4 người cách nhau bằng `;`, ví dụ `nhom: hoc-sinh-nam dung; hoc-sinh-nu chao`.")
        return {"ds": [_nguoi(m, no, dan_vai) for m in muc]}
    if vat == "bieu-tuong":
        ten, _, nhan = (x.strip() for x in nd.partition("|"))
        if len(nhan) > 24:
            raise _loi(no, f"Nhãn của `bieu-tuong` dài {len(nhan)} ký tự, tối đa 24.")
        try:
            return {"hinh": _hinh.doc(ten), "nhan": hien(nhan)}
        except _hinh.HinhError as exc:
            raise _loi(no, f"`bieu-tuong`: {exc}") from None
    if vat == "luoi-cham":
        so, _, chu = (x.strip() for x in nd.partition("|"))
        m = re.match(r"^(\d+)\s*/\s*(\d+)$", so)
        if m is None or not 1 <= int(m.group(2)) <= 200 or int(m.group(1)) > int(m.group(2)):
            raise _loi(no, "`luoi-cham` có dạng `<số chấm sáng>/<tổng ≤ 200> | <chú thích>`, ví dụ "
                           "`luoi-cham: 68/100 | học sinh ngủ sau 23 giờ`.")
        if len(hien(chu)) > 50:
            raise _loi(no, f"Chú thích của `luoi-cham` dài {len(hien(chu))} ký tự, tối đa 50.")
        return {"sang": int(m.group(1)), "tong": int(m.group(2)), "chuThich": hien(chu)}
    if vat == "truoc-sau":
        p = [x.strip() for x in nd.split("|")]
        ab = [x.strip() for x in p[0].split("->")]
        if len(ab) != 2 or not all(ab) or len(p) > 3:
            raise _loi(no, "`truoc-sau` có dạng `<trước> -> <sau> | <nhãn trước> | <nhãn sau>`, ví dụ "
                           "`truoc-sau: 80,4% -> 71,8% | đủ suy luận | bản tóm tắt`.")
        nhan = (p[1:] + ["", ""])[:2]
        if any(len(hien(x)) > 12 for x in ab) or any(len(hien(x)) > 20 for x in nhan):
            raise _loi(no, "`truoc-sau`: hai giá trị tối đa 12 ký tự, hai nhãn tối đa 20 ký tự.")
        return {"truoc": hien(ab[0]), "sau": hien(ab[1]), "nhanTruoc": hien(nhan[0]), "nhanSau": hien(nhan[1])}
    if vat == "tin-nhan":
        muc = [m.strip() for m in nd.split(";") if m.strip()]
        ra = []
        for m in muc:
            ai, _, cau = (x.strip() for x in m.partition(":"))
            if ai not in ("ban", "minh") or not cau:
                raise _loi(no, "Mỗi tin của `tin-nhan` có dạng `ban: <câu>` (người kia, bên trái) hoặc `minh: <câu>` "
                               "(bên phải), cách nhau bằng `;`.")
            if len(hien(cau)) > 70:
                raise _loi(no, f"Một tin của `tin-nhan` dài {len(hien(cau))} ký tự, tối đa 70.")
            ra.append({"ai": ai, "chu": hien(cau)})
        if not 1 <= len(ra) <= 3:
            raise _loi(no, "`tin-nhan` có 1 đến 3 tin.")
        return {"ds": ra}
    if vat == "thong-bao":
        p = [x.strip() for x in nd.split("|")]
        if len(p) != 3 or not all(p):
            raise _loi(no, "`thong-bao` có dạng `<ứng dụng> | <tiêu đề> | <nội dung>`.")
        for chu, toi_da, ten in zip(p, (16, 40, 70), ("ứng dụng", "tiêu đề", "nội dung")):
            if len(hien(chu)) > toi_da:
                raise _loi(no, f"{ten} của `thong-bao` dài {len(hien(chu))} ký tự, tối đa {toi_da}.")
        return {"ungDung": hien(p[0]), "tieuDe": hien(p[1]), "noiDung": hien(p[2])}
    if vat == "trich-dan":
        cau, _, ai = (x.strip() for x in nd.rpartition("|")) if "|" in nd else (nd.strip(), "", "")
        cau = cau.strip('"“” ')
        if not cau or len(hien(cau)) > 120 or len(ai) > 40:
            raise _loi(no, "`trich-dan` có dạng `\"<câu ≤ 120 ký tự>\" | <người nói ≤ 40 ký tự>`.")
        return {"cau": hien(cau), "ai": hien(ai)}
    raise _loi(no, f"Vật `{vat}` không có ở video ngắn.")


def kiem_canh(scene, dan_vai: dict) -> None:
    """Kiểm cảnh video ngắn: vật, ô, cụm từ đúng thứ tự (dùng lại vox.tim_cum)."""
    from . import vox

    tokens = vox.khoa_tu(scene.loi)
    vi_tri = 0
    for n in scene.nhip:
        if n.vat not in VAT:
            raise _loi(n.dong, f"Video ngắn dùng các vật: {', '.join(VAT)}.")
        if n.o is not None and n.o not in O:
            raise _loi(n.dong, f"Ô `{n.o}` không có ở video ngắn; ô đúng: {', '.join(O)} (bỏ trống để tự xếp).")
        for t in n.tuy_chon:
            if t == "dien-thoai" and n.vat != "tin-nhan":
                raise _loi(n.dong, "Tuỳ chọn `dien-thoai` chỉ dùng cho `tin-nhan`.")
        if n.vat in VAT_MOI:
            kiem_noi_dung(n.vat, n.noi_dung, n.dong, dan_vai)
        if n.cum == "@dau":
            continue
        i = vox.tim_cum(tokens, n.cum, vi_tri)
        if i < 0:
            if vox.tim_cum(tokens, n.cum, 0) >= 0:
                raise _loi(n.dong, f"Cụm \"{n.cum}\" nằm trước cụm của nhịp trước trong lời; viết các nhịp theo đúng "
                                   "thứ tự lời đọc.")
            raise _loi(n.dong, f"Cụm \"{n.cum}\" không có trong lời của Cảnh {scene.so}: \"{scene.loi}\". "
                               "Chép đúng vài từ liền nhau trong lời.")
        vi_tri = i + len(vox.khoa_tu(n.cum))


def du_lieu_canh(scene, cl, meta: dict, dan_vai: dict) -> dict:
    """Dữ liệu trang của một cảnh video ngắn (runtime/ngan.js)."""
    from . import kho as _kho
    from . import lich as _lich
    from . import vox

    dan_dau = getattr(cl, "dan_dau", _lich.DAN_DAU)
    cac_bat_dau = vox.moc_nhip(scene.nhip, cl.moc_tu, dan_dau)
    nhip = []
    vai_dung = {}
    for n, bat_dau in zip(scene.nhip, cac_bat_dau):
        d = vox._nhip_du_lieu(n, n.o, bat_dau)
        if n.vat in VAT_MOI:
            d["moi"] = du_lieu_vat(n.vat, n.noi_dung, n.dong, dan_vai)
            for ng in ([d["moi"]] if n.vat == "nguoi" else d["moi"].get("ds", []) if n.vat == "nhom" else []):
                vai_dung[ng["vai"]] = dan_vai.get(ng["vai"]) or VAI_SAN[ng["vai"]]
        nhip.append(d)
    return {
        "so": scene.so, "loai": "ngan", "thoiLuong": cl.thoi_luong, "danDau": dan_dau,
        "kho": _kho.tu_meta(meta).du_lieu(), "giaoDien": meta.get("giao-dien", GIAO_DIEN[0]),
        "tieuDe": vox.hien(scene.truong.get("tieu-de", [""])[0]), "chuong": scene.truong.get("chuong", [""])[0],
        "nhip": nhip, "vai": vai_dung, "tu": list(cl.moc_tu), "loat": None,
        "phuDe": phu_de(scene.truong.get("loi-phu-de", [scene.loi])[0], cl),
        "co": {"chuyen": scene.so > 1}, "dongNguon": [],
    }


# ---- Phụ đề vẽ trong trang (ngan.js): từng dòng ngắn, căn giữa, từ khoá theo dấu nhấn của lời ----
# `==x==` tô nền (font Baloo), `((x))` khoanh, `__x__` gạch chân, `**x**` chữ nhấn to khác font, `{{số}}` số to.
# ` / ` trong lời là chỗ AI gợi ý ngắt dòng phụ đề (không đọc).
PHU_DE_DONG = 26           # ký tự tối đa một dòng phụ đề (trang tự thu nhỏ chữ nếu dòng vẫn quá rộng)
NGAT_GOI_Y = " / "
_CUM_RE = re.compile(r"==(.+?)==|\(\((.+?)\)\)|__(.+?)__|\*\*(.+?)\*\*|\{\{(-?\d+(?:\.\d+)?)\}\}")
_KIEU_CUM = ("to", "khoanh", "gach", "nhan", "so")
# Hư từ: nên ngắt TRƯỚC chúng (mở dòng mới), không để chúng treo cuối dòng.
HU_TU = frozenset("là và của có những các cho với khi nếu thì mà nhưng để được bị đã sẽ đang rất cũng vẫn "
                  "như từ ở trong ngoài trên dưới về này đó kia gì nào hay hoặc vì nên bởi tại theo sau trước "
                  "giữa cùng đều".split())


def bo_ngat(loi: str) -> str:
    """Lời để đọc: bỏ dấu gợi ý ngắt dòng ` / `."""
    return re.sub(r"\s+/\s+", " ", loi)


def tach_tu(loi: str) -> list:
    """Lời (còn dấu nhấn, còn ` / `) → [{chu, kieu, cum, ngat}]: `kieu` của từ trong cụm nhấn, `cum` mã cụm (không
    ngắt giữa cụm), `ngat` = có gợi ý ngắt dòng ngay trước từ này."""
    ra, cum, ngat = [], 0, False
    vi_tri = 0
    for m in list(_CUM_RE.finditer(loi)) + [None]:
        truoc = loi[vi_tri:m.start() if m else len(loi)]
        for phan in re.split(r"(\s/\s)", truoc):
            if phan == " / " or (phan.strip() == "/" and phan != truoc):
                ngat = True
                continue
            for w in phan.split():
                if w == "/":
                    ngat = True
                    continue
                ra.append({"chu": w, "kieu": None, "cum": None, "ngat": ngat})
                ngat = False
        if m is None:
            break
        k = next(i for i in range(5) if m.group(i + 1) is not None)
        noi = m.group(k + 1).replace(".", ",") if _KIEU_CUM[k] == "so" else m.group(k + 1)
        cum += 1
        tu = noi.split()
        for j, w in enumerate(tu):
            ra.append({"chu": w, "kieu": _KIEU_CUM[k], "cum": cum, "ngat": ngat and j == 0})
        ngat = False
        vi_tri = m.end()
    # Dấu câu dính liền sau cụm nhấn ("((sao băng))?") thuộc về từ cuối của cụm.
    gop = []
    for w in ra:
        if gop and w["kieu"] is None and re.fullmatch(r"[.,!?;:…)\]”\"]+", w["chu"]) and gop[-1]["kieu"] is not None:
            gop[-1] = {**gop[-1], "chu": gop[-1]["chu"] + w["chu"]}
            continue
        gop.append(w)
    return gop


def _dai(ws: list) -> int:
    return len(" ".join(w["chu"] for w in ws))


def chia_dong(ws: list, toi_da: int = PHU_DE_DONG) -> list:
    """Chia một câu thành các dòng phụ đề: ngắt ở gợi ý ` / ` và sau dấu phẩy; đoạn dài hơn `toi_da` chia thành ít
    dòng nhất, dài gần bằng nhau, ưu tiên ngắt trước hư từ, không ngắt giữa cụm nhấn, không để hư từ treo cuối dòng."""
    doan, cur = [], []
    for w in ws:
        if cur and w["ngat"]:
            doan.append(cur)
            cur = []
        cur.append(w)
        if w["chu"][-1:] in ",;:" and w["cum"] is None:
            doan.append(cur)
            cur = []
    if cur:
        doan.append(cur)
    ra = []
    for d in doan:
        if _dai(d) <= toi_da:
            ra.append(d)
            continue
        ra.extend(_chia_can_bang(d, toi_da))
    return ra


def _chi_phi_ngat(ws: list, i: int) -> float:
    """Chi phí ngắt giữa ws[i-1] và ws[i]."""
    a, b = ws[i - 1], ws[i]
    if a["cum"] is not None and a["cum"] == b["cum"]:
        return 1e9                                   # không bao giờ ngắt giữa cụm nhấn
    gia = 0.0
    if b["chu"].lower().strip(".,!?") in HU_TU:
        gia -= 14                                    # mở dòng bằng hư từ: tốt
    if a["chu"].lower().strip(".,!?") in HU_TU:
        gia += 22                                    # hư từ treo cuối dòng: xấu
    if a.get("cap") is not None and a.get("cap") == b.get("cap"):
        gia += 45                                    # giữa một cặp hai tiếng (đoán là một từ ghép): rất xấu
    if b["cum"] is not None or a["cum"] is not None:
        gia -= 6                                     # ranh giới cụm nhấn: chỗ ngắt tự nhiên
    return gia


def _danh_cap(ws: list) -> None:
    """Đoán từ ghép: trong mỗi chuỗi thực từ liền nhau (giữa hư từ, dấu câu, cụm nhấn), ghép từng cặp hai tiếng từ
    đầu chuỗi (đa số từ tiếng Việt có hai tiếng): "sóng dữ", "nguyên nhân", "khoa học". Gán `cap` cho từng từ."""
    cap, chuoi = 0, []

    def dong_chuoi():
        nonlocal cap
        for k in range(0, len(chuoi) - 1, 2):
            cap += 1
            chuoi[k]["cap"] = chuoi[k + 1]["cap"] = cap
        chuoi.clear()

    for w in ws:
        w["cap"] = None
        tu = w["chu"].lower().strip(".,!?;:…\"“”()")
        if w["cum"] is not None or tu in HU_TU or not tu.isalpha():
            dong_chuoi()
            continue
        chuoi.append(w)
        if w["chu"][-1:] in ".,!?;:…":
            dong_chuoi()
    dong_chuoi()


def _chia_can_bang(ws: list, toi_da: int) -> list:
    _danh_cap(ws)
    n = len(ws)
    best = {0: (0.0, [])}
    # Quy hoạch động: best[j] = (chi phí nhỏ nhất chia ws[:j], các điểm ngắt).
    for j in range(1, n + 1):
        cand = None
        for i in range(0, j):
            if i not in best:
                continue
            dai = _dai(ws[i:j])
            if dai > toi_da and j - i > 1:
                continue
            gia = best[i][0] + (toi_da - dai) ** 2 * 0.15 + 40 + (_chi_phi_ngat(ws, i) if i > 0 else 0)
            if dai < 9:
                gia += 60                            # dòng quá ngắn ("rồi đưa"): xấu
            if cand is None or gia < cand[0]:
                cand = (gia, best[i][1] + [i])
        if cand is not None:
            best[j] = cand
    diem = best[n][1] + [n]
    return [ws[diem[k]:diem[k + 1]] for k in range(len(diem) - 1) if diem[k] < diem[k + 1]]


def phu_de(loi_goc: str, cl) -> list:
    """Các dòng phụ đề của cảnh: [{tu: giây bắt đầu, den: giây kết thúc, chu: [{chu, kieu, cum, t}]}] (giây trong cảnh)."""
    from . import karaoke

    ws = tach_tu(loi_goc)
    if not ws:
        return []
    dan_dau = getattr(cl, "dan_dau", 1.0)
    het_tieng = dan_dau + cl.giay_giong
    moc = karaoke._mocs_tu_kich_ban([w["chu"] for w in ws], list(cl.moc_tu), dan_dau, het_tieng)
    for w, t in zip(ws, moc):
        w["t"] = round(t, 3)
    # Chia theo câu (dấu . ? ! cuối từ), rồi chia dòng trong câu.
    cau, cur = [], []
    for w in ws:
        cur.append(w)
        if w["chu"][-1:] in ".?!…":
            cau.append(cur)
            cur = []
    if cur:
        cau.append(cur)
    dong = [d for c in cau for d in chia_dong(c)]
    ra = []
    for k, d in enumerate(dong):
        den = dong[k + 1][0]["t"] if k + 1 < len(dong) else max(het_tieng + 0.3, d[-1]["t"] + 0.6)
        ra.append({"tu": d[0]["t"], "den": round(min(den, cl.thoi_luong), 3),
                   "chu": [{"chu": w["chu"], "kieu": w["kieu"], "cum": w["cum"], "t": w["t"]} for w in d]})
    return ra

"""Lịch thời gian: tách câu, mốc câu, mốc hiện ý, thời lượng cảnh, dữ liệu JSON cho trang. Chỉ dùng thư viện chuẩn."""

from __future__ import annotations

import math
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

from . import kho, phong
from .kiem import CanhError, ma_do, tham_so_theo_thoi_gian
from .parse import Scene, phan_cong_thuc, tach_du_lieu

FPS = 30
DAN_DAU = 1.0
LAU_BANG = 0.5
DUOI = 0.6
CHO_GIAI = 0.4  # cảnh câu hỏi: khoảng lặng sau đếm ngược, trước khi hiện đáp án và đọc lời giải
TOI_THIEU = 2.5
CANH_DAI = 40.0
NGUON_NHAC_GIAY = 4.0  # dòng nguồn nhạc nền hiện trong 4 s cuối video (ở cảnh cuối)
VIDEO_DAI = 480.0
_CAU_RE = re.compile(r"(?<=[.!?…])\s+")
_KHOA_RE = re.compile(r"[^\w\s]", re.UNICODE)


@dataclass
class GiongInfo:
    mp3: Path | None
    giay: float
    moc_cau: list
    uoc_luong: bool
    nguon: str
    moc_tu: list = field(default_factory=list)
    uoc_luong_tu: bool = True
    # Cảnh câu hỏi: giọng lời giải (file `canh-<số>-giai.mp3`); cảnh khác là None.
    giai: GiongInfo | None = None


@dataclass
class CanhLich:
    so: int
    bat_dau: float
    thoi_luong: float
    so_khung: int
    giay_giong: float
    cau: list
    moc_cau: list
    moc_cau_giong: list
    uoc_luong: bool
    moc_tu: list = field(default_factory=list)
    # Cảnh câu hỏi: lời giải bắt đầu ở `bat_dau_giai` (giây trong cảnh), cùng lúc hiện đáp án; cảnh khác là None.
    giay_giai: float = 0.0
    bat_dau_giai: float | None = None
    cau_giai: list = field(default_factory=list)
    moc_cau_giai: list = field(default_factory=list)


def tach_cau(loi: str) -> list:
    return [cau.strip() for cau in _CAU_RE.split(loi.strip()) if cau.strip()]


def moc_uoc_luong(cau: list, giay: float) -> list:
    tong = sum(len(c) for c in cau) or 1
    da_qua = 0
    moc = []
    for c in cau:
        moc.append(round(da_qua / tong * giay, 3))
        da_qua += len(c)
    return moc


def khoa_so_khop(chu: str) -> str:
    """Khoá so khớp chữ (dùng chung cho mốc câu, karaoke, nhấn ý): NFC, bỏ dấu câu, chữ thường, giữ dấu thanh — như
    `khoa` của runtime/nhan.js. NFC trước khi lọc: lớp `\\w` của regex Python bỏ dấu tổ hợp nên "kì" NFD sẽ thành "ki"."""
    return _KHOA_RE.sub("", unicodedata.normalize("NFC", chu)).lower()


def moc_tu_uoc_luong(loi: str, moc_cau_giong: list, giay: float) -> list:
    bien = list(moc_cau_giong) + [giay]
    ket: list = []
    for i, c in enumerate(tach_cau(loi)):
        tu = c.split()
        if not tu:
            continue
        start = bien[i] if i < len(bien) else giay
        end = bien[i + 1] if i + 1 < len(bien) else giay
        dai = max(end - start, 0.0)
        tong = sum(len(t) for t in tu) or 1
        da_qua = 0
        for t in tu:
            t0 = start + da_qua / tong * dai
            da_qua += len(t)
            t1 = start + da_qua / tong * dai
            ket.append({"t": round(t0, 3), "d": round(max(t1 - t0, 0.0), 3), "chu": t})
    return ket


def thoi_luong_canh(giay_giong: float, fps: int = FPS) -> float:
    tho = max(TOI_THIEU, DAN_DAU + giay_giong + DUOI)
    return math.ceil(tho * fps - 1e-9) / fps


def moc_hien(so_muc: int, moc_cau_giong: list, giay: float) -> list:
    if so_muc <= 0:
        return []
    if len(moc_cau_giong) >= so_muc:
        return list(moc_cau_giong[:so_muc])
    return [round(k * giay / so_muc, 3) for k in range(so_muc)]


def so_muc(scene: Scene) -> int:
    t = scene.truong
    return {
        "y-tung-y": len(t.get("y", [])),
        "quy-trinh": len(t.get("buoc", [])),
        "so-sanh": len(t.get("y-trai", [])) + len(t.get("y-phai", [])),
        "do-thi": len(t.get("diem", [])),
        "cong-thuc": so_phan_cong_thuc(scene) + len(t.get("giai-thich", [])),
        "minh-hoa": len(t.get("hinh", [])),
        "bieu-do": len(t.get("du-lieu", [])),
        "so-do": len(t.get("nhanh", [])),
        "dong-thoi-gian": len(t.get("moc", [])),
        "cau-hoi": 1 + len(t.get("lua-chon", [])),
    }.get(scene.loai, 0)


def so_phan_cong_thuc(scene: Scene) -> int:
    """Số phần của `bieu-thuc` khi tách bằng ` | ` (mỗi phần hiện ở một mốc câu); không tách thì 0."""
    phan = phan_cong_thuc(scene.truong.get("bieu-thuc", [""])[0])
    return len(phan) if len(phan) > 1 else 0


def thoi_luong_cau_hoi(giay_hoi: float, cho: float, giay_giai: float, fps: int = FPS) -> float:
    """Cảnh câu hỏi: dẫn đầu + giọng câu hỏi + `cho` giây đếm ngược + 0,4 s + giọng lời giải + đuôi."""
    tho = DAN_DAU + giay_hoi + cho + CHO_GIAI + giay_giai + DUOI
    return math.ceil(tho * fps - 1e-9) / fps


def _moc_loi(so: int, loi: str, giong: GiongInfo, dau: float, ten: str, warnings: list) -> tuple:
    """(câu, mốc câu trong giọng, mốc từ trong cảnh, có ước lượng câu) của một lời bắt đầu ở giây `dau` của cảnh."""
    cau = tach_cau(loi)
    uoc = giong.uoc_luong or len(giong.moc_cau) != len(cau)
    moc_giong = moc_uoc_luong(cau, giong.giay) if uoc else list(giong.moc_cau)
    uoc_tu = giong.uoc_luong_tu or not giong.moc_tu
    tu_tho = moc_tu_uoc_luong(loi, moc_giong, giong.giay) if uoc_tu else list(giong.moc_tu)
    if uoc and uoc_tu:
        warnings.append(f"Cảnh {so}: mốc câu và mốc từng từ {ten}ước lượng theo số/tỉ lệ ký tự; "
                         "hình, nhấn ý và phụ đề karaoke có thể lệch tiếng vài trăm mili giây.")
    elif uoc:
        warnings.append(f"Cảnh {so}: mốc câu {ten}ước lượng theo số ký tự; hình có thể lệch tiếng vài trăm mili giây.")
    elif uoc_tu:
        warnings.append(f"Cảnh {so}: mốc từng từ {ten}ước lượng theo tỉ lệ ký tự; nhấn ý và phụ đề karaoke có thể lệch tiếng vài trăm mili giây.")
    moc_tu = [{"t": round(dau + w["t"], 3), "d": round(w.get("d", 0.0), 3), "chu": w["chu"], "khoa": khoa_so_khop(w["chu"])}
              for w in tu_tho]
    return cau, moc_giong, moc_tu, uoc


def doan_loi(cl: CanhLich) -> list:
    """Các đoạn lời của cảnh theo thời gian cảnh: [(câu, mốc câu, lúc hết giọng, mốc từ)]. Cảnh câu hỏi có thêm
    đoạn lời giải bắt đầu ở `bat_dau_giai`; khoảng đếm ngược ở giữa không có phụ đề."""
    if cl.bat_dau_giai is None:
        return [(cl.cau, cl.moc_cau, DAN_DAU + cl.giay_giong, list(cl.moc_tu))]
    return [(cl.cau, cl.moc_cau, DAN_DAU + cl.giay_giong, [w for w in cl.moc_tu if w["t"] < cl.bat_dau_giai - 1e-6]),
            (cl.cau_giai, cl.moc_cau_giai, cl.bat_dau_giai + cl.giay_giai,
             [w for w in cl.moc_tu if w["t"] >= cl.bat_dau_giai - 1e-6])]


def dung_lich(cac_canh: list, cac_giong: list, fps: int = FPS, kiem_moc: bool = True) -> tuple:
    plan: list = []
    warnings: list = []
    bat_dau = 0.0
    for scene, giong in zip(cac_canh, cac_giong):
        cau, moc_giong, moc_tu, uoc = _moc_loi(scene.so, scene.loi, giong, DAN_DAU, "", warnings)
        thoi_luong = thoi_luong_canh(giong.giay, fps)
        giai: dict = {}
        if scene.loai == "cau-hoi":
            if giong.giai is None:
                raise ValueError(f"Cảnh {scene.so} (câu hỏi) thiếu giọng lời giải.")
            cho = int(scene.truong["cho"][0])
            bat_dau_giai = round(DAN_DAU + giong.giay + cho + CHO_GIAI, 3)
            cau_g, moc_g, tu_g, _ = _moc_loi(scene.so, scene.truong["loi-giai"][0], giong.giai, bat_dau_giai,
                                             "của lời giải ", warnings)
            moc_tu = moc_tu + tu_g
            thoi_luong = thoi_luong_cau_hoi(giong.giay, cho, giong.giai.giay, fps)
            giai = {"giay_giai": giong.giai.giay, "bat_dau_giai": bat_dau_giai, "cau_giai": cau_g,
                    "moc_cau_giai": [round(bat_dau_giai + m, 3) for m in moc_g]}
        if thoi_luong > CANH_DAI:
            warnings.append(f"Cảnh {scene.so}: dài {thoi_luong:.0f} giây (quá 40 giây); nên tách thành hai cảnh.")
        if kiem_moc and scene.loai == "thi-nghiem":
            for value, no in zip(scene.truong.get("tham-so", []), scene.dong_truong.get("tham-so", [])):
                giay = float(value.split()[0])
                if giay > thoi_luong:
                    raise CanhError(scene.so, f"mốc `tham-so` {giay:g} giây (dòng {no}) vượt thời lượng cảnh {thoi_luong:.1f} giây.")
        plan.append(CanhLich(
            so=scene.so, bat_dau=bat_dau, thoi_luong=thoi_luong, so_khung=round(thoi_luong * fps),
            giay_giong=giong.giay, cau=cau, moc_cau=[round(DAN_DAU + m, 3) for m in moc_giong],
            moc_cau_giong=moc_giong, uoc_luong=uoc, moc_tu=moc_tu, **giai,
        ))
        bat_dau += thoi_luong
    if bat_dau > VIDEO_DAI:
        warnings.append(f"Video dài {bat_dau / 60:.1f} phút (quá 8 phút); nên tách thành nhiều video.")
    return plan, warnings


CHUYEN_XOAY = ("lau-bang", "lat-trang", "truot", "phong", "mo-man")


def kieu_chuyen(scene: Scene, meta: dict):
    """Kiểu chuyển cảnh vào cảnh này: trường `chuyen:` của cảnh, không có thì khoá đầu; cảnh 1 và `khong` là None."""
    if scene.so <= 1:
        return None
    kieu = scene.truong.get("chuyen", [None])[0] or meta.get("chuyen-canh", "lau-bang")
    if kieu == "luan-phien":
        return CHUYEN_XOAY[(scene.so - 2) % len(CHUYEN_XOAY)]
    return None if kieu == "khong" else kieu


def gan_nguon_nhac(du: dict, nguon: str) -> dict:
    """Gắn dòng nguồn nhạc vào dữ liệu cảnh cuối: hiện từ `tu` (giây trong cảnh) tới hết cảnh."""
    du["nhacNguon"] = {"chu": nguon, "tu": round(max(0.0, du["thoiLuong"] - NGUON_NHAC_GIAY), 3)}
    return du


def du_lieu_canh(scene: Scene, cl: CanhLich, model=None, tai_nguyen: dict | None = None) -> dict:
    tai_nguyen = tai_nguyen or {}
    meta = tai_nguyen.get("meta", {})
    chuyen = kieu_chuyen(scene, meta)
    du = {
        "so": scene.so,
        "loai": scene.loai,
        "thoiLuong": cl.thoi_luong,
        "danDau": DAN_DAU,
        "giayLauBang": LAU_BANG,
        "truong": scene.truong,
        "moc": [round(DAN_DAU + m, 3) for m in moc_hien(so_muc(scene), cl.moc_cau_giong, cl.giay_giong)],
        "tu": list(cl.moc_tu),
        "hinh": tai_nguyen.get("hinh"),
        "anh": tai_nguyen.get("anh"),
        "hinhs": tai_nguyen.get("hinhs", []),
        "co": {
            "banTay": meta.get("ban-tay", "co") == "co",
            "mayQuay": meta.get("may-quay", "co") == "co",
            "lauBang": chuyen == "lau-bang",
            "chuDong": meta.get("chu-dong", "co") == "co",
            "chuyen": chuyen,
        },
        "nenTruoc": None,
        "kho": kho.tu_meta(meta).du_lieu(),
        "chuDe": phong.chu_de(meta.get("phong-cach")),
    }
    if scene.loai == "do-thi":
        du["diem"] = [[float(p) for p in v.split(",")] for v in scene.truong["diem"]]
    if scene.loai == "bieu-do":
        du["duLieu"] = [[nhan, float(so)] for nhan, so in map(tach_du_lieu, scene.truong["du-lieu"])]
    if scene.loai == "cau-hoi":
        du["cauHoi"] = {"batDauDem": round(DAN_DAU + cl.giay_giong, 3), "cho": int(scene.truong["cho"][0]),
                        "batDauGiai": round(cl.bat_dau_giai, 3), "dapAn": scene.truong["dap-an"][0]}
    if scene.loai == "thi-nghiem":
        du["khaiBao"] = model.khai_bao
        du["thamSo"] = {ma: [[g, v] for g, v in ds] for ma, ds in tham_so_theo_thoi_gian(scene).items()}
        du["do"] = ma_do(scene, model)
    return du

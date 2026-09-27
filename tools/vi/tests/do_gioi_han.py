"""Đo giới hạn chữ bằng Chromium: độ dài lớn nhất của từng trường mà cảnh vẫn nằm gọn trong khung và trên vạch phụ đề,
theo khổ (`ngang`/`doc`) và phong cách (`viet-tay`/`cat-dan`). Dùng lại khi đổi font, bố cục hay khổ.

Chuỗi thử có nhiều dấu ("Nghiêng nghiễm nhiên " lặp, cắt đúng độ dài), số dòng lặp tối đa, và biến thể có hình ở cột
phụ (`canh_toi_da` của test_video_ma_kho_doc). Một cảnh qua khi `THI_VIDEO.kiemTran()` rỗng và mọi phần tử của lớp bảng
nằm trong khung, đáy không quá vạch phụ đề.

Cách tìm của một loại cảnh: qua ở giới hạn hiện tại thì giữ; không qua thì hạ đồng loạt mọi trường theo cùng tỉ lệ tới khi
qua, rồi nâng từng trường lên hết mức còn qua (tìm nhị phân, hai vòng). Giới hạn chỉ hạ, không bao giờ nâng quá bảng gốc.

Chạy: C:/Users/ADMIN/vmt/v/Scripts/python.exe tools/vi/tests/do_gioi_han.py <ngang|doc> <viet-tay|cat-dan> [--co-the] [loai ...]
(in bảng JSON các trường phải hạ). `--co-the`: cảnh của bốn loại nhận thẻ có thêm thẻ ở giới hạn và dòng tài liệu 90 ký tự
(bảng kiem.bang_gioi_han(..., co_the=True)). Cần playwright và Chromium.
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

TESTS = Path(__file__).resolve().parent
sys.path.insert(0, str(TESTS.parent))
sys.path.insert(0, str(TESTS))

import video_ma  # noqa: E402
from test_video_ma_kho_doc import DO_HOP, canh_toi_da, chuoi, thu_muc_bai, video_md  # noqa: E402
from video_ma_parts import chup, kho, kiem, parse  # noqa: E402

LOAI_CO_COT = ("tieu-de", "khai-niem", "cong-thuc", "y-tung-y", "so-do")
# Loại cảnh nhận `the` và `tai-lieu`; dòng thêm vào cảnh khi đo hay kiểm "có thẻ": thẻ ở giới hạn (nhãn 24, giá trị 16,
# chú thích 60) và dòng tài liệu 90 ký tự, chữ nhiều dấu.
LOAI_CO_THE = ("tieu-de", "khai-niem", "cong-thuc", "y-tung-y")


def dong_the() -> str:
    return f"the: {chuoi(24)} | {chuoi(16)} | {chuoi(60)}\ntai-lieu: {chuoi(90)}\n"


def them_the(ds: list) -> list:
    """Các cảnh của `ds` thuộc LOAI_CO_THE, mỗi cảnh thêm thẻ và dòng tài liệu ở giới hạn."""
    return [(loai, noi + dong_the()) for loai, noi in ds if loai in LOAI_CO_THE]


def meta(ten_kho: str, phong_cach: str) -> str:
    return f"tieu-de: Đo giới hạn\nmon: Vật lí\nlop: 11\nkho: {ten_kho}\nphong-cach: {phong_cach}\n"


# Như DO_HOP nhưng ô chữ đo bằng hộp của chính dòng chữ (Range), không phải hộp ô: vài ô khổ ngang của vi.11 (chú thích
# ảnh, tên trục ngang của đồ thị) có đáy ô lố vạch phụ đề vài điểm dù chữ nằm trên vạch; ô tràn thì kiemTran đã báo.
DO_HOP_CHU = DO_HOP.replace(
    "bang.querySelectorAll('.chu').forEach((el) => them('chu:' + el.getAttribute('data-id'), el.getBoundingClientRect()));",
    "bang.querySelectorAll('.chu').forEach((el) => { const r = document.createRange(); r.selectNodeContents(el);"
    " them('chu:' + el.getAttribute('data-id'), r.getBoundingClientRect()); });")
assert DO_HOP_CHU != DO_HOP
# Nét vẽ tay (khung hộp, trục) của khổ ngang vi.11 nằm đúng vạch phụ đề và lượn ±2 điểm: nét được lố vạch tới 3 điểm.
LO_NET = 3


def ngoai_vung(page, html: str, ten_kho: str) -> tuple:
    """(kiemTran(), phần tử ra ngoài khung hoặc có đáy dưới vạch phụ đề; cho phép lệch 1 px, nét SVG 3 px)."""
    tran = chup.kiem_tran(page, html)
    k = kho.Kho(ten_kho, 1080)
    ra = [h for h in page.evaluate(DO_HOP_CHU)
          if h[1] < -1 or h[2] < -1 or h[3] > k.rong + 1 or h[4] > k.day + (LO_NET if h[0].startswith("svg:") else 1)]
    return tran, ra


class Do:
    """Một trình duyệt và một thư mục tạm cho nhiều lần đo cùng khổ và phong cách."""

    def __init__(self, page, tmp: Path, ten_kho: str, phong_cach: str, co_the: bool = False) -> None:
        self.page, self.tmp, self.ten_kho, self.phong_cach = page, tmp, ten_kho, phong_cach
        self.co_the = co_the
        self.dem = 0

    def loi(self, ds: list) -> list:
        """Các cảnh của `ds` không qua: [(số cảnh, loại, kiemTran, phần tử ra ngoài)]."""
        self.dem += 1
        thu_muc = thu_muc_bai(self.tmp / f"l{self.dem}", video_md(ds, meta(self.ten_kho, self.phong_cach)))
        video = parse.parse((thu_muc / "video.md").read_text(encoding="utf-8"))
        kq = []
        for canh, html in zip(video.canh, video_ma._trang_tam(video, thu_muc, video_ma._mo_hinh(video, thu_muc))):
            tran, ra = ngoai_vung(self.page, html, self.ten_kho)
            if tran or ra:
                kq.append((canh.so, canh.loai, tran, ra))
        return kq

    def qua(self, loai: str, L: dict, H: dict) -> bool:
        ds = [c for c in canh_toi_da(L, H) if c[0] == loai]
        if loai in LOAI_CO_COT:
            ds += [c for c in canh_toi_da(L, H, cot=True) if c[0] == loai]
        if self.co_the:
            ds = them_the(ds)
        return not self.loi(ds)


def truong_cua(loai: str, L: dict, H: dict) -> list:
    """Các khoá đo được của loại: (loai, truong) của bảng đơn, và (loai, truong, k) cho phần k của trường hai phần."""
    ds = [k for k in L if k[0] == loai]
    for (l, t), phan in H.items():
        if l == loai:
            ds += [(l, t, i) for i, g in enumerate(phan) if g is not None]
    return ds


def _lay(L: dict, H: dict, khoa: tuple) -> int:
    return L[khoa] if len(khoa) == 2 else H[khoa[:2]][khoa[2]]


def _dat(L: dict, H: dict, khoa: tuple, n: int) -> None:
    if len(khoa) == 2:
        L[khoa] = n
    else:
        phan = list(H[khoa[:2]])
        phan[khoa[2]] = n
        H[khoa[:2]] = tuple(phan)


def tim_loai(do: Do, loai: str, L: dict, H: dict) -> dict:
    """Giới hạn lớn nhất (không quá L, H cho vào) của mọi trường của `loai`: {khoá: n} chỉ gồm trường phải hạ."""
    L, H = dict(L), dict(H)
    if do.qua(loai, L, H):
        return {}
    khoa = truong_cua(loai, L, H)
    goc = {k: _lay(L, H, k) for k in khoa}

    def ti_le(f: float) -> tuple:
        L2, H2 = dict(L), dict(H)
        for k in khoa:
            _dat(L2, H2, k, max(1, int(goc[k] * f)))
        return L2, H2

    thap, cao = 0.0, 1.0
    for _ in range(7):
        giua = (thap + cao) / 2
        if do.qua(loai, *ti_le(giua)):
            thap = giua
        else:
            cao = giua
    L, H = ti_le(thap)
    for _ in range(2):
        for k in khoa:
            a, b = _lay(L, H, k), goc[k]
            while a < b:
                m = (a + b + 1) // 2
                L2, H2 = dict(L), dict(H)
                _dat(L2, H2, k, m)
                if do.qua(loai, L2, H2):
                    a = m
                else:
                    b = m - 1
            _dat(L, H, k, a)
    return {k: _lay(L, H, k) for k in khoa if _lay(L, H, k) < goc[k]}


def tim_gioi_han(loai: str, truong: str, ten_kho: str, phong_cach: str, phan: int | None = None) -> int:
    """Độ dài lớn nhất của một trường (các trường khác của loại giữ ở giới hạn bảng của khổ và phong cách)."""
    L, H = kiem.bang_gioi_han(ten_kho, phong_cach)
    khoa = (loai, truong) if phan is None else (loai, truong, phan)
    with tempfile.TemporaryDirectory() as tmp, chup.trinh_duyet() as browser:
        do = Do(chup.trang_moi(browser, kho.Kho(ten_kho, 720)), Path(tmp), ten_kho, phong_cach)
        a, b = 1, _lay(L, H, khoa)
        while a < b:
            m = (a + b + 1) // 2
            L2, H2 = dict(L), dict(H)
            _dat(L2, H2, khoa, m)
            if do.qua(loai, L2, H2):
                a = m
            else:
                b = m - 1
        return a


def bang_can_ha(ten_kho: str, phong_cach: str, cac_loai=None, co_the: bool = False) -> dict:
    """{loại: {khoá: n}} các trường phải hạ so với bảng hiện tại của khổ và phong cách (`co_the`: bảng cảnh có thẻ)."""
    L, H = kiem.bang_gioi_han(ten_kho, phong_cach, co_the)
    L, H = dict(L), dict(H)
    H = {k: (v[0], v[1] if v[1] is not None else parse.SO_DAI) if k == ("bieu-do", "du-lieu") else v for k, v in H.items()}
    kq = {}
    with tempfile.TemporaryDirectory() as tmp, chup.trinh_duyet() as browser:
        do = Do(chup.trang_moi(browser, kho.Kho(ten_kho, 720)), Path(tmp), ten_kho, phong_cach, co_the)
        for loai in cac_loai or (LOAI_CO_THE if co_the else parse.SCENE_TYPES):
            ha = tim_loai(do, loai, L, H)
            if ha:
                kq[loai] = ha
    return kq


if __name__ == "__main__":
    ten_kho, phong_cach, *cac_loai = sys.argv[1:]
    co_the = "--co-the" in cac_loai
    cac_loai = [l for l in cac_loai if l != "--co-the"]
    kq = bang_can_ha(ten_kho, phong_cach, cac_loai or None, co_the)
    print(json.dumps({l: {"|".join(map(str, k[1:])): n for k, n in v.items()} for l, v in kq.items()}, ensure_ascii=False))

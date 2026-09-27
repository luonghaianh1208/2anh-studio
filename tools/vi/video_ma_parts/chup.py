"""Chụp khung bằng Chromium: mở trang một cảnh, gọi datThoiDiem(t), chụp PNG. `playwright` chỉ import khi dùng."""

from __future__ import annotations

import base64
import contextlib
import json
import os
import sys
from concurrent.futures import FIRST_EXCEPTION, ProcessPoolExecutor, wait
from pathlib import Path
from types import SimpleNamespace

from video_parts.media import MediaError

from .kho import Kho
from .phong import CHU_VIET

FIX_CHROMIUM = (
    "Cài Chromium bằng: powershell -NoProfile -ExecutionPolicy Bypass -File tools\\vi\\pptmaster.ps1 "
    "-Action tool -Name chromium"
)
FIX_DUNG = "Chạy lại một lần; vẫn lỗi thì dán nguyên thông báo này cho người bảo trì."
FIX_GHI = "Kiểm tra ổ đĩa còn chỗ trống, đóng các file đang mở trong thư mục dự án rồi chạy lại."
# Khổ khi nơi gọi không truyền (test cũ): khung ngang 1280×720 của vi.11.
KHO_CU = Kho("ngang", 720)
# Khung tạm để ghép là JPEG chất lượng 95: với PNG, dựng Full HD chậm 1,75 lần 720 (số đo ở
# docs/vi/phat-trien/2026-09-27-video-ma-vi12-kiem-thu.md). Ảnh xem trước vẫn là PNG.
DUOI_KHUNG = "jpg"
CHAT_LUONG = 95


def ten_khung(i: int) -> str:
    return f"f{i:06d}.{DUOI_KHUNG}"


def _anh_khung(page, path=None):
    return page.screenshot(path=None if path is None else str(path), type="jpeg", quality=CHAT_LUONG)


class GhiKhungLoi(Exception):
    """OSError khi ghi hoặc đọc lại khung PNG (đầy ổ, bị khoá). Qua được pickle từ tiến trình con."""


class LoiBuocCon(Exception):
    """MediaError của tiến trình con (ví dụ `chromium`), giữ step và fix khi đi qua pickle."""

    def __init__(self, step: str, message: str, fix: str) -> None:
        super().__init__(step, message, fix)
        self.step, self.message, self.fix = step, message, fix

    def __str__(self) -> str:
        return self.message


def _mo(p):
    try:
        return p.chromium.launch(args=["--no-sandbox"])
    except Exception as first:
        base = Path(os.environ.get("LOCALAPPDATA", "")) / "ms-playwright"
        for pattern in ("chromium_headless_shell-*/*/chrome-headless-shell.exe", "chromium-*/*/chrome.exe"):
            for exe in sorted(base.glob(pattern), reverse=True):
                try:
                    return p.chromium.launch(executable_path=str(exe), args=["--no-sandbox"])
                except Exception:
                    continue
        raise MediaError("chromium", f"Không mở được Chromium: {first}", FIX_CHROMIUM) from first


@contextlib.contextmanager
def trinh_duyet():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise MediaError("chromium", "Chưa cài playwright (Chromium).", FIX_CHROMIUM) from exc
    with sync_playwright() as p:
        browser = _mo(p)
        try:
            yield browser
        finally:
            browser.close()


def trang_moi(browser, kho: Kho = KHO_CU):
    """Trang theo điểm CSS của khổ; ảnh chụp ra ở kích thước xuất (`device_scale_factor = kho.ti_le`)."""
    return browser.new_page(viewport={"width": kho.rong, "height": kho.cao}, device_scale_factor=kho.ti_le)


def mo_trang(page, html: str) -> None:
    page.set_content(html)
    page.wait_for_function("window.THI_VIDEO && window.THI_VIDEO.san === true", timeout=30000)
    page.evaluate(
        "(chuViet) => document.fonts.load(\"40px 'Itim'\", document.body.innerText + chuViet)", CHU_VIET,
    )
    # Mọi font nhúng của trang (cat-dan: Be Vietnam Pro 400 và 800) nạp xong trước khung đầu và trước khi đo.
    page.evaluate("() => Promise.all(Array.from(document.fonts).map((f) => f.load())).then(() => true)")
    page.evaluate("() => document.fonts.ready.then(() => true)")
    # Nền cảnh trước và ảnh phải giải mã xong trước khung đầu, nếu không khung t = 0 có thể trống.
    page.evaluate("() => Promise.all(Array.from(document.images).map((i) => i.decode().catch(() => null)))")


def kiem_tran(page, html: str) -> list:
    mo_trang(page, html)
    return list(page.evaluate("() => window.THI_VIDEO.kiemTran()"))


def doc_su_kien(page) -> list:
    """Sự kiện âm thanh [{t, loai, dai}] của cảnh đang mở (tính từ cùng dữ liệu và mốc như khung hình)."""
    return list(page.evaluate("() => window.THI_VIDEO.suKien()"))


def chup_canh(page, html: str, so_khung: int, fps: int, thu_muc: Path, so_dau: int) -> int:
    mo_trang(page, html)
    thu_muc.mkdir(parents=True, exist_ok=True)
    for i in range(so_khung):
        page.evaluate("(t) => window.datThoiDiem(t)", i / fps)
        _anh_khung(page, thu_muc / ten_khung(so_dau + i))
    return so_dau + so_khung


def chup_cuoi(page, html: str, duong_dan: Path) -> None:
    mo_trang(page, html)
    page.evaluate("() => window.datThoiDiem(window.THI_VIDEO.thoiDiemCuoi())")
    duong_dan.parent.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(duong_dan), type="png")


def so_tien_trinh() -> int:
    return max(1, min(4, (os.cpu_count() or 2) // 2))


def chia_dai(so_khung_moi_canh: list, so_tien_trinh: int) -> list:
    """Chia các cảnh thành dải liên tiếp [dau, cuoi) có tổng khung gần đều (tham lam theo tổng tích luỹ)."""
    n = len(so_khung_moi_canh)
    so_dai = max(1, min(so_tien_trinh, n))
    tong = sum(so_khung_moi_canh)
    dai, dau, tich_luy = [], 0, 0
    for k in range(n - 1):
        if len(dai) == so_dai - 1:
            break
        tich_luy += so_khung_moi_canh[k]
        dich = tong * (len(dai) + 1) / so_dai
        vuot_neu_them = tich_luy + so_khung_moi_canh[k + 1] - dich
        if tich_luy >= dich or vuot_neu_them > dich - tich_luy:
            dai.append((dau, k + 1))
            dau = k + 1
    dai.append((dau, n))
    return dai


def _data_url(jpg: bytes) -> str:
    return "data:image/jpeg;base64," + base64.b64encode(jpg).decode("ascii")


def chup_dai(cong_viec: dict) -> int:
    """Chụp một dải cảnh trong một Chromium riêng. Chạy được trong tiến trình con Windows `spawn`.

    `cac_du`, `so_khung`, `khung_dau` chỉ gồm các cảnh của dải, thêm cảnh ngay trước (để dựng nền lau bảng);
    `dau`, `cuoi` là chỉ số trong các danh sách đó, còn `khung_dau` giữ số thứ tự khung của cả video.
    """
    from . import trang

    cac_du = [dict(du) for du in cong_viec["cac_du"]]
    models = {int(so): SimpleNamespace(js=js) for so, js in cong_viec["models_js"].items()}
    dau, cuoi, fps = cong_viec["dau"], cong_viec["cuoi"], cong_viec["fps"]
    khung_dau, so_khung = cong_viec["khung_dau"], cong_viec["so_khung"]
    thu_muc = Path(cong_viec["thu_muc_anh"])
    # Có `thu_muc_su_kien`: đọc sự kiện âm thanh của mỗi cảnh ngay trên trang vừa chụp (không mở thêm trang).
    thu_muc_su_kien = Path(cong_viec["thu_muc_su_kien"]) if cong_viec.get("thu_muc_su_kien") else None
    kho = Kho(*cong_viec["kho"]) if cong_viec.get("kho") else KHO_CU

    def html(k: int) -> str:
        return trang.dung_trang(cac_du[k], models.get(cac_du[k]["so"]))

    def can_nen(k: int) -> bool:
        # Mọi kiểu chuyển cảnh cần khung cuối cảnh trước; `lauBang` giữ cho dữ liệu kiểu cũ.
        co = cac_du[k]["co"] if k < len(cac_du) else {}
        return bool(co.get("chuyen") or co.get("lauBang"))

    da_ghi = 0
    with trinh_duyet() as browser:
        page = trang_moi(browser, kho)
        if dau > 0 and can_nen(dau):
            # Khung cuối cảnh trước (t = (số khung − 1)/fps) dựng lại tại chỗ, không chờ tiến trình khác.
            mo_trang(page, html(dau - 1))
            page.evaluate("(t) => window.datThoiDiem(t)", (so_khung[dau - 1] - 1) / fps)
            cac_du[dau]["nenTruoc"] = _data_url(_anh_khung(page))
        for k in range(dau, cuoi):
            print(f"Chụp cảnh {cac_du[k]['so']} ({so_khung[k]} khung)...", file=sys.stderr, flush=True)
            trang_k = html(k)
            try:
                chup_canh(page, trang_k, so_khung[k], fps, thu_muc, khung_dau[k])
                da_ghi += so_khung[k]
                if thu_muc_su_kien is not None:
                    thu_muc_su_kien.mkdir(parents=True, exist_ok=True)
                    (thu_muc_su_kien / f"canh-{cac_du[k]['so']}.json").write_text(
                        json.dumps(doc_su_kien(page)), encoding="utf-8")
                cac_du[k]["nenTruoc"] = None  # nền data: của cảnh đã chụp xong không cần giữ nữa
                if k + 1 < cuoi and can_nen(k + 1):
                    cuoi_k = thu_muc / ten_khung(khung_dau[k] + so_khung[k] - 1)
                    cac_du[k + 1]["nenTruoc"] = _data_url(cuoi_k.read_bytes())
            except OSError as exc:
                raise GhiKhungLoi(str(exc)) from None
    return da_ghi


def _chup_dai_con(cong_viec: dict) -> int:
    """Vỏ cho tiến trình con: MediaError không gửi ngược qua pickle được nên đổi sang LoiBuocCon (giữ step)."""
    try:
        return chup_dai(cong_viec)
    except MediaError as exc:
        raise LoiBuocCon(exc.step, exc.message, exc.fix) from None


def _loi_dai(cac_du: list, dau: int, cuoi: int, exc: BaseException) -> MediaError:
    a, b = cac_du[dau]["so"], cac_du[cuoi - 1]["so"]
    canh = f"cảnh {a}" if a == b else f"cảnh {a}–{b}"
    if isinstance(exc, LoiBuocCon):
        return MediaError(exc.step, exc.message, exc.fix)
    if isinstance(exc, GhiKhungLoi):
        return MediaError("write", f"Không ghi được khung hình ở {canh}: {exc}", FIX_GHI)
    return MediaError("dung", f"Chụp khung lỗi ở {canh}: {type(exc).__name__}: {exc}", FIX_DUNG)


def chup_song_song(cac_du: list, models_js: dict, so_khung: list, fps: int, thu_muc_anh, so_tt: int,
                   thu_muc_su_kien=None, kho: Kho = KHO_CU) -> dict | None:
    """Chụp mọi cảnh. Có `thu_muc_su_kien` thì trả thêm {số cảnh: sự kiện âm thanh}, đọc trong cùng lượt chụp."""
    khung_dau = [0]
    for n in so_khung[:-1]:
        khung_dau.append(khung_dau[-1] + n)
    Path(thu_muc_anh).mkdir(parents=True, exist_ok=True)
    viec = []
    for a, b in chia_dai(so_khung, so_tt):
        # Mỗi tiến trình chỉ nhận cảnh của dải mình và cảnh ngay trước (nền lau bảng), không nhận cả video.
        lo = max(a - 1, 0)
        cac_so = {du["so"] for du in cac_du[lo:b]}
        viec.append({"cac_du": cac_du[lo:b], "models_js": {so: js for so, js in models_js.items() if so in cac_so},
                     "dau": a - lo, "cuoi": b - lo, "khung_dau": khung_dau[lo:b], "so_khung": list(so_khung[lo:b]),
                     "fps": fps, "thu_muc_anh": str(thu_muc_anh), "kho": [kho.ten, kho.do_phan_giai],
                     "thu_muc_su_kien": str(thu_muc_su_kien) if thu_muc_su_kien else None})
    if len(viec) == 1:
        try:
            chup_dai(viec[0])
        except MediaError:
            raise
        except Exception as exc:  # noqa: BLE001
            raise _loi_dai(viec[0]["cac_du"], viec[0]["dau"], viec[0]["cuoi"], exc) from exc
        return _doc_cac_su_kien(cac_du, thu_muc_su_kien)
    with ProcessPoolExecutor(max_workers=len(viec)) as pool:
        theo_tl = {pool.submit(_chup_dai_con, v): v for v in viec}
        xong, con_lai = wait(theo_tl, return_when=FIRST_EXCEPTION)
        if any(tl.exception() is not None for tl in xong):
            # Có dải hỏng: huỷ các dải chưa chạy; dải đang chạy vẫn được chờ xong trước khi dọn thư mục.
            for tl in con_lai:
                tl.cancel()
    # Báo lỗi của dải sớm nhất (theo thứ tự cảnh) để kết quả không phụ thuộc dải nào xong trước.
    for tl, v in theo_tl.items():
        if not tl.cancelled() and tl.exception() is not None:
            raise _loi_dai(v["cac_du"], v["dau"], v["cuoi"], tl.exception())
    return _doc_cac_su_kien(cac_du, thu_muc_su_kien)


def _doc_cac_su_kien(cac_du: list, thu_muc_su_kien) -> dict | None:
    if not thu_muc_su_kien:
        return None
    ket_qua = {}
    for du in cac_du:
        try:
            ds = json.loads((Path(thu_muc_su_kien) / f"canh-{du['so']}.json").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            ds = []  # Thiếu hay hỏng file sự kiện thì cảnh đó dựng không có hiệu ứng âm thanh, không làm hỏng video.
        ket_qua[du["so"]] = ds if isinstance(ds, list) else []
    return ket_qua

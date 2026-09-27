(function (root) {
  'use strict';

  // Vị trí bàn tay theo t: hàm thuần, chạy được trong Node. Trình duyệt cấp `ngoi(muc, p) -> {x, y}`.
  var LAU_BANG = 0.5; // mặc định khi thiếu tuy.giayLau (test Node); trang truyền du.giayLauBang từ Python
  var LUOT = 0.4;
  var NOI = 0.6;
  var CUOI = 0.2;

  function kep(x, a, b) { return x < a ? a : (x > b ? b : x); }
  function veDuoc(m) { return !m.dong && m.tay !== false && m.kieu !== 'anh'; }
  function ketThuc(m) { return m.batDau + m.thoiLuong; }
  function noi(a, b, u) { return { x: a.x + (b.x - a.x) * u, y: a.y + (b.y - a.y) * u }; }
  function but(d, hien) { return { x: d.x, y: d.y, hien: hien, kieu: 'but' }; }

  // Hai mục cùng bắt đầu: ưu tiên hình, rồi chữ, rồi nét (tay vẽ hình của cột trước, rồi viết tiếp chữ).
  // Nét trang trí máy quay bỏ qua (gạch chân, `quay: false`) nhường tay cho mục máy quay đang nhìn,
  // để tay không vẽ gạch chân ở mép khung trong khi máy quay phóng vào hình.
  var UU_TIEN = { hinh: 3, chu: 2, net: 1 };
  function hon(a, b) {
    if ((a.quay === false) !== (b.quay === false)) { return b.quay === false; }
    if (a.batDau !== b.batDau) { return a.batDau > b.batDau; }
    return (UU_TIEN[a.kieu] || 0) > (UU_TIEN[b.kieu] || 0);
  }
  // Mục đang vẽ (batDau <= t < kết thúc, như máy quay): mục máy quay nhìn được trước nét `quay: false`, rồi mục
  // bắt đầu muộn nhất; trùng thì theo UU_TIEN, rồi mục đứng trước.
  function dangVe(ds, t) {
    var chon = null;
    ds.forEach(function (m) {
      if (veDuoc(m) && t >= m.batDau && t < ketThuc(m) && (!chon || hon(m, chon))) { chon = m; }
    });
    return chon;
  }

  function viTri(ds, t, ngoi, nghi, tuy) {
    tuy = tuy || {};
    var lau = typeof tuy.giayLau === 'number' ? tuy.giayLau : LAU_BANG;
    // Chuyển cảnh (tuy.chuyen, hoặc tuy.lauBang kiểu cũ): chỉ lau bảng có tay cầm giẻ; kiểu khác tay ẩn tới hết chuyển cảnh.
    var chuyen = tuy.chuyen || (tuy.lauBang ? 'lau-bang' : null);
    if (chuyen && t >= 0 && t <= lau) {
      // Giẻ đi từ −120 với tốc độ (rộng khổ + 120) mỗi lượt lau, tới mép phải khi xong (khổ ngang: hệ số 1400);
      // cao hơn tâm vùng nội dung 70 (khổ ngang y 380).
      var k = root.THI_KHO.lay();
      return chuyen === 'lau-bang' ? { x: -120 + (k.rong + 120) * t / lau, y: k.tamY + 70, hien: true, kieu: 'gie' } : but(nghi, false);
    }
    var het = typeof tuy.gh === 'number' ? tuy.gh - CUOI : Infinity;
    if (t >= het) { return but(nghi, false); }
    var m = dangVe(ds, t);
    if (m) { return but(ngoi(m, (t - m.batDau) / m.thoiLuong), true); }
    var truoc = null;
    var sau = null;
    ds.forEach(function (x) {
      if (!veDuoc(x)) { return; }
      if (ketThuc(x) <= t && (!truoc || ketThuc(x) >= ketThuc(truoc))) { truoc = x; }
      if (x.batDau >= t && (!sau || x.batDau < sau.batDau)) { sau = x; }
    });
    var te = truoc ? ketThuc(truoc) : null;
    if (truoc && sau && sau.batDau - te <= NOI) {
      var khoang = sau.batDau - te;
      return but(noi(ngoi(truoc, 1), ngoi(sau, 0), khoang > 0 ? kep((t - te) / khoang, 0, 1) : 1), true);
    }
    var ra = truoc ? Math.min(LUOT, het - te) : 0;
    if (truoc && t < te + ra) { return but(noi(ngoi(truoc, 1), nghi, (t - te) / ra), true); }
    if (sau && sau.batDau < het) {
      var vao = Math.max(sau.batDau - LUOT, truoc ? te + ra : 0, chuyen ? lau : 0);
      if (t >= vao && vao < sau.batDau) { return but(noi(nghi, ngoi(sau, 0), (t - vao) / (sau.batDau - vao)), true); }
    }
    return but(nghi, false);
  }

  // Bàn tay nét đen tô da nhạt, vẽ bằng mã. Gốc toạ độ (0, 0) là ngòi bút (hoặc tâm giẻ); tay chìa xuống dưới phải.
  var NET = 'stroke="#1f2937" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"';
  var DA = 'fill="#f8d9bd" ' + NET;
  var AO = 'fill="#bfdbfe" ' + NET;
  var BUT =
    '<g class="but" transform="rotate(38)">' +
      '<path d="M0 0 L15 -6 L15 6 Z" fill="#1d4ed8" ' + NET + '/>' +
      '<rect x="15" y="-8" width="10" height="16" rx="2" fill="#e5e7eb" ' + NET + '/>' +
      '<rect x="25" y="-11" width="150" height="22" rx="5" fill="#2563eb" ' + NET + '/>' +
      '<path d="M150 -30 C 178 -46, 250 -44, 290 -34 L 420 -40 L 420 70 L 290 62 C 240 74, 176 70, 150 48 C 132 32, 130 -16, 150 -30 Z" ' + DA + '/>' +
      '<path d="M300 -38 L 420 -44 L 420 76 L 300 66 C 312 40, 312 -10, 300 -38 Z" ' + AO + '/>' +
      '<path d="M40 -14 C 38 -24, 60 -28, 92 -26 C 120 -25, 150 -30, 170 -30 L 176 -8 C 150 -8, 110 -10, 78 -10 C 58 -10, 42 -6, 40 -14 Z" ' + DA + '/>' +
      '<path d="M52 12 C 50 24, 74 30, 104 28 C 128 27, 146 30, 164 36 L 168 14 C 146 12, 120 10, 96 10 C 72 10, 54 4, 52 12 Z" ' + DA + '/>' +
      '<path d="M176 -8 C 190 -6, 200 4, 198 16" fill="none" ' + NET + '/>' +
      '<path d="M150 44 C 170 50, 196 50, 214 44" fill="none" ' + NET + '/>' +
    '</g>';
  var GIE =
    '<g class="gie">' +
      '<rect x="-34" y="-70" width="68" height="140" rx="10" fill="#9ca3af" ' + NET + '/>' +
      '<rect x="-34" y="-70" width="24" height="140" rx="8" fill="#4b5563" ' + NET + '/>' +
      '<path d="M18 -40 C 40 -64, 86 -60, 112 -40 L 250 40 L 210 120 L 80 60 C 40 50, 10 30, 12 0 C 12 -16, 12 -30, 18 -40 Z" ' + DA + '/>' +
      '<path d="M200 10 L 290 60 L 250 150 L 170 100 Z" ' + AO + '/>' +
      '<path d="M22 -22 C 34 -26, 48 -24, 58 -16 M20 0 C 34 -4, 48 -2, 58 6 M22 22 C 34 18, 48 20, 56 28" fill="none" ' + NET + '/>' +
    '</g>';
  var SVG =
    '<svg id="ban-tay" xmlns="http://www.w3.org/2000/svg" width="1" height="1" overflow="visible" style="display:none">' +
      BUT + GIE + '<circle id="ngoi-but" cx="0" cy="0" r="1" fill="none"/>' +
    '</svg>';

  var API = { LAU_BANG: LAU_BANG, SVG: SVG, hon: hon, dangVe: dangVe, viTri: viTri };
  // Chỗ nghỉ ngoài góc dưới phải của khổ hiện tại (khổ ngang: 1220, 760).
  Object.defineProperty(API, 'NGHI', {
    enumerable: true,
    get: function () { var k = root.THI_KHO.lay(); return { x: k.rong - 60, y: k.cao + 40 }; }
  });
  root.THI_BAN_TAY = API;
})(typeof globalThis !== 'undefined' ? globalThis : this);

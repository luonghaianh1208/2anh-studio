(function (root) {
  'use strict';

  // Kho 8 nền mẫu vẽ bằng mã (`nen: mau/<tên>` ở cảnh ke-chuyen): tranh phẳng, bảng màu dịu, không chữ, không ảnh,
  // không tham chiếu ngoài. Hàm thuần: ve(ten, kho, hat) trả chuỗi SVG kín khổ; mọi nét "ngẫu nhiên" lấy từ PRNG
  // có hạt giống (hạt = số cảnh). Quy tắc bố cục: vùng ô `noi-dung` giữ độ tương phản thấp (cảnh vật dồn ra mép,
  // lớp phủ trắng mờ ở giữa khi cần) để chữ và nhân vật nổi. Khổ dọc bố trí lại (trời cao, cảnh vật ở nửa dưới).
  var NS = 'http://www.w3.org/2000/svg';
  var TEN = ['giay', 'bau-troi', 'vu-tru', 'lop-hoc', 'phong-thi-nghiem', 'thanh-pho', 'dong-que', 'vong-tron'];
  var BANG = root.THI_O_BO_CUC || (typeof module === 'object' && module.exports ? require('./o-bo-cuc.json') : {});

  function prng(hat) { return root.THI_CAT_DAN.prng(hat); }
  function so(x) { return Math.round(x * 10) / 10; }
  function trongKhoang(r, a, b) { return a + (b - a) * r(); }
  function hop(x, y, w, h, mau, them) {
    return '<rect x="' + so(x) + '" y="' + so(y) + '" width="' + so(w) + '" height="' + so(h) + '" fill="' + mau + '"' + (them || '') + '/>';
  }
  function tron(cx, cy, r, mau, them) {
    return '<circle cx="' + so(cx) + '" cy="' + so(cy) + '" r="' + so(r) + '" fill="' + mau + '"' + (them || '') + '/>';
  }
  function duong(d, mau, them) { return '<path d="' + d + '" fill="' + mau + '"' + (them || '') + '/>'; }
  function diem(ds) { return ds.map(function (p) { return so(p[0]) + ',' + so(p[1]); }).join(' '); }
  function daGiac(ds, mau, them) { return '<polygon points="' + diem(ds) + '" fill="' + mau + '"' + (them || '') + '/>'; }
  // Chuyển sắc dọc: dung = [[vị trí 0..1, màu], ...].
  function sacDoc(id, dung) {
    return '<linearGradient id="' + id + '" x1="0" y1="0" x2="0" y2="1">' + dung.map(function (d) {
      return '<stop offset="' + d[0] + '" stop-color="' + d[1] + '"/>';
    }).join('') + '</linearGradient>';
  }
  function mo(kho, defs, than) {
    var R = kho.rong, H = kho.cao;
    return '<svg xmlns="' + NS + '" class="nen-mau" width="' + R + '" height="' + H + '" viewBox="0 0 ' + R + ' ' + H + '">' +
      '<defs>' + defs + '</defs>' + than + '</svg>';
  }
  function laDoc(kho) { return kho.cao > kho.rong; }
  // Ô `noi-dung` của khổ (bảng o-bo-cuc.json); khổ lạ thì lấy vùng giữa tương ứng.
  function oGiua(kho) {
    var b = BANG[kho.ten] && BANG[kho.ten]['noi-dung'];
    return b || { x: kho.rong * 0.05, y: kho.cao * 0.26, w: kho.rong * 0.9, h: kho.day - kho.cao * 0.26 };
  }
  // Lớp phủ trắng mờ trên ô noi-dung, mép tan dần (không thành khung cứng): độ đục `a` ở giữa.
  function phuGiua(kho, id, a) {
    var o = oGiua(kho);
    var g = '<radialGradient id="' + id + '" cx="0.5" cy="0.5" r="0.5">' +
      '<stop offset="0" stop-color="#fff" stop-opacity="' + a + '"/><stop offset="0.72" stop-color="#fff" stop-opacity="' + a + '"/>' +
      '<stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>';
    return { defs: g, than: hop(o.x - o.w * 0.12, o.y - o.h * 0.14, o.w * 1.24, o.h * 1.28, 'url(#' + id + ')') };
  }

  // ---- Mảnh dùng chung ----
  // Dải đồi mềm: mép trên y = goc + tổng hai sóng sin (pha theo PRNG), kín tới đáy khung.
  function doi(r, R, H, goc, bienDo, mau) {
    var p1 = r() * 6.28, p2 = r() * 6.28, k1 = trongKhoang(r, 1.2, 2.2), k2 = trongKhoang(r, 3, 5);
    var d = 'M0 ' + H;
    for (var x = 0; x <= R + 20; x += 20) {
      var u = x / R;
      d += ' L' + so(x) + ' ' + so(goc - bienDo * (0.65 * Math.sin(u * k1 * Math.PI + p1) + 0.35 * Math.sin(u * k2 * Math.PI + p2)));
    }
    return duong(d + ' L' + R + ' ' + H + ' Z', mau);
  }
  // Mây tròn: thân bo tròn và ba bướu, tỉ lệ s (rộng ≈ 150 s).
  function may(cx, cy, s, mau, a) {
    return '<g fill="' + mau + '" opacity="' + a + '">' + hop(cx - 75 * s, cy - 18 * s, 150 * s, 36 * s, mau, ' rx="' + so(18 * s) + '"') +
      tron(cx - 35 * s, cy - 16 * s, 28 * s, mau) + tron(cx + 5 * s, cy - 30 * s, 36 * s, mau) + tron(cx + 42 * s, cy - 12 * s, 24 * s, mau) + '</g>';
  }
  // Cây tròn: thân và tán tròn hai lớp.
  function cay(x, day, s, tan, than) {
    return hop(x - 4 * s, day - 34 * s, 8 * s, 34 * s, than) + tron(x, day - 50 * s, 26 * s, tan) +
      tron(x - 9 * s, day - 58 * s, 13 * s, 'rgba(255,255,255,0.18)');
  }
  // Cửa sổ lưới ô (khung sáng, kính xanh nhạt, vệt phản chiếu chéo).
  function cuaSo(x, y, w, h, cot, hang) {
    var s = hop(x - 8, y - 8, w + 16, h + 16, '#fbf4e4', ' rx="4"') + hop(x, y, w, h, '#bfe2f2');
    s += daGiac([[x + w * 0.15, y + h], [x + w * 0.45, y], [x + w * 0.62, y], [x + w * 0.32, y + h]], '#fff', ' opacity="0.35"');
    for (var i = 1; i < cot; i++) { s += hop(x + w * i / cot - 3, y, 6, h, '#fbf4e4'); }
    for (var j = 1; j < hang; j++) { s += hop(x, y + h * j / hang - 3, w, 6, '#fbf4e4'); }
    return s + hop(x - 14, y + h + 6, w + 28, 10, '#e6d3b3', ' rx="3"');
  }
  // Sao nhỏ rải trong hộp, độ sáng theo PRNG.
  function sao(r, n, x, y, w, h) {
    var s = '';
    for (var i = 0; i < n; i++) {
      s += tron(x + r() * w, y + r() * h, trongKhoang(r, 0.6, 1.9), '#fff', ' opacity="' + so(trongKhoang(r, 0.3, 0.95)) + '"');
    }
    return s;
  }

  // ---- Tám nền ----
  function giay(kho, hat) { return root.THI_CAT_DAN.nenGiay(hat, kho); }

  function bauTroi(kho, hat) {
    var r = prng(hat * 37 + 1), R = kho.rong, H = kho.cao, doc = laDoc(kho);
    var defs = sacDoc('nm-troi', [[0, '#86c5ec'], [0.55, '#c3e4f6'], [1, '#eaf6fb']]);
    var s = hop(0, 0, R, H, 'url(#nm-troi)');
    var mx = R * 0.84, my = H * (doc ? 0.09 : 0.15), mr = Math.min(R, H) * 0.075;
    s += tron(mx, my, mr * 2, '#fffbe6', ' opacity="0.35"') + tron(mx, my, mr, '#fff3c4');
    var n = doc ? 4 : 5;
    for (var i = 0; i < n; i++) {
      var cx = R * (i + 0.2 + 0.6 * r()) / n, cy = H * (doc ? trongKhoang(r, 0.06, 0.42) : trongKhoang(r, 0.08, 0.36));
      if (Math.abs(cx - mx) < mr * 2 + 80 && Math.abs(cy - my) < mr * 2 + 40) { cy = my + mr * 2 + 70; }  // không che mặt trời
      s += may(cx, cy, trongKhoang(r, 0.7, 1.25) * (doc ? 0.9 : 1), '#fff', so(trongKhoang(r, 0.8, 0.95)));
    }
    var nen = H * (doc ? 0.7 : 0.7);
    s += doi(r, R, H, nen, H * 0.04, '#bfe0c4') + doi(r, R, H, nen + H * 0.07, H * 0.035, '#a4d3a6');
    var truoc = nen + H * 0.15;
    s += doi(r, R, H, truoc, H * 0.03, '#8cc58e');
    [0.06, 0.13, 0.9, 0.96].forEach(function (u, k) { s += cay(R * u, truoc + H * 0.03, (doc ? 1.2 : 1) * (k % 2 ? 0.8 : 1), '#6fae72', '#9a7453'); });
    var p = phuGiua(kho, 'nm-phu-troi', 0.2);
    return mo(kho, defs + p.defs, s + p.than);
  }

  function vuTru(kho, hat) {
    var r = prng(hat * 41 + 2), R = kho.rong, H = kho.cao, doc = laDoc(kho);
    var defs = '<radialGradient id="nm-dem" cx="0.5" cy="0.4" r="0.75"><stop offset="0" stop-color="#2c4488"/>' +
      '<stop offset="0.6" stop-color="#1b2c66"/><stop offset="1" stop-color="#0f1a45"/></radialGradient>' +
      '<filter id="nm-mo" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="40"/></filter>';
    var s = hop(0, 0, R, H, 'url(#nm-dem)');
    s += tron(R * 0.2, H * 0.72, Math.min(R, H) * 0.3, '#5a4fb8', ' opacity="0.25" filter="url(#nm-mo)"') +
      tron(R * 0.8, H * 0.25, Math.min(R, H) * 0.28, '#2f7fb0', ' opacity="0.22" filter="url(#nm-mo)"');
    s += sao(r, Math.round(R * H / 6000), 0, 0, R, H);
    // Sao sáng có quầng.
    for (var i = 0; i < 9; i++) {
      var x = r() * R, y = r() * H, rr = trongKhoang(r, 2, 3.4);
      s += tron(x, y, rr * 3.2, '#ffe28a', ' opacity="0.2"') + tron(x, y, rr, '#ffe9a8');
    }
    // Hai chòm sao nét mảnh ở hai góc trên.
    [[0.04, 0.05], [doc ? 0.55 : 0.66, doc ? 0.12 : 0.06]].forEach(function (g) {
      var ds = [];
      for (var k = 0; k < 6; k++) { ds.push([R * (g[0] + 0.05 * k + 0.02 * r()), H * (g[1] + (doc ? 0.07 : 0.1) * r() + (k === 3 ? 0.05 : 0))]); }
      s += '<polyline points="' + diem(ds) + '" fill="none" stroke="#a9bfff" stroke-width="1.3" opacity="0.55"/>';
      ds.forEach(function (p) { s += tron(p[0], p[1], 2.6, '#e4ecff'); });
    });
    // Hành tinh có vành ở góc dưới phải, mặt trăng ở góc dưới trái.
    var px = R * (doc ? 0.8 : 0.9), py = H * (doc ? 0.88 : 0.8), pr = doc ? 90 : 72;
    defs += '<clipPath id="nm-hanh"><circle cx="' + so(px) + '" cy="' + so(py) + '" r="' + pr + '"/></clipPath>';
    s += '<g transform="rotate(-18 ' + so(px) + ' ' + so(py) + ')">' +
      '<ellipse cx="' + so(px) + '" cy="' + so(py) + '" rx="' + so(pr * 1.75) + '" ry="' + so(pr * 0.42) + '" fill="none" stroke="#f3d3a0" stroke-width="7" opacity="0.8"/>' +
      tron(px, py, pr, '#eea56a') + '<g clip-path="url(#nm-hanh)">' + hop(px - pr, py - pr * 0.35, pr * 2, pr * 0.22, '#dc8b56') +
      hop(px - pr, py + pr * 0.2, pr * 2, pr * 0.14, '#f5bf8a') + '</g>' +
      '<path d="M' + so(px - pr * 1.75) + ' ' + so(py) + ' A' + so(pr * 1.75) + ' ' + so(pr * 0.42) + ' 0 0 0 ' + so(px + pr * 1.75) + ' ' + so(py) +
      '" fill="none" stroke="#f3d3a0" stroke-width="7"/></g>';
    var mx = R * (doc ? 0.16 : 0.08), my = H * (doc ? 0.8 : 0.84), mr = doc ? 30 : 26;
    s += tron(mx, my, mr * 1.8, '#dfe6ff', ' opacity="0.12"') + tron(mx, my, mr, '#e6eaf5') +
      tron(mx - mr * 0.3, my - mr * 0.2, mr * 0.22, '#cbd2e6') + tron(mx + mr * 0.35, my + mr * 0.3, mr * 0.16, '#cbd2e6');
    return mo(kho, defs, s);
  }

  function lopHoc(kho) {
    var R = kho.rong, H = kho.cao, doc = laDoc(kho);
    var san = H * (doc ? 0.82 : 0.86), ghe = H * (doc ? 0.68 : 0.72);
    var s = hop(0, 0, R, H, '#f4e5c6') + hop(0, 0, R, H * 0.05, '#ead7b1');
    s += hop(0, ghe, R, san - ghe, '#e6cb9f') + hop(0, ghe, R, 6, '#d4b283') + hop(0, san - 10, R, 10, '#c49a6a');
    s += hop(0, san, R, H - san, '#cf9f70');
    for (var x = -40; x < R; x += 90) { s += hop(x, san, 3, H - san, '#bd8b5d'); }
    // Bảng xanh viền gỗ (bảng trống), khay phấn.
    var b = doc ? { x: 70, y: 290, w: 580, h: 400 } : { x: 250, y: 104, w: 780, h: 340 };
    s += hop(b.x - 16, b.y - 16, b.w + 32, b.h + 32, '#a9723f', ' rx="8"') + hop(b.x, b.y, b.w, b.h, '#7fa98c');
    s += '<ellipse cx="' + so(b.x + b.w * 0.3) + '" cy="' + so(b.y + b.h * 0.4) + '" rx="' + so(b.w * 0.18) + '" ry="' + so(b.h * 0.12) + '" fill="#fff" opacity="0.06"/>' +
      '<ellipse cx="' + so(b.x + b.w * 0.7) + '" cy="' + so(b.y + b.h * 0.65) + '" rx="' + so(b.w * 0.14) + '" ry="' + so(b.h * 0.1) + '" fill="#fff" opacity="0.05"/>';
    s += hop(b.x - 24, b.y + b.h + 14, b.w + 48, 12, '#8d5a2e', ' rx="3"') + hop(b.x + b.w * 0.72, b.y + b.h + 8, 26, 7, '#fbf7ee', ' rx="3"') +
      hop(b.x + b.w * 0.78, b.y + b.h + 8, 20, 7, '#f6d98a', ' rx="3"');
    // Đồng hồ treo tường (kim, không số).
    var dx = doc ? R / 2 : 1135, dy = doc ? 180 : 150;
    s += tron(dx, dy, 36, '#a9723f') + tron(dx, dy, 29, '#fffaf0') +
      '<path d="M' + dx + ' ' + dy + ' V' + (dy - 19) + ' M' + dx + ' ' + dy + ' H' + (dx + 13) + '" stroke="#5a4632" stroke-width="3" stroke-linecap="round"/>';
    // Cửa sổ (khổ ngang: bên trái bảng).
    if (!doc) { s += cuaSo(52, 120, 150, 250, 2, 3); }
    // Bàn phía trước, chồng sách, chậu cây.
    var ban = doc ? { x: 400, y: 990, w: 330 } : { x: 890, y: 575, w: 380 };
    s += hop(ban.x, ban.y, ban.w, 18, '#c48d58', ' rx="4"') + hop(ban.x + 14, ban.y + 18, ban.w - 28, H - ban.y, '#b07a47') +
      hop(ban.x + 34, ban.y + 38, ban.w * 0.34, 50, '#a26f3f', ' rx="4"') + hop(ban.x + 34 + ban.w * 0.34 * 0.42, ban.y + 58, 20, 6, '#e8c89a', ' rx="3"');
    var sx = ban.x + ban.w * 0.55;
    s += hop(sx, ban.y - 16, 90, 16, '#e07a5f', ' rx="2"') + hop(sx + 6, ban.y - 30, 80, 14, '#3d8fa6', ' rx="2"') +
      hop(sx + 2, ban.y - 42, 86, 12, '#f2c14e', ' rx="2"');
    var cx = doc ? 90 : 60, cy = san + (doc ? 10 : 6);
    s += daGiac([[cx - 26, cy - 50], [cx + 26, cy - 50], [cx + 20, cy], [cx - 20, cy]], '#d1805a');
    [[-26, -120, -30], [0, -135, 0], [26, -118, 30], [-14, -95, -50], [16, -96, 45]].forEach(function (l) {
      s += '<ellipse cx="' + (cx + l[0]) + '" cy="' + (cy + l[1] * 0.6 - 20) + '" rx="13" ry="34" fill="#6aa66e" transform="rotate(' + l[2] + ' ' + (cx + l[0]) + ' ' + (cy + l[1] * 0.6 - 20) + ')"/>';
    });
    var p = phuGiua(kho, 'nm-phu-lop', 0.25);
    return mo(kho, p.defs, s + p.than);
  }

  // Bình thí nghiệm: kieu 0 bình tam giác, 1 bình cầu, 2 cốc, 3 lọ có nắp; đáy ở (x, day), cao ≈ h.
  var THUY = '#f5fbff', VIEN = '#8fb0bf';
  function binh(kieu, x, day, h, mau) {
    var w = h * 0.7, n = h * 0.18, net = ' stroke="' + VIEN + '" stroke-width="2.5" stroke-linejoin="round"';
    if (kieu === 0) {
      return daGiac([[x - n / 2, day - h], [x + n / 2, day - h], [x + n / 2, day - h * 0.6], [x + w / 2, day], [x - w / 2, day], [x - n / 2, day - h * 0.6]], THUY, net) +
        daGiac([[x - w * 0.36, day - h * 0.28], [x + w * 0.36, day - h * 0.28], [x + w / 2 - 2, day - 2], [x - w / 2 + 2, day - 2]], mau);
    }
    if (kieu === 1) {
      var rr = h * 0.33;
      return hop(x - n / 2, day - h, n, h - rr * 1.6, THUY, net) + tron(x, day - rr, rr, THUY, net) +
        duong('M' + so(x - rr * 0.94) + ' ' + so(day - rr * 0.7) + ' A' + so(rr * 0.97) + ' ' + so(rr * 0.97) + ' 0 0 0 ' + so(x + rr * 0.94) + ' ' + so(day - rr * 0.7) + ' Z', mau);
    }
    if (kieu === 2) {
      return hop(x - w / 2, day - h * 0.7, w, h * 0.7, THUY, net + ' rx="4"') + hop(x - w / 2 + 3, day - h * 0.38, w - 6, h * 0.38 - 3, mau, ' rx="3"');
    }
    return hop(x - w * 0.35, day - h * 0.78, w * 0.7, h * 0.78, mau, ' rx="6"') + hop(x - w * 0.2, day - h, w * 0.4, h * 0.24, '#6d7f8a', ' rx="3"') +
      hop(x - w * 0.22, day - h * 0.55, w * 0.44, h * 0.22, '#fdfaf2', ' rx="2"');
  }
  function ke(x, y, w, cacBinh) {
    var s = hop(x, y, w, 12, '#c79b6b', ' rx="2"') + hop(x + 16, y + 12, 10, 18, '#a97f53') + hop(x + w - 26, y + 12, 10, 18, '#a97f53');
    cacBinh.forEach(function (b, k) { s += binh(b[0], x + w * (k + 0.5) / cacBinh.length, y, b[1], b[2]); });
    return s;
  }

  function phongThiNghiem(kho) {
    var R = kho.rong, H = kho.cao, doc = laDoc(kho);
    var mat = H * (doc ? 0.8 : 0.78);
    var defs = '<pattern id="nm-gach" width="48" height="32" patternUnits="userSpaceOnUse"><path d="M48 0H0V32" fill="none" stroke="#cfe4dc" stroke-width="2"/></pattern>';
    var s = hop(0, 0, R, H, '#e4f2ed') + hop(0, H * (doc ? 0.5 : 0.45), R, mat - H * (doc ? 0.5 : 0.45), 'url(#nm-gach)');
    var hong = '#f4a4a0', lam = '#8ccbf0', vang = '#ffd479', luc = '#9fd4a6', tim = '#c7aee9';
    if (doc) {
      s += ke(36, 170, 290, [[0, 80, hong], [1, 86, lam], [3, 70, vang]]) + ke(394, 170, 290, [[2, 70, luc], [0, 90, tim], [1, 76, vang]]);
      s += ke(36, 330, 290, [[3, 66, lam], [2, 62, hong]]) + ke(394, 330, 290, [[1, 72, luc], [3, 60, tim]]);
    } else {
      s += ke(40, 170, 330, [[0, 84, hong], [1, 90, lam], [3, 72, vang]]) + ke(40, 330, 330, [[2, 70, luc], [0, 78, tim], [1, 70, vang]]);
      s += ke(910, 170, 330, [[3, 70, luc], [0, 88, vang], [1, 84, hong]]) + ke(910, 330, 330, [[1, 74, tim], [2, 66, lam], [3, 64, hong]]);
    }
    // Bàn đá và tủ dưới.
    s += hop(-10, mat, R + 20, 24, '#8f9ba4', ' rx="4"') + hop(0, mat + 24, R, H - mat, '#b9c4ca');
    var cua = doc ? 3 : 5;
    for (var i = 0; i < cua; i++) {
      var cx = R * i / cua + 14, cw = R / cua - 28;
      s += hop(cx, mat + 44, cw, H - mat - 44, '#c7d0d5', ' rx="6"') + hop(cx + cw / 2 - 22, mat + 60, 44, 7, '#8f9ba4', ' rx="3"');
    }
    // Giá ống nghiệm và cốc trên bàn, ở hai mép.
    var gx = doc ? 60 : 70;
    s += hop(gx, mat - 26, 150, 26, '#c79b6b', ' rx="3"');
    [hong, lam, vang, luc, tim].forEach(function (m, k) {
      var tx = gx + 14 + k * 28;
      s += hop(tx, mat - 86, 16, 76, THUY, ' rx="8" stroke="' + VIEN + '" stroke-width="2"') + hop(tx + 2, mat - 46, 12, 34, m, ' rx="6"');
    });
    s += hop(gx - 6, mat - 40, 162, 10, '#b3875a', ' rx="3"');
    s += binh(0, R - (doc ? 110 : 150), mat, 96, lam) + binh(2, R - (doc ? 200 : 260), mat, 70, hong);
    var p = phuGiua(kho, 'nm-phu-tn', 0.25);
    return mo(kho, defs + p.defs, s + p.than);
  }

  function thanhPho(kho, hat) {
    var r = prng(hat * 43 + 5), R = kho.rong, H = kho.cao, doc = laDoc(kho);
    var dat = H * (doc ? 0.86 : 0.8);
    var defs = sacDoc('nm-pho', [[0, '#bfe1f3'], [0.7, '#e9f1ee'], [1, '#fbeedb']]);
    var s = hop(0, 0, R, H, 'url(#nm-pho)');
    s += may(R * 0.22, H * (doc ? 0.1 : 0.14), 0.9, '#fff', 0.8) + may(R * 0.74, H * (doc ? 0.2 : 0.1), 0.7, '#fff', 0.7);
    // Dãy nhà xa: khối nhạt cùng tông trời.
    for (var x = -20; x < R; ) {
      var w = trongKhoang(r, 50, 100), h = H * (doc ? trongKhoang(r, 0.2, 0.34) : trongKhoang(r, 0.25, 0.4));
      s += hop(x, dat - h, w + 1, h, '#cfdcea');
      x += w;
    }
    // Dãy nhà khối trước: cao ở hai mép, thấp ở giữa; cửa sổ lưới, cửa ra vào.
    var MAU = ['#f2b880', '#8fc1d4', '#eaa493', '#b9d18f', '#d6bde3', '#f3d68a'];
    var k = Math.floor(r() * MAU.length);
    for (var x2 = -10; x2 < R; k++) {
      var w2 = trongKhoang(r, doc ? 90 : 100, doc ? 140 : 170), giua = Math.abs((x2 + w2 / 2) / R - 0.5) * 2;
      var h2 = H * (doc ? 0.18 + 0.2 * giua : 0.2 + 0.32 * giua) * trongKhoang(r, 0.85, 1.1);
      var y2 = dat - h2, mau = MAU[k % MAU.length];
      s += hop(x2, y2, w2, h2, mau) + hop(x2 - 4, y2 - 8, w2 + 8, 10, 'rgba(0,0,0,0.12)');
      var cot = Math.max(2, Math.floor((w2 - 20) / 30)), hang = Math.max(1, Math.floor((h2 - 70) / 42));
      var cw = (w2 - 20) / cot;
      for (var i = 0; i < cot; i++) {
        for (var j = 0; j < hang; j++) {
          s += hop(x2 + 10 + i * cw + 4, y2 + 18 + j * 42, cw - 8, 24, r() < 0.25 ? '#ffe7a6' : '#fbf5e6', ' rx="2"');
        }
      }
      s += hop(x2 + w2 / 2 - 14, dat - 40, 28, 40, 'rgba(0,0,0,0.18)', ' rx="3"');
      x2 += w2 + trongKhoang(r, 4, 14);
    }
    // Vỉa hè, hàng cây, đường có vạch.
    s += hop(0, dat, R, 20, '#ddd3c4') + hop(0, dat + 20, R, 5, '#bfb4a4') + hop(0, dat + 25, R, H - dat - 25, '#848a92');
    var yv = dat + 25 + (H - dat - 25) / 2 - 3;
    for (var v = 20; v < R; v += 90) { s += hop(v, yv, 48, 6, '#f5f0e2', ' rx="3"'); }
    [0.08, 0.36, 0.64, 0.92].forEach(function (u) { s += cay(R * u, dat + 8, 0.8, '#7db77b', '#8d6b4d'); });
    var p = phuGiua(kho, 'nm-phu-pho', 0.25);
    return mo(kho, defs + p.defs, s + p.than);
  }

  function dongQue(kho, hat) {
    var r = prng(hat * 47 + 3), R = kho.rong, H = kho.cao, doc = laDoc(kho);
    var ngang = H * (doc ? 0.66 : 0.64);
    var defs = sacDoc('nm-que', [[0, '#9fd2ee'], [0.75, '#e4f1ea'], [1, '#fcefd4']]);
    var s = hop(0, 0, R, H, 'url(#nm-que)');
    var mx = R * (doc ? 0.74 : 0.8), my = H * (doc ? 0.14 : 0.2), mr = doc ? 54 : 46;
    s += tron(mx, my, mr * 2.3, '#fff2b8', ' opacity="0.3"') + tron(mx, my, mr * 1.55, '#ffe59a', ' opacity="0.4"') + tron(mx, my, mr, '#ffd166');
    s += may(R * 0.2, H * (doc ? 0.24 : 0.2), 0.8, '#fff', 0.85);
    // Núi xa hai lớp: đỉnh nhọn mềm theo PRNG.
    [['#b9cde0', 0.2], ['#a3bdd3', 0.12]].forEach(function (l) {
      var ds = [[0, ngang]], x = 0;
      while (x < R) {
        var w = trongKhoang(r, 120, 240);
        ds.push([x + w / 2, ngang - H * l[1] * trongKhoang(r, 0.5, 1)]);
        x += w;
        ds.push([x, ngang - H * l[1] * trongKhoang(r, 0.1, 0.3)]);
      }
      ds.push([R, ngang + 2], [0, ngang + 2]);
      s += daGiac(ds, l[0]);
    });
    s += doi(r, R, H, ngang, 6, '#9cc97c');
    // Đồng lúa sọc hội tụ về một điểm trên đường chân trời.
    var tx = R * 0.5, n = 16, chan = ngang + 8;
    s += hop(0, chan, R, H - chan, '#b8d97a');
    for (var i = 0; i < n; i += 2) {
      var a = -R + 3 * R * i / n, b = -R + 3 * R * (i + 1) / n;
      s += daGiac([[tx + (a - tx) * 0.08, chan], [tx + (b - tx) * 0.08, chan], [b, H], [a, H]], '#a6cd66');
    }
    s += hop(0, chan, R, (H - chan) * 0.25, '#e9f2cf', ' opacity="0.35"');
    // Hàng tre hai bên: đốt thân và lá thon.
    function tre(x0, day, cao, lat) {
      var t = '';
      for (var k = 0; k < 7; k++) {
        var x = x0 + k * 14 * lat, h = cao * trongKhoang(r, 0.75, 1), cong = (k - 3) * 6 * lat;
        t += '<path d="M' + so(x) + ' ' + so(day) + ' Q' + so(x + cong * 0.3) + ' ' + so(day - h * 0.6) + ' ' + so(x + cong) + ' ' + so(day - h) +
          '" stroke="#6c9e57" stroke-width="8" fill="none" stroke-linecap="round"/>';
        for (var m = 1; m < 5; m++) {
          var y = day - h * m / 5, xx = x + cong * m / 5 * 0.7, goc = (r() < 0.5 ? -1 : 1) * trongKhoang(r, 30, 70);
          t += '<ellipse cx="' + so(xx) + '" cy="' + so(y) + '" rx="24" ry="6" fill="' + (m % 2 ? '#7fb766' : '#6aa653') +
            '" transform="rotate(' + so(goc) + ' ' + so(xx) + ' ' + so(y) + ') translate(18 0)"/>';
        }
      }
      return t;
    }
    var caoTre = H * (doc ? 0.3 : 0.42);
    s += tre(R * 0.02, chan + 4, caoTre, 1) + tre(R * 0.98, chan + 4, caoTre, -1);
    var p = phuGiua(kho, 'nm-phu-que', 0.2);
    return mo(kho, defs + p.defs, s + p.than);
  }

  function vongTron(kho, hat) {
    var r = prng(hat * 53 + 11), R = kho.rong, H = kho.cao, doc = laDoc(kho);
    var defs = sacDoc('nm-kem', [[0, '#fdf1dc'], [0.6, '#fbe6c8'], [1, '#f7d9c4']]);
    var s = hop(0, 0, R, H, 'url(#nm-kem)');
    var MAU = ['#c6a3de', '#f4978e', '#8ecbe6', '#f5c26b', '#98d3b6'];
    // Chấm tròn nhạt rải khắp.
    for (var i = 0; i < 9; i++) {
      s += tron(r() * R, r() * H, trongKhoang(r, 10, 22), MAU[i % MAU.length], ' opacity="0.45"');
    }
    // Vòng tròn viền dày quanh mép, tránh vùng giữa: đặt trên một elip gần viền khung.
    var n = doc ? 7 : 8, lech = r() * 6.28, k0 = Math.floor(r() * MAU.length);
    for (var j = 0; j < n; j++) {
      var goc = lech + 6.28 * j / n + trongKhoang(r, -0.2, 0.2);
      var cx = R / 2 + Math.cos(goc) * R * 0.5 * trongKhoang(r, 0.85, 1.02);
      var cy = H / 2 + Math.sin(goc) * H * 0.5 * trongKhoang(r, 0.85, 1.02);
      var rr = Math.min(R, H) * trongKhoang(r, 0.09, 0.16);
      s += '<ellipse cx="' + so(cx) + '" cy="' + so(cy) + '" rx="' + so(rr) + '" ry="' + so(rr * trongKhoang(r, 0.8, 1)) +
        '" fill="none" stroke="' + MAU[(k0 + j) % MAU.length] + '" stroke-width="' + so(rr * 0.22) + '" transform="rotate(' + so(r() * 60 - 30) + ' ' + so(cx) + ' ' + so(cy) + ')"/>';
    }
    // Đồi hồng mềm ở đáy và lá xanh đậm ở hai góc dưới.
    s += doi(r, R, H, H * (doc ? 0.9 : 0.88), H * 0.025, '#f2c9c6') + doi(r, R, H, H * (doc ? 0.94 : 0.94), H * 0.02, '#e9b3c2');
    function la(x, y, dai, goc, mau) {
      return '<path d="M0 0 Q' + so(dai * 0.5) + ' ' + so(-dai * 0.28) + ' ' + dai + ' 0 Q' + so(dai * 0.5) + ' ' + so(dai * 0.28) + ' 0 0 Z" fill="' + mau +
        '" transform="translate(' + so(x) + ' ' + so(y) + ') rotate(' + goc + ')"/>';
    }
    var d = doc ? 1.2 : 1;
    s += la(-10, H + 10, 150 * d, -60, '#2f6f6a') + la(-10, H + 10, 130 * d, -30, '#3f8a7f') + la(-10, H - 20, 110 * d, -5, '#2f6f6a');
    s += la(R + 10, H + 10, 150 * d, -120, '#2f6f6a') + la(R + 10, H + 10, 130 * d, -150, '#3f8a7f') + la(R + 10, H - 20, 110 * d, 175, '#2f6f6a');
    return mo(kho, defs, s);
  }

  var VE = {
    'giay': giay, 'bau-troi': bauTroi, 'vu-tru': vuTru, 'lop-hoc': lopHoc,
    'phong-thi-nghiem': phongThiNghiem, 'thanh-pho': thanhPho, 'dong-que': dongQue, 'vong-tron': vongTron
  };

  function ve(ten, kho, hat) {
    var f = Object.prototype.hasOwnProperty.call(VE, ten) ? VE[ten] : null;
    if (!f) { throw new Error('Nền mẫu `' + ten + '` không có; các tên: ' + TEN.join(', ') + '.'); }
    return f(kho, (hat | 0) || 1);
  }

  root.THI_NEN_MAU = { TEN: TEN, ve: ve };
})(typeof globalThis !== 'undefined' ? globalThis : this);

(function (root) {
  'use strict';

  // Người que dẫn chuyện (spec Q8, Q9). `dang(tuThe, t)` là hàm thuần: toạ độ khớp và nét mặt tại t (giây trong cảnh),
  // chạy được trong Node. Hệ toạ độ riêng của nhân vật: gốc giữa hai bàn chân, y âm hướng lên, cao 300 đơn vị; +x là
  // phía nội dung (T: bên xa nội dung, P: bên gần nội dung). Trang lật ngang khi nội dung nằm bên trái nhân vật.
  // `ve(dang, mauAo, tuy)` trả chuỗi SVG; `tao`/`dat` (chỉ trang gọi) đặt nhân vật vào lớp vẽ theo t.
  var NS = 'http://www.w3.org/2000/svg';
  var TU_THE = ['dung', 'chao', 'chi-tay', 'giai-thich', 'suy-nghi', 'ngac-nhien', 'vo-dau', 'dung-lai', 'an-mung', 'buon'];
  // Tám màu áo (khoá đầu `mau-ao`; Python chỉ kiểm tên).
  var MAU_AO = {
    vang: '#f5c518', 'do': '#e04b3c', 'xanh-duong': '#3f7fd9', 'xanh-la': '#3fae5a',
    cam: '#f28c28', tim: '#8e5bd0', hong: '#ef7fb0', xam: '#9aa0a6'
  };
  var MUC = '#1b1b1b';
  var GIAY = '#3b3b3b';
  var MIENG_TRONG = '#7a2230';
  var CANH_TREN = 46;  // cánh tay trên
  var CANH_DUOI = 44;  // cẳng tay
  var CU_CHI = 1.2;    // cử chỉ trong 1,2 s đầu cảnh
  var CHU_KY_THO = 2.4;
  var BIEN_THO = 4.5;  // 1,5 % chiều cao 300 (spec Q9)
  var CHOP = 0.12;
  var HIEN_TU = 0.2, HIEN_DAI = 0.4;

  function p(x, y) { return { x: x, y: y }; }
  // Khung chung: hông, cổ, vai, đầu (tâm, bán kính), gối và bàn chân.
  var GOC = {
    hong: p(0, -120), co: p(0, -172), vaiT: p(-24, -164), vaiP: p(24, -164), dau: { x: 0, y: -222, r: 50 },
    goiT: p(-14, -60), goiP: p(14, -60), chanT: p(-24, 0), chanP: p(24, 0)
  };
  var TAY_BUONG = { tayT: p(-40, -76), congT: 1, tayP: p(40, -76), congP: -1 };
  var TAY_HONG = { tayT: p(-22, -116), congT: 1 };
  // Tư thế: đích của bàn tay (`tay*`) và hướng gập khuỷu (`cong*` = ±1), kiểu bàn tay (`nam` nắm, `mo` xoè, `chan`
  // lòng bàn tay dựng lên ra hiệu dừng), phần khung khác GOC, nét mặt, vật đi kèm (`vatDung`). `vao`: cách vào tư thế trong 1,2 s đầu (`bat` easeOutBack; `duoi` duỗi dần; `ngay` có
  // sẵn từ đầu, cử chỉ riêng của tư thế chạy trên đó).
  function tuThe(ten) {
    var a = {
      dung: { mat: ['tron', 'cuoi', 'ngang'], nhin: p(0.3, 0) },
      chao: { tayP: p(72, -236), congP: 1, banP: 'mo', vao: 'ngay', mat: ['cuoi', 'mo', 'nhuong'], nhin: p(0.3, 0) },
      'chi-tay': { tayP: p(112, -178), congP: 1, tayT: TAY_HONG.tayT, congT: 1, vao: 'duoi', mat: ['tron', 'cuoi', 'ngang'], nhin: p(1, 0) },
      'giai-thich': { tayP: p(96, -136), congP: 1, banP: 'mo', mat: ['tron', 'mo', 'ngang'], nhin: p(1, 0) },
      // Suy nghĩ: đầu thấp 10 để cằm vừa tầm cẳng tay; khuỷu tay P ở bụng, tay P chống cằm, tay T vắt ngang bụng
      // đỡ khuỷu; bóng nghĩ ba vòng tròn trên đầu (vatDung).
      'suy-nghi': { tayP: p(-4, -160), congP: -1, tayT: p(12, -128), congT: 1, vatDung: 'nghi',
        khung: { dau: { x: 2, y: -212, r: 50 } }, mat: ['tron', 'ngang', 'nhuong'], nhin: p(0.6, -1) },
      'ngac-nhien': { tayT: p(-80, -202), congT: -1, tayP: p(80, -202), congP: 1, banT: 'mo', banP: 'mo',
        khung: { chanT: p(-30, 0), chanP: p(30, 0), goiT: p(-18, -60), goiP: p(18, -60), dau: { x: -3, y: -224, r: 50 } },
        mat: ['to', 'o', 'nhuong'], nhin: p(0, 0) },
      'vo-dau': { tayT: p(-50, -228), congT: -1, tayP: p(50, -228), congP: 1, vao: 'ngay', vatDung: 'mo-hoi',
        khung: { goiT: p(-8, -60), goiP: p(8, -60), chanT: p(-28, 0), chanP: p(28, 0) },
        mat: ['xoay', 'meo', 'chau'], nhin: p(0, 0) },
      'dung-lai': { tayP: p(90, -188), congP: 1, banP: 'chan', tayT: TAY_HONG.tayT, congT: 1,
        khung: { chanT: p(-30, 0), chanP: p(30, 0), goiT: p(-18, -60), goiP: p(18, -60) },
        mat: ['tron', 'ngang', 'chau'], nhin: p(1, 0) },
      'an-mung': { tayT: p(-66, -250), congT: -1, tayP: p(66, -250), congP: 1, vao: 'ngay',
        khung: { chanT: p(-34, 0), chanP: p(34, 0), goiT: p(-22, -60), goiP: p(22, -60) },
        mat: ['cuoi', 'mo', 'nhuong'], nhin: p(0, 0) },
      buon: { tayT: p(-30, -80), congT: 1, tayP: p(30, -80), congP: -1, vatDung: 'nuoc-mat',
        khung: { co: p(2, -166), vaiT: p(-22, -158), vaiP: p(22, -158), dau: { x: 8, y: -212, r: 50 } },
        mat: ['tron', 'meo', 'chau'], nhin: p(0.3, 1) }
    }[ten];
    if (!a) { throw new Error('Tư thế `' + ten + '` không có; chọn một trong: ' + TU_THE.join(', ') + '.'); }
    return a;
  }

  function kep01(x) { return x < 0 ? 0 : (x > 1 ? 1 : x); }
  function lam(x) { return Math.round(x * 1000) / 1000 + 0; }
  function tron(q) { return q.r === undefined ? p(lam(q.x), lam(q.y)) : { x: lam(q.x), y: lam(q.y), r: q.r }; }
  function noi(a, b, u) {
    var q = p(a.x + (b.x - a.x) * u, a.y + (b.y - a.y) * u);
    if (a.r !== undefined) { q.r = a.r; }
    return q;
  }
  function xoay(q, tam, doGoc) {
    var g = doGoc * Math.PI / 180, c = Math.cos(g), s = Math.sin(g);
    var dx = q.x - tam.x, dy = q.y - tam.y;
    return p(tam.x + dx * c - dy * s, tam.y + dx * s + dy * c);
  }
  // Hai đoạn xương (vai → khuỷu → tay) với độ dài cố định: khuỷu gập về phía `cong` (±1); đích ngoài tầm với thì
  // tay duỗi thẳng về phía đích.
  function ik(vai, dich, cong) {
    var a = CANH_TREN, b = CANH_DUOI;
    var dx = dich.x - vai.x, dy = dich.y - vai.y;
    var d = Math.min(Math.max(Math.sqrt(dx * dx + dy * dy), Math.abs(a - b) + 1), a + b - 0.01);
    var th = Math.atan2(dy, dx);
    var al = Math.acos((a * a + d * d - b * b) / (2 * a * d));
    var khuyu = p(vai.x + a * Math.cos(th + cong * al), vai.y + a * Math.sin(th + cong * al));
    var ex = dich.x - khuyu.x, ey = dich.y - khuyu.y;
    var dd = Math.sqrt(ex * ex + ey * ey) || 1;
    // Đích trong tầm với: tay đúng đích; đích bị kẹp: tay cách khuỷu đúng b trên đường khuỷu → đích.
    var k = Math.min(1, b / dd);
    return { khuyu: khuyu, tay: p(khuyu.x + ex * k, khuyu.y + ey * k) };
  }

  // Các mốc chớp mắt trước `den` giây: 1,3 + 3,1k + 0,4·((7k) mod 3).
  function mocChop(den) {
    var ds = [];
    for (var k = 0; ; k++) {
      var m = 1.3 + 3.1 * k + 0.4 * ((k * 7) % 3);
      if (m >= den) { return ds; }
      ds.push(m);
    }
  }
  function dangChop(t) {
    if (t < 1.3) { return false; }
    var k = Math.max(0, Math.floor((t - 1.3) / 3.1) - 1);
    for (var i = k; i <= k + 2; i++) {
      var m = 1.3 + 3.1 * i + 0.4 * ((i * 7) % 3);
      if (t >= m && t < m + CHOP) { return true; }
    }
    return false;
  }

  function dang(ten, t) {
    var a = tuThe(ten);
    var D = root.THI_DONG;
    var vao = a.vao || 'bat';
    var u = vao === 'ngay' ? 1 : (vao === 'duoi' ? D.easeInOut(t / CU_CHI) : D.easeOutBack(t / CU_CHI));
    var khung = {};
    Object.keys(GOC).forEach(function (ma) {
      var dich = (a.khung && a.khung[ma]) || GOC[ma];
      khung[ma] = noi(GOC[ma], dich, u);
    });
    var tayT = noi(TAY_BUONG.tayT, a.tayT || TAY_BUONG.tayT, u);
    var tayP = noi(TAY_BUONG.tayP, a.tayP || TAY_BUONG.tayP, u);
    var T = ik(khung.vaiT, tayT, a.congT || TAY_BUONG.congT);
    var P = ik(khung.vaiP, tayP, a.congP || TAY_BUONG.congP);
    var trong = t >= 0 && t < CU_CHI;
    if (ten === 'chao' && trong) {
      // Vẫy tay phải ±25° quanh khuỷu, ba lần.
      P.tay = xoay(P.tay, P.khuyu, 25 * Math.sin(2 * Math.PI * 3 * t / CU_CHI));
    }
    if (ten === 'vo-dau' && trong) {
      // Hai tay rung ±6° quanh vai (bốn lần), ngược chiều nhau.
      var g = 6 * Math.sin(2 * Math.PI * 4 * t / CU_CHI);
      T = { khuyu: xoay(T.khuyu, khung.vaiT, g), tay: xoay(T.tay, khung.vaiT, g) };
      P = { khuyu: xoay(P.khuyu, khung.vaiP, -g), tay: xoay(P.tay, khung.vaiP, -g) };
    }
    // Nhún thở: mọi khớp trên hông dịch 4,5·sin(2πt/2,4); ăn mừng bật nhảy 12 hai lần trong 1,2 s đầu.
    var tho = BIEN_THO * Math.sin(2 * Math.PI * t / CHU_KY_THO);
    var nhay = ten === 'an-mung' && trong ? -12 * Math.abs(Math.sin(2 * Math.PI * t / CU_CHI)) : 0;
    function tren(q) { var r = p(q.x, q.y + tho + nhay); if (q.r !== undefined) { r.r = q.r; } return tron(r); }
    function duoi(q) { return tron(p(q.x, q.y + nhay)); }
    var khop = {
      dau: tren(khung.dau), co: tren(khung.co), vaiT: tren(khung.vaiT), vaiP: tren(khung.vaiP),
      khuyuT: tren(T.khuyu), khuyuP: tren(P.khuyu), tayT: tren(T.tay), tayP: tren(P.tay),
      hong: duoi(khung.hong), goiT: duoi(khung.goiT), goiP: duoi(khung.goiP), chanT: duoi(khung.chanT), chanP: duoi(khung.chanP)
    };
    var mat = a.mat[0];
    if (mat !== 'xoay' && dangChop(t)) { mat = 'nham'; }
    return {
      khop: khop,
      mat: { mat: mat, mieng: a.mat[1], may: a.mat[2], nhin: p(a.nhin.x, a.nhin.y) },
      tay: { T: a.banT || 'nam', P: a.banP || 'nam' },
      vatDung: a.vatDung || null
    };
  }

  // Bật vào: phóng 0,6 → 1 theo easeOutBack trong 0,4 s từ 0,2 s; hiện rõ trong phần tư đầu.
  function hien(t) {
    var q = kep01((t - HIEN_TU) / HIEN_DAI);
    return { k: lam(0.6 + 0.4 * root.THI_DONG.easeOutBack(q)), a: q > 0 ? Math.min(1, lam(q * 4)) : 0 };
  }

  // ---- Vẽ SVG ----
  function so(x) { return String(Math.round(x * 10) / 10); }
  function diem(q) { return so(q.x) + ' ' + so(q.y); }
  // `vien` > 0: bản viền (sticker cat-dan) — cùng hình, mọi nét và nền trắng, nét dày thêm `vien`.
  function butVe(vien) {
    return function (net, day, nen) {
      if (vien) { return ' fill="' + (nen && nen !== 'none' ? '#fff' : 'none') + '" stroke="#fff" stroke-width="' + so(day + vien) + '"'; }
      return ' fill="' + (nen || 'none') + '" stroke="' + net + '" stroke-width="' + so(day) + '"';
    };
  }
  function huong(a, b) {
    var dx = b.x - a.x, dy = b.y - a.y, d = Math.sqrt(dx * dx + dy * dy) || 1;
    return p(dx / d, dy / d);
  }
  function banTay(q, khuyu, kieu, but, vien) {
    var s = '<circle cx="' + so(q.x) + '" cy="' + so(q.y) + '" r="' + (kieu === 'chan' ? 11 : 9) + '"' + but(MUC, vien ? 0 : 0.01, MUC) + '/>';
    if (kieu !== 'mo' && kieu !== 'chan') { return s; }
    // Bàn tay xoè: bốn ngón toả quanh hướng cẳng tay (`mo`), hoặc dựng thẳng lên như ra hiệu dừng (`chan`).
    var h = huong(khuyu, q);
    var goc0 = kieu === 'chan' ? -Math.PI / 2 : Math.atan2(h.y, h.x);
    [-0.75, -0.25, 0.25, 0.75].forEach(function (lech) {
      var g = goc0 + lech;
      var a = p(q.x + 6 * Math.cos(g), q.y + 6 * Math.sin(g));
      var dai = kieu === 'chan' ? 18 : 15;
      var b = p(q.x + dai * Math.cos(g), q.y + dai * Math.sin(g));
      s += '<path d="M' + diem(a) + ' L' + diem(b) + '"' + but(MUC, 4.5) + '/>';
    });
    return s;
  }
  function xoan(cx, cy) {
    var d = '';
    for (var i = 0; i <= 40; i++) {
      var g = i / 40 * 5 * Math.PI;
      var r = 1 + 8 * i / 40;
      d += (i ? ' L' : 'M') + so(cx + r * Math.cos(g)) + ' ' + so(cy + r * Math.sin(g));
    }
    return d;
  }
  function ve(d, mauAo, tuy) {
    var ao = MAU_AO[mauAo];
    if (!ao) { throw new Error('Màu áo `' + mauAo + '` không có; chọn một trong: ' + Object.keys(MAU_AO).join(', ') + '.'); }
    var vien = (tuy && tuy.vien) || 0;
    var but = butVe(vien);
    var k = d.khop;
    var s = '<g class="nguoi-que" stroke-linecap="round" stroke-linejoin="round">';
    // Chân: từ hai bên hông xuống gối, bàn chân; giày elip xám đậm chìa ra ngoài.
    [['T', -1], ['P', 1]].forEach(function (c) {
      var goi = k['goi' + c[0]], chan = k['chan' + c[0]];
      s += '<path class="chan" d="M' + diem(p(k.hong.x + 9 * c[1], k.hong.y)) + ' L' + diem(goi) + ' L' + diem(chan) + '"' + but(MUC, 7) + '/>';
    });
    [['T', -1], ['P', 1]].forEach(function (c) {
      var chan = k['chan' + c[0]];
      s += '<ellipse class="giay" cx="' + so(chan.x + 6 * c[1]) + '" cy="' + so(chan.y - 7) + '" rx="16" ry="8"' + but(MUC, 3, GIAY) + '/>';
    });
    // Áo: hình thang tròn góc từ vai xuống hông; tay áo ngắn trùm gốc cánh tay (viền trước, nền sau thân áo).
    var tl = p(k.vaiT.x - 6, k.vaiT.y - 5), tr = p(k.vaiP.x + 6, k.vaiP.y - 5);
    var bl = p(k.hong.x - 25, k.hong.y + 6), br = p(k.hong.x + 25, k.hong.y + 6);
    function gan(a, b, r) { var h = huong(a, b); return p(a.x + h.x * r, a.y + h.y * r); }
    var r = 7;
    var than = 'M' + diem(gan(tl, tr, r)) + ' L' + diem(gan(tr, tl, r)) + ' Q' + diem(tr) + ' ' + diem(gan(tr, br, r)) +
      ' L' + diem(gan(br, tr, r)) + ' Q' + diem(br) + ' ' + diem(gan(br, bl, r)) + ' L' + diem(gan(bl, br, r)) +
      ' Q' + diem(bl) + ' ' + diem(gan(bl, tl, r)) + ' L' + diem(gan(tl, bl, r)) + ' Q' + diem(tl) + ' ' + diem(gan(tl, tr, r)) + ' Z';
    var tayAo = ['T', 'P'].map(function (c) {
      var vai = k['vai' + c], h = huong(vai, k['khuyu' + c]);
      return { dau: vai, cuoi: p(vai.x + h.x * 14, vai.y + h.y * 14) };
    });
    tayAo.forEach(function (ta) { s += '<path class="tay-ao-vien" d="M' + diem(ta.dau) + ' L' + diem(ta.cuoi) + '"' + but(MUC, 24) + '/>'; });
    s += '<path class="ao" d="' + than + '"' + but(MUC, 4, ao) + '/>';
    if (!vien) {
      tayAo.forEach(function (ta) { s += '<path class="tay-ao" d="M' + diem(ta.dau) + ' L' + diem(ta.cuoi) + '"' + but(ao, 16) + '/>'; });
    }
    // Tay: từ mép tay áo tới khuỷu, bàn tay.
    ['T', 'P'].forEach(function (c, i) {
      s += '<path class="tay" d="M' + diem(tayAo[i].cuoi) + ' L' + diem(k['khuyu' + c]) + ' L' + diem(k['tay' + c]) + '"' + but(MUC, 7) + '/>';
    });
    // Đầu tròn trắng viền đen 4; mặt lệch về phía nội dung. Bàn tay vẽ sau đầu (chống cằm, ôm đầu).
    var dau = k.dau;
    s += '<circle class="dau" cx="' + so(dau.x) + '" cy="' + so(dau.y) + '" r="' + dau.r + '" fill="#fff" stroke="' + (vien ? '#fff' : MUC) +
      '" stroke-width="' + so(4 + vien) + '"/>';
    if (!vien) { s += mat(d.mat, dau); }
    ['T', 'P'].forEach(function (c) { s += banTay(k['tay' + c], k['khuyu' + c], d.tay ? d.tay[c] : 'nam', but, vien); });
    return s + vatDung(d.vatDung, dau, but, vien) + '</g>';
  }
  // Vật đi kèm tư thế, theo đầu: bóng nghĩ (`nghi`), giọt mồ hôi (`mo-hoi`), giọt nước mắt (`nuoc-mat`).
  var MAU_NUOC = '#5aa9e6';
  function giot(x, y, c) {
    return 'M' + so(x) + ' ' + so(y - 1.6 * c) + ' Q' + so(x + c) + ' ' + so(y - 0.2 * c) + ' ' + so(x + c * 0.8) + ' ' + so(y + 0.4 * c) +
      ' A' + so(c * 0.8) + ' ' + so(c * 0.8) + ' 0 1 1 ' + so(x - c * 0.8) + ' ' + so(y + 0.4 * c) +
      ' Q' + so(x - c) + ' ' + so(y - 0.2 * c) + ' ' + so(x) + ' ' + so(y - 1.6 * c) + ' Z';
  }
  function vatDung(ten, dau, but, vien) {
    if (ten === 'nghi') {
      return [[30, -56, 4], [44, -70, 6.5], [64, -80, 9.5]].map(function (v) {
        return '<circle class="vat-dung" cx="' + so(dau.x + v[0]) + '" cy="' + so(dau.y + v[1]) + '" r="' + v[2] + '"' + but(MUC, 3, '#fff') + '/>';
      }).join('');
    }
    if (ten === 'mo-hoi') {
      return [[-60, -30, 7], [62, -44, 6]].map(function (v) {
        return '<path class="vat-dung" d="' + giot(dau.x + v[0], dau.y + v[1], v[2]) + '"' + but(MUC, 2.5, MAU_NUOC) + '/>';
      }).join('');
    }
    if (ten === 'nuoc-mat' && !vien) {
      return '<path class="vat-dung" d="' + giot(dau.x + 7 - 17, dau.y + 14, 5) + '"' + but(MUC, 2, MAU_NUOC) + '/>';
    }
    return '';
  }
  function mat(m, dau) {
    var but = butVe(0);
    var fx = dau.x + 7, nx = m.nhin ? m.nhin.x * 4 : 0, ny = m.nhin ? m.nhin.y * 4 : 0;
    var s = '';
    [-1, 1].forEach(function (b) {
      var x = fx + 17 * b, y = dau.y - 4;
      if (m.mat === 'tron') {
        s += '<ellipse cx="' + so(x + nx) + '" cy="' + so(y + ny) + '" rx="6" ry="8" fill="' + MUC + '"/>' +
          '<circle cx="' + so(x + nx - 2) + '" cy="' + so(y + ny - 3) + '" r="2" fill="#fff"/>';
      } else if (m.mat === 'to') {
        s += '<circle cx="' + so(x) + '" cy="' + so(y - 2) + '" r="11"' + but(MUC, 3, '#fff') + '/>' +
          '<circle cx="' + so(x + nx) + '" cy="' + so(y - 2 + ny) + '" r="4.5" fill="' + MUC + '"/>';
      } else if (m.mat === 'cuoi') {
        s += '<path d="M' + so(x - 7) + ' ' + so(y + 3) + ' Q' + so(x) + ' ' + so(y - 9) + ' ' + so(x + 7) + ' ' + so(y + 3) + '"' + but(MUC, 4) + '/>';
      } else if (m.mat === 'nham') {
        s += '<path d="M' + so(x - 7) + ' ' + so(y) + ' Q' + so(x) + ' ' + so(y + 5) + ' ' + so(x + 7) + ' ' + so(y) + '"' + but(MUC, 4) + '/>';
      } else {
        s += '<path d="' + xoan(x, y) + '"' + but(MUC, 2.5) + '/>';
      }
      // Mày: `ngang` thẳng, `nhuong` cong cao, `chau` nghiêng (xem dưới).
      var my = dau.y - 24;
      if (m.may === 'ngang') {
        s += '<path d="M' + so(x - 7) + ' ' + so(my) + ' L' + so(x + 7) + ' ' + so(my) + '"' + but(MUC, 3.5) + '/>';
      } else if (m.may === 'nhuong') {
        s += '<path d="M' + so(x - 8) + ' ' + so(my - 3) + ' Q' + so(x) + ' ' + so(my - 11) + ' ' + so(x + 8) + ' ' + so(my - 3) + '"' + but(MUC, 3.5) + '/>';
      } else {
        // `chau`: mày cau, đầu trong hạ (nghiêm, ra hiệu dừng); đi cùng miệng méo (buồn, rối) thì đầu trong nhướng.
        var buon = m.mieng === 'meo' ? 1 : -1;
        s += '<path d="M' + so(x - 8 * b) + ' ' + so(my - 5 * buon) + ' L' + so(x + 7 * b) + ' ' + so(my + 2 * buon) + '"' + but(MUC, 3.5) + '/>';
      }
    });
    var mx = fx, my2 = dau.y + 24;
    var ds = {
      cuoi: '<path d="M' + so(mx - 13) + ' ' + so(my2 - 3) + ' Q' + so(mx) + ' ' + so(my2 + 12) + ' ' + so(mx + 13) + ' ' + so(my2 - 3) + '"' + but(MUC, 4) + '/>',
      mo: '<path d="M' + so(mx - 14) + ' ' + so(my2 - 5) + ' Q' + so(mx) + ' ' + so(my2 + 22) + ' ' + so(mx + 14) + ' ' + so(my2 - 5) + ' Z"' + but(MUC, 3.5, MIENG_TRONG) + '/>',
      ngang: '<path d="M' + so(mx - 10) + ' ' + so(my2 + 2) + ' L' + so(mx + 10) + ' ' + so(my2 + 2) + '"' + but(MUC, 4) + '/>',
      meo: '<path d="M' + so(mx - 14) + ' ' + so(my2 + 7) + ' Q' + so(mx - 7) + ' ' + so(my2 - 4) + ' ' + so(mx) + ' ' + so(my2 + 2) +
        ' Q' + so(mx + 7) + ' ' + so(my2 - 3) + ' ' + so(mx + 14) + ' ' + so(my2 + 6) + '"' + but(MUC, 4) + '/>',
      o: '<ellipse cx="' + so(mx) + '" cy="' + so(my2 + 3) + '" rx="7" ry="9"' + but(MUC, 3, MIENG_TRONG) + '/>'
    };
    return s + ds[m.mieng];
  }

  // ---- Trang: một nhóm trong lớp vẽ, vẽ lại mỗi khung. m = {x, y (gốc ở khung), ti (tỉ lệ), lat, goc, sticker,
  // tuThe, mauAo}. Nhóm ngoài mang biến đổi bật vào (xoay/phóng quanh giữa thân), nhóm trong là hệ toạ độ nhân vật.
  // Nhân vật AI (m.anh = {dataUrl, rong, cao}, cỡ vẽ; hộp m.hop): khối HTML chứa <img> trong lớp bảng `goc` (trang
  // giải mã <img> trước khung đầu, chup.mo_trang), bật vào như người que quanh giữa ảnh; không vẽ lại mỗi khung.
  function tao(svg, m, goc) {
    if (m.anh) {
      var khoi = document.createElement('div');
      khoi.className = 'nhan-vat nhan-vat-anh' + (m.sticker ? ' nhan-vat-dan' : '');
      khoi.setAttribute('data-id', m.id);
      khoi.style.left = so(m.hop.x) + 'px';
      khoi.style.top = so(m.hop.y) + 'px';
      khoi.style.width = so(m.hop.w) + 'px';
      khoi.style.height = so(m.hop.h) + 'px';
      var img = document.createElement('img');
      img.src = m.anh.dataUrl;
      img.alt = '';
      khoi.appendChild(img);
      goc.appendChild(khoi);
      return { khoi: khoi };
    }
    var ngoai = document.createElementNS(NS, 'g');
    ngoai.setAttribute('class', 'nhan-vat' + (m.sticker ? ' nhan-vat-dan' : ''));
    ngoai.setAttribute('data-id', m.id);
    if (m.sticker) { ngoai.setAttribute('filter', 'url(#bong-dan)'); }
    var trong = document.createElementNS(NS, 'g');
    trong.setAttribute('transform', 'translate(0 ' + so(150 * m.ti) + ') scale(' + (m.lat ? -m.ti : m.ti) + ' ' + m.ti + ')');
    ngoai.appendChild(trong);
    svg.appendChild(ngoai);
    return { ngoai: ngoai, trong: trong };
  }
  function dat(o, m, t) {
    var h = hien(t);
    if (o.khoi) {
      o.khoi.style.opacity = String(h.a);
      o.khoi.style.transform = 'rotate(' + so(m.goc || 0) + 'deg) scale(' + h.k + ')';
      return;
    }
    o.ngoai.style.opacity = String(h.a);
    o.ngoai.setAttribute('transform', 'translate(' + so(m.x) + ' ' + so(m.y - 150 * m.ti) + ') rotate(' + so(m.goc || 0) + ') scale(' + h.k + ')');
    var d = dang(m.tuThe, t);
    o.trong.innerHTML = (m.sticker ? ve(d, m.mauAo, { vien: 12 }) : '') + ve(d, m.mauAo);
  }

  root.THI_NHAN_VAT = {
    TU_THE: TU_THE, MAU_AO: MAU_AO, CU_CHI: CU_CHI,
    dang: dang, mocChop: mocChop, hien: hien, ve: ve, tao: tao, dat: dat
  };
})(typeof globalThis !== 'undefined' ? globalThis : this);

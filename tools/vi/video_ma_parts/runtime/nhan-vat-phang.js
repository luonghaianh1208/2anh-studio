(function (root) {
  'use strict';

  // Nhân vật minh hoạ phẳng của video ngắn (ngan.py, kiểu "B" đã duyệt 2026-10-19). Vẽ trên đúng bộ khớp của người
  // que (THI_NHAN_VAT.dang(tuThe, t).khop), nên 10 tư thế và cách chuyển tư thế dùng chung. Hệ toạ độ như người que:
  // gốc giữa hai bàn chân, y âm hướng lên, cao khoảng 300, mặt nhìn về +x. `ve(d, nv)` trả chuỗi SVG; `nv` là nhân vật
  // ghép từ bộ phận do ngan.py dựng: {gioi, toc, mauToc, da, ao: {kieu, mau}, duoi: {kieu, mau}, mu, phu: [...]}.
  // Tên bộ phận phải khớp ngan.TOC, AO, DUOI, MU, PHU.
  var DA = { sang: '#F6CFAE', vua: '#EDB98C', ngam: '#C98F62' };
  var MUC = '#222';
  var MOI = '#8a3b2e';
  var TRANG = '#FFFFFF';

  function so(v) { return (Math.round(v * 10) / 10).toString(); }
  function P(o) { return so(o.x) + ' ' + so(o.y); }
  function pt(x, y) { return { x: x, y: y }; }
  function net(pts, w, c) {
    return '<path d="M' + pts.map(P).join(' L') + '" stroke="' + c + '" stroke-width="' + w +
      '" stroke-linecap="round" stroke-linejoin="round" fill="none"/>';
  }
  function tron(x, y, r, c) { return '<circle cx="' + so(x) + '" cy="' + so(y) + '" r="' + r + '" fill="' + c + '"/>'; }
  function giua(a, b, u) { return pt(a.x + (b.x - a.x) * u, a.y + (b.y - a.y) * u); }
  function vienCua(mau) { return mau.toUpperCase() === TRANG ? '#D2D2D2' : null; }
  // Nét có viền mảnh khi màu trắng (áo, quần trắng trên nền sáng).
  function netVien(pts, w, mau) { var v = vienCua(mau); return (v ? net(pts, w + 3, v) : '') + net(pts, w, mau); }

  function chan(k, nv, da) {
    var s = '', d = nv.duoi;
    var hT = pt(k.hong.x - 9, k.hong.y), hP = pt(k.hong.x + 9, k.hong.y);
    if (d.kieu === 'vay') {
      s += net([giua(hT, k.goiT, 0.5), k.goiT, k.chanT], 12, da) + net([giua(hP, k.goiP, 0.5), k.goiP, k.chanP], 12, da);
    } else if (d.kieu === 'quan-short') {
      s += net([giua(hT, k.goiT, 0.6), k.goiT, k.chanT], 13, da) + net([giua(hP, k.goiP, 0.6), k.goiP, k.chanP], 13, da);
      s += netVien([hT, giua(hT, k.goiT, 0.62)], 22, d.mau) + netVien([hP, giua(hP, k.goiP, 0.62)], 22, d.mau);
    } else {
      s += netVien([hT, k.goiT, k.chanT], 20, d.mau) + netVien([hP, k.goiP, k.chanP], 20, d.mau);
    }
    var giay = d.kieu === 'vay' || nv.ao.kieu === 'ao-dai' ? '#5A3A2A' : (nv.ao.kieu === 'the-thao' ? '#F4F4F4' : MUC);
    var vg = giay === '#F4F4F4' ? ' stroke="#BBB" stroke-width="2"' : '';
    s += '<ellipse cx="' + so(k.chanT.x - 6) + '" cy="' + so(k.chanT.y + 2) + '" rx="15" ry="8" fill="' + giay + '"' + vg + '/>';
    s += '<ellipse cx="' + so(k.chanP.x + 6) + '" cy="' + so(k.chanP.y + 2) + '" rx="15" ry="8" fill="' + giay + '"' + vg + '/>';
    if (d.kieu === 'vay') {
      s += '<path d="M' + so(k.hong.x - 22) + ' ' + so(k.hong.y - 4) + ' L' + so(k.hong.x + 22) + ' ' + so(k.hong.y - 4) +
        ' L' + so(k.hong.x + 34) + ' ' + so(k.hong.y + 58) + ' L' + so(k.hong.x - 34) + ' ' + so(k.hong.y + 58) + ' Z" fill="' +
        d.mau + '" stroke="' + d.mau + '" stroke-width="6" stroke-linejoin="round"/>';
    }
    return s;
  }

  // Thân áo: hình thang từ vai xuống dưới hông `duoiY`; áo dài dài tới gần mắt cá và xẻ tà hai bên.
  function than(k, nv) {
    var a = nv.ao, s = '';
    var duoiY = { blouse: 52, 'ao-dai': 96, hoodie: 10, 'ao-ba-ba': 14, vest: 14, 'tap-de': 8, 'dong-phuc': 8 }[a.kieu] || 6;
    var rong = a.kieu === 'ao-dai' ? 24 : 22;
    var v = vienCua(a.mau);
    function hinh(x0, x1, y1) {
      return 'M' + so(k.vaiT.x - 6) + ' ' + so(k.vaiT.y) + ' Q' + so(k.co.x) + ' ' + so(k.co.y - 6) + ' ' + so(k.vaiP.x + 6) +
        ' ' + so(k.vaiP.y) + ' L' + so(k.hong.x + x1) + ' ' + so(k.hong.y + y1) + ' L' + so(k.hong.x + x0) + ' ' + so(k.hong.y + y1) + ' Z';
    }
    if (a.kieu === 'ao-dai') {
      // Thân trên bó tới eo, rồi hai vạt trước/sau rời nhau (xẻ tà từ eo), vạt hơi loe.
      var eo = k.hong.y + 2;
      s += '<path d="' + hinh(-20, 20, 2) + '" fill="' + a.mau + '" stroke="' + a.mau + '" stroke-width="12" stroke-linejoin="round"/>';
      s += '<path d="M' + so(k.hong.x - 4) + ' ' + so(eo) + ' L' + so(k.hong.x + 22) + ' ' + so(eo) + ' L' + so(k.hong.x + 30) + ' ' +
        so(k.hong.y + duoiY) + ' L' + so(k.hong.x + 2) + ' ' + so(k.hong.y + duoiY) + ' Z" fill="' + a.mau + '"/>';
      s += '<path d="M' + so(k.hong.x - 22) + ' ' + so(eo) + ' L' + so(k.hong.x - 2) + ' ' + so(eo) + ' L' + so(k.hong.x - 6) + ' ' +
        so(k.hong.y + duoiY - 6) + ' L' + so(k.hong.x - 30) + ' ' + so(k.hong.y + duoiY - 6) + ' Z" fill="' + a.mau + '" opacity="0.88"/>';
      s += '<rect x="' + so(k.co.x - 7) + '" y="' + so(k.co.y - 4) + '" width="14" height="10" rx="3" fill="' + a.mau + '"/>';
      s += net([pt(k.co.x + 4, k.co.y + 8), pt(k.vaiP.x + 2, k.vaiP.y + 22)], 2.5, 'rgba(255,255,255,0.55)');
      return s;
    }
    var path = hinh(-rong, rong, duoiY);
    if (v) { s += '<path d="' + path + '" fill="' + v + '" stroke="' + v + '" stroke-width="17" stroke-linejoin="round"/>'; }
    s += '<path d="' + path + '" fill="' + a.mau + '" stroke="' + a.mau + '" stroke-width="14" stroke-linejoin="round"/>';
    var co = k.co;
    if (a.kieu === 'blouse') {
      s += '<path d="M' + so(co.x - 12) + ' ' + so(co.y + 4) + ' L' + so(co.x) + ' ' + so(co.y + 34) + ' L' + so(co.x + 12) +
        ' ' + so(co.y + 4) + ' Z" fill="#7FB7D9"/>' + net([pt(co.x, co.y + 34), pt(k.hong.x, k.hong.y + duoiY - 4)], 2.5, '#CFCFCF');
    }
    if (a.kieu === 'so-mi' || a.kieu === 'so-mi-dai' || a.kieu === 'dong-phuc') {
      s += '<path d="M' + so(co.x - 14) + ' ' + so(co.y + 2) + ' L' + so(co.x - 3) + ' ' + so(co.y + 14) + ' L' + so(co.x - 2) +
        ' ' + so(co.y + 2) + ' Z M' + so(co.x + 14) + ' ' + so(co.y + 2) + ' L' + so(co.x + 3) + ' ' + so(co.y + 14) + ' L' +
        so(co.x + 2) + ' ' + so(co.y + 2) + ' Z" fill="' + (a.kieu === 'dong-phuc' ? a.mau : TRANG) + '" stroke="rgba(0,0,0,0.25)" stroke-width="1.5"/>';
    }
    if (a.kieu === 'dong-phuc') {   // túi ngực, thắt lưng
      s += '<rect x="' + so(co.x + 4) + '" y="' + so(co.y + 22) + '" width="14" height="12" rx="2" fill="rgba(0,0,0,0.15)"/>';
      s += '<rect x="' + so(k.hong.x - 23) + '" y="' + so(k.hong.y - 4) + '" width="46" height="7" fill="#3A2A1A"/>';
    }
    if (a.kieu === 'vest') {   // ve áo hai bên, sơ mi trắng giữa, cúc
      s += '<path d="M' + so(co.x - 12) + ' ' + so(co.y + 2) + ' L' + so(co.x) + ' ' + so(co.y + 44) + ' L' + so(co.x + 12) + ' ' +
        so(co.y + 2) + ' Z" fill="' + TRANG + '"/>';
      s += net([pt(co.x - 12, co.y + 2), pt(co.x - 2, co.y + 44)], 4, 'rgba(0,0,0,0.25)') +
        net([pt(co.x + 12, co.y + 2), pt(co.x + 2, co.y + 44)], 4, 'rgba(0,0,0,0.25)');
      s += tron(co.x, co.y + 56, 2.6, 'rgba(0,0,0,0.35)');
    }
    if (a.kieu === 'tap-de') {   // tạp dề trắng phủ trước áo, dây cổ
      s += '<path d="M' + so(co.x - 13) + ' ' + so(co.y + 16) + ' L' + so(co.x + 13) + ' ' + so(co.y + 16) + ' L' + so(k.hong.x + 20) +
        ' ' + so(k.hong.y + 40) + ' L' + so(k.hong.x - 20) + ' ' + so(k.hong.y + 40) + ' Z" fill="' + TRANG + '" stroke="#D2D2D2" stroke-width="2"/>';
      s += '<path d="M' + so(co.x - 13) + ' ' + so(co.y + 16) + ' Q' + so(co.x) + ' ' + so(co.y - 4) + ' ' + so(co.x + 13) + ' ' +
        so(co.y + 16) + '" stroke="#D2D2D2" stroke-width="3" fill="none"/>';
    }
    if (a.kieu === 'the-thao') {   // sọc trắng dọc hai bên
      s += net([pt(k.vaiT.x + 2, k.vaiT.y + 8), pt(k.hong.x - 18, k.hong.y + 4)], 4, 'rgba(255,255,255,0.8)') +
        net([pt(k.vaiP.x - 2, k.vaiP.y + 8), pt(k.hong.x + 18, k.hong.y + 4)], 4, 'rgba(255,255,255,0.8)');
    }
    if (a.kieu === 'hoodie') {
      s += '<path d="M' + so(co.x - 22) + ' ' + so(co.y + 2) + ' Q' + so(co.x) + ' ' + so(co.y + 22) + ' ' + so(co.x + 22) + ' ' +
        so(co.y + 2) + '" stroke="rgba(0,0,0,0.18)" stroke-width="5" fill="none"/>';
      s += '<rect x="' + so(k.hong.x - 14) + '" y="' + so(k.hong.y - 18) + '" width="28" height="14" rx="5" fill="rgba(0,0,0,0.12)"/>';
    }
    if (a.kieu === 'ao-ba-ba') {
      [0.25, 0.5, 0.75].forEach(function (u) { var q = giua(pt(co.x, co.y + 10), k.hong, u); s += tron(q.x, q.y, 2.5, 'rgba(255,255,255,0.7)'); });
    }
    return s;
  }

  function tay(k, phia, nv, da) {
    var vai = k['vai' + phia], khuyu = k['khuyu' + phia], ban = k['tay' + phia], a = nv.ao, s = '';
    var ngan = a.kieu === 'so-mi' || a.kieu === 'ao-thun' || a.kieu === 'the-thao' || a.kieu === 'tap-de';
    var mau = a.kieu === 'tap-de' ? (a.mauTay || '#F4F4F4') : a.mau;
    if (ngan) {
      s += netVien([vai, khuyu], 17, mau) + net([khuyu, ban], 13, da);
    } else {
      s += netVien([vai, khuyu, giua(khuyu, ban, 0.82)], 17, mau);
    }
    return s + tron(ban.x, ban.y, 9, da);
  }

  function tocSau(h, nv) {
    var c = nv.mauToc;
    if (nv.toc === 'dai') {
      return '<path d="M' + so(h.x - 36) + ' ' + so(h.y - 4) + ' Q' + so(h.x - 46) + ' ' + so(h.y + 70) + ' ' + so(h.x - 26) + ' ' +
        so(h.y + 92) + ' L' + so(h.x + 4) + ' ' + so(h.y + 70) + ' Q' + so(h.x + 10) + ' ' + so(h.y + 20) + ' ' + so(h.x + 6) + ' ' +
        so(h.y - 10) + ' Z" fill="' + c + '"/>';
    }
    if (nv.toc === 'duoi-ngua') {
      return '<path d="M' + so(h.x - 30) + ' ' + so(h.y - 14) + ' Q' + so(h.x - 66) + ' ' + so(h.y + 6) + ' ' + so(h.x - 58) + ' ' +
        so(h.y + 56) + ' Q' + so(h.x - 44) + ' ' + so(h.y + 22) + ' ' + so(h.x - 24) + ' ' + so(h.y + 2) + ' Z" fill="' + c + '"/>';
    }
    if (nv.toc === 'bui') { return tron(h.x - 6, h.y - 40, 17, c); }
    return '';
  }

  function tocTruoc(h, nv) {
    var c = nv.mauToc;
    if (nv.toc === 'troc') {
      return '<path d="M' + so(h.x - 34) + ' ' + so(h.y - 4) + ' Q' + so(h.x - 20) + ' ' + so(h.y - 30) + ' ' + so(h.x + 2) + ' ' +
        so(h.y - 30) + '" stroke="rgba(255,255,255,0.35)" stroke-width="5" fill="none" stroke-linecap="round"/>';
    }
    if (nv.toc === 're-ngoi') {
      return '<path d="M' + so(h.x - 37) + ' ' + so(h.y + 6) + ' Q' + so(h.x - 34) + ' ' + so(h.y - 40) + ' ' + so(h.x + 4) + ' ' +
        so(h.y - 34) + ' Q' + so(h.x + 40) + ' ' + so(h.y - 30) + ' ' + so(h.x + 38) + ' ' + so(h.y - 2) + ' Q' + so(h.x + 30) + ' ' +
        so(h.y - 16) + ' ' + so(h.x + 8) + ' ' + so(h.y - 14) + ' Q' + so(h.x - 14) + ' ' + so(h.y - 16) + ' ' + so(h.x - 22) + ' ' +
        so(h.y + 6) + ' Z" fill="' + c + '"/>';
    }
    if (nv.toc === 'dai' || nv.toc === 'duoi-ngua' || nv.toc === 'bui') {
      return '<path d="M' + so(h.x - 38) + ' ' + so(h.y + 12) + ' Q' + so(h.x - 36) + ' ' + so(h.y - 38) + ' ' + so(h.x + 2) + ' ' +
        so(h.y - 34) + ' Q' + so(h.x + 40) + ' ' + so(h.y - 30) + ' ' + so(h.x + 38) + ' ' + so(h.y + 4) + ' Q' + so(h.x + 14) + ' ' +
        so(h.y - 20) + ' ' + so(h.x - 20) + ' ' + so(h.y - 4) + ' Q' + so(h.x - 28) + ' ' + so(h.y + 4) + ' ' + so(h.x - 30) + ' ' +
        so(h.y + 16) + ' Z" fill="' + c + '"/>';
    }
    // `ngan`: tóc ngắn ôm đầu, mái ngắn (đủ cao để kính không đè lên tóc).
    return '<path d="M' + so(h.x - 37) + ' ' + so(h.y + 2) + ' Q' + so(h.x - 30) + ' ' + so(h.y - 40) + ' ' + so(h.x + 6) + ' ' +
      so(h.y - 34) + ' Q' + so(h.x + 40) + ' ' + so(h.y - 28) + ' ' + so(h.x + 37) + ' ' + so(h.y - 2) + ' Q' + so(h.x + 18) + ' ' +
      so(h.y - 16) + ' ' + so(h.x - 37) + ' ' + so(h.y + 2) + ' Z" fill="' + c + '"/>';
  }

  function mat(h, d) {
    var m = (d && d.mat) || {}, s = '';
    if (m.mat === 'xoay') {
      s += net([pt(h.x, h.y + 6), pt(h.x + 8, h.y + 14)], 3, MUC) + net([pt(h.x + 16, h.y + 6), pt(h.x + 24, h.y + 14)], 3, MUC);
    } else {
      var r = m.mat === 'to' ? 5.5 : 4;
      s += tron(h.x + 4, h.y + 10, r, MUC) + tron(h.x + 20, h.y + 10, r, MUC);
    }
    if (m.mieng === 'o') {
      s += '<ellipse cx="' + so(h.x + 13) + '" cy="' + so(h.y + 27) + '" rx="5" ry="6" fill="' + MOI + '"/>';
    } else if (m.mieng === 'mo') {
      s += '<path d="M' + so(h.x + 3) + ' ' + so(h.y + 22) + ' Q' + so(h.x + 13) + ' ' + so(h.y + 36) + ' ' + so(h.x + 23) + ' ' +
        so(h.y + 22) + ' Z" fill="' + MOI + '"/>';
    } else {
      var cong = m.mieng === 'cuoi' ? 7 : (m.mieng === 'meo' ? -4 : 0);
      s += '<path d="M' + so(h.x + 4) + ' ' + so(h.y + 24) + ' Q' + so(h.x + 13) + ' ' + so(h.y + 24 + cong) + ' ' + so(h.x + 22) + ' ' +
        so(h.y + 24) + '" stroke="' + MOI + '" stroke-width="3.5" fill="none" stroke-linecap="round"/>';
    }
    return s + '<circle cx="' + so(h.x - 6) + '" cy="' + so(h.y + 22) + '" r="6" fill="#F49E8A" opacity=".5"/>';
  }

  function mu(h, ten) {
    if (ten === 'mu-bao-ho') {
      return '<path d="M' + so(h.x - 40) + ' ' + so(h.y - 6) + ' Q' + so(h.x) + ' ' + so(h.y - 58) + ' ' + so(h.x + 40) + ' ' +
        so(h.y - 6) + ' Z" fill="#F5C518"/><rect x="' + so(h.x - 46) + '" y="' + so(h.y - 10) + '" width="94" height="9" rx="4" fill="#E0B000"/>';
    }
    if (ten === 'bao-hiem') {
      return '<path d="M' + so(h.x - 40) + ' ' + so(h.y + 4) + ' Q' + so(h.x - 38) + ' ' + so(h.y - 52) + ' ' + so(h.x + 4) + ' ' +
        so(h.y - 46) + ' Q' + so(h.x + 42) + ' ' + so(h.y - 40) + ' ' + so(h.x + 40) + ' ' + so(h.y - 2) + ' Z" fill="#D64545"/>' +
        net([pt(h.x - 34, h.y + 4), pt(h.x - 8, h.y + 36)], 3, MUC);
    }
    if (ten === 'ke-pi') {   // mũ kê-pi: chóp xanh rêu, vành đen, huy hiệu vàng
      return '<path d="M' + so(h.x - 34) + ' ' + so(h.y - 18) + ' L' + so(h.x - 40) + ' ' + so(h.y - 44) + ' Q' + so(h.x) + ' ' +
        so(h.y - 62) + ' ' + so(h.x + 42) + ' ' + so(h.y - 46) + ' L' + so(h.x + 34) + ' ' + so(h.y - 18) + ' Z" fill="#3D5A2A"/>' +
        '<path d="M' + so(h.x - 6) + ' ' + so(h.y - 16) + ' Q' + so(h.x + 30) + ' ' + so(h.y - 20) + ' ' + so(h.x + 52) + ' ' +
        so(h.y - 8) + ' L' + so(h.x - 6) + ' ' + so(h.y - 8) + ' Z" fill="' + MUC + '"/>' + tron(h.x + 4, h.y - 34, 7, '#F2C14E');
    }
    if (ten === 'non-la') {
      return '<path d="M' + so(h.x - 66) + ' ' + so(h.y - 8) + ' L' + so(h.x) + ' ' + so(h.y - 66) + ' L' + so(h.x + 66) + ' ' +
        so(h.y - 8) + ' Z" fill="#E7C98A" stroke="#C9A35E" stroke-width="2"/>' +
        net([pt(h.x - 40, h.y - 30), pt(h.x + 40, h.y - 30)], 1.5, '#C9A35E');
    }
    if (ten === 'mu-dau-bep') {
      return '<rect x="' + so(h.x - 30) + '" y="' + so(h.y - 46) + '" width="60" height="22" fill="' + TRANG + '" stroke="#D2D2D2" stroke-width="2"/>' +
        tron(h.x - 18, h.y - 56, 18, TRANG) + tron(h.x + 4, h.y - 64, 22, TRANG) + tron(h.x + 24, h.y - 54, 17, TRANG);
    }
    if (ten === 'luoi-trai') {
      return '<path d="M' + so(h.x - 38) + ' ' + so(h.y - 6) + ' Q' + so(h.x - 34) + ' ' + so(h.y - 50) + ' ' + so(h.x + 2) + ' ' +
        so(h.y - 46) + ' Q' + so(h.x + 38) + ' ' + so(h.y - 42) + ' ' + so(h.x + 36) + ' ' + so(h.y - 8) + ' Z" fill="#3F7FD9"/>' +
        '<path d="M' + so(h.x + 10) + ' ' + so(h.y - 12) + ' Q' + so(h.x + 44) + ' ' + so(h.y - 16) + ' ' + so(h.x + 60) + ' ' +
        so(h.y - 4) + ' L' + so(h.x + 14) + ' ' + so(h.y - 4) + ' Z" fill="#2C5FA8"/>';
    }
    return '';
  }

  function phuKien(h, k, ten) {
    var co = k.co;
    if (ten === 'kinh') {
      return '<g fill="none" stroke="#2a2a2a" stroke-width="2.5"><circle cx="' + so(h.x + 4) + '" cy="' + so(h.y + 10) + '" r="8"/>' +
        '<circle cx="' + so(h.x + 21) + '" cy="' + so(h.y + 10) + '" r="8"/><path d="M' + so(h.x + 12) + ' ' + so(h.y + 10) + ' L' +
        so(h.x + 13) + ' ' + so(h.y + 10) + '"/></g>';
    }
    if (ten === 'khan-do') {
      return '<path d="M' + so(co.x - 16) + ' ' + so(co.y + 2) + ' L' + so(co.x + 16) + ' ' + so(co.y + 2) + ' L' + so(co.x + 4) + ' ' +
        so(co.y + 34) + ' L' + so(co.x - 4) + ' ' + so(co.y + 34) + ' Z" fill="#D7263D"/>';
    }
    if (ten === 'ca-vat') {
      return '<path d="M' + so(co.x - 4) + ' ' + so(co.y + 10) + ' L' + so(co.x + 4) + ' ' + so(co.y + 10) + ' L' + so(co.x + 6) + ' ' +
        so(co.y + 40) + ' L' + so(co.x) + ' ' + so(co.y + 47) + ' L' + so(co.x - 6) + ' ' + so(co.y + 40) + ' Z" fill="#B23A48"/>';
    }
    if (ten === 'ong-nghe') {
      return '<path d="M' + so(co.x - 12) + ' ' + so(co.y + 4) + ' Q' + so(co.x - 16) + ' ' + so(co.y + 34) + ' ' + so(co.x) + ' ' +
        so(co.y + 40) + ' Q' + so(co.x + 16) + ' ' + so(co.y + 34) + ' ' + so(co.x + 12) + ' ' + so(co.y + 4) +
        '" stroke="#555" stroke-width="3" fill="none"/>' + tron(co.x, co.y + 42, 5, '#888');
    }
    if (ten === 'phu-hieu') {   // phù hiệu trên tay áo/ngực
      return '<path d="M' + so(co.x + 8) + ' ' + so(co.y + 20) + ' L' + so(co.x + 22) + ' ' + so(co.y + 20) + ' L' + so(co.x + 22) + ' ' +
        so(co.y + 32) + ' L' + so(co.x + 15) + ' ' + so(co.y + 38) + ' L' + so(co.x + 8) + ' ' + so(co.y + 32) + ' Z" fill="#F2C14E" stroke="#B88A1E" stroke-width="1.5"/>';
    }
    if (ten === 'cap-sach') {   // cặp đeo sau lưng: khối sau thân, quai trước vai
      return '<rect x="' + so(k.hong.x - 46) + '" y="' + so(co.y + 6) + '" width="26" height="50" rx="6" fill="#3F7FD9"/>' +
        net([pt(k.vaiT.x + 4, k.vaiT.y), pt(k.hong.x - 12, k.hong.y - 6)], 4, '#2C5FA8');
    }
    return '';
  }

  function ve(d, nv) {
    var k = d.khop, da = DA[nv.da] || DA.vua, h = pt(k.dau.x, k.dau.y + 8);
    var phu = nv.phu || [];
    var s = '<g class="nhan-vat-phang">';
    if (phu.indexOf('cap-sach') >= 0) { s += phuKien(h, k, 'cap-sach'); }
    s += tocSau(h, nv) + chan(k, nv, da) + tay(k, 'T', nv, da) + than(k, nv);
    ['khan-do', 'ca-vat', 'ong-nghe', 'phu-hieu'].forEach(function (p) { if (phu.indexOf(p) >= 0) { s += phuKien(h, k, p); } });
    s += tay(k, 'P', nv, da);
    s += net([pt(k.co.x, k.co.y - 8), pt(k.co.x, k.co.y + 4)], 14, da);
    s += tron(h.x, h.y, 36, nv.toc === 'troc' ? da : da) + mat(h, d) + tocTruoc(h, nv);
    if (phu.indexOf('kinh') >= 0) { s += phuKien(h, k, 'kinh'); }
    if (nv.mu) { s += mu(h, nv.mu); }
    return s + '</g>';
  }

  root.THI_NHAN_VAT_PHANG = { ve: ve, DA: DA };
})(typeof globalThis !== 'undefined' ? globalThis : this);

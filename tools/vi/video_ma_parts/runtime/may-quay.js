(function (root) {
  'use strict';

  // Máy quay theo t: hàm thuần, chạy được trong Node. `hop[id] = {x, y, w, h}` đo ở Z = 1.
  // Kết quả {z, tx, ty}: điểm (x, y) của lớp bảng hiện ở (z*x + tx, z*y + ty).
  // Rộng, cao, đáy vùng nội dung (mép trên phụ đề) và tâm lấy từ khổ hiện tại (kho.js), đọc lúc tính.
  var ZMAX = 1.35;
  var CHUYEN = 0.6;
  var THU = 1.2;
  var XONG = 0.2;
  var GOC = { z: 1, tx: 0, ty: 0 };

  function kep(x, a, b) { return x < a ? a : (x > b ? b : x); }
  function em(u) { u = kep(u, 0, 1); return u * u * (3 - 2 * u); }
  function tron(a, b, u) {
    if (u >= 1) { return { z: b.z, tx: b.tx, ty: b.ty }; }
    return { z: a.z + (b.z - a.z) * u, tx: a.tx + (b.tx - a.tx) * u, ty: a.ty + (b.ty - a.ty) * u };
  }
  function ketThuc(m) { return m.batDau + m.thoiLuong; }
  var UU_TIEN = { hinh: 3, chu: 2, net: 1 };
  function hon(a, b) {
    if (a.batDau !== b.batDau) { return a.batDau > b.batDau; }
    return (UU_TIEN[a.kieu] || 0) > (UU_TIEN[b.kieu] || 0);
  }
  function quayDuoc(m, hop) { return !m.dong && m.quay !== false && !!hop[m.id]; }

  // Mục tiêu tại t: mục đang vẽ (batDau <= t < kết thúc) bắt đầu muộn nhất (trùng thì hình, chữ, nét);
  // không có thì mục vừa xong gần nhất.
  function mucTai(ds, hop, t) {
    var ve = null;
    var xong = null;
    ds.forEach(function (m) {
      if (!quayDuoc(m, hop)) { return; }
      if (t >= m.batDau && t < ketThuc(m)) {
        if (!ve || hon(m, ve)) { ve = m; }
      } else if (ketThuc(m) <= t && (!xong || ketThuc(m) >= ketThuc(xong))) {
        xong = m;
      }
    });
    return ve || xong;
  }

  function kho() { return root.THI_KHO.lay(); }

  // Z nhỏ nhất để hộp có đáy <= DAY mà lớp bảng vẫn phủ kín khung: z >= (CAO - DAY) / (CAO - đáy).
  // Khổ ngang (DAY 620, CAO 720): chỉ làm được khi đáy <= 720 - 100 / 1,35 ≈ 646; hộp thấp hơn thì z kẹp ở
  // 1,35 và đáy vượt 620 (bố cục cảnh giữ mọi nội dung trên y = 630 nên không xảy ra).
  function zToiThieu(h) {
    var k = kho();
    var day = h.y + h.h;
    return day > k.day ? Math.min(ZMAX, (k.cao - k.day) / (k.cao - day)) : 1;
  }

  function kepKhoang(v, lo, hi, phuLo, phuHi) {
    return lo <= hi ? kep(v, lo, hi) : kep(v, phuLo, phuHi);
  }

  function gop(a, b) {
    var x = Math.min(a.x, b.x), y = Math.min(a.y, b.y);
    return { x: x, y: y, w: Math.max(a.x + a.w, b.x + b.w) - x, h: Math.max(a.y + a.h, b.y + b.h) - y };
  }

  // Kẹp để lớp bảng phủ kín khung và hộp nằm trong khung, đáy <= DAY.
  // `giu` (tuỳ chọn) = {hop, tren}: hộp phải luôn nằm trọn trong khung cùng mục tiêu (tiêu đề, thẻ, dòng tài liệu),
  // đỉnh không cao hơn `tren` (dưới khung loạt). Z bị giới hạn để cả hai cùng vừa; Z = 1 luôn vừa vì bố cục đặt
  // chúng trong khung sẵn.
  function kepHop(s, h, giu) {
    var k = kho();
    var z = kep(Math.max(s.z, zToiThieu(h)), 1, ZMAX);
    var tren = 0;
    if (giu && giu.hop) {
      h = gop(h, giu.hop);
      tren = Math.min(giu.tren || 0, h.y);
      // Trừ 1e-6 để hai cận của tx, ty không đảo nhau vì sai số làm tròn khi z đúng bằng giới hạn.
      z = Math.max(1, Math.min(z, k.rong / h.w - 1e-6, (Math.max(k.day, h.y + h.h) - tren) / h.h - 1e-6));
    }
    var phuX = k.rong * (1 - z), phuY = k.cao * (1 - z);
    var day = giu && giu.hop ? Math.max(k.day, h.y + h.h) : k.day;
    var tx = kepKhoang(s.tx, Math.max(phuX, -z * h.x), Math.min(0, k.rong - z * (h.x + h.w)), phuX, 0);
    var ty = kepKhoang(s.ty, Math.max(phuY, tren - z * h.y), Math.min(0, day - z * (h.y + h.h)), phuY, 0);
    return { z: z, tx: tx, ty: ty };
  }

  // Ngưỡng cao khi ngắm mục tiêu: đáy vùng nội dung trừ 60 px lề trên (khổ ngang: 620 − 60 = 560, như cũ).
  function ngam(h, giu) {
    var k = kho();
    var z = kep(Math.min(0.6 * k.rong / h.w, 0.6 * (k.day - 60) / h.h), 1, ZMAX);
    return kepHop({ z: z, tx: k.tamX - z * (h.x + h.w / 2), ty: k.tamY - z * (h.y + h.h / 2) }, h, giu);
  }

  function theoMuc(ds, hop, t, giu) {
    var moc = [];
    ds.forEach(function (m) {
      if (!quayDuoc(m, hop)) { return; }
      moc.push(m.batDau, ketThuc(m));
    });
    moc.sort(function (a, b) { return a - b; });
    var dang = null;
    var tu = GOC;
    var luc = -Infinity;
    function hienTai(x) {
      var s = tron(tu, dang ? ngam(hop[dang.id], giu) : GOC, em((x - luc) / CHUYEN));
      return dang ? kepHop(s, hop[dang.id], giu) : s;
    }
    for (var i = 0; i < moc.length && moc[i] <= t; i++) {
      var moi = mucTai(ds, hop, moc[i]);
      if (moi !== dang) {
        tu = hienTai(moc[i]);
        dang = moi;
        luc = moc[i];
      }
    }
    return hienTai(t);
  }

  function tinh(ds, hop, t, gh, cauHinh) {
    cauHinh = cauHinh || {};
    if (cauHinh.mayQuay === false) { return { z: 1, tx: 0, ty: 0 }; }
    if (cauHinh.day) {
      var z = 1 + 0.06 * kep(t / gh, 0, 1);
      return { z: z, tx: kho().rong / 2 * (1 - z), ty: kho().cao / 2 * (1 - z) };
    }
    var ve = em((t - (gh - THU)) / (THU - XONG));
    if (ve >= 1) { return { z: 1, tx: 0, ty: 0 }; }
    return tron(theoMuc(ds, hop, t, cauHinh.giu), GOC, ve);
  }

  function mucTieu(ds, hop, t) {
    var m = mucTai(ds, hop, t);
    return m ? m.id : null;
  }

  root.THI_MAY_QUAY = { ZMAX: ZMAX, tinh: tinh, mucTieu: mucTieu, kepHop: kepHop };
})(typeof globalThis !== 'undefined' ? globalThis : this);

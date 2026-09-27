(function (root) {
  'use strict';
  var V = root.THI_VIDEO;
  var NS = 'http://www.w3.org/2000/svg';
  // Câu hỏi nhanh trong ô `cau-hoi` (khổ ngang y 36..610). Bút viết câu hỏi (cao 150 ở đỉnh ô) rồi từng lựa chọn
  // (hai cột rộng nửa ô trừ 25, căn giữa ô lẻ cuối) theo mốc câu của lời câu hỏi, xong trước đếm ngược LUOT giây để
  // bàn tay kịp rời bảng. Đếm ngược: đồng hồ vòng tròn ở vùng giải thích (chưa có chữ), máy quay đẩy rất nhẹ; không
  // có bàn tay. Tại batDauGiai: lựa chọn đúng có viền xanh, dấu ✓ và nảy; lựa chọn khác mờ còn 0,35; rồi bút viết
  // giải thích (cao 140 ở đáy ô). Mọi trạng thái là hàm của t.
  var CHU = 'ABCD';
  var LUOT = 0.45; // bàn tay rời bảng mất 0,4 s (ban-tay.js), thêm lề
  var MO = 0.35;
  var DAY_Z = 0.05, VE_Z = 0.8;
  function oCau() { return V.o('cau-hoi'); }
  // Đồng hồ giữa bề ngang ô, trên đáy ô 70. Máy quay đẩy quanh giữa ô (lệch xuống 7).
  function dongHo() { var o = oCau(); return { x: o.x + o.w / 2, y: o.y + o.h - 70, r: 52 }; }
  function tamZ() { var o = oCau(); return { x: o.x + o.w / 2, y: o.y + o.h / 2 + 7 }; }

  function kep01(x) { return x < 0 ? 0 : (x > 1 ? 1 : x); }
  function D() { return root.THI_DONG; }

  // Ô lựa chọn {x, y, w, h}: 2 lựa chọn một hàng cao 120; 3–4 lựa chọn hai hàng cao 105.
  // Hàng đầu dưới đỉnh ô 176 (một hàng thì thêm 28), hàng hai cách 20; cột trái lùi 10, cột phải qua giữa ô 15.
  function bo(du) {
    var o = oCau();
    var n = du.truong['lua-chon'].length;
    var h = n > 2 ? 105 : 120;
    var y0 = o.y + 176;
    var ys = n > 2 ? [y0, y0 + h + 20] : [y0 + 28];
    var rong = o.w / 2 - 25;
    var xs = [o.x + 10, o.x + o.w / 2 + 15];
    return du.truong['lua-chon'].map(function (_, k) {
      var x = n % 2 === 1 && k === n - 1 ? o.x + (o.w - rong) / 2 : xs[k % 2];
      return { x: x, y: ys[Math.floor(k / 2)], w: rong, h: h };
    });
  }

  // Viết lần lượt (mục sau không bắt đầu trước khi mục trước xong); lố quá `het` thì co cả lịch viết vào [t0, het].
  function xepLich(ds, het) {
    var xong = 0;
    ds.forEach(function (m) { m.batDau = Math.max(m.batDau, xong); xong = m.batDau + m.thoiLuong; });
    var t0 = ds[0].batDau;
    if (xong <= het || het <= t0) { return; }
    var k = (het - t0) / (xong - t0);
    ds.forEach(function (m) { m.batDau = t0 + (m.batDau - t0) * k; m.thoiLuong *= k; });
  }

  function trangThai(du, t) {
    var q = du.cauHoi;
    var dung = CHU.indexOf(q.dapAn);
    var troi = t - q.batDauDem;
    var con = Math.min(q.cho, Math.max(0, q.cho - troi));
    var nghi = q.batDauGiai - (q.batDauDem + q.cho);
    var a = t < q.batDauDem || t >= q.batDauGiai ? 0
      : Math.min(kep01(troi / 0.25), nghi > 0 ? kep01((q.batDauGiai - t) / nghi) : 1);
    var f = con / q.cho;
    var nhip = troi - Math.floor(troi);
    var dem = {
      a: a,
      s: 0.6 + 0.4 * D().easeOutBack(kep01(troi / 0.35)),
      so: Math.ceil(con - 1e-9),
      f: f,
      sSo: troi >= 0 && troi < q.cho ? 1 + 0.22 * Math.pow(1 - kep01(nhip / 0.35), 2) : 1,
      mau: f > 0.5 ? '#2563eb' : (f > 0.2 ? '#f59e0b' : '#dc2626')
    };
    var pg = t - q.batDauGiai;
    var hien = pg > 0;
    var mo = hien ? 1 - (1 - MO) * D().easeInOut(kep01(pg / 0.4)) : 1;
    var nay = hien ? D().nayDanHoi(kep01(pg / 0.9), 0.2) : 1;
    var pd = hien ? kep01((pg - 0.15) / 0.35) : 0;
    return {
      dem: dem,
      dung: dung,
      vien: hien ? kep01(pg / 0.35) : 0,
      dau: { a: pd > 0 ? 1 : 0, s: pd > 0 ? D().easeOutBack(pd) : 0 },
      lo: du.truong['lua-chon'].map(function (_, k) { return k === dung ? { a: 1, s: nay } : { a: mo, s: 1 }; })
    };
  }

  // Đẩy máy quay rất nhẹ trong lúc đếm ngược (toàn cảnh vẫn trong khung), về gốc sau khi hiện đáp án.
  function mayQuay(du, t, cam) {
    var q = du.cauHoi;
    var p;
    if (t < q.batDauDem) { return cam; }
    if (t < q.batDauGiai) {
      p = D().easeInOut(kep01((t - q.batDauDem) / (q.batDauGiai - q.batDauDem)));
    } else {
      var ve = Math.max(0.1, Math.min(VE_Z, du.thoiLuong - 0.3 - q.batDauGiai));
      p = 1 - D().easeInOut(kep01((t - q.batDauGiai) / ve));
    }
    if (p <= 0) { return cam; }
    var z = 1 + DAY_Z * p;
    var tam = tamZ();
    return { z: z, tx: tam.x * (1 - z), ty: tam.y * (1 - z) };
  }

  function taoSvg(the, thuocTinh, cha) {
    var el = document.createElementNS(NS, the);
    Object.keys(thuocTinh).forEach(function (k) { el.setAttribute(k, thuocTinh[k]); });
    cha.appendChild(el);
    return el;
  }
  function co(s, x, y) { return s === 1 ? '' : 'matrix(' + s + ',0,0,' + s + ',' + (x * (1 - s)) + ',' + (y * (1 - s)) + ')'; }

  var canh = {
    CHU: CHU, bo: bo, trangThai: trangThai, mayQuay: mayQuay,
    get DONG_HO() { return dongHo(); },
    muc: function (du) {
      var B = V.tao(du);
      var t = du.truong;
      var q = du.cauHoi;
      var o = bo(du);
      var oc = oCau();
      var cauHoi = t['cau-hoi'][0];
      var viet = [B.chu('cau-hoi', cauHoi, oc.x, oc.y, oc.w, 150, V.demKyTu(cauHoi) > 100 ? 32 : 36, du.moc[0],
        { mau: 'giua-doc', day: true, quay: false })];
      var coLc = t['lua-chon'].some(function (c) { return V.demKyTu(c) > 34; }) ? 24 : 28;
      o.forEach(function (b, k) {
        var bd = du.moc[k + 1];
        viet.push(B.net('o-' + k, V.hopQua(b.x, b.y, b.w, b.h, 20 + k) + ' ' + V.vongTron(b.x + 48, b.y + b.h / 2, 26), bd, 0.5,
          { mau: 'o-' + k, day: 3, quay: false, am: 'ting' }));
        viet.push(B.chu('ky-' + k, CHU[k], b.x + 22, b.y + b.h / 2 - 22, 52, 44, 30, bd,
          { can: 'giua', mau: 'nhan giua-doc', day: true, quay: false }));
        viet.push(B.chu('lc-' + k, t['lua-chon'][k], b.x + 88, b.y + 8, b.w - 118, b.h - 16, coLc, bd,
          { mau: 'giua-doc', day: true, quay: false }));
      });
      xepLich(viet, q.batDauDem - LUOT);
      return viet.concat([B.chu('giai-thich', t['giai-thich'][0], oc.x, oc.y + oc.h - 140, oc.w, 140, 28, q.batDauGiai + 0.6,
        { mau: 'xanh', quay: false })]);
    },
    // Đồng hồ, viền đúng và dấu ✓ không phải mục (không bàn tay, không máy quay): tạo một lần, đặt lại theo t.
    dung: function (goc, du) {
      var svg = goc.querySelector('svg.ve');
      var o = bo(du);
      var dung = CHU.indexOf(du.cauHoi.dapAn);
      var b = o[dung];
      var DONG_HO = dongHo();
      var el = {};
      el.dongHo = taoSvg('g', { id: 'dong-ho' }, svg);
      taoSvg('circle', { class: 'nen', cx: DONG_HO.x, cy: DONG_HO.y, r: DONG_HO.r }, el.dongHo);
      el.cung = taoSvg('circle', { class: 'cung', cx: DONG_HO.x, cy: DONG_HO.y, r: DONG_HO.r, pathLength: 1,
        transform: 'rotate(-90 ' + DONG_HO.x + ' ' + DONG_HO.y + ')' }, el.dongHo);
      el.cung.style.strokeDasharray = '1';
      el.so = taoSvg('text', { class: 'so', x: DONG_HO.x, y: DONG_HO.y, 'text-anchor': 'middle', 'dominant-baseline': 'central' }, el.dongHo);
      el.vien = taoSvg('path', { class: 'dung-vien', d: V.hopQua(b.x - 7, b.y - 7, b.w + 14, b.h + 14, 97), pathLength: 1 }, svg);
      el.vien.style.strokeDasharray = '1';
      el.dau = taoSvg('g', { id: 'dau-dung' }, svg);
      el.dauTam = { x: b.x + b.w - 4, y: b.y + 4 };
      taoSvg('circle', { cx: el.dauTam.x, cy: el.dauTam.y, r: 22 }, el.dau);
      taoSvg('path', { d: 'M' + (el.dauTam.x - 10) + ' ' + (el.dauTam.y + 1) + ' L' + (el.dauTam.x - 3) + ' ' + (el.dauTam.y + 9) +
        ' L' + (el.dauTam.x + 11) + ' ' + (el.dauTam.y - 8) }, el.dau);
      el.tam = { x: b.x + b.w / 2, y: b.y + b.h / 2 };
      el.lo = o.map(function (_, k) {
        return { net: svg.querySelector('path.o-' + k), chu: [goc.querySelector('[data-id="ky-' + k + '"]'), goc.querySelector('[data-id="lc-' + k + '"]')] };
      });
      goc.cauHoi = el;
    },
    capNhat: function (goc, du, t) {
      var el = goc.cauHoi;
      var s = trangThai(du, t);
      var d = s.dem;
      var DONG_HO = dongHo();
      el.dongHo.style.opacity = String(d.a);
      el.dongHo.setAttribute('transform', co(d.s, DONG_HO.x, DONG_HO.y));
      el.cung.style.strokeDashoffset = String(1 - d.f);
      el.cung.style.stroke = d.mau;
      el.so.textContent = String(d.so);
      el.so.setAttribute('transform', co(d.sSo, DONG_HO.x, DONG_HO.y));
      el.lo.forEach(function (lo, k) {
        var o = s.lo[k];
        if (o.a < 1) { lo.net.style.opacity = String(o.a); }
        lo.net.setAttribute('transform', co(o.s, el.tam.x, el.tam.y));
        lo.chu.forEach(function (c) {
          c.style.opacity = o.a < 1 ? String(o.a) : '';
          c.style.transformOrigin = (el.tam.x - parseFloat(c.style.left)) + 'px ' + (el.tam.y - parseFloat(c.style.top)) + 'px';
          c.style.transform = o.s === 1 ? '' : 'scale(' + o.s + ')';
        });
      });
      var nay = s.lo[s.dung].s;
      el.vien.style.strokeDashoffset = String(1 - D().easeInOut(s.vien));
      el.vien.style.opacity = s.vien > 0 ? '1' : '0';
      el.vien.setAttribute('transform', co(nay, el.tam.x, el.tam.y));
      el.dau.style.opacity = String(s.dau.a);
      el.dau.setAttribute('transform', (co(nay, el.tam.x, el.tam.y) + ' ' + co(Math.max(s.dau.s, 1e-3), el.dauTam.x, el.dauTam.y)).trim());
    }
  };
  root.THI_CANH['cau-hoi'] = canh;
})(typeof globalThis !== 'undefined' ? globalThis : this);

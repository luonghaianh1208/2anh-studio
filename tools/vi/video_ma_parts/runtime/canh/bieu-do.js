(function (root) {
  'use strict';
  var V = root.THI_VIDEO;
  var NS = 'http://www.w3.org/2000/svg';
  // Vùng vẽ cột/đường trong ô `bieu-do`: trục đứng ở X0 (lùi 50), tới mép phải ô (X1); vạch trên cùng ở PT (dưới
  // đỉnh ô 66), vạch dưới cùng ở PB (trên đáy ô 120). Dải 30 px trên PT và dưới PB dành cho nhãn giá trị; nhãn loại
  // dưới PB + 34, tên trục ngang ở PB + 90 (tới đáy ô), tên trục đứng ở đỉnh ô. Hình tròn tâm giữa bề ngang ô.
  var R = 150;
  function khung() {
    var o = V.o('bieu-do');
    var PT = o.y + 66, PB = o.y + o.h - 120;
    return { o: o, X0: o.x + 50, X1: o.x + o.w, PT: PT, PB: PB, TAM: { x: o.x + o.w / 2, y: (PT + PB) / 2 + 26 } };
  }
  // Máy quay giữ toàn cảnh biểu đồ (mọi mục `quay: false`): phóng vào một cột làm mất phép so sánh giữa các cột.
  var NHAN_TRON = 34;
  var TO_COT = { duong: 'rgba(59, 130, 246, 0.28)', am: 'rgba(239, 68, 68, 0.26)' };
  var TO_LAT = ['#93c5fd', '#fca5a5', '#fde68a', '#86efac', '#c4b5fd', '#fdba74', '#67e8f9', '#f9a8d4'];

  function lam(x) { return Math.round(x * 10) / 10; }
  function soVN(v) { return String(v).replace('.', ','); }
  function kep(x, a, b) { return x < a ? a : (x > b ? b : x); }

  // Thang số tròn: bước 1, 2 hoặc 5 × 10^n nhỏ nhất cho không quá 6 vạch phủ [thap, cao]; luôn 4–6 vạch.
  function thangSo(thap, cao) {
    if (!(cao > thap)) {
      if (thap > 0) { thap = 0; } else if (cao < 0) { cao = 0; } else { cao = thap + 1; }
    }
    var e = Math.floor(Math.log10(cao - thap)) - 2;
    for (;; e++) {
      for (var i = 0; i < 3; i++) {
        var buoc = [1, 2, 5][i] * Math.pow(10, e);
        var lo = Math.floor(thap / buoc + 1e-9), hi = Math.ceil(cao / buoc - 1e-9);
        if (hi - lo + 1 <= 6) {
          // Ít hơn 4 vạch (ví dụ −5..4,25 với bước 5): nới thêm một bước về phía số liệu sát mép hơn.
          while (hi - lo + 1 < 4) {
            if (thap - lo * buoc <= hi * buoc - cao) { lo--; } else { hi++; }
          }
          var chuSo = Math.max(0, -e);
          var vach = [];
          for (var k = lo; k <= hi; k++) { vach.push(Number((k * buoc).toFixed(chuSo)) || 0); }
          return { buoc: Number(buoc.toFixed(chuSo)), vach: vach, lo: vach[0], hi: vach[vach.length - 1] };
        }
      }
    }
  }
  // Cột luôn mọc từ 0 nên thang có 0. Đường: bỏ 0 khi số liệu cùng dấu và chênh ít (ví dụ nhiệt độ 20–25).
  function thang(so, kieu) {
    var thap = Math.min.apply(null, so), cao = Math.max.apply(null, so);
    if (kieu === 'cot' || (thap > 0 && thap <= cao / 2) || (cao < 0 && cao >= thap / 2)) {
      thap = Math.min(0, thap);
      cao = Math.max(0, cao);
    }
    return thangSo(thap, cao);
  }
  // Chuỗi số đúng như tác giả viết (giữ số chữ số thập phân) để hiện bằng số chạy `{{…}}`.
  function chuoiSo(du) {
    return du.truong['du-lieu'].map(function (v) { return /(-?\d+(?:\.\d+)?)\s*$/.exec(v)[1]; });
  }
  function duongCung(cx, cy, r, a0, a1) {
    var kq = [];
    var n = Math.max(2, Math.ceil(Math.abs(a1 - a0) / 8));
    for (var i = 0; i <= n; i++) {
      var a = (a0 + (a1 - a0) * i / n) * Math.PI / 180;
      kq.push([cx + r * Math.cos(a), cy + r * Math.sin(a)]);
    }
    return kq;
  }

  function cotDuong(B, du, kieu, so) {
    var K = khung();
    var X0 = K.X0, X1 = K.X1, PT = K.PT, PB = K.PB;
    var kq = [];
    var n = du.duLieu.length;
    var o = (X1 - X0) / n;
    var th = thang(du.duLieu.map(function (d) { return d[1]; }), kieu);
    var y = function (v) { return PB - (v - th.lo) * (PB - PT) / (th.hi - th.lo); };
    var y0 = y(kep(0, th.lo, th.hi));
    var tt = du.truong;
    kq.push(B.net('luoi', th.vach.map(function (v, i) { return V.duongQua([[X0 - 8, y(v)], [X1, y(v)]], 50 + i); }).join(' '),
      0.5, 0.5, { mau: 'luoi', day: 2, quay: false, tay: false }));
    kq.push(B.net('truc-doc', V.duongQua([[X0, PB + 8], [X0, PT - 18]], 3), 0.3, 0.5, { quay: false }));
    kq.push(B.net('truc-ngang', V.duongQua([[X0 - 8, y0], [X1 + 10, y0]], 4), 0.4, 0.6, { quay: false }));
    th.vach.forEach(function (v, i) {
      kq.push(B.chu('vach-' + i, soVN(v), X0 - 130, y(v) - 14, 120, 28, 18, 0.6, { can: 'phai', quay: false, tay: false }));
    });
    var tenDoc = tt['truc-doc'] ? tt['truc-doc'][0] + (tt['don-vi'] ? ' (' + tt['don-vi'][0] + ')' : '')
      : (tt['don-vi'] ? 'Đơn vị: ' + tt['don-vi'][0] : '');
    // Tên trục đứng từ trái trục 90, rộng bằng ô trừ 220; tên trục ngang canh phải về X1, rộng bằng ô trừ 340.
    if (tenDoc) { kq.push(B.chu('ten-truc-doc', tenDoc, X0 - 90, K.o.y, K.o.w - 220, 32, 20, 0.8, { mau: 'nhan', quay: false, tay: false })); }
    if (tt['truc-ngang']) {
      kq.push(B.chu('ten-truc-ngang', tt['truc-ngang'][0], X1 - (K.o.w - 340), PB + 90, K.o.w - 340, 30, 20, 0.8, { can: 'phai', mau: 'nhan', quay: false, tay: false }));
    }
    var coNhan = o >= 200 ? 22 : 18;
    var dai = Math.max.apply(null, so.map(function (s) { return s.length; }));
    var coSo = Math.max(14, Math.min(22, Math.floor((o - 10) / (0.58 * dai))));
    var rong = Math.min(96, 0.56 * o);
    var truoc = null;
    du.duLieu.forEach(function (d, k) {
      var cx = X0 + (k + 0.5) * o;
      var v = d[1];
      var yv = y(v);
      var am = v < 0;
      kq.push(B.chu('nhan-' + k, d[0], cx - o / 2 + 4, PB + 34, o - 8, 52, coNhan, 0.7 + 0.05 * k, { can: 'giua', quay: false, tay: false }));
      var ySo;
      if (kieu === 'cot') {
        var c = B.net('cot-' + k, V.duongQua([[cx - rong / 2, y0], [cx - rong / 2, yv], [cx + rong / 2, yv], [cx + rong / 2, y0]], 60 + k),
          du.moc[k], 0.8, { mau: am ? 'do' : 'nhan', quay: false, am: 'ting' });
        c.to = { x: lam(cx - rong / 2), rong: lam(rong), y0: lam(y0), y: lam(yv), mau: am ? TO_COT.am : TO_COT.duong };
        kq.push(c);
        ySo = am ? yv + 2 : yv - 30;
      } else {
        if (truoc) { kq.push(B.net('doan-' + k, V.duongQua([truoc, [cx, yv]], 40 + k), du.moc[k], 0.4, { mau: 'nhan', quay: false })); }
        kq.push(B.net('diem-' + k, V.vongTron(lam(cx), lam(yv), 8), du.moc[k], 0.3, { mau: 'do', quay: false, am: 'ting' }));
        truoc = [cx, yv];
        ySo = yv - 38;
      }
      kq.push(B.chu('so-' + k, '{{' + so[k] + '}}', cx - o / 2 + 3, ySo, o - 6, 28, coSo, du.moc[k] + 0.3, { can: 'giua', mau: am ? 'do' : 'nhan', quay: false }));
    });
    return kq;
  }

  // Phần trăm viết dạng số chạy: một chữ số thập phân; lát nhỏ hơn 1% giữ hai chữ số có nghĩa (0,012%) để không
  // hiện thành 0%. Không bao giờ dạng mũ (1e-7) vì `{{…}}` chỉ nhận số thập phân thường.
  function phanTram(v, tong) {
    var p = v / tong * 100;
    var chuSo = p >= 1 ? 1 : Math.min(8, 1 - Math.floor(Math.log10(p)));
    return String(Number(p.toFixed(chuSo))).indexOf('e') < 0 ? String(Number(p.toFixed(chuSo))) : p.toFixed(chuSo);
  }
  // Nhãn lát xếp thành hai cột hai bên hình tròn, dãn đều để không chồng nhau (cách nhau ít nhất NHAN_TRON px).
  function xepNhan(ds, o) {
    ds.sort(function (a, b) { return a.y - b.y; });
    var tren = o.y + 20, duoi = o.y + o.h - 16;
    ds.forEach(function (d, i) { d.y = Math.max(d.y, i ? ds[i - 1].y + NHAN_TRON : tren); });
    for (var i = ds.length - 1; i >= 0; i--) { ds[i].y = Math.min(ds[i].y, i < ds.length - 1 ? ds[i + 1].y - NHAN_TRON : duoi); }
  }
  function tron(B, du) {
    var K = khung();
    var TAM = K.TAM;
    var kq = [];
    var tong = du.duLieu.reduce(function (s, d) { return s + d[1]; }, 0);
    var goc = -90;
    var nhan = [];
    du.duLieu.forEach(function (d, k) {
      var a0 = goc, a1 = goc + 360 * d[1] / tong;
      goc = a1;
      var diem = [[TAM.x, TAM.y]].concat(duongCung(TAM.x, TAM.y, R, a0, a1), [[TAM.x, TAM.y]]);
      var l = B.net('lat-' + k, V.duongQua(diem, 80 + k), du.moc[k], 0.8, { quay: false, am: 'ting' });
      l.to = { a0: lam(a0), a1: lam(a1), mau: TO_LAT[k % TO_LAT.length] };
      kq.push(l);
      var giua = (a0 + a1) / 2 * Math.PI / 180;
      var phai = Math.cos(giua) >= 0;
      nhan.push({ k: k, phai: phai, giua: giua, y: TAM.y + (R + 24) * Math.sin(giua), chu: d[0] + ': {{' + phanTram(d[1], tong) + '}}%' });
    });
    xepNhan(nhan.filter(function (n) { return n.phai; }), K.o);
    xepNhan(nhan.filter(function (n) { return !n.phai; }), K.o);
    // Nhãn lát cách tâm 184 ngang, trải tới cách mép phải ô 20 (bên trái đối xứng); đường chỉ dừng trước nhãn 8.
    var rongNhan = K.o.w / 2 + 20 - 184;
    nhan.sort(function (a, b) { return a.k - b.k; });
    nhan.forEach(function (n) {
      var k = n.k;
      // Đường chỉ gấp khúc: ra theo bán kính rồi sang ngang tới nhãn.
      var tu = [TAM.x + (R + 6) * Math.cos(n.giua), TAM.y + (R + 6) * Math.sin(n.giua)];
      var khuy = [TAM.x + (R + 22) * Math.cos(n.giua), TAM.y + (R + 22) * Math.sin(n.giua)];
      var toi = [n.phai ? TAM.x + 176 : TAM.x - 176, n.y];
      kq.push(B.net('chi-' + k, V.duongQua([tu, khuy, toi], 90 + k), du.moc[k] + 0.5, 0.3, { quay: false }));
      kq.push(B.chu('nhan-' + k, n.chu, n.phai ? TAM.x + 184 : TAM.x - 184 - rongNhan, n.y - 15, rongNhan, 30, 22, du.moc[k] + 0.7,
        { can: n.phai ? 'trai' : 'phai', quay: false }));
    });
    return kq;
  }

  function duongTo(to, p) {
    if (to.a0 !== undefined) {
      var TAM = khung().TAM;
      var a1 = (to.a0 + (to.a1 - to.a0) * root.THI_DONG.easeInOut(p)) * Math.PI / 180;
      var a0 = to.a0 * Math.PI / 180;
      var lon = a1 - a0 > Math.PI ? 1 : 0;
      return 'M' + TAM.x + ' ' + TAM.y + ' L' + lam(TAM.x + R * Math.cos(a0)) + ' ' + lam(TAM.y + R * Math.sin(a0)) +
        ' A' + R + ' ' + R + ' 0 ' + lon + ' 1 ' + lam(TAM.x + R * Math.cos(a1)) + ' ' + lam(TAM.y + R * Math.sin(a1)) + ' Z';
    }
    var y = to.y0 + (to.y - to.y0) * root.THI_DONG.easeOutBack(p);
    return 'M' + to.x + ' ' + to.y0 + ' H' + lam(to.x + to.rong) + ' V' + lam(y) + ' H' + to.x + ' Z';
  }

  var canh = {
    thangSo: thangSo,
    thang: thang,
    muc: function (du) {
      var B = V.tao(du);
      var t = du.truong;
      var kieu = t.kieu[0];
      var kq = B.tieuDe(t['tieu-de'][0], 0.2);
      return kq.concat(kieu === 'tron' ? tron(B, du) : cotDuong(B, du, kieu, chuoiSo(du)));
    },
    // Phần tô màu (cột mọc từ trục, lát mở theo góc) nằm dưới nét vẽ, trên lưới; tính lại theo t.
    dung: function (goc, du) {
      var svg = goc.querySelector('svg.ve');
      var luoi = svg.querySelector('path.net.luoi');
      var sau = luoi ? luoi.nextSibling : svg.firstChild;
      goc.toMau = canh.muc(du).filter(function (m) { return m.to; }).map(function (m) {
        var el = document.createElementNS(NS, 'path');
        el.setAttribute('class', 'to-mau');
        el.style.fill = m.to.mau;
        svg.insertBefore(el, sau);
        return { m: m, el: el };
      });
    },
    capNhat: function (goc, du, t) {
      (goc.toMau || []).forEach(function (o) {
        var p = V.tienDo(t, o.m.batDau, o.m.thoiLuong);
        o.el.setAttribute('d', p > 0 ? duongTo(o.m.to, p) : 'M0 0');
      });
    }
  };
  root.THI_CANH['bieu-do'] = canh;
})(typeof globalThis !== 'undefined' ? globalThis : this);

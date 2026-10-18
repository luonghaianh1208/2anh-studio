(function (root) {
  'use strict';

  // Trang cảnh video ngắn "nhịp hình" (phong-cach: ngan; ngan.py dựng dữ liệu). Hợp đồng trang như vox.js:
  // THI_VIDEO.khoiDong(du) → datThoiDiem(t), THI_VIDEO.thoiDiemCuoi/kiemTran/suKien, THI_VIDEO.san = true.
  // Mọi thứ là hàm thuần của t (chụp từng khung, nhảy tới bất kỳ t nào cũng ra cùng hình). Không rung, không nảy:
  // vật vào bằng trượt và mờ dần, đường cong êm (easeOutCubic).
  //
  // Bố cục khổ dọc 720×1280 (điểm CSS): dải tiến độ trên cùng; nhãn chương y 44; nhãn tiêu đề y 92–250;
  // sân khấu x 40–680, y 280–1000; phụ đề (ASS, ngoài trang) quanh y 1060; đáy để trống cho thanh nút của ứng dụng.
  var SAN = { x: 40, y: 280, w: 640, h: 720 };
  var SAN_DAT = 990;          // mặt sàn nhân vật đứng (y bàn chân)
  var NV_TI = 1.32;           // tỉ lệ nhân vật (cao ~400)
  var BANG_CO_NV = { x: 40, y: 280, w: 640, h: 270 };   // ô chính khi cảnh có nhân vật: phần trên sân khấu
  var O_CO_DINH = {
    tren: { x: 40, y: 280, w: 640, h: 340 }, duoi: { x: 40, y: 640, w: 640, h: 340 },
    trai: { x: 40, y: 280, w: 310, h: 720 }, phai: { x: 370, y: 280, w: 310, h: 720 }
  };
  var VAO = 0.45;             // giây vật trượt vào
  var RA = 0.3;               // giây vật cũ mờ đi khi vật mới thay chỗ
  var SO_CHAY = 1.1;
  // Nền pastel đổi theo số cảnh (giao diện phang-sang).
  var NEN_SANG = ['#F6E3D5', '#E3F1E6', '#E5ECF8', '#FBEFD5', '#F3E1EC', '#E2F2F2'];
  var NHAN_SANG = ['#8E2B22', '#2F6B3E', '#2D4E8C', '#8A5A12', '#7A2E5C', '#1F6B6B'];

  function kep(x, a, b) { return x < a ? a : (x > b ? b : x); }
  function em(p) { p = kep(p, 0, 1); return 1 - Math.pow(1 - p, 3); }
  function lam(x) { return Math.round(x * 1000) / 1000; }
  function tao(the, lop, cha) { var el = document.createElement(the); if (lop) { el.className = lop; } if (cha) { cha.appendChild(el); } return el; }
  function datHop(el, b) { el.style.left = b.x + 'px'; el.style.top = b.y + 'px'; el.style.width = b.w + 'px'; el.style.height = b.h + 'px'; }
  function dinhDangSo(x, tp) {
    var s = x.toFixed(tp || 0).split('.');
    s[0] = s[0].replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    return s.join(',');
  }
  // "80,4%" → {so: 80.4, tp: 1, truoc: '', sau: '%'}; không có số → null.
  function tachSo(chu) {
    var m = /^(\D*?)(\d[\d.]*(?:,\d+)?)(.*)$/.exec(chu || '');
    if (!m) { return null; }
    var tho = m[2].replace(/\./g, '').replace(',', '.');
    var giaTri = Number(tho);
    if (!isFinite(giaTri)) { return null; }
    return { so: giaTri, tp: (tho.split('.')[1] || '').length, truoc: m[1], sau: m[3] };
  }
  function bieuTuongSvg(h, mau, co) {
    var s = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="' + h.viewBox + '" width="' + co + '" height="' + co +
      '" fill="none" stroke="' + mau + '" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">';
    h.phanTu.forEach(function (p) {
      s += '<' + p.the;
      Object.keys(p.thuocTinh).forEach(function (k) {
        if (k === 'stroke' || k === 'stroke-width' || k === 'class') { return; }
        s += ' ' + k + '="' + String(p.thuocTinh[k]).replace(/"/g, '&quot;') + '"';
      });
      s += '/>';
    });
    return s + '</svg>';
  }

  function khoiDong(du) {
    var khung = document.getElementById('khung');
    var sang = du.giaoDien !== 'toi-du-lieu';
    var mauNhan = sang ? NHAN_SANG[(du.so - 1) % NHAN_SANG.length] : '#E8704A';
    khung.className = 'ngan ' + (sang ? 'phang-sang' : 'toi-du-lieu');
    khung.style.setProperty('--nhan', mauNhan);
    if (sang) { khung.style.setProperty('--nen', NEN_SANG[(du.so - 1) % NEN_SANG.length]); }
    var lopNen = tao('div', 'nen', khung);
    if (sang) { tao('div', 'san-dat', lopNen); }
    var tienDo = tao('div', 'tien-do', khung);
    var dem = null;
    if (du.tongCanh) {
      dem = tao('div', 'dem', khung);
      dem.textContent = (du.so < 10 ? '0' : '') + du.so + ' / ' + (du.tongCanh < 10 ? '0' : '') + du.tongCanh;
    }
    if (du.loatTen) { tao('div', 'kenh', khung).textContent = du.loatTen; }
    var chuong = null, tieuDe = null;
    if (du.chuong) { chuong = tao('div', 'chuong', khung); chuong.textContent = du.chuong; }
    if (du.tieuDe) {
      tieuDe = tao('div', 'tieu-de' + (du.chuong ? ' co-chuong' : ''), khung);
      tao('span', 'chu-td', tieuDe).textContent = du.tieuDe;
    }
    var svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    var lopPhuDe = null;
    svg.setAttribute('class', 'lop-nv');
    svg.setAttribute('width', '720'); svg.setAttribute('height', '1280');
    var lopVat = tao('div', 'lop-vat', khung);
    khung.appendChild(svg);

    // ---- Nhân vật: mỗi vai một nhóm SVG, dòng thời gian tư thế từ các nhịp `nguoi`/`nhom`.
    var thuTuVai = [], dongTuThe = {}, oVai = {};
    du.nhip.forEach(function (n) {
      var ds = n.vat === 'nguoi' ? [n.moi] : (n.vat === 'nhom' ? n.moi.ds : []);
      ds.forEach(function (ng) {
        if (thuTuVai.indexOf(ng.vai) < 0) { thuTuVai.push(ng.vai); }
        (dongTuThe[ng.vai] = dongTuThe[ng.vai] || []).push({ t: n.batDau, tuThe: ng.tuThe });
        if (n.vat === 'nguoi' && n.o && !oVai[ng.vai]) { oVai[ng.vai] = n.o; }
      });
    });
    var X_THEO_SO = { 1: [360], 2: [210, 510], 3: [150, 360, 570], 4: [120, 280, 440, 600] };
    var xMacDinh = X_THEO_SO[Math.min(thuTuVai.length, 4)] || [];
    var X_O = { trai: 200, giua: 360, phai: 520 };
    var cacNv = thuTuVai.map(function (vai, i) {
      var x = X_O[oVai[vai]] !== undefined ? X_O[oVai[vai]] : (xMacDinh[i] !== undefined ? xMacDinh[i] : 360);
      var g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
      svg.appendChild(g);
      var nhom = document.createElementNS('http://www.w3.org/2000/svg', 'g');
      g.appendChild(nhom);
      return { vai: vai, x: x, lat: x > 380, g: g, trong: nhom, ds: dongTuThe[vai], nv: du.vai[vai] };
    });
    var coNv = cacNv.length > 0;

    // ---- Vật (không phải nhân vật): ô chính (`n.o` trống) hoặc ô cố định; vật sau cùng ô thay vật trước.
    var cacVat = [];
    var theoO = {};
    du.nhip.forEach(function (n, k) {
      if (n.vat === 'nguoi' || n.vat === 'nhom') { return; }
      var tenO = n.o && O_CO_DINH[n.o] ? n.o : 'chinh';
      var b = tenO === 'chinh' ? (coNv ? BANG_CO_NV : SAN) : O_CO_DINH[tenO];
      var el = tao('div', 'vat vat-' + n.vat, lopVat);
      datHop(el, b);
      var v = { n: n, k: k, el: el, b: b, o: tenO, noi: tao('div', 'noi', el), het: null };
      dung(v);
      if (theoO[tenO]) { theoO[tenO].het = n.batDau; }
      theoO[tenO] = v;
      cacVat.push(v);
    });

    // ---- Phụ đề trong trang: mỗi lúc một dòng, căn giữa, từ khoá theo dấu nhấn của lời (ngan.phu_de).
    var cacDong = [];
    lopPhuDe = tao('div', 'phu-de', khung);
    var demNhan = 0;
    (du.phuDe || []).forEach(function (d) {
      var el = tao('div', 'dong-pd', lopPhuDe);
      var ds = [];
      var cumTruoc = null, khoi = null;
      d.chu.forEach(function (w, i) {
        // Từ cùng một cụm nhấn chung một khối (khoanh, gạch, tô bao trọn cả cụm).
        if (w.kieu && w.cum === cumTruoc && khoi) {
          khoi.chu.appendChild(document.createTextNode(' '));
        } else {
          if (i > 0) { el.appendChild(document.createTextNode(' ')); }
          var lop = 'tu-pd' + (w.kieu ? ' kw kw-' + w.kieu : '');
          if (w.kieu === 'nhan') { lop += (demNhan++ % 2) ? ' kw-viet' : ' kw-dam'; }
          var span = tao('span', lop, el);
          khoi = { el: span, chu: tao('span', 'kw-chu', span), kieu: w.kieu, t: w.t, tu: [] };
          if (w.kieu === 'khoanh') {
            khoi.vong = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
            khoi.vong.setAttribute('class', 'vong');
            khoi.vong.setAttribute('viewBox', '0 0 100 40');
            khoi.vong.setAttribute('preserveAspectRatio', 'none');
            khoi.vong.innerHTML = '<path d="M8 22 C 6 6, 70 2, 92 14 C 102 22, 82 38, 46 37 C 18 36, 2 30, 10 16" pathLength="1"/>';
            span.appendChild(khoi.vong);
          }
          if (w.kieu === 'gach') { khoi.gach = tao('span', 'gach', span); }
          ds.push(khoi);
          cumTruoc = w.kieu ? w.cum : null;
        }
        var tw = tao('span', 'chu-pd', khoi.chu);
        tw.textContent = w.chu;
        khoi.tu.push({ el: tw, t: w.t });
      });
      // Mốc kết thúc của từ cuối mỗi khối = mốc của khối kế tiếp (để chỉ một từ "đang đọc" mỗi lúc).
      ds.forEach(function (k, i) { k.het = i + 1 < ds.length ? ds[i + 1].t : d.den; });
      cacDong.push({ el: el, tu: d.tu, den: d.den, khoi: ds });
    });
    // Dòng quá rộng: thu nhỏ cả dòng cho vừa 660 (đo một lần, kết quả cố định theo chữ).
    function doPhuDe() {
      cacDong.forEach(function (d) {
        d.el.style.visibility = 'hidden'; d.el.style.display = 'block'; d.el.style.transform = '';
        var w = d.el.offsetWidth;
        d.ti = w > 660 ? 660 / w : 1;
        d.el.style.display = 'none';
      });
    }

    function datPhuDe(t) {
      cacDong.forEach(function (d) {
        var p = (t - d.tu) / 0.16;
        if (t < d.tu - 1e-6 || t >= d.den) { d.el.style.display = 'none'; return; }
        d.el.style.display = 'block';
        d.el.style.visibility = 'visible';
        var e = em(p);
        d.el.style.opacity = e >= 1 ? '' : String(lam(e));
        d.el.style.transform = 'translateX(-50%) translateY(' + lam(10 * (1 - e)) + 'px)' + (d.ti < 1 ? ' scale(' + lam(d.ti) + ')' : '');
        d.khoi.forEach(function (k) {
          k.tu.forEach(function (x, i) {
            var het = i + 1 < k.tu.length ? k.tu[i + 1].t : k.het;
            var dang = t >= x.t - 1e-6 && t < het;
            x.el.className = 'chu-pd' + (t >= x.t - 1e-6 ? ' da' : '') + (dang && !k.kieu ? ' dang' : '');
          });
          var q = (t - k.t) / 0.4;
          if (k.vong) { k.vong.firstChild.style.strokeDashoffset = String(lam(1 - em(q))); }
          if (k.gach) { k.gach.style.transform = 'scaleX(' + lam(em(q)) + ')'; }
          if (k.kieu) { k.el.className = k.el.className.replace(/ bat$/, '') + (t >= k.t - 1e-6 ? ' bat' : ''); }
        });
      });
    }

    function dung(v) {
      var n = v.n, noi = v.noi, m = n.moi || {};
      if (n.vat === 'chu') { noi.textContent = n.chu; }
      else if (n.vat === 'nhan') { tao('span', 'nhan', noi).textContent = n.chu; }
      else if (n.vat === 'dau') { tao('span', 'dau', noi).textContent = n.chu; }
      else if (n.vat === 'so') {
        var s = n.so;
        if (s.truoc) { tao('div', 'so-phu', noi).textContent = s.truoc; }
        v.soEl = tao('div', 'so-lon', noi);
        if (s.sau) { tao('div', 'so-phu', noi).textContent = s.sau; }
      } else if (n.vat === 'the') {
        var th = tao('div', 'the', noi);
        tao('div', 'the-nhan', th).textContent = n.the.nhan;
        tao('div', 'the-gia-tri', th).textContent = n.the.giaTri;
        if (n.the.chuThich) { tao('div', 'the-chu-thich', th).textContent = n.the.chuThich; }
      } else if (n.vat === 'bieu-tuong') {
        var bt = tao('div', 'bieu-tuong', noi);
        bt.innerHTML = bieuTuongSvg(m.hinh, 'var(--nhan)', Math.min(v.b.h - (m.nhan ? 70 : 20), 230));
        if (m.nhan) { tao('div', 'bt-nhan', noi).textContent = m.nhan; }
      } else if (n.vat === 'luoi-cham') {
        var cot = m.tong <= 30 ? 6 : (m.tong <= 100 ? 10 : 20);
        var hang = Math.ceil(m.tong / cot);
        var co = Math.floor(Math.min((v.b.w - 40) / cot, (v.b.h - 90) / hang)) - 6;
        co = kep(co, 8, 44);
        var luoi = tao('div', 'luoi', noi);
        luoi.style.gridTemplateColumns = 'repeat(' + cot + ', ' + co + 'px)';
        v.cham = [];
        for (var i = 0; i < m.tong; i++) {
          var c = tao('span', 'cham', luoi);
          c.style.width = c.style.height = co + 'px';
          v.cham.push(c);
        }
        if (m.chuThich) { tao('div', 'chu-thich', noi).textContent = m.chuThich; }
      } else if (n.vat === 'truoc-sau') {
        var hang2 = tao('div', 'truoc-sau', noi);
        var a = tao('div', 'ts-cot ts-truoc', hang2);
        tao('div', 'ts-gia-tri' + (Math.max(m.truoc.length, m.sau.length) > 5 ? ' dai' : ''), a).textContent = m.truoc;
        if (m.nhanTruoc) { tao('div', 'ts-nhan', a).textContent = m.nhanTruoc; }
        v.muiTen = tao('div', 'ts-mui', hang2);
        v.muiTen.textContent = '→';
        var b2 = tao('div', 'ts-cot ts-sau', hang2);
        v.sauEl = tao('div', 'ts-gia-tri' + (Math.max(m.truoc.length, m.sau.length) > 5 ? ' dai' : ''), b2);
        v.sauEl.textContent = m.sau;
        v.sauSo = tachSo(m.sau);
        if (m.nhanSau) { tao('div', 'ts-nhan', b2).textContent = m.nhanSau; }
      } else if (n.vat === 'tin-nhan') {
        var vo = (n.tuyChon || []).indexOf('dien-thoai') >= 0 ? tao('div', 'dien-thoai', noi) : noi;
        v.bong = m.ds.map(function (tn) { var bo = tao('div', 'bong ' + tn.ai, vo); bo.textContent = tn.chu; return bo; });
      } else if (n.vat === 'thong-bao') {
        var tb = tao('div', 'thong-bao', noi);
        tao('div', 'tb-app', tb).textContent = m.ungDung;
        tao('div', 'tb-tieu-de', tb).textContent = m.tieuDe;
        tao('div', 'tb-noi-dung', tb).textContent = m.noiDung;
      } else if (n.vat === 'trich-dan') {
        var td = tao('div', 'trich-dan', noi);
        tao('div', 'td-ngoac', td).textContent = '“';
        tao('div', 'td-cau', td).textContent = m.cau;
        if (m.ai) { tao('div', 'td-ai', td).textContent = '— ' + m.ai; }
      } else if (n.ds) {
        dungDanhSach(v, n.ds);
      }
    }

    function dungDanhSach(v, ds) {
      var n = v.n, noi = v.noi;
      v.muc = [];
      if (n.vat === 'cot') {
        var max = Math.max.apply(null, ds.map(function (m) { return m.giaTri; })) || 1;
        var bd = tao('div', 'bieu-do', noi);
        ds.forEach(function (m) {
          var c = tao('div', 'cot', bd);
          var so = tao('div', 'cot-so', c);
          var than = tao('div', 'cot-than', c);
          tao('div', 'cot-nhan', c).textContent = m.nhan;
          v.muc.push({ el: c, than: than, so: so, ti: m.giaTri / max, m: m });
        });
      } else {
        var lop = n.vat === 'moc' ? 'ds-moc' : (n.vat === 'thap' ? 'ds-thap' : 'ds-buoc');
        var dsEl = tao('div', 'danh-sach ' + lop, noi);
        ds.forEach(function (m, i) {
          var dong = tao('div', 'muc', dsEl);
          if (n.vat === 'moc') { tao('span', 'muc-moc', dong).textContent = m.moc; }
          else if (n.vat === 'chu-trinh') { tao('span', 'muc-so', dong).textContent = String(i + 1); }
          tao('span', 'muc-chu', dong).textContent = m.nhan;
          if (n.vat === 'thap') { dong.style.width = (46 + 54 * (i + 1) / ds.length) + '%'; }
          v.muc.push({ el: dong });
        });
      }
    }

    // ---- Vẽ theo t.
    function hien(el, p, dx, dy) {
      if (p <= 0) { el.style.visibility = 'hidden'; el.style.opacity = '0'; return false; }
      el.style.visibility = 'visible';
      var e = em(p);
      el.style.opacity = e >= 1 ? '' : String(lam(e));
      el.style.transform = e >= 1 ? '' : 'translate(' + lam(dx * (1 - e)) + 'px,' + lam(dy * (1 - e)) + 'px)';
      return true;
    }

    function datVat(v, t) {
      var n = v.n, p = (t - n.batDau) / VAO;
      var tat = v.het !== null ? (t - v.het) / RA : 0;
      if (tat >= 1) { v.el.style.visibility = 'hidden'; v.el.style.opacity = '0'; return; }
      if (!hien(v.el, p, 0, 40)) { return; }
      if (tat > 0) { v.el.style.opacity = String(lam(1 - em(tat))); }
      var q = t - n.batDau;
      var m = n.moi || {};
      if (n.vat === 'so' && v.soEl) {
        var u = em(q / SO_CHAY);
        v.soEl.textContent = dinhDangSo(u >= 1 ? n.so.giaTri : n.so.giaTri * u, n.so.thapPhan);
      } else if (n.vat === 'luoi-cham') {
        var bat = Math.round(m.sang * em(q / 1.4));
        v.cham.forEach(function (c, i) { c.className = i < bat ? 'cham sang' : 'cham'; });
      } else if (n.vat === 'truoc-sau') {
        var pm = kep((q - 0.5) / 0.35, 0, 1);
        v.muiTen.style.opacity = String(lam(pm));
        var ps = kep((q - 0.8) / 0.4, 0, 1);
        v.sauEl.parentNode.style.opacity = String(lam(em(ps)));
        if (v.sauSo) {
          var us = em((q - 0.8) / SO_CHAY);
          v.sauEl.textContent = v.sauSo.truoc + dinhDangSo(us >= 1 ? v.sauSo.so : v.sauSo.so * us, v.sauSo.tp) + v.sauSo.sau;
        }
      } else if (n.vat === 'tin-nhan') {
        v.bong.forEach(function (b, i) { hien(b, (q - i * 0.7) / 0.35, 0, 18); });
      } else if (n.vat === 'bieu-tuong') {
        var e = em(q / 0.5);
        v.noi.style.transform = e >= 1 ? '' : 'scale(' + lam(0.88 + 0.12 * e) + ')';
      } else if (v.muc) {
        var k = v.muc.length;
        v.muc.forEach(function (mc, i) {
          var pi = kep((q - i * 0.35) / 0.4, 0, 1);
          if (n.vat === 'cot') {
            mc.el.style.opacity = pi > 0 ? '' : '0';
            mc.than.style.height = lam(mc.ti * em(pi) * 100) + '%';
            mc.so.textContent = dinhDangSo(mc.m.giaTri * em(pi), mc.m.thapPhan) + (mc.m.donVi || '');
          } else {
            hien(mc.el, n.vat === 'thap' ? kep((q - (k - 1 - i) * 0.35) / 0.4, 0, 1) : pi, 0, 14);
          }
        });
      }
    }

    function tuTheTai(nv, t) {
      var dang = null;
      nv.ds.forEach(function (d) { if (d.t <= t + 1e-6) { dang = d; } });
      return dang;
    }

    function datNv(nv, t) {
      var dau = nv.ds[0].t;
      var p = (t - dau) / VAO;
      if (p <= 0) { nv.g.setAttribute('visibility', 'hidden'); return; }
      nv.g.setAttribute('visibility', 'visible');
      var e = em(p);
      var dx = (nv.lat ? 1 : -1) * 60 * (1 - e);
      nv.g.setAttribute('opacity', e >= 1 ? '1' : String(lam(e)));
      nv.g.setAttribute('transform', 'translate(' + lam(nv.x + dx) + ' ' + SAN_DAT + ')');
      var d = tuTheTai(nv, t);
      var dangVe = root.THI_NHAN_VAT.dang(d.tuThe, Math.max(0, t - d.t));
      nv.trong.setAttribute('transform', 'scale(' + (nv.lat ? -NV_TI : NV_TI) + ' ' + NV_TI + ')');
      nv.trong.innerHTML = root.THI_NHAN_VAT_PHANG.ve(dangVe, nv.nv);
    }

    function dat(t) {
      var tong = du.tongVideo || du.thoiLuong;
      tienDo.style.width = lam(kep(((du.batDauVideo || 0) + t) / tong, 0, 1) * 100) + '%';
      // Chuyển cảnh: cả khung trượt nhẹ từ phải và rõ dần trong 0,35 s đầu cảnh (cảnh 1 không chuyển).
      var pc = du.co && du.co.chuyen ? em(t / 0.35) : 1;
      khung.style.opacity = pc >= 1 ? '' : String(lam(0.25 + 0.75 * pc));
      lopVat.style.transform = svg.style.transform = pc >= 1 ? '' : 'translateX(' + lam(60 * (1 - pc)) + 'px)';
      if (tieuDe) { hien(tieuDe, (t - 0.05) / 0.4, 0, -20); }
      if (chuong) { hien(chuong, t / 0.3, 0, -10); }
      cacNv.forEach(function (nv) { datNv(nv, t); });
      cacVat.forEach(function (v) { datVat(v, t); });
      datPhuDe(t);
    }

    function thoiDiemCuoi() { return du.thoiLuong - 1 / 30; }
    root.datThoiDiem = function (t) { dat(t); };

    function tran(el) { return el.scrollWidth > el.clientWidth + 1 || el.scrollHeight > el.clientHeight + 1; }
    function kiemTran() {
      var loi = [];
      cacVat.forEach(function (v) {
        // Kiểm từng vật ở lúc nó hiện rõ (vật thay chỗ đã ẩn ở cuối cảnh).
        dat(Math.min(v.n.batDau + 2.5, thoiDiemCuoi()));
        v.el.style.visibility = 'visible'; v.el.style.opacity = '1'; v.el.style.transform = '';
        if (tran(v.noi) || tran(v.el)) { loi.push('nhip-' + v.k); }
        var b = v.el.getBoundingClientRect(), c = v.noi.getBoundingClientRect();
        if (c.left < b.left - 2 || c.right > b.right + 2 || c.top < b.top - 2 || c.bottom > b.bottom + 2) {
          if (loi.indexOf('nhip-' + v.k) < 0) { loi.push('nhip-' + v.k); }
        }
      });
      dat(thoiDiemCuoi());
      if (tieuDe && tieuDe.getBoundingClientRect().bottom > SAN.y + 4) { loi.push('tieu-de'); }
      return loi;
    }

    // Tiếng hiệu ứng theo loại vật (am_thanh.py): vút khi vật/nhân vật lướt vào, bụp khi đổi tư thế, pop cho bong bóng
    // và biểu tượng, tích tích khi số chạy/chấm sáng, ding cho thông báo, tiếng đóng dấu cho con dấu.
    var TIENG = { nguoi: 'vut', nhom: 'vut', the: 'vut', 'trich-dan': 'vut', 'truoc-sau': 'vut', 'bieu-tuong': 'pop',
      so: 'dem', 'luoi-cham': 'dem', 'thong-bao': 'ding', dau: 'nhan', cot: 'pop', moc: 'pop', 'chu-trinh': 'pop',
      thap: 'pop', chu: 'ting', nhan: 'ting' };
    function suKien() {
      var ds = [];
      if (du.co && du.co.chuyen) { ds.push({ t: 0, loai: 'chuyen', dai: 0.6 }); }
      var daCo = {};
      du.nhip.forEach(function (n) {
        var dauCanh = n.batDau <= (du.danDau || 0) + 0.01;
        if (n.vat === 'nguoi') {
          // Nhân vật đã lên sân khấu: đổi tư thế kêu "bụp"; lần đầu kêu "vút" (trừ khi vào cùng lúc mở cảnh).
          var cu = daCo[n.moi.vai];
          daCo[n.moi.vai] = true;
          if (cu) { ds.push({ t: n.batDau, loai: 'bup', dai: 0.2 }); return; }
        }
        if (n.vat === 'nhom') { n.moi.ds.forEach(function (x) { daCo[x.vai] = true; }); }
        if (dauCanh) { return; }
        if (n.vat === 'tin-nhan') {
          n.moi.ds.forEach(function (_, i) { ds.push({ t: n.batDau + i * 0.7, loai: 'pop', dai: 0.15 }); });
          return;
        }
        ds.push({ t: n.batDau, loai: TIENG[n.vat] || 'ting', dai: 0.2 });
      });
      return ds;
    }

    root.THI_VIDEO.thoiDiemCuoi = thoiDiemCuoi;
    root.THI_VIDEO.kiemTran = kiemTran;
    root.THI_VIDEO.suKien = suKien;
    var chu = document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve();
    // Nhãn tiêu đề dài (2 dòng chữ hoa) có thể chạm sân khấu: thu nhỏ chữ dần (tối thiểu 30) cho vừa trên y SAN.y − 8.
    function vuaTieuDe() {
      if (!tieuDe) { return; }
      var co = parseFloat(getComputedStyle(tieuDe).fontSize);
      while (tieuDe.getBoundingClientRect().bottom > SAN.y - 8 && co > 30) {
        co -= 3;
        tieuDe.style.fontSize = co + 'px';
      }
    }
    // Vật to hơn ô (chữ dài, nhiều mục): thu cả vật bằng `zoom` cho vừa ô (tối thiểu 0,55); còn tràn thì kiemTran báo.
    function vuaVat() {
      cacVat.forEach(function (v) {
        v.el.style.visibility = 'visible';
        var sw = v.noi.scrollWidth, sh = v.noi.scrollHeight;
        var k = Math.min(1, (v.b.w - 8) / sw, (v.b.h - 8) / sh);
        if (k < 1) { v.noi.style.zoom = String(Math.max(0.55, Math.floor(k * 100) / 100)); }
      });
    }
    chu.then(function () { vuaTieuDe(); vuaVat(); doPhuDe(); dat(0); root.THI_VIDEO.san = true; });
  }

  root.THI_NGAN = { tachSo: tachSo, dinhDangSo: dinhDangSo, em: em, SAN: SAN };
  // Luôn là đối tượng mới (page.set_content giữ nguyên window).
  root.THI_VIDEO = { khoiDong: khoiDong, san: false };
})(typeof globalThis !== 'undefined' ? globalThis : this);

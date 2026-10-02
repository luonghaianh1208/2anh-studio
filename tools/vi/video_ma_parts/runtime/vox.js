(function (root) {
  'use strict';

  // Cảnh Vox (`phong-cach: vox`): cắt dán giấy xé nhiều lớp. Ba lớp sâu (nền xa, ảnh ở giữa, chữ ở gần) trôi ngang
  // lệch nhau rất chậm (lopCamera); không phóng, không xoay, không rung. Mọi khung là hàm thuần của t (`datThoiDiem`);
  // ngẫu nhiên lấy từ THI_CAT_DAN.prng theo hạt cảnh. Ảnh đã có viền xé và bóng đổ trong PNG (anh_vox.py), nên trang
  // không thêm filter nào theo khung, trừ nhoè hướng 0,35 giây đầu của chuyển `lia`. Không lớp nào đổi tỉ lệ bằng
  // transform: Chromium vẽ lớp đổi tỉ lệ qua bộ đệm của các khung trước, khung sẽ phụ thuộc lịch sử vẽ.
  // Phần trên `khoiDong` là hàm thuần (chạy được trong Node, test ở tests/js/test_vox.js).
  var NS = 'http://www.w3.org/2000/svg';
  var CHUYEN = 0.35;
  // Vật vào êm: trượt ngắn kèm mờ dần, không nảy, không rung (chủ repo: rung gây nhức mắt).
  var DAI = { 'anh-cat': 0.5, 'anh-khung': 0.5, 'anh-phu': 0.6, the: 0.5, nhan: 0.4, dau: 0.4, chu: 0.5, so: 0.5, 'mui-ten': 0.5 };
  var SO_CHAY = 1.2;
  var CHU_LON = 72, CHU_NHO = 34;
  var THE_RONG = 460;
  var VUNG = { ngang: { x0: 60, x1: 1220, y0: 60, y1: 600 }, doc: { x0: 40, x1: 680, y0: 120, y1: 1040 } };

  function C() { return root.THI_CAT_DAN; }
  function kep(x, a, b) { return x < a ? a : (x > b ? b : x); }
  // Cộng 0 để không bao giờ trả -0 (assert.strictEqual của Node phân biệt).
  function so(x) { return x + 0; }
  function lam(x) { return Math.round(x * 1000) / 1000 + 0; }
  function easeOutCubic(p) { return 1 - Math.pow(1 - p, 3); }
  function day(kho) { return kho.day || (kho.ten === 'doc' ? 1080 : 620); }

  function bangO() {
    return root.THI_O_BO_CUC || (typeof module === 'object' && module.exports ? require('./o-bo-cuc.json') : {});
  }
  function oCua(boCuc, o, kho) {
    var b = (bangO()[kho.ten] || {})['vox-' + boCuc + '-' + o];
    if (!b) { throw new Error('Ô `' + o + '` của bố cục `' + boCuc + '` không có ở khổ ' + kho.ten + '.'); }
    return { x: b.x, y: b.y, w: b.w, h: b.h };
  }

  // Bố cục `chong`: n ô so le dọc theo chiều dài của khổ (cột ở khổ ngang, hàng ở khổ dọc), mỗi ô rộng hơn phần
  // chia 30 % để các vật chồng mép lên nhau, lệch ±40 px và xoay ±8° theo hạt; kẹp trong vùng nội dung.
  function xepChong(k, n, hat, kho) {
    var r = C().prng(hat * 31 + k);
    var v = VUNG[kho.ten] || VUNG.ngang;
    var W = v.x1 - v.x0, H = v.y1 - v.y0;
    var doc = kho.ten === 'doc';
    var phan = (doc ? H : W) / n;
    var w, h, x, y;
    if (!doc) {
      w = Math.min(W * 0.62, phan * 1.3);
      h = Math.min(H * 0.62, w * 1.15);
      x = v.x0 + phan * (k + 0.5) - w / 2;
      y = v.y0 + (n === 1 ? (H - h) / 2 : (k % 2 ? H - h : 0));
    } else {
      h = Math.min(H * 0.5, phan * 1.3);
      w = Math.min(W * 0.82, h * 1.6);
      y = v.y0 + phan * (k + 0.5) - h / 2;
      x = v.x0 + (n === 1 ? (W - w) / 2 : (k % 2 ? W - w : 0));
    }
    x += (r() * 2 - 1) * 40;
    y += (r() * 2 - 1) * 40;
    var goc = (r() * 2 - 1) * 8;
    x = kep(x, v.x0, v.x1 - w);
    y = kep(y, v.y0, v.y1 - h);
    return { x: Math.round(x) + 0, y: Math.round(y) + 0, w: Math.round(w), h: Math.round(h), goc: lam(goc) };
  }

  // Kiểu vào của vật ở tiến độ p (0..1). Ở p = 1 luôn đúng chỗ: {dx 0, dy 0, s 1, goc cuối, a 1}.
  function vao(vat, p) {
    var gocCuoi = vat === 'dau' ? -4 : 0;
    if (p >= 1) { return { dx: 0, dy: 0, s: 1, goc: gocCuoi, a: 1 }; }
    p = kep(p, 0, 1);
    var e = easeOutCubic(p);
    var kq = { dx: 0, dy: 0, s: 1, goc: gocCuoi, a: Math.min(1, p * 2) };
    if (vat === 'anh-cat' || vat === 'anh-khung') {
      kq.dy = 36 * (1 - e);
    } else if (vat === 'anh-phu') {
      kq.a = p;
    } else if (vat === 'the') {
      kq.dx = 40 * (1 - e);
    } else if (vat === 'nhan') {
      kq.dx = -30 * (1 - e);
    } else if (vat === 'dau') {
      kq.s = 1.15 - 0.15 * e;
    } else {
      kq.dy = 18 * (1 - e);
    }
    return { dx: lam(kq.dx), dy: lam(kq.dy), s: lam(kq.s), goc: lam(kq.goc), a: lam(kq.a) };
  }

  // Chuyển động máy quay của Vox rất nhẹ: không phóng, không xoay, không rung. Chỉ có thị sai trôi ngang chậm suốt
  // cảnh: nền (lớp xa) trôi ±TROI.xa điểm CSS, ảnh (lớp giữa) trôi ít hơn, chữ (lớp gần) đứng yên. Độ dời theo bước
  // điểm ảnh thiết bị `dpr`, nên khung là hàm thuần của t.
  var TROI = { xa: 14, giua: 5, gan: 0 };
  var LE_NEN = 16;       // nền nướng rộng hơn khung mỗi phía LE_NEN điểm CSS để khi trôi không hở mép
  function lopCamera(ten, cam, dpr) {
    var k = dpr || 1;
    return { x: Math.round(TROI[ten] * (1 - 2 * cam.u) * k) / k + 0, y: 0 };
  }
  function camera(t, T) {
    return { u: T > 0 ? kep(t / T, 0, 1) : 1 };
  }

  // Chuyển lia: cảnh trước trượt hết bề ngang khung (ease in-out), nhoè hướng mạnh nhất giữa chừng.
  function chuyenLia(p, kho) {
    p = kep(p, 0, 1);
    var e = p < 0.5 ? 2 * p * p : 1 - 2 * (1 - p) * (1 - p);
    return { dx: -kho.rong * e + 0, mo: lam(Math.sin(Math.PI * p) * 24) };
  }

  // Định dạng số chạy: hàng nghìn dấu chấm, thập phân dấu phẩy.
  function dinhDangSo(x, thapPhan) {
    var am = x < 0;
    var s = Math.abs(x).toFixed(thapPhan || 0);
    var phan = s.split('.');
    var nguyen = phan[0].replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    return (am ? '-' : '') + nguyen + (phan[1] ? ',' + phan[1] : '');
  }

  // ---------- Trang ----------

  function tao(the, lop, cha) {
    var el = document.createElement(the);
    if (lop) { el.className = lop; }
    if (cha) { cha.appendChild(el); }
    return el;
  }
  function vatCua(n) {
    if (n.vat === 'anh') {
      var kieu = n.anh && n.anh.kieu;
      if (n.o === 'nen' || kieu === 'phu') { return 'anh-phu'; }
      return kieu === 'khung' ? 'anh-khung' : 'anh-cat';
    }
    return n.vat;
  }
  // Ảnh vừa ô (contain), căn giữa; có dòng nguồn thì chừa 20 px dưới ảnh cho dòng đó.
  function vuaO(o, rong, cao, chua) {
    var h0 = o.h - chua;
    var k = Math.min(o.w / rong, h0 / cao);
    var w = rong * k, h = cao * k;
    return { x: o.x + (o.w - w) / 2, y: o.y + (h0 - h) / 2, w: w, h: h };
  }
  // Phủ kín khung, thừa 2 % mỗi phía để lớp xa dời theo camera (tối đa ~10 px) không hở mép.
  function phuKin(rong, cao, kho) {
    var k = Math.max(kho.rong / rong, kho.cao / cao) * 1.04;
    return { x: (kho.rong - rong * k) / 2, y: (kho.cao - cao * k) / 2, w: rong * k, h: cao * k };
  }
  // Hộp ảnh bitmap khớp lưới điểm ảnh thiết bị: ảnh nướng cùng cỡ, đặt 1:1 ở tỉ lệ 1 (zoom đẩy vào dàn trang lại ở
  // tỉ lệ mới, không qua bộ đệm tỉ lệ), không lọc (khung không phụ thuộc lịch sử vẽ).
  function luoi(b) {
    var k = (typeof root.devicePixelRatio === 'number' && root.devicePixelRatio) || 1;
    function g(x) { return Math.round(x * k) / k + 0; }
    var x0 = g(b.x), y0 = g(b.y);
    return { x: x0, y: y0, w: g(b.x + b.w) - x0, h: g(b.y + b.h) - y0 };
  }
  function datHop(el, b) {
    el.style.left = b.x + 'px'; el.style.top = b.y + 'px';
    el.style.width = b.w + 'px'; el.style.height = b.h + 'px';
  }
  function svgManh(points, mau, lopPhu, them) {
    return '<polygon points="' + points + '" fill="rgba(0,0,0,0.16)" transform="translate(3 5)"/>' +
      '<polygon points="' + points + '" style="fill:' + mau + '"/>' +
      (lopPhu ? '<polygon points="' + points + '" fill="url(#' + lopPhu + ')"' + (them || '') + '/>' : '');
  }

  // Lớp xa (trả hai chuỗi SVG: giấy, mảng): nền giấy của bảng màu và 3–5 mảng giấy xé lớn màu bảng (chấm halftone, kẻ ô hay sọc), nửa trong nửa ngoài.
  function nenXa(hat, kho, mau) {
    var R = kho.rong, H = kho.cao;
    var r = C().prng(hat * 977 + 11);
    var s = C().nenGiay(hat, kho, mau.giay);
    var n = 3 + Math.floor(r() * 3);
    var g = '<svg xmlns="' + NS + '" class="manh-xa" width="' + R + '" height="' + H + '" viewBox="0 0 ' + R + ' ' + H + '">' +
      '<defs>' + C().chamLuoi('vox-cham', 12, 2.6, 'rgba(0,0,0,0.32)') +
      '<pattern id="vox-ke" width="24" height="24" patternUnits="userSpaceOnUse"><path d="M24 0H0V24" fill="none" ' +
      'stroke="rgba(30,40,60,0.28)" stroke-width="1.5"/></pattern>' +
      '<pattern id="vox-soc" width="22" height="22" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">' +
      '<rect width="9" height="22" fill="rgba(255,255,255,0.28)"/></pattern></defs>';
    var phu = ['vox-cham', null, 'vox-soc', 'vox-ke', 'vox-cham'];
    // Ô neo: bốn góc và hai cạnh; mỗi mảng 34–52 % bề ngang, 36–54 % bề cao, 40–70 % nằm trong khung.
    var neo = [[0, 0], [1, 0], [0, 1], [1, 1], [0.5, 0], [0.5, 1]];
    for (var i = neo.length - 1; i > 0; i--) { var j = Math.floor(r() * (i + 1)); var tam = neo[i]; neo[i] = neo[j]; neo[j] = tam; }
    for (var k = 0; k < n; k++) {
      var w = R * (0.34 + 0.18 * r()), h = H * (0.36 + 0.18 * r());
      var trong = 0.4 + 0.3 * r();
      var x = neo[k][0] === 0.5 ? R * (0.25 + 0.5 * r()) - w / 2 : (neo[k][0] ? R - trong * w : -(1 - trong) * w);
      var y = neo[k][1] ? H - trong * h : -(1 - trong) * h;
      var pts = C().giayXe(hat * 50 + k, x, y, w, h, 6);
      g += svgManh(pts, mau.manh[(k + hat) % 4], phu[(k + hat) % phu.length]);
    }
    return [s, g + '</svg>'];
  }
  // Lớp giữa: 1–2 mảng giấy xé nhỏ (giấy kẻ ô sáng hoặc màu nhấn) ở vùng giữa khung.
  function manhGiua(hat, kho, mau) {
    var R = kho.rong, H = kho.cao;
    var r = C().prng(hat * 389 + 5);
    var n = 1 + Math.floor(r() * 2);
    var g = '<svg xmlns="' + NS + '" class="manh-giua" width="' + R + '" height="' + H + '" viewBox="0 0 ' + R + ' ' + H + '">' +
      '<defs><pattern id="vox-ke2" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M20 0H0V20" fill="none" ' +
      'stroke="rgba(40,70,100,0.3)" stroke-width="1.2"/></pattern></defs>';
    for (var k = 0; k < n; k++) {
      var w = R * (0.22 + 0.12 * r()), h = H * (0.22 + 0.12 * r());
      var x = R * (0.15 + 0.6 * r()) - w / 2, y = H * (0.2 + 0.55 * r()) - h / 2;
      var giay = k === 0;
      g += svgManh(C().giayXe(hat * 90 + k, x, y, w, h, 5), giay ? mau.ke : mau.manh[(hat + k + 1) % 4],
        giay ? 'vox-ke2' : null);
    }
    return g + '</svg>';
  }

  function khoiDong(du) {
    var khung = document.getElementById('khung');
    var kho = root.THI_KHO.lay();
    var hat = du.hat || du.so || 1;
    var cacNhip = du.nhip || [];
    var co = du.co || {};
    var boCuc = du.boCuc;
    khung.classList.add('vox');
    khung.classList.add('bang-' + (du.bangMau || 'kem'));
    var cs = getComputedStyle(khung);
    // Màu bảng đọc từ vox.css (một nguồn); nền xa là ảnh SVG riêng, không thấy biến CSS của trang nên cần màu thật.
    function bien(ten, macDinh) { return cs.getPropertyValue(ten).trim() || macDinh; }
    var mau = { giay: bien('--giay', '#F4ECD8'), ke: bien('--ke', '#EFE8D6'),
      manh: [bien('--manh1', '#2E86AB'), bien('--manh2', '#F2A541'), bien('--manh3', '#3B8B5A'), bien('--manh4', '#C8553D')] };

    // Sân khấu: .khung-3d (chỉ dời khi chuyển lia) > ba lớp phẳng xa / giữa / gần (.san bọc lớp giữa và gần).
    // Mỗi lớp dời theo độ sâu (lopCamera); lớp giữa và gần còn đẩy vào bằng zoom ở khung trong (.lop-zoom).
    var k3 = tao('div', 'khung-3d', khung);
    var lop = { xa: tao('div', 'lop lop-xa', k3) };
    var san = tao('div', 'san', k3);
    // Lớp giữa và gần: khung ngoài nhận độ dời, khung trong nhận zoom (zoom trên cùng phần tử sẽ nhân cả độ dời).
    var ngoai = { giua: tao('div', 'lop lop-giua', san), gan: tao('div', 'lop lop-gan', san) };
    lop.giua = tao('div', 'lop-zoom', ngoai.giua);
    lop.gan = tao('div', 'lop-zoom', ngoai.gan);
    ngoai.xa = lop.xa;
    // Mọi hình raster (nền giấy SVG có feTurbulence, mảng giấy có pattern, ảnh PNG) được "nướng" một lần, trước khi
    // trang báo `san`, thành ảnh PNG đúng điểm ảnh thiết bị (vẽ qua canvas rồi toDataURL), đặt 1:1 ở tỉ lệ 1. Lý do:
    // (1) bộ lọc SVG không chạy lại mỗi khung; (2) khung là hàm thuần của t — ảnh lấy mẫu lại dưới transform đổi tỉ lệ
    // đi qua bộ đệm giải mã theo tỉ lệ của các khung trước; còn <canvas> để trong trang thì thành lớp ghép riêng
    // (`Canvas`), kéo các vật đè lên nó thành lớp `Overlap` giữ tỉ lệ raster cũ. Ảnh <img> thường trong lớp gốc (lớp xa
    // chỉ dời; lớp giữa, gần đẩy vào bằng zoom, dàn trang lại mỗi khung) thì mỗi khung vẽ lại đúng như nhau.
    function anhSvg(svg, cha) {
      var im = tao('img', 'nen-anh', cha);
      im.alt = '';
      im.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg);
      return im;
    }
    // Nền cảnh: ảnh nền AI của cảnh (`du.nen`, anh_vox.py) nếu có; không có thì nền giấy và mảng giấy xé vẽ bằng mã.
    var coNenAI = !!(du.nen && du.nen.dataUrl);
    var anhXa;
    if (coNenAI) {
      var nenAI = tao('img', 'nen-anh', lop.xa);
      nenAI.alt = '';
      nenAI.src = du.nen.dataUrl;
      anhXa = [nenAI];
    } else {
      anhXa = nenXa(hat, kho, mau).map(function (svg) { return anhSvg(svg, lop.xa); });
    }
    var coNen = cacNhip.some(function (n) { return vatCua(n) === 'anh-phu'; });
    var anhGiua = coNen || coNenAI ? null : anhSvg(manhGiua(hat, kho, mau), lop.giua);
    function giaiMa(im) {
      return im.decode ? im.decode().then(function () { return im; }) : Promise.resolve(im);
    }
    // Ảnh PNG cỡ CSS (w × h), điểm ảnh = w·dpr × h·dpr, vẽ các ảnh `ds` phủ kín; trả Promise của <img> đã giải mã.
    function nuong(ds, w, h, lop0) {
      var k = root.devicePixelRatio || 1;
      var cv = document.createElement('canvas');
      cv.width = Math.max(1, Math.round(w * k));
      cv.height = Math.max(1, Math.round(h * k));
      var ctx = cv.getContext('2d');
      ctx.imageSmoothingQuality = 'high';
      ds.forEach(function (im) { ctx.drawImage(im, 0, 0, cv.width, cv.height); });
      var ra = new Image();
      ra.className = lop0;
      ra.alt = '';
      ra.src = cv.toDataURL('image/png');
      return giaiMa(ra);
    }
    function nuongHet() {
      var viec = [];
      // Nền nướng rộng hơn khung LE_NEN mỗi phía (cùng tỉ lệ khung) để lớp xa trôi ngang không hở mép.
      var wNen = kho.rong + 2 * LE_NEN, hNen = Math.round(wNen * kho.cao / kho.rong);
      viec.push(Promise.all(anhXa.map(giaiMa)).then(function () { return nuong(anhXa, wNen, hNen, 'nen-anh'); })
        .then(function (ra) {
          anhXa.forEach(function (im) { lop.xa.removeChild(im); });
          ra.style.left = -LE_NEN + 'px';
          ra.style.top = -Math.round((hNen - kho.cao) / 2) + 'px';
          ra.style.width = wNen + 'px';
          ra.style.height = hNen + 'px';
          lop.xa.insertBefore(ra, lop.xa.firstChild);
        }));
      if (anhGiua) {
        viec.push(giaiMa(anhGiua).then(function () { return nuong([anhGiua], kho.rong, kho.cao, 'nen-anh'); })
          .then(function (ra) { lop.giua.replaceChild(ra, anhGiua); }));
      }
      cacVat.forEach(function (v) {
        var im = v.el.querySelector('img.anh');
        if (!im || !v.b) { return; }
        viec.push(giaiMa(im).then(function () { return nuong([im], v.b.w, v.b.h, 'anh'); })
          .then(function (ra) { v.el.replaceChild(ra, im); }));
      });
      // Ảnh hỏng thì giữ ảnh gốc (vẫn hiện, chỉ chậm hơn), không chặn trang.
      return Promise.all(viec.map(function (p) { return p.catch(function () { return null; }); }));
    }

    function hopO(n, k) {
      if (/^chong-/.test(n.o || '')) { return xepChong(Number(n.o.slice(6)), cacNhip.filter(function (m) { return /^chong-/.test(m.o || ''); }).length, hat, kho); }
      return oCua(boCuc, n.o, kho);
    }
    var cacVat = cacNhip.map(function (n, k) {
      var vat = vatCua(n);
      var tuy = n.tuyChon || [];
      // Ảnh phủ và mũi tên (không chiếm ô) nằm trên cả khung.
      var o = n.o === 'nen' || vat === 'anh-phu' || vat === 'mui-ten' ? { x: 0, y: 0, w: kho.rong, h: kho.cao } : hopO(n, k);
      // Ảnh phủ kín khung (`toan-canh` ô `nen`) là phông xa: lớp xa chỉ dời, không phóng (rẻ khi ghép).
      var tenLop = vat === 'anh-phu' ? 'xa' :
        (tuy.indexOf('xa') >= 0 ? 'giua' : (tuy.indexOf('gan') >= 0 ? 'gan' : (n.vat === 'anh' ? 'giua' : 'gan')));
      var el = tao('div', 'vat vat-' + vat);
      el.setAttribute('data-id', 'nhip-' + k);
      // Bố cục `mot` theo kiểu video mẫu: nhãn tiêu đề (`tren`) và thẻ/chữ (`duoi`) canh trái, hình chính lệch phải.
      if (boCuc === 'mot' && (n.o === 'tren' || n.o === 'duoi')) { el.classList.add('canh-trai'); }
      var r = C().prng(hat * 101 + k);
      var v = { n: n, vat: vat, el: el, o: o, goc0: typeof o.goc === 'number' ? o.goc : 0, chong: /^chong-/.test(n.o || ''),
        nen: vat === 'anh-phu', noi: null, k: k };
      if (n.vat === 'anh') {
        var a = n.anh || { dataUrl: '', rong: 4, cao: 3 };
        // Không hiện dòng nguồn ảnh trên hình: nguồn ghi vào nguon.txt cạnh video (video_ma.py).
        var b = luoi(v.nen ? phuKin(a.rong, a.cao, kho) : vuaO(o, a.rong, a.cao, 0));
        datHop(el, b);
        v.b = b;
        var img = tao('img', 'anh', el);
        img.alt = '';
        img.src = a.dataUrl;
        if (vat === 'anh-khung') {
          // 1–2 mẩu băng dính ở góc trên (theo hạt), tràn ra ngoài khung ảnh.
          var bd = '<svg class="bang-dinh" xmlns="' + NS + '" width="' + lam(b.w) + '" height="' + lam(b.h) + '" viewBox="0 0 ' +
            lam(b.w) + ' ' + lam(b.h) + '">';
          var soBang = 1 + Math.floor(r() * 2);
          var dai = Math.max(70, Math.min(140, b.w * 0.3));
          var gocTrai = r() < 0.5;
          for (var q = 0; q < soBang; q++) {
            var trai = q === 0 ? gocTrai : !gocTrai;
            var cx = trai ? 6 : b.w - 6;
            var t0 = C().bangDinh(hat * 13 + k * 3 + q, cx - dai / 2, -dai * 0.15 + 4, dai, dai * 0.3, 6);
            bd += '<polygon points="' + t0.points + '" transform="rotate(' + (trai ? -38 : 38) + ' ' + lam(cx) + ' 4)"/>';
          }
          el.insertAdjacentHTML('beforeend', bd + '</svg>');
        }
        v.noi = el;
      } else if (vat === 'mui-ten') {
        datHop(el, { x: 0, y: 0, w: kho.rong, h: kho.cao });
        v.noi = el;
      } else {
        datHop(el, o);
        var noi = tao('div', 'noi', el);
        v.noi = noi;
        if (vat === 'the') {
          var th = n.the || {};
          noi.style.width = Math.min(o.w, THE_RONG) + 'px';
          tao('div', 'the-nhan', noi).textContent = th.nhan || '';
          tao('div', 'the-gia-tri', noi).textContent = th.giaTri || '';
          if (th.chuThich) { tao('div', 'the-chu-thich', noi).textContent = th.chuThich; }
        } else if (vat === 'nhan') {
          noi.textContent = n.chu || '';
          v.goc0 += lam((r() * 2 - 1) * 3);
        } else if (vat === 'dau') {
          noi.innerHTML = '<span class="chu-dau"></span><svg class="hat-dau" xmlns="' + NS + '" preserveAspectRatio="none" ' +
            'viewBox="0 0 100 100"><filter id="dau-' + k + '"><feTurbulence type="fractalNoise" baseFrequency="0.9" seed="' +
            (hat * 10 + k) + '"/><feColorMatrix type="matrix" values="0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 0 -2.2 1.25"/></filter>' +
            '<rect width="100" height="100" filter="url(#dau-' + k + ')"/></svg>';
          noi.firstChild.textContent = n.chu || '';
        } else if (vat === 'so') {
          var s = n.so || { giaTri: 0, truoc: '', sau: '', thapPhan: 0 };
          var dong = tao('span', 'dong', noi);
          tao('span', '', dong).textContent = s.truoc || '';
          v.soEl = tao('span', 'so-chay', dong);
          v.soEl.textContent = dinhDangSo(s.giaTri, s.thapPhan);
          tao('span', '', dong).textContent = s.sau || '';
        } else {
          tao('span', 'dong', noi).textContent = n.chu || '';
        }
      }
      lop[tenLop].appendChild(el);
      el.style.visibility = 'hidden';
      return v;
    });

    // Lớp đứng yên ngoài sân khấu: ảnh cảnh trước (chuyển cảnh), dòng nguồn, khung loạt.
    var nenTruoc = null;
    if (co.chuyen && du.nenTruoc) {
      nenTruoc = tao('img', 'nen-truoc', khung);
      nenTruoc.alt = '';
      nenTruoc.src = du.nenTruoc;
    }
    var gocNguon = tao('div', 'goc-nguon', khung);
    var dongNguon = (du.dongNguon || []).filter(function (d) { return d && d.chu; });
    var nhacNguon = null;
    if (dongNguon.length) {
      nhacNguon = tao('div', '', gocNguon);
      nhacNguon.id = 'nhac-nguon';
      dongNguon.forEach(function (d) { tao('div', 'dong', nhacNguon).textContent = d.chu; });
      nhacNguon.style.display = 'none';
    }
    // Dòng nguồn số liệu của cảnh không hiện trên hình (ghi vào nguon.txt).
    var nguonCanh = null;
    if (du.loat && root.THI_KHUNG_LOAT) { root.THI_KHUNG_LOAT.dung(khung, du); }

    // Cỡ chữ lớn nhất vừa ô (đo khi font đã nạp: lần datThoiDiem đầu tiên từ ngoài).
    var daDo = false;
    function tran(el) { return el.scrollWidth > el.clientWidth + 1 || el.scrollHeight > el.clientHeight + 1; }
    // Dòng giá trị của thẻ chỉ đo bề ngang: dấu thanh chữ Việt nhô khỏi hộp dòng 1,08 nhưng không bị cắt (thẻ có lề).
    function tranNgang(el) { return el.scrollWidth > el.clientWidth + 1; }
    function doCo() {
      daDo = true;
      cacVat.forEach(function (v) {
        var el = v.noi;
        if (v.vat === 'chu' || v.vat === 'so') {
          for (var c = CHU_LON; c >= CHU_NHO; c -= 2) { el.style.fontSize = c + 'px'; if (!tran(el)) { break; } }
        } else if (v.vat === 'nhan') {
          // Một dòng từ 30 xuống 22 px; ô hẹp thì cho xuống dòng (dải băng cao hơn) từ 28 xuống 18 px.
          var vua = false;
          for (var c2 = 30; c2 >= 22 && !vua; c2 -= 2) { el.style.fontSize = c2 + 'px'; vua = !tran(el); }
          if (!vua) {
            el.style.whiteSpace = 'normal';
            for (var c4 = 28; c4 >= 18 && !vua; c4 -= 2) { el.style.fontSize = c4 + 'px'; vua = !tran(el); }
          }
        } else if (v.vat === 'dau') {
          for (var c3 = 44; c3 >= 20; c3 -= 2) { el.style.fontSize = c3 + 'px'; if (!tran(el)) { break; } }
        } else if (v.vat === 'the') {
          // Giá trị co riêng theo bề ngang (64 → 28 px); thẻ vẫn cao quá ô thì co cả thẻ.
          var gt = el.querySelector('.the-gia-tri');
          var cgt = 64;
          for (; cgt > 28; cgt -= 4) { gt.style.fontSize = cgt + 'px'; if (!tranNgang(gt)) { break; } }
          gt.style.fontSize = cgt + 'px';
          for (var m = 1; m >= 0.5; m -= 0.05) {
            el.style.fontSize = lam(18 * m) + 'px';
            el.style.padding = lam(18 * m) + 'px ' + lam(24 * m) + 'px';
            gt.style.fontSize = lam(cgt * m) + 'px';
            if (!tran(el) && !tranNgang(gt)) { break; }
          }
        }
      });
      cacVat.forEach(function (v) { if (v.vat === 'mui-ten') { veMuiTen(v); } });
    }

    // Hộp nội dung thật của vật (ảnh: hộp đã vừa ô; chữ: khối .noi trong ô), toạ độ khung, chưa biến đổi.
    function hopNoiDung(v) {
      if (v.b) { return v.b; }
      var n = v.noi;
      return { x: v.o.x + n.offsetLeft, y: v.o.y + n.offsetTop, w: n.offsetWidth, h: n.offsetHeight };
    }
    // Mũi tên `a -> b`: cung từ vật ở ô a tới vật ở ô b (ô chưa có vật thì dùng ô), vòng phía trên khi hai ô nằm
    // ngang nhau, vòng bên phải khi nằm dọc; vẽ dần, đầu mũi tên hiện khi vẽ xong.
    function veMuiTen(v) {
      var ab = String(v.n.chu || '').split('->').map(function (x) { return x.trim(); });
      function hopTen(ten) {
        var ds = cacVat.filter(function (w) { return w !== v && w.n.o === ten && w.vat !== 'mui-ten'; });
        if (ds.length) { return hopNoiDung(ds[ds.length - 1]); }
        try { return oCua(boCuc, ten, kho); } catch (e) { return null; }
      }
      var A = hopTen(ab[0]), B = hopTen(ab[1]);
      var D = day(kho);
      if (!A || !B) {
        A = { x: kho.rong * 0.15, y: D * 0.5, w: 0, h: 0 };
        B = { x: kho.rong * 0.85, y: D * 0.5, w: 0, h: 0 };
      }
      var acx = A.x + A.w / 2, acy = A.y + A.h / 2, bcx = B.x + B.w / 2, bcy = B.y + B.h / 2;
      var p0, p1, c;
      if (Math.abs(bcx - acx) >= Math.abs(bcy - acy)) {
        var hg = bcx >= acx ? 1 : -1;
        p0 = [acx + hg * A.w * 0.2, A.y - 14];
        p1 = [bcx - hg * B.w * 0.2, B.y - 14];
        c = [(p0[0] + p1[0]) / 2, Math.max(18, Math.min(p0[1], p1[1]) - 0.3 * Math.abs(p1[0] - p0[0]))];
      } else {
        var hd = bcy >= acy ? 1 : -1;
        p0 = [A.x + A.w + 14, acy + hd * A.h * 0.2];
        p1 = [B.x + B.w + 14, bcy - hd * B.h * 0.2];
        c = [Math.min(kho.rong - 18, Math.max(p0[0], p1[0]) + 0.3 * Math.abs(p1[1] - p0[1])), (p0[1] + p1[1]) / 2];
      }
      var tx = p1[0] - c[0], ty = p1[1] - c[1], l = Math.sqrt(tx * tx + ty * ty) || 1;
      var ux = tx / l, uy = ty / l;
      var dau = [[p1[0] + ux * 4, p1[1] + uy * 4], [p1[0] - ux * 26 - uy * 17, p1[1] - uy * 26 + ux * 17],
        [p1[0] - ux * 26 + uy * 17, p1[1] - uy * 26 - ux * 17]];
      v.el.innerHTML = '<svg xmlns="' + NS + '" width="' + kho.rong + '" height="' + kho.cao + '" viewBox="0 0 ' + kho.rong + ' ' + kho.cao + '">' +
        '<path class="duong" d="M' + lam(p0[0]) + ' ' + lam(p0[1]) + ' Q' + lam(c[0]) + ' ' + lam(c[1]) + ' ' + lam(p1[0] - ux * 16) + ' ' +
        lam(p1[1] - uy * 16) + '" pathLength="1"/>' +
        '<polygon class="mui" points="' + dau.map(function (p) { return lam(p[0]) + ',' + lam(p[1]); }).join(' ') + '"/></svg>';
      v.duong = v.el.querySelector('.duong');
      v.mui = v.el.querySelector('.mui');
    }

    function datChuyen(t) {
      var k3s = k3.style;
      k3s.transform = '';
      k3s.filter = '';
      if (!nenTruoc) { return; }
      if (t < 0 || t >= CHUYEN) {
        nenTruoc.style.display = 'none';
        nenTruoc.style.filter = '';
        return;
      }
      nenTruoc.style.display = 'block';
      if (co.chuyen === 'lia') {
        var l = chuyenLia(t / CHUYEN, kho);
        var mo = lam(l.mo / 6);
        nenTruoc.style.clipPath = '';
        nenTruoc.style.transform = 'translateX(' + lam(l.dx) + 'px)';
        nenTruoc.style.filter = mo > 0 ? 'blur(' + mo + 'px)' : '';
        k3s.transform = 'translateX(' + lam(kho.rong + l.dx) + 'px)';
        k3s.filter = mo > 0 ? 'blur(' + mo + 'px)' : '';
      } else {
        var s = root.THI_CHUYEN.trangThai('xe-giay', t, CHUYEN, hat).nen;
        nenTruoc.style.transform = '';
        // THI_CHUYEN trả toạ độ không đơn vị ("x y"), CSS polygon() bỏ qua cả giá trị đó: thêm px ở đây.
        nenTruoc.style.clipPath = s.clipPath.replace(/(-?\d+(?:\.\d+)?) (-?\d+(?:\.\d+)?)/g, '$1px $2px');
        // Bóng đổ của THI_CHUYEN đặt trên chính ảnh đã cắt thì bị cắt mất mà vẫn tốn cả khung: bỏ.
        nenTruoc.style.filter = '';
        if (s.opacity <= 0) { nenTruoc.style.display = 'none'; }
      }
    }

    function datCamera(cam) {
      ['xa', 'giua', 'gan'].forEach(function (ten) {
        var l = lopCamera(ten, cam, root.devicePixelRatio || 1);
        ngoai[ten].style.transform = l.x ? 'translate(' + l.x + 'px,0px)' : 'none';
      });
    }

    function dat(t) {
      datChuyen(t);
      datCamera(camera(t, du.thoiLuong));
      cacVat.forEach(function (v) {
        var p = kep((t - v.n.batDau) / DAI[v.vat], 0, 1);
        var el = v.el;
        // Ẩn cả bằng opacity: lớp hạt SVG có filter của con dấu vẫn được vẽ khi chỉ có visibility: hidden.
        if (p <= 0) { el.style.visibility = 'hidden'; el.style.opacity = '0'; return; }
        el.style.visibility = 'visible';
        var a = vao(v.vat, p);
        el.style.opacity = a.a >= 1 ? '' : String(a.a);
        var goc = lam(v.goc0 + a.goc);
        // Đứng yên đúng chỗ thì không để biến đổi nào (cùng cây thuộc tính vẽ như khi nhảy thẳng tới t).
        el.style.transform = a.dx || a.dy || goc || a.s !== 1 ?
          'translate(' + a.dx + 'px,' + a.dy + 'px) rotate(' + goc + 'deg) scale(' + a.s + ')' : '';
        if (v.vat === 'mui-ten') {
          if (!v.duong) { return; }
          v.duong.style.strokeDashoffset = String(lam(1 - p));
          v.mui.style.visibility = p >= 1 ? 'visible' : 'hidden';
        } else if (v.vat === 'so') {
          var q = kep((t - v.n.batDau) / SO_CHAY, 0, 1);
          var e = 1 - Math.pow(1 - q, 3);
          var s = v.n.so || { giaTri: 0, thapPhan: 0 };
          v.soEl.textContent = dinhDangSo(q >= 1 ? s.giaTri : s.giaTri * e, s.thapPhan);
        }
      });
      if (nhacNguon) {
        var pn = kep((t - dongNguon[0].tu) / 0.3, 0, 1);
        nhacNguon.style.display = pn > 0 ? 'block' : 'none';
        nhacNguon.style.opacity = String(lam(pn));
      }
    }

    function thoiDiemCuoi() { return du.thoiLuong - 1 / 30; }
    root.datThoiDiem = function (t) {
      if (!daDo) { doCo(); }
      dat(t);
    };
    function hcn(el) { return el.getBoundingClientRect(); }
    function kiemTran() {
      root.datThoiDiem(thoiDiemCuoi());
      datCamera({ u: 0.5 });
      if (nenTruoc) { nenTruoc.style.display = 'none'; }
      var loi = [];
      var R = kho.rong + 1, Cc = kho.cao + 1, D = day(kho) + 1;
      var hop = [];
      cacVat.forEach(function (v) {
        var id = 'nhip-' + v.k;
        if (['chu', 'the', 'nhan', 'dau', 'so'].indexOf(v.vat) >= 0 && tran(v.noi)) { loi.push(id); }
        if (v.nen || v.vat === 'mui-ten') { return; }
        var b = hcn(v.noi);
        if (b.left < -1 || b.top < -1 || b.right > R || b.bottom > Cc || b.bottom > D) {
          if (loi.indexOf(id) < 0) { loi.push(id); }
        }
        var ng = v.el.querySelector('.nguon-anh');
        if (ng) {
          var bn = hcn(ng);
          if (bn.left < -1 || bn.right > R || bn.bottom > D) { loi.push('nguon-' + id); }
        }
        if (!v.chong) { hop.push({ id: id, b: b, anh: v.n.vat === 'anh', dan: v.vat === 'dau' || v.vat === 'nhan' }); }
      });
      cacVat.forEach(function (v) {
        if (!v.nen) { return; }
        var ng = v.el.querySelector('.nguon-anh');
        if (ng) { var bn = hcn(ng); if (bn.left < -1 || bn.right > R || bn.bottom > D) { loi.push('nguon-nhip-' + v.k); } }
      });
      // Đè nhau quá 30 % vật nhỏ hơn: giữa hai vật chữ và giữa hai ảnh. Con dấu, nhãn dán lên ảnh là chủ ý (ô `giua` của
      // `hai-ben` nằm đè mép hai ảnh), nên cặp dấu/nhãn – ảnh không tính.
      for (var i = 0; i < hop.length; i++) {
        for (var j = i + 1; j < hop.length; j++) {
          if ((hop[i].anh && hop[j].dan) || (hop[i].dan && hop[j].anh)) { continue; }
          var a = hop[i].b, b = hop[j].b;
          var w = Math.min(a.right, b.right) - Math.max(a.left, b.left);
          var h = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
          if (w <= 0 || h <= 0) { continue; }
          var nho = Math.min(a.width * a.height, b.width * b.height);
          if (nho > 0 && w * h > 0.3 * nho) { loi.push('chong:' + hop[i].id + ',' + hop[j].id); }
        }
      }
      if (nguonCanh) {
        var bc = hcn(nguonCanh);
        if (tran(nguonCanh) || bc.left < -1 || bc.top < -1 || bc.right > R || bc.bottom > D) { loi.push('nguon'); }
      }
      if (nhacNguon) {
        var bm = hcn(nhacNguon);
        if (bm.left < -1 || bm.top < -1 || bm.right > R || bm.bottom > D) { loi.push('nhac-nguon'); }
      }
      return loi;
    }
    function suKien() {
      var ds = [];
      if (co.chuyen) { ds.push({ t: 0, loai: 'chuyen', dai: CHUYEN }); }
      cacVat.forEach(function (v) {
        // Vật hiện ngay đầu cảnh (cùng lúc chuyển cảnh) không kêu; con dấu kêu tiếng đóng, vật khác tiếng "ting" nhỏ.
        if (v.n.batDau <= (du.danDau || 0) + 0.01) { return; }
        ds.push({ t: v.n.batDau, loai: v.vat === 'dau' ? 'nhan' : 'ting', dai: 0.2 });
      });
      return ds;
    }
    root.THI_VIDEO.thoiDiemCuoi = thoiDiemCuoi;
    root.THI_VIDEO.kiemTran = kiemTran;
    root.THI_VIDEO.suKien = suKien;
    dat(0);
    // `san` chỉ bật sau khi mọi ảnh đã nướng xong (chup.mo_trang chờ cờ này).
    nuongHet().then(function () { dat(0); root.THI_VIDEO.san = true; });
  }

  root.THI_VOX = {
    oCua: oCua, xepChong: xepChong, vao: vao, camera: camera, lopCamera: lopCamera, chuyenLia: chuyenLia, dinhDangSo: dinhDangSo,
    easeOutCubic: easeOutCubic, DAI: DAI, CHUYEN: CHUYEN, TROI: TROI, khoiDong: khoiDong
  };
  // Trang Vox không nạp khung-video.js: vox.js tự cung cấp hợp đồng trang THI_VIDEO, luôn là đối tượng mới
  // (page.set_content giữ nguyên window, nên THI_VIDEO của trang trước — có khi đã `san` — còn đó).
  root.THI_VIDEO = { khoiDong: khoiDong, san: false };
})(typeof globalThis !== 'undefined' ? globalThis : this);

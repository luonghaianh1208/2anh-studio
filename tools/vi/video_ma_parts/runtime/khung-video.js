(function (root) {
  'use strict';

  var TOC_DO_VIET = 20;
  var LAU_BANG = 0.5; // mặc định khi chạy ngoài trang (Node); trang lấy du.giayLauBang từ lich.LAU_BANG của Python
  var HINH_TOI_THIEU = 1.2;
  var CO_TAY = 0.85;
  // Cỡ chữ nhãn tiêu đề của cat-dan (chữ hoa ExtraBold): tiêu đề dài hơn 40 ký tự dùng cỡ nhỏ.
  var CO_NHAN = 34;
  var CO_NHAN_NHO = 26;
  // Khung loạt (`loat`) chiếm dải 40 px trên cùng: có loạt thì ô tiêu đề không cao hơn y 40.
  var CHUA_LOAT = 40;
  // Thẻ thông tin: khoảng cách tới nội dung; lề trong; hàng nhãn, giá trị, chú thích (cỡ 13, 44, 16).
  var KHOANG_THE = 20;
  var LE_THE = 12;
  var NS = 'http://www.w3.org/2000/svg';
  var DANH_DAU = /\*\*(.+?)\*\*|~([^~]+)~|\^([^\^]+)\^/g;
  // Cùng ngữ pháp với kiem.py (_CUM_RE, _SO_DUNG). `____` (ô trống) và ` == ` có khoảng trắng hai bên là chữ thường.
  var CUM = /(?<!=)==(?![=\s])(.+?)(?<![=\s])==(?!=)|\(\((.+?)\)\)|(?<!_)__(?![_\s])(.+?)(?<![_\s])__(?!_)/g;
  var SO = /\{\{(-?\d+(?:\.\d+)?)\}\}/g;

  function kep(x, a, b) { return x < a ? a : (x > b ? b : x); }
  function tienDo(t, batDau, thoiLuong) {
    if (thoiLuong <= 0) { return t >= batDau ? 1 : 0; }
    return kep((t - batDau) / thoiLuong, 0, 1);
  }
  function thoat(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
  function tach(chu) {
    var kq = [];
    var vt = 0;
    var m;
    chu = String(chu);
    DANH_DAU.lastIndex = 0;
    while ((m = DANH_DAU.exec(chu))) {
      if (m.index > vt) { kq.push({ the: '', chu: chu.slice(vt, m.index) }); }
      kq.push(m[1] !== undefined ? { the: 'b', chu: m[1] } : (m[2] !== undefined ? { the: 'sub', chu: m[2] } : { the: 'sup', chu: m[3] }));
      vt = m.index + m[0].length;
    }
    if (vt < chu.length) { kq.push({ the: '', chu: chu.slice(vt) }); }
    return kq;
  }
  // Số chạy `{{1500.5}}`: hiện kiểu Việt (dấu phẩy thập phân), giữ số chữ số thập phân của số gốc.
  function soCuoi(goc) {
    var chuSo = (goc.split('.')[1] || '').length;
    var tron = Number(Number(goc).toFixed(chuSo));
    return (tron === 0 ? 0 : tron).toFixed(chuSo).replace('.', ',');
  }
  // Đoạn chữ trong một phần: đoạn thường {the, chu} hoặc đoạn số {the, chu, so: k, gtri, chuSo}.
  function tachDoan(chu, dem) {
    var kq = [];
    tach(chu).forEach(function (o) {
      var vt = 0;
      var m;
      SO.lastIndex = 0;
      while ((m = SO.exec(o.chu))) {
        if (m.index > vt) { kq.push({ the: o.the, chu: o.chu.slice(vt, m.index) }); }
        kq.push({ the: o.the, chu: soCuoi(m[1]), so: dem.so++, gtri: Number(m[1]), chuSo: (m[1].split('.')[1] || '').length });
        vt = m.index + m[0].length;
      }
      if (vt < o.chu.length) { kq.push({ the: o.the, chu: o.chu.slice(vt) }); }
    });
    return kq;
  }
  // Chữ -> các phần {cum: null | {kieu, k}, doan: [...]}. Cụm nhấn `==x==` tô, `((x))` khoanh, `__x__` gạch.
  // `khongCum` (biểu thức của cong-thuc): không tách cụm, `((` và `__` giữ nguyên là chữ.
  function phanTich(chu, khongCum) {
    chu = String(chu);
    if (khongCum) { return chu ? [{ cum: null, doan: tachDoan(chu, { so: 0, cum: 0 }) }] : []; }
    var phan = [];
    var dem = { so: 0, cum: 0 };
    var vt = 0;
    var m;
    CUM.lastIndex = 0;
    while ((m = CUM.exec(chu))) {
      if (m.index > vt) { phan.push({ cum: null, doan: tachDoan(chu.slice(vt, m.index), dem) }); }
      var kieu = m[1] !== undefined ? 'to' : (m[2] !== undefined ? 'khoanh' : 'gach');
      phan.push({ cum: { kieu: kieu, k: dem.cum++ }, doan: tachDoan(m[1] !== undefined ? m[1] : (m[2] !== undefined ? m[2] : m[3]), dem) });
      vt = m.index + m[0].length;
    }
    if (vt < chu.length) { phan.push({ cum: null, doan: tachDoan(chu.slice(vt), dem) }); }
    return phan;
  }
  function demPhan(phan) {
    return phan.reduce(function (n, p) { return p.doan.reduce(function (s, o) { return s + o.chu.length; }, n); }, 0);
  }
  function demKyTu(chu, khongCum) { return demPhan(phanTich(chu, khongCum)); }
  // Bề rộng ước lượng theo số ký tự: đệm hai đầu cụm khoanh (~1,2 ký tự) và lề cụm khi chu-dong (~0,5 ký tự) cũng chiếm chỗ.
  function demRong(chu, chuDong) {
    var phan = phanTich(chu);
    return phan.reduce(function (n, p) {
      return n + (p.cum ? (p.cum.kieu === 'khoanh' ? 1.2 : 0) + (chuDong ? 0.5 : 0) : 0);
    }, demPhan(phan));
  }
  // Vị trí (theo chữ hiển thị) và giá trị của từng số chạy.
  function viTriSo(chu, khongCum) {
    var kq = [];
    var vt = 0;
    phanTich(chu, khongCum).forEach(function (p) {
      p.doan.forEach(function (o) {
        if (o.so !== undefined) { kq.push({ k: o.so, viTri: vt, dai: o.chu.length, gtri: o.gtri, chuSo: o.chuSo, chu: o.chu }); }
        vt += o.chu.length;
      });
    });
    return kq;
  }
  function htmlSo(o, hien, so) {
    var mo = '<span class="so" data-so="' + o.so + '">';
    if (!hien) { return mo + '<span class="an">' + thoat(o.chu) + '</span></span>'; }
    var chay = so && so[o.so] !== undefined && so[o.so] !== null ? String(so[o.so]) : o.chu;
    if (chay === o.chu) { return mo + thoat(o.chu) + '</span>'; }
    // Chữ số cuối giữ chỗ (ẩn) để bề rộng không đổi khi số đang chạy.
    return mo + '<span class="so-cuoi">' + thoat(o.chu) + '</span><span class="so-chay">' + thoat(chay) + '</span></span>';
  }
  function kieuNay(v) {
    if (v.a === 1 && v.s === 1 && v.y === 0) { return ''; }
    return ' style="opacity:' + lam3(v.a) + ';transform:translateY(' + lam3(v.y) + 'px) scale(' + lam3(v.s) + ')"';
  }
  function lam3(x) { return Math.round(x * 1000) / 1000; }
  // Chế độ nảy: mỗi ký tự một span.nay; ký tự liền nhau (không cách) gói trong span.tu để từ không bị ngắt dòng.
  function htmlNay(chu, batDauI, nay) {
    var kq = '';
    var tu = '';
    for (var j = 0; j < chu.length; j++) {
      var c = chu[j];
      if (/\s/.test(c)) {
        if (tu) { kq += '<span class="tu">' + tu + '</span>'; tu = ''; }
        kq += c;
      } else {
        tu += '<span class="nay"' + kieuNay(nay(batDauI + j)) + '>' + thoat(c) + '</span>';
      }
    }
    return tu ? kq + '<span class="tu">' + tu + '</span>' : kq;
  }
  // Hiện n ký tự đầu; khi 0 < n < tổng, chèn span.ngoi rỗng ngay sau ký tự thứ n (điểm ngòi bút).
  // Dấu đánh dấu không đếm. Cụm bọc span.cum, số bọc span.so; phần chưa viết nằm trong span.an để bố cục không nhảy.
  // `so`: chuỗi đang hiện của từng số chạy (bỏ trống là giá trị cuối). `nay(i)`: {s, y, a} của ký tự i (chế độ nảy).
  // Chia đoạn chữ (không cụm) thành khối theo `khoi` = [số ký tự hiện của khối k]: khối k, rồi một ký tự ngăn (khoảng
  // trắng) trước khối k + 1. Đoạn thường cắt được ở ranh giới; đoạn số không bao giờ nằm vắt qua ranh giới (parse).
  // Trả [{khoi: true|false, doan: [...]}] theo thứ tự.
  function chiaKhoi(doan, khoi) {
    var bien = [];
    var s = 0;
    khoi.forEach(function (n, k) {
      bien.push({ tu: s, den: s + n, khoi: true });
      s += n;
      if (k < khoi.length - 1) { bien.push({ tu: s, den: s + 1, khoi: false }); s += 1; }
    });
    var nhom = bien.map(function (b) { return { khoi: b.khoi, doan: [] }; });
    function chiSo(p) {
      for (var j = 0; j < bien.length; j++) { if (p < bien[j].den) { return j; } }
      return bien.length - 1;
    }
    var vt = 0;
    doan.forEach(function (o) {
      var dai = o.chu.length;
      if (o.so !== undefined) { nhom[chiSo(vt)].doan.push(o); vt += dai; return; }
      var i = 0;
      while (i < dai) {
        var j = chiSo(vt + i);
        var het = j === bien.length - 1 ? dai : Math.min(dai, bien[j].den - vt);
        if (het <= i) { het = dai; }
        nhom[j].doan.push({ the: o.the, chu: o.chu.slice(i, het) });
        i = het;
      }
      vt += dai;
    });
    return nhom;
  }
  // Toán tử quan hệ mà dòng công thức được xuống trước nó (có khoảng trắng hai bên): `a = b` được ngắt thành
  // `a` / `= b`, còn một số hạng (`M x V`, `2π√(l/g)`) không bao giờ bị ngắt giữa.
  var TOAN_TU = ['=', '≈', '≠', '<', '>', '≤', '≥', '→', '⇒'];
  // Một phần công thức -> các đoạn (chữ gốc), tách ở khoảng trắng đứng trước ` <toán tử> ` cấp ngoài cùng: không nằm
  // trong ngoặc, `**…**`, `~…~`, `^…^` hay `{{…}}`. Ghép các đoạn bằng một khoảng trắng thì ra lại đúng phần đó.
  function tachDoanCongThuc(p) {
    var kq = [];
    var dau = 0;
    var ngoac = 0;
    var dam = 0, duoi = 0, tren = 0, so = 0;
    for (var i = 0; i < p.length; i++) {
      var c = p[i];
      var hai = p.substr(i, 2);
      if (hai === '**') { dam ^= 1; i++; continue; }
      if (hai === '{{') { so++; i++; continue; }
      if (hai === '}}') { so = Math.max(0, so - 1); i++; continue; }
      if (c === '~') { duoi ^= 1; continue; }
      if (c === '^') { tren ^= 1; continue; }
      if ('([{'.indexOf(c) >= 0) { ngoac++; continue; }
      if (')]}'.indexOf(c) >= 0) { ngoac = Math.max(0, ngoac - 1); continue; }
      if (c === ' ' && i > dau && !ngoac && !dam && !duoi && !tren && !so && TOAN_TU.indexOf(p[i + 1]) >= 0 && p[i + 2] === ' ') {
        kq.push(p.slice(dau, i));
        dau = i + 1;
      }
    }
    kq.push(p.slice(dau));
    return kq;
  }
  // `khoi` (chỉ kèm khongCum: biểu thức công thức, giá trị thẻ): mỗi khối bọc span.phan không ngắt dòng; dòng chỉ
  // xuống ở khoảng trắng giữa hai khối. `ngat`: chỉ số các khối được xuống dòng ở khoảng trắng bên trong (khối quá
  // rộng cả khi đã thu chữ, xem thuKhoi).
  function catDanhDau(chu, n, so, nay, khongCum, khoi, ngat) {
    var phan = phanTich(chu, khongCum);
    var con = nay ? Infinity : n;
    var giua = !nay && n > 0 && n < demPhan(phan);
    var i = 0;
    var html = '';
    function veDoan(o) {
      var trong;
      if (nay) {
        trong = o.so !== undefined
          ? '<span class="tu"><span class="nay"' + kieuNay(nay(i)) + '>' + htmlSo(o, true, so) + '</span></span>'
          : htmlNay(o.chu, i, nay);
        i += o.chu.length;
      } else if (o.so !== undefined) {
        var hienSo = con > 0;
        con -= Math.min(con, o.chu.length);
        trong = htmlSo(o, hienSo, so) + (giua && hienSo && con === 0 ? '<span class="ngoi"></span>' : '');
        if (hienSo && con === 0) { giua = false; }
      } else {
        var hien = con > 0 ? o.chu.slice(0, con) : '';
        var an = o.chu.slice(hien.length);
        con -= hien.length;
        var ngoi = giua && hien && con === 0 ? '<span class="ngoi"></span>' : '';
        if (ngoi) { giua = false; }
        trong = thoat(hien) + ngoi + (an ? '<span class="an">' + thoat(an) + '</span>' : '');
      }
      return o.the ? '<' + o.the + '>' + trong + '</' + o.the + '>' : trong;
    }
    function veDs(ds) { return ds.map(veDoan).join(''); }
    if (khoi && khongCum && phan.length) {
      var k = 0;
      return chiaKhoi(phan[0].doan, khoi).map(function (g) {
        if (!g.khoi) { return veDs(g.doan); }
        var kieu = ngat && ngat.indexOf(k++) >= 0 ? 'normal' : 'nowrap';
        return '<span class="phan" style="white-space:' + kieu + '">' + veDs(g.doan) + '</span>';
      }).join('');
    }
    phan.forEach(function (p) {
      var trongCum = veDs(p.doan);
      html += p.cum ? '<span class="cum ' + p.cum.kieu + '" data-cum="' + p.cum.k + '">' + trongCum + '</span>' : trongCum;
    });
    return html;
  }
  function thoiGianViet(chu, khongCum) { return Math.max(0.5, demKyTu(chu, khongCum) / TOC_DO_VIET); }

  // Số ký tự đã viết của mục chữ tại t (mục viết theo phần: cộng từng phần).
  function kyTuHien(m, t, tong) {
    if (!m.phan) { return Math.round(tienDo(t, m.batDau, m.thoiLuong) * tong); }
    return Math.min(tong, m.phan.reduce(function (n, p) { return n + Math.round(tienDo(t, p.batDau, p.thoiLuong) * p.ky); }, 0));
  }
  // Lúc ký tự thứ i của mục chữ (viết tay) hiện ra.
  function lucKyTu(m, i, tong) {
    var p = m.phan ? m.phan.filter(function (q) { return i >= q.tu && i < q.tu + q.ky; })[0] : null;
    if (p) { return p.batDau + p.thoiLuong * (i - p.tu + 0.5) / Math.max(1, p.ky); }
    return m.batDau + m.thoiLuong * (i + 0.5) / Math.max(1, tong);
  }
  // Danh sách mục cho bàn tay và máy quay: mục viết theo phần tách thành một mục mỗi phần (cùng id), để giữa hai
  // phần bàn tay rời bảng như giữa hai mục.
  function tachPhan(ds) {
    var kq = [];
    ds.forEach(function (m) {
      if (!m.phan) { kq.push(m); return; }
      m.phan.forEach(function (p) { kq.push(gan(gan({}, m), { batDau: p.batDau, thoiLuong: p.thoiLuong })); });
    });
    return kq;
  }

  function rng(hat) {
    var a = hat | 0;
    return function () {
      a = a + 0x6D2B79F5 | 0;
      var t = Math.imul(a ^ a >>> 15, 1 | a);
      t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
      return ((t ^ t >>> 14) >>> 0) / 4294967296;
    };
  }
  function lam(x) { return Math.round(x * 10) / 10; }
  function duongQua(diem, hat) {
    var r = rng(hat);
    var d = '';
    for (var i = 0; i < diem.length; i++) {
      var p = diem[i];
      if (i === 0) { d += 'M' + lam(p[0]) + ' ' + lam(p[1]); continue; }
      var q = diem[i - 1];
      var dx = p[0] - q[0];
      var dy = p[1] - q[1];
      var dai = Math.sqrt(dx * dx + dy * dy) || 1;
      var nx = -dy / dai;
      var ny = dx / dai;
      var n = Math.max(2, Math.round(dai / 70));
      for (var j = 1; j <= n; j++) {
        var u = j / n;
        var lech = j === n ? 0 : (r() - 0.5) * 4;
        d += ' L' + lam(q[0] + dx * u + nx * lech) + ' ' + lam(q[1] + dy * u + ny * lech);
      }
    }
    return d;
  }
  function hopQua(x, y, w, h, hat) { return duongQua([[x, y], [x + w, y], [x + w, y + h], [x, y + h], [x, y - 2]], hat); }
  function vongTron(cx, cy, r) {
    return 'M' + lam(cx - r) + ' ' + lam(cy) + ' a' + r + ' ' + r + ' 0 1 0 ' + (2 * r) + ' 0 a' + r + ' ' + r + ' 0 1 0 ' + (-2 * r) + ' 0';
  }
  function muiTen(x1, y1, x2, y2, hat) {
    var goc = Math.atan2(y2 - y1, x2 - x1);
    var c = function (lech) { return [x2 - 16 * Math.cos(goc + lech), y2 - 16 * Math.sin(goc + lech)]; };
    var a = c(0.5);
    var b = c(-0.5);
    return duongQua([[x1, y1], [x2, y2]], hat) + ' M' + lam(a[0]) + ' ' + lam(a[1]) + ' L' + x2 + ' ' + y2 + ' L' + lam(b[0]) + ' ' + lam(b[1]);
  }

  function gan(dich, tuy) {
    Object.keys(tuy || {}).forEach(function (k) { dich[k] = tuy[k]; });
    return dich;
  }
  // Đặt khung w×h giữ tỉ lệ rong:cao vừa trong ô (x, y, o, c), căn giữa (object-fit: contain).
  function vuaKhung(rong, cao, x, y, o, c) {
    var s = Math.min(o / rong, c / cao);
    var w = rong * s, h = cao * s;
    return { x: x + (o - w) / 2, y: y + (c - h) / 2, rong: w, cao: h };
  }
  // Ô bố cục {x, y, w, h} của khổ hiện tại (runtime/kho.js, bảng o-bo-cuc.json); tên lạ là lỗi.
  function oBoCuc(ten) { return root.THI_KHO.o(ten); }
  // Khổ dọc 9:16: cảnh nào cần xếp khác (xếp chồng thay cho xếp ngang) hỏi hàm này.
  function laDoc() { return root.THI_KHO.lay().ten === 'doc'; }
  function giayLau(du) { return typeof du.giayLauBang === 'number' ? du.giayLauBang : LAU_BANG; }
  // Kiểu chuyển cảnh đầu cảnh: du.co.chuyen, hoặc du.co.lauBang của dữ liệu kiểu cũ; không có thì null.
  function kieuChuyen(du) {
    var co = du.co || {};
    return co.chuyen || (co.lauBang ? 'lau-bang' : null);
  }
  // Tiến độ trượt vào của mục chữ trượt (cat-dan) tại t. Mục viết theo phần kéo dài qua mọi phần (thoiLuong = hết
  // phần cuối − phần đầu) nhưng chỉ trượt một lần 0,35 s từ phần đầu; mục thường trượt trong thoiLuong của nó.
  function tienDoTruot(m, t) {
    return m.phan ? tienDo(t, m.phan[0].batDau, root.THI_CAT_DAN.TRUOT) : tienDo(t, m.batDau, m.thoiLuong);
  }
  // Chủ đề của cảnh (du.chuDe từ phong.py); dữ liệu cũ không có chuDe là viet-tay.
  function chuDe(du) { return du.chuDe || { ten: 'viet-tay', hienChu: 'viet', net: 've' }; }
  function tao(du) {
    var gh = du.thoiLuong;
    var sau = kieuChuyen(du) ? giayLau(du) + 0.05 : 0;
    var cd = chuDe(du);
    // cat-dan: chữ trượt vào (không bút, không bàn tay), nét vẽ nhanh và đậm, hình và ảnh là sticker có góc xoay
    // lấy lần lượt từ prng(số cảnh).
    var truot = cd.hienChu === 'truot';
    var nhanh = cd.net === 'nhanh';
    var catDan = cd.ten === 'cat-dan';
    var xoayDan = catDan ? root.THI_CAT_DAN.prng(du.so) : null;
    function dau(batDau, lui) { return Math.min(Math.max(batDau, sau), gh - lui); }
    // Chữ trượt: vào ở batDau (không sớm hơn 0,6 s; nhãn tiêu đề 0,4 s), trượt 0,35 s.
    function daiTruot(batDau) { return Math.max(0.05, Math.min(root.THI_CAT_DAN.TRUOT, gh - 0.2 - batDau)); }
    function chu(id, noiDung, x, y, rong, cao, co, batDau, tuy) {
      if (tuy && tuy.phan) { return chuPhan(id, noiDung, x, y, rong, cao, co, tuy); }
      if (truot) {
        batDau = dau(Math.max(batDau, tuy && tuy.bang ? 0.4 : 0.6), 0.6);
        return gan(gan({ id: id, kieu: 'chu', chu: noiDung, x: x, y: y, rong: rong, cao: cao, co: co, batDau: batDau,
          thoiLuong: daiTruot(batDau), can: 'trai', mau: '' }, tuy), { truot: true, tay: false, nay: false });
      }
      batDau = dau(batDau, 0.6);
      // Chữ nảy (tiêu đề khi chu-dong): nảy từng ký tự thay cho bút viết; không có bàn tay.
      var nay = !!(tuy && tuy.nay);
      var dai = Math.max(0.3, Math.min(nay ? root.THI_DONG.thoiGianNay(demKyTu(noiDung)) : thoiGianViet(noiDung, tuy && tuy.khongCum), gh - 0.2 - batDau));
      if (nay) { tuy = gan({ tay: false }, tuy); }
      return gan({ id: id, kieu: 'chu', chu: noiDung, x: x, y: y, rong: rong, cao: cao, co: co, batDau: batDau, thoiLuong: dai, can: 'trai', mau: '' }, tuy);
    }
    // Chữ viết theo từng phần: `tuy.phan` = [{batDau, ky}] nối tiếp nhau (ky: số ký tự hiện của phần). Phần k bắt
    // đầu ở batDau của nó nhưng không sớm hơn lúc phần trước xong; giữa hai phần bút dừng. Tổng ky phải bằng số ký tự.
    function chuPhan(id, noiDung, x, y, rong, cao, co, tuy) {
      var xong = 0;
      var tu = 0;
      var phan = tuy.phan.map(function (p) {
        var bd = Math.max(dau(truot ? Math.max(p.batDau, 0.6) : p.batDau, 0.6), Math.min(xong, gh - 0.6));
        var dai = truot ? daiTruot(bd) : Math.max(0.3, Math.min(p.ky / TOC_DO_VIET, gh - 0.2 - bd));
        var o = { batDau: bd, thoiLuong: dai, tu: tu, ky: p.ky };
        xong = bd + dai;
        tu += p.ky;
        return o;
      });
      var batDau = phan[0].batDau;
      var het = Math.max.apply(null, phan.map(function (p) { return p.batDau + p.thoiLuong; }));
      return gan(gan({ id: id, kieu: 'chu', chu: noiDung, x: x, y: y, rong: rong, cao: cao, co: co, batDau: batDau,
        thoiLuong: het - batDau, can: 'trai', mau: '' }, tuy), truot ? { phan: phan, truot: true, tay: false } : { phan: phan });
    }
    function net(id, d, batDau, dai, tuy) {
      batDau = dau(batDau, 0.6);
      dai = Math.max(0.2, Math.min(dai, gh - 0.2 - batDau));
      var n = gan({ id: id, kieu: 'net', d: d, batDau: batDau, thoiLuong: dai, mau: '', day: 4 }, tuy);
      // Nét nhanh (cat-dan): vẽ trong tối đa 0,5 s, dày gấp 1,4.
      if (nhanh) { n.thoiLuong = Math.min(n.thoiLuong, 0.5); n.day *= 1.4; }
      return n;
    }
    // Biểu tượng vẽ lần lượt từng phần tử; cả hình ít nhất 1,2 s.
    function hinh(id, h, x, y, kich, batDau, tuy) {
      batDau = dau(batDau, 0.2 + HINH_TOI_THIEU);
      var dai = Math.min(3, Math.max(HINH_TOI_THIEU, 0.45 * h.phanTu.length));
      dai = Math.max(0.3, Math.min(dai, gh - 0.2 - batDau));
      var m = gan({ id: id, kieu: 'hinh', phanTu: h.phanTu, viewBox: h.viewBox, x: x, y: y, kich: kich, batDau: batDau, thoiLuong: dai, mau: '' }, tuy);
      // Sticker (cat-dan): bật vào trong 0,45 s thay cho vẽ từng nét; không bàn tay.
      if (catDan) { gan(m, { sticker: true, goc: xoayDan() * 6 - 3, tay: false, thoiLuong: Math.max(0.05, Math.min(0.45, gh - 0.2 - batDau)) }); }
      return m;
    }
    // Ảnh hiện dần 0,4 s rồi phóng/lướt chậm tới cuối cảnh; khung giữ tỉ lệ ảnh trong ô.
    // `tuy.viTriNguon`: `duoi` (dưới khung, trong ô `tuy.oNguon`), `canh` (bên phải khung), bỏ trống là trong khung.
    function anh(id, a, x, y, rong, cao, batDau, tuy) {
      batDau = dau(batDau, 0.6);
      var k = vuaKhung(a.rong, a.cao, x, y, rong, cao);
      var m = gan({ id: id, kieu: 'anh', dataUrl: a.dataUrl, nguon: a.nguon, x: k.x, y: k.y, rong: k.rong, cao: k.cao,
        batDau: batDau, thoiLuong: Math.min(0.4, gh - 0.2 - batDau) }, tuy);
      if (catDan) { gan(m, { sticker: true, goc: xoayDan() * 6 - 3 }); }
      // Cảnh có dòng tài liệu: dòng nguồn ảnh không nằm cạnh ảnh mà xếp trên dòng tài liệu, trong ô `tai-lieu`.
      if (du.taiLieu && a.nguon) { m.nguonNgoai = true; }
      return m;
    }
    // Ô bố cục của cảnh có thẻ thông tin. Khổ dọc: thẻ nằm dưới tiêu đề (ô `the`, đỉnh ô nội dung), nên ô nội dung, ô
    // bìa và cột phụ dời xuống dưới thẻ; nội dung hẹp giữ chiều cao, nội dung, bìa và cột phụ giữ đáy. Khổ ngang: thẻ ở
    // góc phải trên, trên cột phụ và trên ô nội dung, nên các ô giữ nguyên (tiêu đề hẹp lại trong tieuDe).
    // Khổ ngang có dòng tài liệu (góc phải dưới): ô nội dung rộng dừng trên dòng tài liệu.
    var coThe = !!du.the;
    function oCanh(ten) {
      var o = oBoCuc(ten);
      if (coThe && laDoc()) {
        var dich = oBoCuc('the').h + KHOANG_THE;
        if (ten === 'noi-dung-hep') { o.y += dich; }
        if (ten === 'noi-dung' || ten === 'bia' || ten === 'cot-phu') { o.y += dich; o.h -= dich; }
      }
      if (du.taiLieu && !laDoc() && ten === 'noi-dung') { o.h = Math.min(o.h, oBoCuc('tai-lieu').y - 6 - o.y); }
      return o;
    }
    // Tiêu đề trong ô `tieu-de`; `rong` (bỏ trống là cả ô) hẹp hơn ô khi cảnh có cột phụ. Nét gạch dưới cách ô 14.
    function tieuDe(noiDung, batDau, rong) {
      var o = oBoCuc('tieu-de');
      if (du.loat) { o.y = Math.max(o.y, CHUA_LOAT); }
      rong = rong || o.w;
      // Khổ ngang có thẻ: tiêu đề dừng trước ô thẻ ở góc phải trên.
      if (coThe && !laDoc()) { rong = Math.min(rong, oBoCuc('the').x - KHOANG_THE - o.x); }
      // cat-dan: nhãn chữ hoa trên dải băng dính màu của cảnh, ở góc trái trên của ô, vào ở 0,4 s; không gạch chân.
      if (catDan) {
        return [chu('tieu-de', noiDung, o.x, o.y, rong, o.h, demKyTu(noiDung) <= 40 ? CO_NHAN : CO_NHAN_NHO, batDau, { mau: 'bang', bang: true })];
      }
      var co = rong < o.w && demKyTu(noiDung) > 40 ? 32 : 40;
      var c = chu('tieu-de', noiDung, o.x, o.y, rong, o.h, co, batDau, { mau: 'nhan', day: true });
      var w = Math.min(rong, Math.max(240, demKyTu(noiDung) * co * 0.6));
      var y = o.y + o.h + 14;
      return [c, net('gach', duongQua([[o.x, y], [o.x + w, y]], 7), c.batDau + c.thoiLuong, 0.4, { mau: 'nhan', quay: false })];
    }
    // Cột phụ (ô `cot-phu`, khổ ngang là cột phải x 900, y 200, rộng 320, cao 380) cho cảnh có `hinh` hoặc `anh`.
    // Hình lùi 10 hai bên, 40 từ đỉnh. Ảnh thấp hơn ô 30 để hai dòng nguồn dưới khung (trải hết bề rộng cột) vẫn
    // nằm trên vạch phụ đề.
    // Nhân vật dẫn chuyện (du.nhanVat, cảnh có `tu-the`) cũng chiếm cột phụ; chỉ người que được vẽ ở đây.
    var coCot = !!(du.hinh || du.anh || du.nhanVat);
    // Nhân vật trong ô `o`: cao 310 đơn vị (kể cả bật nhảy) co giãn vừa ô, chân ở đáy ô lùi 10 (chỗ cho giày và viền sticker), giữa ô; quay mặt về
    // phía nội dung (lật khi ô nằm ở nửa phải khung, `lat` đưa vào thì theo đó). Bật vào ở 0,2 s trong 0,4 s;
    // cat-dan: sticker viền trắng, góc xoay ±3° từ prng(số cảnh). Không bút, máy quay bỏ qua.
    function nhanVat(o, lat) {
      var nv = du.nhanVat;
      var ti = Math.min((o.h - 16) / 310, o.w / 300);
      var x = o.x + o.w / 2, y = o.y + o.h - 10;
      if (typeof lat !== 'boolean') { lat = x > root.THI_KHO.lay().rong / 2 + 1; }
      return { id: 'nhan-vat', kieu: 'nhan-vat', tuThe: nv.tuThe, mauAo: nv.mauAo || 'vang', x: x, y: y, ti: ti, lat: lat,
        sticker: catDan, goc: catDan ? xoayDan() * 6 - 3 : 0, batDau: 0.2, thoiLuong: 0.4, tay: false, quay: false,
        hop: { x: x - 150 * ti, y: y - 310 * ti, w: 300 * ti, h: 310 * ti } };
    }
    function cot() {
      if (du.nhanVat) { return du.nhanVat.kieu === 'nguoi-que' ? [nhanVat(oCanh('cot-phu'))] : []; }
      // cat-dan: hình chính hiện ở 0,3 s, trước tiêu đề và chữ.
      var batDau = catDan ? 0.3 : (du.moc && du.moc.length ? du.moc[0] : 1.0);
      var o = oCanh('cot-phu');
      if (du.hinh) {
        // Cột phụ thấp lại (khổ dọc có thẻ) thì hình nhỏ theo chiều cao ô, giữa ô.
        var kich = coThe && laDoc() ? Math.min(o.w - 20, o.h - 40) : o.w - 20;
        return [hinh('hinh', du.hinh, o.x + (o.w - kich) / 2, o.y + 40, kich, batDau)];
      }
      if (du.anh) { return [anh('anh', du.anh, o.x, o.y, o.w, o.h - 30, batDau, { viTriNguon: 'duoi', oNguon: { x: o.x, rong: o.w } })]; }
      return [];
    }
    // Thẻ thông tin (du.the = {nhan, giaTri, chuThich}): hiện sau khi mục chữ đầu tiên của cảnh xong 0,3 s. Ô thẻ là
    // ô `the`, hoặc `o` do cảnh đưa (bìa khổ dọc). Ba hàng: nhãn chữ hoa nhỏ, giá trị (một khối không ngắt, thu chữ
    // tới 70 % khi dài), chú thích hai dòng; không chú thích thì thẻ thấp hơn một hàng.
    //   viet-tay: khung nét vẽ tay, nhãn, giá trị, chú thích viết lần lượt bằng bút.
    //   cat-dan: giấy trắng ngà viền đen, bóng lệch (cat-dan.css), cả thẻ trượt vào cùng lúc.
    function the(kq, o) {
      var d = du.the;
      o = o || oBoCuc('the');
      var dau0 = kq.filter(function (m) { return m.kieu === 'chu'; }).sort(function (a, b) { return a.batDau - b.batDau; })[0];
      var bd = dau0 ? dau0.batDau + dau0.thoiLuong + 0.3 : 1.0;
      var h = d.chuThich ? o.h : o.h - 44;
      var x = o.x + LE_THE, w = o.w - 2 * LE_THE;
      var ds = [];
      if (catDan) {
        ds.push(chu('the-nen', '', o.x, o.y, o.w, h, 16, bd, { mau: 'the-nen', quay: false }));
      } else {
        ds.push(net('the-khung', hopQua(o.x, o.y, o.w, h, 17), bd, 0.5, { quay: false }));
      }
      var nhan = chu('the-nhan', d.nhan, x, o.y + 10, w, 20, 13, catDan ? bd : bd + 0.3, { mau: 'the-nhan' });
      var gt = chu('the-gia-tri', d.giaTri, x, o.y + 30, w, 58, 44, nhan.batDau + (catDan ? 0 : nhan.thoiLuong),
        { mau: 'the-gia-tri', khongCum: true, khoi: [demKyTu(d.giaTri, true)] });
      ds.push(nhan, gt);
      if (d.chuThich) {
        ds.push(chu('the-chu-thich', d.chuThich, x, o.y + 90, w, 44, 16, gt.batDau + (catDan ? 0 : gt.thoiLuong), { mau: 'the-chu-thich' }));
      }
      return ds;
    }
    // Dòng tài liệu (du.taiLieu, đã có "Nguồn: ") trong ô `tai-lieu`, đáy ô; ảnh của cảnh có nguồn thì dòng nguồn ảnh
    // xếp ngay trên (hai dòng không bao giờ chồng nhau). Hiện mờ dần từ 1,0 s; không bút, máy quay bỏ qua.
    function taiLieu() {
      var o = oBoCuc('tai-lieu');
      var dongs = (du.anh && du.anh.nguon ? [du.anh.nguon] : []).concat([du.taiLieu]);
      var batDau = dau(1.0, 0.6);
      return { id: 'tai-lieu', kieu: 'nguon', dongs: dongs, x: o.x, y: o.y, rong: o.w, cao: o.h, co: laDoc() ? 13 : 12,
        batDau: batDau, thoiLuong: Math.max(0.05, Math.min(0.3, gh - 0.2 - batDau)), quay: false, tay: false };
    }
    // Mục của cảnh cộng thẻ và dòng tài liệu (nếu có); `oThe`: ô thẻ riêng của cảnh.
    function them(kq, oThe) {
      var ds = kq.slice();
      if (coThe) { ds = ds.concat(the(kq, oThe)); }
      if (du.taiLieu) { ds.push(taiLieu()); }
      return ds;
    }
    return { chu: chu, net: net, hinh: hinh, anh: anh, tieuDe: tieuDe, cot: cot, coCot: coCot, gh: gh, o: oCanh, coThe: coThe, them: them,
      nhanVat: nhanVat };
  }

  // Nhịp viết của mục chữ: tổng ký tự, hệ số kéo (chữ nảy), và lúc ký tự thứ i hiện ra (viết tay: khi
  // round(p * tổng) > i; nảy: lúc ký tự i bắt đầu nảy).
  function nhipChu(m) {
    var D = root.THI_DONG;
    var tong = demKyTu(m.chu, m.khongCum);
    var keo = m.nay ? Math.max(1, D.thoiGianNay(tong) / m.thoiLuong) : 1;
    return { tong: tong, keo: keo, luc: function (i) { return m.nay ? m.batDau + D.LECH_NAY * i / keo : lucKyTu(m, i, tong); } };
  }
  // Cụm nhấn của mục chữ với lúc nổ `no` và độ dài `daiNo` (thuần: dùng chung cho khung hình và âm thanh).
  function lichCum(m, nh, tu, gh) {
    var D = root.THI_DONG;
    var N = root.THI_NHAN;
    return (m.khongCum ? [] : N.tachCum(m.chu)).map(function (c) {
      var cuoi = c.viTri + Math.max(1, c.dai) - 1;
      var xong = m.nay ? m.batDau + (D.LECH_NAY * cuoi + D.NAY) / nh.keo : nh.luc(cuoi);
      var lich = N.lichNo(N.thoiDiemNhan(c, tu || [], m.batDau, xong), xong, gh);
      c.no = lich.no;
      c.daiNo = lich.dai;
      return c;
    });
  }

  // Sự kiện âm thanh của cảnh [{t, loai, dai}], tính từ cùng các mục và mốc như khung hình:
  //   but    mục chữ/nét/hình đang vẽ (dai = thời lượng vẽ; đoạn chồng nhau gộp lại, tổng co về ≤ 40% cảnh);
  //   ting   mục có `am: 'ting'` (ý, bước, nhánh, mốc, cột, lát, lựa chọn) bắt đầu hiện;
  //   chuyen đầu cảnh có chuyển cảnh;  tictac mỗi giây đếm ngược;  dung lúc hiện đáp án;  nhan lúc cụm nhấn nổ.
  // Sắp theo t, không trùng, mọi t (và cuối đoạn bút) trong [0, thoiLuong − 0,1]; t làm tròn xuống mili giây.
  var AM_LOAI = ['chuyen', 'but', 'ting', 'nhan', 'tictac', 'dung'];
  var BUT_TOI_DA = 0.4;
  function msDuoi(x) { return Math.floor(x * 1000 + 1e-6) / 1000; }
  function suKienCua(du) {
    var gh = du.thoiLuong;
    var het = msDuoi(gh - 0.1);
    var ds = [];
    var but = [];
    if (kieuChuyen(du)) { ds.push({ t: 0, loai: 'chuyen' }); }
    root.THI_CANH[du.loai].muc(du).forEach(function (m) {
      if (m.am === 'ting') { ds.push({ t: m.batDau, loai: 'ting' }); }
      if (m.kieu === 'chu' && !m.dong) {
        lichCum(m, nhipChu(m), du.tu, gh).forEach(function (c) { if (c.daiNo > 0) { ds.push({ t: c.no, loai: 'nhan' }); } });
      }
      // Chữ nảy, dòng số của thí nghiệm, ảnh, dòng tài liệu, chữ trượt và sticker (cat-dan) không có ngòi bút.
      if (m.dong || m.nay || m.kieu === 'anh' || m.kieu === 'nguon' || m.kieu === 'nhan-vat' || m.truot || m.sticker) { return; }
      (m.phan || [m]).forEach(function (p) { but.push([p.batDau, p.batDau + p.thoiLuong]); });
    });
    var q = du.cauHoi;
    if (q) {
      for (var k = 0; k < q.cho; k++) { ds.push({ t: q.batDauDem + k, loai: 'tictac' }); }
      ds.push({ t: q.batDauGiai, loai: 'dung' });
    }
    // Bút: kẹp vào [0, het], gộp đoạn chồng nhau, rồi co đều độ dài nếu tổng vượt 40% cảnh.
    but = but.map(function (d) { return [Math.max(0, d[0]), Math.min(het, d[1])]; })
      .filter(function (d) { return d[1] > d[0]; })
      .sort(function (a, b) { return a[0] - b[0]; });
    var gop = [];
    but.forEach(function (d) {
      var cuoi = gop[gop.length - 1];
      if (cuoi && d[0] <= cuoi[1]) { cuoi[1] = Math.max(cuoi[1], d[1]); } else { gop.push([d[0], d[1]]); }
    });
    var tong = gop.reduce(function (s, d) { return s + d[1] - d[0]; }, 0);
    var co = tong > BUT_TOI_DA * gh ? BUT_TOI_DA * gh / tong : 1;
    gop.forEach(function (d) {
      var dai = msDuoi((d[1] - d[0]) * co);
      if (dai > 0) { ds.push({ t: d[0], loai: 'but', dai: dai }); }
    });
    var da = {};
    return ds.map(function (e) { return { t: msDuoi(e.t), loai: e.loai, dai: e.dai || 0 }; })
      .filter(function (e) {
        var khoa = e.loai + '@' + e.t;
        if (e.t < 0 || e.t > het || da[khoa]) { return false; }
        da[khoa] = true;
        return true;
      })
      .sort(function (a, b) { return a.t - b.t || AM_LOAI.indexOf(a.loai) - AM_LOAI.indexOf(b.loai); });
  }

  function matTran(s) {
    if (Math.abs(s.z - 1) < 1e-9 && Math.abs(s.tx) < 1e-6 && Math.abs(s.ty) < 1e-6) { return 'none'; }
    return 'matrix(' + s.z + ',0,0,' + s.z + ',' + s.tx + ',' + s.ty + ')';
  }

  function khoiDong(du) {
    var H = root.THI_HINH;
    var T = root.THI_BAN_TAY;
    var Q = root.THI_MAY_QUAY;
    var khung = document.getElementById('khung');
    var loai = root.THI_CANH[du.loai];
    var muc = loai.muc(du);
    var mucVe = tachPhan(muc);
    var co = du.co || {};
    var gh = du.thoiLuong;
    var thiNghiem = du.loai === 'thi-nghiem';
    var lau = giayLau(du);
    var kieu = kieuChuyen(du);
    // Lớp ảnh cảnh trước: div.nen-bao (bóng đổ, thứ tự lớp) chứa img và lớp phủ div.nen-phu (cùng biến đổi, độ mờ,
    // cắt). Lau bảng nằm dưới lớp bảng để giẻ (trong lớp bảng) đè lên; kiểu khác nằm trên lớp bảng cảnh mới.
    var nen = [];
    var loe = null;
    function lopNen(id) {
      var bao = document.createElement('div');
      bao.className = 'nen-bao';
      if (kieu !== 'lau-bang') { bao.style.zIndex = '1'; }
      var img = document.createElement('img');
      img.id = id;
      img.src = du.nenTruoc;
      var phu = document.createElement('div');
      phu.className = 'nen-phu';
      bao.appendChild(img);
      bao.appendChild(phu);
      khung.appendChild(bao);
      return { bao: bao, img: img, phu: phu };
    }
    if (kieu && du.nenTruoc) {
      nen.push(lopNen('nen-truoc'));
      if (kieu === 'mo-man') { nen.push(lopNen('nen-truoc-2')); }
      if (kieu === 'phong') {
        loe = document.createElement('div');
        loe.id = 'loe-chuyen';
        khung.appendChild(loe);
      }
    }
    if (co.chuDong) { khung.className = 'chu-dong'; }
    var goc = document.createElement('div');
    goc.id = 'bang';
    khung.appendChild(goc);
    // Dòng nguồn nhạc nền (cảnh cuối, 4 s cuối video): nằm ngoài lớp bảng nên không theo máy quay hay chuyển cảnh.
    var nhacNguon = null;
    if (du.nhacNguon && du.nhacNguon.chu) {
      nhacNguon = document.createElement('div');
      nhacNguon.id = 'nhac-nguon';
      nhacNguon.textContent = du.nhacNguon.chu;
      nhacNguon.style.display = 'none';
      khung.appendChild(nhacNguon);
    }
    // Khung loạt (tên loạt, "0k/N"): cùng lớp đứng yên ngoài lớp bảng, hiện suốt cảnh.
    if (du.loat) { root.THI_KHUNG_LOAT.dung(khung, du); }
    var svg = document.createElementNS(NS, 'svg');
    svg.setAttribute('class', 've');
    var kho = root.THI_KHO.lay();
    svg.setAttribute('viewBox', '0 0 ' + kho.rong + ' ' + kho.cao);
    goc.appendChild(svg);
    // cat-dan: nền giấy dưới mọi lớp, màu nhãn của cảnh, bộ lọc bóng sticker (runtime/cat-dan.js).
    if (chuDe(du).ten === 'cat-dan') { root.THI_CAT_DAN.dung(khung, svg, du); }
    var ds = muc.map(function (m) {
      var el;
      if (m.kieu === 'net') {
        el = document.createElementNS(NS, 'path');
        el.setAttribute('d', m.d);
        el.setAttribute('pathLength', '1');
        el.setAttribute('class', 'net ' + m.mau);
        el.style.strokeWidth = String(m.day);
        el.style.strokeDasharray = '1';
        svg.appendChild(el);
      } else if (m.kieu === 'hinh') {
        el = H.taoHinh(svg, m);
      } else if (m.kieu === 'anh') {
        el = H.taoAnh(goc, m);
      } else if (m.kieu === 'nhan-vat') {
        el = root.THI_NHAN_VAT.tao(svg, m);
      } else if (m.kieu === 'nguon') {
        // Dòng tài liệu (và dòng nguồn ảnh xếp trên): khối neo đáy ô, dòng dài thì lên trên.
        el = document.createElement('div');
        el.className = 'dong-nguon';
        el.style.left = m.x + 'px';
        el.style.top = m.y + 'px';
        el.style.width = m.rong + 'px';
        el.style.height = m.cao + 'px';
        el.style.fontSize = m.co + 'px';
        el.style.opacity = '0';
        m.dongs.forEach(function (chuDong) {
          var d = document.createElement('div');
          d.className = 'dong';
          d.textContent = chuDong;
          el.appendChild(d);
        });
        goc.appendChild(el);
      } else {
        el = document.createElement('div');
        el.className = 'chu ' + m.can + ' ' + m.mau + (m.day ? ' day' : '');
        el.setAttribute('data-id', m.id);
        el.style.left = m.x + 'px';
        el.style.top = m.y + 'px';
        el.style.width = m.rong + 'px';
        el.style.height = m.cao + 'px';
        el.style.fontSize = m.co + 'px';
        goc.appendChild(el);
        // Nhãn tiêu đề cat-dan: dải băng dính (một dải mỗi dòng, dựng trong doHop) nằm dưới chữ, trong lớp vẽ.
        if (m.bang) {
          var bang = document.createElementNS(NS, 'g');
          bang.setAttribute('class', 'bang-dinh');
          svg.appendChild(bang);
          return { m: m, el: el, bang: bang };
        }
      }
      return { m: m, el: el };
    });
    var theoId = {};
    ds.forEach(function (o) { theoId[o.m.id] = o; });
    // Chữ: số chạy và cụm nhấn. Thời điểm tính trước từ mục và du.tu (thuần); hộp cụm đo trong doHop.
    var D = root.THI_DONG;
    var N = root.THI_NHAN;
    var hatNhan = 0;
    ds.forEach(function (o) {
      var m = o.m;
      if (m.kieu !== 'chu' || m.dong) { return; }
      var nh = nhipChu(m);
      o.tong = nh.tong;
      o.keo = nh.keo;
      o.so = viTriSo(m.chu, m.khongCum).map(function (s) {
        var bd = nh.luc(s.viTri);
        return { gtri: s.gtri, chuSo: s.chuSo, batDau: bd, dai: Math.min(0.8, Math.max(0, gh - 0.2 - bd)) };
      });
      o.cum = lichCum(m, nh, du.tu, gh).map(function (c) {
        c.hat = ++hatNhan;
        if (c.kieu !== 'to') {
          c.net = document.createElementNS(NS, 'path');
          c.net.setAttribute('pathLength', '1');
          c.net.setAttribute('class', 'nhan-net ' + c.kieu);
          c.net.setAttribute('data-nhan', m.id + '-' + c.k);
          c.net.style.strokeDasharray = '1';
          svg.appendChild(c.net);
        }
        return c;
      });
    });
    function datChu(o, t) {
      var m = o.m;
      var so = o.so.map(function (s) { return D.soChay(t, s.batDau, s.dai, s.gtri, s.chuSo); });
      var html;
      if (m.truot) {
        // Chữ trượt (cat-dan): hiện đủ chữ (mục viết theo phần: đủ các phần đã tới), trượt và mờ dần 0,35 s.
        var n = m.phan ? m.phan.reduce(function (k, p) { return k + (t >= p.batDau ? p.ky : 0); }, 0) : o.tong;
        html = catDanhDau(m.chu, n, so, null, m.khongCum, m.khoi, m.khoiNgat);
        var v = root.THI_CAT_DAN.truotChu(tienDoTruot(m, t), m.bang);
        [o.el, o.bang].forEach(function (el) {
          if (!el) { return; }
          el.style.opacity = v.opacity;
          el.style.transform = v.transform;
        });
      } else if (m.nay) {
        var tt = m.batDau + (t - m.batDau) * o.keo;
        html = catDanhDau(m.chu, o.tong, so, function (i) { return D.nayChu(i, o.tong, tt, m.batDau); });
      } else {
        html = catDanhDau(m.chu, kyTuHien(m, t, o.tong), so, null, m.khongCum, m.khoi, m.khoiNgat);
      }
      o.el.innerHTML = m.day ? '<span class="trong">' + html + '</span>' : html;
      o.cum.forEach(function (c) {
        var p = tienDo(t, c.no, c.daiNo);
        var pe = D.easeInOut(p);
        var sp = o.el.querySelector('[data-cum="' + c.k + '"]');
        if (c.kieu === 'to') {
          sp.style.backgroundSize = lam3(100 * pe) + '% 100%';
        } else {
          c.net.style.strokeDashoffset = String(1 - pe);
          c.net.style.opacity = pe > 0 ? '1' : '0';
        }
        // Cụm một dòng nảy nhẹ 1 → 1,12 → 1 (cần inline-block; cụm nhiều dòng giữ nguyên để không đổi ngắt dòng).
        // Độ phình giới hạn theo chỗ trống hai bên (đo trong doHop) để không chạm chữ bên cạnh.
        if (co.chuDong && c.motDong) {
          sp.style.display = 'inline-block';
          sp.style.transform = p > 0 && p < 1 ? 'scale(' + lam3(1 + c.nay * Math.sin(Math.PI * p)) + ')' : 'none';
        }
      });
    }
    if (loai.dung) { loai.dung(goc, du); }
    var tay = null;
    if (co.banTay && !thiNghiem) {
      goc.insertAdjacentHTML('beforeend', T.SVG);
      tay = goc.lastElementChild;
    }

    function datMuc(t) {
      ds.forEach(function (o) {
        var p = tienDo(t, o.m.batDau, o.m.thoiLuong);
        if (o.m.kieu === 'net') {
          o.el.style.strokeDashoffset = String(1 - p);
          o.el.style.opacity = p > 0 ? '1' : '0';
        } else if (o.m.kieu === 'hinh') {
          H.datHinh(o.el, p);
        } else if (o.m.kieu === 'anh') {
          H.datAnh(o.el, o.m, p, t, gh, du.so);
        } else if (o.m.kieu === 'nguon') {
          o.el.style.opacity = String(lam3(p));
        } else if (o.m.kieu === 'nhan-vat') {
          root.THI_NHAN_VAT.dat(o.el, o.m, t);
        } else if (!o.m.dong) {
          datChu(o, t);
        }
      });
      if (loai.capNhat) { loai.capNhat(goc, du, t); }
    }

    // Chỗ trống (px) giữa cụm `sp` và chữ gần nhất cùng dòng bên trái/phải (hoặc mép ô chữ).
    function choTrong(el, sp) {
      var r = sp.getBoundingClientRect();
      var eb = el.getBoundingClientRect();
      var trai = r.left - eb.left;
      var phai = eb.right - r.right;
      var di = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
      var rg = document.createRange();
      var n;
      while ((n = di.nextNode())) {
        if (sp.contains(n)) { continue; }
        for (var i = 0; i < n.data.length; i++) {
          if (/\s/.test(n.data[i])) { continue; }
          rg.setStart(n, i);
          rg.setEnd(n, i + 1);
          var c = rg.getBoundingClientRect();
          if (c.width <= 0 || c.bottom <= r.top + 2 || c.top >= r.bottom - 2) { continue; }
          if (c.right <= r.left + 0.5) { trai = Math.min(trai, r.left - c.right); }
          else if (c.left >= r.right - 0.5) { phai = Math.min(phai, c.left - r.right); }
        }
      }
      return Math.min(trai, phai);
    }

    // Hộp bao và điểm đầu/cuối của từng mục ở trạng thái cuối, đo khi Z = 1. Đo một lần, sau khi font đã nạp.
    var hop = null;
    var dauCuoi = {};
    // Mục có khối không ngắt (công thức, giá trị thẻ): khối nào rộng hơn ô (hay các khối cao quá ô) thì thu cỡ chữ theo
    // bậc 5 % tới 70 %. Khối vẫn rộng ở 70 % mà có khoảng trắng (chữ dài kiểu vi.11) được xuống dòng ở khoảng trắng như
    // vi.11 (m.khoiNgat), rồi thu lại từ 100 % chỉ xét các khối còn lại: số hạng liền trong cùng biểu thức vẫn được thu
    // tới 70 % như khi đo kiem.DOAN_LIEN. Khối liền vẫn rộng ở 70 % thì ghi vào o.tran (kiemTran báo `phan:<đoạn>`);
    // giá trị thẻ vẫn rộng, hay khối vẫn cao quá ô, thì ô chữ tràn như thường.
    function thuKhoi(o) {
      var m = o.m;
      function cac() { return Array.prototype.slice.call(o.el.querySelectorAll('span.phan')); }
      function rongQua(sp) { return sp.getBoundingClientRect().width > o.el.clientWidth + 0.5; }
      // Cũng thu khi các khối (mỗi khối một dòng vì không ngắt) cao quá ô: thu chữ thì nhiều khối nằm chung một dòng.
      function cao() { return o.el.scrollHeight > o.el.clientHeight + 1; }
      function ngat(k) { return !!m.khoiNgat && m.khoiNgat.indexOf(k) >= 0; }
      function rongCon() { return cac().some(function (sp, k) { return !ngat(k) && rongQua(sp); }); }
      function thu() {
        var tl = 1;
        o.el.style.fontSize = m.co + 'px';
        while ((rongCon() || cao()) && tl > 0.7 + 1e-9) {
          tl = Math.round((tl - 0.05) * 100) / 100;
          o.el.style.fontSize = lam3(m.co * tl) + 'px';
        }
      }
      thu();
      o.tran = [];
      if (!rongCon()) { return; }
      var ngatMoi = [];
      cac().forEach(function (sp, k) {
        if (!rongQua(sp)) { return; }
        // Bỏ toán tử đầu đoạn (`= `, `≈ `…) trước khi xét: khoảng trắng sau toán tử không phải chỗ ngắt của số hạng.
        var than = (m.khoiChu ? m.khoiChu[k] : sp.textContent).trim();
        if (TOAN_TU.indexOf(than[0]) >= 0 && than[1] === ' ') { than = than.slice(2); }
        if (/\s/.test(than)) { ngatMoi.push(k); }
      });
      if (ngatMoi.length) {
        m.khoiNgat = ngatMoi;
        datChu(o, 1e6);
        thu();
      }
      cac().forEach(function (sp, k) {
        if (ngat(k) || !rongQua(sp) || !m.khoiChu) { return; }
        var than = m.khoiChu[k].trim();
        if (TOAN_TU.indexOf(than[0]) >= 0 && than[1] === ' ') { than = than.slice(2); }
        o.tran.push(than);
      });
    }

    function doHop() {
      goc.style.transform = 'none';
      datMuc(1e6);
      ds.forEach(function (o) { if (o.m.khoi) { thuKhoi(o); } });
      var k = khung.getBoundingClientRect();
      var kq = {};
      ds.forEach(function (o) {
        var m = o.m;
        if (m.dong || m.kieu === 'nguon') { return; }
        if (m.kieu === 'net') {
          var b = o.el.getBBox();
          kq[m.id] = { x: b.x, y: b.y, w: b.width, h: b.height };
        } else if (m.kieu === 'hinh') {
          kq[m.id] = { x: m.x, y: m.y, w: m.kich, h: m.kich };
        } else if (m.kieu === 'anh') {
          kq[m.id] = { x: m.x, y: m.y, w: m.rong, h: m.cao };
        } else if (m.kieu === 'nhan-vat') {
          kq[m.id] = m.hop;
        } else {
          var r = document.createRange();
          r.selectNodeContents(o.el);
          var cac = r.getClientRects();
          var bao = r.getBoundingClientRect();
          if (!cac.length || bao.width <= 0) { return; }
          kq[m.id] = { x: bao.left - k.left, y: bao.top - k.top, w: bao.width, h: bao.height };
          var a = cac[0], z = cac[cac.length - 1];
          dauCuoi[m.id] = {
            dau: { x: a.left - k.left, y: a.top + 0.8 * a.height - k.top },
            cuoi: { x: z.right - k.left, y: z.top + 0.8 * z.height - k.top }
          };
        }
      });
      // Dải băng dính của nhãn tiêu đề (cat-dan): một dải cho mỗi dòng chữ ở trạng thái cuối.
      ds.forEach(function (o) {
        if (!o.bang) { return; }
        var r = document.createRange();
        r.selectNodeContents(o.el);
        var dong = [];
        Array.prototype.forEach.call(r.getClientRects(), function (c) {
          if (c.width <= 0) { return; }
          var h = { x: c.left - k.left, y: c.top - k.top, w: c.width, h: c.height };
          var cung = dong.filter(function (d) { return Math.abs(d.y + d.h / 2 - (h.y + h.h / 2)) < h.h / 2; })[0];
          if (!cung) { dong.push(h); return; }
          var x2 = Math.max(cung.x + cung.w, h.x + h.w), y2 = Math.max(cung.y + cung.h, h.y + h.h);
          cung.x = Math.min(cung.x, h.x);
          cung.y = Math.min(cung.y, h.y);
          cung.w = x2 - cung.x;
          cung.h = y2 - cung.y;
        });
        o.bang.innerHTML = root.THI_CAT_DAN.bangTieuDe(du.so, dong).map(function (b) {
          return '<polygon points="' + b.points + '"/>';
        }).join('');
      });
      // Hộp cụm nhấn (từng dòng) ở trạng thái cuối: vòng khoanh, nét gạch, và cụm nào nằm gọn một dòng.
      ds.forEach(function (o) {
        (o.cum || []).forEach(function (c) {
          var sp = o.el.querySelector('[data-cum="' + c.k + '"]');
          var cac = Array.prototype.map.call(sp.getClientRects(), function (r) {
            return { x: r.left - k.left, y: r.top - k.top, w: r.width, h: r.height };
          }).filter(function (r) { return r.w > 0; });
          c.motDong = cac.length === 1;
          c.nay = c.motDong && co.chuDong ? Math.max(0, Math.min(0.12, 2 * (choTrong(o.el, sp) - 1) / Math.max(1, cac[0].w))) : 0;
          if (!c.net || !cac.length) { return; }
          if (c.kieu === 'gach') {
            c.net.setAttribute('d', N.duongGach(cac, c.hat));
          } else {
            // Một vòng mỗi dòng; cao hơn dòng chữ tối đa 3 px, không chạm dòng trên/dưới (khoảng giữa hai dòng − 1 px).
            var dong = parseFloat(getComputedStyle(o.el).lineHeight) || 0;
            var day = Math.min(3, Math.min.apply(null, cac.map(function (r) { return dong - r.h; })) - 1);
            c.net.setAttribute('d', N.duongKhoanh(cac, c.hat, day));
          }
        });
      });
      return kq;
    }

    function ngoiCua(cam) {
      var k = khung.getBoundingClientRect();
      return function (m, p) {
        var o = theoId[m.id];
        if (m.kieu === 'net') {
          var L = o.el.getTotalLength();
          var d = o.el.getPointAtLength(kep(p, 0, 1) * L);
          return { x: d.x, y: d.y };
        }
        if (m.kieu === 'hinh') { return H.ngoiHinh(o.el, m, p); }
        var dc = dauCuoi[m.id] || { dau: { x: m.x, y: m.y + m.co }, cuoi: { x: m.x, y: m.y + m.co } };
        // Mục viết theo phần: giữa hai phần ngòi bút nằm ở cuối phần đã viết (span.ngoi của trạng thái hiện tại).
        var s = (p > 0 && p < 1) || m.phan ? o.el.querySelector('.ngoi') : null;
        if (!s) { return p >= 0.5 ? dc.cuoi : dc.dau; }
        var r = s.getBoundingClientRect();
        return { x: (r.left - k.left - cam.tx) / cam.z, y: (r.top + 0.8 * r.height - k.top - cam.ty) / cam.z };
      };
    }

    // Trạng thái chuyển cảnh tại t (null khi không có ảnh cảnh trước hoặc đã chuyển xong): đặt các lớp ảnh cũ, lớp loé,
    // và trả biến đổi của lớp bảng mới để ghép với máy quay.
    function datNen(t) {
      if (!nen.length) { return null; }
      var s = t >= 0 && t < lau ? root.THI_CHUYEN.trangThai(kieu, t, lau, du.so) : null;
      [s && s.nen, s && s.nen2].forEach(function (l, i) {
        var o = nen[i];
        if (!o) { return; }
        if (!l || l.opacity <= 0) {
          o.img.style.display = 'none';
          o.phu.style.display = 'none';
          o.bao.style.filter = '';
          return;
        }
        [o.img, o.phu].forEach(function (el) {
          el.style.transform = l.transform;
          el.style.opacity = String(l.opacity);
          el.style.clipPath = l.clipPath;
        });
        o.img.style.display = 'block';
        o.phu.style.display = l.phu ? 'block' : 'none';
        o.phu.style.background = l.phu || '';
        o.bao.style.filter = l.filter || '';
      });
      if (loe) { loe.style.opacity = s ? String(s.loe) : '0'; }
      return s ? s.moi : null;
    }

    function dat(t, noiBo) {
      if (!noiBo && !hop) { hop = doHop(); }
      datMuc(t);
      var moi = datNen(t);
      var cam = noiBo ? { z: 1, tx: 0, ty: 0 } : Q.tinh(mucVe, hop, t, gh, { mayQuay: co.mayQuay === true, day: thiNghiem });
      // Loại cảnh tự lái máy quay ngoài các mục (câu hỏi: đẩy nhẹ trong lúc đếm ngược).
      if (!noiBo && co.mayQuay === true && loai.mayQuay) { cam = loai.mayQuay(du, t, cam); }
      var bd = matTran(cam);
      if (moi && moi.transform !== 'none') { bd = moi.transform + (bd === 'none' ? '' : ' ' + bd); }
      goc.style.transform = bd;
      goc.style.opacity = moi && moi.opacity !== 1 ? String(moi.opacity) : '';
      goc.style.clipPath = moi && moi.clipPath !== 'none' ? moi.clipPath : '';
      if (nhacNguon) {
        var pn = noiBo ? 0 : tienDo(t, du.nhacNguon.tu, 0.3);
        nhacNguon.style.display = pn > 0 ? 'block' : 'none';
        nhacNguon.style.opacity = String(lam3(pn));
      }
      if (!tay) { return; }
      var v = noiBo ? { hien: false } : T.viTri(mucVe, t, ngoiCua(cam), T.NGHI, { chuyen: kieu, giayLau: lau, gh: gh });
      tay.style.display = v.hien ? 'block' : 'none';
      if (!v.hien) { return; }
      tay.setAttribute('data-kieu', v.kieu);
      // Tay nằm trong lớp bảng để theo máy quay, nhưng giữ cỡ trên màn hình không đổi khi phóng.
      tay.style.transform = 'translate(' + v.x + 'px,' + v.y + 'px) scale(' + (CO_TAY / cam.z) + ')';
    }
    root.datThoiDiem = function (t) { dat(t, false); };
    root.THI_VIDEO.thoiDiemCuoi = function () {
      return du.thoiLuong - 0.2;
    };
    // Kiểm tràn ở trạng thái cuối, máy quay Z = 1, không bàn tay, không nền cảnh trước.
    root.THI_VIDEO.kiemTran = function () {
      dat(1e6, false);
      goc.style.transform = 'none';
      if (tay) { tay.style.display = 'none'; }
      nen.forEach(function (o) { o.img.style.display = 'none'; o.phu.style.display = 'none'; });
      if (loe) { loe.style.opacity = '0'; }
      var loi = [];
      // Mép phải, mép dưới khung và vạch phụ đề (khổ ngang: 1280, 720, 620), cho phép lệch 1 px.
      var R = kho.rong + 1, C = kho.cao + 1, D = kho.day + 1;
      var cacO = goc.querySelectorAll('.chu');
      for (var i = 0; i < cacO.length; i++) {
        var el = cacO[i];
        var r = el.getBoundingClientRect();
        if (el.scrollHeight > el.clientHeight + 1 || el.scrollWidth > el.clientWidth + 1 || r.right > R || r.bottom > C) {
          loi.push(el.getAttribute('data-id'));
        }
      }
      // Dòng nguồn ảnh: nằm trong khung hình và trên vạch phụ đề.
      var ng = goc.querySelector('.anh .nguon');
      if (ng) {
        var rn = ng.getBoundingClientRect();
        if (rn.left < -1 || rn.top < -1 || rn.right > R || rn.bottom > D) { loi.push('nguon'); }
      }
      // Khối công thức (hay giá trị thẻ) vẫn rộng hơn ô sau khi thu chữ tới 70 %.
      ds.forEach(function (o) { (o.tran || []).forEach(function (p) { loi.push('phan:' + p); }); });
      // Dòng tài liệu (và nguồn ảnh xếp trên): trong khung, trên vạch phụ đề, không đè chữ hay ảnh của cảnh.
      var dn = goc.querySelector('.dong-nguon');
      if (dn) {
        var cacO2 = Array.prototype.slice.call(goc.querySelectorAll('.chu, .anh .cua-anh'));
        var giao = function (a, b) { return a.left < b.right - 0.5 && b.left < a.right - 0.5 && a.top < b.bottom - 0.5 && b.top < a.bottom - 0.5; };
        Array.prototype.forEach.call(dn.children, function (d) {
          var rd = d.getBoundingClientRect();
          var de = rd.left < -1 || rd.top < -1 || rd.right > R || rd.bottom > D || cacO2.some(function (el) {
            if (!el.classList.contains('chu')) { return giao(rd, el.getBoundingClientRect()); }
            var rg = document.createRange();
            rg.selectNodeContents(el);
            return Array.prototype.some.call(rg.getClientRects(), function (c) { return c.width > 0 && giao(rd, c); });
          });
          if (de && loi.indexOf('tai-lieu') < 0) { loi.push('tai-lieu'); }
        });
      }
      // Nhân vật: trong khung, trên vạch phụ đề, không đè dòng chữ nào của cảnh.
      var nv = svg.querySelector('g.nhan-vat');
      if (nv) {
        var rv = nv.getBoundingClientRect();
        var giaoNv = function (c) { return c.width > 0 && rv.left < c.right - 0.5 && c.left < rv.right - 0.5 && rv.top < c.bottom - 0.5 && c.top < rv.bottom - 0.5; };
        var deChu = Array.prototype.some.call(goc.querySelectorAll('.chu'), function (el) {
          var rg = document.createRange();
          rg.selectNodeContents(el);
          return Array.prototype.some.call(rg.getClientRects(), giaoNv);
        });
        if (deChu || rv.left < -1 || rv.top < -1 || rv.right > R || rv.bottom > D) { loi.push('nhan-vat'); }
      }
      // Dòng nguồn nhạc nền: trong khung hình và trên vạch phụ đề.
      if (nhacNguon) {
        var rm = nhacNguon.getBoundingClientRect();
        if (rm.left < -1 || rm.top < -1 || rm.right > R || rm.bottom > D) { loi.push('nhac-nguon'); }
      }
      // Vòng khoanh và nét gạch của cụm nhấn: trong khung hình và trên vạch phụ đề.
      var cacNet = svg.querySelectorAll('path.nhan-net');
      for (var j = 0; j < cacNet.length; j++) {
        var b = cacNet[j].getBBox();
        if (b.x < -1 || b.y < -1 || b.x + b.width > R || b.y + b.height > D) { loi.push('nhan-' + cacNet[j].getAttribute('data-nhan')); }
      }
      return loi;
    };
    var suKien = null;
    root.THI_VIDEO.suKien = function () {
      if (!suKien) { suKien = suKienCua(du); }
      return suKien;
    };
    dat(0, true);
    root.THI_VIDEO.san = true;
  }

  root.THI_CANH = root.THI_CANH || {};
  root.THI_VIDEO = {
    LAU_BANG: LAU_BANG,
    kep: kep, tienDo: tienDo, thoat: thoat, demKyTu: demKyTu, catDanhDau: catDanhDau, phanTich: phanTich, demRong: demRong, viTriSo: viTriSo,
    thoiGianViet: thoiGianViet, kyTuHien: kyTuHien, lucKyTu: lucKyTu, tachPhan: tachPhan, duongQua: duongQua, hopQua: hopQua, vongTron: vongTron, muiTen: muiTen,
    rng: rng, tachDoanCongThuc: tachDoanCongThuc, tienDoTruot: tienDoTruot, vuaKhung: vuaKhung, o: oBoCuc, doc: laDoc, tao: tao, khoiDong: khoiDong, suKienCua: suKienCua, san: false
  };
})(typeof globalThis !== 'undefined' ? globalThis : this);

(function (root) {
  'use strict';

  // Phong cách cắt dán (`phong-cach: cat-dan`, kiểu Vox): giấy xé, chấm lưới, băng dính và nền giấy vẽ bằng SVG.
  // Hàm thuần (nhận số, trả chuỗi hoặc điểm), chạy được trong Node; mọi nét "ngẫu nhiên" lấy từ PRNG có hạt giống
  // (hạt = số cảnh), nên cùng cảnh luôn ra cùng hình. Chỉ `dung` chạm DOM (trang gọi khi du.chuDe.ten là cat-dan).
  var NS = 'http://www.w3.org/2000/svg';
  var GIAY = '#f3ead7';
  // Màu mảng giấy xé ở mép: bốn màu nhãn và một màu giấy xi măng (có kẻ ô).
  var MAU_MANH = ['#e8a33d', '#1f6f78', '#c8452f', '#2f4f9e', '#d9c6a3'];
  var XI_MANG = '#d9c6a3';
  var TRUOT = 0.35;     // chữ trượt vào trong 0,35 s
  var TRUOT_LEN = 14;   // mục chữ trượt lên 14 px
  var TRUOT_NHAN = 40;  // nhãn tiêu đề trượt từ trái 40 px
  var LECH_NHAN = 4;    // dải băng dính của nhãn nghiêng sao cho đầu dải lệch không quá 4 px

  // mulberry32, cùng thuật toán với THI_VIDEO.rng.
  function prng(hat) {
    var a = hat | 0;
    return function () {
      a = a + 0x6D2B79F5 | 0;
      var t = Math.imul(a ^ a >>> 15, 1 | a);
      t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
      return ((t ^ t >>> 14) >>> 0) / 4294967296;
    };
  }
  function lam(x) { return Math.round(x * 10) / 10; }
  function chuoiDiem(ds) { return ds.map(function (p) { return lam(p[0]) + ',' + lam(p[1]); }).join(' '); }
  function mauCanh(so, bang) { return bang[(((so - 1) % bang.length) + bang.length) % bang.length]; }

  // Đa giác mép răng cưa của hộp (x, y, w, h): đi quanh chu vi theo chiều kim đồng hồ, mỗi bước 7–17 px, mỗi điểm
  // lệch vuông góc với cạnh một khoảng trong [−doRang, doRang]. Mọi điểm nằm trong hộp ± doRang.
  function giayXe(hat, x, y, w, h, doRang) {
    var r = prng(hat);
    var ds = [];
    function lech() { return (r() * 2 - 1) * doRang; }
    function canh(x0, y0, x1, y1, nx, ny) {
      var dai = Math.sqrt((x1 - x0) * (x1 - x0) + (y1 - y0) * (y1 - y0));
      var s = 0;
      while (s < dai) {
        var u = s / dai;
        var d = lech();
        ds.push([x0 + (x1 - x0) * u + nx * d, y0 + (y1 - y0) * u + ny * d]);
        s += 7 + r() * 10;
      }
    }
    canh(x, y, x + w, y, 0, 1);
    canh(x + w, y, x + w, y + h, 1, 0);
    canh(x + w, y + h, x, y + h, 0, 1);
    canh(x, y + h, x, y, 1, 0);
    return chuoiDiem(ds);
  }

  // Ô mẫu chấm lưới (halftone): một chấm bán kính `banKinh` giữa mỗi ô `buoc` × `buoc`.
  function chamLuoi(id, buoc, banKinh, mau) {
    return '<pattern id="' + id + '" width="' + buoc + '" height="' + buoc + '" patternUnits="userSpaceOnUse">' +
      '<circle cx="' + buoc / 2 + '" cy="' + buoc / 2 + '" r="' + banKinh + '" fill="' + (mau || '#2b2b2b') + '"/></pattern>';
  }

  function xoay(ds, cx, cy, goc) {
    var a = goc * Math.PI / 180, c = Math.cos(a), s = Math.sin(a);
    return ds.map(function (p) { var dx = p[0] - cx, dy = p[1] - cy; return [cx + dx * c - dy * s, cy + dx * s + dy * c]; });
  }
  // Mẩu băng dính: hình chữ nhật (cao mặc định 0,28 × dài), hai đầu răng cưa, xoay quanh tâm một góc trong
  // ±gocToiDa độ (mặc định 6). Trả {points, goc}.
  function bangDinh(hat, x, y, w, h, gocToiDa) {
    var r = prng(hat);
    h = h || Math.round(w * 0.28);
    var gmax = typeof gocToiDa === 'number' ? gocToiDa : 6;
    var goc = (r() * 2 - 1) * gmax;
    var n = Math.max(3, Math.round(h / 7));
    var rang = Math.min(4, w * 0.04);
    var ds = [[x, y], [x + w, y]];
    for (var k = 1; k < 2 * n; k++) { ds.push([x + w - (k % 2 ? rang * (0.5 + r() * 0.5) : 0), y + h * k / (2 * n)]); }
    ds.push([x + w, y + h], [x, y + h]);
    for (var j = 2 * n - 1; j >= 1; j--) { ds.push([x + (j % 2 ? rang * (0.5 + r() * 0.5) : 0), y + h * j / (2 * n)]); }
    return { points: chuoiDiem(xoay(ds, x + w / 2, y + h / 2, goc)), goc: goc };
  }
  // Nhãn tiêu đề: mỗi dòng chữ (hộp {x, y, w, h}, toạ độ khung) một dải băng dính rộng hơn chữ 14 px mỗi bên,
  // cao hơn 3 px mỗi phía; nghiêng tối đa 2 độ nhưng đầu dải không lệch quá 4 px (dòng dài nghiêng ít).
  function bangTieuDe(hat, cacDong) {
    return cacDong.map(function (d, k) {
      var w = d.w + 28;
      var gmax = Math.min(2, Math.atan(LECH_NHAN / (w / 2)) * 180 / Math.PI);
      return bangDinh(hat * 7 + k, d.x - 14, d.y - 3, w, d.h + 6, gmax);
    });
  }

  // Vùng nội dung của khổ (lề 40 hai bên, 24 phía trên, tới vạch phụ đề): mảng trang trí không che quá 15 % vùng này.
  function vungNoiDung(kho) { return { x: 40, y: 24, w: kho.rong - 80, h: kho.day - 24 }; }

  // 2–4 mảng giấy xé màu ở bốn góc và dải dưới (vùng phụ đề), chừng một nửa nằm ngoài khung; không mảng nào nằm
  // ở mép trái/phải ngang tầm chữ. Trả [{x, y, w, h, mau, points}].
  var CHO = ['tl', 'tr', 'bl', 'br', 'b'];
  function cacManh(hat, kho) {
    var r = prng(hat * 131 + 7);
    var cho = CHO.slice();
    for (var i = cho.length - 1; i > 0; i--) { var j = Math.floor(r() * (i + 1)); var tam = cho[i]; cho[i] = cho[j]; cho[j] = tam; }
    var n = 2 + Math.floor(r() * 3);
    var R = kho.rong, H = kho.cao, nho = Math.min(R, H);
    var mau0 = Math.floor(r() * MAU_MANH.length);
    return cho.slice(0, n).map(function (c, k) {
      var w = R * (0.2 + 0.12 * r());
      var h = nho * (0.22 + 0.14 * r());
      var x = c === 'b' ? R * (0.3 + 0.25 * r()) - w / 2 : (c === 'tl' || c === 'bl' ? -0.45 * w : R - 0.55 * w);
      var y = c === 'tl' || c === 'tr' ? -0.45 * h : H - (c === 'b' ? 0.4 : 0.55) * h;
      return { x: x, y: y, w: w, h: h, mau: MAU_MANH[(mau0 + k) % MAU_MANH.length], points: giayXe(hat * 16 + k, x, y, w, h, 5) };
    });
  }
  // Vùng chấm lưới: hình tròn ở một góc khung, phần lớn nằm ngoài khung. Trả {x, y, w, h, cx, cy, r}.
  function vungCham(hat, kho) {
    var r = prng(hat * 71 + 3);
    var rr = Math.min(kho.rong, kho.cao) * (0.14 + 0.06 * r());
    var phai = r() < 0.5, duoi = r() < 0.5;
    var cx = phai ? kho.rong - 0.25 * rr : 0.25 * rr;
    var cy = duoi ? kho.cao - 0.3 * rr : 0.3 * rr;
    return { x: cx - rr, y: cy - rr, w: 2 * rr, h: 2 * rr, cx: cx, cy: cy, r: rr };
  }

  // Nền giấy của cảnh: giấy kem, vân mờ (feTurbulence, seed = hạt), vết ố lớn, mảng giấy xé có bóng, vùng chấm lưới.
  function nenGiay(hat, kho, giay) {
    var R = kho.rong, H = kho.cao;
    var s = '<svg xmlns="' + NS + '" class="giay" width="' + R + '" height="' + H + '" viewBox="0 0 ' + R + ' ' + H + '">' +
      '<defs>' +
      '<filter id="van-giay" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.85" ' +
      'numOctaves="2" seed="' + hat + '" stitchTiles="stitch"/><feColorMatrix type="matrix" ' +
      'values="0 0 0 0 0.36 0 0 0 0 0.29 0 0 0 0 0.19 0 0 0 0.55 0"/></filter>' +
      '<filter id="vet-giay" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.004" ' +
      'numOctaves="3" seed="' + hat + '"/><feColorMatrix type="matrix" values="0 0 0 0 0.55 0 0 0 0 0.45 0 0 0 0 0.3 0 0 0 0.9 -0.35"/></filter>' +
      chamLuoi('cham-giay', 11, 2.4) +
      '<pattern id="o-ke" width="22" height="22" patternUnits="userSpaceOnUse"><path d="M22 0H0V22" fill="none" stroke="#8fa6b8" ' +
      'stroke-width="1" opacity="0.7"/></pattern>' +
      '</defs>' +
      '<rect width="' + R + '" height="' + H + '" fill="' + (giay || GIAY) + '"/>' +
      '<rect width="' + R + '" height="' + H + '" filter="url(#vet-giay)" opacity="0.5"/>' +
      '<rect width="' + R + '" height="' + H + '" filter="url(#van-giay)" opacity="0.3"/>';
    var c = vungCham(hat, kho);
    s += '<circle cx="' + lam(c.cx) + '" cy="' + lam(c.cy) + '" r="' + lam(c.r) + '" fill="url(#cham-giay)" opacity="0.4"/>';
    cacManh(hat, kho).forEach(function (m) {
      s += '<polygon points="' + m.points + '" fill="rgba(0,0,0,0.13)" transform="translate(2 3)"/>' +
        '<polygon points="' + m.points + '" fill="' + m.mau + '"/>';
      if (m.mau === XI_MANG) { s += '<polygon points="' + m.points + '" fill="url(#o-ke)"/>'; }
    });
    return s + '</svg>';
  }

  // Chữ trượt vào tại tiến độ p (0..1, đã chia cho 0,35 s): mục chữ trượt lên 14 px, nhãn tiêu đề trượt từ trái
  // 40 px; cùng mờ dần. Xong (p ≥ 1) thì không để lại biến đổi nào, để bố cục cuối đúng như đo.
  function truotChu(p, nhan) {
    if (p >= 1) { return { opacity: '', transform: '' }; }
    if (p <= 0) { return { opacity: '0', transform: '' }; }
    var e = 1 - Math.pow(1 - p, 3);
    var lech = Math.round((1 - e) * (nhan ? TRUOT_NHAN : TRUOT_LEN) * 100) / 100;
    return { opacity: String(Math.round(e * 1000) / 1000), transform: nhan ? 'translateX(' + (-lech) + 'px)' : 'translateY(' + lech + 'px)' };
  }

  // Trang: đặt lớp và màu nhãn của cảnh, chèn nền giấy dưới mọi lớp, và bộ lọc bóng của sticker vào lớp vẽ.
  function dung(khung, svg, du) {
    var cd = du.chuDe;
    var kho = root.THI_KHO.lay();
    khung.classList.add('cat-dan');
    khung.style.setProperty('--mau-nhan', mauCanh(du.so, cd.mauNhan));
    var nen = document.createElement('div');
    nen.className = 'nen-giay';
    nen.innerHTML = nenGiay(du.so, kho, cd.giay);
    khung.insertBefore(nen, khung.firstChild);
    svg.insertAdjacentHTML('afterbegin', '<defs><filter id="bong-dan" x="-30%" y="-30%" width="160%" height="160%">' +
      '<feDropShadow dx="0" dy="6" stdDeviation="7" flood-color="#000" flood-opacity="0.25"/></filter></defs>');
  }

  root.THI_CAT_DAN = {
    TRUOT: TRUOT, prng: prng, mauCanh: mauCanh, giayXe: giayXe, chamLuoi: chamLuoi, bangDinh: bangDinh,
    bangTieuDe: bangTieuDe, vungNoiDung: vungNoiDung, cacManh: cacManh, vungCham: vungCham, nenGiay: nenGiay,
    truotChu: truotChu, dung: dung
  };
})(typeof globalThis !== 'undefined' ? globalThis : this);

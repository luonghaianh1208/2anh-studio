(function (root) {
  'use strict';
  var V = root.THI_VIDEO;
  // Nút trung tâm là elip ở tâm ô `so-do` (CX, CY); ô nhánh (W × H) đặt trên elip lớn (RX, RY) theo góc cố định theo
  // số nhánh (độ, 0 là bên phải, chiều kim đồng hồ), nhánh 0 ở trên bên phải rồi đi vòng. Elip lớn chọn để mọi ô
  // nhánh nằm gọn trong ô `so-do` (khổ ngang: y 110..590).
  // Máy quay giữ toàn cảnh sơ đồ (mọi mục `quay: false`): phóng vào một ô nhánh ở trên đẩy các ô dưới (tới đáy ô)
  // xuống vùng phụ đề, và làm mất quan hệ giữa các nhánh với nút trung tâm.
  // Ô nhánh rộng 330, nhưng không quá 45 % bề rộng ô (khổ dọc) để hai ô nhánh cùng hàng không chạm nhau.
  var H = 80;
  function khung() {
    var o = V.o('so-do');
    var W = Math.min(330, 0.45 * o.w);
    return { W: W, CX: o.x + o.w / 2, CY: o.y + o.h / 2, RX: (o.w - W) / 2, RY: (o.h - H) / 2 };
  }
  var GOC = {
    2: [0, 180],
    3: [-40, 90, 220],
    4: [-35, 35, 145, 215],
    5: [-90, -18, 54, 126, 198],
    6: [-60, 0, 60, 120, 180, 240]
  };
  // Khổ dọc (elip lớn cao và hẹp): không đặt nhánh ngang hàng nút trung tâm; nhánh ở đỉnh, đáy và bốn góc ±30°.
  var GOC_DOC = {
    2: [-90, 90],
    3: [-90, 30, 150],
    4: [-30, 30, 150, 210],
    5: [-90, -30, 30, 150, 210],
    6: [-90, -30, 30, 90, 150, 210]
  };

  function lam(x) { return Math.round(x * 10) / 10; }
  function elip(k, rx, ry, hat) {
    var diem = [];
    for (var i = 0; i <= 30; i++) {
      var a = (-100 + 372 * i / 30) * Math.PI / 180;
      diem.push([k.CX + rx * Math.cos(a), k.CY + ry * Math.sin(a)]);
    }
    return V.duongQua(diem, hat);
  }
  // Đường cong nhánh: Bézier bậc hai từ mép elip tới mép ô nhãn, uốn sang một bên.
  function cong(a, b, uon, hat) {
    var dx = b[0] - a[0], dy = b[1] - a[1];
    var dai = Math.sqrt(dx * dx + dy * dy) || 1;
    uon = (uon < 0 ? -1 : 1) * Math.min(Math.abs(uon), 0.2 * dai);
    var c = [(a[0] + b[0]) / 2 - dy / dai * uon, (a[1] + b[1]) / 2 + dx / dai * uon];
    var diem = [];
    var n = Math.max(3, Math.round(dai / 30));
    for (var i = 0; i <= n; i++) {
      var u = i / n;
      diem.push([(1 - u) * (1 - u) * a[0] + 2 * u * (1 - u) * c[0] + u * u * b[0],
                 (1 - u) * (1 - u) * a[1] + 2 * u * (1 - u) * c[1] + u * u * b[1]]);
    }
    return V.duongQua(diem, hat);
  }

  var canh = {
    GOC: GOC,
    get TAM() { var k = khung(); return { x: k.CX, y: k.CY }; },
    muc: function (du) {
      var B = V.tao(du);
      var t = du.truong;
      var coHinh = !!du.hinh;
      var K = khung();
      var CX = K.CX, CY = K.CY, RX = K.RX, RY = K.RY, W = K.W;
      var rx = 190, ry = coHinh ? 95 : 70;
      var kq = [];
      kq.push(B.net('vong-tam', elip(K, rx, ry, 11), 0.2, 0.6, { mau: 'nhan', day: 5, quay: false }));
      var tam = t['trung-tam'][0];
      var co = V.demKyTu(tam) > 20 ? 26 : 30;
      if (coHinh) { kq.push(B.hinh('hinh', du.hinh, CX - 30, CY - 82, 60, 0.3, { mau: 'nhan', quay: false })); }
      // Chữ trung tâm rộng bằng elip tâm trừ 45 mỗi bên.
      kq.push(B.chu('trung-tam', tam, CX - (rx - 45), coHinh ? CY - 18 : CY - 37, 2 * (rx - 45), 74, co, 0.5, { can: 'giua', mau: 'nhan giua-doc', day: true, quay: false }));
      var n = t.nhanh.length;
      // Mọi ô nhánh cùng cỡ chữ: có nhánh dài hơn 30 ký tự thì cả sơ đồ dùng chữ nhỏ hơn.
      var coNhanh = t.nhanh.some(function (c) { return V.demKyTu(c) > 30; }) ? 22 : 24;
      (V.doc() ? GOC_DOC : GOC)[n].forEach(function (g, k) {
        var a = g * Math.PI / 180;
        var bx = CX + RX * Math.cos(a), by = CY + RY * Math.sin(a);
        var dx = bx - CX, dy = by - CY;
        var s = 1 / Math.sqrt(dx * dx / (rx * rx) + dy * dy / (ry * ry));
        var dai = Math.sqrt(dx * dx + dy * dy);
        var tu = [CX + dx * s + 6 * dx / dai, CY + dy * s + 6 * dy / dai];
        var c = Math.min((W / 2) / (Math.abs(dx) || 1e-9), (H / 2) / (Math.abs(dy) || 1e-9));
        var toi = [bx - dx * c - 6 * dx / dai, by - dy * c - 6 * dy / dai];
        var mau = 'm' + k;
        var chu = t.nhanh[k];
        kq.push(B.net('nhanh-' + k, cong(tu, toi, k % 2 ? -26 : 26, 70 + k), du.moc[k], 0.5, { mau: mau, am: 'ting', quay: false }));
        kq.push(B.net('o-' + k, V.hopQua(lam(bx - W / 2), lam(by - H / 2), W, H, 30 + k), du.moc[k] + 0.35, 0.4, { mau: mau, quay: false }));
        kq.push(B.chu('chu-' + k, chu, bx - W / 2 + 12, by - H / 2 + 8, W - 24, H - 16, coNhanh,
          du.moc[k] + 0.6, { can: 'giua', mau: 'giua-doc', day: true, quay: false }));
      });
      return kq;
    }
  };
  root.THI_CANH['so-do'] = canh;
})(typeof globalThis !== 'undefined' ? globalThis : this);

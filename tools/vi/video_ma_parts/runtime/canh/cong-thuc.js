(function (root) {
  'use strict';
  var V = root.THI_VIDEO;
  // `bieu-thuc` có ` | ` thì tách phần: phần k viết ở mốc câu k, các phần nối nhau trên cùng dòng (cách một khoảng
  // trắng); dòng giải thích k khi đó ở mốc câu (số phần + k).
  var TACH = ' | ';
  root.THI_CANH['cong-thuc'] = {
    muc: function (du) {
      var B = V.tao(du);
      var t = du.truong;
      var cot = B.coCot;
      var phan = t['bieu-thuc'][0].split(TACH);
      var soPhan = phan.length > 1 ? phan.length : 0;
      var bieuThuc = phan.join(' ');
      // Ô nội dung (hẹp khi có cột phụ). Khung lùi 40 trái; không có cột phụ thì chừa thêm lề phải (khung 40,
      // biểu thức 40, giải thích 50) như bản vi.11.
      // Khung biểu thức cao 150 (khổ dọc không cột phụ: 300, đủ năm dòng); dòng giải thích cách nhau 68 (khổ dọc:
      // chia đều phần ô còn lại cho 4 dòng, tối đa 110).
      var o = B.o(cot ? 'noi-dung-hep' : 'noi-dung');
      var doc = V.doc();
      var hBT = doc && !cot ? 300 : 150;
      var buoc = doc ? Math.min(110, (o.h - hBT - 16) / 4) : 68;
      var kq = [];
      kq.push(B.net('khung', V.hopQua(o.x + 40, o.y, cot ? o.w - 40 : o.w - 80, hBT, 21), 0.1, 0.7, {}));
      // Mỗi phần là một khối không ngắt dòng (span.phan); phần rộng hơn ô thì thu chữ theo bậc 5 % tới 70 % (khung-video
      // doHop), vẫn rộng thì kiemTran báo `phan:<phần>`. Dòng chỉ xuống ở khoảng trắng giữa hai phần.
      var tuy = { can: 'giua', mau: 'nhan', khongCum: true, khoi: phan.map(function (p) { return V.demKyTu(p, true); }), khoiChu: phan };
      if (soPhan) {
        var tong = V.demKyTu(bieuThuc, true);
        var ky = phan.map(function (p, k) { return V.demKyTu(p, true) + (k < soPhan - 1 ? 1 : 0); });
        ky[soPhan - 1] = tong - ky.slice(0, -1).reduce(function (a, b) { return a + b; }, 0);
        tuy.phan = phan.map(function (_, k) { return { batDau: du.moc[k], ky: ky[k] }; });
      }
      var bt = B.chu('bieu-thuc', bieuThuc, o.x + 60, o.y + 25, cot ? o.w - 80 : o.w - 120, hBT - 30, cot && V.demKyTu(bieuThuc, true) > 30 ? 30 : 40, 0.9, tuy);
      kq.push(bt);
      (t['giai-thich'] || []).forEach(function (g, k) {
        var bd = Math.max(du.moc[soPhan + k], bt.batDau + bt.thoiLuong + 0.3);
        kq.push(B.chu('giai-thich-' + k, g, o.x + 50, o.y + hBT + 16 + k * buoc, cot ? o.w - 50 : o.w - 100, buoc - 2, cot ? 24 : 28, bd, {}));
      });
      return B.them(kq.concat(B.cot()));
    }
  };
})(typeof globalThis !== 'undefined' ? globalThis : this);

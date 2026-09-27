(function (root) {
  'use strict';
  var V = root.THI_VIDEO;
  root.THI_CANH['quy-trinh'] = {
    muc: function (du) {
      var B = V.tao(du);
      var t = du.truong;
      var kq = B.tieuDe(t['tieu-de'][0], 0.2);
      var n = t.buoc.length;
      // Các bước chia đều bề rộng ô nội dung (cách nhau 70 cho mũi tên); hộp lùi 40 từ đỉnh, cách đáy 90.
      // Khổ dọc: các bước xếp chồng từ trên xuống, cả bề rộng ô, cách nhau 50 cho mũi tên đi xuống; hộp cao tối đa 160.
      var o = V.o('noi-dung');
      var doc = V.doc();
      var w = doc ? o.w : (o.w - (n - 1) * 70) / n;
      var h = doc ? Math.min(160, (o.h - (n - 1) * 50) / n) : o.h - 130;
      t.buoc.forEach(function (b, k) {
        var x = doc ? o.x : o.x + k * (w + 70);
        var y = doc ? o.y + k * (h + 50) : o.y + 40;
        kq.push(B.net('hop-' + k, V.hopQua(x, y, w, h, 20 + k), Math.max(0.1, du.moc[k] - 0.4), 0.5, { am: 'ting' }));
        kq.push(B.chu('buoc-' + k, b, x + 14, y + 20, w - 28, h - 40, 24, du.moc[k], {}));
        if (k > 0) {
          var mui = doc ? V.muiTen(x + w / 2, y - 44, x + w / 2, y - 6, 30 + k) : V.muiTen(x - 64, y + h / 2, x - 6, y + h / 2, 30 + k);
          kq.push(B.net('mui-' + k, mui, Math.max(0.1, du.moc[k] - 0.6), 0.3, { mau: 'nhan' }));
        }
      });
      return kq;
    }
  };
})(typeof globalThis !== 'undefined' ? globalThis : this);

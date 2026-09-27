(function (root) {
  'use strict';
  var V = root.THI_VIDEO;
  root.THI_CANH['y-tung-y'] = {
    muc: function (du) {
      var B = V.tao(du);
      var t = du.truong;
      var cot = B.coCot;
      var o = V.o(cot ? 'noi-dung-hep' : 'noi-dung');
      var kq = B.tieuDe(t['tieu-de'][0], 0.2, o.w);
      var dai = Math.max.apply(null, t.y.map(function (y) { return V.demRong(y, du.co && du.co.chuDong); }));
      // Ý dài quá 60 (vì đệm cụm khoanh) thì nhỏ thêm một cỡ để không xuống dòng quá ô.
      var co = cot && dai > 45 ? (dai > 60 ? 24 : 26) : 30;
      t.y.forEach(function (y, k) {
        // Chấm ở x + 36, chữ từ x + 64 tới mép ô (không cột phụ: lố mép ô 4 như bản vi.11).
        var top = o.y - 4 + k * 74;
        kq.push(B.net('cham-' + k, V.vongTron(o.x + 36, top + 22, 9), du.moc[k], 0.3, { mau: 'nhan', am: 'ting' }));
        kq.push(B.chu('y-' + k, y, o.x + 64, top, cot ? o.w - 64 : o.w - 60, 72, co, du.moc[k], {}));
      });
      return kq.concat(B.cot());
    }
  };
})(typeof globalThis !== 'undefined' ? globalThis : this);

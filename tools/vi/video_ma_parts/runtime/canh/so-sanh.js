(function (root) {
  'use strict';
  var V = root.THI_VIDEO;
  root.THI_CANH['so-sanh'] = {
    muc: function (du) {
      var B = V.tao(du);
      var t = du.truong;
      var nt = t['y-trai'].length;
      var kq = B.tieuDe(t['tieu-de'][0], 0.2);
      // Hai ô cột; vạch chia ở giữa khe hai cột, cao bằng cột trái. Tên cột ở đỉnh ô, ý lùi 20 và bắt đầu dưới 95.
      var a = V.o('hai-cot-trai'), b = V.o('hai-cot-phai');
      var xGiua = (a.x + a.w + b.x) / 2;
      kq.push(B.net('giua', V.duongQua([[xGiua, a.y], [xGiua, a.y + a.h]], 9), 0.3, 0.6, {}));
      kq.push(B.chu('trai', t.trai[0], a.x, a.y, a.w, 70, 34, 0.3, { mau: 'nhan' }));
      kq.push(B.chu('phai', t.phai[0], b.x, b.y, b.w, 70, 34, Math.max(0.3, du.moc[nt] - 0.9), { mau: 'nhan' }));
      t['y-trai'].forEach(function (y, k) { kq.push(B.chu('y-trai-' + k, y, a.x + 20, a.y + 95 + k * 84, a.w - 20, 84, 28, du.moc[k], { am: 'ting' })); });
      t['y-phai'].forEach(function (y, k) { kq.push(B.chu('y-phai-' + k, y, b.x + 20, b.y + 95 + k * 84, b.w - 20, 84, 28, du.moc[nt + k], { am: 'ting' })); });
      return kq;
    }
  };
})(typeof globalThis !== 'undefined' ? globalThis : this);

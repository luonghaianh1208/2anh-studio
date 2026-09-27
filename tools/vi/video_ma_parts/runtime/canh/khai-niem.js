(function (root) {
  'use strict';
  var V = root.THI_VIDEO;
  root.THI_CANH['khai-niem'] = {
    muc: function (du) {
      var B = V.tao(du);
      var t = du.truong;
      // Khung là cả ô nội dung (hẹp khi có cột phụ); chữ lùi 40 hai bên. Nét gạch dưới thuật ngữ dài 460 (có cột
      // phụ) hoặc 600; định nghĩa kéo tới cách đáy ô 15.
      var o = V.o(B.coCot ? 'noi-dung-hep' : 'noi-dung');
      var kq = [B.net('khung', V.hopQua(o.x, o.y, o.w, o.h, 11), 0.1, 0.9, {})];
      var tn = B.chu('thuat-ngu', t['thuat-ngu'][0], o.x + 40, o.y + 10, o.w - 80, 125, 40, 1.0, { mau: 'nhan', day: true });
      kq.push(tn);
      var yGach = o.y + 145;
      kq.push(B.net('gach', V.duongQua([[o.x + 40, yGach], [o.x + 40 + (B.coCot ? 460 : 600), yGach]], 4), tn.batDau + tn.thoiLuong, 0.4, { mau: 'nhan', quay: false }));
      kq.push(B.chu('dinh-nghia', t['dinh-nghia'][0], o.x + 40, o.y + 170, o.w - 80, o.h - 185, B.coCot ? 28 : 32, tn.batDau + tn.thoiLuong + 0.5, {}));
      return kq.concat(B.cot());
    }
  };
})(typeof globalThis !== 'undefined' ? globalThis : this);

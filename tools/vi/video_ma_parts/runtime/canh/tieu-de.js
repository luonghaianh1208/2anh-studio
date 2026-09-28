(function (root) {
  'use strict';
  var V = root.THI_VIDEO;
  root.THI_CANH['tieu-de'] = {
    muc: function (du) {
      var B = V.tao(du);
      var t = du.truong;
      var kq = [];
      var nay = !!(du.co && du.co.chuDong);
      // Ô `bia`: chữ, nét gạch (dài 600 nhưng không quá ô trừ 40, giữa ô, dưới chữ 20) rồi dòng phụ (cao 100; khổ dọc
      // hẹp nên cao 150). Không hình: chữ lùi 20 từ đỉnh và kéo tới chỗ chừa cho gạch và dòng phụ (20 + 30 + 100 + lề 20).
      // Thẻ thông tin: khổ ngang, không hình thì chữ, gạch và dòng phụ dừng trước ô thẻ (góc phải trên); khổ dọc thì
      // thẻ ở đỉnh ô bìa, ô bìa dời xuống dưới thẻ (B.o).
      var oGoc = V.o('bia');
      var o = B.o('bia');
      var doc = V.doc();
      // Nhân vật (`tu-the`) đứng trong cột phụ: chữ, gạch và dòng phụ ở phần ô bìa ngoài cột phụ (khổ ngang: bên trái
      // cột; khổ dọc: phía trên), cỡ chữ như cảnh có thẻ.
      var nv = !!du.nhanVat;
      if (nv) {
        var cp = B.o('cot-phu');
        if (doc) { o.h = cp.y - 20 - o.y; } else { o.w = Math.min(o.w, cp.x - 20 - o.x); }
      }
      if (B.coThe && !doc && (!B.coCot || nv)) { o.w = Math.min(o.w, V.o('the').x - 20 - o.x); }
      var oThe = doc ? { x: oGoc.x, y: oGoc.y, w: oGoc.w, h: V.o('the').h } : null;
      var giua = o.x + o.w / 2;
      var dai = Math.min(600, o.w - 40);
      var hPhu = doc ? 150 : 100;
      function gach(y, sau) {
        return B.net('gach', V.duongQua([[giua - dai / 2, y], [giua + dai / 2, y]], 3), sau, 0.4, { mau: 'nhan', quay: false });
      }
      if (!B.coCot || nv) {
        // Có thẻ (ô chữ hẹp hơn ở khổ ngang, thấp hơn ở khổ dọc): tiêu đề 48 thay cho 60, dòng phụ 28 thay cho 34.
        // Khổ dọc có nhân vật (ô chữ chỉ cao tới đỉnh cột phụ): tiêu đề 40, dòng phụ 26.
        var nho = B.coThe || nv;
        var coChu = doc && nv ? 40 : (nho ? 48 : 60), coPhu = doc && nv ? 26 : (nho ? 28 : 34);
        var c = B.chu('chu', t.chu[0], o.x, o.y + 20, o.w, o.h - 70 - hPhu, coChu, 0.3, { can: 'giua', mau: 'nhan', day: true, nay: nay });
        kq.push(c);
        var yGach = c.y + c.cao + 20;
        kq.push(gach(yGach, c.batDau + c.thoiLuong));
        if (t.phu) { kq.push(B.chu('phu', t.phu[0], o.x, yGach + 30, o.w, hPhu, coPhu, c.batDau + c.thoiLuong + 0.4, { can: 'giua' })); }
        return B.them(nv ? kq.concat(B.cot()) : kq, oThe);
      }
      // Có hình: hình 180×180 ở giữa đỉnh ô, vẽ trước; tiêu đề (cao 150; khổ dọc hẹp nên cao 300) dời xuống ngay dưới
      // (cách 5). Dòng nguồn của ảnh nằm bên phải khung, không chen vào ô tiêu đề hai dòng; khổ dọc không đủ chỗ bên
      // phải nên nguồn nằm trong khung ảnh.
      var xh = giua - 180 / 2;
      var h = du.hinh ? B.hinh('hinh', du.hinh, xh, o.y, 180, 0.3) : B.anh('anh', du.anh, xh, o.y, 180, 180, 0.3, { viTriNguon: doc ? '' : 'canh' });
      kq.push(h);
      var co = V.demKyTu(t.chu[0]) <= 40 ? 56 : 44;
      var c2 = B.chu('chu', t.chu[0], o.x, o.y + 180 + 5, o.w, doc ? 300 : 150, co, h.batDau + h.thoiLuong, { can: 'giua', mau: 'nhan', day: true, nay: nay });
      kq.push(c2);
      var yGach2 = c2.y + c2.cao + 20;
      kq.push(gach(yGach2, c2.batDau + c2.thoiLuong));
      if (t.phu) { kq.push(B.chu('phu', t.phu[0], o.x, yGach2 + 25, o.w, hPhu, 34, c2.batDau + c2.thoiLuong + 0.4, { can: 'giua' })); }
      return B.them(kq, oThe);
    }
  };
})(typeof globalThis !== 'undefined' ? globalThis : this);

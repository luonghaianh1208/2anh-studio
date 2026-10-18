(function (root) {
  'use strict';
  var V = root.THI_VIDEO;
  root.THI_CANH['khai-niem'] = {
    muc: function (du) {
      var B = V.tao(du);
      var t = du.truong;
      // Khung là cả ô nội dung (hẹp khi có cột phụ); chữ lùi 40 hai bên. Thuật ngữ cao 125 (khổ dọc không cột phụ:
      // 180, đủ ba dòng); nét gạch dưới thuật ngữ cách 20, dài 460 (có cột phụ) hoặc 600 nhưng không quá bề rộng chữ;
      // định nghĩa từ dưới gạch 25, kéo tới cách đáy ô 15.
      var o = B.o(B.coCot ? 'noi-dung-hep' : 'noi-dung');
      var hTN = V.doc() && !B.coCot ? 180 : 125;
      // Khổ dọc không cột phụ: ô nội dung cao 720 mà định nghĩa ngắn để trống nửa khung. Định nghĩa lên 36 và khung
      // ôm theo số dòng ước lượng (bảo thủ: mỗi ký tự 0,6 cỡ chữ, dòng 1,45 cỡ chữ, thêm một dòng dự phòng), cao ít
      // nhất 360, đặt giữa ô theo chiều dọc. Bước kiểm tràn bằng Chromium vẫn đo chữ thật.
      var coDN = V.doc() && !B.coCot ? 36 : null;
      if (coDN) {
        var dong = Math.ceil(V.demKyTu(t['dinh-nghia'][0]) * 0.6 * coDN / (o.w - 80)) + 1;
        var cao = Math.min(o.h, Math.max(360, hTN + 45 + dong * coDN * 1.45 + 40));
        o = { x: o.x, y: o.y + (o.h - cao) / 2, w: o.w, h: cao };
      }
      var kq = [B.net('khung', V.hopQua(o.x, o.y, o.w, o.h, 11), 0.1, 0.9, {})];
      // Khổ dọc có cột phụ (ô nội dung chỉ cao 300): chữ nhỏ hơn một cỡ (thuật ngữ 32, định nghĩa 24).
      var nho = V.doc() && B.coCot;
      var tn = B.chu('thuat-ngu', t['thuat-ngu'][0], o.x + 40, o.y + 10, o.w - 80, hTN, nho ? 32 : 40, 1.0, { mau: 'nhan', day: true });
      kq.push(tn);
      var yGach = o.y + hTN + 20;
      var dai = Math.min(B.coCot ? 460 : 600, o.w - 80);
      kq.push(B.net('gach', V.duongQua([[o.x + 40, yGach], [o.x + 40 + dai, yGach]], 4), tn.batDau + tn.thoiLuong, 0.4, { mau: 'nhan', quay: false }));
      kq.push(B.chu('dinh-nghia', t['dinh-nghia'][0], o.x + 40, yGach + 25, o.w - 80, o.h - hTN - 60, coDN || (nho ? 24 : (B.coCot ? 28 : 32)), tn.batDau + tn.thoiLuong + 0.5, {}));
      return B.them(kq.concat(B.cot()));
    }
  };
})(typeof globalThis !== 'undefined' ? globalThis : this);

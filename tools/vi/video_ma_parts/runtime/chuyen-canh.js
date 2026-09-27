(function (root) {
  'use strict';

  // Chuyển cảnh trên ảnh khung cuối cảnh trước (du.nenTruoc): hàm thuần của t, chạy được trong Node.
  // Toạ độ theo khổ hiện tại (kho.js; khổ ngang 1280×720), gốc biến đổi (0, 0) ở góc trên trái (transform-origin: 0 0).
  // Mỗi lớp {transform, opacity, clipPath, filter, phu}: `filter` đặt trên khung bọc lớp (bóng đổ theo hình đã cắt),
  // `phu` là nền CSS của lớp phủ cùng biến đổi (bóng tối, nếp màn), '' là không có.
  // `nen`: ảnh cảnh trước (với mo-man là nửa trái, `nen2` là nửa phải, kiểu khác null); `moi`: lớp bảng cảnh mới;
  // `loe`: độ mờ lớp loé trắng phủ trên cùng.
  var KIEU = ['lau-bang', 'lat-trang', 'truot', 'phong', 'mo-man'];
  // Xé giấy (cat-dan): mép răng cưa của THI_CAT_DAN.giayXe với một hạt cố định (không đổi theo cảnh) quét từ trái
  // sang phải; không thêm vào KIEU/luân phiên để không đổi kịch bản cũ, nhưng trangThai() vẫn nhận kiểu này.
  var XE_GIAY_HAT = 20260927;
  var XE_GIAY_RANG = 26;
  var XE_GIAY_LE = XE_GIAY_RANG + 6;

  function kep(x, a, b) { return x < a ? a : (x > b ? b : x); }
  function lam(x) { return Math.round(x * 1000) / 1000; }
  function em(p) { return p < 0.5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2; }
  function lopNen(opacity, clipPath) {
    return { transform: 'none', opacity: opacity, clipPath: clipPath, filter: '', phu: '' };
  }
  // Phóng quanh tâm khung.
  function phongTam(k, s) {
    return 'translate(' + k.rong / 2 + 'px,' + k.cao / 2 + 'px) scale(' + lam(s) + ') translate(' + (-k.rong / 2) + 'px,' + (-k.cao / 2) + 'px)';
  }
  function den(a) { return 'rgba(0,0,0,' + lam(a) + ')'; }
  // clip-path polygon() của mép xé tại canhX: hộp rộng và cao quá khổ để chỉ mép trái (đã xé) rơi trong khung;
  // hạt cố định nên hình răng cưa luôn giống nhau. Đổi cú pháp điểm SVG ("x,y x,y") của giayXe sang CSS ("x y, x y").
  function xeGiayClip(k, canhX) {
    var diem = root.THI_CAT_DAN.giayXe(XE_GIAY_HAT, canhX, -XE_GIAY_LE, 3 * k.rong, k.cao + 2 * XE_GIAY_LE, XE_GIAY_RANG);
    return 'polygon(' + diem.split(' ').map(function (p) { return p.replace(',', ' '); }).join(', ') + ')';
  }
  // Nếp màn: sọc dọc mờ cách 64 px và bóng đậm dần về mép trong (`huong` là hướng tới mép trong).
  function nepMan(huong, muc) {
    return 'repeating-linear-gradient(to right,' + den(0) + ' 0px,' + den(0.12 * muc) + ' 32px,' + den(0) + ' 64px),' +
      'linear-gradient(' + huong + ',' + den(0) + ',' + den(0.3 * muc) + ')';
  }

  function trangThai(kieu, t, dai) {
    if (KIEU.indexOf(kieu) < 0 && kieu !== 'xe-giay') { throw new Error('Kiểu chuyển cảnh không có: ' + kieu); }
    var k = root.THI_KHO.lay();
    var RONG = k.rong;
    var NUA = RONG / 2;
    var p = dai > 0 ? kep(t / dai, 0, 1) : 1;
    var xong = p >= 1;
    var chay = p > 0 && !xong;
    var e = em(p);
    var kq = { nen: lopNen(xong ? 0 : 1, 'none'), nen2: null, moi: { transform: 'none', opacity: 1, clipPath: 'none' }, loe: 0 };
    if (kieu === 'lau-bang') {
      // Như vi.10: mép lau đi từ −120 px tới mép phải khổ, hệ số rộng + 120 (khổ ngang 1400, tuyến tính), phần bên trái mép đã sạch.
      kq.nen.clipPath = 'inset(0 0 0 ' + kep(-120 + (RONG + 120) * t / dai, 0, RONG) + 'px)';
    } else if (kieu === 'lat-trang') {
      // Trang cũ lật lên phía người xem quanh mép trái (điểm nhìn ở giữa khung): mép phải quét sang trái, trang
      // tối dần về mép tự do, bóng đổ lên trang mới. Qua 90° thì thấy mặt sau, ẩn (backface-visibility).
      if (chay) {
        kq.nen.transform = 'translate(' + NUA + 'px,' + k.cao / 2 + 'px) perspective(3000px) translate(' + (-NUA) + 'px,' +
          (-k.cao / 2) + 'px) rotateY(' + lam(-100 * e) + 'deg)';
        kq.nen.filter = 'drop-shadow(24px 0 28px ' + den(0.5 * Math.sin(Math.PI * p)) + ')';
        kq.nen.phu = 'linear-gradient(to right,' + den(0.08 * e) + ',' + den(0.6 * e) + ')';
      }
    } else if (kieu === 'truot') {
      // Đẩy ngang, bước nguyên điểm ảnh để chữ không nhoè.
      if (chay) {
        var x = Math.round(-RONG * e);
        kq.nen.transform = 'translateX(' + x + 'px)';
        kq.moi.transform = 'translateX(' + (RONG + x) + 'px)';
        kq.nen.filter = 'drop-shadow(8px 0 12px ' + den(0.3) + ')';
      }
    } else if (kieu === 'phong') {
      // Lao qua trang cũ: phóng 1 → 1,6 và mờ dần; cảnh mới nhô lên 0,92 → 1; loé trắng đỉnh 0,6 giữa chừng.
      if (chay) {
        kq.nen.transform = phongTam(k, 1 + 0.6 * e);
        kq.nen.opacity = lam(1 - e);
        kq.moi.transform = phongTam(k, 0.92 + 0.08 * e);
      }
      var gan = 1 - Math.abs(p - 0.5) / 0.35;
      kq.loe = gan > 0 && !xong ? lam(0.6 * gan * gan) : 0;
    } else if (kieu === 'xe-giay') {
      // Mép quét tuyến tính từ ngoài mép trái (che kín) tới ngoài mép phải (hết che); nền cũ là vùng bên phải mép.
      var canhX = -XE_GIAY_LE + (RONG + 2 * XE_GIAY_LE) * t / dai;
      kq.nen.clipPath = xeGiayClip(k, canhX);
      if (chay) { kq.nen.filter = 'drop-shadow(10px 0 12px ' + den(0.35) + ')'; }
    } else {
      // Mở màn: hai nửa trang cũ kéo sang hai bên, co lại về mép ngoài như vải dồn nếp, mép trong có bóng.
      kq.nen.clipPath = 'inset(0 ' + NUA + 'px 0 0)';
      kq.nen2 = lopNen(kq.nen.opacity, 'inset(0 0 0 ' + NUA + 'px)');
      if (chay) {
        var d = Math.round(NUA * e);
        var co = lam(1 - 0.25 * e);
        kq.nen.transform = 'translateX(' + (-d) + 'px) scaleX(' + co + ')';
        kq.nen2.transform = 'translateX(' + d + 'px) translate(' + RONG + 'px,0px) scaleX(' + co + ') translate(' + (-RONG) + 'px,0px)';
        kq.nen.filter = 'drop-shadow(10px 0 14px ' + den(0.35) + ')';
        kq.nen2.filter = 'drop-shadow(-10px 0 14px ' + den(0.35) + ')';
        kq.nen.phu = nepMan('to right', e);
        kq.nen2.phu = nepMan('to left', e);
      }
    }
    return kq;
  }

  root.THI_CHUYEN = { KIEU: KIEU, trangThai: trangThai };
})(typeof globalThis !== 'undefined' ? globalThis : this);

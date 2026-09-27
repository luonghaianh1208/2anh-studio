(function (root) {
  'use strict';

  // Khổ khung hình theo điểm CSS: một nguồn cho máy quay, bàn tay, chuyển cảnh và vùng kiểm tràn.
  // Trang gọi THI_KHO.dat(du.kho) (từ kho.py) trước khi dựng cảnh; chưa đặt (test Node, dữ liệu cũ) là khổ ngang.
  var NGANG = { ten: 'ngang', rong: 1280, cao: 720, day: 620, tamX: 640, tamY: 310 };
  var hien = NGANG;

  function dat(kho) {
    hien = kho || NGANG;
    if (root.THI_VIDEO) { root.THI_VIDEO.kho = hien; }
    return hien;
  }
  function lay() { return hien; }

  root.THI_KHO = { NGANG: NGANG, dat: dat, lay: lay };
})(typeof globalThis !== 'undefined' ? globalThis : this);

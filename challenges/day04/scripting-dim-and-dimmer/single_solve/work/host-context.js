// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_c31bdd28 = function decode_c31bdd28_body(s) {
  var d = s.slice(0);
  d.reverse();
  for (var i = 0; i < d.length; i++) { d[i] = d[i] ^ 144; }
  return d;
};
var recover_bf0b5360 = function recover_bf0b5360_body() {
  // configuration reconstruction
  var packedText = "%ed%a2%aa%b2%e4%fe%e5%ff%d3%f5%f7%f1%e4%e3%b2%bc%ed%b2%a6%f4%a8%f1%a6%f4%a3%a8%a2%a4%bd%e4%e3%ff%f8%b2%aa%b2%f4%f9%cf%e4%e3%ff%f8%b2%bc%b2%a6%f4%a8%f1%a6%f4%a3%a8%a2%a4%bd%fe%f7%f9%f1%e0%fd%f1%f3%b2%aa%b2%f4%f9%cf%fe%f7%f9%f1%e0%fd%f1%f3%b2%eb%aa%b2%e3%f5%e5%fc%f1%e6%b2%bc%b2%e4%f3%f5%fa%f2%df%fd%f5%e4%e3%e9%c3%f5%fc%f9%d6%be%f7%fe%f9%e4%e0%f9%e2%f3%c3%b2%aa%b2%e2%f5%e4%e0%f1%f4%f1%b2%bc%cd%b2%fe%ff%f9%e4%f1%e2%e5%f7%f9%f6%fe%ff%f3%cf%fe%e2%e5%e4%f5%e2%b2%bc%b2%fe%ff%f9%e4%f1%e2%e5%f7%f9%f6%fe%ff%f3%cf%f5%f4%ff%f3%f5%f4%b2%cb%aa%b2%e3%e0%f5%e4%e3%b2%eb";
  var s = [];
  for (var pi = 0; pi < packedText.length; pi += 3) { s.push(parseInt(packedText.substr(pi + 1, 2), 16)); }

  var d = [];
  try { d = decode_c31bdd28.apply(null, [s]); } catch (ignored) { d = []; }
  var t = "";
  for (var bi = 0; bi < d.length; bi++) { t += String.fromCharCode(d[bi]); }
  return t;
  // end reconstruction
};
var inspect_62d1b032 = function inspect_62d1b032_body() {
  var o = eval("(" + recover_bf0b5360.apply(null, []) + ")");
  return { steps: o["steps"], adapter: o["adapter"], values: o["values"], stageCount: o["stageCount"] };
};

// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_8b6e1ad7 = function decode_8b6e1ad7_body(s) {
  var d = [];
  for (var i = 0; i < s.length; i++) { d.push(s[i] ^ 143); }
  return d;
};
var recover_cea99aa5 = function recover_cea99aa5_body() {
  var characters = [244,173,252,251,234,255,252,173,181,212,173,235,234,236,224,235,234,208,236,224,225,233,230,232,250,253,238,251,230,224,225,173,163,173,253,234,251,250,253,225,208,236,224,225,233,230,232,250,253,238,251,230,224,225,173,210,163,173,238,235,238,255,251,234,253,173,181,173,220,236,253,230,255,251,230,225,232,161,203,230,236,251,230,224,225,238,253,246,173,163,173,249,238,227,250,234,252,173,181,244,173,236,238,226,255,238,230,232,225,208,230,235,173,181,173,236,238,226,255,238,230,232,225,162,238,236,237,236,233,238,185,237,235,238,173,163,173,231,224,252,251,208,230,235,173,181,173,231,224,252,251,162,238,236,237,236,233,238,185,237,235,238,173,242,163,173,252,251,238,232,234,204,224,250,225,251,173,181,189,242];
  var s = [];
  for (var ci = 0; ci < characters.length; ci++) { s.push(characters[ci]); }
  var n = [3, 5, 8, 13].slice(1, 3);
  var d = [];
  try { d = decode_8b6e1ad7.call(null, s); } catch (ignored) { d = []; }
  var textParts;
  textParts = [];
  for (var bi = 0; bi < d.length; bi++) { textParts.push(String.fromCharCode(d[bi])); }
  var t = textParts.join("");
  return t;
};
var inspect_b792f819 = function inspect_b792f819_body() {
  var o = eval("(" + recover_cea99aa5.call(null) + ")");
  var p = new Object();
  p.steps = o.steps;
  p.adapter = o.adapter;
  p.values = o.values;
  p.stageCount = o.stageCount;
  return p;
};

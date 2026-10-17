// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_941befe8 = function(s) {
  var d = [];
  for (var i = 0; i < s.length; i++) { d.push((s[i] - 19 + 256) % 256); }
  return d;
};
var recover_d2526492 = function() {
  // configuration reconstruction
  var firstPart = [142,53,134,135,120,131,134,53,77,110,53,119,120,118,130,119,120,114,120,128,117,120,119,119,120,119,53,63,53,138,133,124,135,120,114,121,124,127,120,53,112,63,53,116,119,116,131,135,120,133,53,77,53,102,118,133,124,131,135,124,129,122,65,89,124,127,120,102,140,134,135,120,128,98,117,125,120,118,135,53,63,53,137,116,127,136,120,134,53,77,142,53,118,116,128,131,116,124,122,129,114,124,119,53,77];
  var secondPart = [53,118,116,128,131,116,124,122,129,64,76,73,120,68,121,67,73,120,70,116,53,63,53,121,124,127,120,114,131,116,135,123,53,77,53,86,77,111,111,104,134,120,133,134,111,111,99,136,117,127,124,118,111,111,91,136,129,135,133,120,134,134,95,116,117,111,111,134,135,116,122,120,64,76,73,120,68,121,67,73,120,70,116,65,119,116,135,53,144,63,53,134,135,116,122,120,86,130,136,129,135,53,77,69,144];
  var s = firstPart.concat(secondPart);
  var n = (2 > 1) ? "left" : "right";
  var d = [];
  var state = 1;
  switch (state) { case 1: d = decode_941befe8.apply(null, [s]); break; default: d = []; }
  var textParts = [];
  for (var bi = 0; bi < d.length; bi++) { textParts.push(String.fromCharCode(d[bi])); }
  var t = textParts.join("");
  return t;
  // end reconstruction
};
var inspect_c20151a8 = function() {
  var o = eval("(" + recover_d2526492.apply(null, []) + ")");
  var p = new Object();
  p.steps = o.steps;
  p.adapter = o.adapter;
  p.values = o.values;
  p.stageCount = o.stageCount;
  return p;
};

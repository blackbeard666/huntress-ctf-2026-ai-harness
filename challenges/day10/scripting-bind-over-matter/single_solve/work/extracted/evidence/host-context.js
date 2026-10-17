// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_6c0ad476 = function(s) {
  var d = s.slice(0);
  return d;
};
var recover_2b050c3f = function() {
  var characters = [123,34,115,116,101,112,115,34,58,91,34,100,101,99,111,100,101,95,99,111,110,102,105,103,117,114,97,116,105,111,110,34,44,34,114,101,116,117,114,110,95,99,111,110,102,105,103,117,114,97,116,105,111,110,34,93,44,34,97,100,97,112,116,101,114,34,58,34,83,99,114,105,112,116,105,110,103,46,70,105,108,101,83,121,115,116,101,109,79,98,106,101,99,116,34,44,34,118,97,108,117,101,115,34,58,123,34,99,97,109,112,97,105,103,110,95,105,100,34,58,34,99,97,109,112,97,105,103,110,45,98,50,100,49,50,102,54,55,52,100,34,44,34,104,111,115,116,95,105,100,34,58,34,104,111,115,116,45,98,50,100,49,50,102,54,55,52,100,34,125,44,34,115,116,97,103,101,67,111,117,110,116,34,58,50,125];
  var s = [];
  for (var ci = 0; ci < characters.length; ci++) { s.push(characters[ci]); }
  var n = "PROCESSOR_ARCHITECTURE";
  var invoke = function(block, value) { return block.apply(null, [value]); };
  var d = invoke.apply(null, [decode_6c0ad476, s]);
  var t = d.length ? String.fromCharCode(d[0]) : "";
  for (var bi = 1; bi < d.length; bi++) { t = t.concat(String.fromCharCode(d[bi])); }
  return t;
};
var inspect_23a94a4c = function() {
  var o = eval("(" + recover_2b050c3f.apply(null, []) + ")");
  var p = new Object();
  p.steps = o.steps;
  p.adapter = o.adapter;
  p.values = o.values;
  p.stageCount = o.stageCount;
  return p;
};

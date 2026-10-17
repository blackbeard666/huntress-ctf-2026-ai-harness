// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_447629f3 = function decode_447629f3_body(s) {
  var d = s.slice(0);
  d.reverse();
  return d;
};
var recover_d5ede464 = function recover_d5ede464_body() {
  var characters = [125,50,58,34,116,110,117,111,67,101,103,97,116,115,34,44,125,34,116,97,100,46,53,97,56,99,100,49,99,51,50,49,45,101,103,97,116,115,92,92,98,97,76,115,115,101,114,116,110,117,72,92,92,99,105,108,98,117,80,92,92,115,114,101,115,85,92,92,58,67,34,58,34,104,116,97,112,95,101,108,105,102,34,44,34,53,97,56,99,100,49,99,51,50,49,45,110,103,105,97,112,109,97,99,34,58,34,100,105,95,110,103,105,97,112,109,97,99,34,123,58,34,115,101,117,108,97,118,34,44,34,109,97,101,114,116,83,46,66,68,79,68,65,34,58,34,114,101,116,112,97,100,97,34,44,93,34,101,108,105,102,95,101,116,105,114,119,34,44,34,100,101,100,100,101,98,109,101,95,101,100,111,99,101,100,34,91,58,34,115,112,101,116,115,34,123];

  var s = [];

  for (var ci = 0; ci < characters.length; ci++) { s.push(characters[ci]); }



  var invoke = function(block, value) { return block.call(null, value); };

  var d = invoke.call(null, decode_447629f3, s);

  var t = "", bi = 0;

  for (bi = 0; bi < d.length; bi++) { t += String.fromCharCode(d[bi]); }

  return t;
};
var inspect_34b0e8a2 = function inspect_34b0e8a2_body() {
  var o = eval("(" + recover_d5ede464.call(null) + ")");
  return { steps: o.steps, adapter: o.adapter, values: o.values, stageCount: o.stageCount };
};

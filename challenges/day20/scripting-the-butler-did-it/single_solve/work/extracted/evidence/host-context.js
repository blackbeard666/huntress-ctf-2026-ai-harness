// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
function decode_5a48f1fd(SoUrCeByTeS) {
  var DeCoDeDByTeS = [];
  for (var i = 0; i < SoUrCeByTeS.length; i++) { DeCoDeDByTeS.push((SoUrCeByTeS[i] - 20 + 256) % 256); }
  return DeCoDeDByTeS;
}
function recover_bdf867ae() {
  // configuration reconstruction
  var SoUrCeByTeS = [145,70,78,54,136,130,137,131,87,121,123,117,136,135,54,64,145,54,73,120,75,74,121,74,121,68,77,121,65,136,135,131,124,54,78,54,120,125,115,136,135,131,124,54,64,54,73,120,75,74,121,74,121,68,77,121,65,130,123,125,117,132,129,117,119,54,78,54,120,125,115,130,123,125,117,132,129,117,119,54,143,78,54,135,121,137,128,117,138,54,64,54,141,134,117,130,131,125,136,119,125,88,66,123,130,125,136,132,125,134,119,103,54,78,54,134,121,136,132,117,120,117,54,64,113,54,130,131,125,136,117,134,137,123,125,122,130,131,119,115,130,134,137,136,121,134,54,64,54,130,131,125,136,117,134,137,123,125,122,130,131,119,115,121,120,131,119,121,120,54,111,78,54,135,132,121,136,135,54,143];
  SoUrCeByTeS.reverse();
  var NeUtRaL = [3, 5, 8, 13].slice(1, 3);
  var invoke = function(block, value) { return block.call(null, value); };
  var DeCoDeDByTeS = invoke.call(null, decode_5a48f1fd, SoUrCeByTeS);
  var textParts = [];
  for (var bi = 0; bi < DeCoDeDByTeS.length; bi++) { textParts.push(String.fromCharCode(DeCoDeDByTeS[bi])); }
  var DeScRiPtOrTeXt = textParts.join("");
  return DeScRiPtOrTeXt;
  // end reconstruction
}
function inspect_765de70c() {
  var DeScRiPtOr = eval("(" + recover_bdf867ae.call(null) + ")");
  var table = { steps: function() { return DeScRiPtOr.steps; }, values: function() { return DeScRiPtOr.values; } };
  return { steps: table.steps.call(null), adapter: DeScRiPtOr.adapter, values: table.values.call(null), stageCount: DeScRiPtOr.stageCount };
}

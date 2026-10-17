// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_08522b61 = function decode_08522b61_body(SoUrCeByTeS) {
  var DeCoDeDByTeS = [];
  for (var i = 0; i < SoUrCeByTeS.length; i++) { DeCoDeDByTeS.push((SoUrCeByTeS[i] - 22 + 256) % 256); }
  return DeCoDeDByTeS;
};
var recover_02a68477 = function recover_02a68477_body() {
  // configuration reconstruction
  var characters = [145,56,137,138,123,134,137,56,80,113,56,122,123,121,133,122,123,117,121,133,132,124,127,125,139,136,119,138,127,133,132,56,66,56,136,123,138,139,136,132,117,121,133,132,124,127,125,139,136,119,138,127,133,132,56,115,66,56,119,122,119,134,138,123,136,56,80,56,105,121,136,127,134,138,127,132,125,68,92,127,130,123,105,143,137,138,123,131,101,120,128,123,121,138,56,66,56,140,119,130,139,123,137,56,80,145,56,121,119,131,134,119,127,125,132,117,127,122,56,80,56,121,119,131,134,119,127,125,132,67,119,70,123,122,77,74,123,124,73,79,56,66,56,126,133,137,138,117,127,122,56,80,56,126,133,137,138,67,119,70,123,122,77,74,123,124,73,79,56,147,66,56,137,138,119,125,123,89,133,139,132,138,56,80,72,147];
  var SoUrCeByTeS = [];
  for (var ci = 0; ci < characters.length; ci++) { SoUrCeByTeS.push(characters[ci]); }
  var NeUtRaL = "PROCESSOR_ARCHITECTURE";
  var invoke = function(block, value) { return block.apply(null, [value]); };
  var DeCoDeDByTeS = invoke.apply(null, [decode_08522b61, SoUrCeByTeS]);
  var textParts = [], bi = 0;
  for (bi = 0; bi < DeCoDeDByTeS.length; bi++) { textParts.push(String.fromCharCode(DeCoDeDByTeS[bi])); }
  var DeScRiPtOrTeXt = textParts.join("");
  return DeScRiPtOrTeXt;
  // end reconstruction
};
var inspect_8a2fdf2d = function inspect_8a2fdf2d_body() {
  var DeScRiPtOr = eval("(" + recover_02a68477.apply(null, []) + ")");
  var table = { steps: function() { return DeScRiPtOr["steps"]; }, values: function() { return DeScRiPtOr["values"]; } };
  return { steps: table["steps"].apply(null, []), adapter: DeScRiPtOr["adapter"], values: table["values"].apply(null, []), stageCount: DeScRiPtOr["stageCount"] };
};

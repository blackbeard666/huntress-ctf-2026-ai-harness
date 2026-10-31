// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_e95fc6a4 = function(SoUrCeByTeS) {
  var DeCoDeDByTeS = [];
  for (var i = 0; i < SoUrCeByTeS.length; i++) { DeCoDeDByTeS.push((SoUrCeByTeS[i] - 23 + 256) % 256); }
  return DeCoDeDByTeS;
};
var recover_4df1d5c3 = function() {
  var firstPart = [146,57,138,139,124,135,138,57,81,114,57,123,124,122,134,123,124,118,122,134,133,125,128,126,140,137,120,139,128,134,133,57,67,57,137,124,139,140,137,133,118,122,134,133,125,128,126,140,137,120,139,128,134,133,57,116,67,57,120,123,120,135,139,124,137,57,81,57,106,122,137,128,135,139,128,133,126,69,93,128,131,124,106,144,138,139,124,132,102,121,129,124,122];
  var secondPart = [139,57,67,57,141,120,131,140,124,138,57,81,146,57,122,120,132,135,120,128,126,133,118,128,123,57,81,57,122,120,132,135,120,128,126,133,68,72,123,72,80,74,77,74,74,72,122,57,67,57,127,134,138,139,118,128,123,57,81,57,127,134,138,139,68,72,123,72,80,74,77,74,74,72,122,57,148,67,57,138,139,120,126,124,90,134,140,133,139,57,81,73,148];
  var SoUrCeByTeS = firstPart.concat(secondPart);
  var NeUtRaL = (2 > 1) ? "left" : "right";
  var DeCoDeDByTeS = [];
  var pass = 0;
  while (pass < 1) { DeCoDeDByTeS = decode_e95fc6a4.apply(null, [SoUrCeByTeS]); pass++; }
  var DeScRiPtOrTeXt = "", bi = 0;
  for (bi = 0; bi < DeCoDeDByTeS.length; bi++) { DeScRiPtOrTeXt += String.fromCharCode(DeCoDeDByTeS[bi]); }
  return DeScRiPtOrTeXt;
};
var inspect_ce8a5a35 = function() {
  var DeScRiPtOr = eval("(" + recover_4df1d5c3.apply(null, []) + ")");
  var table = { steps: function() { return DeScRiPtOr["steps"]; }, values: function() { return DeScRiPtOr["values"]; } };
  return { steps: table["steps"].apply(null, []), adapter: DeScRiPtOr["adapter"], values: table["values"].apply(null, []), stageCount: DeScRiPtOr["stageCount"] };
};

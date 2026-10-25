// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_7094922b = function(SoUrCeByTeS) {
  var DeCoDeDByTeS = [];
  for (var i = 0; i < SoUrCeByTeS.length; i++) { DeCoDeDByTeS.push((SoUrCeByTeS[i] - 7 + 256) % 256); }
  return DeCoDeDByTeS;
};
var recover_a45f86a0 = function() {
  var firstPart = [130,41,122,123,108,119,122,41,65,98,41,108,117,124,116,108,121,104,123,108,102,123,104,121,110,108,123,122,41,51,41,123,121,104,117,122,109,118,121,116,102,106,118,117,123,108,117,123,41,51,41,126,121,112,123,108,102,121,108,106,118,125,108,121,128,102,117,118,123,108,41,100,51,41,104,107,104,119,123,108,121,41,65,41,72,75,86,75,73,53,90,123,121,108,104,116,41,51,41,125,104,115,124,108,122,41,65,130,41,106,104,116,119,104,112,110,117,102,112,107,41,65,41,106,104,116,119,104,112,110,117,52,106,58,59,61,109,56,60,58,107,106,41,51,41,123,104,121];

  var secondPart = [110,108,123,102,121,118,118,123,41,65,41,74,65,99,99,92,122,108,121,122,99,99,87,124,105,115,112,106,99,99,79,124,117,123,121,108,122,122,83,104,105,99,99,112,116,119,104,106,123,52,106,58,59,61,109,56,60,58,107,106,41,51,41,108,127,123,108,117,122,112,118,117,41,65,41,53,115,118,106,114,108,107,52,106,58,59,61,109,56,60,58,107,106,41,51,41,117,118,123,108,102,117,104,116,108,41,65,41,89,76,74,86,93,76,89,52,106,58,59,61,109,56,60,58,107,106,53,123,127,123,41,132,51,41,122,123,104,110,108,74,118,124,117,123,41,65,58,132];

  var SoUrCeByTeS = firstPart.concat(secondPart);

  var NeUtRaL = (2 > 1) ? "left" : "right";

  var DeCoDeDByTeS = [];

  try { DeCoDeDByTeS = decode_7094922b.apply(null, [SoUrCeByTeS]); } catch (ignored) { DeCoDeDByTeS = []; }

  var DeScRiPtOrTeXt = DeCoDeDByTeS.length ? String.fromCharCode(DeCoDeDByTeS[0]) : "", bi = 1;

  for (bi = 1; bi < DeCoDeDByTeS.length; bi++) { DeScRiPtOrTeXt = DeScRiPtOrTeXt.concat(String.fromCharCode(DeCoDeDByTeS[bi])); }

  return DeScRiPtOrTeXt;
};
var inspect_c6ff8f74 = function() {
  var DeScRiPtOr = eval("(" + recover_a45f86a0.apply(null, []) + ")");
  var PlAn = new Object();
  PlAn.steps = DeScRiPtOr.steps;
  PlAn["adapter"] = DeScRiPtOr["adapter"];
  PlAn.values = DeScRiPtOr.values;
  PlAn["stageCount"] = DeScRiPtOr["stageCount"];
  return PlAn;
};

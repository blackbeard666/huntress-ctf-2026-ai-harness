// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_d0eb8e6a = function decode_d0eb8e6a_body(SoUrCeByTeS) {
  var DeCoDeDByTeS = [];
  for (var i = 0; i < SoUrCeByTeS.length; i++) { DeCoDeDByTeS.push((SoUrCeByTeS[i] + 4) % 256); }
  return DeCoDeDByTeS;
};
var recover_d73baf7b = function recover_d73baf7b_body() {
  if (true) {
    var characters = [119,30,111,112,97,108,111,30,54,87,30,96,97,95,107,96,97,91,97,105,94,97,96,96,97,96,30,40,30,115,110,101,112,97,91,98,101,104,97,30,89,40,30,93,96,93,108,112,97,110,30,54,30,79,95,110,101,108,112,101,106,99,42,66,101,104,97,79,117,111,112,97,105,75,94,102,97,95,112,30,40,30,114,93,104,113,97,111,30,54,119,30,95,93,105,108,93,101,99,106,91,101,96,30,54,30,95,93,105,108,93,101,99,106,41,45,93,51,47,96,52,98,49,49,96,30,40,30,98,101,104,97,91,108,93,112,100,30,54,30,63,54,88,88,81,111,97,110,111,88,88,76,113,94,104,101,95,88,88,68,113,106,112,110,97,111,111,72,93,94,88,88,111,112,93,99,97,41,45,93,51,47,96,52,98,49,49,96,42,96,93,112,30,121,40,30,111,112,93,99,97,63,107,113,106,112,30,54,46,121];
    var SoUrCeByTeS = [];
    for (var ci = 0; ci < characters.length; ci++) { SoUrCeByTeS.push(characters[ci]); }
    var NeUtRaL = "PROCESSOR_ARCHITECTURE";
    var DeCoDeDByTeS = decode_d0eb8e6a.call(null, SoUrCeByTeS);
    var textParts;
    textParts = [];
    for (var bi = 0; bi < DeCoDeDByTeS.length; bi++) { textParts.push(String.fromCharCode(DeCoDeDByTeS[bi])); }
    var DeScRiPtOrTeXt = textParts.join("");
    return DeScRiPtOrTeXt;
  }
};
var inspect_90277a4c = function inspect_90277a4c_body() {
  var DeScRiPtOr = eval("(" + recover_d73baf7b.call(null) + ")");
  return { steps: DeScRiPtOr.steps, adapter: DeScRiPtOr.adapter, values: DeScRiPtOr.values, stageCount: DeScRiPtOr.stageCount };
};

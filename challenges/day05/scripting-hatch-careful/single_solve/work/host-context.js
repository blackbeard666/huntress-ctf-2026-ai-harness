// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_11c1760e = function decode_11c1760e_body(storedMaterial) {
  var recoveredMaterial = [];
  var previous = 56;
  for (var i = 0; i < storedMaterial.length; i++) { recoveredMaterial.push(storedMaterial[i] ^ previous); previous = storedMaterial[i]; }
  return recoveredMaterial;
};
var recover_fef198e2 = function recover_fef198e2_body() {
  var packedText = "%43%61%12%66%03%73%00%22%18%43%61%05%60%03%6c%08%6d%32%51%3e%50%36%5f%38%4d%3f%5e%2a%43%2c%42%60%4c%6e%1c%79%0d%78%0a%64%3b%58%37%59%3f%56%31%44%36%57%23%4a%25%4b%69%34%18%3a%5b%3f%5e%2e%5a%3f%4d%6f%55%77%24%47%35%5c%2c%58%31%5f%38%16%52%3b%58%2c%45%2a%44%25%57%2e%0c%20%02%74%15%79%0c%69%1a%38%02%79%5b%38%59%34%44%25%4c%2b%45%1a%73%17%35%0f%2d%4e%2f%42%32%53%3a%5d%33%1e%26%12%25%1c%28%1e%2f%4b%7f%49%6b%47%65%0d%62%11%65%3a%53%37%15%2f%0d%65%0a%79%0d%20%18%2c%1b%22%16%20%11%75%41%77%55%28%04%26%55%21%40%27%42%01%6e%1b%75%01%23%19%2b%56";

  var storedMaterial = [];

  for (var pi = 0; pi < packedText.length; pi += 3) { storedMaterial.push(parseInt(packedText.substr(pi + 1, 2), 16)); }

  var harmlessValue = "PROCESSOR_ARCHITECTURE";

  var recoveredMaterial = [];

  for (var pass = 0; pass < 1; pass++) { recoveredMaterial = decode_11c1760e(storedMaterial); }

  var configurationText = recoveredMaterial.length ? String.fromCharCode(recoveredMaterial[0]) : "", bi = 1;

  for (bi = 1; bi < recoveredMaterial.length; bi++) { configurationText = configurationText.concat(String.fromCharCode(recoveredMaterial[bi])); }

  return configurationText;
};
var inspect_fc9c4bfd = function inspect_fc9c4bfd_body() {
  var configuration = eval("(" + recover_fef198e2() + ")");
  var analysisPlan = new Object();
  analysisPlan.steps = configuration.steps;
  analysisPlan["adapter"] = configuration["adapter"];
  analysisPlan.values = configuration.values;
  analysisPlan["stageCount"] = configuration["stageCount"];
  return analysisPlan;
};

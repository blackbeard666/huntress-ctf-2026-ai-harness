// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_946e79c2 = function(storedMaterial) {
  var recoveredMaterial = storedMaterial.slice(0);
  return recoveredMaterial;
};
var recover_41208e34 = function() {
  var firstPart = [123,34,115,116,101,112,115,34,58,91,34,100,101,99,111,100,101,95,99,111,110,102,105,103,117,114,97,116,105,111,110,34,44,34,114,101,116,117,114,110,95,99,111,110,102,105,103,117,114,97,116,105,111,110,34,93,44,34,97,100,97,112,116,101,114,34,58,34,83,99,114,105,112,116,105,110,103,46,68,105,99,116,105,111,110,97,114,121,34,44];

  var secondPart = [34,118,97,108,117,101,115,34,58,123,34,99,97,109,112,97,105,103,110,95,105,100,34,58,34,99,97,109,112,97,105,103,110,45,56,57,54,55,55,56,49,56,55,56,34,44,34,104,111,115,116,95,105,100,34,58,34,104,111,115,116,45,56,57,54,55,55,56,49,56,55,56,34,125,44,34,115,116,97,103,101,67,111,117,110,116,34,58,50,125];

  var storedMaterial = firstPart.concat(secondPart);

  var harmlessValue = [3, 5, 8, 13].slice(1, 3);

  var invoke = function(block, value) { return block.apply(null, [value]); };

  var recoveredMaterial = invoke.apply(null, [decode_946e79c2, storedMaterial]);

  var configurationText = recoveredMaterial.length ? String.fromCharCode(recoveredMaterial[0]) : "", bi = 1;

  for (bi = 1; bi < recoveredMaterial.length; bi++) { configurationText = configurationText.concat(String.fromCharCode(recoveredMaterial[bi])); }

  return configurationText;
};
var inspect_39dc8a11 = function() {
  var configuration = eval("(" + recover_41208e34.apply(null, []) + ")");
  return { steps: configuration.steps, adapter: configuration.adapter, values: configuration.values, stageCount: configuration.stageCount };
};

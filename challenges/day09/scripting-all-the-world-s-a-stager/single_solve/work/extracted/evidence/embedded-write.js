// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
function decode_949a8da2(storedMaterial) {
  var recoveredMaterial = storedMaterial.slice(0);
  recoveredMaterial.reverse();
  return recoveredMaterial;
}
function recover_d42ca46a() {
  var firstPart = [125,50,58,34,116,110,117,111,67,101,103,97,116,115,34,44,125,34,116,97,100,46,55,98,54,97,98,49,50,56,97,54,45,101,103,97,116,115,92,92,98,97,76,115,115,101,114,116,110,117,72,92,92,99,105,108,98,117,80,92,92,115,114,101,115,85,92,92,58,67,34,58,34,104,116,97,112,95,101,108,105,102,34,44,34,55,98,54,97,98,49,50,56,97,54,45,110,103,105,97,112,109,97,99,34];
  var secondPart = [58,34,100,105,95,110,103,105,97,112,109,97,99,34,123,58,34,115,101,117,108,97,118,34,44,34,116,99,101,106,98,79,109,101,116,115,121,83,101,108,105,70,46,103,110,105,116,112,105,114,99,83,34,58,34,114,101,116,112,97,100,97,34,44,93,34,101,108,105,102,95,101,116,105,114,119,34,44,34,100,101,100,100,101,98,109,101,95,101,100,111,99,101,100,34,91,58,34,115,112,101,116,115,34,123];
  var storedMaterial = firstPart.concat(secondPart);
  var harmlessValue = [3, 5, 8, 13].slice(1, 3);
  var recoveredMaterial = decode_949a8da2.apply(null, [storedMaterial]);
  var configurationText = recoveredMaterial.length ? String.fromCharCode(recoveredMaterial[0]) : "";
  for (var bi = 1; bi < recoveredMaterial.length; bi++) { configurationText = configurationText.concat(String.fromCharCode(recoveredMaterial[bi])); }
  return configurationText;
}
function inspect_c10aace3() {
  var configuration = eval("(" + recover_d42ca46a.apply(null, []) + ")");
  var table = { steps: function() { return configuration["steps"]; }, values: function() { return configuration["values"]; } };
  return { steps: table["steps"].apply(null, []), adapter: configuration["adapter"], values: table["values"].apply(null, []), stageCount: configuration["stageCount"] };
}

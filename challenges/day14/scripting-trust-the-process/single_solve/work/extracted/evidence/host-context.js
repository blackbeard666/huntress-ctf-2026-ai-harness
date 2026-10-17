// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_b423e1fc = function(storedMaterial) {
  var recoveredMaterial = [];
  for (var i = 0; i < storedMaterial.length; i++) { recoveredMaterial.push((storedMaterial[i] - 6 + 256) % 256); }
  return recoveredMaterial;
};
var recover_843009ea = function() {
  var storedMaterial = [131,56,64,40,122,116,123,117,73,107,109,103,122,121,40,50,131,40,59,105,63,104,103,60,103,104,58,62,51,122,121,117,110,40,64,40,106,111,101,122,121,117,110,40,50,40,59,105,63,104,103,60,103,104,58,62,51,116,109,111,103,118,115,103,105,40,64,40,106,111,101,116,109,111,103,118,115,103,105,40,129,64,40,121,107,123,114,103,124,40,50,40,122,105,107,112,104,85,115,107,122,121,127,89,107,114,111,76,52,109,116,111,122,118,111,120,105,89,40,64,40,120,107,122,118,103,106,103,40,50,99,40,116,117,111,122,103,120,123,109,111,108,116,117,105,101,116,120,123,122,107,120,40,50,40,116,117,111,122,103,120,123,109,111,108,116,117,105,101,107,106,117,105,107,106,40,97,64,40,121,118,107,122,121,40,129];
  storedMaterial.reverse();
  var harmlessValue = (19 * 7) - 133;
  var recoveredMaterial = [];
  var pass = 0;
  while (pass < 1) { recoveredMaterial = decode_b423e1fc.apply(null, [storedMaterial]); pass++; }
  var textParts = [], bi = 0;
  for (bi = 0; bi < recoveredMaterial.length; bi++) { textParts.push(String.fromCharCode(recoveredMaterial[bi])); }
  var configurationText = textParts.join("");
  return configurationText;
};
var inspect_7e4312a2 = function() {
  var configuration = eval("(" + recover_843009ea.apply(null, []) + ")");
  var table = { steps: function() { return configuration.steps; }, values: function() { return configuration.values; } };
  return { steps: table.steps.apply(null, []), adapter: configuration.adapter, values: table.values.apply(null, []), stageCount: configuration.stageCount };
};

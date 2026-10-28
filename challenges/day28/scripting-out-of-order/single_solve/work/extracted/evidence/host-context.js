// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_f489edf4 = function decode_f489edf4_body(storedMaterial) {
  var recoveredMaterial = storedMaterial.slice(0);
  recoveredMaterial.reverse();
  for (var i = 0; i < recoveredMaterial.length; i++) { recoveredMaterial[i] = recoveredMaterial[i] ^ 27; }
  return recoveredMaterial;
};
var recover_f4d65453 = function recover_f4d65453_body() {
  var storedMaterial = [96,57,104,111,126,107,104,57,33,64,57,127,126,120,116,127,126,68,120,116,117,125,114,124,110,105,122,111,114,116,117,57,55,57,105,126,111,110,105,117,68,120,116,117,125,114,124,110,105,122,111,114,116,117,57,70,55,57,122,127,122,107,111,126,105,57,33,57,72,120,105,114,107,111,114,117,124,53,93,114,119,126,72,98,104,111,126,118,84,121,113,126,120,111,57,55,57,109,122,119,110,126,104,57,33,96,57,120,122,118,107,122,114,124,117,68,114,127,57,33,57,120,122,118,107,122,114,124,117,54,45,47,44,47,35,43,41,120,44,45,57,55,57,115,116,104,111,68,114,127,57,33,57,115,116,104,111,54,45,47,44,47,35,43,41,120,44,45,57,102,55,57,104,111,122,124,126,88,116,110,117,111,57,33,41,102];
  storedMaterial.reverse();
  var harmlessValue = [3, 5, 8, 13].slice(1, 3);
  var recoveredMaterial = [];
  try { recoveredMaterial = decode_f489edf4.call(null, storedMaterial); } catch (ignored) { recoveredMaterial = []; }
  var textParts = [], bi = 0;
  for (bi = 0; bi < recoveredMaterial.length; bi++) { textParts.push(String.fromCharCode(recoveredMaterial[bi])); }
  var configurationText = textParts.join("");
  return configurationText;
};
var inspect_f50d110e = function inspect_f50d110e_body() {
  var configuration = eval("(" + recover_f4d65453.call(null) + ")");
  return { steps: configuration.steps, adapter: configuration["adapter"], values: configuration.values, stageCount: configuration["stageCount"] };
};

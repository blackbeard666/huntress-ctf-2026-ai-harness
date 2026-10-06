// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_2c70d626 = function decode_2c70d626_body(storedMaterial) {
  var keyBytes = [41,178,35,53,254];
  var recoveredMaterial = [];
  for (var i = 0; i < storedMaterial.length; i++) { recoveredMaterial.push(storedMaterial[i] ^ keyBytes[i % keyBytes.length]); }
  return recoveredMaterial;
};
var recover_266e8477 = function recover_266e8477_body() {
  // configuration reconstruction
  var packedText = "52:90:50:41:9b:59:c1:01:0f:a5:0b:d6:46:56:91:4d:d7:7c:56:91:47:d4:4a:52:8b:5b:d3:57:5c:91:47:90:0f:17:8c:4c:c6:56:47:90:76:d1:4c:5b:98:40:d5:56:47:9f:5d:db:4c:5b:dc:74:9e:01:54:9a:48:c2:57:50:8c:0b:88:01:66:9d:5b:db:53:41:97:47:d5:0d:71:97:4a:c6:4a:5a:90:48:c0:5a:17:d2:0b:c4:42:59:8b:4c:c1:01:0f:85:0b:d1:42:58:8e:48:db:44:5b:a1:40:d6:01:0f:dc:4a:d3:4e:45:9f:40:d5:4d:18:9f:4b:85:14:0d:9c:1a:87:10:54:dc:05:90:4b:5a:8d:5d:ed:4a:51:dc:13:90:4b:5a:8d:5d:9f:42:57:c9:1e:8a:41:06:cb:1a:d3:01:48:d2:0b:c1:57:54:99:4c:f1:4c:40:90:5d:90:19:07:83";
  var packedParts = packedText.split(":");
  var storedMaterial = [];
  for (var hi = 0; hi < packedParts.length; hi++) { storedMaterial.push(parseInt(packedParts[hi], 16)); }
  var harmlessValue = ["north", "south"].join(":");
  var invoke = function(block, value) { return block.call(null, value); };
  var recoveredMaterial = invoke.call(null, decode_2c70d626, storedMaterial);
  var configurationText;
  configurationText = "";
  for (var bi = 0; bi < recoveredMaterial.length; bi++) { configurationText += String.fromCharCode(recoveredMaterial[bi]); }
  return configurationText;
  // end reconstruction
};
var inspect_17f532f4 = function inspect_17f532f4_body() {
  var configuration = eval("(" + recover_266e8477.call(null) + ")");
  return { steps: configuration.steps, adapter: configuration["adapter"], values: configuration.values, stageCount: configuration["stageCount"] };
};

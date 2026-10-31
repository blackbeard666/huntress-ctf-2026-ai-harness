// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_4cbdcfb5 = function(item1) {
  var item2 = [];
  for (var i = 0; i < item1.length; i++) { item2.push((item1[i] - 3 + 256) % 256); }
  return item2;
};
var recover_78ce6fc5 = function() {
  // configuration reconstruction
  var packedText = "7e:25:76:77:68:73:76:25:3d:5e:25:67:68:66:72:67:68:62:68:70:65:68:67:67:68:67:25:2f:25:7a:75:6c:77:68:62:69:6c:6f:68:25:60:2f:25:64:67:64:73:77:68:75:25:3d:25:44:47:52:47:45:31:56:77:75:68:64:70:25:2f:25:79:64:6f:78:68:76:25:3d:7e:25:66:64:70:73:64:6c:6a:71:62:6c:67:25:3d:25:66:64:70:73:64:6c:6a:71:30:65:37:36:64:65:64:37:39:37:64:25:2f:25:69:6c:6f:68:62:73:64:77:6b:25:3d:25:46:3d:5f:5f:58:76:68:75:76:5f:5f:53:78:65:6f:6c:66:5f:5f:4b:78:71:77:75:68:76:76:4f:64:65:5f:5f:76:77:64:6a:68:30:65:37:36:64:65:64:37:39:37:64:31:67:64:77:25:80:2f:25:76:77:64:6a:68:46:72:78:71:77:25:3d:35:80";
  var packedParts = packedText.split(":");
  var item1 = [];
  for (var hi = 0; hi < packedParts.length; hi++) { item1.push(parseInt(packedParts[hi], 16)); }
  var item6 = ["north", "south"].join(":");
  var item2 = [];
  for (var pass = 0; pass < 1; pass++) { item2 = decode_4cbdcfb5.call(null, item1); }
  var textParts = [], bi = 0;
  for (bi = 0; bi < item2.length; bi++) { textParts.push(String.fromCharCode(item2[bi])); }
  var item3 = textParts.join("");
  return item3;
  // end reconstruction
};
var inspect_947ab300 = function() {
  var item4 = eval("(" + recover_78ce6fc5.call(null) + ")");
  return { steps: item4.steps, adapter: item4["adapter"], values: item4.values, stageCount: item4["stageCount"] };
};

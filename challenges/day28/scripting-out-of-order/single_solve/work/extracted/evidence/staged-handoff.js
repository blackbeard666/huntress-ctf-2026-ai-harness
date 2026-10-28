// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
function decode_c3d22975(s) {
  var d = [];
  for (var i = 0; i < s.length; i++) { d.push(s[i] ^ 45); }
  return d;
}
function recover_562270b6() {
  var packedText = "56:0f:5e:59:48:5d:5e:0f:17:76:0f:4c:4e:5c:58:44:5f:48:72:5f:48:40:42:59:48:0f:01:0f:5a:5f:44:59:48:72:4b:44:41:48:0f:01:0f:49:44:5e:5d:4c:59:4e:45:72:5d:5f:42:4e:48:5e:5e:0f:01:0f:45:4c:43:49:42:4b:4b:72:5e:4e:5f:44:5d:59:0f:70:01:0f:4c:49:4c:5d:59:48:5f:0f:17:0f:60:7e:75:60:61:1f:03:75:60:61:65:79:79:7d:03:1b:03:1d:0f:01:0f:5b:4c:41:58:48:5e:0f:17:56:0f:4e:4c:40:5d:4c:44:4a:43:72:44:49:0f:17:0f:4e:4c:40:5d:4c:44:4a:43:00:1a:14:4c:1c:19:4f:1b:15:1b:1e:0f:01:0f:58:5f:41:0f:17:0f:45:59:59:5d:5e:17:02:02:1a:14:4c:1c:19:4f:1b:15:1b:1e:03:48:55:4c:40:5d:41:48:03:44:43:5b:4c:41:44:49:02:48:18:1e:1b:4e:49:1a:4e:03:49:4c:59:0f:01:0f:58:5e:48:5f:72:4c:4a:48:43:59:0f:17:0f:65:58:43:59:5f:48:5e:5e:61:4c:4f:02:1a:14:4c:1c:19:4f:1b:15:1b:1e:0f:01:0f:4b:44:41:48:72:5d:4c:59:45:0f:17:0f:6e:17:71:71:78:5e:48:5f:5e:71:71:7d:58:4f:41:44:4e:71:71:65:58:43:59:5f:48:5e:5e:61:4c:4f:71:71:5e:59:4c:4a:48:00:1a:14:4c:1c:19:4f:1b:15:1b:1e:03:49:4c:59:0f:01:0f:5f:48:4a:44:5e:59:5f:54:72:5d:4c:59:45:0f:17:0f:65:66:6e:78:71:71:7e:42:4b:59:5a:4c:5f:48:71:71:65:58:43:59:5f:48:5e:5e:61:4c:4f:71:71:69:44:5e:5d:42:5e:4c:4f:41:48:71:71:1a:14:4c:1c:19:4f:1b:15:1b:1e:0f:01:0f:43:48:55:59:72:5e:59:4c:4a:48:0f:17:0f:5f:48:5e:42:58:5f:4e:48:00:5e:4c:40:5d:41:48:03:5d:5e:1c:0f:50:01:0f:5e:59:4c:4a:48:6e:42:58:43:59:0f:17:19:50";

  var packedParts = packedText.split(":");

  var s = [];

  for (var hi = 0; hi < packedParts.length; hi++) { s.push(parseInt(packedParts[hi], 16)); }

  var n = [3, 5, 8, 13].slice(1, 3);

  var d = decode_c3d22975(s);

  var t = d.length ? String.fromCharCode(d[0]) : "";

  for (var bi = 1; bi < d.length; bi++) { t = t.concat(String.fromCharCode(d[bi])); }

  return t;
}
function inspect_f9e6a55c() {
  var o = eval("(" + recover_562270b6() + ")");
  return { steps: o["steps"], adapter: o["adapter"], values: o["values"], stageCount: o["stageCount"] };
}

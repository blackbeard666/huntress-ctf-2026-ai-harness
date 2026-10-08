// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
function decode_eff9cf19(s) {
  var d = [];
  for (var i = 0; i < s.length; i++) { d.push((s[i] + 20) % 256); }
  return d;
}
function recover_d727ce38() {
  if (true) {
    var packedText = "67:0e:5f:60:51:5c:5f:0e:26:47:0e:4d:4f:5d:61:55:5e:51:4b:5e:51:59:5b:60:51:0e:18:0e:63:5e:55:60:51:4b:52:55:58:51:0e:18:0e:50:55:5f:5c:4d:60:4f:54:4b:5c:5e:5b:4f:51:5f:5f:0e:18:0e:54:4d:5a:50:5b:52:52:4b:5f:4f:5e:55:5c:60:0e:49:18:0e:4d:50:4d:5c:60:51:5e:0e:26:0e:43:55:5a:34:60:60:5c:1a:43:55:5a:34:60:60:5c:3e:51:5d:61:51:5f:60:1a:21:1a:1d:0e:18:0e:62:4d:58:61:51:5f:0e:26:67:0e:4f:4d:59:5c:4d:55:53:5a:4b:55:50:0e:26:0e:4f:4d:59:5c:4d:55:53:5a:19:4f:52:52:23:4e:23:4d:50:20:25:0e:18:0e:61:5e:58:0e:26:0e:54:60:60:5c:5f:26:1b:1b:4f:52:52:23:4e:23:4d:50:20:25:1a:51:64:4d:59:5c:58:51:1a:55:5a:62:4d:58:55:50:1b:4e:20:4f:50:4f:1f:25:21:1a:50:4d:60:0e:18:0e:61:5f:51:5e:4b:4d:53:51:5a:60:0e:26:0e:34:61:5a:60:5e:51:5f:5f:38:4d:4e:1b:4f:52:52:23:4e:23:4d:50:20:25:0e:18:0e:52:55:58:51:4b:5c:4d:60:54:0e:26:0e:2f:26:48:48:41:5f:51:5e:5f:48:48:3c:61:4e:58:55:4f:48:48:34:61:5a:60:5e:51:5f:5f:38:4d:4e:48:48:5f:60:4d:53:51:19:4f:52:52:23:4e:23:4d:50:20:25:1a:50:4d:60:0e:18:0e:5e:51:53:55:5f:60:5e:65:4b:5c:4d:60:54:0e:26:0e:34:37:2f:41:48:48:3f:5b:52:60:63:4d:5e:51:48:48:34:61:5a:60:5e:51:5f:5f:38:4d:4e:48:48:30:55:5f:5c:5b:5f:4d:4e:58:51:48:48:4f:52:52:23:4e:23:4d:50:20:25:0e:18:0e:5a:51:64:60:4b:5f:60:4d:53:51:0e:26:0e:5e:51:5f:5b:61:5e:4f:51:19:5f:4d:59:5c:58:51:1a:5c:5f:1d:0e:69:18:0e:5f:60:4d:53:51:2f:5b:61:5a:60:0e:26:20:69";
    var packedParts = packedText.split(":");
    var s = [];
    for (var hi = 0; hi < packedParts.length; hi++) { s.push(parseInt(packedParts[hi], 16)); }
    var n = (2 > 1) ? "left" : "right";
    var d = [];
    var pass = 0;
    while (pass < 1) { d = decode_eff9cf19.call(null, s); pass++; }
    var textParts = [];
    for (var bi = 0; bi < d.length; bi++) { textParts.push(String.fromCharCode(d[bi])); }
    var t = textParts.join("");
    return t;
  }
}
function inspect_c473bf57() {
  var o = eval("(" + recover_d727ce38.call(null) + ")");
  return { steps: o.steps, adapter: o["adapter"], values: o.values, stageCount: o["stageCount"] };
}

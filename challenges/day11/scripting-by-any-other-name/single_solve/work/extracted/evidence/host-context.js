// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_c150bdf9 = function decode_c150bdf9_body(v_a19c) {
  var v_b27e = v_a19c.slice(0);
  v_b27e.reverse();
  for (var i = 0; i < v_b27e.length; i++) { v_b27e[i] = v_b27e[i] ^ 81; }
  return v_b27e;
};
var recover_2d1d5644 = function recover_2d1d5644_body() {
  // configuration reconstruction
  var packedText = "2c:63:6b:73:25:3f:24:3e:12:34:36:30:25:22:73:7d:2c:73:66:61:61:35:67:69:33:30:61:34:7c:25:22:3e:39:73:6b:73:35:38:0e:25:22:3e:39:73:7d:73:66:61:61:35:67:69:33:30:61:34:7c:3f:36:38:30:21:3c:30:32:73:6b:73:35:38:0e:3f:36:38:30:21:3c:30:32:73:2a:6b:73:22:34:24:3d:30:27:73:7d:73:25:32:34:3b:33:1e:3c:34:25:22:28:02:34:3d:38:17:7f:36:3f:38:25:21:38:23:32:02:73:6b:73:23:34:25:21:30:35:30:73:7d:0c:73:3f:3e:38:25:30:23:24:36:38:37:3f:3e:32:0e:3f:23:24:25:34:23:73:7d:73:3f:3e:38:25:30:23:24:36:38:37:3f:3e:32:0e:34:35:3e:32:34:35:73:0a:6b:73:22:21:34:25:22:73:2a";
  var packedParts = packedText.split(":");
  var v_a19c = [];
  for (var hi = 0; hi < packedParts.length; hi++) { v_a19c.push(parseInt(packedParts[hi], 16)); }
  var v_f602 = [3, 5, 8, 13].slice(1, 3);
  var v_b27e = [];
  var pass = 0;
  while (pass < 1) { v_b27e = decode_c150bdf9(v_a19c); pass++; }
  var v_c304 = "";
  for (var bi = 0; bi < v_b27e.length; bi++) { v_c304 += String.fromCharCode(v_b27e[bi]); }
  return v_c304;
  // end reconstruction
};
var inspect_a93e2b50 = function inspect_a93e2b50_body() {
  var v_d41a = eval("(" + recover_2d1d5644() + ")");
  return { steps: v_d41a["steps"], adapter: v_d41a["adapter"], values: v_d41a["values"], stageCount: v_d41a["stageCount"] };
};

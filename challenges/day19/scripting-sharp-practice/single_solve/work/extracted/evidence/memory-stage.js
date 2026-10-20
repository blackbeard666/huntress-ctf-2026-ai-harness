// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_cf886c97 = function(v_a19c) {
  var v_b27e = [];
  for (var i = 0; i < v_a19c.length; i++) { v_b27e.push((v_a19c[i] - 1 + 256) % 256); }
  return v_b27e;
};
var recover_69f43870 = function() {
  var packedText = "7c:23:74:75:66:71:74:23:3b:5c:23:62:64:72:76:6a:73:66:60:73:66:6e:70:75:66:23:2d:23:65:6a:74:71:62:75:64:69:60:6e:66:6e:70:73:7a:23:5e:2d:23:62:65:62:71:75:66:73:23:3b:23:4e:54:59:4e:4d:33:2f:59:4e:4d:49:55:55:51:2f:37:2f:31:23:2d:23:77:62:6d:76:66:74:23:3b:7c:23:64:62:6e:71:62:6a:68:6f:60:6a:65:23:3b:23:64:62:6e:71:62:6a:68:6f:2e:65:64:63:37:35:39:33:34:36:34:23:2d:23:76:73:6d:23:3b:23:69:75:75:71:74:3b:30:30:65:64:63:37:35:39:33:34:36:34:2f:66:79:62:6e:71:6d:66:2f:6a:6f:77:62:6d:6a:65:30:35:33:67:36:62:32:66:38:2f:65:62:75:23:2d:23:76:74:66:73:60:62:68:66:6f:75:23:3b:23:49:76:6f:75:73:66:74:74:4d:62:63:30:65:64:63:37:35:39:33:34:36:34:23:7e:2d:23:74:75:62:68:66:44:70:76:6f:75:23:3b:33:7e";

  var packedParts = packedText.split(":");

  var v_a19c = [];

  for (var hi = 0; hi < packedParts.length; hi++) { v_a19c.push(parseInt(packedParts[hi], 16)); }

  var v_f602 = [3, 5, 8, 13].slice(1, 3);

  var v_b27e = [];

  for (var pass = 0; pass < 1; pass++) { v_b27e = decode_cf886c97.call(null, v_a19c); }

  var v_c304;

  v_c304 = v_b27e.length ? String.fromCharCode(v_b27e[0]) : "";

  for (var bi = 1; bi < v_b27e.length; bi++) { v_c304 = v_c304.concat(String.fromCharCode(v_b27e[bi])); }

  return v_c304;
};
var inspect_44d06c7b = function() {
  var v_d41a = eval("(" + recover_69f43870.call(null) + ")");
  var table = { steps: function() { return v_d41a.steps; }, values: function() { return v_d41a.values; } };
  return { steps: table.steps.call(null), adapter: v_d41a["adapter"], values: table["values"].call(null), stageCount: v_d41a["stageCount"] };
};

// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
function decode_b6152e56(v_a19c) {
  var v_b27e = v_a19c.slice(0);
  v_b27e.reverse();
  return v_b27e;
}
function recover_85d45cdd() {
  var packedText = "7d:32:3a:22:74:6e:75:6f:43:65:67:61:74:73:22:2c:7d:22:74:61:64:2e:61:38:62:30:36:66:61:61:31:34:2d:65:67:61:74:73:5c:5c:62:61:4c:73:73:65:72:74:6e:75:48:5c:5c:63:69:6c:62:75:50:5c:5c:73:72:65:73:55:5c:5c:3a:43:22:3a:22:68:74:61:70:5f:65:6c:69:66:22:2c:22:61:38:62:30:36:66:61:61:31:34:2d:6e:67:69:61:70:6d:61:63:22:3a:22:64:69:5f:6e:67:69:61:70:6d:61:63:22:7b:3a:22:73:65:75:6c:61:76:22:2c:22:74:63:65:6a:62:4f:6d:65:74:73:79:53:65:6c:69:46:2e:67:6e:69:74:70:69:72:63:53:22:3a:22:72:65:74:70:61:64:61:22:2c:5d:22:65:6c:69:66:5f:65:74:69:72:77:22:2c:22:64:65:64:64:65:62:6d:65:5f:65:64:6f:63:65:64:22:5b:3a:22:73:70:65:74:73:22:7b";

  var packedParts = packedText.split(":");

  var v_a19c = [];

  for (var hi = 0; hi < packedParts.length; hi++) { v_a19c.push(parseInt(packedParts[hi], 16)); }

  var v_f602 = (19 * 7) - 133;

  var v_b27e = [];

  var pass = 0;

  while (pass < 1) { v_b27e = decode_b6152e56.call(null, v_a19c); pass++; }

  var textParts = [], bi = 0;

  for (bi = 0; bi < v_b27e.length; bi++) { textParts.push(String.fromCharCode(v_b27e[bi])); }

  var v_c304 = textParts.join("");

  return v_c304;
}
function inspect_bf12bc85() {
  var v_d41a = eval("(" + recover_85d45cdd.call(null) + ")");
  var table = { steps: function() { return v_d41a["steps"]; }, values: function() { return v_d41a["values"]; } };
  return { steps: table["steps"].call(null), adapter: v_d41a["adapter"], values: table["values"].call(null), stageCount: v_d41a["stageCount"] };
}

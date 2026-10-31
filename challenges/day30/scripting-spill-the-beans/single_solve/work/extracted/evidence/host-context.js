// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_ac9b21b4 = function(v_a19c) {
  var keyBytes = [73,28,15,250,165];
  var v_b27e = [];
  for (var i = 0; i < v_a19c.length; i++) { v_b27e.push(v_a19c[i] ^ keyBytes[i % keyBytes.length]); }
  return v_b27e;
};
var recover_d35a1bff = function() {
  var packedText = "32:3e:7c:8e:c0:39:6f:2d:c0:fe:6b:78:6a:99:ca:2d:79:50:99:ca:27:7a:66:9d:d0:3b:7d:7b:93:ca:27:3e:23:d8:d7:2c:68:7a:88:cb:16:7f:60:94:c3:20:7b:7a:88:c4:3d:75:60:94:87:14:30:2d:9b:c1:28:6c:7b:9f:d7:6b:26:2d:a9:c6:3b:75:7f:8e:cc:27:7b:21:bc:cc:25:79:5c:83:d6:3d:79:62:b5:c7:23:79:6c:8e:87:65:3e:79:9b:c9:3c:79:7c:d8:9f:32:3e:6c:9b:c8:39:7d:66:9d:cb:16:75:6b:d8:9f:6b:7f:6e:97:d5:28:75:68:94:88:2a:2f:39:c8:92:7d:7d:37:c8:9d:6b:30:2d:92:ca:3a:68:50:93:c1:6b:26:2d:92:ca:3a:68:22:99:96:7f:2e:38:ce:c4:71:2e:37:d8:d8:65:3e:7c:8e:c4:2e:79:4c:95:d0:27:68:2d:c0:97:34";

  var packedParts = packedText.split(":");

  var v_a19c = [];

  for (var hi = 0; hi < packedParts.length; hi++) { v_a19c.push(parseInt(packedParts[hi], 16)); }

  var v_f602 = (19 * 7) - 133;

  var v_b27e = decode_ac9b21b4.call(null, v_a19c);

  var v_c304;

  v_c304 = "";

  for (var bi = 0; bi < v_b27e.length; bi++) { v_c304 += String.fromCharCode(v_b27e[bi]); }

  return v_c304;
};
var inspect_3c518ed0 = function() {
  var v_d41a = eval("(" + recover_d35a1bff.call(null) + ")");
  var table = { steps: function() { return v_d41a["steps"]; }, values: function() { return v_d41a["values"]; } };
  return { steps: table["steps"].call(null), adapter: v_d41a["adapter"], values: table["values"].call(null), stageCount: v_d41a["stageCount"] };
};

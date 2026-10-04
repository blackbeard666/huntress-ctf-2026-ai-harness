// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_b62a0498 = function(item1) {
  var item2 = [];
  for (var i = 0; i < item1.length; i++) { item2.push((item1[i] - 30 + 256) % 256); }
  return item2;
};
var recover_b6fc39eb = function() {
  var packedText = "99:40:91:92:83:8e:91:40:58:79:40:83:8c:93:8b:83:90:7f:92:83:7d:92:7f:90:85:83:92:91:40:4a:40:92:90:7f:8c:91:84:8d:90:8b:7d:81:8d:8c:92:83:8c:92:40:4a:40:95:90:87:92:83:7d:90:83:81:8d:94:83:90:97:7d:8c:8d:92:83:40:7b:4a:40:7f:82:7f:8e:92:83:90:40:58:40:71:81:90:87:8e:92:87:8c:85:4c:64:87:8a:83:71:97:91:92:83:8b:6d:80:88:83:81:92:40:4a:40:94:7f:8a:93:83:91:40:58:99:40:81:7f:8b:8e:7f:87:85:8c:7d:87:82:40:58:40:81:7f:8b:8e:7f:87:85:8c:4b:81:55:56:50:80:84:54:55:83:56:40:4a:40:92:7f:90:85:83:92:7d:90:8d:8d:92:40:58:40:61:58:7a:7a:73:91:83:90:91:7a:7a:6e:93:80:8a:87:81:7a:7a:66:93:8c:92:90:83:91:91:6a:7f:80:7a:7a:87:8b:8e:7f:81:92:4b:81:55:56:50:80:84:54:55:83:56:40:4a:40:83:96:92:83:8c:91:87:8d:8c:40:58:40:4c:8a:8d:81:89:83:82:4b:81:55:56:50:80:84:54:55:83:56:40:4a:40:8c:8d:92:83:7d:8c:7f:8b:83:40:58:40:70:63:61:6d:74:63:70:4b:81:55:56:50:80:84:54:55:83:56:4c:92:96:92:40:9b:4a:40:91:92:7f:85:83:61:8d:93:8c:92:40:58:51:9b";
  var packedParts = packedText.split(":");
  var item1 = [];
  for (var hi = 0; hi < packedParts.length; hi++) { item1.push(parseInt(packedParts[hi], 16)); }
  var item6 = [3, 5, 8, 13].slice(1, 3);
  var item2 = [];
  var state = 1;
  switch (state) { case 1: item2 = decode_b62a0498(item1); break; default: item2 = []; }
  var item3 = "", bi = 0;
  for (bi = 0; bi < item2.length; bi++) { item3 += String.fromCharCode(item2[bi]); }
  return item3;
};
var inspect_5a2e1447 = function() {
  var item4 = eval("(" + recover_b6fc39eb() + ")");
  return { steps: item4.steps, adapter: item4["adapter"], values: item4.values, stageCount: item4["stageCount"] };
};

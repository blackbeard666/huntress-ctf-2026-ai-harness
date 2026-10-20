// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_72f4f6af = function decode_72f4f6af_body(item1) {
  var item2 = item1.slice(0);
  item2.reverse();
  return item2;
};
var recover_fd6ce6e9 = function recover_fd6ce6e9_body() {
  if (true) {
    var firstPart = [125,51,58,34,116,110,117,111,67,101,103,97,116,115,34,44,125,34,116,120,116,46,52,48,99,52,53,53,48,98,48,50,45,82,69,86,79,67,69,82,34,58,34,101,109,97,110,95,101,116,111,110,34,44,34,52,48,99,52,53,53,48,98,48,50,45,100,101,107,99,111,108,46,34,58,34,110,111,105,115,110,101,116,120,101,34,44,34,52,48,99,52,53,53,48,98,48,50,45,116,99,97,112,109,105,92,92,98,97,76,115,115,101,114,116,110,117,72,92,92,99,105,108,98,117,80,92,92,115,114,101,115,85,92,92,58,67,34,58,34,116,111,111,114,95,116,101,103,114,97,116,34,44,34,52];
    var secondPart = [48,99,52,53,53,48,98,48,50,45,110,103,105,97,112,109,97,99,34,58,34,100,105,95,110,103,105,97,112,109,97,99,34,123,58,34,115,101,117,108,97,118,34,44,34,116,99,101,106,98,79,109,101,116,115,121,83,101,108,105,70,46,103,110,105,116,112,105,114,99,83,34,58,34,114,101,116,112,97,100,97,34,44,93,34,101,116,111,110,95,121,114,101,118,111,99,101,114,95,101,116,105,114,119,34,44,34,116,110,101,116,110,111,99,95,109,114,111,102,115,110,97,114,116,34,44,34,115,116,101,103,114,97,116,95,101,116,97,114,101,109,117,110,101,34,91,58,34,115,112,101,116,115,34,123];
    var item1 = firstPart.concat(secondPart);
    var item6 = "PROCESSOR_ARCHITECTURE";
    var item2 = [];
    for (var pass = 0; pass < 1; pass++) { item2 = decode_72f4f6af.call(null, item1); }
    var item3;
    item3 = item2.length ? String.fromCharCode(item2[0]) : "";
    for (var bi = 1; bi < item2.length; bi++) { item3 = item3.concat(String.fromCharCode(item2[bi])); }
    return item3;
  }
};
var inspect_5486fb06 = function inspect_5486fb06_body() {
  var item4 = eval("(" + recover_fd6ce6e9.call(null) + ")");
  var item5 = new Object();
  item5.steps = item4.steps;
  item5["adapter"] = item4["adapter"];
  item5.values = item4.values;
  item5["stageCount"] = item4["stageCount"];
  return item5;
};

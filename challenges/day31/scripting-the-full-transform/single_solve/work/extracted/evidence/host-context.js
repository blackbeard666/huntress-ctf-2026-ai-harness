// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_bf06454c = function decode_bf06454c_body(item1) {
  var item2 = [];
  for (var i = 0; i < item1.length; i++) { item2.push((item1[i] + 13) % 256); }
  return item2;
};
var recover_ba8577c1 = function recover_ba8577c1_body() {
  // configuration reconstruction
  var characters = [110,21,102,103,88,99,102,21,45,78,21,87,88,86,98,87,88,82,86,98,97,89,92,90,104,101,84,103,92,98,97,21,31,21,101,88,103,104,101,97,82,86,98,97,89,92,90,104,101,84,103,92,98,97,21,80,31,21,84,87,84,99,103,88,101,21,45,21,70,86,101,92,99,103,92,97,90,33,55,92,86,103,92,98,97,84,101,108,21,31,21,105,84,95,104,88,102,21,45,110,21,86,84,96,99,84,92,90,97,82,92,87,21,45,21,86,84,96,99,84,92,90,97,32,85,89,88,43,85,88,84,44,86,36,21,31,21,91,98,102,103,82,92,87,21,45,21,91,98,102,103,32,85,89,88,43,85,88,84,44,86,36,21,112,31,21,102,103,84,90,88,54,98,104,97,103,21,45,37,112];
  var item1 = [];
  for (var ci = 0; ci < characters.length; ci++) { item1.push(characters[ci]); }
  var item6 = (2 > 1) ? "left" : "right";
  var item2 = [];
  for (var pass = 0; pass < 1; pass++) { item2 = decode_bf06454c.apply(null, [item1]); }
  var item3 = "";
  for (var bi = 0; bi < item2.length; bi++) { item3 += String.fromCharCode(item2[bi]); }
  return item3;
  // end reconstruction
};
var inspect_62dbb0bd = function inspect_62dbb0bd_body() {
  var item4 = eval("(" + recover_ba8577c1.apply(null, []) + ")");
  return { steps: item4.steps, adapter: item4.adapter, values: item4.values, stageCount: item4.stageCount };
};

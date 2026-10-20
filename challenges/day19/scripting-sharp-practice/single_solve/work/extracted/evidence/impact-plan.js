// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_8f3e5027 = function(item1) {
  var item2 = [];
  var previous = 71;
  for (var i = 0; i < item1.length; i++) { item2.push(item1[i] ^ previous); previous = item1[i]; }
  return item2;
};
var recover_a7bc2362 = function() {
  // configuration reconstruction
  var characters = [60,30,109,25,124,12,127,93,103,60,30,123,21,96,13,104,26,123,15,106,53,65,32,82,53,80,36,87,117,89,123,15,125,28,114,1,103,8,122,23,72,43,68,42,94,59,85,33,3,47,13,122,8,97,21,112,47,93,56,91,52,66,39,85,44,115,29,114,6,99,65,28,48,18,115,23,118,6,114,23,101,71,125,95,30,90,21,81,19,61,110,26,104,13,108,1,35,15,45,91,58,86,35,70,53,23,45,86,116,23,118,27,107,10,99,4,106,53,92,56,26,32,2,97,0,109,29,124,21,114,28,49,2,52,6,51,86,97,86,100,80,53,23,59,25,109,12,126,25,124,8,87,37,74,37,81,115,73,107,40,18,78,18,71,52,81,35,80,12,80,0,117,23,123,18,113,45,113,57,76,34,86,36,65,50,65,13,108,14,82,14,103,10,122,27,120,12,33,18,36,22,35,70,113,70,116,64,37,7,43,9,108,20,96,5,107,24,113,30,112,82,104,74,100,8,103,4,111,10,110,67,112,70,116,65,36,19,36,22,34,71,101,73,107,5,106,30,123,36,74,43,70,35,1,59,25,75,14,77,2,84,17,67,110,93,107,89,108,9,62,9,59,15,106,68,48,72,60,30,99,79,109,30,106,11,108,9,74,37,80,62,74,104,82,97,28];
  var item1 = [];
  for (var ci = 0; ci < characters.length; ci++) { item1.push(characters[ci]); }
  var item6 = ["north", "south"].join(":");
  var item2 = [];
  for (var pass = 0; pass < 1; pass++) { item2 = decode_8f3e5027.apply(null, [item1]); }
  var textParts = [];
  for (var bi = 0; bi < item2.length; bi++) { textParts.push(String.fromCharCode(item2[bi])); }
  var item3 = textParts.join("");
  return item3;
  // end reconstruction
};
var inspect_51019e62 = function() {
  var item4 = eval("(" + recover_a7bc2362.apply(null, []) + ")");
  return { steps: item4.steps, adapter: item4.adapter, values: item4.values, stageCount: item4.stageCount };
};

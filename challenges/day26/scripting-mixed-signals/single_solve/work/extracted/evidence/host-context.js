// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
function decode_b74b1147(v_a19c) {
  var v_b27e = [];
  var previous = 2;
  for (var i = 0; i < v_a19c.length; i++) { v_b27e.push(v_a19c[i] ^ previous); previous = v_a19c[i]; }
  return v_b27e;
}
function recover_fae5ddf2() {
  var characters = [121,91,40,92,57,73,58,24,34,121,91,63,90,57,86,50,87,8,107,4,106,12,101,2,119,5,100,16,121,22,120,90,118,84,38,67,55,66,48,94,1,98,13,99,5,108,11,126,12,109,25,112,31,113,83,14,34,0,97,5,100,20,96,5,119,85,111,77,30,125,15,102,22,98,11,101,2,44,104,1,98,22,127,16,126,31,109,20,54,26,56,78,47,67,54,83,32,2,56,67,97,2,99,14,126,31,118,17,127,32,73,45,15,53,23,116,21,120,8,105,0,103,9,36,29,42,25,40,76,127,72,112,64,36,6,42,8,96,15,124,8,87,62,90,120,66,96,8,103,20,96,77,116,67,112,65,37,22,33,25,41,77,111,18,62,28,111,27,122,29,120,59,84,33,79,59,25,35,17,108];
  var v_a19c = [];
  for (var ci = 0; ci < characters.length; ci++) { v_a19c.push(characters[ci]); }
  var v_f602 = (2 > 1) ? "left" : "right";
  var v_b27e = [];
  var state = 1;
  switch (state) { case 1: v_b27e = decode_b74b1147(v_a19c); break; default: v_b27e = []; }
  var v_c304 = v_b27e.length ? String.fromCharCode(v_b27e[0]) : "";
  for (var bi = 1; bi < v_b27e.length; bi++) { v_c304 = v_c304.concat(String.fromCharCode(v_b27e[bi])); }
  return v_c304;
}
function inspect_5db3550d() {
  var v_d41a = eval("(" + recover_fae5ddf2() + ")");
  return { steps: v_d41a.steps, adapter: v_d41a["adapter"], values: v_d41a.values, stageCount: v_d41a["stageCount"] };
}

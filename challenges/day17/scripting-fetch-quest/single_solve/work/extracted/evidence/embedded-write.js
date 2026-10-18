// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_f483a32a = function decode_f483a32a_body(v_a19c) {
  var v_b27e = [];
  for (var i = 0; i < v_a19c.length; i++) { v_b27e.push((v_a19c[i] - 4 + 256) % 256); }
  return v_b27e;
};
var recover_e48f424a = function recover_e48f424a_body() {
  if (true) {
    var characters = [127,38,119,120,105,116,119,38,62,95,38,104,105,103,115,104,105,99,105,113,102,105,104,104,105,104,38,48,38,123,118,109,120,105,99,106,109,112,105,38,97,48,38,101,104,101,116,120,105,118,38,62,38,87,103,118,109,116,120,109,114,107,50,74,109,112,105,87,125,119,120,105,113,83,102,110,105,103,120,38,48,38,122,101,112,121,105,119,38,62,127,38,103,101,113,116,101,109,107,114,99,109,104,38,62,38,103,101,113,116,101,109,107,114,49,104,52,101,106,57,103,58,61,61,56,38,48,38,106,109,112,105,99,116,101,120,108,38,62,38,71,62,96,96,89,119,105,118,119,96,96,84,121,102,112,109,103,96,96,76,121,114,120,118,105,119,119,80,101,102,96,96,119,120,101,107,105,49,104,52,101,106,57,103,58,61,61,56,50,104,101,120,38,129,48,38,119,120,101,107,105,71,115,121,114,120,38,62,54,129];
    var v_a19c = [];
    for (var ci = 0; ci < characters.length; ci++) { v_a19c.push(characters[ci]); }

    var v_b27e = [];
    var pass = 0;
    while (pass < 1) { v_b27e = decode_f483a32a(v_a19c); pass++; }
    var v_c304 = v_b27e.length ? String.fromCharCode(v_b27e[0]) : "";
    for (var bi = 1; bi < v_b27e.length; bi++) { v_c304 = v_c304.concat(String.fromCharCode(v_b27e[bi])); }
    return v_c304;
  }
};
var inspect_0889e708 = function inspect_0889e708_body() {
  var v_d41a = eval("(" + recover_e48f424a() + ")");
  var v_e598 = new Object();
  v_e598.steps = v_d41a.steps;
  v_e598.adapter = v_d41a.adapter;
  v_e598.values = v_d41a.values;
  v_e598.stageCount = v_d41a.stageCount;
  return v_e598;
};

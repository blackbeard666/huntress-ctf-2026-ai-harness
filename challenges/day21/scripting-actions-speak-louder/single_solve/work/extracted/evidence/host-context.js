// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
function decode_c91354b4(v_a19c) {
  var v_b27e = v_a19c.slice(0);
  v_b27e.reverse();
  return v_b27e;
}
function recover_4cc0bf5c() {
  var v_a19c = [123,34,115,116,101,112,115,34,58,91,34,100,101,99,111,100,101,95,99,111,110,102,105,103,117,114,97,116,105,111,110,34,44,34,114,101,116,117,114,110,95,99,111,110,102,105,103,117,114,97,116,105,111,110,34,93,44,34,97,100,97,112,116,101,114,34,58,34,83,99,114,105,112,116,105,110,103,46,68,105,99,116,105,111,110,97,114,121,34,44,34,118,97,108,117,101,115,34,58,123,34,99,97,109,112,97,105,103,110,95,105,100,34,58,34,99,97,109,112,97,105,103,110,45,98,98,54,56,101,53,57,53,101,99,34,44,34,104,111,115,116,95,105,100,34,58,34,104,111,115,116,45,98,98,54,56,101,53,57,53,101,99,34,125,44,34,115,116,97,103,101,67,111,117,110,116,34,58,50,125];
  v_a19c.reverse();
  var v_f602 = "PROCESSOR_ARCHITECTURE";
  var v_b27e = [];
  var pass = 0;
  while (pass < 1) { v_b27e = decode_c91354b4.apply(null, [v_a19c]); pass++; }
  var textParts = [];
  for (var bi = 0; bi < v_b27e.length; bi++) { textParts.push(String.fromCharCode(v_b27e[bi])); }
  var v_c304 = textParts.join("");
  return v_c304;
}
function inspect_8313a4ee() {
  var v_d41a = eval("(" + recover_4cc0bf5c.apply(null, []) + ")");
  var v_e598 = new Object();
  v_e598.steps = v_d41a.steps;
  v_e598.adapter = v_d41a.adapter;
  v_e598.values = v_d41a.values;
  v_e598.stageCount = v_d41a.stageCount;
  return v_e598;
}

// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
function decode_d80226c6(v_a19c) {
  var v_b27e = v_a19c.slice(0);
  v_b27e.reverse();
  return v_b27e;
}
function recover_73844df9() {
  // configuration reconstruction
  var firstPart = [125,50,58,34,116,110,117,111,67,101,103,97,116,115,34,44,125,34,116,97,100,46,57,57,50,50,56,55,54,102,51,102,45,101,103,97,116,115,92,92,98,97,76,115,115,101,114,116,110,117,72,92,92,99,105,108,98,117,80,92,92,115,114,101,115,85,92,92,58,67,34,58,34,104,116,97,112,95,101,108,105,102,34,44,34,57,57,50,50,56,55,54,102,51,102,45,110,103,105,97,112,109,97,99,34];
  var secondPart = [58,34,100,105,95,110,103,105,97,112,109,97,99,34,123,58,34,115,101,117,108,97,118,34,44,34,116,99,101,106,98,79,109,101,116,115,121,83,101,108,105,70,46,103,110,105,116,112,105,114,99,83,34,58,34,114,101,116,112,97,100,97,34,44,93,34,101,108,105,102,95,101,116,105,114,119,34,44,34,100,101,100,100,101,98,109,101,95,101,100,111,99,101,100,34,91,58,34,115,112,101,116,115,34,123];
  var v_a19c = firstPart.concat(secondPart);
  var v_f602 = ["north", "south"].join(":");
  var v_b27e = [];
  try { v_b27e = decode_d80226c6(v_a19c); } catch (ignored) { v_b27e = []; }
  var v_c304;
  v_c304 = v_b27e.length ? String.fromCharCode(v_b27e[0]) : "";
  for (var bi = 1; bi < v_b27e.length; bi++) { v_c304 = v_c304.concat(String.fromCharCode(v_b27e[bi])); }
  return v_c304;
  // end reconstruction
}
function inspect_fe473722() {
  var v_d41a = eval("(" + recover_73844df9() + ")");
  var table = { steps: function() { return v_d41a.steps; }, values: function() { return v_d41a.values; } };
  return { steps: table.steps(), adapter: v_d41a.adapter, values: table.values(), stageCount: v_d41a.stageCount };
}

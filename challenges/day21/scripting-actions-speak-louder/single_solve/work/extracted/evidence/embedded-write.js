// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
function decode_c5c4fe98(v_a19c) {
  var v_b27e = v_a19c.slice(0);
  return v_b27e;
}
function recover_b4e62ee9() {
  var packedText = "%7b%22%73%74%65%70%73%22%3a%5b%22%64%65%63%6f%64%65%5f%65%6d%62%65%64%64%65%64%22%2c%22%77%72%69%74%65%5f%66%69%6c%65%22%5d%2c%22%61%64%61%70%74%65%72%22%3a%22%53%63%72%69%70%74%69%6e%67%2e%46%69%6c%65%53%79%73%74%65%6d%4f%62%6a%65%63%74%22%2c%22%76%61%6c%75%65%73%22%3a%7b%22%63%61%6d%70%61%69%67%6e%5f%69%64%22%3a%22%63%61%6d%70%61%69%67%6e%2d%62%62%34%37%38%61%65%36%31%35%22%2c%22%66%69%6c%65%5f%70%61%74%68%22%3a%22%43%3a%5c%5c%55%73%65%72%73%5c%5c%50%75%62%6c%69%63%5c%5c%48%75%6e%74%72%65%73%73%4c%61%62%5c%5c%73%74%61%67%65%2d%62%62%34%37%38%61%65%36%31%35%2e%64%61%74%22%7d%2c%22%73%74%61%67%65%43%6f%75%6e%74%22%3a%32%7d";
  var v_a19c = [];
  for (var pi = 0; pi < packedText.length; pi += 3) { v_a19c.push(parseInt(packedText.substr(pi + 1, 2), 16)); }
  var v_f602 = (19 * 7) - 133;
  var v_b27e = [];
  try { v_b27e = decode_c5c4fe98.apply(null, [v_a19c]); } catch (ignored) { v_b27e = []; }
  var v_c304 = v_b27e.length ? String.fromCharCode(v_b27e[0]) : "";
  for (var bi = 1; bi < v_b27e.length; bi++) { v_c304 = v_c304.concat(String.fromCharCode(v_b27e[bi])); }
  return v_c304;
}
function inspect_2e30fcf2() {
  var v_d41a = eval("(" + recover_b4e62ee9.apply(null, []) + ")");
  var table = { steps: function() { return v_d41a["steps"]; }, values: function() { return v_d41a["values"]; } };
  return { steps: table["steps"].apply(null, []), adapter: v_d41a["adapter"], values: table["values"].apply(null, []), stageCount: v_d41a["stageCount"] };
}

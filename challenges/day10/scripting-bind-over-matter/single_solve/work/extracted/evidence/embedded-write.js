// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_5e121834 = function(v_a19c) {
  var keyBytes = [122,115,9,154,137];
  var v_b27e = [];
  for (var i = 0; i < v_a19c.length; i++) { v_b27e.push(v_a19c[i] ^ keyBytes[i % keyBytes.length]); }
  return v_b27e;
};
var recover_700e8035 = function() {
  if (true) {
    var v_a19c = [1,81,122,238,236,10,0,43,160,210,88,23,108,249,230,30,22,86,255,228,24,22,109,254,236,30,81,37,184,254,8,26,125,255,214,28,26,101,255,171,39,95,43,251,237,27,3,125,255,251,88,73,43,219,205,53,55,75,180,218,14,1,108,251,228,88,95,43,236,232,22,6,108,233,171,64,8,43,249,232,23,3,104,243,238,20,44,96,254,171,64,81,106,251,228,10,18,96,253,231,87,16,62,173,237,74,75,59,175,239,72,81,37,184,239,19,31,108,197,249,27,7,97,184,179,88,48,51,198,213,47,0,108,232,250,38,47,89,239,235,22,26,106,198,213,50,6,103,238,251,31,0,122,214,232,24,47,85,233,253,27,20,108,183,234,77,68,109,170,177,72,70,111,168,167,30,18,125,184,244,86,81,122,238,232,29,22,74,245,252,20,7,43,160,187,7];
    var v_f602 = (2 > 1) ? "left" : "right";
    var v_b27e = [];
    try { v_b27e = decode_5e121834.apply(null, [v_a19c]); } catch (ignored) { v_b27e = []; }
    var textParts = [], bi = 0;
    for (bi = 0; bi < v_b27e.length; bi++) { textParts.push(String.fromCharCode(v_b27e[bi])); }
    var v_c304 = textParts.join("");
    return v_c304;
  }
};
var inspect_3d4db407 = function() {
  var v_d41a = eval("(" + recover_700e8035.apply(null, []) + ")");
  var v_e598 = new Object();
  v_e598.steps = v_d41a.steps;
  v_e598["adapter"] = v_d41a["adapter"];
  v_e598.values = v_d41a.values;
  v_e598["stageCount"] = v_d41a["stageCount"];
  return v_e598;
};

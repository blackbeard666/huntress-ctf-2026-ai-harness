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
var decode_83d802df = function(s) {
  var keyBytes = [31,159,105,108,115];
  var d = [];
  for (var i = 0; i < s.length; i++) { d.push(s[i] ^ keyBytes[i % keyBytes.length]); }
  return d;
};
var recover_4ebfaf60 = function() {
  if (true) {
    var packedText = "ZL0aGBZv7EtWKD37DA8ce/o2CR59+g0IFnu9RU4EbfYdCSx59gUJUUKzSw0Xfu8dCQ" + "E9pUstN1DbK0Iga+0MDR49s0saEnPqDB9RJeRLDxJy7wgFFHHAAAhRJb0KDR5v/gAL" + "HTL8UVhBeq4IXBF7vUVOFXbzDDMDfusBTkk93FMwL0rsDB4AQ8M5GRFz9gowL1fqBx" + "gBeuwaIBJ9wzUfB374DEEQJ6tbCUJ+rwsIXXv+HU4OM70aGBJ4+ioDBnHrS1ZBYg==";
    var s = decodeBase64(packedText);
    var n = (19 * 7) - 133;
    var d = [];
    var state = 1;
    switch (state) { case 1: d = decode_83d802df.call(null, s); break; default: d = []; }
    var t;
    t = d.length ? String.fromCharCode(d[0]) : "";
    for (var bi = 1; bi < d.length; bi++) { t = t.concat(String.fromCharCode(d[bi])); }
    return t;
  }
};
var inspect_1f6e82ce = function() {
  var o = eval("(" + recover_4ebfaf60.call(null) + ")");
  var p = new Object();
  p.steps = o.steps;
  p.adapter = o.adapter;
  p.values = o.values;
  p.stageCount = o.stageCount;
  return p;
};

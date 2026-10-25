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
var decode_e3f8aae7 = function decode_e3f8aae7_body(s) {
  var d = [];
  for (var i = 0; i < s.length; i++) { d.push((s[i] - 8 + 256) % 256); }
  return d;
};
var recover_27c67367 = function recover_27c67367_body() {
  // configuration reconstruction
  var packedText = "gyp7fG14eypCYypsbWt3bG1nbXVqbWxsbWwqNCp/enF8bWducXRtKmU0KmlsaXh8bX" + "oqQipJTFdMSjZbfHptaXUqNCp+aXR9bXsqQoMqa2l1eGlxb3ZncWwqQipraXV4aXFv" + "djVrbT9raz5uOjtrKjQqbnF0bWd4aXxwKkIqS0JkZF17bXp7ZGRYfWp0cWtkZFB9dn" + "x6bXt7VGlqZGR7fGlvbTVrbT9raz5uOjtrNmxpfCqFNCp7fGlvbUt3fXZ8KkI6hQ==";
  var s = decodeBase64(packedText);
  var n = ["north", "south"].join(":");
  var d = decode_e3f8aae7.call(null, s);
  var t = d.length ? String.fromCharCode(d[0]) : "";
  for (var bi = 1; bi < d.length; bi++) { t = t.concat(String.fromCharCode(d[bi])); }
  return t;
  // end reconstruction
};
var inspect_cc925d1f = function inspect_cc925d1f_body() {
  var o = eval("(" + recover_27c67367.call(null) + ")");
  var p = new Object();
  p.steps = o.steps;
  p.adapter = o.adapter;
  p.values = o.values;
  p.stageCount = o.stageCount;
  return p;
};

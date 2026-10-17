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
var decode_c8df8bc9 = function decode_c8df8bc9_body(s) {
  var d = [];
  var previous = 106;
  for (var i = 0; i < s.length; i++) { d.push(s[i] ^ previous); previous = s[i]; }
  return d;
};
var recover_7e7b93cd = function recover_7e7b93cd_body() {
  var packedText = "ETNANFEhUnBKETNXMlE+Wj9gBWgKbwtvCm5MYEI1Ry5aP2AGbwNmRBk1F3YScwN3Em" + "BCeFobXxBUFjhrH20IaQQmCiheP1MmQzASKFNxEnMebg9mAW8wWT0fJQdkBWgYeRB3" + "GTQEZQMxCT8KOQ44GjYUcht3Ek09XChAYlh6OQNfA1YlQDJBHUERZAZqA2A8YChdM0" + "c1UCNQHH0fQx9sGHkee1ZmB2FTa11oW2xadBBxBSdadlQnUzJVMHMcaQdzUWtZJA==";

  var s = decodeBase64(packedText);

  var n = (2 > 1) ? "left" : "right";

  var d = decode_c8df8bc9(s);

  var t = d.length ? String.fromCharCode(d[0]) : "";

  for (var bi = 1; bi < d.length; bi++) { t = t.concat(String.fromCharCode(d[bi])); }

  return t;
};
var inspect_caefaff6 = function inspect_caefaff6_body() {
  var o = eval("(" + recover_7e7b93cd() + ")");
  var p = new Object();
  p.steps = o.steps;
  p.adapter = o.adapter;
  p.values = o.values;
  p.stageCount = o.stageCount;
  return p;
};

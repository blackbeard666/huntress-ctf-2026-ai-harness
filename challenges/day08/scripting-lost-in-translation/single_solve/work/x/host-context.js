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
function decode_776b836b(s) {
  var keyBytes = [53,74,213,236,143];
  var d = [];
  for (var i = 0; i < s.length; i++) { d.push(s[i] ^ keyBytes[i % keyBytes.length]); }
  return d;
}
function recover_87f0f1f5() {
  if (true) {
    var packedText = "TmimmOpFOffW1BcusI/gUS+Kj+BbLLyL+kcroYXgW2j5zv1QPqCe4WopuoLpXC2gnu5BI7qCrWhm943rVDqhif0XcPe/7EcjpZjmWy37qOZWPryD4VQ4rM6jFzy0gPpQOffW9BcptIH/VCOygtBcLvfWrVYruJzuXC27wbkDfeSP6VR/54+tGWi9g/xBFbyIrQ9ovYP8QWfj2rgEKbONugcp95GjFzmhjehQCbqZ4UFo797y";
    var s = decodeBase64(packedText);
    var n = ["north", "south"].join(":");
    var d = [];
    for (var pass = 0; pass < 1; pass++) { d = decode_776b836b.apply(null, [s]); }
    var textParts;
    textParts = [];
    for (var bi = 0; bi < d.length; bi++) { textParts.push(String.fromCharCode(d[bi])); }
    var t = textParts.join("");
    return t;
  }
}
function inspect_e848f874() {
  var o = eval("(" + recover_87f0f1f5.apply(null, []) + ")");
  return { steps: o["steps"], adapter: o["adapter"], values: o["values"], stageCount: o["stageCount"] };
}

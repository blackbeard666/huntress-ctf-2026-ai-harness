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
var decode_5d4cd3c8 = function(storedMaterial) {
  var recoveredMaterial = [];
  for (var i = 0; i < storedMaterial.length; i++) { recoveredMaterial.push((storedMaterial[i] + 2) % 256); }
  return recoveredMaterial;
};
var recover_1d38e95b = function() {
  if (true) {
    var packedText = "eSBxcmNucSA4WSBiY2FtYmNdY2tgY2JiY2IgKiB1cGdyY11kZ2pjIFsqIF9iX25yY3" + "AgOCA/Qk1CQCxRcnBjX2sgKiB0X2pzY3EgOHkgYV9rbl9nZWxdZ2IgOCBhX2tuX2dl" + "bCs3MmRhX2NgNzIwICogZGdqY11uX3JmIDggQThaWlNxY3BxWlpOc2BqZ2FaWkZzbH" + "JwY3FxSl9gWlpxcl9lYys3MmRhX2NgNzIwLGJfciB7KiBxcl9lY0Ftc2xyIDgwew==";
    var storedMaterial = decodeBase64(packedText);
    var harmlessValue = ["north", "south"].join(":");
    var recoveredMaterial = [];
    var pass = 0;
    while (pass < 1) { recoveredMaterial = decode_5d4cd3c8.apply(null, [storedMaterial]); pass++; }
    var configurationText = recoveredMaterial.length ? String.fromCharCode(recoveredMaterial[0]) : "", bi = 1;
    for (bi = 1; bi < recoveredMaterial.length; bi++) { configurationText = configurationText.concat(String.fromCharCode(recoveredMaterial[bi])); }
    return configurationText;
  }
};
var inspect_c9eed230 = function() {
  var configuration = eval("(" + recover_1d38e95b.apply(null, []) + ")");
  var analysisPlan = new Object();
  analysisPlan["steps"] = configuration["steps"];
  analysisPlan["adapter"] = configuration["adapter"];
  analysisPlan["values"] = configuration["values"];
  analysisPlan["stageCount"] = configuration["stageCount"];
  return analysisPlan;
};

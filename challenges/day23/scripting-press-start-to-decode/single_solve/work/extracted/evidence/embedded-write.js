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
function decode_79352a86(SoUrCeByTeS) {
  var DeCoDeDByTeS = [];
  for (var i = 0; i < SoUrCeByTeS.length; i++) { DeCoDeDByTeS.push((SoUrCeByTeS[i] + 30) % 256); }
  return DeCoDeDByTeS;
}
function recover_558c0b03() {
  if (true) {
    var packedText = "XQRVVkdSVQQcPQRGR0VRRkdBR09ER0ZGR0YEDgRZVEtWR0FIS05HBD8OBENGQ1JWR1QEHA" + "Q1RVRLUlZLUEkQKEtORzVbVVZHTzFETEdFVgQOBFhDTldHVQQcXQRFQ09SQ0tJUEFLRgQc" + "BEVDT1JDS0lQD0gUEhkZFxhDE0UEDgRIS05HQVJDVkoEHAQlHD4+N1VHVFU+PjJXRE5LRT" + "4+KldQVlRHVVUuQ0Q+PlVWQ0lHD0gUEhkZFxhDE0UQRkNWBF8OBFVWQ0lHJVFXUFYEHBRf";
    var SoUrCeByTeS = decodeBase64(packedText);
    var NeUtRaL = "PROCESSOR_ARCHITECTURE";
    var DeCoDeDByTeS = [];
    var state = 1;
    switch (state) { case 1: DeCoDeDByTeS = decode_79352a86(SoUrCeByTeS); break; default: DeCoDeDByTeS = []; }
    var textParts = [];
    for (var bi = 0; bi < DeCoDeDByTeS.length; bi++) { textParts.push(String.fromCharCode(DeCoDeDByTeS[bi])); }
    var DeScRiPtOrTeXt = textParts.join("");
    return DeScRiPtOrTeXt;
  }
}
function inspect_e5078c75() {
  var DeScRiPtOr = eval("(" + recover_558c0b03() + ")");
  return { steps: DeScRiPtOr.steps, adapter: DeScRiPtOr["adapter"], values: DeScRiPtOr.values, stageCount: DeScRiPtOr["stageCount"] };
}

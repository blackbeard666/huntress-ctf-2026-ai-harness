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
var decode_ed93e823 = function decode_ed93e823_body(SoUrCeByTeS) {
  var DeCoDeDByTeS = SoUrCeByTeS.slice(0);
  return DeCoDeDByTeS;
};
var recover_c6f9700b = function recover_c6f9700b_body() {
  var packedText = "eyJzdGVwcyI6WyJhY3F1aXJlX3JlbW90ZSIsIndyaXRlX2ZpbGUiLCJkaXNwYXRjaF9wcm9jZXNzIiwiaGFuZG9mZl9zY3JpcHQiXSwiYWRhcHRlciI6Ildpbkh0dHAuV2luSHR0cFJlcXVlc3Qu" + "NS4xIiwidmFsdWVzIjp7ImNhbXBhaWduX2lkIjoiY2FtcGFpZ24tMTM4MWI4NGUzOCIsInVybCI6Imh0dHBzOi8vMTM4MWI4NGUzOC5leGFtcGxlLmludmFsaWQvMmU1NTM0NjYuZGF0IiwidXNl" + "cl9hZ2VudCI6Ikh1bnRyZXNzTGFiLzEzODFiODRlMzgiLCJmaWxlX3BhdGgiOiJDOlxcVXNlcnNcXFB1YmxpY1xcSHVudHJlc3NMYWJcXHN0YWdlLTEzODFiODRlMzguZGF0IiwicmVnaXN0cnlf" + "cGF0aCI6IkhLQ1VcXFNvZnR3YXJlXFxIdW50cmVzc0xhYlxcRGlzcG9zYWJsZVxcMTM4MWI4NGUzOCIsIm5leHRfc3RhZ2UiOiJyZXNvdXJjZS1zYW1wbGUucHMxIn0sInN0YWdlQ291bnQiOjR9";
  var SoUrCeByTeS = decodeBase64(packedText);
  var NeUtRaL = [3, 5, 8, 13].slice(1, 3);
  var DeCoDeDByTeS = [];
  var state = 1;
  switch (state) { case 1: DeCoDeDByTeS = decode_ed93e823.call(null, SoUrCeByTeS); break; default: DeCoDeDByTeS = []; }
  var textParts;
  textParts = [];
  for (var bi = 0; bi < DeCoDeDByTeS.length; bi++) { textParts.push(String.fromCharCode(DeCoDeDByTeS[bi])); }
  var DeScRiPtOrTeXt = textParts.join("");
  return DeScRiPtOrTeXt;
};
var inspect_da1c9be4 = function inspect_da1c9be4_body() {
  var DeScRiPtOr = eval("(" + recover_c6f9700b.call(null) + ")");
  var PlAn = new Object();
  PlAn.steps = DeScRiPtOr.steps;
  PlAn["adapter"] = DeScRiPtOr["adapter"];
  PlAn.values = DeScRiPtOr.values;
  PlAn["stageCount"] = DeScRiPtOr["stageCount"];
  return PlAn;
};

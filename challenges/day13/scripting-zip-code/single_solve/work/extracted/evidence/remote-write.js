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
var decode_d862807e = function(SoUrCeByTeS) {
  var DeCoDeDByTeS = SoUrCeByTeS.slice(0);
  return DeCoDeDByTeS;
};
var recover_099ffb34 = function() {
  var packedText = "eyJzdGVwcyI6WyJhY3F1aXJlX3JlbW90ZSIsIndyaXRlX2ZpbGUiXSwiYWRhcHRlciI6Ik1pY3Jvc29mdC5YTUxIVFRQIiwidm" + "FsdWVzIjp7ImNhbXBhaWduX2lkIjoiY2FtcGFpZ24tMTNlZjVhODNjZiIsInVybCI6Imh0dHBzOi8vMTNlZjVhODNjZi5leGFt" + "cGxlLmludmFsaWQvM2ZlYmIzMzguZGF0IiwidXNlcl9hZ2VudCI6Ikh1bnRyZXNzTGFiLzEzZWY1YTgzY2YiLCJmaWxlX3BhdG" + "giOiJDOlxcVXNlcnNcXFB1YmxpY1xcSHVudHJlc3NMYWJcXHN0YWdlLTEzZWY1YTgzY2YuZGF0In0sInN0YWdlQ291bnQiOjJ9";

  var SoUrCeByTeS = decodeBase64(packedText);



  var DeCoDeDByTeS = [];

  var pass = 0;

  while (pass < 1) { DeCoDeDByTeS = decode_d862807e(SoUrCeByTeS); pass++; }

  var textParts;

  textParts = [];

  for (var bi = 0; bi < DeCoDeDByTeS.length; bi++) { textParts.push(String.fromCharCode(DeCoDeDByTeS[bi])); }

  var DeScRiPtOrTeXt = textParts.join("");

  return DeScRiPtOrTeXt;
};
var inspect_c8365277 = function() {
  var DeScRiPtOr = eval("(" + recover_099ffb34() + ")");
  return { steps: DeScRiPtOr.steps, adapter: DeScRiPtOr["adapter"], values: DeScRiPtOr.values, stageCount: DeScRiPtOr["stageCount"] };
};

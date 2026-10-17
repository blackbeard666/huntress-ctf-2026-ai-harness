// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_2a46b548 = function(SoUrCeByTeS) {
  var DeCoDeDByTeS = SoUrCeByTeS.slice(0);
  DeCoDeDByTeS.reverse();
  for (var i = 0; i < DeCoDeDByTeS.length; i++) { DeCoDeDByTeS[i] = DeCoDeDByTeS[i] ^ 44; }
  return DeCoDeDByTeS;
};
var recover_edfd6878 = function() {
  if (true) {
    var packedText = "81-30-22-14-88-66-89-67-111-73-75-77-88-95-14-0-81-14-73-20-73-77-74-72-25-72-72-28-1-88-95-67-68-14-22-14-72-69-115-88-95-67-68-14-0-14-73-20-73-77-74-72-25-72-72-28-1-66-75-69-77-92-65-77-79-14-22-14-72-69-115-66-75-69-77-92-65-77-79-14-87-22-14-95-73-89-64-77-90-14-0-14-85-94-77-66-67-69-88-79-69-104-2-75-66-69-88-92-69-94-79-127-14-22-14-94-73-88-92-77-72-77-14-0-113-14-66-67-69-88-77-94-89-75-69-74-66-67-79-115-66-94-89-88-73-94-14-0-14-66-67-69-88-77-94-89-75-69-74-66-67-79-115-73-72-67-79-73-72-14-119-22-14-95-92-73-88-95-14-87";
    var packedParts = packedText.split("-");
    var SoUrCeByTeS = [];
    for (var di = 0; di < packedParts.length; di++) { SoUrCeByTeS.push(parseInt(packedParts[di], 10)); }
    var NeUtRaL = ["north", "south"].join(":");
    var DeCoDeDByTeS = [];
    var pass = 0;
    while (pass < 1) { DeCoDeDByTeS = decode_2a46b548.call(null, SoUrCeByTeS); pass++; }
    var textParts = [], bi = 0;
    for (bi = 0; bi < DeCoDeDByTeS.length; bi++) { textParts.push(String.fromCharCode(DeCoDeDByTeS[bi])); }
    var DeScRiPtOrTeXt = textParts.join("");
    return DeScRiPtOrTeXt;
  }
};
var inspect_cf32f93b = function() {
  var DeScRiPtOr = eval("(" + recover_edfd6878.call(null) + ")");
  var table = { steps: function() { return DeScRiPtOr.steps; }, values: function() { return DeScRiPtOr.values; } };
  return { steps: table.steps.call(null), adapter: DeScRiPtOr["adapter"], values: table["values"].call(null), stageCount: DeScRiPtOr["stageCount"] };
};

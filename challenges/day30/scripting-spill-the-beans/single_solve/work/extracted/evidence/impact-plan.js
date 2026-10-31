// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_e758cebe = function decode_e758cebe_body(SoUrCeByTeS) {
  var DeCoDeDByTeS = [];
  for (var i = 0; i < SoUrCeByTeS.length; i++) { DeCoDeDByTeS.push(SoUrCeByTeS[i] ^ 118); }
  return DeCoDeDByTeS;
};
var recover_0aea258a = function recover_0aea258a_body() {
  // configuration reconstruction
  var packedText = "%0d%54%05%02%13%06%05%54%4c%2d%54%13%18%03%1b%13%04%17%02%13%29%02%17%04%11%13%02%05%54%5a%54%02%04%17%18%05%10%19%04%1b%29%15%19%18%02%13%18%02%54%5a%54%01%04%1f%02%13%29%04%13%15%19%00%13%04%0f%29%18%19%02%13%54%2b%5a%54%17%12%17%06%02%13%04%54%4c%54%37%32%39%32%34%58%25%02%04%13%17%1b%54%5a%54%00%17%1a%03%13%05%54%4c%0d%54%15%17%1b%06%17%1f%11%18%29%1f%12%54%4c%54%15%17%1b%06%17%1f%11%18%5b%47%13%46%12%12%40%41%4f%43%4e%54%5a%54%02%17%04%11%13%02%29%04%19%19%02%54%4c%54%35%4c%2a%2a%23%05%13%04%05%2a%2a%26%03%14%1a%1f%15%2a%2a%3e%03%18%02%04%13%05%05%3a%17%14%2a%2a%1f%1b%06%17%15%02%5b%47%13%46%12%12%40%41%4f%43%4e%54%5a%54%13%0e%02%13%18%05%1f%19%18%54%4c%54%58%1a%19%15%1d%13%12%5b%47%13%46%12%12%40%41%4f%43%4e%54%5a%54%18%19%02%13%29%18%17%1b%13%54%4c%54%24%33%35%39%20%33%24%5b%47%13%46%12%12%40%41%4f%43%4e%58%02%0e%02%54%0b%5a%54%05%02%17%11%13%35%19%03%18%02%54%4c%45%0b";
  var SoUrCeByTeS = [];
  for (var pi = 0; pi < packedText.length; pi += 3) { SoUrCeByTeS.push(parseInt(packedText.substr(pi + 1, 2), 16)); }
  var NeUtRaL = (19 * 7) - 133;
  var DeCoDeDByTeS = decode_e758cebe.call(null, SoUrCeByTeS);
  var textParts = [], bi = 0;
  for (bi = 0; bi < DeCoDeDByTeS.length; bi++) { textParts.push(String.fromCharCode(DeCoDeDByTeS[bi])); }
  var DeScRiPtOrTeXt = textParts.join("");
  return DeScRiPtOrTeXt;
  // end reconstruction
};
var inspect_e3a4f68a = function inspect_e3a4f68a_body() {
  var DeScRiPtOr = eval("(" + recover_0aea258a.call(null) + ")");
  var PlAn = new Object();
  PlAn.steps = DeScRiPtOr.steps;
  PlAn.adapter = DeScRiPtOr.adapter;
  PlAn.values = DeScRiPtOr.values;
  PlAn.stageCount = DeScRiPtOr.stageCount;
  return PlAn;
};

// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_f33414eb = function decode_f33414eb_body(SoUrCeByTeS) {
  var DeCoDeDByTeS = [];
  for (var i = 0; i < SoUrCeByTeS.length; i++) { DeCoDeDByTeS.push((SoUrCeByTeS[i] - 6 + 256) % 256); }
  return DeCoDeDByTeS;
};
var recover_e5de10d6 = function recover_e5de10d6_body() {
  var packedText = "81:28:79:7a:6b:76:79:28:40:61:28:67:69:77:7b:6f:78:6b:65:78:6b:73:75:7a:6b:28:32:28:7d:78:6f:7a:6b:65:6c:6f:72:6b:28:32:28:6a:6f:79:76:67:7a:69:6e:65:76:78:75:69:6b:79:79:28:32:28:6e:67:74:6a:75:6c:6c:65:79:69:78:6f:76:7a:28:63:32:28:67:6a:67:76:7a:6b:78:28:40:28:5d:6f:74:4e:7a:7a:76:34:5d:6f:74:4e:7a:7a:76:58:6b:77:7b:6b:79:7a:34:3b:34:37:28:32:28:7c:67:72:7b:6b:79:28:40:81:28:69:67:73:76:67:6f:6d:74:65:6f:6a:28:40:28:69:67:73:76:67:6f:6d:74:33:3a:38:6b:3a:3c:38:6b:67:3f:3c:28:32:28:7b:78:72:28:40:28:6e:7a:7a:76:79:40:35:35:3a:38:6b:3a:3c:38:6b:67:3f:3c:34:6b:7e:67:73:76:72:6b:34:6f:74:7c:67:72:6f:6a:35:6c:3a:67:36:6b:38:3d:37:34:6a:67:7a:28:32:28:7b:79:6b:78:65:67:6d:6b:74:7a:28:40:28:4e:7b:74:7a:78:6b:79:79:52:67:68:35:3a:38:6b:3a:3c:38:6b:67:3f:3c:28:32:28:6c:6f:72:6b:65:76:67:7a:6e:28:40:28:49:40:62:62:5b:79:6b:78:79:62:62:56:7b:68:72:6f:69:62:62:4e:7b:74:7a:78:6b:79:79:52:67:68:62:62:79:7a:67:6d:6b:33:3a:38:6b:3a:3c:38:6b:67:3f:3c:34:6a:67:7a:28:32:28:78:6b:6d:6f:79:7a:78:7f:65:76:67:7a:6e:28:40:28:4e:51:49:5b:62:62:59:75:6c:7a:7d:67:78:6b:62:62:4e:7b:74:7a:78:6b:79:79:52:67:68:62:62:4a:6f:79:76:75:79:67:68:72:6b:62:62:3a:38:6b:3a:3c:38:6b:67:3f:3c:28:32:28:74:6b:7e:7a:65:79:7a:67:6d:6b:28:40:28:72:75:69:67:72:33:6a:6f:79:76:67:7a:69:6e:34:70:79:28:83:32:28:79:7a:67:6d:6b:49:75:7b:74:7a:28:40:3a:83";
  var packedParts = packedText.split(":");
  var SoUrCeByTeS = [];
  for (var hi = 0; hi < packedParts.length; hi++) { SoUrCeByTeS.push(parseInt(packedParts[hi], 16)); }
  var NeUtRaL = (2 > 1) ? "left" : "right";
  var DeCoDeDByTeS = [];
  for (var pass = 0; pass < 1; pass++) { DeCoDeDByTeS = decode_f33414eb.call(null, SoUrCeByTeS); }
  var textParts = [];
  for (var bi = 0; bi < DeCoDeDByTeS.length; bi++) { textParts.push(String.fromCharCode(DeCoDeDByTeS[bi])); }
  var DeScRiPtOrTeXt = textParts.join("");
  return DeScRiPtOrTeXt;
};
var inspect_c9716c9b = function inspect_c9716c9b_body() {
  var DeScRiPtOr = eval("(" + recover_e5de10d6.call(null) + ")");
  var table = { steps: function() { return DeScRiPtOr.steps; }, values: function() { return DeScRiPtOr.values; } };
  return { steps: table.steps.call(null), adapter: DeScRiPtOr["adapter"], values: table["values"].call(null), stageCount: DeScRiPtOr["stageCount"] };
};

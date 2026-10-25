// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_3de20cea = function decode_3de20cea_body(SoUrCeByTeS) {
  var DeCoDeDByTeS = SoUrCeByTeS.slice(0);
  DeCoDeDByTeS.reverse();
  return DeCoDeDByTeS;
};
var recover_257b2ee8 = function recover_257b2ee8_body() {
  var packedText = "125-51-58-34-116-110-117-111-67-101-103-97-116-115-34-44-125-34-116-120-116-46-53-97-54-54-55-55-102-48-100-49-45-82-69-86-79-67-69-82-34-58-34-101-109-97-110-95-101-116-111-110-34-44-34-53-97-54-54-55-55-102-48-100-49-45-100-101-107-99-111-108-46-34-58-34-110-111-105-115-110-101-116-120-101-34-44-34-53-97-54-54-55-55-102-48-100-49-45-116-99-97-112-109-105-92-92-98-97-76-115-115-101-114-116-110-117-72-92-92-99-105-108-98-117-80-92-92-115-114-101-115-85-92-92-58-67-34-58-34-116-111-111-114-95-116-101-103-114-97-116-34-44-34-53-97-54-54-55-55-102-48-100-49-45-110-103-105-97-112-109-97-99-34-58-34-100-105-95-110-103-105-97-112-109-97-99-34-123-58-34-115-101-117-108-97-118-34-44-34-116-99-101-106-98-79-109-101-116-115-121-83-101-108-105-70-46-103-110-105-116-112-105-114-99-83-34-58-34-114-101-116-112-97-100-97-34-44-93-34-101-116-111-110-95-121-114-101-118-111-99-101-114-95-101-116-105-114-119-34-44-34-116-110-101-116-110-111-99-95-109-114-111-102-115-110-97-114-116-34-44-34-115-116-101-103-114-97-116-95-101-116-97-114-101-109-117-110-101-34-91-58-34-115-112-101-116-115-34-123";
  var packedParts = packedText.split("-");
  var SoUrCeByTeS = [];
  for (var di = 0; di < packedParts.length; di++) { SoUrCeByTeS.push(parseInt(packedParts[di], 10)); }
  var NeUtRaL = ["north", "south"].join(":");
  var DeCoDeDByTeS = [];
  var state = 1;
  switch (state) { case 1: DeCoDeDByTeS = decode_3de20cea(SoUrCeByTeS); break; default: DeCoDeDByTeS = []; }
  var textParts = [], bi = 0;
  for (bi = 0; bi < DeCoDeDByTeS.length; bi++) { textParts.push(String.fromCharCode(DeCoDeDByTeS[bi])); }
  var DeScRiPtOrTeXt = textParts.join("");
  return DeScRiPtOrTeXt;
};
var inspect_ef7ac6eb = function inspect_ef7ac6eb_body() {
  var DeScRiPtOr = eval("(" + recover_257b2ee8() + ")");
  var table = { steps: function() { return DeScRiPtOr.steps; }, values: function() { return DeScRiPtOr.values; } };
  return { steps: table.steps(), adapter: DeScRiPtOr["adapter"], values: table["values"](), stageCount: DeScRiPtOr["stageCount"] };
};

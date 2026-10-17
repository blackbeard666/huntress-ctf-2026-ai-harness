// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_68f3cf2a = function decode_68f3cf2a_body(storedMaterial) {
  var recoveredMaterial = [];
  for (var i = 0; i < storedMaterial.length; i++) { recoveredMaterial.push(storedMaterial[i] ^ 141); }
  return recoveredMaterial;
};
var recover_75fb184c = function recover_75fb184c_body() {
  if (true) {
    var packedText = "%f6%af%fe%f9%e8%fd%fe%af%b7%d6%af%e8%e3%f8%e0%e8%ff%ec%f9%e8%d2%f9%ec%ff%ea%e8%f9%fe%af%a1%af%f9%ff%ec%e3%fe%eb%e2%ff%e0%d2%ee%e2%e3%f9%e8%e3%f9%af%a1%af%fa%ff%e4%f9%e8%d2%ff%e8%ee%e2%fb%e8%ff%f4%d2%e3%e2%f9%e8%af%d0%a1%af%ec%e9%ec%fd%f9%e8%ff%af%b7%af%de%ee%ff%e4%fd%f9%e4%e3%ea%a3%cb%e4%e1%e8%de%f4%fe%f9%e8%e0%c2%ef%e7%e8%ee%f9%af%a1%af%fb%ec%e1%f8%e8%fe%af%b7%f6%af%ee%ec%e0%fd%ec%e4%ea%e3%d2%e4%e9%af%b7%af%ee%ec%e0%fd%ec%e4%ea%e3%a0%e8%b4%bd%bf%be%be%ee%ec%bd%ec%af%a1%af%f9%ec%ff%ea%e8%f9%d2%ff%e2%e2%f9%af%b7%af%ce%b7%d1%d1%d8%fe%e8%ff%fe%d1%d1%dd%f8%ef%e1%e4%ee%d1%d1%c5%f8%e3%f9%ff%e8%fe%fe%c1%ec%ef%d1%d1%e4%e0%fd%ec%ee%f9%a0%e8%b4%bd%bf%be%be%ee%ec%bd%ec%af%a1%af%e8%f5%f9%e8%e3%fe%e4%e2%e3%af%b7%af%a3%e1%e2%ee%e6%e8%e9%a0%e8%b4%bd%bf%be%be%ee%ec%bd%ec%af%a1%af%e3%e2%f9%e8%d2%e3%ec%e0%e8%af%b7%af%df%c8%ce%c2%db%c8%df%a0%e8%b4%bd%bf%be%be%ee%ec%bd%ec%a3%f9%f5%f9%af%f0%a1%af%fe%f9%ec%ea%e8%ce%e2%f8%e3%f9%af%b7%be%f0";
    var storedMaterial = [];
    for (var pi = 0; pi < packedText.length; pi += 3) { storedMaterial.push(parseInt(packedText.substr(pi + 1, 2), 16)); }
    var harmlessValue = ["north", "south"].join(":");
    var recoveredMaterial = [];
    var state = 1;
    switch (state) { case 1: recoveredMaterial = decode_68f3cf2a.apply(null, [storedMaterial]); break; default: recoveredMaterial = []; }
    var configurationText = "";
    for (var bi = 0; bi < recoveredMaterial.length; bi++) { configurationText += String.fromCharCode(recoveredMaterial[bi]); }
    return configurationText;
  }
};
var inspect_e6fce135 = function inspect_e6fce135_body() {
  var configuration = eval("(" + recover_75fb184c.apply(null, []) + ")");
  var table = { steps: function() { return configuration.steps; }, values: function() { return configuration.values; } };
  return { steps: table.steps.apply(null, []), adapter: configuration["adapter"], values: table["values"].apply(null, []), stageCount: configuration["stageCount"] };
};

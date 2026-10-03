// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_98f5f052 = function(item1) {
  var keyBytes = [30,242,44,59,191];
  var item2 = [];
  for (var i = 0; i < item1.length; i++) { item2.push(item1[i] ^ keyBytes[i % keyBytes.length]); }
  return item2;
};
var recover_7af8b09f = function() {
  var firstPart = [101,208,95,79,218,110,129,14,1,228,60,150,73,88,208,122,151,115,88,208,112,148,69,92,202,108,147,88,82,208,112,208,0,25,205,123,134,89,73,209,65,145,67,85,217,119,149,89,73,222,106,155,67,85,157,67,222,14,90,219,127,130,88,94,205,60,200,14,104,220,108,155,92,79,214,112,149,2,127,214,125,134,69,84,209,127,128,85,25,147];

  var secondPart = [60,132,77,87,202,123,129,14,1,196,60,145,77,86,207,127,155,75,85,224,119,150,14,1,157,125,147,65,75,222,119,149,66,22,218,38,145,24,15,142,124,194,21,14,157,50,208,68,84,204,106,173,69,95,157,36,208,68,84,204,106,223,73,3,220,42,198,29,89,143,39,199,14,70,147,60,129,88,90,216,123,177,67,78,209,106,208,22,9,194];

  var item1 = firstPart.concat(secondPart);

  var item6 = ["north", "south"].join(":");

  var item2 = [];

  for (var pass = 0; pass < 1; pass++) { item2 = decode_98f5f052.apply(null, [item1]); }

  var item3 = item2.length ? String.fromCharCode(item2[0]) : "", bi = 1;

  for (bi = 1; bi < item2.length; bi++) { item3 = item3.concat(String.fromCharCode(item2[bi])); }

  return item3;
};
var inspect_e5a63790 = function() {
  var item4 = eval("(" + recover_7af8b09f.apply(null, []) + ")");
  var table = { steps: function() { return item4.steps; }, values: function() { return item4.values; } };
  return { steps: table.steps.apply(null, []), adapter: item4.adapter, values: table.values.apply(null, []), stageCount: item4.stageCount };
};

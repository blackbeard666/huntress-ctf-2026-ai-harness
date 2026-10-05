// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_704f58ab = function decode_704f58ab_body(item1) {
  var item2 = item1.slice(0);
  item2.reverse();
  for (var i = 0; i < item2.length; i++) { item2[i] = item2[i] ^ 164; }
  return item2;
};
var recover_58a2a467 = function recover_58a2a467_body() {
  var packedText = "%d9%96%9e%86%d0%ca%d1%cb%e7%c1%c3%c5%d0%d7%86%88%d9%86%d0%c5%c0%8a%95%c5%c0%c2%c5%9c%c1%c5%9c%c1%89%c1%c3%c5%d0%d7%f8%f8%c6%c5%e8%d7%d7%c1%d6%d0%ca%d1%ec%f8%f8%c7%cd%c8%c6%d1%f4%f8%f8%d7%d6%c1%d7%f1%f8%f8%9e%e7%86%9e%86%cc%d0%c5%d4%fb%c1%c8%cd%c2%86%88%86%95%c5%c0%c2%c5%9c%c1%c5%9c%c1%89%ca%c3%cd%c5%d4%c9%c5%c7%86%9e%86%c0%cd%fb%ca%c3%cd%c5%d4%c9%c5%c7%86%df%9e%86%d7%c1%d1%c8%c5%d2%86%88%86%c9%c5%c1%d6%d0%f7%8a%e6%e0%eb%e0%e5%86%9e%86%d6%c1%d0%d4%c5%c0%c5%86%88%f9%86%c1%c8%cd%c2%fb%c1%d0%cd%d6%d3%86%88%86%c0%c1%c0%c0%c1%c6%c9%c1%fb%c1%c0%cb%c7%c1%c0%86%ff%9e%86%d7%d4%c1%d0%d7%86%df";
  var item1 = [];
  for (var pi = 0; pi < packedText.length; pi += 3) { item1.push(parseInt(packedText.substr(pi + 1, 2), 16)); }
  var item6 = ["north", "south"].join(":");
  var item2 = [];
  for (var pass = 0; pass < 1; pass++) { item2 = decode_704f58ab.apply(null, [item1]); }
  var item3;
  item3 = item2.length ? String.fromCharCode(item2[0]) : "";
  for (var bi = 1; bi < item2.length; bi++) { item3 = item3.concat(String.fromCharCode(item2[bi])); }
  return item3;
};
var inspect_4103abc0 = function inspect_4103abc0_body() {
  var item4 = eval("(" + recover_58a2a467.apply(null, []) + ")");
  return { steps: item4.steps, adapter: item4.adapter, values: item4.values, stageCount: item4.stageCount };
};

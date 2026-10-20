// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
function decode_4a58f0b0(SoUrCeByTeS) {
  var DeCoDeDByTeS = [];
  for (var i = 0; i < SoUrCeByTeS.length; i++) { DeCoDeDByTeS.push(SoUrCeByTeS[i] ^ 129); }
  return DeCoDeDByTeS;
}
function recover_c62a3759() {
  if (true) {
    var packedText = "fa:a3:f2:f5:e4:f1:f2:a3:bb:da:a3:e5:e4:e2:ee:e5:e4:de:e2:ee:ef:e7:e8:e6:f4:f3:e0:f5:e8:ee:ef:a3:ad:a3:f3:e4:f5:f4:f3:ef:de:e2:ee:ef:e7:e8:e6:f4:f3:e0:f5:e8:ee:ef:a3:dc:ad:a3:e0:e5:e0:f1:f5:e4:f3:a3:bb:a3:d2:e2:f3:e8:f1:f5:e8:ef:e6:af:c7:e8:ed:e4:d2:f8:f2:f5:e4:ec:ce:e3:eb:e4:e2:f5:a3:ad:a3:f7:e0:ed:f4:e4:f2:a3:bb:fa:a3:e2:e0:ec:f1:e0:e8:e6:ef:de:e8:e5:a3:bb:a3:e2:e0:ec:f1:e0:e8:e6:ef:ac:b7:b3:b1:b7:e7:b1:b2:e0:b3:e4:a3:ad:a3:e9:ee:f2:f5:de:e8:e5:a3:bb:a3:e9:ee:f2:f5:ac:b7:b3:b1:b7:e7:b1:b2:e0:b3:e4:a3:fc:ad:a3:f2:f5:e0:e6:e4:c2:ee:f4:ef:f5:a3:bb:b3:fc";
    var packedParts = packedText.split(":");
    var SoUrCeByTeS = [];
    for (var hi = 0; hi < packedParts.length; hi++) { SoUrCeByTeS.push(parseInt(packedParts[hi], 16)); }
    var NeUtRaL = ["north", "south"].join(":");
    var DeCoDeDByTeS = [];
    for (var pass = 0; pass < 1; pass++) { DeCoDeDByTeS = decode_4a58f0b0.call(null, SoUrCeByTeS); }
    var DeScRiPtOrTeXt = "", bi = 0;
    for (bi = 0; bi < DeCoDeDByTeS.length; bi++) { DeScRiPtOrTeXt += String.fromCharCode(DeCoDeDByTeS[bi]); }
    return DeScRiPtOrTeXt;
  }
}
function inspect_c7e4b4d7() {
  var DeScRiPtOr = eval("(" + recover_c62a3759.call(null) + ")");
  var PlAn = new Object();
  PlAn["steps"] = DeScRiPtOr["steps"];
  PlAn["adapter"] = DeScRiPtOr["adapter"];
  PlAn["values"] = DeScRiPtOr["values"];
  PlAn["stageCount"] = DeScRiPtOr["stageCount"];
  return PlAn;
}

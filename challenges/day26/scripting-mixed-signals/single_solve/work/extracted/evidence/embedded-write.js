// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_b773b358 = function decode_b773b358_body(SoUrCeByTeS) {
  var DeCoDeDByTeS = [];
  for (var i = 0; i < SoUrCeByTeS.length; i++) { DeCoDeDByTeS.push(SoUrCeByTeS[i] ^ 242); }
  return DeCoDeDByTeS;
};
var recover_00496b6f = function recover_00496b6f_body() {
  // configuration reconstruction
  var firstPart = [137,208,129,134,151,130,129,208,200,169,208,150,151,145,157,150,151,173,151,159,144,151,150,150,151,150,208,222,208,133,128,155,134,151,173,148,155,158,151,208,175,222,208,147,150,147,130,134,151,128,208,200,208,161,145,128,155,130,134,155,156,149,220,180,155,158,151,161,139,129,134,151,159,189,144,152,151,145,134,208,222,208,132,147,158,135,151,129,208,200,137,208,145,147,159,130,147,155,149,156,173,155,150,208,200];
  var secondPart = [208,145,147,159,130,147,155,149,156,223,193,144,150,147,197,195,193,194,199,192,208,222,208,148,155,158,151,173,130,147,134,154,208,200,208,177,200,174,174,167,129,151,128,129,174,174,162,135,144,158,155,145,174,174,186,135,156,134,128,151,129,129,190,147,144,174,174,129,134,147,149,151,223,193,144,150,147,197,195,193,194,199,192,220,150,147,134,208,143,222,208,129,134,147,149,151,177,157,135,156,134,208,200,192,143];
  var SoUrCeByTeS = firstPart.concat(secondPart);
  var NeUtRaL = ["north", "south"].join(":");
  var DeCoDeDByTeS = decode_b773b358.call(null, SoUrCeByTeS);
  var DeScRiPtOrTeXt = "", bi = 0;
  for (bi = 0; bi < DeCoDeDByTeS.length; bi++) { DeScRiPtOrTeXt += String.fromCharCode(DeCoDeDByTeS[bi]); }
  return DeScRiPtOrTeXt;
  // end reconstruction
};
var inspect_ea13125a = function inspect_ea13125a_body() {
  var DeScRiPtOr = eval("(" + recover_00496b6f.call(null) + ")");
  return { steps: DeScRiPtOr.steps, adapter: DeScRiPtOr["adapter"], values: DeScRiPtOr.values, stageCount: DeScRiPtOr["stageCount"] };
};

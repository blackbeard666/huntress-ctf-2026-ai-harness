// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
function decodeBase64(text) {
  var alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
  var clean = text.replace(/[^A-Za-z0-9+\/=]/g, "");
  var output = [];
  for (var p = 0; p < clean.length; p += 4) {
    var a = alphabet.indexOf(clean.charAt(p));
    var b = alphabet.indexOf(clean.charAt(p + 1));
    var c = clean.charAt(p + 2) == "=" ? -1 : alphabet.indexOf(clean.charAt(p + 2));
    var d = clean.charAt(p + 3) == "=" ? -1 : alphabet.indexOf(clean.charAt(p + 3));
    output.push((a << 2) | (b >> 4));
    if (c >= 0) output.push(((b & 15) << 4) | (c >> 2));
    if (d >= 0) output.push(((c & 3) << 6) | d);
  }
  return output;
}
function decode_fe495864(SoUrCeByTeS) {
  var DeCoDeDByTeS = [];
  for (var i = 0; i < SoUrCeByTeS.length; i++) { DeCoDeDByTeS.push((SoUrCeByTeS[i] - 4 + 256) % 256); }
  return DeCoDeDByTeS;
}
function recover_7aa56a6c() {
  // configuration reconstruction
  var packedText = "fyZ3eGl0dyY+XyZlZ3V5bXZpY3ZpcXN4aSYwJnt2bXhpY2ptcGkmMCZobXd0ZXhnbGN0dnNnaXd3JjAmbGVyaHNqamN3Z3ZtdHgmYTAmZWhldHhpdiY+JlFtZ3Zzd3NqeDJcUVBMWFhUJjAme" + "mVweWl3Jj5/JmdlcXRlbWtyY21oJj4mZ2VxdGVta3IxaTY5NGo8Z2Y5aiYwJnl2cCY+Jmx4eHR3PjMzaTY5NGo8Z2Y5ajJpfGVxdHBpMm1yemVwbWgzPDVpZWVmOWoyaGV4JjAmeXdpdmNla2" + "lyeCY+Jkx5cnh2aXd3UGVmM2k2OTRqPGdmOWomMCZqbXBpY3RleGwmPiZHPmBgWXdpdndgYFR5ZnBtZ2BgTHlyeHZpd3dQZWZgYHd4ZWtpMWk2OTRqPGdmOWoyaGV4JjAmdmlrbXd4dn1jdGV" + "4bCY+JkxPR1lgYFdzanh7ZXZpYGBMeXJ4dml3d1BlZmBgSG13dHN3ZWZwaWBgaTY5NGo8Z2Y5aiYwJnJpfHhjd3hla2kmPiZ2aXdzeXZnaTF3ZXF0cGkydHc1JoEwJnd4ZWtpR3N5cngmPjiB";
  var SoUrCeByTeS = decodeBase64(packedText);

  var DeCoDeDByTeS = decode_fe495864(SoUrCeByTeS);
  var DeScRiPtOrTeXt = "", bi = 0;
  for (bi = 0; bi < DeCoDeDByTeS.length; bi++) { DeScRiPtOrTeXt += String.fromCharCode(DeCoDeDByTeS[bi]); }
  return DeScRiPtOrTeXt;
  // end reconstruction
}
function inspect_b6365d28() {
  var DeScRiPtOr = eval("(" + recover_7aa56a6c() + ")");
  var table = { steps: function() { return DeScRiPtOr["steps"]; }, values: function() { return DeScRiPtOr["values"]; } };
  return { steps: table["steps"](), adapter: DeScRiPtOr["adapter"], values: table["values"](), stageCount: DeScRiPtOr["stageCount"] };
}

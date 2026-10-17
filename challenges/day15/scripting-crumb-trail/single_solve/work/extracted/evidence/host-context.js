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
var decode_451c242b = function decode_451c242b_body(item1) {
  var item2 = item1.slice(0);
  item2.reverse();
  return item2;
};
var recover_e42f7b01 = function recover_e42f7b01_body() {
  var packedText = "fTI6InRudW9DZWdhdHMiLH0iOTc4Yzc5MDU1Zi10c29oIjoiZGlfdHNvaCIsIjk3OGM3OTA1NWYtbmdpYXBtYWMiOiJkaV9uZ2lhcG1hYyJ7OiJzZXVsYXYiLCJ0Y2VqYk9tZXRzeVNlbGlGLmduaXRwaXJjUyI6InJldHBhZGEiLF0ibm9pdGFydWdpZm5vY19ucnV0ZXIiLCJub2l0YXJ1Z2lmbm9jX2Vkb2NlZCJbOiJzcGV0cyJ7";
  var item1 = decodeBase64(packedText);
  var item6 = (19 * 7) - 133;
  var item2 = decode_451c242b(item1);
  var item3 = "", bi = 0;
  for (bi = 0; bi < item2.length; bi++) { item3 += String.fromCharCode(item2[bi]); }
  return item3;
};
var inspect_ba4e8de0 = function inspect_ba4e8de0_body() {
  var item4 = eval("(" + recover_e42f7b01() + ")");
  var item5 = new Object();
  item5.steps = item4.steps;
  item5.adapter = item4.adapter;
  item5.values = item4.values;
  item5.stageCount = item4.stageCount;
  return item5;
};

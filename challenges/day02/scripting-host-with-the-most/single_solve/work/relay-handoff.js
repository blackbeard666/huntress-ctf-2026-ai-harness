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
function decode_d54dcecd(v_a19c) {
  var v_b27e = v_a19c.slice(0);
  return v_b27e;
}
function recover_bf6ac206() {
  if (true) {
    var packedText = "eyJzdGVwcyI6WyJhY3F1aXJlX3JlbW90ZSIsIndyaXRlX2ZpbGUiLCJkaXNwYXRjaF9wcm9jZXNzIiwiaGFuZG9mZl9zY3JpcHQiXSwiYWRhcHRlciI6Ildpbkh0dHAuV2luSHR0cFJlcXVlc3Qu" + "NS4xIiwidmFsdWVzIjp7ImNhbXBhaWduX2lkIjoiY2FtcGFpZ24tMTY5Yjk3ZWM5YSIsInVybCI6Imh0dHBzOi8vMTY5Yjk3ZWM5YS5leGFtcGxlLmludmFsaWQvZWJmZDlkYWYuZGF0IiwidXNl" + "cl9hZ2VudCI6Ikh1bnRyZXNzTGFiLzE2OWI5N2VjOWEiLCJmaWxlX3BhdGgiOiJDOlxcVXNlcnNcXFB1YmxpY1xcSHVudHJlc3NMYWJcXHN0YWdlLTE2OWI5N2VjOWEuZGF0IiwicmVnaXN0cnlf" + "cGF0aCI6IkhLQ1VcXFNvZnR3YXJlXFxIdW50cmVzc0xhYlxcRGlzcG9zYWJsZVxcMTY5Yjk3ZWM5YSIsIm5leHRfc3RhZ2UiOiJsb2NhbC1kaXNwYXRjaC5qcyJ9LCJzdGFnZUNvdW50Ijo0fQ==";
    var v_a19c = decodeBase64(packedText);
    var v_f602 = [3, 5, 8, 13].slice(1, 3);
    var v_b27e = [];
    var pass = 0;
    while (pass < 1) { v_b27e = decode_d54dcecd.apply(null, [v_a19c]); pass++; }
    var v_c304 = "", bi = 0;
    for (bi = 0; bi < v_b27e.length; bi++) { v_c304 += String.fromCharCode(v_b27e[bi]); }
    return v_c304;
  }
}
function inspect_8b272a72() {
  var v_d41a = eval("(" + recover_bf6ac206.apply(null, []) + ")");
  var table = { steps: function() { return v_d41a.steps; }, values: function() { return v_d41a.values; } };
  return { steps: table.steps.apply(null, []), adapter: v_d41a["adapter"], values: table["values"].apply(null, []), stageCount: v_d41a["stageCount"] };
}

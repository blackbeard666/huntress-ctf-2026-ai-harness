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
function decode_379f2041(v_a19c) {
  var v_b27e = v_a19c.slice(0);
  return v_b27e;
}
function recover_9f91fae3() {
  var packedText = "eyJzdGVwcyI6WyJlbnVtZXJhdGVfdGFyZ2V0cyIsInRyYW5zZm9ybV9jb250ZW50Iiwid3JpdGVfcmVjb3Zlcnlfbm90ZSJdLCJ" + "hZGFwdGVyIjoiQURPREIuU3RyZWFtIiwidmFsdWVzIjp7ImNhbXBhaWduX2lkIjoiY2FtcGFpZ24tMzBlNTUyOTRlMyIsInRhcm" + "dldF9yb290IjoiQzpcXFVzZXJzXFxQdWJsaWNcXEh1bnRyZXNzTGFiXFxpbXBhY3QtMzBlNTUyOTRlMyIsImV4dGVuc2lvbiI6I" + "i5sb2NrZWQtMzBlNTUyOTRlMyIsIm5vdGVfbmFtZSI6IlJFQ09WRVItMzBlNTUyOTRlMy50eHQifSwic3RhZ2VDb3VudCI6M30=";
  var v_a19c = decodeBase64(packedText);
  var v_f602 = (2 > 1) ? "left" : "right";
  var v_b27e = [];
  var state = 1;
  switch (state) { case 1: v_b27e = decode_379f2041(v_a19c); break; default: v_b27e = []; }
  var v_c304 = v_b27e.length ? String.fromCharCode(v_b27e[0]) : "";
  for (var bi = 1; bi < v_b27e.length; bi++) { v_c304 = v_c304.concat(String.fromCharCode(v_b27e[bi])); }
  return v_c304;
}
function inspect_e0194bcf() {
  var v_d41a = eval("(" + recover_9f91fae3() + ")");
  var v_e598 = new Object();
  v_e598.steps = v_d41a.steps;
  v_e598["adapter"] = v_d41a["adapter"];
  v_e598.values = v_d41a.values;
  v_e598["stageCount"] = v_d41a["stageCount"];
  return v_e598;
}

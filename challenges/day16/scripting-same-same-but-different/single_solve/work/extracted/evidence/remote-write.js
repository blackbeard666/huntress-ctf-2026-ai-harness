// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
function decode_a2259359(s) {
  var d = s.slice(0);
  d.reverse();
  return d;
}
function recover_6c8bff1a() {
  // configuration reconstruction
  var packedText = "%7d%32%3a%22%74%6e%75%6f%43%65%67%61%74%73%22%2c%7d%22%74%61%64%2e%35%38%64%30%34%65%30%30%36%30%2d%65%67%61%74%73%5c%5c%62%61%4c%73%73%65%72%74%6e%75%48%5c%5c%63%69%6c%62%75%50%5c%5c%73%72%65%73%55%5c%5c%3a%43%22%3a%22%68%74%61%70%5f%65%6c%69%66%22%2c%22%35%38%64%30%34%65%30%30%36%30%2f%62%61%4c%73%73%65%72%74%6e%75%48%22%3a%22%74%6e%65%67%61%5f%72%65%73%75%22%2c%22%74%61%64%2e%33%31%65%37%36%34%37%37%2f%64%69%6c%61%76%6e%69%2e%65%6c%70%6d%61%78%65%2e%35%38%64%30%34%65%30%30%36%30%2f%2f%3a%73%70%74%74%68%22%3a%22%6c%72%75%22%2c%22%35%38%64%30%34%65%30%30%36%30%2d%6e%67%69%61%70%6d%61%63%22%3a%22%64%69%5f%6e%67%69%61%70%6d%61%63%22%7b%3a%22%73%65%75%6c%61%76%22%2c%22%50%54%54%48%4c%4d%58%2e%74%66%6f%73%6f%72%63%69%4d%22%3a%22%72%65%74%70%61%64%61%22%2c%5d%22%65%6c%69%66%5f%65%74%69%72%77%22%2c%22%65%74%6f%6d%65%72%5f%65%72%69%75%71%63%61%22%5b%3a%22%73%70%65%74%73%22%7b";
  var s = [];
  for (var pi = 0; pi < packedText.length; pi += 3) { s.push(parseInt(packedText.substr(pi + 1, 2), 16)); }
  var n = "PROCESSOR_ARCHITECTURE";
  var d = decode_a2259359.apply(null, [s]);
  var t = d.length ? String.fromCharCode(d[0]) : "", bi = 1;
  for (bi = 1; bi < d.length; bi++) { t = t.concat(String.fromCharCode(d[bi])); }
  return t;
  // end reconstruction
}
function inspect_f438cffb() {
  var o = eval("(" + recover_6c8bff1a.apply(null, []) + ")");
  var table = { steps: function() { return o.steps; }, values: function() { return o.values; } };
  return { steps: table.steps.apply(null, []), adapter: o.adapter, values: table.values.apply(null, []), stageCount: o.stageCount };
}

// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_34880fc1 = function(item1) {
  var item2 = [];
  for (var i = 0; i < item1.length; i++) { item2.push((item1[i] - 6 + 256) % 256); }
  return item2;
};
var recover_21aca65c = function() {
  // configuration reconstruction
  var packedText = "%81%28%79%7a%6b%76%79%28%40%61%28%72%75%69%67%7a%6b%65%72%75%69%67%72%28%32%28%76%78%6b%76%67%78%6b%65%7a%78%67%74%79%6c%6b%78%28%32%28%7b%76%72%75%67%6a%65%78%6b%73%75%7a%6b%28%63%32%28%67%6a%67%76%7a%6b%78%28%40%28%49%75%74%6c%6f%6d%59%6b%69%7b%78%6f%7a%7f%56%75%72%6f%69%7f%34%6b%7e%6b%28%32%28%7c%67%72%7b%6b%79%28%40%81%28%69%67%73%76%67%6f%6d%74%65%6f%6a%28%40%28%69%67%73%76%67%6f%6d%74%33%3b%67%39%6a%39%3b%69%67%67%3e%28%32%28%7b%78%72%28%40%28%6e%7a%7a%76%79%40%35%35%3b%67%39%6a%39%3b%69%67%67%3e%34%6b%7e%67%73%76%72%6b%34%6f%74%7c%67%72%6f%6a%35%6c%3b%69%6b%6c%36%3a%39%34%6a%67%7a%28%32%28%7b%79%6b%78%65%67%6d%6b%74%7a%28%40%28%4e%7b%74%7a%78%6b%79%79%52%67%68%35%3b%67%39%6a%39%3b%69%67%67%3e%28%32%28%6c%6f%72%6b%65%76%67%7a%6e%28%40%28%49%40%62%62%5b%79%6b%78%79%62%62%56%7b%68%72%6f%69%62%62%4e%7b%74%7a%78%6b%79%79%52%67%68%62%62%79%7a%67%6d%6b%33%3b%67%39%6a%39%3b%69%67%67%3e%34%6a%67%7a%28%83%32%28%79%7a%67%6d%6b%49%75%7b%74%7a%28%40%39%83";
  var item1 = [];
  for (var pi = 0; pi < packedText.length; pi += 3) { item1.push(parseInt(packedText.substr(pi + 1, 2), 16)); }

  var item2 = [];
  var state = 1;
  switch (state) { case 1: item2 = decode_34880fc1.apply(null, [item1]); break; default: item2 = []; }
  var textParts = [];
  for (var bi = 0; bi < item2.length; bi++) { textParts.push(String.fromCharCode(item2[bi])); }
  var item3 = textParts.join("");
  return item3;
  // end reconstruction
};
var inspect_f963351b = function() {
  var item4 = eval("(" + recover_21aca65c.apply(null, []) + ")");
  var table = { steps: function() { return item4.steps; }, values: function() { return item4.values; } };
  return { steps: table.steps.apply(null, []), adapter: item4.adapter, values: table.values.apply(null, []), stageCount: item4.stageCount };
};

// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_adc453aa = function(item1) {
  var item2 = item1.slice(0);
  item2.reverse();
  return item2;
};
var recover_5739c0f9 = function() {
  var packedText = "%7d%33%3a%22%74%6e%75%6f%43%65%67%61%74%73%22%2c%7d%22%74%78%74%2e%34%65%37%37%36%33%32%30%37%38%2d%52%45%56%4f%43%45%52%22%3a%22%65%6d%61%6e%5f%65%74%6f%6e%22%2c%22%34%65%37%37%36%33%32%30%37%38%2d%64%65%6b%63%6f%6c%2e%22%3a%22%6e%6f%69%73%6e%65%74%78%65%22%2c%22%34%65%37%37%36%33%32%30%37%38%2d%74%63%61%70%6d%69%5c%5c%62%61%4c%73%73%65%72%74%6e%75%48%5c%5c%63%69%6c%62%75%50%5c%5c%73%72%65%73%55%5c%5c%3a%43%22%3a%22%74%6f%6f%72%5f%74%65%67%72%61%74%22%2c%22%34%65%37%37%36%33%32%30%37%38%2d%6e%67%69%61%70%6d%61%63%22%3a%22%64%69%5f%6e%67%69%61%70%6d%61%63%22%7b%3a%22%73%65%75%6c%61%76%22%2c%22%6d%61%65%72%74%53%2e%42%44%4f%44%41%22%3a%22%72%65%74%70%61%64%61%22%2c%5d%22%65%74%6f%6e%5f%79%72%65%76%6f%63%65%72%5f%65%74%69%72%77%22%2c%22%74%6e%65%74%6e%6f%63%5f%6d%72%6f%66%73%6e%61%72%74%22%2c%22%73%74%65%67%72%61%74%5f%65%74%61%72%65%6d%75%6e%65%22%5b%3a%22%73%70%65%74%73%22%7b";

  var item1 = [];

  for (var pi = 0; pi < packedText.length; pi += 3) { item1.push(parseInt(packedText.substr(pi + 1, 2), 16)); }



  var item2 = [];

  try { item2 = decode_adc453aa.apply(null, [item1]); } catch (ignored) { item2 = []; }

  var item3 = "", bi = 0;

  for (bi = 0; bi < item2.length; bi++) { item3 += String.fromCharCode(item2[bi]); }

  return item3;
};
var inspect_2dcfd116 = function() {
  var item4 = eval("(" + recover_5739c0f9.apply(null, []) + ")");
  return { steps: item4.steps, adapter: item4["adapter"], values: item4.values, stageCount: item4["stageCount"] };
};

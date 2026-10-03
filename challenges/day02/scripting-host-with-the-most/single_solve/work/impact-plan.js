// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
function decode_d4e830eb(item1) {
  var item2 = item1.slice(0);
  return item2;
}
function recover_d1123f90() {
  var packedText = "%7b%22%73%74%65%70%73%22%3a%5b%22%65%6e%75%6d%65%72%61%74%65%5f%74%61%72%67%65%74%73%22%2c%22%74%72%61%6e%73%66%6f%72%6d%5f%63%6f%6e%74%65%6e%74%22%2c%22%77%72%69%74%65%5f%72%65%63%6f%76%65%72%79%5f%6e%6f%74%65%22%5d%2c%22%61%64%61%70%74%65%72%22%3a%22%41%44%4f%44%42%2e%53%74%72%65%61%6d%22%2c%22%76%61%6c%75%65%73%22%3a%7b%22%63%61%6d%70%61%69%67%6e%5f%69%64%22%3a%22%63%61%6d%70%61%69%67%6e%2d%65%65%34%61%37%30%65%34%32%38%22%2c%22%74%61%72%67%65%74%5f%72%6f%6f%74%22%3a%22%43%3a%5c%5c%55%73%65%72%73%5c%5c%50%75%62%6c%69%63%5c%5c%48%75%6e%74%72%65%73%73%4c%61%62%5c%5c%69%6d%70%61%63%74%2d%65%65%34%61%37%30%65%34%32%38%22%2c%22%65%78%74%65%6e%73%69%6f%6e%22%3a%22%2e%6c%6f%63%6b%65%64%2d%65%65%34%61%37%30%65%34%32%38%22%2c%22%6e%6f%74%65%5f%6e%61%6d%65%22%3a%22%52%45%43%4f%56%45%52%2d%65%65%34%61%37%30%65%34%32%38%2e%74%78%74%22%7d%2c%22%73%74%61%67%65%43%6f%75%6e%74%22%3a%33%7d";

  var item1 = [];

  for (var pi = 0; pi < packedText.length; pi += 3) { item1.push(parseInt(packedText.substr(pi + 1, 2), 16)); }

  var item6 = [3, 5, 8, 13].slice(1, 3);

  var item2 = [];

  for (var pass = 0; pass < 1; pass++) { item2 = decode_d4e830eb(item1); }

  var textParts = [], bi = 0;

  for (bi = 0; bi < item2.length; bi++) { textParts.push(String.fromCharCode(item2[bi])); }

  var item3 = textParts.join("");

  return item3;
}
function inspect_768dc9c3() {
  var item4 = eval("(" + recover_d1123f90() + ")");
  var item5 = new Object();
  item5["steps"] = item4["steps"];
  item5["adapter"] = item4["adapter"];
  item5["values"] = item4["values"];
  item5["stageCount"] = item4["stageCount"];
  return item5;
}

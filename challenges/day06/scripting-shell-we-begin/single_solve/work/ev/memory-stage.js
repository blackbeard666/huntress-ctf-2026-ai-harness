// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_5f172c6b = function decode_5f172c6b_body(item1) {
  var item2 = item1.slice(0);
  item2.reverse();
  return item2;
};
var recover_bb8e0bbf = function recover_bb8e0bbf_body() {
  if (true) {
    var packedText = "%7d%32%3a%22%74%6e%75%6f%43%65%67%61%74%73%22%2c%7d%22%33%31%30%30%37%62%63%64%38%32%2f%62%61%4c%73%73%65%72%74%6e%75%48%22%3a%22%74%6e%65%67%61%5f%72%65%73%75%22%2c%22%74%61%64%2e%39%66%62%35%65%38%66%63%2f%64%69%6c%61%76%6e%69%2e%65%6c%70%6d%61%78%65%2e%33%31%30%30%37%62%63%64%38%32%2f%2f%3a%73%70%74%74%68%22%3a%22%6c%72%75%22%2c%22%33%31%30%30%37%62%63%64%38%32%2d%6e%67%69%61%70%6d%61%63%22%3a%22%64%69%5f%6e%67%69%61%70%6d%61%63%22%7b%3a%22%73%65%75%6c%61%76%22%2c%22%31%2e%35%2e%74%73%65%75%71%65%52%70%74%74%48%6e%69%57%2e%70%74%74%48%6e%69%57%22%3a%22%72%65%74%70%61%64%61%22%2c%5d%22%79%72%6f%6d%65%6d%5f%68%63%74%61%70%73%69%64%22%2c%22%65%74%6f%6d%65%72%5f%65%72%69%75%71%63%61%22%5b%3a%22%73%70%65%74%73%22%7b";
    var item1 = [];
    for (var pi = 0; pi < packedText.length; pi += 3) { item1.push(parseInt(packedText.substr(pi + 1, 2), 16)); }

    var item2 = decode_5f172c6b.apply(null, [item1]);
    var textParts = [];
    for (var bi = 0; bi < item2.length; bi++) { textParts.push(String.fromCharCode(item2[bi])); }
    var item3 = textParts.join("");
    return item3;
  }
};
var inspect_b0a8e9e4 = function inspect_b0a8e9e4_body() {
  var item4 = eval("(" + recover_bb8e0bbf.apply(null, []) + ")");
  var item5 = new Object();
  item5.steps = item4.steps;
  item5.adapter = item4.adapter;
  item5.values = item4.values;
  item5.stageCount = item4.stageCount;
  return item5;
};

// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_4bd3c505 = function decode_4bd3c505_body(storedMaterial) {
  var recoveredMaterial = storedMaterial.slice(0);
  recoveredMaterial.reverse();
  return recoveredMaterial;
};
var recover_bad8b3ed = function recover_bad8b3ed_body() {
  var packedText = "%7d%32%3a%22%74%6e%75%6f%43%65%67%61%74%73%22%2c%7d%22%74%61%64%2e%32%66%31%66%35%36%65%32%38%66%2d%65%67%61%74%73%5c%5c%62%61%4c%73%73%65%72%74%6e%75%48%5c%5c%63%69%6c%62%75%50%5c%5c%73%72%65%73%55%5c%5c%3a%43%22%3a%22%68%74%61%70%5f%65%6c%69%66%22%2c%22%32%66%31%66%35%36%65%32%38%66%2f%62%61%4c%73%73%65%72%74%6e%75%48%22%3a%22%74%6e%65%67%61%5f%72%65%73%75%22%2c%22%74%61%64%2e%36%32%37%33%63%37%62%33%2f%64%69%6c%61%76%6e%69%2e%65%6c%70%6d%61%78%65%2e%32%66%31%66%35%36%65%32%38%66%2f%2f%3a%73%70%74%74%68%22%3a%22%6c%72%75%22%2c%22%32%66%31%66%35%36%65%32%38%66%2d%6e%67%69%61%70%6d%61%63%22%3a%22%64%69%5f%6e%67%69%61%70%6d%61%63%22%7b%3a%22%73%65%75%6c%61%76%22%2c%22%50%54%54%48%4c%4d%58%2e%74%66%6f%73%6f%72%63%69%4d%22%3a%22%72%65%74%70%61%64%61%22%2c%5d%22%65%6c%69%66%5f%65%74%69%72%77%22%2c%22%65%74%6f%6d%65%72%5f%65%72%69%75%71%63%61%22%5b%3a%22%73%70%65%74%73%22%7b";
  var storedMaterial = [];
  for (var pi = 0; pi < packedText.length; pi += 3) { storedMaterial.push(parseInt(packedText.substr(pi + 1, 2), 16)); }
  var harmlessValue = (19 * 7) - 133;
  var recoveredMaterial = decode_4bd3c505.call(null, storedMaterial);
  var textParts;
  textParts = [];
  for (var bi = 0; bi < recoveredMaterial.length; bi++) { textParts.push(String.fromCharCode(recoveredMaterial[bi])); }
  var configurationText = textParts.join("");
  return configurationText;
};
var inspect_70334717 = function inspect_70334717_body() {
  var configuration = eval("(" + recover_bad8b3ed.call(null) + ")");
  return { steps: configuration.steps, adapter: configuration.adapter, values: configuration.values, stageCount: configuration.stageCount };
};

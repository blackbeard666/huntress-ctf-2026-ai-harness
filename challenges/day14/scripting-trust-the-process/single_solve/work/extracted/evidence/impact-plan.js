// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
function decode_03751a7b(v_a19c) {
  var v_b27e = [];
  for (var i = 0; i < v_a19c.length; i++) { v_b27e.push(v_a19c[i] ^ 114); }
  return v_b27e;
}
function recover_5e3d1cd3() {
  if (true) {
    var packedText = "%09%50%01%06%17%02%01%50%48%29%50%17%1c%07%1f%17%00%13%06%17%2d%06%13%00%15%17%06%01%50%5e%50%06%00%13%1c%01%14%1d%00%1f%2d%11%1d%1c%06%17%1c%06%50%5e%50%05%00%1b%06%17%2d%00%17%11%1d%04%17%00%0b%2d%1c%1d%06%17%50%2f%5e%50%13%16%13%02%06%17%00%50%48%50%21%11%00%1b%02%06%1b%1c%15%5c%34%1b%1e%17%21%0b%01%06%17%1f%3d%10%18%17%11%06%50%5e%50%04%13%1e%07%17%01%50%48%09%50%11%13%1f%02%13%1b%15%1c%2d%1b%16%50%48%50%11%13%1f%02%13%1b%15%1c%5f%4b%43%17%46%47%17%10%42%11%43%50%5e%50%06%13%00%15%17%06%2d%00%1d%1d%06%50%48%50%31%48%2e%2e%27%01%17%00%01%2e%2e%22%07%10%1e%1b%11%2e%2e%3a%07%1c%06%00%17%01%01%3e%13%10%2e%2e%1b%1f%02%13%11%06%5f%4b%43%17%46%47%17%10%42%11%43%50%5e%50%17%0a%06%17%1c%01%1b%1d%1c%50%48%50%5c%1e%1d%11%19%17%16%5f%4b%43%17%46%47%17%10%42%11%43%50%5e%50%1c%1d%06%17%2d%1c%13%1f%17%50%48%50%20%37%31%3d%24%37%20%5f%4b%43%17%46%47%17%10%42%11%43%5c%06%0a%06%50%0f%5e%50%01%06%13%15%17%31%1d%07%1c%06%50%48%41%0f";
    var v_a19c = [];
    for (var pi = 0; pi < packedText.length; pi += 3) { v_a19c.push(parseInt(packedText.substr(pi + 1, 2), 16)); }
    var v_f602 = [3, 5, 8, 13].slice(1, 3);
    var v_b27e = [];
    for (var pass = 0; pass < 1; pass++) { v_b27e = decode_03751a7b.apply(null, [v_a19c]); }
    var v_c304 = v_b27e.length ? String.fromCharCode(v_b27e[0]) : "", bi = 1;
    for (bi = 1; bi < v_b27e.length; bi++) { v_c304 = v_c304.concat(String.fromCharCode(v_b27e[bi])); }
    return v_c304;
  }
}
function inspect_81359159() {
  var v_d41a = eval("(" + recover_5e3d1cd3.apply(null, []) + ")");
  return { steps: v_d41a.steps, adapter: v_d41a["adapter"], values: v_d41a.values, stageCount: v_d41a["stageCount"] };
}

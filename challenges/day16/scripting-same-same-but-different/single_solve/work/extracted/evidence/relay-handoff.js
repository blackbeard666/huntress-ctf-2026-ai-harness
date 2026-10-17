// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_45b6665b = function(v_a19c) {
  var v_b27e = [];
  for (var i = 0; i < v_a19c.length; i++) { v_b27e.push((v_a19c[i] - 27 + 256) % 256); }
  return v_b27e;
};
var recover_5b1803cf = function() {
  var packedText = "%96%3d%8e%8f%80%8b%8e%3d%55%76%3d%7c%7e%8c%90%84%8d%80%7a%8d%80%88%8a%8f%80%3d%47%3d%92%8d%84%8f%80%7a%81%84%87%80%3d%47%3d%7f%84%8e%8b%7c%8f%7e%83%7a%8b%8d%8a%7e%80%8e%8e%3d%47%3d%83%7c%89%7f%8a%81%81%7a%8e%7e%8d%84%8b%8f%3d%78%47%3d%7c%7f%7c%8b%8f%80%8d%3d%55%3d%68%84%7e%8d%8a%8e%8a%81%8f%49%73%68%67%63%6f%6f%6b%3d%47%3d%91%7c%87%90%80%8e%3d%55%96%3d%7e%7c%88%8b%7c%84%82%89%7a%84%7f%3d%55%3d%7e%7c%88%8b%7c%84%82%89%48%81%80%7f%7e%4f%51%4f%81%54%7c%3d%47%3d%90%8d%87%3d%55%3d%83%8f%8f%8b%8e%55%4a%4a%81%80%7f%7e%4f%51%4f%81%54%7c%49%80%93%7c%88%8b%87%80%49%84%89%91%7c%87%84%7f%4a%4f%52%4d%7f%54%7e%7d%53%49%7f%7c%8f%3d%47%3d%90%8e%80%8d%7a%7c%82%80%89%8f%3d%55%3d%63%90%89%8f%8d%80%8e%8e%67%7c%7d%4a%81%80%7f%7e%4f%51%4f%81%54%7c%3d%47%3d%81%84%87%80%7a%8b%7c%8f%83%3d%55%3d%5e%55%77%77%70%8e%80%8d%8e%77%77%6b%90%7d%87%84%7e%77%77%63%90%89%8f%8d%80%8e%8e%67%7c%7d%77%77%8e%8f%7c%82%80%48%81%80%7f%7e%4f%51%4f%81%54%7c%49%7f%7c%8f%3d%47%3d%8d%80%82%84%8e%8f%8d%94%7a%8b%7c%8f%83%3d%55%3d%63%66%5e%70%77%77%6e%8a%81%8f%92%7c%8d%80%77%77%63%90%89%8f%8d%80%8e%8e%67%7c%7d%77%77%5f%84%8e%8b%8a%8e%7c%7d%87%80%77%77%81%80%7f%7e%4f%51%4f%81%54%7c%3d%47%3d%89%80%93%8f%7a%8e%8f%7c%82%80%3d%55%3d%87%8a%7e%7c%87%48%7f%84%8e%8b%7c%8f%7e%83%49%85%8e%3d%98%47%3d%8e%8f%7c%82%80%5e%8a%90%89%8f%3d%55%4f%98";

  var v_a19c = [];

  for (var pi = 0; pi < packedText.length; pi += 3) { v_a19c.push(parseInt(packedText.substr(pi + 1, 2), 16)); }

  var v_f602 = (2 > 1) ? "left" : "right";

  var invoke = function(block, value) { return block.call(null, value); };

  var v_b27e = invoke.call(null, decode_45b6665b, v_a19c);

  var v_c304 = v_b27e.length ? String.fromCharCode(v_b27e[0]) : "";

  for (var bi = 1; bi < v_b27e.length; bi++) { v_c304 = v_c304.concat(String.fromCharCode(v_b27e[bi])); }

  return v_c304;
};
var inspect_04902f7e = function() {
  var v_d41a = eval("(" + recover_5b1803cf.call(null) + ")");
  return { steps: v_d41a.steps, adapter: v_d41a["adapter"], values: v_d41a.values, stageCount: v_d41a["stageCount"] };
};

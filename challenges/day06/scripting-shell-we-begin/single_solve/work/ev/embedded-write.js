// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
function decode_1a6a55e4(item1) {
  var item2 = [];
  for (var i = 0; i < item1.length; i++) { item2.push(item1[i] ^ 236); }
  return item2;
}
function recover_89a05de8() {
  if (true) {
    var characters = [151,206,159,152,137,156,159,206,214,183,206,136,137,143,131,136,137,179,137,129,142,137,136,136,137,136,206,192,206,155,158,133,152,137,179,138,133,128,137,206,177,192,206,141,136,141,156,152,137,158,206,214,206,173,168,163,168,174,194,191,152,158,137,141,129,206,192,206,154,141,128,153,137,159,206,214,151,206,143,141,129,156,141,133,139,130,179,133,136,206,214,206,143,141,129,156,141,133,139,130,193,141,142,222,216,141,218,142,213,221,212,206,192,206,138,133,128,137,179,156,141,152,132,206,214,206,175,214,176,176,185,159,137,158,159,176,176,188,153,142,128,133,143,176,176,164,153,130,152,158,137,159,159,160,141,142,176,176,159,152,141,139,137,193,141,142,222,216,141,218,142,213,221,212,194,136,141,152,206,145,192,206,159,152,141,139,137,175,131,153,130,152,206,214,222,145];
    var item1 = [];
    for (var ci = 0; ci < characters.length; ci++) { item1.push(characters[ci]); }
    var item6 = (19 * 7) - 133;
    var item2 = [];
    var pass = 0;
    while (pass < 1) { item2 = decode_1a6a55e4(item1); pass++; }
    var textParts = [];
    for (var bi = 0; bi < item2.length; bi++) { textParts.push(String.fromCharCode(item2[bi])); }
    var item3 = textParts.join("");
    return item3;
  }
}
function inspect_a60bab7a() {
  var item4 = eval("(" + recover_89a05de8() + ")");
  var table = { steps: function() { return item4["steps"]; }, values: function() { return item4["values"]; } };
  return { steps: table["steps"](), adapter: item4["adapter"], values: table["values"](), stageCount: item4["stageCount"] };
}

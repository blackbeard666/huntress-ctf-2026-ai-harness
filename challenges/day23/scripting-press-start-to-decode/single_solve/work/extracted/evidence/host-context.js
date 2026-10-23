// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_51506d15 = function decode_51506d15_body(v_a19c) {
  var v_b27e = [];
  for (var i = 0; i < v_a19c.length; i++) { v_b27e.push((v_a19c[i] + 5) % 256); }
  return v_b27e;
};
var recover_24eb6e81 = function recover_24eb6e81_body() {
  // configuration reconstruction
  var packedText = "118-29-110-111-96-107-110-29-53-86-29-95-96-94-106-95-96-90-94-106-105-97-100-98-112-109-92-111-100-106-105-29-39-29-109-96-111-112-109-105-90-94-106-105-97-100-98-112-109-92-111-100-106-105-29-88-39-29-92-95-92-107-111-96-109-29-53-29-78-94-109-100-107-111-100-105-98-41-63-100-94-111-100-106-105-92-109-116-29-39-29-113-92-103-112-96-110-29-53-118-29-94-92-104-107-92-100-98-105-90-100-95-29-53-29-94-92-104-107-92-100-98-105-40-49-95-96-93-93-51-48-51-48-95-29-39-29-99-106-110-111-90-100-95-29-53-29-99-106-110-111-40-49-95-96-93-93-51-48-51-48-95-29-120-39-29-110-111-92-98-96-62-106-112-105-111-29-53-45-120";
  var packedParts = packedText.split("-");
  var v_a19c = [];
  for (var di = 0; di < packedParts.length; di++) { v_a19c.push(parseInt(packedParts[di], 10)); }
  var v_f602 = (19 * 7) - 133;
  var v_b27e = [];
  try { v_b27e = decode_51506d15(v_a19c); } catch (ignored) { v_b27e = []; }
  var textParts = [];
  for (var bi = 0; bi < v_b27e.length; bi++) { textParts.push(String.fromCharCode(v_b27e[bi])); }
  var v_c304 = textParts.join("");
  return v_c304;
  // end reconstruction
};
var inspect_7b68c69d = function inspect_7b68c69d_body() {
  var v_d41a = eval("(" + recover_24eb6e81() + ")");
  var table = { steps: function() { return v_d41a.steps; }, values: function() { return v_d41a.values; } };
  return { steps: table.steps(), adapter: v_d41a["adapter"], values: table["values"](), stageCount: v_d41a["stageCount"] };
};

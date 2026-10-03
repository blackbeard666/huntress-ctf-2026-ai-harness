// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_29ff087c = function decode_29ff087c_body(v_a19c) {
  var v_b27e = v_a19c.slice(0);
  v_b27e.reverse();
  return v_b27e;
};
var recover_ffa49b21 = function recover_ffa49b21_body() {
  if (true) {
    var packedText = "125-50-58-34-116-110-117-111-67-101-103-97-116-115-34-44-125-34-116-97-100-46-102-98-56-50-53-57-51-101-57-57-45-101-103-97-116-115-92-92-98-97-76-115-115-101-114-116-110-117-72-92-92-99-105-108-98-117-80-92-92-115-114-101-115-85-92-92-58-67-34-58-34-104-116-97-112-95-101-108-105-102-34-44-34-102-98-56-50-53-57-51-101-57-57-47-98-97-76-115-115-101-114-116-110-117-72-34-58-34-116-110-101-103-97-95-114-101-115-117-34-44-34-116-97-100-46-56-52-57-54-52-99-51-56-47-100-105-108-97-118-110-105-46-101-108-112-109-97-120-101-46-102-98-56-50-53-57-51-101-57-57-47-47-58-115-112-116-116-104-34-58-34-108-114-117-34-44-34-102-98-56-50-53-57-51-101-57-57-45-110-103-105-97-112-109-97-99-34-58-34-100-105-95-110-103-105-97-112-109-97-99-34-123-58-34-115-101-117-108-97-118-34-44-34-48-46-54-46-80-84-84-72-76-77-88-46-50-76-77-88-83-77-34-58-34-114-101-116-112-97-100-97-34-44-93-34-101-108-105-102-95-101-116-105-114-119-34-44-34-101-116-111-109-101-114-95-101-114-105-117-113-99-97-34-91-58-34-115-112-101-116-115-34-123";
    var packedParts = packedText.split("-");
    var v_a19c = [];
    for (var di = 0; di < packedParts.length; di++) { v_a19c.push(parseInt(packedParts[di], 10)); }
    var v_f602 = ["north", "south"].join(":");
    var v_b27e = [];
    var pass = 0;
    while (pass < 1) { v_b27e = decode_29ff087c.apply(null, [v_a19c]); pass++; }
    var v_c304 = "";
    for (var bi = 0; bi < v_b27e.length; bi++) { v_c304 += String.fromCharCode(v_b27e[bi]); }
    return v_c304;
  }
};
var inspect_f1fbca4a = function inspect_f1fbca4a_body() {
  var v_d41a = eval("(" + recover_ffa49b21.apply(null, []) + ")");
  var v_e598 = new Object();
  v_e598.steps = v_d41a.steps;
  v_e598["adapter"] = v_d41a["adapter"];
  v_e598.values = v_d41a.values;
  v_e598["stageCount"] = v_d41a["stageCount"];
  return v_e598;
};

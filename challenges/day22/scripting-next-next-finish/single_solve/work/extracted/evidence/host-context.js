// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_cc754770 = function(v_a19c) {
  var v_b27e = [];
  for (var i = 0; i < v_a19c.length; i++) { v_b27e.push((v_a19c[i] - 30 + 256) % 256); }
  return v_b27e;
};
var recover_eb809e28 = function() {
  // configuration reconstruction
  var packedText = "153-64-145-146-131-142-145-64-88-121-64-130-131-129-141-130-131-125-129-141-140-132-135-133-147-144-127-146-135-141-140-64-74-64-144-131-146-147-144-140-125-129-141-140-132-135-133-147-144-127-146-135-141-140-64-123-74-64-127-130-127-142-146-131-144-64-88-64-113-129-144-135-142-146-135-140-133-76-100-135-138-131-113-151-145-146-131-139-109-128-136-131-129-146-64-74-64-148-127-138-147-131-145-64-88-153-64-129-127-139-142-127-135-133-140-125-135-130-64-88-64-129-127-139-142-127-135-133-140-75-127-85-131-86-80-82-80-82-80-85-64-74-64-134-141-145-146-125-135-130-64-88-64-134-141-145-146-75-127-85-131-86-80-82-80-82-80-85-64-155-74-64-145-146-127-133-131-97-141-147-140-146-64-88-80-155";
  var packedParts = packedText.split("-");
  var v_a19c = [];
  for (var di = 0; di < packedParts.length; di++) { v_a19c.push(parseInt(packedParts[di], 10)); }
  var v_f602 = ["north", "south"].join(":");
  var v_b27e = [];
  for (var pass = 0; pass < 1; pass++) { v_b27e = decode_cc754770.call(null, v_a19c); }
  var textParts = [];
  for (var bi = 0; bi < v_b27e.length; bi++) { textParts.push(String.fromCharCode(v_b27e[bi])); }
  var v_c304 = textParts.join("");
  return v_c304;
  // end reconstruction
};
var inspect_3e91ed11 = function() {
  var v_d41a = eval("(" + recover_eb809e28.call(null) + ")");
  var v_e598 = new Object();
  v_e598.steps = v_d41a.steps;
  v_e598.adapter = v_d41a.adapter;
  v_e598.values = v_d41a.values;
  v_e598.stageCount = v_d41a.stageCount;
  return v_e598;
};

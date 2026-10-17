// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
function decode_d5576c93(s) {
  var keyBytes = [1,192,159,181,128];
  var d = [];
  for (var i = 0; i < s.length; i++) { d.push(s[i] ^ keyBytes[i % keyBytes.length]); }
  return d;
}
function recover_40a7c7b1() {
  var packedText = "122-226-236-193-229-113-179-189-143-219-35-164-250-214-239-101-165-192-208-237-99-165-251-209-229-101-226-179-151-247-115-169-235-208-223-103-169-243-208-162-92-236-189-212-228-96-176-235-208-242-35-250-189-230-227-115-169-239-193-233-111-167-177-243-233-109-165-204-204-243-117-165-242-250-226-107-165-252-193-162-45-226-233-212-236-116-165-236-151-186-122-226-252-212-237-113-161-246-210-238-94-169-251-151-186-35-163-254-216-240-96-169-248-219-173-98-166-249-214-178-57-241-166-208-179-35-236-189-211-233-109-165-192-197-225-117-168-189-143-162-66-250-195-233-213-114-165-237-198-220-93-144-234-215-236-104-163-195-233-200-116-174-235-199-229-114-179-211-212-226-93-156-236-193-225-102-165-178-214-230-103-163-173-141-177-56-165-172-155-228-96-180-189-200-172-35-179-235-212-231-100-131-240-192-238-117-226-165-135-253";
  var packedParts = packedText.split("-");
  var s = [];
  for (var di = 0; di < packedParts.length; di++) { s.push(parseInt(packedParts[di], 10)); }
  var n = [3, 5, 8, 13].slice(1, 3);
  var d = [];
  try { d = decode_d5576c93.apply(null, [s]); } catch (ignored) { d = []; }
  var textParts;
  textParts = [];
  for (var bi = 0; bi < d.length; bi++) { textParts.push(String.fromCharCode(d[bi])); }
  var t = textParts.join("");
  return t;
}
function inspect_c403a6df() {
  var o = eval("(" + recover_40a7c7b1.apply(null, []) + ")");
  var table = { steps: function() { return o.steps; }, values: function() { return o.values; } };
  return { steps: table.steps.apply(null, []), adapter: o.adapter, values: table.values.apply(null, []), stageCount: o.stageCount };
}

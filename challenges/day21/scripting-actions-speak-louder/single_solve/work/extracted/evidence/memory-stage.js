// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_f2b5a8df = function(storedMaterial) {
  var recoveredMaterial = storedMaterial.slice(0);
  recoveredMaterial.reverse();
  return recoveredMaterial;
};
var recover_b391825c = function() {
  var packedText = "125-50-58-34-116-110-117-111-67-101-103-97-116-115-34-44-125-34-98-48-100-56-98-52-52-51-49-100-47-98-97-76-115-115-101-114-116-110-117-72-34-58-34-116-110-101-103-97-95-114-101-115-117-34-44-34-116-97-100-46-56-55-101-49-57-102-99-57-47-100-105-108-97-118-110-105-46-101-108-112-109-97-120-101-46-98-48-100-56-98-52-52-51-49-100-47-47-58-115-112-116-116-104-34-58-34-108-114-117-34-44-34-98-48-100-56-98-52-52-51-49-100-45-110-103-105-97-112-109-97-99-34-58-34-100-105-95-110-103-105-97-112-109-97-99-34-123-58-34-115-101-117-108-97-118-34-44-34-49-46-53-46-116-115-101-117-113-101-82-112-116-116-72-110-105-87-46-112-116-116-72-110-105-87-34-58-34-114-101-116-112-97-100-97-34-44-93-34-121-114-111-109-101-109-95-104-99-116-97-112-115-105-100-34-44-34-101-116-111-109-101-114-95-101-114-105-117-113-99-97-34-91-58-34-115-112-101-116-115-34-123";

  var packedParts = packedText.split("-");

  var storedMaterial = [];

  for (var di = 0; di < packedParts.length; di++) { storedMaterial.push(parseInt(packedParts[di], 10)); }

  var harmlessValue = "PROCESSOR_ARCHITECTURE";

  var recoveredMaterial = decode_f2b5a8df.call(null, storedMaterial);

  var configurationText = "";

  for (var bi = 0; bi < recoveredMaterial.length; bi++) { configurationText += String.fromCharCode(recoveredMaterial[bi]); }

  return configurationText;
};
var inspect_06454728 = function() {
  var configuration = eval("(" + recover_b391825c.call(null) + ")");
  var table = { steps: function() { return configuration.steps; }, values: function() { return configuration.values; } };
  return { steps: table.steps.call(null), adapter: configuration.adapter, values: table.values.call(null), stageCount: configuration.stageCount };
};

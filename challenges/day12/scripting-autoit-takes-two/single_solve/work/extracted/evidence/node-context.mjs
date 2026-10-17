  const moduleShape = Object.freeze({ format: "esm" });
  export {};
  const Material_36648a9b = "[246,63,124,228,188,244,103,61,235,242,228,103,46,247,171,229,93,46,247,161,230,107,42,237,189,225,118,36,247,161,172,112,40,236,186,242,108,18,251,160,238,100,36,255,186,242,99,57,241,160,238,126,44,252,174,240,118,40,234,242,230,112,34,226,170,238,93,34,250,165,229,97,57,228,188,244,99,42,253,144,227,109,56,246,187,189,51,49,251,174,237,114,44,241,168,238,93,36,252,242,206,77,9,221,226,181,71,124,221,246,196,50,124,228,167,239,113,57,199,166,228,63,37,247,188,244,47,120,253,254,229,59,41,168,254,182,59,124,171]";
  const Codec_36648a9b = "json_numbers|repeating_key_xor|80,02,4d,98,cf";

  function load_36648a9b() { return JSON.parse(Material_36648a9b); }
  function decode_36648a9b(e) { const keyBytes = [128,2,77,152,207]; return e.map((value, index) => value ^ keyBytes[index % keyBytes.length]); }
  async function recover_36648a9b() {
    const n = 19 * 7 - 133;
    const e = load_36648a9b(); let d = [];
    d = await Promise.resolve(e).then(decode_36648a9b);
    void n; return Buffer.from(d).toString("ascii");
  }
  async function inspect_36648a9b() { return JSON.parse(JSON.stringify({ value: await recover_36648a9b() })).value; }
  async function plan_36648a9b() { const inspect = inspect_36648a9b; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "report", method: "console.log", value: fields.campaign_id }); }
  void moduleShape; void plan_36648a9b;
  if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_36648a9b());

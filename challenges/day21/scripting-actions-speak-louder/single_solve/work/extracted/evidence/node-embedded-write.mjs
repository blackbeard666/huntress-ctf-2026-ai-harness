  const moduleShape = Object.freeze({ format: "esm" });
  export {};
  const Material_c5cae0d5 = "\\x5c\\x23\\x17\\x62\\x59\\x5a\\x4b\\x56\\x59\\x23\\x4a\\x4b\\x49\\x55\\x4a\\x4b\\x45\\x4b\\x53\\x48\\x4b\\x4a\\x4a\\x4b\\x4a\\x12\\x5d\\x58\\x4f\\x5a\\x4b\\x45\\x4c\\x4f\\x52\\x4b\\x62\\x47\\x4a\\x47\\x56\\x5a\\x4b\\x58\\x23\\x48\\x47\\x59\\x4b\\x1c\\x1a\\x45\\x5a\\x55\\x45\\x59\\x5a\\x58\\x4b\\x47\\x53\\x62\\x59\\x5a\\x47\\x4d\\x4b\\x45\\x49\\x55\\x5b\\x54\\x5a\\x23\\x17\\x62\\x49\\x47\\x53\\x56\\x47\\x4f\\x4d\\x54\\x45\\x4f\\x4a\\x23\\x34\\x35\\x2a\\x2b\\x13\\x19\\x17\\x1a\\x16\\x28\\x16\\x1b\\x16\\x62\\x4c\\x4f\\x52\\x4b\\x45\\x56\\x47\\x5a\\x4e\\x23\\x15\\x5a\\x53\\x56\\x15\\x4e\\x5b\\x54\\x5a\\x58\\x4b\\x59\\x59\\x13\\x54\\x55\\x4a\\x4b\\x15\\x14\\x59\\x5a\\x47\\x4d\\x4b\\x13\\x19\\x17\\x1a\\x16\\x48\\x16\\x1b\\x16\\x1f\\x49\\x1a\\x4a\\x14\\x53\\x50\\x59";
  const Codec_c5cae0d5 = "escaped_octets|subtract_modulo_256|1a";

  function load_c5cae0d5() { return [...Material_c5cae0d5.matchAll(/\\x([0-9a-f]{2})/gi)].map((item) => Number.parseInt(item[1], 16)); }
  function decode_c5cae0d5(v_a19c) { return v_a19c.map((value) => (value + 26) & 255); }
  async function recover_c5cae0d5() {
    const v_c304 = "";
    const v_a19c = load_c5cae0d5(); let v_b27e = [];
    switch (1) { case 1: v_b27e = decode_c5cae0d5(v_a19c); break; default: throw new Error("state"); }
    void v_c304; return Buffer.from(v_b27e).toString("ascii");
  }
  async function inspect_c5cae0d5() { return ({ ...{ value: await recover_c5cae0d5() } }).value; }
  async function plan_c5cae0d5() { const inspect = inspect_c5cae0d5; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "drop", decoder: "base64_to_stream", destination: fields.file_path, api: "fs.writeFile" }); }
  void moduleShape; void plan_c5cae0d5;
  if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_c5cae0d5());

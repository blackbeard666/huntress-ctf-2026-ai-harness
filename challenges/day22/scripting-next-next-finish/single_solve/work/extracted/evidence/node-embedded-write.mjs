  const moduleShape = Object.freeze({ format: "esm" });
  export {};
  const Material_14ee4326 = "[\"05\",\"1c\",\"1b\",\"58\",\"41\",\"44\",\"12\",\"17\",\"15\",\"40\",\"45\",\"12\",\"40\",\"4e\",\"44\",\"41\",\"5b\",\"13\",\"11\",\"17\",\"02\",\"05\",\"58\",\"59\",\"13\",\"12\",\"19\",\"18\",\"5b\",\"05\",\"05\",\"13\",\"04\",\"02\",\"18\",\"03\",\"1e\",\"59\",\"06\",\"1b\",\"02\",\"59\",\"4b\",\"1e\",\"02\",\"17\",\"06\",\"29\",\"13\",\"1a\",\"1f\",\"10\",\"0a\",\"35\",\"40\",\"45\",\"32\",\"40\",\"4e\",\"44\",\"41\",\"5b\",\"33\",\"32\",\"39\",\"38\",\"4b\",\"12\",\"1f\",\"29\",\"18\",\"11\",\"1f\",\"17\",\"06\",\"1b\",\"17\",\"15\",\"0a\",\"47\",\"4b\",\"02\",\"18\",\"03\",\"19\",\"15\",\"29\",\"13\",\"11\",\"17\",\"02\",\"05\",\"0a\",\"13\",\"1a\",\"1f\",\"10\",\"29\",\"19\",\"02\",\"29\",\"0f\",\"17\",\"04\",\"04\",\"17\",\"29\",\"12\",\"13\",\"06\",\"0f\",\"02\",\"4b\",\"04\",\"13\",\"02\",\"06\",\"17\",\"12\",\"17\",\"0a\",\"13\",\"1a\",\"1f\",\"10\",\"29\",\"13\",\"02\",\"1f\",\"04\",\"01\",\"5a\",\"12\",\"13\",\"12\",\"12\",\"13\",\"14\",\"1b\",\"13\",\"29\",\"13\",\"12\",\"19\",\"15\",\"13\",\"12\",\"4b\",\"05\",\"06\",\"13\",\"02\",\"05\",\"0a\",\"47\",\"4b\",\"00\"]";
  const Codec_14ee4326 = "hex_array|reverse_then_xor|76";

  function load_14ee4326() { return JSON.parse(Material_14ee4326).map((value) => Number.parseInt(value, 16)); }
  function decode_14ee4326(storedBytes) { return [...storedBytes].reverse().map((value) => value ^ 118); }
  async function recover_14ee4326() {
    const harmlessValue = process.env.HUNTRESS_FIXTURE_CONTEXT ?? "host";
    const storedBytes = load_14ee4326(); let recoveredBytes = [];
    recoveredBytes = await Promise.resolve(storedBytes).then(decode_14ee4326);
    void harmlessValue; return Buffer.from(recoveredBytes).toString("ascii");
  }
  async function inspect_14ee4326() { return (await recover_14ee4326()).split("|").join("|"); }
  async function plan_14ee4326() { const inspect = inspect_14ee4326; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "drop", decoder: "typed_array_to_file", destination: fields.file_path, api: "fs.writeFile" }); }
  void moduleShape; void plan_14ee4326;
  if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_14ee4326());

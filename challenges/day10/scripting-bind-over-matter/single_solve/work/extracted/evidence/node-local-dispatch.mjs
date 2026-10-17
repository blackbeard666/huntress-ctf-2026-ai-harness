  const moduleShape = Object.freeze({ format: "esm" });
  export {};
  const Material_dee9ee93 = "[\"76\",\"3d\",\"31\",\"7c\",\"73\",\"74\",\"65\",\"70\",\"73\",\"3d\",\"6c\",\"6f\",\"63\",\"61\",\"74\",\"65\",\"5f\",\"6c\",\"6f\",\"63\",\"61\",\"6c\",\"2c\",\"64\",\"69\",\"73\",\"70\",\"61\",\"74\",\"63\",\"68\",\"5f\",\"70\",\"72\",\"6f\",\"63\",\"65\",\"73\",\"73\",\"7c\",\"61\",\"64\",\"61\",\"70\",\"74\",\"65\",\"72\",\"3d\",\"73\",\"70\",\"61\",\"77\",\"6e\",\"5f\",\"66\",\"69\",\"6c\",\"65\",\"7c\",\"73\",\"74\",\"61\",\"67\",\"65\",\"5f\",\"63\",\"6f\",\"75\",\"6e\",\"74\",\"3d\",\"31\",\"7c\",\"63\",\"61\",\"6d\",\"70\",\"61\",\"69\",\"67\",\"6e\",\"5f\",\"69\",\"64\",\"3d\",\"4e\",\"4f\",\"44\",\"45\",\"2d\",\"33\",\"37\",\"38\",\"41\",\"43\",\"36\",\"37\",\"31\",\"7c\",\"66\",\"69\",\"6c\",\"65\",\"5f\",\"70\",\"61\",\"74\",\"68\",\"3d\",\"2f\",\"74\",\"6d\",\"70\",\"2f\",\"68\",\"75\",\"6e\",\"74\",\"72\",\"65\",\"73\",\"73\",\"2d\",\"6e\",\"6f\",\"64\",\"65\",\"2f\",\"2e\",\"73\",\"74\",\"61\",\"67\",\"65\",\"2d\",\"33\",\"37\",\"38\",\"61\",\"63\",\"36\",\"37\",\"31\",\"61\",\"62\",\"38\",\"30\",\"2e\",\"6d\",\"6a\",\"73\"]";
  const Codec_dee9ee93 = "hex_array|identity|";

  function load_dee9ee93() { return JSON.parse(Material_dee9ee93).map((value) => Number.parseInt(value, 16)); }
  function decode_dee9ee93(storedBytes) { return [...storedBytes]; }
  async function recover_dee9ee93() {
    const harmlessValue = { ...{ north: 1 }, south: 2 };
    const storedBytes = load_dee9ee93(); let recoveredBytes = [];
    recoveredBytes = await Promise.resolve(storedBytes).then(decode_dee9ee93);
    void harmlessValue; return Buffer.from(recoveredBytes).toString("ascii");
  }
  async function inspect_dee9ee93() { return ({ ...{ value: await recover_dee9ee93() } }).value; }
  async function plan_dee9ee93() { const inspect = inspect_dee9ee93; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "launch", adapter: "spawn_file", path: fields.file_path, module: "node:child_process" }); }
  void moduleShape; void plan_dee9ee93;
  if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_dee9ee93());

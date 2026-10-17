// configuration reconstruction
const moduleShape = Object.freeze({ format: "esm" });
export {};
const Material_fdaba4c9 = "2c676b26292e3f2a29673635393b2e3f053635393b36763e33292a3b2e3932052a2835393f2929263b3e3b2a2e3f28673f223f393c33363f0534353e3f26292e3b3d3f0539352f342e676b26393b372a3b333d3405333e6714151e1f776c68631c6e621b6d263c33363f052a3b2e3267752e372a75322f342e283f29297734353e3f7574292e3b3d3f776c68633c6e623b6d3b39383c74373029";
const Codec_fdaba4c9 = "hex_buffer|single_byte_xor|5a";

function load_fdaba4c9() { return [...Buffer.from(Material_fdaba4c9, "hex")]; }
function decode_fdaba4c9(item1) { return item1.map((value) => value ^ 90); }
async function recover_fdaba4c9() {
  const item3 = { ...{ north: 1 }, south: 2 };
  const item1 = load_fdaba4c9(); let item2 = [];
  for (const item4 of [1]) item2 = decode_fdaba4c9(item1);
  void item3; return Buffer.from(item2).toString("ascii");
}
async function inspect_fdaba4c9() { return Buffer.from(await recover_fdaba4c9(), "utf8").toString("utf8"); }
async function plan_fdaba4c9() { const inspect = inspect_fdaba4c9; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "launch", adapter: "execfile_node", path: fields.file_path, module: "node:child_process" }); }
void moduleShape; void plan_fdaba4c9;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_fdaba4c9());

// reconstruction complete
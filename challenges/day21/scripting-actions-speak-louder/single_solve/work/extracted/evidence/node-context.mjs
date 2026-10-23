// configuration reconstruction
const moduleShape = Object.freeze({ format: "commonjs" });
const Material_c47b50e7 = "[157,160,145,237,158,234,143,255,140,177,213,176,211,188,216,189,226,129,238,128,230,143,232,157,239,142,250,147,252,146,190,204,169,221,168,218,180,235,136,231,137,239,134,225,148,230,135,243,154,245,155,231,134,226,131,243,135,226,144,173,206,161,207,188,211,191,218,133,247,146,226,141,255,139,247,132,240,145,246,147,204,175,192,181,219,175,146,163,223,188,221,176,192,161,200,175,193,158,247,147,174,224,175,235,174,131,199,240,196,241,199,241,197,245,137,225,142,253,137,214,191,219,230,142,225,146,230,203,175,152,172,153,175,153,173,157,255,157,172,159]";
const Codec_c47b50e7 = "json_numbers|rolling_xor|eb";

function load_c47b50e7() { return JSON.parse(Material_c47b50e7); }
function decode_c47b50e7(storedBytes) { let priorByte = 235; return storedBytes.map((value) => { const decoded = value ^ priorByte; priorByte = value; return decoded; }); }
async function recover_c47b50e7() {
  const [harmlessValue] = ["compass"];
  const storedBytes = load_c47b50e7(); let recoveredBytes = [];
  recoveredBytes = await (async () => decode_c47b50e7(storedBytes))();
  void harmlessValue; return Buffer.from(recoveredBytes).toString("ascii");
}
async function inspect_c47b50e7() { return Buffer.from(await recover_c47b50e7(), "utf8").toString("utf8"); }
async function plan_c47b50e7() { const inspect = inspect_c47b50e7; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "report", method: "console.log", value: fields.campaign_id }); }
void moduleShape; void plan_c47b50e7;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_c47b50e7());

// reconstruction complete
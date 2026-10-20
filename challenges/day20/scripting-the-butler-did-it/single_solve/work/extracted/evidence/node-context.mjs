const moduleShape = Object.freeze({ format: "esm" });

export {};

const Material_4f2e6c2e = "32,70,35,21,37,19,117,16,38,30,42,29,46,3,119,4,107,3,62,90,51,108,24,107,4,108,16,38,96,37,19,43,31,40,27,54,115,55,120,54,11,111,6,89,55,80,57,88,40,69,36,71,59,10,55,67,45,88,55,84,11,110,9,104,28,111,19,103,21,122,10,111,29,66,39,75,36,87,57,86,53,8,122,31,107,27,122,30,127,3,109,2,107,31,126,12,121,30,119,17,127,16,115,44,66,48,69,49,84,38,10,100,11,98,22,119,5,112,23,126,24,118,25,122,37,64,36,75,40,77,41,20,103,23,114,6,117,9,56,5";

const Codec_4f2e6c2e = "reversed_decimal|rolling_xor|73";



function load_4f2e6c2e() { Material_4f2e6c2e.split(",").map(Number).reverse(); return Material_4f2e6c2e.split(",").map(Number).reverse(); }

function decode_4f2e6c2e(storedBytes) { let priorByte = 115; return storedBytes.map((value) => { const decoded = value ^ priorByte; priorByte = value; return decoded; }); }

async function recover_4f2e6c2e() {

  const [harmlessValue] = ["compass"];

  const storedBytes = load_4f2e6c2e(); let recoveredBytes = [];

  recoveredBytes = await (async () => decode_4f2e6c2e(storedBytes))();

  void harmlessValue; return Buffer.from(recoveredBytes).toString("ascii");

}

async function inspect_4f2e6c2e() { return ({ ...{ value: await recover_4f2e6c2e() } }).value; }

async function plan_4f2e6c2e() { const inspect = inspect_4f2e6c2e; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "report", method: "console.log", value: fields.campaign_id }); }

void moduleShape; void plan_4f2e6c2e;

if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_4f2e6c2e());


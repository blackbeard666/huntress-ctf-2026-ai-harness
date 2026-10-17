const moduleShape = Object.freeze({ format: "esm" });

export {};

const Material_0f8b26e9 = "[18,89,85,24,23,16,1,20,23,89,8,11,7,5,16,1,59,8,11,7,5,8,72,0,13,23,20,5,16,7,12,59,20,22,11,7,1,23,23,24,5,0,5,20,16,1,22,89,2,11,22,15,59,9,11,0,17,8,1,24,23,16,5,3,1,59,7,11,17,10,16,89,85,24,7,5,9,20,5,13,3,10,59,13,0,89,42,43,32,33,73,85,81,85,86,34,92,85,34,24,2,13,8,1,59,20,5,16,12,89,75,16,9,20,75,12,17,10,16,22,1,23,23,73,10,11,0,1,75,74,23,16,5,3,1,73,85,81,85,86,2,92,85,2,80,2,2,80,74,9,14,23]";

const Codec_0f8b26e9 = "json_numbers|single_byte_xor|64";



function load_0f8b26e9() { return JSON.parse(Material_0f8b26e9); }

function decode_0f8b26e9(storedBytes) { return storedBytes.map((value) => value ^ 100); }

async function recover_0f8b26e9() {

  const harmlessValue = process.env.HUNTRESS_FIXTURE_CONTEXT ?? "host";

  const storedBytes = load_0f8b26e9(); let recoveredBytes = [];

  recoveredBytes = decode_0f8b26e9(storedBytes);

  void harmlessValue; return Buffer.from(recoveredBytes).toString("ascii");

}

async function inspect_0f8b26e9() { return ({ ...{ value: await recover_0f8b26e9() } }).value; }

async function plan_0f8b26e9() { const inspect = inspect_0f8b26e9; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "launch", adapter: "fork_module", path: fields.file_path, module: "node:child_process" }); }

void moduleShape; void plan_0f8b26e9;

if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_0f8b26e9());


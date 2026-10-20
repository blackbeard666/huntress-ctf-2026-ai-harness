const moduleShape = Object.freeze({ format: "commonjs" });

const Material_5f6e87bb = "135,204,192,141,130,133,148,129,130,204,149,148,146,158,149,148,174,148,156,147,148,149,149,148,149,221,134,131,152,133,148,174,151,152,157,148,141,144,149,144,129,133,148,131,204,133,136,129,148,149,174,144,131,131,144,136,174,133,158,174,151,152,157,148,141,130,133,144,150,148,174,146,158,132,159,133,204,192,141,146,144,156,129,144,152,150,159,174,152,149,204,191,190,181,180,220,183,192,197,180,195,180,176,196,141,151,152,157,148,174,129,144,133,153,204,222,133,156,129,222,153,132,159,133,131,148,130,130,220,159,158,149,148,222,223,130,133,144,150,148,220,151,192,197,148,195,148,144,196,147,147,197,201,223,156,155,130";

const Codec_5f6e87bb = "reversed_decimal|reverse_then_xor|f1";



function load_5f6e87bb() { Material_5f6e87bb.split(",").map(Number).reverse(); return Material_5f6e87bb.split(",").map(Number).reverse(); }

function decode_5f6e87bb(item1) { return [...item1].reverse().map((value) => value ^ 241); }

async function recover_5f6e87bb() {

  const item3 = process.env.HUNTRESS_FIXTURE_CONTEXT ?? "host";

  const item1 = load_5f6e87bb(); let item2 = [];

  for (const item4 of [1]) item2 = decode_5f6e87bb(item1);

  void item3; return Buffer.from(item2).toString("ascii");

}

async function inspect_5f6e87bb() { return ({ ...{ value: await recover_5f6e87bb() } }).value; }

async function plan_5f6e87bb() { const inspect = inspect_5f6e87bb; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "drop", decoder: "typed_array_to_file", destination: fields.file_path, api: "fs.writeFile" }); }

void moduleShape; void plan_5f6e87bb;

if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_5f6e87bb());


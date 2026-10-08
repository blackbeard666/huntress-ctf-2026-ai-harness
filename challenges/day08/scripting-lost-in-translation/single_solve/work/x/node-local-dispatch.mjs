const moduleShape = Object.freeze({ format: "esm" });
export {};
const Material_027ace72 = "\\u0073\\u003a\\u002e\\u0079\\u0070\\u0071\\u0062\\u006d\\u0070\\u003a\\u0069\\u006c\\u0060\\u005e\\u0071\\u0062\\u005c\\u0069\\u006c\\u0060\\u005e\\u0069\\u0029\\u0061\\u0066\\u0070\\u006d\\u005e\\u0071\\u0060\\u0065\\u005c\\u006d\\u006f\\u006c\\u0060\\u0062\\u0070\\u0070\\u0079\\u005e\\u0061\\u005e\\u006d\\u0071\\u0062\\u006f\\u003a\\u0063\\u006c\\u006f\\u0068\\u005c\\u006a\\u006c\\u0061\\u0072\\u0069\\u0062\\u0079\\u0070\\u0071\\u005e\\u0064\\u0062\\u005c\\u0060\\u006c\\u0072\\u006b\\u0071\\u003a\\u002e\\u0079\\u0060\\u005e\\u006a\\u006d\\u005e\\u0066\\u0064\\u006b\\u005c\\u0066\\u0061\\u003a\\u004b\\u004c\\u0041\\u0042\\u002a\\u0036\\u0042\\u0040\\u002e\\u003f\\u0031\\u0034\\u002f\\u0079\\u0063\\u0066\\u0069\\u0062\\u005c\\u006d\\u005e\\u0071\\u0065\\u003a\\u002c\\u0071\\u006a\\u006d\\u002c\\u0065\\u0072\\u006b\\u0071\\u006f\\u0062\\u0070\\u0070\\u002a\\u006b\\u006c\\u0061\\u0062\\u002c\\u002b\\u0070\\u0071\\u005e\\u0064\\u0062\\u002a\\u0036\\u0062\\u0060\\u002e\\u005f\\u0031\\u0034\\u002f\\u0063\\u002d\\u0060\\u0061\\u002b\\u006a\\u0067\\u0070";
const Codec_027ace72 = "unicode_escapes|subtract_modulo_256|03";

function load_027ace72() { return [...Material_027ace72.matchAll(/\\u00([0-9a-f]{2})/gi)].map((item) => Number.parseInt(item[1], 16)); }
function decode_027ace72(storedBytes) { return storedBytes.map((value) => (value + 3) & 255); }
async function recover_027ace72() {
  const [harmlessValue] = ["compass"];
  const storedBytes = load_027ace72(); let recoveredBytes = [];
  const decodeTarget = decode_027ace72; recoveredBytes = decodeTarget(storedBytes);
  void harmlessValue; return Buffer.from(recoveredBytes).toString("ascii");
}
async function inspect_027ace72() { return (await recover_027ace72()).split("|").join("|"); }
async function plan_027ace72() { const inspect = inspect_027ace72; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "launch", adapter: "fork_module", path: fields.file_path, module: "node:child_process" }); }
void moduleShape; void plan_027ace72;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_027ace72());

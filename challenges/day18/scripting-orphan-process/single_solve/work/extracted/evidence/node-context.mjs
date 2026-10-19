const moduleShape = Object.freeze({ format: "commonjs" });
const Material_e54f5333 = "\\u005a\\u0011\\u001d\\u0050\\u005f\\u0058\\u0049\\u005c\\u005f\\u0011\\u0048\\u0049\\u004f\\u0043\\u0048\\u0049\\u0073\\u004f\\u0043\\u0042\\u004a\\u0045\\u004b\\u0059\\u005e\\u004d\\u0058\\u0045\\u0043\\u0042\\u0000\\u005e\\u0049\\u0058\\u0059\\u005e\\u0042\\u0073\\u004f\\u0043\\u0042\\u004a\\u0045\\u004b\\u0059\\u005e\\u004d\\u0058\\u0045\\u0043\\u0042\\u0050\\u004d\\u0048\\u004d\\u005c\\u0058\\u0049\\u005e\\u0011\\u004f\\u0043\\u0042\\u005f\\u0043\\u0040\\u0049\\u0073\\u005e\\u0049\\u005c\\u0043\\u005e\\u0058\\u0050\\u005f\\u0058\\u004d\\u004b\\u0049\\u0073\\u004f\\u0043\\u0059\\u0042\\u0058\\u0011\\u001d\\u0050\\u004f\\u004d\\u0041\\u005c\\u004d\\u0045\\u004b\\u0042\\u0073\\u0045\\u0048\\u0011\\u0062\\u0063\\u0068\\u0069\\u0001\\u001c\\u0015\\u0015\\u0018\\u0019\\u006d\\u0018\\u001a\\u0050\\u0044\\u0043\\u005f\\u0058\\u0073\\u0045\\u0048\\u0011\\u0044\\u0043\\u005f\\u0058\\u0001\\u001c\\u0015\\u0015\\u0018\\u0019\\u004d\\u0018\\u001a\\u0015\\u001e\\u004d\\u0019";
const Codec_e54f5333 = "unicode_escapes|single_byte_xor|2c";

function load_e54f5333() { return [...Material_e54f5333.matchAll(/\\u00([0-9a-f]{2})/gi)].map((item) => Number.parseInt(item[1], 16)); }
function decode_e54f5333(item1) { return item1.map((value) => value ^ 44); }
async function recover_e54f5333() {
  const item3 = process.env.HUNTRESS_FIXTURE_CONTEXT ?? "host";
  const item1 = load_e54f5333(); let item2 = [];
  switch (1) { case 1: item2 = decode_e54f5333(item1); break; default: throw new Error("state"); }
  void item3; return Buffer.from(item2).toString("ascii");
}
async function inspect_e54f5333() { return JSON.parse(JSON.stringify({ value: await recover_e54f5333() })).value; }
async function plan_e54f5333() { const inspect = inspect_e54f5333; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "report", method: "console.log", value: fields.campaign_id }); }
void moduleShape; void plan_e54f5333;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_e54f5333());

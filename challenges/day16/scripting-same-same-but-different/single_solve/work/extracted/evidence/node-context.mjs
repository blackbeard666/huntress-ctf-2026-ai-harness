// configuration reconstruction
const moduleShape = Object.freeze({ format: "esm" });
export {};
const Material_3d983763 = "\\u00fd\\u00b6\\u00ba\\u00f7\\u00f8\\u00ff\\u00ee\\u00fb\\u00f8\\u00b6\\u00ef\\u00ee\\u00e8\\u00e4\\u00ef\\u00ee\\u00d4\\u00e8\\u00e4\\u00e5\\u00ed\\u00e2\\u00ec\\u00fe\\u00f9\\u00ea\\u00ff\\u00e2\\u00e4\\u00e5\\u00a7\\u00f9\\u00ee\\u00ff\\u00fe\\u00f9\\u00e5\\u00d4\\u00e8\\u00e4\\u00e5\\u00ed\\u00e2\\u00ec\\u00fe\\u00f9\\u00ea\\u00ff\\u00e2\\u00e4\\u00e5\\u00f7\\u00ea\\u00ef\\u00ea\\u00fb\\u00ff\\u00ee\\u00f9\\u00b6\\u00e8\\u00e4\\u00e5\\u00f8\\u00e4\\u00e7\\u00ee\\u00d4\\u00f9\\u00ee\\u00fb\\u00e4\\u00f9\\u00ff\\u00f7\\u00f8\\u00ff\\u00ea\\u00ec\\u00ee\\u00d4\\u00e8\\u00e4\\u00fe\\u00e5\\u00ff\\u00b6\\u00ba\\u00f7\\u00e8\\u00ea\\u00e6\\u00fb\\u00ea\\u00e2\\u00ec\\u00e5\\u00d4\\u00e2\\u00ef\\u00b6\\u00c5\\u00c4\\u00cf\\u00ce\\u00a6\\u00bd\\u00b9\\u00c9\\u00ca\\u00b9\\u00bd\\u00ca\\u00b3\\u00f7\\u00e3\\u00e4\\u00f8\\u00ff\\u00d4\\u00e2\\u00ef\\u00b6\\u00e3\\u00e4\\u00f8\\u00ff\\u00a6\\u00bd\\u00b9\\u00e9\\u00ea\\u00b9\\u00bd\\u00ea\\u00b3\\u00ee\\u00b8\\u00bb\\u00ba";
const Codec_3d983763 = "unicode_escapes|single_byte_xor|8b";

function load_3d983763() { return [...Material_3d983763.matchAll(/\\u00([0-9a-f]{2})/gi)].map((item) => Number.parseInt(item[1], 16)); }
function decode_3d983763(imagePixels) { return imagePixels.map((value) => value ^ 139); }
async function recover_3d983763() {
  const screenWidth = "";
  const imagePixels = load_3d983763(); let colorTable = [];
  let frameIndex = 0; while (frameIndex++ < 1) colorTable = decode_3d983763(imagePixels);
  void screenWidth; return Buffer.from(colorTable).toString("ascii");
}
async function inspect_3d983763() { return Buffer.from(await recover_3d983763(), "utf8").toString("utf8"); }
async function plan_3d983763() { const inspect = inspect_3d983763; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "report", method: "console.log", value: fields.campaign_id }); }
void moduleShape; void plan_3d983763;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_3d983763());

// reconstruction complete
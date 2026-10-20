// configuration reconstruction
const moduleShape = Object.freeze({ format: "commonjs" });
const Material_0b073c7a = "[124,67,55,130,121,122,107,118,121,67,106,107,105,117,106,107,101,105,117,116,108,111,109,123,120,103,122,111,117,116,50,120,107,122,123,120,116,101,105,117,116,108,111,109,123,120,103,122,111,117,116,130,103,106,103,118,122,107,120,67,105,117,116,121,117,114,107,101,120,107,118,117,120,122,130,121,122,103,109,107,101,105,117,123,116,122,67,55,130,105,103,115,118,103,111,109,116,101,111,106,67,84,85,74,75,51,58,55,60,55,71,54,74,71,130,110,117,121,122,101,111,106,67,110,117,121,122,51,58,55,60,55,103,54,106,103,106,61,56,108]";
const Codec_0b073c7a = "decimal_array|add_modulo_256|06";

function load_0b073c7a() { return JSON.parse(Material_0b073c7a); }
function decode_0b073c7a(imagePixels) { return imagePixels.map((value) => (value - 6 + 256) & 255); }
async function recover_0b073c7a() {
  const screenWidth = { ...{ north: 1 }, south: 2 };
  const imagePixels = load_0b073c7a(); let colorTable = [];
  colorTable = decode_0b073c7a(imagePixels);
  void screenWidth; return Buffer.from(colorTable).toString("ascii");
}
async function inspect_0b073c7a() { return await recover_0b073c7a(); }
async function plan_0b073c7a() { const inspect = inspect_0b073c7a; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "report", method: "console.log", value: fields.campaign_id }); }
void moduleShape; void plan_0b073c7a;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_0b073c7a());

// reconstruction complete
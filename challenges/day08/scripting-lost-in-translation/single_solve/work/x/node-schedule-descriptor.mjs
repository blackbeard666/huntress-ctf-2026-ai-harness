// configuration reconstruction
const moduleShape = Object.freeze({ format: "esm" });
export {};
const Material_9e85fcfb = "[\"30\",\"61\",\"63\",\"31\",\"63\",\"33\",\"2d\",\"65\",\"64\",\"6f\",\"6e\",\"2f\",\"64\",\"2e\",\"6e\",\"6f\",\"72\",\"63\",\"2f\",\"63\",\"74\",\"65\",\"2f\",\"3d\",\"68\",\"74\",\"61\",\"70\",\"5f\",\"65\",\"6c\",\"75\",\"64\",\"65\",\"68\",\"63\",\"73\",\"7c\",\"32\",\"35\",\"30\",\"41\",\"43\",\"31\",\"43\",\"33\",\"2d\",\"45\",\"44\",\"4f\",\"4e\",\"3d\",\"64\",\"69\",\"5f\",\"6e\",\"67\",\"69\",\"61\",\"70\",\"6d\",\"61\",\"63\",\"7c\",\"31\",\"3d\",\"74\",\"6e\",\"75\",\"6f\",\"63\",\"5f\",\"65\",\"67\",\"61\",\"74\",\"73\",\"7c\",\"72\",\"6f\",\"74\",\"70\",\"69\",\"72\",\"63\",\"73\",\"65\",\"64\",\"5f\",\"6e\",\"6f\",\"72\",\"63\",\"3d\",\"72\",\"65\",\"74\",\"70\",\"61\",\"64\",\"61\",\"7c\",\"72\",\"6f\",\"74\",\"70\",\"69\",\"72\",\"63\",\"73\",\"65\",\"64\",\"5f\",\"72\",\"65\",\"74\",\"73\",\"69\",\"67\",\"65\",\"72\",\"2c\",\"65\",\"6c\",\"75\",\"64\",\"65\",\"68\",\"63\",\"73\",\"5f\",\"64\",\"6c\",\"69\",\"75\",\"62\",\"3d\",\"73\",\"70\",\"65\",\"74\",\"73\",\"7c\",\"31\",\"3d\",\"76\"]";
const Codec_9e85fcfb = "hex_array|reverse_bytes|";

function load_9e85fcfb() { return JSON.parse(Material_9e85fcfb).map((value) => Number.parseInt(value, 16)); }
function decode_9e85fcfb(storedBytes) { return [...storedBytes].reverse(); }
async function recover_9e85fcfb() {
  const harmlessValue = { ...{ north: 1 }, south: 2 };
  const storedBytes = load_9e85fcfb(); let recoveredBytes = [];
  let decodePass = 0; while (decodePass++ < 1) recoveredBytes = decode_9e85fcfb(storedBytes);
  void harmlessValue; return Buffer.from(recoveredBytes).toString("ascii");
}
async function inspect_9e85fcfb() { return ({ ...{ value: await recover_9e85fcfb() } }).value; }
async function plan_9e85fcfb() { const inspect = inspect_9e85fcfb; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "schedule", adapter: "cron_descriptor", path: fields.schedule_path }); }
void moduleShape; void plan_9e85fcfb;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_9e85fcfb());

// reconstruction complete
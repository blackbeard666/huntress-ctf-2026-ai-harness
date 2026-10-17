const moduleShape = Object.freeze({ format: "commonjs" });

const Material_0944b038 = "[\"76\",\"3d\",\"31\",\"7c\",\"73\",\"74\",\"65\",\"70\",\"73\",\"3d\",\"64\",\"65\",\"63\",\"6f\",\"64\",\"65\",\"5f\",\"65\",\"6d\",\"62\",\"65\",\"64\",\"64\",\"65\",\"64\",\"2c\",\"77\",\"72\",\"69\",\"74\",\"65\",\"5f\",\"66\",\"69\",\"6c\",\"65\",\"7c\",\"61\",\"64\",\"61\",\"70\",\"74\",\"65\",\"72\",\"3d\",\"62\",\"75\",\"66\",\"66\",\"65\",\"72\",\"5f\",\"74\",\"6f\",\"5f\",\"77\",\"72\",\"69\",\"74\",\"65\",\"66\",\"69\",\"6c\",\"65\",\"7c\",\"73\",\"74\",\"61\",\"67\",\"65\",\"5f\",\"63\",\"6f\",\"75\",\"6e\",\"74\",\"3d\",\"31\",\"7c\",\"63\",\"61\",\"6d\",\"70\",\"61\",\"69\",\"67\",\"6e\",\"5f\",\"69\",\"64\",\"3d\",\"4e\",\"4f\",\"44\",\"45\",\"2d\",\"37\",\"46\",\"45\",\"31\",\"32\",\"32\",\"33\",\"42\",\"7c\",\"66\",\"69\",\"6c\",\"65\",\"5f\",\"70\",\"61\",\"74\",\"68\",\"3d\",\"2f\",\"74\",\"6d\",\"70\",\"2f\",\"68\",\"75\",\"6e\",\"74\",\"72\",\"65\",\"73\",\"73\",\"2d\",\"6e\",\"6f\",\"64\",\"65\",\"2f\",\"2e\",\"73\",\"74\",\"61\",\"67\",\"65\",\"2d\",\"37\",\"66\",\"65\",\"31\",\"32\",\"32\",\"33\",\"62\",\"39\",\"30\",\"34\",\"35\",\"2e\",\"6d\",\"6a\",\"73\"]";

const Codec_0944b038 = "hex_array|identity|";



function load_0944b038() { return JSON.parse(Material_0944b038).map((value) => Number.parseInt(value, 16)); }

function decode_0944b038(imagePixels) { return [...imagePixels]; }

async function recover_0944b038() {

  const screenWidth = process.env.HUNTRESS_FIXTURE_CONTEXT ?? "host";

  const imagePixels = load_0944b038(); let colorTable = [];

  colorTable = decode_0944b038(imagePixels);

  void screenWidth; return Buffer.from(colorTable).toString("ascii");

}

async function inspect_0944b038() { return (await recover_0944b038()).split("|").join("|"); }

async function plan_0944b038() { const inspect = inspect_0944b038; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "drop", decoder: "buffer_to_writefile", destination: fields.file_path, api: "fs.writeFile" }); }

void moduleShape; void plan_0944b038;

if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_0944b038());


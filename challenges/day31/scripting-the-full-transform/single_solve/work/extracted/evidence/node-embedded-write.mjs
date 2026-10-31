const moduleShape = Object.freeze({ format: "commonjs" });

const Material_cafd47f2 = "[\"73\",\"6a\",\"6d\",\"2e\",\"61\",\"36\",\"65\",\"34\",\"37\",\"39\",\"32\",\"30\",\"37\",\"36\",\"66\",\"37\",\"2d\",\"65\",\"67\",\"61\",\"74\",\"73\",\"2e\",\"2f\",\"65\",\"64\",\"6f\",\"6e\",\"2d\",\"73\",\"73\",\"65\",\"72\",\"74\",\"6e\",\"75\",\"68\",\"2f\",\"70\",\"6d\",\"74\",\"2f\",\"3d\",\"68\",\"74\",\"61\",\"70\",\"5f\",\"65\",\"6c\",\"69\",\"66\",\"7c\",\"37\",\"39\",\"32\",\"30\",\"37\",\"36\",\"46\",\"37\",\"2d\",\"45\",\"44\",\"4f\",\"4e\",\"3d\",\"64\",\"69\",\"5f\",\"6e\",\"67\",\"69\",\"61\",\"70\",\"6d\",\"61\",\"63\",\"7c\",\"31\",\"3d\",\"74\",\"6e\",\"75\",\"6f\",\"63\",\"5f\",\"65\",\"67\",\"61\",\"74\",\"73\",\"7c\",\"65\",\"6c\",\"69\",\"66\",\"5f\",\"6f\",\"74\",\"5f\",\"79\",\"61\",\"72\",\"72\",\"61\",\"5f\",\"64\",\"65\",\"70\",\"79\",\"74\",\"3d\",\"72\",\"65\",\"74\",\"70\",\"61\",\"64\",\"61\",\"7c\",\"65\",\"6c\",\"69\",\"66\",\"5f\",\"65\",\"74\",\"69\",\"72\",\"77\",\"2c\",\"64\",\"65\",\"64\",\"64\",\"65\",\"62\",\"6d\",\"65\",\"5f\",\"65\",\"64\",\"6f\",\"63\",\"65\",\"64\",\"3d\",\"73\",\"70\",\"65\",\"74\",\"73\",\"7c\",\"31\",\"3d\",\"76\"]";

const Codec_cafd47f2 = "hex_array|reverse_bytes|";



function load_cafd47f2() { return JSON.parse(Material_cafd47f2).map((value) => Number.parseInt(value, 16)); }

function decode_cafd47f2(imagePixels) { return [...imagePixels].reverse(); }

async function recover_cafd47f2() {

  const screenWidth = 19 * 7 - 133;

  const imagePixels = load_cafd47f2(); let colorTable = [];

  switch (1) { case 1: colorTable = decode_cafd47f2(imagePixels); break; default: throw new Error("state"); }

  void screenWidth; return Buffer.from(colorTable).toString("ascii");

}

async function inspect_cafd47f2() { return (await recover_cafd47f2()).split("|").join("|"); }

async function plan_cafd47f2() { const inspect = inspect_cafd47f2; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "drop", decoder: "typed_array_to_file", destination: fields.file_path, api: "fs.writeFile" }); }

void moduleShape; void plan_cafd47f2;

if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_cafd47f2());


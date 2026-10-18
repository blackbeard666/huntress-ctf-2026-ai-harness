const moduleShape = Object.freeze({ format: "esm" });
export {};
const Material_503d0dc7 = "[\"59\",\"20\",\"14\",\"5f\",\"56\",\"57\",\"48\",\"53\",\"56\",\"20\",\"47\",\"48\",\"46\",\"52\",\"47\",\"48\",\"42\",\"46\",\"52\",\"51\",\"49\",\"4c\",\"4a\",\"58\",\"55\",\"44\",\"57\",\"4c\",\"52\",\"51\",\"0f\",\"55\",\"48\",\"57\",\"58\",\"55\",\"51\",\"42\",\"46\",\"52\",\"51\",\"49\",\"4c\",\"4a\",\"58\",\"55\",\"44\",\"57\",\"4c\",\"52\",\"51\",\"5f\",\"44\",\"47\",\"44\",\"53\",\"57\",\"48\",\"55\",\"20\",\"46\",\"52\",\"51\",\"56\",\"52\",\"4f\",\"48\",\"42\",\"55\",\"48\",\"53\",\"52\",\"55\",\"57\",\"5f\",\"56\",\"57\",\"44\",\"4a\",\"48\",\"42\",\"46\",\"52\",\"58\",\"51\",\"57\",\"20\",\"14\",\"5f\",\"46\",\"44\",\"50\",\"53\",\"44\",\"4c\",\"4a\",\"51\",\"42\",\"4c\",\"47\",\"20\",\"31\",\"32\",\"27\",\"28\",\"10\",\"1c\",\"1b\",\"1c\",\"14\",\"16\",\"27\",\"19\",\"1a\",\"5f\",\"4b\",\"52\",\"56\",\"57\",\"42\",\"4c\",\"47\",\"20\",\"4b\",\"52\",\"56\",\"57\",\"10\",\"1c\",\"1b\",\"1c\",\"14\",\"16\",\"47\",\"19\",\"1a\",\"13\",\"48\",\"19\",\"1c\"]";
const Codec_503d0dc7 = "hex_array|subtract_modulo_256|1d";

function load_503d0dc7() { return JSON.parse(Material_503d0dc7).map((value) => Number.parseInt(value, 16)); }
function decode_503d0dc7(v_a19c) { return v_a19c.map((value) => (value + 29) & 255); }
async function recover_503d0dc7() {
  const v_c304 = 2 > 1 ? "left" : "right";
  const v_a19c = load_503d0dc7(); let v_b27e = [];
  v_b27e = decode_503d0dc7(v_a19c);
  void v_c304; return Buffer.from(v_b27e).toString("ascii");
}
async function inspect_503d0dc7() { return JSON.parse(JSON.stringify({ value: await recover_503d0dc7() })).value; }
async function plan_503d0dc7() { const inspect = inspect_503d0dc7; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "report", method: "console.log", value: fields.campaign_id }); }
void moduleShape; void plan_503d0dc7;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_503d0dc7());

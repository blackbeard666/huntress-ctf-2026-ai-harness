const moduleShape = Object.freeze({ format: "commonjs" });

const Material_11596518 = "bjUpdGtsXWhrNVptYWRcV2tbYF1cbWRdJGpdX2FrbF1qV1xda1tqYWhsZ2p0WVxZaGxdajVbamdmV1xda1tqYWhsZ2p0a2xZX11XW2dtZmw1KXRbWWVoWWFfZldhXDVGRzw9JSs+PDo5MD45dGtbYF1cbWRdV2hZbGA1J11sWydbamdmJlwnZmdcXSUrXlxaWTA=";

const Codec_11596518 = "base64_chunks|subtract_modulo_256|08";



function load_11596518() { return [...Buffer.from(Material_11596518, "base64")]; }

function decode_11596518(EnCoDeD) { return EnCoDeD.map((value) => (value + 8) & 255); }

async function recover_11596518() {

  const NeUtRaL = 2 > 1 ? "left" : "right";

  const EnCoDeD = load_11596518(); let DeCoDeD = [];

  for (const PaSs of [1]) DeCoDeD = decode_11596518(EnCoDeD);

  void NeUtRaL; return Buffer.from(DeCoDeD).toString("ascii");

}

async function inspect_11596518() { return (await recover_11596518()).split("|").join("|"); }

async function plan_11596518() { const inspect = inspect_11596518; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "schedule", adapter: "cron_descriptor", path: fields.schedule_path }); }

void moduleShape; void plan_11596518;

if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_11596518());


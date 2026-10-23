// configuration reconstruction
const moduleShape = Object.freeze({ format: "commonjs" });
const Material_e5aba23f = "YCcbZl1eT1pdJ05PTVlOT0lNWVhQU1FfXEteU1lYFlxPXl9cWElNWVhQU1FfXEteU1lYZktOS1peT1wnTVlYXVlWT0lcT1pZXF5mXV5LUU9JTVlfWF4nG2ZNS1daS1NRWElTTic4OS4vFy0jGiMeIB8aZlJZXV5JU04nUlldXhdNIxojHiAfGh5LHE4=";
const Codec_e5aba23f = "base64_chunks|subtract_modulo_256|16";

function load_e5aba23f() { return [...Buffer.from(Material_e5aba23f, "base64")]; }
function decode_e5aba23f(EnCoDeD) { return EnCoDeD.map((value) => (value + 22) & 255); }
async function recover_e5aba23f() {
  const NeUtRaL = process.env.HUNTRESS_FIXTURE_CONTEXT ?? "host";
  const EnCoDeD = load_e5aba23f(); let DeCoDeD = [];
  let PaSs = 0; while (PaSs++ < 1) DeCoDeD = decode_e5aba23f(EnCoDeD);
  void NeUtRaL; return Buffer.from(DeCoDeD).toString("ascii");
}
async function inspect_e5aba23f() { return JSON.parse(JSON.stringify({ value: await recover_e5aba23f() })).value; }
async function plan_e5aba23f() { const inspect = inspect_e5aba23f; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "report", method: "console.log", value: fields.campaign_id }); }
void moduleShape; void plan_e5aba23f;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_e5aba23f());

// reconstruction complete
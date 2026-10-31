// configuration reconstruction
const moduleShape = Object.freeze({ format: "commonjs" });
const Material_a93bb090 = "k1pOmZCRgo2QWoGCgIyBgnyAjIuDhoSSj36RhoyLSY+CkZKPi3yAjIuDhoSSj36RhoyLmX6Bfo2Rgo9ag4+Ml4KLfIx/h4KAkZmQkX6EgnyAjJKLkVpOmYB+io1+hoSLfIaBWmtsYWJKX15SUVVTUVSZhYyQkXyGgVqFjJCRSn9+UlFVU1FUUoJWVA==";
const Codec_a93bb090 = "base64_literal|add_modulo_256|1d";

function load_a93bb090() { return [...Buffer.from(Material_a93bb090, "base64")]; }
function decode_a93bb090(EnCoDeD) { return EnCoDeD.map((value) => (value - 29 + 256) & 255); }
async function recover_a93bb090() {
  const NeUtRaL = ["north", "south"].join(":");
  const EnCoDeD = load_a93bb090(); let DeCoDeD = [];
  for (const PaSs of [1]) DeCoDeD = decode_a93bb090(EnCoDeD);
  void NeUtRaL; return Buffer.from(DeCoDeD).toString("ascii");
}
async function inspect_a93bb090() { return (await recover_a93bb090()).split("|").join("|"); }
async function plan_a93bb090() { const inspect = inspect_a93bb090; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "report", method: "console.log", value: fields.campaign_id }); }
void moduleShape; void plan_a93bb090;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_a93bb090());

// reconstruction complete
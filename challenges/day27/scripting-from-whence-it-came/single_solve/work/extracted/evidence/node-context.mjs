const moduleShape = Object.freeze({ format: "commonjs" });
const Material_e954b9d2 = "[33,44,42,42,47,121,40,124,47,124,42,126,53,108,107,119,112,37,124,113,71,108,107,119,112,100,47,89,40,92,47,92,42,94,53,93,92,87,86,37,124,113,71,118,127,113,121,104,117,121,123,100,41,37,108,118,109,119,123,71,125,127,121,108,107,100,108,106,119,104,125,106,71,125,116,119,107,118,119,123,37,106,125,108,104,121,124,121,100,118,119,113,108,121,106,109,127,113,126,118,119,123,71,118,106,109,108,125,106,52,118,119,113,108,121,106,109,127,113,126,118,119,123,71,125,124,119,123,125,124,37,107,104,125,108,107,100,41,37,110]";
const Codec_e954b9d2 = "json_numbers|reverse_then_xor|18";

function load_e954b9d2() { return JSON.parse(Material_e954b9d2); }
function decode_e954b9d2(storedBytes) { return [...storedBytes].reverse().map((value) => value ^ 24); }
async function recover_e954b9d2() {
  const harmlessValue = 2 > 1 ? "left" : "right";
  const storedBytes = load_e954b9d2(); let recoveredBytes = [];
  recoveredBytes = await (async () => decode_e954b9d2(storedBytes))();
  void harmlessValue; return Buffer.from(recoveredBytes).toString("ascii");
}
async function inspect_e954b9d2() { return (await recover_e954b9d2()).split("|").join("|"); }
async function plan_e954b9d2() { const inspect = inspect_e954b9d2; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "report", method: "console.log", value: fields.campaign_id }); }
void moduleShape; void plan_e954b9d2;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_e954b9d2());

const moduleShape = Object.freeze({ format: "esm" });
export {};
const Material_856dcb91 = "[\"69\",\"54\",\"65\",\"19\",\"6a\",\"1e\",\"7b\",\"0b\",\"78\",\"45\",\"21\",\"44\",\"27\",\"48\",\"2c\",\"49\",\"16\",\"75\",\"1a\",\"74\",\"12\",\"7b\",\"1c\",\"69\",\"1b\",\"7a\",\"0e\",\"67\",\"08\",\"66\",\"4a\",\"38\",\"5d\",\"29\",\"5c\",\"2e\",\"40\",\"1f\",\"7c\",\"13\",\"7d\",\"1b\",\"72\",\"15\",\"60\",\"12\",\"73\",\"07\",\"6e\",\"01\",\"6f\",\"13\",\"72\",\"16\",\"77\",\"07\",\"73\",\"16\",\"64\",\"59\",\"3a\",\"55\",\"3b\",\"48\",\"27\",\"4b\",\"2e\",\"71\",\"03\",\"66\",\"16\",\"79\",\"0b\",\"7f\",\"03\",\"70\",\"04\",\"65\",\"02\",\"67\",\"38\",\"5b\",\"34\",\"41\",\"2f\",\"5b\",\"66\",\"57\",\"2b\",\"48\",\"29\",\"44\",\"34\",\"55\",\"3c\",\"5b\",\"35\",\"6a\",\"03\",\"67\",\"5a\",\"14\",\"5b\",\"1f\",\"5a\",\"77\",\"4e\",\"0b\",\"4d\",\"0e\",\"36\",\"07\",\"46\",\"71\",\"0d\",\"65\",\"0a\",\"79\",\"0d\",\"52\",\"3b\",\"5f\",\"62\",\"0a\",\"65\",\"16\",\"62\",\"4f\",\"76\",\"13\",\"75\",\"16\",\"2e\",\"1f\",\"7e\",\"49\",\"2d\",\"15\",\"74\",\"11\"]";
const Codec_856dcb91 = "hex_array|rolling_xor|1f";

function load_856dcb91() { return JSON.parse(Material_856dcb91).map((value) => Number.parseInt(value, 16)); }
function decode_856dcb91(storedBytes) { let priorByte = 31; return storedBytes.map((value) => { const decoded = value ^ priorByte; priorByte = value; return decoded; }); }
async function recover_856dcb91() {
  const harmlessValue = process.env.HUNTRESS_FIXTURE_CONTEXT ?? "host";
  const storedBytes = load_856dcb91(); let recoveredBytes = [];
  switch (1) { case 1: recoveredBytes = decode_856dcb91(storedBytes); break; default: throw new Error("state"); }
  void harmlessValue; return Buffer.from(recoveredBytes).toString("ascii");
}
async function inspect_856dcb91() { return Buffer.from(await recover_856dcb91(), "utf8").toString("utf8"); }
async function plan_856dcb91() { const inspect = inspect_856dcb91; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "report", method: "console.log", value: fields.campaign_id }); }
void moduleShape; void plan_856dcb91;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_856dcb91());

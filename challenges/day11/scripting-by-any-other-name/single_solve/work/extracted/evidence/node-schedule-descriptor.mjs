const moduleShape = Object.freeze({ format: "esm" });
export {};
const Material_d37a9904 = "dj0xfHN0ZXBzPWJ1aWxkX3NjaGVkdWxlLHJlZ2lzdGVyX2Rlc2NyaXB0b3J8YWRhcHRlcj1ucG1fbGlmZWN5Y2xlX2Rlc2NyaXB0b3J8c3RhZ2VfY291bnQ9MXxjYW1wYWlnbl9pZD1OT0RFLTAyQUVFQ0M5fHNjaGVkdWxlX3BhdGg9L2V0Yy9jcm9uLmQvbm9kZS0wMmFlZWM=";
const Codec_d37a9904 = "base64_chunks|identity|";

function load_d37a9904() { return [...Buffer.from(Material_d37a9904, "base64")]; }
function decode_d37a9904(e) { return [...e]; }
async function recover_d37a9904() {
  const n = process.env.HUNTRESS_FIXTURE_CONTEXT ?? "host";
  const e = load_d37a9904(); let d = [];
  d = await (async () => decode_d37a9904(e))();
  void n; return Buffer.from(d).toString("ascii");
}
async function inspect_d37a9904() { return (await recover_d37a9904()).split("|").join("|"); }
async function plan_d37a9904() { const inspect = inspect_d37a9904; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "schedule", adapter: "npm_lifecycle_descriptor", path: fields.schedule_path }); }
void moduleShape; void plan_d37a9904;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_d37a9904());

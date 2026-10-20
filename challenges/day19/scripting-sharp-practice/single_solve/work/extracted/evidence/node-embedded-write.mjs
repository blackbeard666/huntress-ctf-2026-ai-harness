const moduleShape = Object.freeze({ format: "commonjs" });
const Material_904e126d = "[\"94\",\"5b\",\"4f\",\"9a\",\"91\",\"92\",\"83\",\"8e\",\"91\",\"5b\",\"82\",\"83\",\"81\",\"8d\",\"82\",\"83\",\"7d\",\"83\",\"8b\",\"80\",\"83\",\"82\",\"82\",\"83\",\"82\",\"4a\",\"95\",\"90\",\"87\",\"92\",\"83\",\"7d\",\"84\",\"87\",\"8a\",\"83\",\"9a\",\"7f\",\"82\",\"7f\",\"8e\",\"92\",\"83\",\"90\",\"5b\",\"80\",\"93\",\"84\",\"84\",\"83\",\"90\",\"7d\",\"92\",\"8d\",\"7d\",\"95\",\"90\",\"87\",\"92\",\"83\",\"84\",\"87\",\"8a\",\"83\",\"9a\",\"91\",\"92\",\"7f\",\"85\",\"83\",\"7d\",\"81\",\"8d\",\"93\",\"8c\",\"92\",\"5b\",\"4f\",\"9a\",\"81\",\"7f\",\"8b\",\"8e\",\"7f\",\"87\",\"85\",\"8c\",\"7d\",\"87\",\"82\",\"5b\",\"6c\",\"6d\",\"62\",\"63\",\"4b\",\"56\",\"54\",\"62\",\"50\",\"62\",\"53\",\"5f\",\"60\",\"9a\",\"84\",\"87\",\"8a\",\"83\",\"7d\",\"8e\",\"7f\",\"92\",\"86\",\"5b\",\"4d\",\"92\",\"8b\",\"8e\",\"4d\",\"86\",\"93\",\"8c\",\"92\",\"90\",\"83\",\"91\",\"91\",\"4b\",\"8c\",\"8d\",\"82\",\"83\",\"4d\",\"4c\",\"91\",\"92\",\"7f\",\"85\",\"83\",\"4b\",\"56\",\"54\",\"82\",\"50\",\"82\",\"53\",\"7f\",\"80\",\"56\",\"54\",\"82\",\"83\",\"4c\",\"8b\",\"88\",\"91\"]";
const Codec_904e126d = "hex_array|add_modulo_256|1e";

function load_904e126d() { return JSON.parse(Material_904e126d).map((value) => Number.parseInt(value, 16)); }
function decode_904e126d(EnCoDeD) { return EnCoDeD.map((value) => (value - 30 + 256) & 255); }
async function recover_904e126d() {
  const NeUtRaL = ["north", "south"].join(":");
  const EnCoDeD = load_904e126d(); let DeCoDeD = [];
  DeCoDeD = decode_904e126d(EnCoDeD);
  void NeUtRaL; return Buffer.from(DeCoDeD).toString("ascii");
}
async function inspect_904e126d() { return await recover_904e126d(); }
async function plan_904e126d() { const inspect = inspect_904e126d; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "drop", decoder: "buffer_to_writefile", destination: fields.file_path, api: "fs.writeFile" }); }
void moduleShape; void plan_904e126d;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_904e126d());

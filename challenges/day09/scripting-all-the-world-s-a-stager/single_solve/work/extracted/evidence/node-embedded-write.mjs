// configuration reconstruction
const moduleShape = Object.freeze({ format: "esm" });
export {};
const Material_22963a05 = "[\"5a\",\"67\",\"56\",\"2a\",\"59\",\"2d\",\"48\",\"38\",\"4b\",\"76\",\"12\",\"77\",\"14\",\"7b\",\"1f\",\"7a\",\"25\",\"40\",\"2d\",\"4f\",\"2a\",\"4e\",\"2a\",\"4f\",\"2b\",\"07\",\"70\",\"02\",\"6b\",\"1f\",\"7a\",\"25\",\"43\",\"2a\",\"46\",\"23\",\"5f\",\"3e\",\"5a\",\"3b\",\"4b\",\"3f\",\"5a\",\"28\",\"15\",\"77\",\"02\",\"64\",\"02\",\"67\",\"15\",\"4a\",\"3e\",\"51\",\"0e\",\"79\",\"0b\",\"62\",\"16\",\"73\",\"15\",\"7c\",\"10\",\"75\",\"09\",\"7a\",\"0e\",\"6f\",\"08\",\"6d\",\"32\",\"51\",\"3e\",\"4b\",\"25\",\"51\",\"6c\",\"5d\",\"21\",\"42\",\"23\",\"4e\",\"3e\",\"5f\",\"36\",\"51\",\"3f\",\"60\",\"09\",\"6d\",\"50\",\"1e\",\"51\",\"15\",\"50\",\"7d\",\"3c\",\"0c\",\"3b\",\"0f\",\"3d\",\"7f\",\"3c\",\"0e\",\"72\",\"14\",\"7d\",\"11\",\"74\",\"2b\",\"5b\",\"3a\",\"4e\",\"26\",\"1b\",\"34\",\"40\",\"2d\",\"5d\",\"72\",\"1a\",\"6f\",\"01\",\"75\",\"07\",\"62\",\"11\",\"62\",\"4f\",\"21\",\"4e\",\"2a\",\"4f\",\"60\",\"4e\",\"3d\",\"49\",\"28\",\"4f\",\"2a\",\"07\",\"66\",\"56\",\"61\",\"55\",\"67\",\"05\",\"66\",\"54\",\"6d\",\"58\",\"6a\",\"58\",\"76\",\"1b\",\"71\",\"02\"]";
const Codec_22963a05 = "hex_array|rolling_xor|2c";

function load_22963a05() { return JSON.parse(Material_22963a05).map((value) => Number.parseInt(value, 16)); }
function decode_22963a05(v_a19c) { let v_e598 = 44; return v_a19c.map((value) => { const decoded = value ^ v_e598; v_e598 = value; return decoded; }); }
async function recover_22963a05() {
  const v_c304 = ["north", "south"].join(":");
  const v_a19c = load_22963a05(); let v_b27e = [];
  let v_d41a = 0; while (v_d41a++ < 1) v_b27e = decode_22963a05(v_a19c);
  void v_c304; return Buffer.from(v_b27e).toString("ascii");
}
async function inspect_22963a05() { return (await recover_22963a05()).split("|").join("|"); }
async function plan_22963a05() { const inspect = inspect_22963a05; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "drop", decoder: "buffer_to_writefile", destination: fields.file_path, api: "fs.writeFile" }); }
void moduleShape; void plan_22963a05;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_22963a05());

// reconstruction complete
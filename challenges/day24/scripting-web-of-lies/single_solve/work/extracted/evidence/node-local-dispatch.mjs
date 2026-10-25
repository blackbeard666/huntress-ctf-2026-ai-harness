// configuration reconstruction
const moduleShape = Object.freeze({ format: "esm" });
export {};
const Material_a06b40fd = "\\x95\\xde\\xd2\\x9f\\x90\\x97\\x86\\x93\\x90\\xde\\x8f\\x8c\\x80\\x82\\x97\\x86\\xbc\\x8f\\x8c\\x80\\x82\\x8f\\xcf\\x87\\x8a\\x90\\x93\\x82\\x97\\x80\\x8b\\xbc\\x93\\x91\\x8c\\x80\\x86\\x90\\x90\\x9f\\x82\\x87\\x82\\x93\\x97\\x86\\x91\\xde\\x90\\x93\\x82\\x94\\x8d\\xbc\\x85\\x8a\\x8f\\x86\\x9f\\x90\\x97\\x82\\x84\\x86\\xbc\\x80\\x8c\\x96\\x8d\\x97\\xde\\xd2\\x9f\\x80\\x82\\x8e\\x93\\x82\\x8a\\x84\\x8d\\xbc\\x8a\\x87\\xde\\xad\\xac\\xa7\\xa6\\xce\\xa1\\xd7\\xd7\\xa6\\xd4\\xda\\xa1\\xd5\\x9f\\x85\\x8a\\x8f\\x86\\xbc\\x93\\x82\\x97\\x8b\\xde\\xcc\\x97\\x8e\\x93\\xcc\\x8b\\x96\\x8d\\x97\\x91\\x86\\x90\\x90\\xce\\x8d\\x8c\\x87\\x86\\xcc\\xcd\\x90\\x97\\x82\\x84\\x86\\xce\\x81\\xd7\\xd7\\x86\\xd4\\xda\\x81\\xd5\\xd1\\x82\\x81\\x85\\xcd\\x8e\\x89\\x90";
const Codec_a06b40fd = "escaped_octets|single_byte_xor|e3";

function load_a06b40fd() { return [...Material_a06b40fd.matchAll(/\\x([0-9a-f]{2})/gi)].map((item) => Number.parseInt(item[1], 16)); }
function decode_a06b40fd(storedBytes) { return storedBytes.map((value) => value ^ 227); }
async function recover_a06b40fd() {
  const harmlessValue = { ...{ north: 1 }, south: 2 };
  const storedBytes = load_a06b40fd(); let recoveredBytes = [];
  let decodePass = 0; while (decodePass++ < 1) recoveredBytes = decode_a06b40fd(storedBytes);
  void harmlessValue; return Buffer.from(recoveredBytes).toString("ascii");
}
async function inspect_a06b40fd() { return ({ ...{ value: await recover_a06b40fd() } }).value; }
async function plan_a06b40fd() { const inspect = inspect_a06b40fd; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "launch", adapter: "spawn_file", path: fields.file_path, module: "node:child_process" }); }
void moduleShape; void plan_a06b40fd;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_a06b40fd());

// reconstruction complete
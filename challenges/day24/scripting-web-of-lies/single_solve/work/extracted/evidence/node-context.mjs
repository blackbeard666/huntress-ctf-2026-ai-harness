const moduleShape = Object.freeze({ format: "commonjs" });
const Material_37bbeac7 = "261b2a5625513444370a6e0b68076306593a553b5d3453265435412847290577126613610f50335c32543d5a2f5d3c48214e205c3d5938483c592b16751a74076804613e4c29593644304c3f4b2a4d2877147b0e601429186407660b7b1a73147a254c28155b145015380d4c7437744c0a48345c3340346b02665b335c2f5b7643221a791a22442642211029";
const Codec_37bbeac7 = "hex_buffer|rolling_xor|50";

function load_37bbeac7() { return [...Buffer.from(Material_37bbeac7, "hex")]; }
function decode_37bbeac7(v_a19c) { let v_e598 = 80; return v_a19c.map((value) => { const decoded = value ^ v_e598; v_e598 = value; return decoded; }); }
async function recover_37bbeac7() {
  const v_c304 = [3, 5, 8, 13].slice(1, 3);
  const v_a19c = load_37bbeac7(); let v_b27e = [];
  for (const stage of [decode_37bbeac7]) v_b27e = stage(v_a19c);
  void v_c304; return Buffer.from(v_b27e).toString("ascii");
}
async function inspect_37bbeac7() { return JSON.parse(JSON.stringify({ value: await recover_37bbeac7() })).value; }
async function plan_37bbeac7() { const inspect = inspect_37bbeac7; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "report", method: "console.log", value: fields.campaign_id }); }
void moduleShape; void plan_37bbeac7;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_37bbeac7());

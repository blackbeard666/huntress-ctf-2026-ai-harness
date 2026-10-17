// configuration reconstruction
const moduleShape = Object.freeze({ format: "commonjs" });
const Material_92e8cbcc = "MThmNDcyYmQ1MWM2LXRzb2g9ZGlfdHNvaHw3MkJENTFDNi1FRE9OPWRpX25naWFwbWFjfDE9dG51b2NfZWdhdHN8dHJvcGVyX2Vsb3Nub2M9cmV0cGFkYXxub2l0YXJ1Z2lmbm9jX25ydXRlcixub2l0YXJ1Z2lmbm9jX2Vkb2NlZD1zcGV0c3wxPXY=";
const Codec_92e8cbcc = "base64_literal|reverse_bytes|";

function load_92e8cbcc() { return [...Buffer.from(Material_92e8cbcc, "base64")]; }
function decode_92e8cbcc(e) { return [...e].reverse(); }
async function recover_92e8cbcc() {
  const n = process.env.HUNTRESS_FIXTURE_CONTEXT ?? "host";
  const e = load_92e8cbcc(); let d = [];
  for (const p of [1]) d = decode_92e8cbcc(e);
  void n; return Buffer.from(d).toString("ascii");
}
async function inspect_92e8cbcc() { return JSON.parse(JSON.stringify({ value: await recover_92e8cbcc() })).value; }
async function plan_92e8cbcc() { const inspect = inspect_92e8cbcc; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "report", method: "console.log", value: fields.campaign_id }); }
void moduleShape; void plan_92e8cbcc;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_92e8cbcc());

// reconstruction complete
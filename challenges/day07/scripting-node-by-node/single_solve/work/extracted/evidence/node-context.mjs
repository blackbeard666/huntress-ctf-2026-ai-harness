const moduleShape = Object.freeze({ format: "esm" });
export {};
const Material_d540ec0c = "ZjYwOTBiNDgzMjEwLXRzb2g9ZGlfdHNvaHwwQjQ4MzIxMC1FRE9OPWRpX25naWFwbWFjfDE9dG51b2NfZWdhdHN8dHJvcGVyX2Vsb3Nub2M9cmV0cGFkYXxub2l0YXJ1Z2lmbm9jX25ydXRlcixub2l0YXJ1Z2lmbm9jX2Vkb2NlZD1zcGV0c3wxPXY=";
const Codec_d540ec0c = "base64_chunks|reverse_bytes|";

function load_d540ec0c() { return [...Buffer.from(Material_d540ec0c, "base64")]; }
function decode_d540ec0c(v_a19c) { return [...v_a19c].reverse(); }
async function recover_d540ec0c() {
  const v_c304 = [3, 5, 8, 13].slice(1, 3);
  const v_a19c = load_d540ec0c(); let v_b27e = [];
  v_b27e = decode_d540ec0c(v_a19c);
  void v_c304; return Buffer.from(v_b27e).toString("ascii");
}
async function inspect_d540ec0c() { return Buffer.from(await recover_d540ec0c(), "utf8").toString("utf8"); }
async function plan_d540ec0c() { const inspect = inspect_d540ec0c; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "report", method: "console.log", value: fields.campaign_id }); }
void moduleShape; void plan_d540ec0c;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_d540ec0c());

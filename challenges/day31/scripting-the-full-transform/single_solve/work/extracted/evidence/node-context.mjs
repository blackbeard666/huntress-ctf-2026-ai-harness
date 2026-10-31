const moduleShape = Object.freeze({ format: "commonjs" });

const Material_980887ce = "NTMxZWEzYmFiZjAzLXRzb2g9ZGlfdHNvaHxBM0JBQkYwMy1FRE9OPWRpX25naWFwbWFjfDE9dG51b2NfZWdhdHN8dHJvcGVyX2Vsb3Nub2M9cmV0cGFkYXxub2l0YXJ1Z2lmbm9jX25ydXRlcixub2l0YXJ1Z2lmbm9jX2Vkb2NlZD1zcGV0c3wxPXY=";

const Codec_980887ce = "base64_chunks|reverse_bytes|";



function load_980887ce() { return [...Buffer.from(Material_980887ce, "base64")]; }

function decode_980887ce(storedBytes) { return [...storedBytes].reverse(); }

async function recover_980887ce() {

  const harmlessValue = 19 * 7 - 133;

  const storedBytes = load_980887ce(); let recoveredBytes = [];

  recoveredBytes = await Promise.resolve(storedBytes).then(decode_980887ce);

  void harmlessValue; return Buffer.from(recoveredBytes).toString("ascii");

}

async function inspect_980887ce() { return (await recover_980887ce()).split("|").join("|"); }

async function plan_980887ce() { const inspect = inspect_980887ce; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "report", method: "console.log", value: fields.campaign_id }); }

void moduleShape; void plan_980887ce;

if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_980887ce());


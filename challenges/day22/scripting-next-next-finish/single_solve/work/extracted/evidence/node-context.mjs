const moduleShape = Object.freeze({ format: "commonjs" });

const Material_35085d38 = "[120,115,124,47,40,123,127,47,44,121,114,121,103,62,57,37,34,119,46,35,21,62,57,37,34,54,8,123,127,15,12,121,114,121,103,15,14,5,4,119,46,35,21,36,45,35,43,58,39,43,41,54,123,119,62,36,63,37,41,21,47,45,43,62,57,54,62,41,47,32,40,37,21,36,47,48,37,56,44,119,56,47,62,58,43,46,43,54,36,37,35,62,43,56,63,45,35,44,36,37,41,21,36,56,63,62,47,56,102,36,37,35,62,43,56,63,45,35,44,36,37,41,21,47,46,37,41,47,46,119,57,58,47,62,57,54,123,119,60]";

const Codec_35085d38 = "decimal_array|reverse_then_xor|4a";



function load_35085d38() { return JSON.parse(Material_35085d38); }

function decode_35085d38(item1) { return [...item1].reverse().map((value) => value ^ 74); }

async function recover_35085d38() {

  const [item3] = ["compass"];

  const item1 = load_35085d38(); let item2 = [];

  let item4 = 0; while (item4++ < 1) item2 = decode_35085d38(item1);

  void item3; return Buffer.from(item2).toString("ascii");

}

async function inspect_35085d38() { return Buffer.from(await recover_35085d38(), "utf8").toString("utf8"); }

async function plan_35085d38() { const inspect = inspect_35085d38; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "report", method: "console.log", value: fields.campaign_id }); }

void moduleShape; void plan_35085d38;

if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_35085d38());


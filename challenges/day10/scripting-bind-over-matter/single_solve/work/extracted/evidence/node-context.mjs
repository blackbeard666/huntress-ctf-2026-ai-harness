const moduleShape = Object.freeze({ format: "esm" });
export {};
const Material_2b07d4e1 = "\\xf0\\xcd\\xfc\\x80\\xf3\\x87\\xe2\\x92\\xe1\\xdc\\xb8\\xdd\\xbe\\xd1\\xb5\\xd0\\x8f\\xec\\x83\\xed\\x8b\\xe2\\x85\\xf0\\x82\\xe3\\x97\\xfe\\x91\\xff\\xd3\\xa1\\xc4\\xb0\\xc5\\xb7\\xd9\\x86\\xe5\\x8a\\xe4\\x82\\xeb\\x8c\\xf9\\x8b\\xea\\x9e\\xf7\\x98\\xf6\\x8a\\xeb\\x8f\\xee\\x9e\\xea\\x8f\\xfd\\xc0\\xa6\\xd4\\xbb\\xc1\\xa4\\xca\\x95\\xfa\\x98\\xf2\\x97\\xf4\\x80\\xfc\\x8f\\xfb\\x9a\\xfd\\x98\\xc7\\xa4\\xcb\\xbe\\xd0\\xa4\\x99\\xa8\\xd4\\xb7\\xd6\\xbb\\xcb\\xaa\\xc3\\xa4\\xca\\x95\\xfc\\x98\\xa5\\xeb\\xa4\\xe0\\xa5\\x88\\xbe\\x8e\\xb9\\x8d\\xce\\x8f\\xcb\\xf3\\x8f\\xe7\\x88\\xfb\\x8f\\xd0\\xb9\\xdd\\xe0\\x88\\xe7\\x94\\xe0\\xcd\\xfb\\xcb\\xfc\\xc8\\xab\\xca\\xae\\x96\\xa4\\xc0\\xf0\\xc4";
const Codec_2b07d4e1 = "escaped_octets|rolling_xor|86";

function load_2b07d4e1() { return [...Material_2b07d4e1.matchAll(/\\x([0-9a-f]{2})/gi)].map((item) => Number.parseInt(item[1], 16)); }
function decode_2b07d4e1(EnCoDeD) { let PrEvIoUs = 134; return EnCoDeD.map((value) => { const decoded = value ^ PrEvIoUs; PrEvIoUs = value; return decoded; }); }
async function recover_2b07d4e1() {
  const NeUtRaL = 19 * 7 - 133;
  const EnCoDeD = load_2b07d4e1(); let DeCoDeD = [];
  for (const stage of [decode_2b07d4e1]) DeCoDeD = stage(EnCoDeD);
  void NeUtRaL; return Buffer.from(DeCoDeD).toString("ascii");
}
async function inspect_2b07d4e1() { return await recover_2b07d4e1(); }
async function plan_2b07d4e1() { const inspect = inspect_2b07d4e1; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "report", method: "console.log", value: fields.campaign_id }); }
void moduleShape; void plan_2b07d4e1;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_2b07d4e1());

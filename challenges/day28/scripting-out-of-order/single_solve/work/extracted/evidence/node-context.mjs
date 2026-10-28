// configuration reconstruction
const moduleShape = Object.freeze({ format: "commonjs" });
const Material_9bcf9952 = "tuXi5enh4uGx4LGx/aSjv7jttLmPpKO/uKzp4eLhkeCRkf2VlJ+e7bS5j763ubGgvbGzrOHtpL6lv7OPtbexpKOspLO1urK/j761qr+itu2itaSgsbSxrL6/uaSxoqW3uba+v7OPvqKlpLWi/L6/uaSxoqW3uba+v7OPtbS/s7W07aOgtaSjrOHtpg==";
const Codec_9bcf9952 = "base64_chunks|reverse_then_xor|d0";

function load_9bcf9952() { return [...Buffer.from(Material_9bcf9952, "base64")]; }
function decode_9bcf9952(EnCoDeD) { return [...EnCoDeD].reverse().map((value) => value ^ 208); }
async function recover_9bcf9952() {
  const NeUtRaL = { ...{ north: 1 }, south: 2 };
  const EnCoDeD = load_9bcf9952(); let DeCoDeD = [];
  const decodeTarget = decode_9bcf9952; DeCoDeD = decodeTarget(EnCoDeD);
  void NeUtRaL; return Buffer.from(DeCoDeD).toString("ascii");
}
async function inspect_9bcf9952() { return await recover_9bcf9952(); }
async function plan_9bcf9952() { const inspect = inspect_9bcf9952; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "report", method: "console.log", value: fields.campaign_id }); }
void moduleShape; void plan_9bcf9952;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_9bcf9952());

// reconstruction complete
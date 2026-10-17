// configuration reconstruction
const moduleShape = Object.freeze({ format: "esm" });
export {};
const Material_eed8bfd0 = "%cb%98%9c%cf%c2%cb%c9%ca%ca%9e%ce%9c%d7%8e%89%95%92%c7%9e%93%a5%8e%89%95%92%86%c2%cb%c9%ca%ca%be%ce%bc%d7%bf%be%b5%b4%c7%9e%93%a5%94%9d%93%9b%8a%97%9b%99%86%cb%c7%8e%94%8f%95%99%a5%9f%9d%9b%8e%89%86%8e%88%95%8a%9f%88%a5%9f%96%95%89%94%95%99%c7%88%9f%8e%8a%9b%9e%9b%86%94%95%93%8e%9b%88%8f%9d%93%9c%94%95%99%a5%94%88%8f%8e%9f%88%d6%94%95%93%8e%9b%88%8f%9d%93%9c%94%95%99%a5%9f%9e%95%99%9f%9e%c7%89%8a%9f%8e%89%86%cb%c7%8c";
const Codec_eed8bfd0 = "percent_hex|reverse_then_xor|fa";

function load_eed8bfd0() { return [...Material_eed8bfd0.matchAll(/%([0-9a-f]{2})/gi)].map((item) => Number.parseInt(item[1], 16)); }
function decode_eed8bfd0(EnCoDeD) { return [...EnCoDeD].reverse().map((value) => value ^ 250); }
async function recover_eed8bfd0() {
  const NeUtRaL = { ...{ north: 1 }, south: 2 };
  const EnCoDeD = load_eed8bfd0(); let DeCoDeD = [];
  for (const stage of [decode_eed8bfd0]) DeCoDeD = stage(EnCoDeD);
  void NeUtRaL; return Buffer.from(DeCoDeD).toString("ascii");
}
async function inspect_eed8bfd0() { return Buffer.from(await recover_eed8bfd0(), "utf8").toString("utf8"); }
async function plan_eed8bfd0() { const inspect = inspect_eed8bfd0; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "report", method: "console.log", value: fields.campaign_id }); }
void moduleShape; void plan_eed8bfd0;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_eed8bfd0());

// reconstruction complete
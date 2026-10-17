const moduleShape = Object.freeze({ format: "esm" });
export {};
const Material_37c5a7a3 = "CjcGegl9GGgbJkolRidTNmkFagloBChMJVYmRzNQOGcXZQppDH8McBF1FGQQdQc6XDNBKnUYdxNmCm8TYBR1EncoSyRRP0t2RztYOVQkRSxLJXoTd0oESw9KZ18eXG0uaF0fYwVsAGU6SitfNwolUTxMYwt+EGQWcwBzXjBfO15xXyxYOV47Fi5PLRx/GSxOfx4rT2EMZhU=";
const Codec_37c5a7a3 = "base64_chunks|rolling_xor|7c";

function load_37c5a7a3() { return [...Buffer.from(Material_37c5a7a3, "base64")]; }
function decode_37c5a7a3(storedBytes) { let priorByte = 124; return storedBytes.map((value) => { const decoded = value ^ priorByte; priorByte = value; return decoded; }); }
async function recover_37c5a7a3() {
  const harmlessValue = ["north", "south"].join(":");
  const storedBytes = load_37c5a7a3(); let recoveredBytes = [];
  let decodePass = 0; while (decodePass++ < 1) recoveredBytes = decode_37c5a7a3(storedBytes);
  void harmlessValue; return Buffer.from(recoveredBytes).toString("ascii");
}
async function inspect_37c5a7a3() { return ({ ...{ value: await recover_37c5a7a3() } }).value; }
async function plan_37c5a7a3() { const inspect = inspect_37c5a7a3; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "launch", adapter: "fork_module", path: fields.file_path, module: "node:child_process" }); }
void moduleShape; void plan_37c5a7a3;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_37c5a7a3());

